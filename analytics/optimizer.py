"""
Energy Analytics and Optimization Module - Intelligent Energy Analysis System
============================================================================

This module provides sophisticated analysis of historical energy data to generate
personalized optimization recommendations, efficiency insights, and predictive
energy planning advice for solar energy systems.

CORE FUNCTIONALITY:
1. HISTORICAL DATA ANALYSIS:
   - Pattern recognition in production and consumption data
   - Statistical analysis of energy efficiency trends
   - Identification of optimization opportunities
   - Seasonal and weather correlation analysis

2. PERSONALIZED RECOMMENDATIONS:
   - Context-aware energy saving tips
   - Optimal timing suggestions for high-energy activities
   - Appliance usage optimization based on solar surplus
   - Priority-based recommendation system

3. EFFICIENCY METRICS:
   - Self-consumption rate calculations
   - Grid dependency analysis
   - Solar utilization efficiency
   - Energy independence scoring

4. WEATHER-AWARE FORECASTING:
   - Integration with real weather data for predictions
   - Solar production forecasting based on weather conditions
   - Optimal timing recommendations considering weather
   - Seasonal planning and adaptation strategies

5. ELDERLY USER SPECIALIZATION:
   - Simplified language recommendations in Catalan
   - Focus on practical, actionable advice
   - Consideration of typical elderly household patterns
   - Safety and comfort prioritization

ANALYTICS ALGORITHMS:
- Time-series analysis for pattern detection
- Statistical trend analysis and anomaly detection
- Machine learning-inspired optimization suggestions
- Weather correlation modeling for production forecasting

DATABASE INTEGRATION:
- Automatic analytics table creation and management
- Historical data aggregation and processing
- Daily, weekly, and monthly trend analysis
- Weather data correlation and storage

RECOMMENDATION ENGINE:
- Priority-based tip generation (high, medium, low)
- Category-based organization (timing, efficiency, waste reduction)
- Potential savings calculation in kWh/day
- Contextual advice based on current energy situation

This system enables users to maximize their solar energy efficiency through
data-driven insights and intelligent recommendations tailored to their
specific usage patterns and local weather conditions.
"""

import sqlite3
import statistics
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from dataclasses import dataclass

# Add parent directory to path for weather service import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from weather.weather_service import WeatherService


@dataclass
class EnergyInsight:
    """
    Data structure for energy optimization insights and recommendations.
    
    This class encapsulates individual energy optimization recommendations
    with metadata about their importance, potential impact, and categorization.
    
    Attributes:
        tip (str): Human-readable recommendation text in appropriate language
        priority (str): Importance level - 'high', 'medium', 'low'
        potential_savings (float): Estimated daily energy savings in kWh/day
        category (str): Recommendation type - 'timing', 'efficiency', 'waste_reduction'
        
    Priority Levels:
    - HIGH: Critical optimizations with significant impact (>2 kWh/day savings)
    - MEDIUM: Important improvements with moderate impact (0.5-2 kWh/day savings)
    - LOW: Minor optimizations with small impact (<0.5 kWh/day savings)
    
    Categories:
    - TIMING: Recommendations about when to use appliances for optimal solar utilization
    - EFFICIENCY: Suggestions for reducing overall energy consumption
    - WASTE_REDUCTION: Advice for eliminating unnecessary energy usage
    """
    tip: str                    # Recommendation text (localized for elderly users)
    priority: str              # 'high', 'medium', 'low' - impact level
    potential_savings: float   # Estimated daily savings in kWh
    category: str             # 'timing', 'efficiency', 'waste_reduction'


