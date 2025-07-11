"""
Web Dashboard Module

This module provides a web interface for monitoring and controlling the
energy automation system. It uses Flask to serve a real-time dashboard
that displays:
- Current solar production
- House consumption
- Grid power flow
- Status of managed devices

The dashboard updates automatically every 5 seconds.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from flask import Flask, render_template, jsonify, request
from parra_energy.api.smart_fronius import SmartFroniusClient
from parra_energy.automations.manager import AutomationManager
from parra_energy.analytics.optimizer import EnergyOptimizer
from datetime import datetime, timedelta
import sqlite3
import threading
import time
import atexit

# Initialize Flask application
app = Flask(__name__)

# Initialize system components  
fronius = SmartFroniusClient(host="192.168.1.128")  # Smart client that auto-detects real vs mock
automation_manager = AutomationManager()
energy_optimizer = EnergyOptimizer('parra_energy/data/energy_data.db')

# --- Background fetcher thread for 5s polling and 5min averaging ---
def background_fetcher():
    local_buffer = []
    while True:
        try:
            power_data = fronius.get_power_data()
            print(f"[FETCH] {datetime.now().isoformat()} - Production: {power_data.get('P_PV', 0)}, Consumption: {power_data.get('P_Load', 0)}")
            local_buffer.append({
                'production': float(power_data.get('P_PV', 0)),
                'consumption': float(power_data.get('P_Load', 0))
            })
            if len(local_buffer) >= 60:  # 60 * 5s = 5min
                avg_prod = sum(x['production'] for x in local_buffer) / len(local_buffer)
                avg_cons = sum(x['consumption'] for x in local_buffer) / len(local_buffer)
                ts = datetime.now().replace(second=0, microsecond=0, minute=(datetime.now().minute // 5) * 5)
                print(f"[AVERAGE] {ts.isoformat()} - Avg Production: {avg_prod}, Avg Consumption: {avg_cons}")
                conn = sqlite3.connect('energy_data.db')
                c = conn.cursor()
                c.execute('INSERT OR REPLACE INTO energy (timestamp, production, consumption) VALUES (?, ?, ?)',
                          (ts.isoformat(), avg_prod, avg_cons))
                conn.commit()
                conn.close()
                print(f"[DB SAVE] {ts.isoformat()} - Saved to DB.")
                local_buffer.clear()
            time.sleep(5)
        except Exception as e:
            print(f"Background fetch error: {e}")
            time.sleep(5)

import atexit
fetcher_thread = threading.Thread(target=background_fetcher, daemon=True)
fetcher_thread.start()
atexit.register(lambda: fetcher_thread.join(timeout=1))

@app.route('/')
def index():
    """Render the main dashboard page.
    
    Returns:
        The rendered index.html template
    """
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Get current system status.
    
    This endpoint is called by the frontend to get real-time updates.
    It fetches:
    1. Current power data from the Fronius inverter (real or mock)
    2. Status of all managed devices
    3. Information about whether we're using real or mock data
    
    Returns:
        JSON response containing:
            - power_data: Current power readings
            - automation: Status of all managed devices
            - client_status: Information about real vs mock data
    """
    power_data = fronius.get_power_data()
    automation_manager.update(power_data)
    automation_status = automation_manager.get_status()
    client_status = fronius.get_status()
    
    return jsonify({
        'power_data': power_data,
        'automation': automation_status,
        'client_status': client_status
    })

@app.route('/debug/all')
def debug_all():
    db = sqlite3.connect('energy_data.db')
    db.row_factory = sqlite3.Row
    rows = db.execute('SELECT * FROM energy ORDER BY timestamp').fetchall()
    return jsonify([dict(row) for row in rows])

@app.route('/history/<date>')
def history(date):
    try:
        day = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return "Invalid date", 400
    db = sqlite3.connect('energy_data.db')
    db.row_factory = sqlite3.Row
    start = day.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    rows = db.execute(
        'SELECT timestamp, production, consumption FROM energy WHERE timestamp >= ? AND timestamp < ?',
        (start.isoformat(), end.isoformat())
    ).fetchall()
    print(f"[HISTORY] {len(rows)} rows fetched for {date}")
    # Aggregate 5-min blocks into hourly kWh
    hourly = [{'hour': h, 'production': 0, 'consumption': 0, 'count': 0} for h in range(24)]
    for row in rows:
        ts = datetime.fromisoformat(row['timestamp'])
        h = ts.hour
        # Each 5-min block: kWh = (W * 5/60) / 1000
        hourly[h]['production'] += row['production'] * 5 / 60 / 1000
        hourly[h]['consumption'] += row['consumption'] * 5 / 60 / 1000
        hourly[h]['count'] += 1
    chart_data = []
    for h in hourly:
        prod = h['production']
        cons = h['consumption']
        green = min(prod, cons)
        red = max(0, cons - prod)
        chart_data.append({
            'hour': h['hour'],
            'production': prod,
            'consumption': cons,
            'self_consumed': green,
            'from_grid': red
        })
        print(f"[HOUR] {chart_data[-1]}")
    return jsonify(chart_data)

