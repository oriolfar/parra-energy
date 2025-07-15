"""
Enhanced Mock Fronius API Client - Sophisticated Solar Simulation System
=======================================================================

This module provides an advanced mock client that simulates Fronius solar inverter
behavior using REAL weather data and sophisticated algorithms. It's designed to
provide realistic solar energy patterns for demonstration, development, and
specialized user interfaces.

ADVANCED SIMULATION FEATURES:
1. REAL WEATHER INTEGRATION:
   - Live weather data from Open-Meteo API for Agramunt, Spain
   - Solar production calculations based on actual weather conditions
   - UV index, cloud cover, and temperature correlation
   - Seasonal variations and realistic daily patterns

2. INTELLIGENT CONSUMPTION MODELING:
   - Historical pattern analysis from database
   - Time-of-day consumption profiles
   - Appliance usage simulation (washing machine, dishwasher, etc.)
   - Elderly-specific usage patterns and behaviors

3. ELDERLY USER SPECIALIZATION:
   - Simplified advice generation in Catalan language
   - Context-aware recommendations for appliance timing
   - Weather-based energy planning guidance
   - Optimal timing suggestions for household activities

4. TESTING AND DEMO CAPABILITIES:
   - Manual override controls for solar production (0-100%)
   - Manual consumption setting for specific scenarios
   - Predefined test scenarios (excess solar, high consumption, etc.)
   - Realistic energy flow calculations and grid interaction

SOLAR PRODUCTION SIMULATION:
- Daily solar cycles following sun patterns (7 AM - 7 PM)
- Weather-based production scaling using real meteorological data
- Seasonal variations matching Spain's solar patterns
- Peak capacity: 2.2kW (realistic home installation)

CONSUMPTION SIMULATION:
- Base load: 300W (always-on devices)
- Morning routine: 6-10 AM (1.8x factor)
- Midday cooking: 12-14 PM (2.2x factor)  
- Evening peak: 17-21 PM (2.5x factor)
- Night rest: 21-6 AM (0.6x factor)

ELDERLY USER FEATURES:
- Contextual advice based on current energy situation
- Weather-aware appliance timing recommendations
- Simple language explanations in Catalan
- Focus on practical, actionable guidance

WEATHER DATA SOURCES:
- Open-Meteo API for Agramunt, Spain (41.7869°N, 1.0968°E)
- Real-time weather conditions and 7-day forecasts
- Solar radiation, UV index, and cloud cover data
- Temperature and precipitation information

This enhanced mock ensures that users receive realistic solar energy data
and valuable insights regardless of whether they're connected to a real
Fronius inverter, making the system useful for demonstrations, development,
and training purposes while maintaining data quality and user experience.
"""

import random
import math
import sqlite3
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, Optional

