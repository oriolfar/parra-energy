"""
Parra Energy Web Dashboard - Flask Application
==============================================

This module provides the main web interface for the Parra Energy solar monitoring
and automation system. It serves a real-time dashboard that displays and controls:

REAL-TIME MONITORING:
- Solar production from Fronius inverter
- Household energy consumption  
- Grid power flow (import/export)
- Energy efficiency metrics

SMART FEATURES:
- Automatic device control based on solar surplus
- Weather-aware energy optimization
- Personalized recommendations for elderly users
- Historical data analysis and trends

DUAL INTERFACE MODES:
- Technical Mode: Detailed metrics and controls for energy-savvy users
- Elderly Mode: Simplified interface with basic advice in Catalan

BACKEND ARCHITECTURE:
- Flask web server for API and template serving
- SQLite database for historical data storage
- Background thread for continuous data collection
- Smart client system (real inverter + mock fallback)
- Weather integration via Open-Meteo API

DATA COLLECTION CYCLE:
- 5-second polling for real-time updates
- 5-minute averaging for database storage
- Automatic fallback between real and mock data
- Continuous background operation

SYSTEM CONFIGURATION:
- Target: Fronius inverter at 192.168.1.128
- Solar capacity: 2.2kW (2200W peak)
- Database: SQLite (data/energy_data.db)
- Web port: 5001
- Update frequency: 5 seconds
"""

# =============================================================================
# IMPORTS AND SYSTEM SETUP
# =============================================================================

import sys
import os
import sqlite3
import threading
import time
import atexit
from datetime import datetime, timedelta

# Add parent directories to path for module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Flask web framework imports
from flask import Flask, render_template, jsonify, request, session

# Parra Energy system components
from api.smart_fronius import SmartFroniusClient
from automations.manager import AutomationManager
from analytics.optimizer import EnergyOptimizer
from config.settings import Config
from utils.logger import setup_logger, log_system_info
from utils.database import DatabaseManager

# =============================================================================
# FLASK APPLICATION INITIALIZATION
# =============================================================================

# Initialize Flask application with template and static file configuration
app = Flask(__name__)

# Set secret key for session management (change in production!)
# Used for storing user preferences like dashboard mode (technical/elderly)
app.secret_key = 'super_secret_key_for_parra_energy'  # TODO: Use environment variable in production

# Load configuration to check quiet mode
config = Config()
if not config.logging.quiet_mode:
    print("🔧 Initializing Parra Energy system components...")

# =============================================================================
# CORE SYSTEM COMPONENTS
# =============================================================================

# Initialize Smart Fronius Client
# This automatically detects if real inverter is available at 192.168.1.128
# Falls back to enhanced mock with real weather data if unavailable
fronius = SmartFroniusClient(host="192.168.1.128")
print("✅ Smart Fronius client initialized (auto-detection enabled)")

# Initialize Automation Manager
# Handles automatic control of household devices based on solar surplus
automation_manager = AutomationManager()
print("✅ Automation manager initialized")

# Initialize Energy Analytics & Optimization Engine
# Provides historical analysis and personalized recommendations
energy_optimizer = EnergyOptimizer('data/energy_data.db')
print("✅ Energy optimizer initialized")

# =============================================================================
# BACKGROUND DATA COLLECTION SYSTEM
# =============================================================================