@app.route('/history5min/<date>')
def history5min(date):
    try:
        day = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return "Invalid date", 400
    db = sqlite3.connect('energy_data.db')
    db.row_factory = sqlite3.Row
    start = day.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    rows = db.execute(
        'SELECT timestamp, production, consumption FROM energy WHERE timestamp >= ? AND timestamp < ?',
        (start.isoformat(), end.isoformat())
    ).fetchall()
    data = []
    for row in rows:
        prod = row['production'] * 5 / 60 / 1000  # kWh for 5min
        cons = row['consumption'] * 5 / 60 / 1000
        green = min(prod, cons)
        red = max(0, cons - prod)
        data.append({
            'timestamp': row['timestamp'],
            'production': prod,
            'consumption': cons,
            'self_consumed': green,
            'from_grid': red
        })
    return jsonify(data)

@app.route('/export/<date>')
def export_csv(date):
    try:
        day = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return "Invalid date", 400
    db = sqlite3.connect('energy_data.db')
    db.row_factory = sqlite3.Row
    start = day.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    rows = db.execute(
        'SELECT timestamp, production, consumption FROM energy WHERE timestamp >= ? AND timestamp < ?',
        (start.isoformat(), end.isoformat())
    ).fetchall()
    import csv
    from io import StringIO
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['timestamp', 'production_W', 'consumption_W'])
    for row in rows:
        cw.writerow([row['timestamp'], row['production'], row['consumption']])
    output = si.getvalue()
    return output, 200, {'Content-Type': 'text/csv'}

# Analytics endpoints
@app.route('/api/analytics/tips')
def get_optimization_tips():
    """Get personalized optimization tips based on historical data."""
    days = request.args.get('days', default=30, type=int)
    tips = energy_optimizer.get_optimization_tips(days)
    
    return jsonify({
        'tips': [
            {
                'tip': tip.tip,
                'priority': tip.priority,
                'potential_savings': tip.potential_savings,
                'category': tip.category
            }
            for tip in tips
        ],
        'generated_at': datetime.now().isoformat(),
        'analysis_period_days': days
    })

@app.route('/api/analytics/daily-report')
@app.route('/api/analytics/daily-report/<date>')
def get_daily_report(date=None):
    """Get detailed daily report for a specific date."""
    report = energy_optimizer.get_daily_report(date)
    return jsonify(report)

@app.route('/api/analytics/weekly-forecast')
def get_weekly_forecast():
    """Get weekly forecast and recommendations."""
    forecast = energy_optimizer.get_weekly_forecast()
    return jsonify(forecast)

@app.route('/api/analytics/historical')
def get_historical_analysis():
    """Get historical analysis for specified period."""
    days = request.args.get('days', default=30, type=int)
    analysis = energy_optimizer.analyze_historical_data(days)
    
    if 'error' in analysis:
        return jsonify(analysis), 404
    
    # Calculate summary metrics
    daily_data = analysis['daily_data']
    total_production = sum(d['production'] for d in daily_data.values())
    total_consumption = sum(d['consumption'] for d in daily_data.values())
    total_self_consumed = sum(d['self_consumed'] for d in daily_data.values())
    total_from_grid = sum(d['from_grid'] for d in daily_data.values())
    total_to_grid = sum(d['to_grid'] for d in daily_data.values())
    
    summary = {
        'total_production': round(total_production, 2),
        'total_consumption': round(total_consumption, 2),
        'total_self_consumed': round(total_self_consumed, 2),
        'total_from_grid': round(total_from_grid, 2),
        'total_to_grid': round(total_to_grid, 2),
        'self_consumption_rate': round((total_self_consumed / total_production * 100) if total_production > 0 else 0, 1),
        'grid_dependency': round((total_from_grid / total_consumption * 100) if total_consumption > 0 else 0, 1),
        'energy_independence': round(100 - (total_from_grid / total_consumption * 100) if total_consumption > 0 else 100, 1)
    }
    
    return jsonify({
        'summary': summary,
        'analysis': analysis,
        'generated_at': datetime.now().isoformat()
    })