# Add parent directories to path for module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class EnhancedMockFroniusClient:
    """
    Advanced Fronius inverter simulator with real weather integration.
    
    This class provides sophisticated simulation of solar energy production
    and household consumption patterns, using real weather data and intelligent
    algorithms to generate realistic energy scenarios for testing, development,
    and elderly user assistance.
    """
    
    def __init__(self, host: str = "mock", port: int = 80, db_path: str = "data/energy_data.db"):
        """
        Initialize the enhanced mock Fronius client with weather integration.
        
        Args:
            host: Placeholder for compatibility (ignored in mock mode)
            port: Placeholder for compatibility (ignored in mock mode)
            db_path: Path to SQLite database for historical data and weather storage
            
        Initialization Process:
        1. Configure solar system parameters (2.2kW capacity)
        2. Set up manual testing controls
        3. Initialize energy counters and state tracking
        4. Connect to real weather service for Agramunt, Spain
        5. Load historical consumption patterns for realistic simulation
        """
        # Connection parameters (for compatibility with real client interface)
        self.host = host
        self.port = port
        self.db_path = db_path
        
        print("🔧 Initializing Enhanced Mock Fronius Client")
        
        # =================================================================
        # SOLAR SYSTEM CONFIGURATION
        # =================================================================
        
        # Solar panel system specifications (matching real 2.2kW installation)
        self.max_solar_power = 2200  # Peak capacity in watts (2.2kW)
        self.base_consumption = 300  # Base household load in watts
        
        print(f"   📋 Solar system: {self.max_solar_power}W peak capacity")
        print(f"   🏠 Base consumption: {self.base_consumption}W")
        
        # =================================================================
        # MANUAL TESTING CONTROLS
        # =================================================================
        
        # Manual override controls for testing specific scenarios
        # None = automatic mode, specific values = manual override
        self._manual_solar_percentage = None    # Solar production override (0-100%)
        self._manual_consumption_watts = None   # Consumption override (watts)
        
        print("   🔧 Manual testing controls initialized")
        
        # =================================================================
        # ENERGY TRACKING AND COUNTERS
        # =================================================================
        
        # Cumulative energy tracking for realistic dashboard display
        self._daily_energy = 0          # Today's energy production (kWh)
        self._total_energy = 145000     # Simulated total since installation (kWh)
        self._yearly_energy = 12500     # Simulated yearly production so far (kWh)
        self._last_update = datetime.now()
        self._last_day = datetime.now().day
        
        print("   📊 Energy counters initialized with realistic values")
        
        # =================================================================
        # WEATHER SERVICE INTEGRATION
        # =================================================================
        
        # Initialize connection to real weather service for Agramunt, Spain
        self._init_weather_service()
        
        # =================================================================
        # HISTORICAL PATTERN LOADING
        # =================================================================
        
        # Load historical consumption patterns for realistic simulation
        self._load_historical_patterns()
        
        print("✅ Enhanced Mock Fronius Client ready with real weather integration")
        
    def _init_weather_service(self):
        """
        Initialize connection to real weather service for Agramunt, Spain.
        
        This method attempts to connect to the WeatherService module which
        provides real weather data from the Open-Meteo API. If the weather
        service is unavailable, the mock will fall back to simulated weather
        patterns while maintaining realistic behavior.
        
        Weather Integration Benefits:
        - Solar production based on actual weather conditions
        - Realistic cloud cover and UV index correlation
        - Seasonal variations matching real Spain climate
        - Enhanced elderly user advice based on weather forecasts
        """
        try:
            from weather.weather_service import WeatherService
            self.weather_service = WeatherService(self.db_path)
            self._has_weather_service = True
            print("   🌤️  Connected to real weather service (Open-Meteo API)")
            print("   📍 Location: Agramunt, Spain (41.7869°N, 1.0968°E)")
        except Exception as e:
            print(f"   ⚠️  Could not load weather service: {e}")
            print("   🔄 Using fallback weather simulation patterns")
            self.weather_service = None
            self._has_weather_service = False
    
    def _load_historical_patterns(self):
        """
        Load historical consumption patterns for realistic household simulation.
        
        This method defines typical Spanish household energy usage patterns
        and attempts to load actual historical data from the database to
        improve simulation accuracy.
        
        Consumption Patterns:
        - Morning routine (6-10h): Coffee, breakfast, getting ready
        - Midday cooking (12-14h): Lunch preparation and cooking
        - Evening routine (17-21h): Dinner, TV, family activities
        - Night rest (21-6h): Sleep mode with minimal consumption
        
        The patterns are calibrated for elderly users with typical Spanish
        meal times and daily routines.
        """
        print("   🏠 Loading household consumption patterns...")
        
        # Define typical Spanish household consumption patterns
        # Times are in 24-hour format, factors multiply base consumption
        self.elderly_patterns = {
            'morning_routine': {
                'time': (6, 10),           # 6:00 AM - 10:00 AM
                'factor': 1.8,             # 1.8x base consumption
                'activities': ['coffee', 'breakfast', 'morning_tv']
            },
            'midday_cooking': {
                'time': (12, 14),          # 12:00 PM - 2:00 PM  
                'factor': 2.2,             # 2.2x base consumption
                'activities': ['lunch_prep', 'cooking', 'kitchen_appliances']
            },
            'evening_routine': {
                'time': (17, 21),          # 5:00 PM - 9:00 PM
                'factor': 2.5,             # 2.5x base consumption
                'activities': ['dinner_prep', 'tv', 'lighting', 'heating_cooling']
            },
            'night_rest': {
                'time': (21, 6),           # 9:00 PM - 6:00 AM
                'factor': 0.6,             # 0.6x base consumption
                'activities': ['sleep', 'security_systems', 'minimal_lighting']
            }
        }
        
        # Attempt to load actual historical data from database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            print("   📈 Analyzing historical data for pattern improvement...")
            
            # Get average consumption patterns by hour from last 30 days
            cursor.execute('''
                SELECT 
                    strftime('%H', timestamp) as hour,
                    AVG(consumption) as avg_consumption,
                    COUNT(*) as count
                FROM energy 
                WHERE timestamp > datetime('now', '-30 days')
                  AND consumption > 0
                GROUP BY strftime('%H', timestamp)
                ORDER BY hour
            ''')
            
            historical_data = cursor.fetchall()
            if historical_data and len(historical_data) > 12:  # Need reasonable amount of data
                self.historical_hourly_consumption = {int(row[0]): row[1] for row in historical_data}
                print(f"✅ Loaded {len(historical_data)} hours of historical consumption patterns")
            else:
                self.historical_hourly_consumption = {}
                print("ℹ️  Using elderly-specific consumption patterns (no historical data)")
                
            conn.close()
        except Exception as e:
            print(f"ℹ️  No historical data available: {e}")
            self.historical_hourly_consumption = {}
    
    def get_power_data(self) -> Dict:
        """Generate enhanced mock power data using real weather and historical patterns.
        
        Returns:
            Dict containing realistic solar and consumption data with elderly-focused optimizations
        """
        current_time = datetime.now()
        
        # Reset daily counter at midnight
        if current_time.day != self._last_day:
            self._daily_energy = 0
            self._last_day = current_time.day
            # Refresh weather data for new day
            self._refresh_weather_data()
        
        # Calculate solar production using REAL weather data
        solar_power = self._calculate_weather_enhanced_solar_production(current_time)
        
        # Calculate household consumption using historical patterns
        consumption_power = self._calculate_elderly_consumption_patterns(current_time)
        
        # Calculate grid power (positive = importing, negative = exporting)
        grid_power = consumption_power - solar_power
        
        # Update energy counters
        time_delta = (current_time - self._last_update).total_seconds() / 3600  # hours
        energy_increment = solar_power * time_delta
        self._daily_energy += energy_increment
        self._total_energy += energy_increment
        self._yearly_energy += energy_increment
        self._last_update = current_time
        
        # Calculate efficiency metrics for elderly advice
        if consumption_power > 0:
            self_consumed = min(solar_power, consumption_power)
            autonomy = (self_consumed / consumption_power) * 100
        else:
            autonomy = 100 if solar_power > 0 else 0
            
        if solar_power > 0:
            self_consumption_rate = (min(solar_power, consumption_power) / solar_power) * 100
        else:
            self_consumption_rate = 0
        
        # Generate elderly-friendly advice context
        advice_context = self._generate_elderly_advice_context(solar_power, consumption_power, grid_power, current_time)
        
        return {
            'P_PV': round(solar_power, 1),  # Solar production in watts
            'P_Load': round(consumption_power, 1),  # House consumption in watts  
            'P_Grid': round(grid_power, 1),  # Grid power flow in watts
            'P_Akku': 0,  # No battery in this simulation
            'E_Day': round(self._daily_energy, 1),  # Energy produced today in Wh
            'E_Total': round(self._total_energy, 1),  # Total energy produced in Wh
            'E_Year': round(self._yearly_energy, 1),  # Energy produced this year in Wh
            'rel_Autonomy': round(autonomy, 1),  # Percentage of energy autonomy
            'rel_SelfConsumption': round(self_consumption_rate, 1),  # Percentage of self-consumption
            'elderly_advice_context': advice_context  # NEW: Elderly-specific advice context
        }
    
    def _refresh_weather_data(self):
        """Refresh weather data for the current day"""
        if self._has_weather_service:
            try:
                # Fetch fresh weather data
                weather_data = self.weather_service.fetch_weather_forecast(1)
                if weather_data:
                    print("🌤️  Updated real weather data for enhanced mock system")
            except Exception as e:
                print(f"⚠️  Could not refresh weather data: {e}")
    
    def _calculate_weather_enhanced_solar_production(self, current_time: datetime) -> float:
        """Calculate solar production using REAL weather data from Agramunt"""
        hour = current_time.hour
        
        # Check for manual solar percentage override
        if self._manual_solar_percentage is not None:
            return (self._manual_solar_percentage / 100.0) * self.max_solar_power
        minute = current_time.minute
        
        # No production during night
        if hour < 7 or hour >= 19:
            return 0
        
        # Base sun angle calculation
        time_factor = hour + minute / 60.0
        sun_angle = math.sin(math.pi * (time_factor - 7) / 12)
        
        if sun_angle <= 0:
            return 0
        
        # Base production from sun angle
        base_production = self.max_solar_power * sun_angle
        
        # Apply REAL weather effects if available
        weather_factor = self._get_real_weather_factor(current_time)
        
        # Apply seasonal effects
        month = current_time.month
        seasonal_factor = self._get_seasonal_factor(month)
        
        # Small random variation to make it feel authentic
        variation = random.uniform(0.98, 1.02)
        
        production = base_production * weather_factor * seasonal_factor * variation
        
        return max(0, production)
    
    def _get_real_weather_factor(self, current_time: datetime) -> float:
        """Get weather factor using REAL weather data from database"""
        if not self._has_weather_service:
            # Fallback to seasonal appropriate weather
            month = current_time.month
            if month in [6, 7, 8]:  # Summer
                return random.uniform(0.8, 1.0)
            elif month in [12, 1, 2]:  # Winter  
                return random.uniform(0.5, 0.8)
            else:  # Spring/Fall
                return random.uniform(0.6, 0.9)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get current weather conditions
            current_hour = current_time.strftime('%Y-%m-%d %H:00:00')
            cursor.execute('''
                SELECT cloud_cover, direct_radiation, global_tilted_irradiance, precipitation
                FROM weather_forecast 
                WHERE timestamp = ?
                ORDER BY created_at DESC
                LIMIT 1
            ''', (current_hour,))
            
            weather_data = cursor.fetchone()
            conn.close()
            
            if weather_data:
                cloud_cover, direct_radiation, global_tilted_irradiance, precipitation = weather_data
                
                # Calculate weather factor based on real conditions
                weather_factor = 1.0
                
                # Cloud cover impact (0-100%)
                if cloud_cover is not None:
                    weather_factor *= (1 - (cloud_cover / 100) * 0.7)
                
                # Precipitation impact
                if precipitation is not None and precipitation > 0:
                    weather_factor *= (1 - min(precipitation * 0.1, 0.5))
                
                # Direct radiation boost
                if direct_radiation is not None and direct_radiation > 0:
                    # Normalize direct radiation (typical range 0-1000 W/m²)
                    radiation_factor = min(direct_radiation / 800, 1.2)
                    weather_factor *= radiation_factor
                
                return max(0.1, min(weather_factor, 1.0))
            
        except Exception as e:
            print(f"⚠️  Could not get real weather factor: {e}")
        
        # Fallback to seasonal appropriate weather
        month = current_time.month
        if month in [6, 7, 8]:  # Summer
            return random.uniform(0.7, 0.95)
        elif month in [12, 1, 2]:  # Winter  
            return random.uniform(0.4, 0.7)
        else:  # Spring/Fall
            return random.uniform(0.5, 0.85)
    
    def _calculate_elderly_consumption_patterns(self, current_time: datetime) -> float:
        """Calculate consumption based on elderly usage patterns and historical data"""
        hour = current_time.hour
        
        # Check for manual consumption override
        if self._manual_consumption_watts is not None:
            return self._manual_consumption_watts
        
        # Use historical data if available
        if hour in self.historical_hourly_consumption:
            historical_consumption = self.historical_hourly_consumption[hour]
            # Add some variation to make it feel real
            variation = random.uniform(0.85, 1.15)
            base_consumption = historical_consumption * variation
        else:
            # Use elderly-specific patterns
            base_consumption = self._get_elderly_consumption_pattern(hour)
        
        # Add appliance usage specific to elderly patterns
        appliance_usage = self._simulate_elderly_appliance_usage(hour)
        
        total_consumption = base_consumption + appliance_usage
        
        return max(100, total_consumption)  # Minimum 100W for elderly household
    
    def _get_elderly_consumption_pattern(self, hour: int) -> float:
        """Get consumption pattern specific to elderly users"""
        if 6 <= hour < 10:  # Morning routine - coffee, breakfast, morning news
            return self.base_consumption * 1.8
        elif 10 <= hour < 12:  # Mid-morning - light activities
            return self.base_consumption * 1.1
        elif 12 <= hour < 14:  # Lunch time - cooking, higher usage
            return self.base_consumption * 2.2
        elif 14 <= hour < 17:  # Afternoon - siesta, light activities
            return self.base_consumption * 0.9
        elif 17 <= hour < 21:  # Evening - dinner, TV, social activities
            return self.base_consumption * 2.5
        elif 21 <= hour < 23:  # Late evening - TV, reading
            return self.base_consumption * 1.5
        else:  # Night - minimal usage
            return self.base_consumption * 0.6
    
    def _simulate_elderly_appliance_usage(self, hour: int) -> float:
        """Simulate appliance usage patterns specific to elderly users"""
        appliance_boost = 0
        
        # Elderly-specific appliance timing
        if 8 <= hour < 10:  # Morning dishwasher (after breakfast)
            if random.random() < 0.3:  # 30% chance
                appliance_boost += random.uniform(1800, 2200)  # Dishwasher
        
        elif 10 <= hour < 12:  # Late morning washing machine
            if random.random() < 0.2:  # 20% chance
                appliance_boost += random.uniform(1500, 2000)  # Washing machine
        
        elif 12 <= hour < 14:  # Lunch cooking
            if random.random() < 0.4:  # 40% chance
                appliance_boost += random.uniform(2000, 3000)  # Electric stove/oven
        
        elif 17 <= hour < 19:  # Evening cooking
            if random.random() < 0.5:  # 50% chance
                appliance_boost += random.uniform(2000, 3000)  # Electric stove/oven
        
        elif 19 <= hour < 21:  # Evening dishwasher
            if random.random() < 0.25:  # 25% chance
                appliance_boost += random.uniform(1800, 2200)  # Dishwasher
        
        return appliance_boost
    
    def _generate_elderly_advice_context(self, solar_power: float, consumption_power: float, grid_power: float, current_time: datetime) -> Dict:
        """Generate context for elderly-friendly advice"""
        hour = current_time.hour
        
        # Determine current energy situation
        if grid_power < -500:  # Selling significant energy
            energy_situation = "excellent_surplus"
            advice_priority = "high_energy_tasks"
        elif grid_power < -100:  # Selling some energy
            energy_situation = "good_surplus"
            advice_priority = "moderate_energy_tasks"
        elif grid_power < 200:  # Balanced or slight import
            energy_situation = "balanced"
            advice_priority = "essential_tasks_only"
        else:  # Importing significant energy
            energy_situation = "high_import"
            advice_priority = "delay_tasks"
        
        # Generate time-specific advice
        current_advice = self._get_time_specific_elderly_advice(hour, energy_situation)
        
        # Get weather-based recommendations
        weather_advice = self._get_weather_based_advice()
        
        return {
            'energy_situation': energy_situation,
            'advice_priority': advice_priority,
            'current_advice': current_advice,
            'weather_advice': weather_advice,
            'optimal_appliance_timing': self._get_optimal_appliance_timing(),
            'hour': hour,
            'solar_percentage': round((solar_power / self.max_solar_power) * 100, 1)
        }
    
    def _get_time_specific_elderly_advice(self, hour: int, energy_situation: str) -> str:
        """Get advice specific to elderly users based on time and energy situation"""
        if energy_situation == "excellent_surplus":
            if 8 <= hour < 12:
                return "Ara és el moment perfecte per posar la rentadora i el rentaplats!"
            elif 12 <= hour < 15:
                return "Ideal per cuinar amb el forn elèctric i fer servir tots els electrodomèstics!"
            elif 15 <= hour < 18:
                return "Bon moment per planxar, fer servir l'aspiradora o posar la secadora!"
            else:
                return "Tens molta energia solar! Aprofita per fer servir el que necessitis."
        
        elif energy_situation == "good_surplus":
            if 8 <= hour < 12:
                return "Bon moment per posar la rentadora o el rentaplats (un de cada vegada)."
            elif 12 <= hour < 15:
                return "Pots cuinar tranquil·lament, tens energia solar suficient."
            else:
                return "Pots fer servir electrodomèstics amb moderació."
        
        elif energy_situation == "balanced":
            return "Energia equilibrada. Pots fer servir el que necessitis però sense excessos."
        
        else:  # high_import
            if 7 <= hour < 10:
                return "Ara gastes de la xarxa. Millor esperar per posar electrodomèstics."
            elif 17 <= hour < 20:
                return "Poca energia solar. Millor cuinar amb gas si pots."
            else:
                return "Millor esperar a demà quan faci més sol per fer servir electrodomèstics."
    
    def _get_weather_based_advice(self) -> str:
        """Get weather-based advice for elderly users using real weather data"""
        if not self._has_weather_service:
            return "Consulta el temps per planificar l'ús d'electrodomèstics."
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get tomorrow's weather forecast
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT weather_quality_score, solar_production_forecast
                FROM weather_daily 
                WHERE date = ?
                ORDER BY created_at DESC
                LIMIT 1
            ''', (tomorrow,))
            
            weather_data = cursor.fetchone()
            conn.close()
            
            if weather_data:
                quality_score, production_forecast = weather_data
                
                if quality_score >= 80:
                    return "Demà farà molt sol! Ideal per deixar la bugada per demà."
                elif quality_score >= 60:
                    return "Demà farà sol. Pots planificar la rentadora per demà al matí."
                elif quality_score < 40:
                    return "Demà estarà núvol. Millor fer la bugada avui si pots."
                else:
                    return "Demà farà un temps regular per l'energia solar."
            
        except Exception as e:
            print(f"⚠️  Could not get weather advice: {e}")
        
        return "Consulta el temps per planificar l'ús d'electrodomèstics."
    
    def _get_optimal_appliance_timing(self) -> Dict:
        """Get optimal timing for elderly appliances based on weather and patterns"""
        current_hour = datetime.now().hour
        
        # Get solar production forecast for rest of day
        optimal_times = {
            'rentadora': self._get_optimal_time_for_appliance('washing_machine', 1.5),
            'rentaplats': self._get_optimal_time_for_appliance('dishwasher', 1.8),
            'forn': self._get_optimal_time_for_appliance('oven', 2.5),
            'planxa': self._get_optimal_time_for_appliance('iron', 1.2)
        }
        
        return optimal_times
    
    def _get_optimal_time_for_appliance(self, appliance_type: str, power_kw: float) -> str:
        """Get optimal time for specific appliance using real weather data"""
        current_hour = datetime.now().hour
        
        # Try to get real weather forecast for optimization
        if self._has_weather_service:
            try:
                best_hours = self.weather_service.get_best_hours_forecast()
                if best_hours and best_hours['peak_production_hours']:
                    peak_hour = best_hours['peak_production_hours'][0]['hour']
                    if current_hour < peak_hour:
                        return f"{peak_hour}:00-{peak_hour+2}:00"
                    elif current_hour <= peak_hour + 2:
                        return "Ara mateix!"
                    else:
                        return "Demà al migdia"
            except Exception:
                pass
        
        # Fallback to simple optimization
        if current_hour < 12:
            return "12:00-15:00"  # Peak solar hours
        elif current_hour < 16:
            return "Ara mateix!"  # Currently in peak hours
        else:
            return "Demà al migdia"  # Tomorrow's peak hours
    
    def _get_seasonal_factor(self, month: int) -> float:
        """Get seasonal factor for Spain"""
        seasonal_factors = {
            1: 0.6, 2: 0.7, 3: 0.8, 4: 0.9, 5: 0.95, 6: 1.0,
            7: 1.0, 8: 0.98, 9: 0.9, 10: 0.8, 11: 0.65, 12: 0.55
        }
        return seasonal_factors.get(month, 0.8)
    
    def is_available(self) -> bool:
        """Check if the enhanced mock client is available (always True)"""
        return True
    
    def get_elderly_recommendations(self) -> Dict:
        """Get specific recommendations for elderly users"""
        current_time = datetime.now()
        power_data = self.get_power_data()
        
        return {
            'immediate_actions': self._get_immediate_actions(power_data),
            'planning_advice': self._get_planning_advice(),
            'energy_saving_tips': self._get_energy_saving_tips(),
            'weather_planning': self._get_weather_planning_advice()
        }
    
    def _get_immediate_actions(self, power_data: Dict) -> list:
        """Get immediate actions elderly users can take"""
        actions = []
        
        if power_data['P_Grid'] < -500:  # Strong surplus
            actions.append("🟢 Ara pots posar la rentadora i el rentaplats alhora!")
            actions.append("🟢 Bon moment per fer servir el forn elèctric!")
        elif power_data['P_Grid'] < -100:  # Mild surplus
            actions.append("🟡 Pots posar la rentadora o el rentaplats (un de cada vegada).")
        elif power_data['P_Grid'] > 200:  # Importing
            actions.append("🔴 Millor esperar per posar electrodomèstics.")
        
        return actions
    
    def _get_planning_advice(self) -> list:
        """Get planning advice for elderly users"""
        return [
            "Planifica la bugada per quan més sol faci (12:00-15:00)",
            "Cuina amb el forn elèctric quan hi hagi excedent solar",
            "Aprofita els dies de sol per fer servir la secadora"
        ]
    
    def _get_energy_saving_tips(self) -> list:
        """Get energy saving tips for elderly users"""
        return [
            "Aprofita la llum natural durant el dia",
            "Usa la rentadora amb aigua freda quan sigui possible",
            "Cuina amb cassoles petites per gastar menys energia"
        ]
    
    def _get_weather_planning_advice(self) -> list:
        """Get weather-based planning advice using real weather data"""
        return [
            "Consulta el temps per planificar l'ús d'electrodomèstics",
            "Els dies núvols, millor fer servir gas per cuinar",
            "Aprofita els dies de sol per fer tota la bugada"
        ]

    def set_manual_solar_percentage(self, percentage: float):
        """Set manual solar production percentage for testing specific cases.
        
        Args:
            percentage: Solar production percentage (0-100), or None to use automatic mode
        """
        if percentage is None:
            self._manual_solar_percentage = None
            print("🔧 Manual solar control disabled - using automatic weather-based production")
        else:
            percentage = max(0, min(100, percentage))  # Clamp to 0-100
            self._manual_solar_percentage = percentage
            print(f"🔧 Manual solar control enabled - set to {percentage}% of maximum capacity")
    
    def set_manual_consumption_watts(self, watts: float):
        """Set manual consumption for testing specific cases.
        
        Args:
            watts: Consumption in watts, or None to use automatic mode
        """
        if watts is None:
            self._manual_consumption_watts = None
            print("🔧 Manual consumption control disabled - using automatic patterns")
        else:
            watts = max(50, watts)  # Minimum 50W
            self._manual_consumption_watts = watts
            print(f"🔧 Manual consumption control enabled - set to {watts}W")
    
    def get_manual_controls(self) -> Dict:
        """Get current manual control settings.
        
        Returns:
            Dict containing current manual control settings
        """
        return {
            'solar_percentage': self._manual_solar_percentage,
            'consumption_watts': self._manual_consumption_watts,
            'is_manual_solar': self._manual_solar_percentage is not None,
            'is_manual_consumption': self._manual_consumption_watts is not None
        }
    
    def reset_manual_controls(self):
        """Reset all manual controls to automatic mode."""
        self._manual_solar_percentage = None
        self._manual_consumption_watts = None
        print("🔧 All manual controls reset to automatic mode")