class EnergyOptimizer:
    """
    Intelligent energy optimization and analytics engine.
    
    This class provides comprehensive analysis of energy data to generate
    personalized recommendations, efficiency insights, and predictive
    planning advice for solar energy systems.
    """
    
    def __init__(self, db_path: str = 'data/energy_data.db'):
        """
        Initialize the energy optimizer with database and weather integration.
        
        Args:
            db_path: Path to SQLite database containing energy and weather data
            
        Initialization Process:
        1. Set up database connection and path
        2. Initialize weather service for forecasting capabilities
        3. Create or verify analytics database tables
        4. Prepare optimization algorithms and metrics
        """
        print("🧠 Initializing Energy Analytics & Optimization Engine")
        
        # Database configuration
        self.db_path = db_path
        print(f"   📊 Database: {db_path}")
        
        # Weather service integration for forecasting
        self.weather_service = WeatherService(db_path)
        print("   🌤️  Weather integration enabled for predictive analytics")
        
        # Initialize database tables for analytics storage
        self._init_analytics_tables()
        print("   📋 Analytics database tables initialized")
        
        print("✅ Energy Optimizer ready for intelligent analysis")
    
    def _init_analytics_tables(self):
        """
        Initialize additional database tables for analytics storage.
        
        This method creates specialized tables for storing processed analytics
        data, daily summaries, and optimization insights. These tables enable
        faster queries and better performance for dashboard and reporting.
        
        Tables Created:
        - daily_analytics: Daily aggregated metrics and efficiency scores
        - optimization_insights: Generated recommendations and tips
        - weather_correlations: Weather impact analysis on energy production
        - usage_patterns: Identified consumption patterns and trends
        """
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            print("   🔧 Creating analytics database tables...")
            
            # Daily analytics aggregation table
            c.execute('''CREATE TABLE IF NOT EXISTS daily_analytics (
                date TEXT PRIMARY KEY,                  -- Date in YYYY-MM-DD format
                total_production REAL,                  -- Total solar production (kWh)
                total_consumption REAL,                 -- Total house consumption (kWh)
                self_consumption_rate REAL,             -- Percentage of solar used directly
                grid_import REAL,                       -- Energy imported from grid (kWh)
                grid_export REAL,                       -- Energy exported to grid (kWh)
                efficiency_score REAL,                  -- Daily efficiency rating (0-100)
                weather_quality REAL,                   -- Weather quality score for the day
                optimization_potential REAL,            -- Estimated improvement potential
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # Optimization insights and recommendations table
            c.execute('''CREATE TABLE IF NOT EXISTS optimization_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,                              -- Date insight was generated
                tip_text TEXT,                          -- Recommendation text
                priority TEXT,                          -- high/medium/low priority
                category TEXT,                          -- timing/efficiency/waste_reduction
                potential_savings REAL,                 -- Estimated kWh/day savings
                confidence_score REAL,                  -- Algorithm confidence (0-1)
                applied BOOLEAN DEFAULT FALSE,          -- Whether user acted on tip
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # Weather correlation analysis table
            c.execute('''CREATE TABLE IF NOT EXISTS weather_correlations (
                date TEXT PRIMARY KEY,                  -- Date of analysis
                weather_score REAL,                     -- Weather quality (0-100)
                actual_production REAL,                 -- Actual solar production
                predicted_production REAL,              -- Weather-based prediction
                correlation_accuracy REAL,              -- Prediction accuracy
                seasonal_factor REAL,                   -- Seasonal adjustment factor
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # Usage pattern identification table
            c.execute('''CREATE TABLE IF NOT EXISTS usage_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT,                      -- morning/midday/evening/night
                hour_start INTEGER,                     -- Pattern start hour
                hour_end INTEGER,                       -- Pattern end hour
                avg_consumption REAL,                   -- Average consumption during pattern
                frequency REAL,                         -- How often pattern occurs
                optimization_opportunity REAL,          -- Potential for improvement
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            conn.commit()
            conn.close()
            
            print("   ✅ Analytics tables created successfully")
            
        except Exception as e:
            print(f"   ❌ Error creating analytics tables: {e}")
            # Continue operation even if analytics tables fail
            pass
    
    def analyze_historical_data(self, days: int = 30) -> Dict:
        """Analyze historical data for the last N days."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        # Get data for the last N days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        query = '''
        SELECT timestamp, production, consumption 
        FROM energy 
        WHERE timestamp >= ? AND timestamp < ?
        ORDER BY timestamp
        '''
        
        rows = conn.execute(query, (start_date.isoformat(), end_date.isoformat())).fetchall()
        conn.close()
        
        if not rows:
            return {"error": "No historical data available"}
        
        # Process data
        daily_data = {}
        hourly_patterns = {}
        
        for row in rows:
            ts = datetime.fromisoformat(row['timestamp'])
            date_key = ts.date().isoformat()
            hour_key = ts.hour
            
            # Daily aggregation
            if date_key not in daily_data:
                daily_data[date_key] = {
                    'production': 0, 'consumption': 0, 
                    'self_consumed': 0, 'from_grid': 0, 'to_grid': 0
                }
            
            # Hourly pattern aggregation
            if hour_key not in hourly_patterns:
                hourly_patterns[hour_key] = {'production': [], 'consumption': []}
            
            # Calculate 5-minute energy (kWh)
            prod_kwh = row['production'] * 5 / 60 / 1000
            cons_kwh = row['consumption'] * 5 / 60 / 1000
            
            daily_data[date_key]['production'] += prod_kwh
            daily_data[date_key]['consumption'] += cons_kwh
            
            # Calculate flows
            self_consumed = min(prod_kwh, cons_kwh)
            from_grid = max(0, cons_kwh - prod_kwh)
            to_grid = max(0, prod_kwh - cons_kwh)
            
            daily_data[date_key]['self_consumed'] += self_consumed
            daily_data[date_key]['from_grid'] += from_grid
            daily_data[date_key]['to_grid'] += to_grid
            
            # Hourly patterns
            hourly_patterns[hour_key]['production'].append(row['production'])
            hourly_patterns[hour_key]['consumption'].append(row['consumption'])
        
        return {
            'daily_data': daily_data,
            'hourly_patterns': hourly_patterns,
            'analysis_period': f"{start_date.date()} to {end_date.date()}",
            'total_days': len(daily_data)
        }
    
    def get_optimization_tips(self, days: int = 30) -> List[EnergyInsight]:
        """Generate personalized optimization tips based on historical data."""
        analysis = self.analyze_historical_data(days)
        
        if 'error' in analysis:
            return []
        
        tips = []
        daily_data = analysis['daily_data']
        hourly_patterns = analysis['hourly_patterns']
        
        # Calculate overall metrics
        total_production = sum(d['production'] for d in daily_data.values())
        total_consumption = sum(d['consumption'] for d in daily_data.values())
        total_self_consumed = sum(d['self_consumed'] for d in daily_data.values())
        total_from_grid = sum(d['from_grid'] for d in daily_data.values())
        total_to_grid = sum(d['to_grid'] for d in daily_data.values())
        
        # Calculate key metrics
        self_consumption_rate = (total_self_consumed / total_production * 100) if total_production > 0 else 0
        grid_dependency = (total_from_grid / total_consumption * 100) if total_consumption > 0 else 0
        waste_rate = (total_to_grid / total_production * 100) if total_production > 0 else 0
        
        # Generate tips based on patterns
        
        # 1. Self-consumption optimization
        if self_consumption_rate < 70:
            potential_savings = total_to_grid * 0.7  # Assume 70% can be optimized
            tips.append(EnergyInsight(
                tip=f"El vostre autoconsum és del {self_consumption_rate:.1f}%. Podeu millorar-lo utilizando més aparells durant les hores de més sol (10h-16h).",
                priority='high',
                potential_savings=potential_savings,
                category='efficiency'
            ))
        
        # 2. Best hours identification
        best_hours = self._find_best_usage_hours(hourly_patterns)
        if best_hours:
            tips.append(EnergyInsight(
                tip=f"Les millors hores per utilitzar aparells grossos són: {', '.join(map(str, best_hours))}h. Programeu la rentadora, rentaplats i aire condicionat per aquestes hores.",
                priority='high',
                potential_savings=total_from_grid * 0.3,
                category='timing'
            ))
        
        # 3. Grid dependency reduction
        if grid_dependency > 30:
            tips.append(EnergyInsight(
                tip=f"Depeneu de la xarxa un {grid_dependency:.1f}%. Intenteu desplaçar consums grans (cuinar, planxar, aire condicionat) a les hores de més sol.",
                priority='medium',
                potential_savings=total_from_grid * 0.2,
                category='waste_reduction'
            ))
        
        # 4. Seasonal recommendations
        seasonal_tip = self._get_seasonal_recommendations()
        if seasonal_tip:
            tips.append(seasonal_tip)
        
        # 5. Waste reduction
        if waste_rate > 50:
            tips.append(EnergyInsight(
                tip=f"Esteu venent el {waste_rate:.1f}% de l'energia solar. Considereu utilitzar més aparells durant el dia: rentadora, assecadora, bomba de calor de l'aigua.",
                priority='medium',
                potential_savings=total_to_grid * 0.4,
                category='waste_reduction'
            ))
        
        # 6. Weather-aware recommendations
        weather_tips = self._get_weather_aware_tips()
        tips.extend(weather_tips)
        
        # 7. Consumption pattern analysis
        pattern_tip = self._analyze_consumption_patterns(hourly_patterns)
        if pattern_tip:
            tips.append(pattern_tip)
        
        return sorted(tips, key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x.priority], reverse=True)
    
    def _find_best_usage_hours(self, hourly_patterns: Dict) -> List[int]:
        """Find the hours with best solar production vs consumption ratio."""
        best_hours = []
        
        for hour in range(24):
            if hour not in hourly_patterns:
                continue
            
            avg_prod = statistics.mean(hourly_patterns[hour]['production']) if hourly_patterns[hour]['production'] else 0
            avg_cons = statistics.mean(hourly_patterns[hour]['consumption']) if hourly_patterns[hour]['consumption'] else 0
            
            # Good hours: high production, potential for more consumption
            if avg_prod > 1000 and avg_prod > avg_cons * 1.5:  # 1kW+ production, 50% more than current consumption
                best_hours.append(hour)
        
        return sorted(best_hours)
    
    def _get_seasonal_recommendations(self) -> EnergyInsight:
        """Get seasonal recommendations based on current month."""
        current_month = datetime.now().month
        
        if current_month in [12, 1, 2]:  # Winter
            return EnergyInsight(
                tip="A l'hivern, les hores de sol són més curtes (10h-15h). Concentreu el consum d'aparells grans en aquest període.",
                priority='medium',
                potential_savings=2.0,
                category='timing'
            )
        elif current_month in [6, 7, 8]:  # Summer
            return EnergyInsight(
                tip="A l'estiu teniu molt més sol! Podeu utilitzar l'aire condicionat durant el dia (9h-18h) sense comprar energia de la xarxa.",
                priority='high',
                potential_savings=5.0,
                category='timing'
            )
        elif current_month in [3, 4, 5]:  # Spring
            return EnergyInsight(
                tip="A la primavera, les hores de sol augmenten. Ideal per començar a utilitzar més aparells durant el dia (9h-17h).",
                priority='medium',
                potential_savings=3.0,
                category='timing'
            )
        else:  # Autumn
            return EnergyInsight(
                tip="A la tardor, aprofiteu les hores de sol del migdia (11h-16h) abans que arribi l'hivern.",
                priority='medium',
                potential_savings=2.5,
                category='timing'
            )
    
    def _analyze_consumption_patterns(self, hourly_patterns: Dict) -> EnergyInsight:
        """Analyze consumption patterns and suggest improvements."""
        night_consumption = 0  # 22h-6h
        day_consumption = 0    # 10h-16h
        
        for hour in range(24):
            if hour not in hourly_patterns or not hourly_patterns[hour]['consumption']:
                continue
            
            avg_cons = statistics.mean(hourly_patterns[hour]['consumption'])
            
            if hour >= 22 or hour <= 6:  # Night hours
                night_consumption += avg_cons
            elif 10 <= hour <= 16:  # Best solar hours
                day_consumption += avg_cons
        
        if night_consumption > day_consumption:
            return EnergyInsight(
                tip="Consumiu més energia a la nit que durant el dia. Intenteu desplaçar alguns aparells (rentadora, rentaplats) a les hores de sol.",
                priority='high',
                potential_savings=night_consumption * 0.4 / 1000,  # Convert to kWh
                category='timing'
            )
        
        return None
    
    def get_weekly_forecast(self) -> Dict:
        """Generate weekly forecast and recommendations."""
        analysis = self.analyze_historical_data(days=14)  # Use 2 weeks for pattern
        
        if 'error' in analysis:
            return {"error": "Insufficient data for forecast"}
        
        hourly_patterns = analysis['hourly_patterns']
        
        # Calculate expected production and optimal consumption for next week
        weekly_forecast = []
        
        for day in range(7):  # Next 7 days
            date = datetime.now() + timedelta(days=day)
            day_forecast = {
                'date': date.strftime('%Y-%m-%d'),
                'day_name': date.strftime('%A'),
                'expected_production': 0,
                'optimal_consumption_hours': [],
                'recommendations': []
            }
            
            # Estimate production based on historical patterns
            for hour in range(24):
                if hour in hourly_patterns and hourly_patterns[hour]['production']:
                    avg_prod = statistics.mean(hourly_patterns[hour]['production'])
                    day_forecast['expected_production'] += avg_prod * 5 / 60 / 1000  # Convert to kWh
                    
                    if avg_prod > 1000:  # Good production hours
                        day_forecast['optimal_consumption_hours'].append(hour)
            
            # Generate daily recommendations
            if day_forecast['optimal_consumption_hours']:
                best_hours = day_forecast['optimal_consumption_hours']
                day_forecast['recommendations'].append(
                    f"Millors hores per aparells grans: {min(best_hours)}h-{max(best_hours)}h"
                )
            
            weekly_forecast.append(day_forecast)
        
        return {
            'weekly_forecast': weekly_forecast,
            'generated_at': datetime.now().isoformat()
        }
    
    def get_daily_report(self, date: str = None) -> Dict:
        """Generate a detailed daily report for a specific date."""
        if not date:
            date = datetime.now().date().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        # Get data for the specific day
        start_dt = datetime.strptime(date, '%Y-%m-%d')
        end_dt = start_dt + timedelta(days=1)
        
        query = '''
        SELECT timestamp, production, consumption 
        FROM energy 
        WHERE timestamp >= ? AND timestamp < ?
        ORDER BY timestamp
        '''
        
        rows = conn.execute(query, (start_dt.isoformat(), end_dt.isoformat())).fetchall()
        conn.close()
        
        if not rows:
            return {"error": f"No data available for {date}"}
        
        # Calculate daily metrics
        total_prod = 0
        total_cons = 0
        total_self_consumed = 0
        total_from_grid = 0
        total_to_grid = 0
        
        hourly_breakdown = {}
        
        for row in rows:
            ts = datetime.fromisoformat(row['timestamp'])
            hour = ts.hour
            
            # Convert to kWh
            prod_kwh = row['production'] * 5 / 60 / 1000
            cons_kwh = row['consumption'] * 5 / 60 / 1000
            
            total_prod += prod_kwh
            total_cons += cons_kwh
            
            # Calculate flows
            self_consumed = min(prod_kwh, cons_kwh)
            from_grid = max(0, cons_kwh - prod_kwh)
            to_grid = max(0, prod_kwh - cons_kwh)
            
            total_self_consumed += self_consumed
            total_from_grid += from_grid
            total_to_grid += to_grid
            
            # Hourly breakdown
            if hour not in hourly_breakdown:
                hourly_breakdown[hour] = {'production': 0, 'consumption': 0, 'self_consumed': 0}
            
            hourly_breakdown[hour]['production'] += prod_kwh
            hourly_breakdown[hour]['consumption'] += cons_kwh
            hourly_breakdown[hour]['self_consumed'] += self_consumed
        
        # Calculate efficiency metrics
        self_consumption_rate = (total_self_consumed / total_prod * 100) if total_prod > 0 else 0
        grid_dependency = (total_from_grid / total_cons * 100) if total_cons > 0 else 0
        energy_independence = 100 - grid_dependency
        
        # Calculate score (0-100)
        efficiency_score = (self_consumption_rate * 0.6 + energy_independence * 0.4)
        
        return {
            'date': date,
            'totals': {
                'production': round(total_prod, 2),
                'consumption': round(total_cons, 2),
                'self_consumed': round(total_self_consumed, 2),
                'from_grid': round(total_from_grid, 2),
                'to_grid': round(total_to_grid, 2)
            },
            'metrics': {
                'self_consumption_rate': round(self_consumption_rate, 1),
                'grid_dependency': round(grid_dependency, 1),
                'energy_independence': round(energy_independence, 1),
                'efficiency_score': round(efficiency_score, 1)
            },
            'hourly_breakdown': hourly_breakdown,
            'grade': self._calculate_grade(efficiency_score),
            'improvements': self._suggest_daily_improvements(self_consumption_rate, grid_dependency, total_to_grid)
        }
    
    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade based on efficiency score."""
        if score >= 90:
            return "A+ (Excel·lent!)"
        elif score >= 80:
            return "A (Molt bé!)"
        elif score >= 70:
            return "B (Bé)"
        elif score >= 60:
            return "C (Regular)"
        elif score >= 50:
            return "D (Millorable)"
        else:
            return "F (Necessita millores)"
    
    def _suggest_daily_improvements(self, self_consumption_rate: float, grid_dependency: float, to_grid: float) -> List[str]:
        """Suggest specific improvements for a day."""
        improvements = []
        
        if self_consumption_rate < 70:
            improvements.append("Intenteu utilitzar més aparells durant les hores de sol")
        
        if grid_dependency > 30:
            improvements.append("Desplaceu consums grans a les hores de més producció solar")
        
        if to_grid > 5:  # More than 5kWh sold
            improvements.append("Heu venut molta energia - considereu utilitzar més aparells durant el dia")
            
        if not improvements:
            improvements.append("Dia excel·lent! Continueu així!")
        
        return improvements
    
    def _get_weather_aware_tips(self) -> List[EnergyInsight]:
        """Generate weather-aware optimization tips."""
        tips = []
        
        try:
            # Fetch fresh weather data
            weather_forecast = self.weather_service.fetch_weather_forecast(7)
            if not weather_forecast:
                return tips
            
            # Get weekly weather summary
            weekly_summary = self.weather_service.get_weekly_weather_summary()
            if weekly_summary is None or weekly_summary.empty:
                return tips
            
            # Analyze next 3 days for actionable tips
            next_days = weekly_summary.head(3)
            
            # 1. Sunny day optimization
            excellent_days = next_days[next_days['weather_quality_score'] >= 85]
            if not excellent_days.empty:
                best_day = excellent_days.iloc[0]['date']
                tips.append(EnergyInsight(
                    tip=f"🌞 Dia excel·lent per la solar demà ({best_day})! Programeu la rentadora, assecadora i aparells grans per充分利用生产高峰。",
                    priority='high',
                    potential_savings=8.0,
                    category='timing'
                ))
            
            # 2. Cloudy day warnings
            poor_days = next_days[next_days['weather_quality_score'] < 50]
            if not poor_days.empty:
                poor_day = poor_days.iloc[0]['date']
                tips.append(EnergyInsight(
                    tip=f"☁️ Dia poc solar previst ({poor_day}). Reduïu el consum d'aparells grans i utilitzeu-los els dies anteriors o posteriors.",
                    priority='medium',
                    potential_savings=5.0,
                    category='timing'
                ))
            
            # 3. Temperature-based efficiency tips
            hot_days = next_days[next_days['temperature_max'] > 30]
            if not hot_days.empty:
                tips.append(EnergyInsight(
                    tip=f"🌡️ Temperatures altes previstes ({hot_days.iloc[0]['temperature_max']:.1f}°C). Els panells solars seran menys eficients. Utilitzeu l'aire condicionat durant les primeres hores del matí quan la producció és alta.",
                    priority='medium',
                    potential_savings=3.0,
                    category='efficiency'
                ))
            
            # 4. Best hours forecast
            today_best_hours = self.weather_service.get_best_hours_forecast()
            if today_best_hours and today_best_hours['peak_production_hours']:
                peak_hours = [str(h['hour']) for h in today_best_hours['peak_production_hours'][:3]]
                tips.append(EnergyInsight(
                    tip=f"⚡ Millors hores d'avui per màxima producció: {', '.join(peak_hours)}h. Aprofiteu per fer la bugada, planxar o carregar el cotxe elèctric.",
                    priority='high',
                    potential_savings=4.0,
                    category='timing'
                ))
            
        except Exception as e:
            print(f"Error generating weather tips: {e}")
        
        return tips
    
    def get_weather_enhanced_forecast(self, days: int = 7) -> Dict:
        """Get enhanced forecast combining energy patterns with weather predictions."""
        try:
            # Get weather forecast
            weather_forecast = self.weather_service.fetch_weather_forecast(days)
            if not weather_forecast:
                return {"error": "Could not fetch weather data"}
            
            # Get weekly weather summary
            weekly_summary = self.weather_service.get_weekly_weather_summary()
            if weekly_summary is None:
                return {"error": "No weather summary available"}
            
            # Enhanced forecast combining weather + historical patterns
            enhanced_forecast = []
            
            for _, day in weekly_summary.iterrows():
                date = day['date']
                weather_score = day['weather_quality_score']
                predicted_production = day['solar_production_forecast']
                
                # Generate day-specific recommendations
                day_recommendations = []
                
                # Production-based recommendations
                if predicted_production > 25:
                    day_recommendations.append("📈 Alta producció prevista - Ideal per rentadora i aparells grans")
                elif predicted_production < 10:
                    day_recommendations.append("📉 Baixa producció prevista - Minimitzeu consum no essencial")
                
                # Weather quality recommendations
                if weather_score >= 85:
                    day_recommendations.append("☀️ Condicions excel·lents - Aprofiteu per tots els aparells")
                elif weather_score < 50:
                    day_recommendations.append("☁️ Condicions pobres - Eviteu consums alts")
                
                enhanced_forecast.append({
                    'date': date,
                    'weather_quality': day['quality_rating'],
                    'weather_score': weather_score,
                    'sunrise': day['sunrise'],
                    'sunset': day['sunset'],
                    'predicted_production_kwh': predicted_production,
                    'production_category': day['production_category'],
                    'temperature_max': day['temperature_max'],
                    'temperature_min': day['temperature_min'],
                    'uv_index': day['uv_index_max'],
                    'daylight_hours': day['daylight_duration'] / 3600,
                    'recommendations': day_recommendations
                })
            
            return {
                'enhanced_forecast': enhanced_forecast,
                'summary': {
                    'best_days': [d for d in enhanced_forecast if d['weather_score'] >= 80],
                    'average_production': sum(d['predicted_production_kwh'] for d in enhanced_forecast) / len(enhanced_forecast)
                }
            }
            
        except Exception as e:
            print(f"Error creating enhanced forecast: {e}")
            return {"error": str(e)} 