# Weather-enhanced endpoints
@app.route('/api/weather/forecast')
def get_weather_forecast():
    """Get weather forecast for solar planning."""
    try:
        days = request.args.get('days', default=7, type=int)
        # Get the weather service from the energy optimizer
        weather_service = energy_optimizer.weather_service
        
        # Fetch fresh weather data
        weather_data = weather_service.fetch_weather_forecast(days)
        if not weather_data:
            return jsonify({'error': 'Could not fetch weather data'}), 500
        
        # Get weekly summary
        weekly_summary = weather_service.get_weekly_weather_summary()
        if weekly_summary is None:
            return jsonify({'error': 'No weather summary available'}), 500
        
        # Convert DataFrame to JSON-serializable format
        weekly_data = []
        for _, row in weekly_summary.iterrows():
            weekly_data.append({
                'date': row['date'],
                'sunrise': row['sunrise'],
                'sunset': row['sunset'],
                'daylight_hours': round(row['daylight_duration'] / 3600, 2),
                'uv_index_max': row['uv_index_max'],
                'temperature_max': row['temperature_max'],
                'temperature_min': row['temperature_min'],
                'solar_production_forecast': row['solar_production_forecast'],
                'weather_quality_score': row['weather_quality_score'],
                'quality_rating': row['quality_rating'],
                'production_category': row['production_category']
            })
        
        return jsonify({
            'weekly_forecast': weekly_data,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/weather/enhanced-forecast')
def get_enhanced_forecast():
    """Get weather-enhanced forecast combining weather and energy patterns."""
    try:
        days = request.args.get('days', default=7, type=int)
        enhanced_forecast = energy_optimizer.get_weather_enhanced_forecast(days)
        return jsonify(enhanced_forecast)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/weather/best-hours')
@app.route('/api/weather/best-hours/<date>')
def get_best_hours_forecast(date=None):
    """Get the best hours for energy consumption based on weather forecast."""
    try:
        weather_service = energy_optimizer.weather_service
        best_hours = weather_service.get_best_hours_forecast(date)
        
        if best_hours is None:
            return jsonify({'error': 'No weather data available for this date'}), 404
        
        return jsonify(best_hours)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/weather/refresh')
def refresh_weather_data():
    """Manually refresh weather data."""
    try:
        weather_service = energy_optimizer.weather_service
        weather_data = weather_service.fetch_weather_forecast(7)
        
        if weather_data:
            return jsonify({
                'status': 'success',
                'message': 'Weather data refreshed successfully',
                'coordinates': weather_data['coordinates'],
                'updated_at': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to refresh weather data'
            }), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/fronius/status')
def get_fronius_status():
    """Get detailed status of the Fronius client (real vs mock)."""
    return jsonify(fronius.get_status())

@app.route('/api/fronius/force-mock', methods=['POST'])
def force_mock_mode():
    """Force the Fronius client to use mock data for demo purposes."""
    fronius.force_mock_mode()
    return jsonify({
        'status': 'success',
        'message': 'Switched to mock mode for demo',
        'client_status': fronius.get_status()
    })

@app.route('/api/fronius/force-real', methods=['POST'])
def force_real_mode():
    """Force the Fronius client to try using real data."""
    fronius.force_real_mode()
    return jsonify({
        'status': 'success',
        'message': 'Attempting to switch to real mode',
        'client_status': fronius.get_status()
    })


# Enhanced Mock Client Endpoints
@app.route('/api/elderly/recommendations')
def get_elderly_recommendations():
    """Get elderly-specific recommendations from the enhanced mock client."""
    try:
        recommendations = fronius.get_elderly_recommendations()
        return jsonify(recommendations)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/elderly/advice')
def get_elderly_advice():
    """Get contextual advice for elderly users based on current energy situation."""
    try:
        power_data = fronius.get_power_data()
        if 'elderly_advice_context' in power_data:
            return jsonify({
                'status': 'success',
                'advice_context': power_data['elderly_advice_context'],
                'current_energy': {
                    'solar_power': power_data['P_PV'],
                    'consumption': power_data['P_Load'],
                    'grid_power': power_data['P_Grid']
                }
            })
        else:
            return jsonify({
                'status': 'limited',
                'message': 'Enhanced advice only available in mock mode',
                'basic_advice': 'Consult your energy dashboard for current status'
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/elderly/optimal-timing')
def get_optimal_timing():
    """Get optimal timing for elderly appliances based on weather forecast."""
    try:
        power_data = fronius.get_power_data()
        if 'elderly_advice_context' in power_data:
            advice_context = power_data['elderly_advice_context']
            return jsonify({
                'status': 'success',
                'optimal_timing': advice_context.get('optimal_appliance_timing', {}),
                'weather_advice': advice_context.get('weather_advice', ''),
                'energy_situation': advice_context.get('energy_situation', 'balanced')
            })
        else:
            return jsonify({
                'status': 'limited',
                'message': 'Enhanced timing only available in mock mode',
                'general_advice': 'Best hours are typically 12:00-15:00 for solar energy'
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/enhanced-mock/status')
def get_enhanced_mock_status():
    """Get status of the enhanced mock system including weather integration."""
    try:
        status = fronius.get_status()
        
        # If using enhanced mock, get additional information
        if not status.get('using_real_data', False):
            # Get weather service status
            weather_service = energy_optimizer.weather_service
            
            # Check if weather data is available
            try:
                conn = sqlite3.connect('parra_energy/data/energy_data.db')
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM weather_daily WHERE date >= date('now')")
                weather_count = cursor.fetchone()[0]
                conn.close()
                
                weather_status = {
                    'weather_data_available': weather_count > 0,
                    'weather_entries': weather_count,
                    'coordinates': {
                        'latitude': weather_service.latitude,
                        'longitude': weather_service.longitude
                    }
                }
            except Exception:
                weather_status = {
                    'weather_data_available': False,
                    'weather_entries': 0
                }
            
            status['enhanced_mock_features'] = {
                'weather_integration': weather_status,
                'elderly_advice': True,
                'historical_patterns': True,
                'optimal_timing': True
            }
        
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Run the Flask application
    # debug=True enables auto-reload on code changes
    # host='0.0.0.0' makes the server accessible from other devices
    app.run(debug=True, host='0.0.0.0', port=5001) 
# Manual Control Endpoints for Testing Specific Cases
@app.route('/api/mock/set-solar-percentage', methods=['POST'])
def set_solar_percentage():
    print("🔧 DEBUG: Received set-solar-percentage request")
    """Set manual solar production percentage for testing specific cases."""
    try:
        data = request.get_json()
        percentage = data.get('percentage')
        
        if percentage is None:
            fronius.set_manual_solar_percentage(None)
            return jsonify({
                'status': 'success',
                'message': 'Solar production set to automatic mode',
                'percentage': None
            })
        
        percentage = float(percentage)
        fronius.set_manual_solar_percentage(percentage)
        
        return jsonify({
            'status': 'success',
            'message': f'Solar production set to {percentage}% of maximum capacity',
            'percentage': percentage
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mock/set-consumption', methods=['POST'])
def set_consumption():
    print("🔧 DEBUG: Received set-consumption request")
    """Set manual consumption for testing specific cases."""
    try:
        data = request.get_json()
        watts = data.get('watts')
        
        if watts is None:
            fronius.set_manual_consumption_watts(None)
            return jsonify({
                'status': 'success',
                'message': 'Consumption set to automatic mode',
                'watts': None
            })
        
        watts = float(watts)
        fronius.set_manual_consumption_watts(watts)
        
        return jsonify({
            'status': 'success',
            'message': f'Consumption set to {watts}W',
            'watts': watts
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mock/get-manual-controls')
def get_manual_controls():
    """Get current manual control settings."""
    try:
        controls = fronius.get_manual_controls()
        return jsonify(controls)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mock/reset-controls', methods=['POST'])
def reset_manual_controls():
    """Reset all manual controls to automatic mode."""
    try:
        fronius.reset_manual_controls()
        return jsonify({
            'status': 'success',
            'message': 'All manual controls reset to automatic mode'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mock/test-scenario', methods=['POST'])
def test_scenario():
    """Set up a specific test scenario with predefined solar and consumption values."""
    try:
        data = request.get_json()
        scenario = data.get('scenario', 'balanced')
        
        scenarios = {
            'excess_solar': {'solar_percentage': 80, 'consumption_watts': 500, 'name': 'Excess Solar Production'},
            'balanced': {'solar_percentage': 40, 'consumption_watts': 2000, 'name': 'Balanced Energy'},
            'high_consumption': {'solar_percentage': 20, 'consumption_watts': 3000, 'name': 'High Consumption'},
            'zero_solar': {'solar_percentage': 0, 'consumption_watts': 1500, 'name': 'No Solar (Night)'},
            'peak_production': {'solar_percentage': 100, 'consumption_watts': 800, 'name': 'Peak Solar Production'},
            'morning_routine': {'solar_percentage': 15, 'consumption_watts': 1800, 'name': 'Morning Routine'},
            'evening_cooking': {'solar_percentage': 5, 'consumption_watts': 2500, 'name': 'Evening Cooking'}
        }
        
        if scenario not in scenarios:
            return jsonify({'error': 'Unknown scenario'}), 400
        
        scenario_config = scenarios[scenario]
        
        # Set the scenario
        fronius.set_manual_solar_percentage(scenario_config['solar_percentage'])
        fronius.set_manual_consumption_watts(scenario_config['consumption_watts'])
        
        return jsonify({
            'status': 'success',
            'scenario': scenario,
            'name': scenario_config['name'],
            'solar_percentage': scenario_config['solar_percentage'],
            'consumption_watts': scenario_config['consumption_watts'],
            'message': f'Test scenario "{scenario_config["name"]}" activated'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