def background_fetcher():
    """
    Background thread for continuous data collection and database storage.
    
    This function runs continuously in a separate thread to:
    1. Poll Fronius inverter every 5 seconds for real-time data
    2. Buffer data points for 5-minute averaging
    3. Store averaged data to SQLite database  
    4. Provide uninterrupted data flow for the web interface
    
    Data Flow:
    - Real-time: 5-second intervals (displayed on dashboard)
    - Historical: 5-minute averages (stored in database)
    - Buffering: 60 data points = 5 minutes of data
    
    Error Handling:
    - Automatic retry on connection failures
    - Graceful fallback between real and mock data
    - Continuous operation even with temporary errors
    """
    print("📡 Background data collection thread started")
    local_buffer = []  # Buffer to store 5-second readings before averaging
    
    while True:
        try:
            # Get current power data from Fronius (real or mock)
            power_data = fronius.get_power_data()
            
            # Log real-time data for debugging (only in non-quiet mode)
            if not config.logging.quiet_mode:
                print(f"[FETCH] {datetime.now().isoformat()} - "
                      f"Production: {power_data.get('P_PV', 0):,.0f}W, "
                      f"Consumption: {power_data.get('P_Load', 0):,.0f}W")
            
            # Add current reading to buffer
            local_buffer.append({
                'production': float(power_data.get('P_PV', 0)),
                'consumption': float(power_data.get('P_Load', 0))
            })
            
            # When buffer reaches 60 readings (5 minutes), calculate averages and save
            if len(local_buffer) >= 60:  # 60 * 5s = 5min
                # Calculate 5-minute averages
                avg_prod = sum(x['production'] for x in local_buffer) / len(local_buffer)
                avg_cons = sum(x['consumption'] for x in local_buffer) / len(local_buffer)
                
                # Create timestamp aligned to 5-minute boundaries
                ts = datetime.now().replace(
                    second=0, 
                    microsecond=0, 
                    minute=(datetime.now().minute // 5) * 5
                )
                
                print(f"[AVERAGE] {ts.isoformat()} - "
                      f"Avg Production: {avg_prod:,.0f}W, "
                      f"Avg Consumption: {avg_cons:,.0f}W")
                
                # Save averaged data to database
                try:
                    conn = sqlite3.connect('data/energy_data.db')
                    c = conn.cursor()
                    c.execute(
                        'INSERT OR REPLACE INTO energy (timestamp, production, consumption) VALUES (?, ?, ?)',
                        (ts.isoformat(), avg_prod, avg_cons)
                    )
                    conn.commit()
                    conn.close()
                    print(f"[DB SAVE] {ts.isoformat()} - Successfully saved to database")
                except Exception as db_error:
                    print(f"[DB ERROR] Failed to save data: {db_error}")
                
                # Clear buffer for next 5-minute cycle
                local_buffer.clear()
            
            # Wait 5 seconds before next reading
            time.sleep(5)
            
        except Exception as e:
            print(f"[FETCH ERROR] Background fetch error: {e}")
            print("🔄 Retrying in 5 seconds...")
            time.sleep(5)

# Start background data collection thread
# daemon=True ensures thread stops when main program exits
print("🚀 Starting background data collection...")
fetcher_thread = threading.Thread(target=background_fetcher, daemon=True)
fetcher_thread.start()

# Register cleanup function to gracefully stop background thread on exit
atexit.register(lambda: fetcher_thread.join(timeout=1))

print("✅ Background data collection started successfully")
print("🌐 Web server initialization complete")

# =============================================================================
# MAIN WEB ROUTES
# =============================================================================

@app.route('/')
def index():
    """
    Main dashboard route - serves appropriate interface based on user mode.
    
    The system supports two dashboard modes stored in user session:
    
    TECHNICAL MODE (default):
    - Detailed energy metrics and charts
    - Manual testing controls (sliders, scenarios)
    - Advanced analytics and device management
    - Full system information and debugging tools
    
    ELDERLY MODE:
    - Simplified interface in Catalan language
    - Large fonts and easy-to-understand advice
    - Focus on actionable recommendations
    - Minimal complexity and clear guidance
    
    Mode switching is handled via a toggle switch in the top-right corner
    of both interfaces, styled like a light/dark mode toggle.
    
    Returns:
        Rendered HTML template (elderly.html or technical.html)
    """
    # Get current dashboard mode from session (defaults to technical)
    mode = session.get('dashboard_mode', 'technical')
    
    # Log dashboard requests only in non-quiet mode
    if not config.logging.quiet_mode:
        print(f"📱 Dashboard request - Mode: {mode}")
    
    if mode == 'elderly':
        return render_template('elderly.html', mode=mode)
    else:
        return render_template('technical.html', mode=mode)

@app.route('/api/status')
def get_status():
    """
    Main API endpoint for real-time system status.
    
    This endpoint is called every 5 seconds by the frontend JavaScript
    to update the dashboard with current readings. It provides:
    
    POWER DATA:
    - P_PV: Solar production (watts)
    - P_Load: House consumption (watts)  
    - P_Grid: Grid power (+ importing, - exporting)
    - Derived metrics: self-consumption, autonomy percentages
    
    AUTOMATION STATUS:
    - List of all managed devices
    - Current on/off status of each device
    - Power consumption of each device
    - Available solar surplus for automation
    
    CLIENT STATUS:
    - Whether using real or mock data
    - Connection status to Fronius inverter
    - Fallback mode information
    
    Returns:
        JSON response with complete system status
    """
    try:
        # Get current power readings from Fronius (real or mock)
        power_data = fronius.get_power_data()
        
        # Update automation system with current power data
        # This triggers device on/off decisions based on solar surplus
        automation_manager.update(power_data)
        automation_status = automation_manager.get_status()
        
        # Get information about data source (real vs mock)
        client_status = fronius.get_status()
        
        # Log API call for debugging (only in non-quiet mode)
        if not config.logging.quiet_mode:
            print(f"[API] Status request - "
                  f"Solar: {power_data.get('P_PV', 0):,.0f}W, "
                  f"Load: {power_data.get('P_Load', 0):,.0f}W, "
                  f"Grid: {power_data.get('P_Grid', 0):+,.0f}W")
        
        return jsonify({
            'power_data': power_data,
            'automation': automation_status,
            'client_status': client_status
        })
        
    except Exception as e:
        print(f"[API ERROR] Status endpoint error: {e}")
        return jsonify({'error': str(e)}), 500

# =============================================================================
# DEBUGGING AND DATA EXPORT ROUTES
# =============================================================================

@app.route('/debug/all')
def debug_all():
    """
    Development endpoint to dump all database records.
    
    Returns all energy records from the database for debugging purposes.
    Useful for verifying data collection and troubleshooting issues.
    
    Returns:
        JSON array of all energy records with timestamps, production, consumption
    """
    try:
        db = sqlite3.connect('data/energy_data.db')
        db.row_factory = sqlite3.Row
        rows = db.execute('SELECT * FROM energy ORDER BY timestamp').fetchall()
        return jsonify([dict(row) for row in rows])
    except Exception as e:
        print(f"[DEBUG ERROR] Failed to fetch debug data: {e}")
        return jsonify({'error': str(e)}), 500

# =============================================================================
# HISTORICAL DATA AND ANALYTICS ROUTES
# =============================================================================

@app.route('/history/<date>')
def history(date):
    """
    Get historical energy data for a specific date, aggregated by hour.
    
    This endpoint provides hourly energy data for charting and analysis.
    It takes 5-minute database records and aggregates them into hourly
    totals for easier visualization and reduced data transfer.
    
    Args:
        date: Date string in YYYY-MM-DD format
        
    Data Processing:
    1. Fetches all 5-minute records for the specified date
    2. Groups records by hour (0-23)
    3. Converts watts to kWh: (watts * 5_minutes/60_minutes) / 1000
    4. Calculates self-consumption (min of production/consumption)
    5. Calculates grid import (excess consumption over production)
    
    Returns:
        JSON array with hourly data:
        - hour: Hour of day (0-23)
        - production: Solar production (kWh)
        - consumption: House consumption (kWh)
        - self_consumed: Energy used directly from solar (kWh)
        - from_grid: Energy imported from grid (kWh)
    """
    try:
        # Parse and validate date parameter
        day = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD", 400
    
    try:
        # Connect to database and set up row factory for dict-like access
        db = sqlite3.connect('data/energy_data.db')
        db.row_factory = sqlite3.Row
        
        # Define time bounds for the requested date
        start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        
        # Fetch all 5-minute records for the date
        rows = db.execute(
            'SELECT timestamp, production, consumption FROM energy WHERE timestamp >= ? AND timestamp < ?',
            (start.isoformat(), end.isoformat())
        ).fetchall()
        
        print(f"[HISTORY] {len(rows)} records fetched for {date}")
        
        # Initialize hourly aggregation buckets (24 hours)
        hourly = [{'hour': h, 'production': 0, 'consumption': 0, 'count': 0} for h in range(24)]
        
        # Aggregate 5-minute records into hourly totals
        for row in rows:
            ts = datetime.fromisoformat(row['timestamp'])
            h = ts.hour
            
            # Convert watts to kWh for 5-minute period: (W * 5/60) / 1000
            hourly[h]['production'] += row['production'] * 5 / 60 / 1000
            hourly[h]['consumption'] += row['consumption'] * 5 / 60 / 1000
            hourly[h]['count'] += 1
        
        # Build chart data with energy flow calculations
        chart_data = []
        for h in hourly:
            prod = h['production']  # kWh produced this hour
            cons = h['consumption']  # kWh consumed this hour
            
            # Calculate energy flows
            green = min(prod, cons)  # Self-consumed: energy used directly from solar
            red = max(0, cons - prod)  # Grid import: energy needed beyond solar
            
            chart_data.append({
                'hour': h['hour'],
                'production': prod,
                'consumption': cons,
                'self_consumed': green,
                'from_grid': red
            })
            
            # Debug logging for each hour
            if h['count'] > 0:  # Only log hours with data
                print(f"[HOUR {h['hour']:02d}] Prod: {prod:.2f}kWh, "
                      f"Cons: {cons:.2f}kWh, Self: {green:.2f}kWh, Grid: {red:.2f}kWh")
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"[HISTORY ERROR] Failed to process history for {date}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/history5min/<date>')
def history5min(date):
    """
    Get detailed 5-minute resolution energy data for a specific date.
    
    This endpoint provides high-resolution data for detailed analysis
    and fine-grained charting. Unlike the hourly endpoint, this returns
    individual 5-minute records with precise timestamps.
    
    Args:
        date: Date string in YYYY-MM-DD format
        
    Returns:
        JSON array with 5-minute records:
        - timestamp: ISO timestamp of the 5-minute period
        - production: Solar production (kWh for 5-minute period)
        - consumption: House consumption (kWh for 5-minute period)
        - self_consumed: Energy used directly from solar (kWh)
        - from_grid: Energy imported from grid (kWh)
    """
    try:
        # Parse and validate date parameter
        day = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD", 400
    
    try:
        # Connect to database
        db = sqlite3.connect('data/energy_data.db')
        db.row_factory = sqlite3.Row
        
        # Define time bounds for the requested date
        start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        
        # Fetch all 5-minute records for the date
        rows = db.execute(
            'SELECT timestamp, production, consumption FROM energy WHERE timestamp >= ? AND timestamp < ?',
            (start.isoformat(), end.isoformat())
        ).fetchall()
        
        # Convert each record to kWh and calculate energy flows
        data = []
        for row in rows:
            # Convert watts to kWh for 5-minute period: (W * 5/60) / 1000
            prod = row['production'] * 5 / 60 / 1000  # kWh for 5min period
            cons = row['consumption'] * 5 / 60 / 1000
            
            # Calculate energy flows
            green = min(prod, cons)  # Self-consumed: energy used directly from solar
            red = max(0, cons - prod)  # Grid import: energy needed beyond solar
            
            data.append({
                'timestamp': row['timestamp'],
                'production': prod,
                'consumption': cons,
                'self_consumed': green,
                'from_grid': red
            })
        
        print(f"[HISTORY5MIN] {len(data)} 5-minute records returned for {date}")
        return jsonify(data)
        
    except Exception as e:
        print(f"[HISTORY5MIN ERROR] Failed to fetch 5-minute data for {date}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/export/<date>')
def export_csv(date):
    """
    Export energy data for a specific date as CSV file.
    
    This endpoint generates a downloadable CSV file containing all
    energy records for the specified date. Useful for external analysis,
    reporting, or backup purposes.
    
    Args:
        date: Date string in YYYY-MM-DD format
        
    Returns:
        CSV file with columns:
        - timestamp: ISO timestamp
        - production_W: Solar production in watts
        - consumption_W: House consumption in watts
    """
    try:
        # Parse and validate date parameter
        day = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD", 400
    
    try:
        # Connect to database
        db = sqlite3.connect('data/energy_data.db')
        db.row_factory = sqlite3.Row
        
        # Define time bounds for the requested date
        start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        
        # Fetch all records for the date
        rows = db.execute(
            'SELECT timestamp, production, consumption FROM energy WHERE timestamp >= ? AND timestamp < ?',
            (start.isoformat(), end.isoformat())
        ).fetchall()
        
        # Generate CSV content
        import csv
        from io import StringIO
        
        si = StringIO()
        cw = csv.writer(si)
        
        # Write CSV header
        cw.writerow(['timestamp', 'production_W', 'consumption_W'])
        
        # Write data rows
        for row in rows:
            cw.writerow([row['timestamp'], row['production'], row['consumption']])
        
        output = si.getvalue()
        
        print(f"[EXPORT] CSV generated for {date} - {len(rows)} records")
        return output, 200, {'Content-Type': 'text/csv'}
        
    except Exception as e:
        print(f"[EXPORT ERROR] Failed to generate CSV for {date}: {e}")
        return f"Error generating CSV: {e}", 500

# =============================================================================
# ANALYTICS AND OPTIMIZATION ENDPOINTS
# =============================================================================

@app.route('/api/analytics/tips')
def get_optimization_tips():
    """
    Get personalized energy optimization tips based on historical data analysis.
    
    This endpoint leverages the EnergyOptimizer to analyze usage patterns
    and provide actionable recommendations for improving energy efficiency.
    
    Query Parameters:
        days (int): Number of days to analyze (default: 30)
        
    Analytics Process:
    1. Analyzes historical production and consumption patterns
    2. Identifies inefficiencies and opportunities
    3. Generates personalized recommendations with priority levels
    4. Calculates potential energy/cost savings
    
    Returns:
        JSON response with:
        - tips: Array of optimization recommendations
        - Each tip includes: tip text, priority, potential savings, category
        - generated_at: Timestamp of analysis
        - analysis_period_days: Number of days analyzed
    """
    try:
        # Get analysis period from query parameter (default: 30 days)
        days = request.args.get('days', default=30, type=int)
        
        # Generate optimization tips using historical data
        tips = energy_optimizer.get_optimization_tips(days)
        
        # Format tips for JSON response
        formatted_tips = []
        for tip in tips:
            formatted_tips.append({
                'tip': tip.tip,
                'priority': tip.priority,  # 'high', 'medium', 'low'
                'potential_savings': tip.potential_savings,  # kWh/day
                'category': tip.category  # 'timing', 'efficiency', 'waste_reduction'
            })
        
        print(f"[ANALYTICS] Generated {len(formatted_tips)} optimization tips for {days} days")
        
        return jsonify({
            'tips': formatted_tips,
            'generated_at': datetime.now().isoformat(),
            'analysis_period_days': days
        })
        
    except Exception as e:
        print(f"[ANALYTICS ERROR] Failed to generate optimization tips: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/daily-report')
@app.route('/api/analytics/daily-report/<date>')
def get_daily_report(date=None):
    """
    Get comprehensive daily energy report for analysis and review.
    
    This endpoint provides detailed metrics for a specific date,
    including production, consumption, efficiency metrics, and
    personalized recommendations.
    
    Args:
        date (optional): Date in YYYY-MM-DD format (defaults to today)
        
    Report Contents:
    - Energy production and consumption totals
    - Self-consumption and autonomy percentages
    - Grid import/export volumes
    - Weather correlation data
    - Efficiency scoring and grade
    - Specific recommendations for improvement
    
    Returns:
        JSON response with comprehensive daily metrics and analysis
    """
    try:
        # Generate daily report (uses today if no date specified)
        report = energy_optimizer.get_daily_report(date)
        
        report_date = date or datetime.now().strftime('%Y-%m-%d')
        print(f"[ANALYTICS] Daily report generated for {report_date}")
        
        return jsonify(report)
        
    except Exception as e:
        print(f"[ANALYTICS ERROR] Failed to generate daily report for {date}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/weekly-forecast')
def get_weekly_forecast():
    """
    Get weekly energy forecast and planning recommendations.
    
    This endpoint combines weather forecasting with historical usage
    patterns to provide predictive insights for energy planning.
    
    Forecast Components:
    - 7-day solar production forecast based on weather
    - Expected consumption patterns from historical data
    - Optimal timing recommendations for high-energy activities
    - Weather-aware energy planning advice
    
    Returns:
        JSON response with:
        - Daily forecasts for the upcoming week
        - Recommended timing for appliances
        - Weather-based planning suggestions
        - Expected energy balance for each day
    """
    try:
        # Generate weekly forecast with weather integration
        forecast = energy_optimizer.get_weekly_forecast()
        
        print("[ANALYTICS] Weekly forecast generated with weather integration")
        
        return jsonify(forecast)
        
    except Exception as e:
        print(f"[ANALYTICS ERROR] Failed to generate weekly forecast: {e}")
        return jsonify({'error': str(e)}), 500

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

# =============================================================================
# WEATHER INTEGRATION ENDPOINTS
# =============================================================================

@app.route('/api/weather/forecast')
def get_weather_forecast():
    """
    Get comprehensive weather forecast for solar energy planning.
    
    This endpoint provides weather data specifically tailored for solar
    energy optimization, including solar production forecasts and
    optimal timing recommendations.
    
    Query Parameters:
        days (int): Number of forecast days (default: 7)
        
    Weather Data Sources:
    - Open-Meteo API for Agramunt, Spain coordinates
    - Real-time weather conditions and forecasts
    - Solar radiation and UV index data
    - Temperature and daylight duration
    
    Returns:
        JSON response with:
        - weekly_forecast: Array of daily weather and solar forecasts
        - Each day includes: date, sunrise/sunset, daylight hours, temperatures
        - Solar production forecasts and quality ratings
        - Weather-based energy planning recommendations
    """
    try:
        # Get forecast period from query parameter (default: 7 days)
        days = request.args.get('days', default=7, type=int)
        
        # Get the weather service from the energy optimizer
        weather_service = energy_optimizer.weather_service
        
        # Fetch fresh weather data from Open-Meteo API
        weather_data = weather_service.fetch_weather_forecast(days)
        if not weather_data:
            return jsonify({'error': 'Could not fetch weather data from Open-Meteo API'}), 500
        
        # Get processed weekly summary with solar forecasts
        weekly_summary = weather_service.get_weekly_weather_summary()
        if weekly_summary is None:
            return jsonify({'error': 'No weather summary available'}), 500
        
        # Convert DataFrame to JSON-serializable format for frontend
        weekly_data = []
        for _, row in weekly_summary.iterrows():
            weekly_data.append({
                'date': row['date'],
                'sunrise': row['sunrise'],
                'sunset': row['sunset'],
                'daylight_hours': round(row['daylight_duration'] / 3600, 2),  # Convert seconds to hours
                'uv_index_max': row['uv_index_max'],
                'temperature_max': row['temperature_max'],
                'temperature_min': row['temperature_min'],
                'solar_production_forecast': row['solar_production_forecast'],  # Expected kWh
                'weather_quality_score': row['weather_quality_score'],  # 0-100 score
                'quality_rating': row['quality_rating'],  # 'Excellent', 'Good', etc.
                'production_category': row['production_category']  # 'High', 'Medium', 'Low'
            })
        
        print(f"[WEATHER] Forecast generated for {days} days from Agramunt, Spain")
        
        return jsonify({
            'weekly_forecast': weekly_data,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"[WEATHER ERROR] Failed to fetch weather forecast: {e}")
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
                conn = sqlite3.connect('data/energy_data.db')
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
# =============================================================================
# MOCK SYSTEM CONTROL ENDPOINTS FOR TESTING AND DEMOS
# =============================================================================

@app.route('/api/mock/set-solar-percentage', methods=['POST'])
def set_solar_percentage():
    """
    Manually set solar production percentage for testing specific scenarios.
    
    This endpoint allows manual override of solar production when using
    the mock system, enabling testing of various energy scenarios without
    waiting for real weather conditions.
    
    POST Body:
        percentage (float): Solar production as percentage of max capacity (0-100)
                           Set to null/None to return to automatic mode
                           
    Solar Calculation:
    - 0%: No solar production (night/cloudy)
    - 50%: 1100W (50% of 2200W max capacity)
    - 100%: 2200W (peak production)
    
    Use Cases:
    - Testing automation logic with different solar levels
    - Demonstrating system behavior in various conditions
    - Training users on energy management
    - Debugging energy flow calculations
    
    Returns:
        JSON response with status, message, and applied percentage
    """
    print("🔧 DEBUG: Received set-solar-percentage request")
    
    try:
        data = request.get_json()
        percentage = data.get('percentage')
        
        if percentage is None:
            # Return to automatic weather-based production
            fronius.set_manual_solar_percentage(None)
            print("🔧 MANUAL CONTROL: Solar production set to automatic mode")
            return jsonify({
                'status': 'success',
                'message': 'Solar production set to automatic weather-based mode',
                'percentage': None
            })
        
        # Set manual solar percentage (0-100%)
        percentage = float(percentage)
        fronius.set_manual_solar_percentage(percentage)
        
        watts = (percentage / 100) * 2200  # Convert percentage to watts (2200W max)
        print(f"🔧 MANUAL CONTROL: Solar set to {percentage}% ({watts:.0f}W)")
        
        return jsonify({
            'status': 'success',
            'message': f'Solar production set to {percentage}% of maximum capacity ({watts:.0f}W)',
            'percentage': percentage,
            'watts': watts
        })
        
    except Exception as e:
        print(f"🔧 MANUAL CONTROL ERROR: Failed to set solar percentage: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/mock/set-consumption', methods=['POST'])
def set_consumption():
    """
    Manually set household consumption for testing specific scenarios.
    
    This endpoint allows manual override of consumption patterns when using
    the mock system, enabling testing of various household energy scenarios.
    
    POST Body:
        watts (float): Consumption in watts
                       Set to null/None to return to automatic patterns
                       
    Consumption Ranges:
    - Minimum: 100W (base load - lights, standby devices)
    - Typical: 500-1500W (normal household usage)
    - High: 2000-3000W (cooking, heating, multiple appliances)
    - Maximum: 5000W (extreme usage scenario)
    
    Use Cases:
    - Testing grid import/export scenarios
    - Demonstrating self-consumption optimization
    - Training on appliance timing
    - Debugging consumption-based automation
    
    Returns:
        JSON response with status, message, and applied consumption
    """
    print("🔧 DEBUG: Received set-consumption request")
    
    try:
        data = request.get_json()
        watts = data.get('watts')
        
        if watts is None:
            # Return to automatic consumption patterns
            fronius.set_manual_consumption_watts(None)
            print("🔧 MANUAL CONTROL: Consumption set to automatic patterns")
            return jsonify({
                'status': 'success',
                'message': 'Consumption set to automatic household patterns',
                'watts': None
            })
        
        # Set manual consumption in watts
        watts = float(watts)
        fronius.set_manual_consumption_watts(watts)
        
        print(f"🔧 MANUAL CONTROL: Consumption set to {watts:.0f}W")
        
        return jsonify({
            'status': 'success',
            'message': f'Consumption set to {watts:.0f}W',
            'watts': watts
        })
        
    except Exception as e:
        print(f"🔧 MANUAL CONTROL ERROR: Failed to set consumption: {e}")
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

# Enhanced: Mode switching for dashboards
@app.route('/switch_mode', methods=['POST'])
def switch_mode():
    current_mode = session.get('dashboard_mode', 'technical')
    new_mode = 'elderly' if current_mode == 'technical' else 'technical'
    session['dashboard_mode'] = new_mode
    return jsonify({'mode': new_mode})

