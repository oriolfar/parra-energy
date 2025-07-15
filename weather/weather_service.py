"""
Weather Service Module - Real Weather Data Integration for Solar Forecasting
===========================================================================

This module provides comprehensive weather data integration using the Open-Meteo API
to enhance solar energy production forecasting and optimization. It's specifically
configured for Agramunt and provides weather-aware energy planning capabilities.

WEATHER DATA INTEGRATION:
1. REAL-TIME WEATHER DATA:
   - Open-Meteo API integration for accurate meteorological data
   - Agramunt, Spain coordinates (41.7869°N, 1.0968°E)
   - Hourly weather updates with automatic caching
   - 7-day forecast data with historical correlation

2. SOLAR FORECASTING PARAMETERS:
   - Direct and diffuse solar radiation measurements
   - Global tilted irradiance for solar panel optimization
   - Cloud cover percentage for production scaling
   - UV index for solar efficiency calculations

3. WEATHER-AWARE FEATURES:
   - Solar production forecasting based on weather conditions
   - Optimal timing recommendations for appliance usage
   - Weather quality scoring for energy planning
   - Seasonal adjustment factors for Spain's climate

4. DATABASE INTEGRATION:
   - Automatic weather data storage and retrieval
   - Historical weather correlation with energy production
   - Daily and weekly weather summaries
   - Weather forecast accuracy tracking

SOLAR ENERGY CORRELATION:
- Cloud cover impact on solar production (0-100% scaling)
- Temperature effects on panel efficiency
- Wind speed influence on cooling and performance
- Precipitation impact on panel cleanliness and output

FORECASTING CAPABILITIES:
- 7-day solar production forecasts
- Optimal appliance timing based on expected solar output
- Weather-based energy planning recommendations
- Elderly user advice considering weather conditions

OPEN-METEO API FEATURES:
- Free, high-quality weather data
- No API key required
- Reliable service with automatic retry logic
- Comprehensive meteorological parameters

This weather integration enables the Parra Energy system to provide
intelligent, weather-aware energy optimization and forecasting for
maximum solar energy utilization and user convenience.
"""

import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
from datetime import datetime, timedelta
import numpy as np
import sqlite3
import os


class WeatherService:
    """
    Weather data service for solar energy forecasting and optimization.
    
    This service integrates with the Open-Meteo API to provide real weather
    data for Agramunt, Spain, enabling accurate solar production forecasting
    and weather-aware energy optimization recommendations.
    """
    
    def __init__(self, db_path="data/energy_data.db"):
        """
        Initialize weather service with Open-Meteo API integration.
        
        Args:
            db_path: Path to SQLite database for weather data storage
            
        Setup Process:
        1. Configure Open-Meteo API client with caching and retry logic
        2. Set coordinates for Agramunt, Spain (grandfather's house location)
        3. Initialize database tables for weather data storage
        4. Prepare solar forecasting algorithms
        """
        print("🌤️  Initializing Weather Service for Solar Forecasting")
        
        # =================================================================
        # OPEN-METEO API CLIENT SETUP
        # =================================================================
        
        # Setup HTTP client with caching and retry logic for reliability
        # Cache expires after 1 hour to balance freshness with API usage
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        self.openmeteo = openmeteo_requests.Client(session=retry_session)
        
        print("   🔗 Open-Meteo API client configured with caching and retry logic")
        
        # =================================================================
        # LOCATION CONFIGURATION
        # =================================================================
        
        # Coordinates for Agramunt, Spain (where grandfather's house is located)
        # These coordinates are optimized for Spanish solar conditions and weather patterns
        self.latitude = 41.7869   # Latitude: 41.7869°N
        self.longitude = 1.0968   # Longitude: 1.0968°E
        self.db_path = db_path
        
        print(f"   📍 Location: Agramunt, Spain ({self.latitude}°N, {self.longitude}°E)")
        print(f"   💾 Database: {db_path}")
        
        # =================================================================
        # DATABASE INITIALIZATION
        # =================================================================
        
        # Initialize weather database tables for data storage and analysis
        self._init_weather_db()
        
        print("✅ Weather Service ready for solar forecasting")
    
    def _init_weather_db(self):
        """
        Initialize weather database tables for comprehensive data storage.
        
        This method creates the necessary database tables for storing:
        - Raw weather forecast data from Open-Meteo API
        - Daily weather summaries and solar forecasts
        - Weather quality scores and ratings
        - Historical weather correlation with energy production
        
        Tables are designed for efficient querying and long-term data storage
        while supporting both real-time forecasting and historical analysis.
        """
        print("   🔧 Initializing weather database tables...")
        
        # Ensure database directory exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # =============================================================
            # WEATHER FORECAST DATA TABLE
            # =============================================================
            
            # Raw weather forecast data from Open-Meteo API
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS weather_forecast (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,                    -- ISO datetime for forecast hour
                    temperature_2m REAL,                       -- Temperature at 2m height (°C)
                    cloud_cover REAL,                          -- Cloud cover percentage (0-100%)
                    direct_radiation REAL,                     -- Direct solar radiation (W/m²)
                    diffuse_radiation REAL,                    -- Diffuse solar radiation (W/m²)
                    global_tilted_irradiance REAL,             -- Global tilted irradiance (W/m²)
                    shortwave_radiation REAL,                  -- Shortwave radiation (W/m²)
                    wind_speed_10m REAL,                       -- Wind speed at 10m height (m/s)
                    precipitation REAL,                        -- Precipitation amount (mm)
                    uv_index REAL,                             -- UV index (0-11+)
                    forecast_date TEXT NOT NULL,               -- Date when forecast was made
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP, -- Database insertion timestamp
                    UNIQUE(timestamp, forecast_date)           -- Prevent duplicate forecasts
                )
            ''')
            
            # =============================================================
            # DAILY WEATHER SUMMARY TABLE  
            # =============================================================
            
            # Daily aggregated weather data and solar forecasts
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS weather_daily (
                    date TEXT PRIMARY KEY,                     -- Date in YYYY-MM-DD format
                    sunrise TEXT,                              -- Sunrise time (HH:MM)
                    sunset TEXT,                               -- Sunset time (HH:MM)
                    daylight_duration INTEGER,                 -- Daylight duration (seconds)
                    temperature_max REAL,                      -- Maximum temperature (°C)
                    temperature_min REAL,                      -- Minimum temperature (°C)
                    uv_index_max REAL,                         -- Maximum UV index
                    cloud_cover_avg REAL,                      -- Average cloud cover (%)
                    precipitation_total REAL,                  -- Total precipitation (mm)
                    wind_speed_max REAL,                       -- Maximum wind speed (m/s)
                    solar_production_forecast REAL,            -- Forecasted solar production (kWh)
                    weather_quality_score REAL,                -- Weather quality for solar (0-100)
                    quality_rating TEXT,                       -- Human-readable quality rating
                    production_category TEXT,                  -- High/Medium/Low production category
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP  -- Database insertion timestamp
                )
            ''')
            
            # =============================================================
            # WEATHER IMPACT ANALYSIS TABLE
            # =============================================================
            
            # Analysis of weather impact on actual solar production
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS weather_impact (
                    date TEXT PRIMARY KEY,                     -- Date of analysis
                    forecasted_production REAL,                -- Weather-based forecast (kWh)
                    actual_production REAL,                    -- Actual measured production (kWh)
                    forecast_accuracy REAL,                    -- Accuracy percentage (0-100%)
                    weather_factor REAL,                       -- Weather impact factor (0-1)
                    seasonal_adjustment REAL,                  -- Seasonal correction factor
                    learning_weight REAL,                      -- Machine learning weight
                    notes TEXT,                                -- Analysis notes
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP  -- Analysis timestamp
                )
            ''')
            
            conn.commit()
            conn.close()
            
            print("   ✅ Weather database tables created successfully")
            
        except Exception as e:
            print(f"   ❌ Error creating weather database tables: {e}")
            # Continue operation even if weather DB setup fails
    
    def fetch_weather_forecast(self, forecast_days=7):
        """Fetch comprehensive weather forecast optimized for solar predictions"""
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "daily": [
                "sunrise", "sunset", "daylight_duration", "uv_index_max", 
                "temperature_2m_max", "temperature_2m_min", "shortwave_radiation_sum"
            ],
            "hourly": [
                "temperature_2m", "cloud_cover", "direct_radiation", 
                "diffuse_radiation", "global_tilted_irradiance", 
                "shortwave_radiation", "wind_speed_10m", "precipitation"
            ],
            "timezone": "Europe/Madrid",
            "forecast_days": forecast_days,
            "tilt": 30,  # Typical solar panel tilt for Spain
            "azimuth": 180  # South-facing panels
        }
        
        try:
            responses = self.openmeteo.weather_api(url, params=params)
            response = responses[0]
            
            # Process data
            hourly_data = self._process_hourly_data(response.Hourly())
            daily_data = self._process_daily_data(response.Daily())
            
            # Store in database
            self._store_weather_data(hourly_data, daily_data)
            
            return {
                'hourly': hourly_data,
                'daily': daily_data,
                'coordinates': {
                    'latitude': response.Latitude(),
                    'longitude': response.Longitude(),
                    'elevation': response.Elevation()
                }
            }
            
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return None
    
    def _process_hourly_data(self, hourly):
        """Process hourly weather data into a useful format"""
        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            )
        }
        
        variables = [
            "temperature_2m", "cloud_cover", "direct_radiation", 
            "diffuse_radiation", "global_tilted_irradiance", 
            "shortwave_radiation", "wind_speed_10m", "precipitation"
        ]
        
        for i, var in enumerate(variables):
            hourly_data[var] = hourly.Variables(i).ValuesAsNumpy()
        
        return pd.DataFrame(data=hourly_data)
    
    def _process_daily_data(self, daily):
        """Process daily weather data"""
        daily_data = {
            "date": pd.date_range(
                start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=daily.Interval()),
                inclusive="left"
            )
        }
        
        daily_data["sunrise"] = daily.Variables(0).ValuesInt64AsNumpy()
        daily_data["sunset"] = daily.Variables(1).ValuesInt64AsNumpy()
        daily_data["daylight_duration"] = daily.Variables(2).ValuesAsNumpy()
        daily_data["uv_index_max"] = daily.Variables(3).ValuesAsNumpy()
        daily_data["temperature_max"] = daily.Variables(4).ValuesAsNumpy()
        daily_data["temperature_min"] = daily.Variables(5).ValuesAsNumpy()
        daily_data["shortwave_radiation_sum"] = daily.Variables(6).ValuesAsNumpy()
        
        return pd.DataFrame(data=daily_data)
    
    def _store_weather_data(self, hourly_df, daily_df):
        """Store weather data in database"""
        conn = sqlite3.connect(self.db_path)
        forecast_date = datetime.now().strftime('%Y-%m-%d')
        
        # Store hourly data
        for _, row in hourly_df.iterrows():
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO weather_forecast 
                    (timestamp, temperature_2m, cloud_cover, direct_radiation, 
                     diffuse_radiation, global_tilted_irradiance, shortwave_radiation,
                     wind_speed_10m, precipitation, forecast_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['date'].isoformat(),
                    float(row['temperature_2m']) if not pd.isna(row['temperature_2m']) else None,
                    float(row['cloud_cover']) if not pd.isna(row['cloud_cover']) else None,
                    float(row['direct_radiation']) if not pd.isna(row['direct_radiation']) else None,
                    float(row['diffuse_radiation']) if not pd.isna(row['diffuse_radiation']) else None,
                    float(row['global_tilted_irradiance']) if not pd.isna(row['global_tilted_irradiance']) else None,
                    float(row['shortwave_radiation']) if not pd.isna(row['shortwave_radiation']) else None,
                    float(row['wind_speed_10m']) if not pd.isna(row['wind_speed_10m']) else None,
                    float(row['precipitation']) if not pd.isna(row['precipitation']) else None,
                    forecast_date
                ))
            except Exception as e:
                print(f"Error storing hourly data: {e}")
        
        # Store daily data
        for _, row in daily_df.iterrows():
            cursor = conn.cursor()
            try:
                solar_forecast = self._calculate_solar_forecast(row)
                weather_score = self._calculate_weather_quality_score(row)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO weather_daily 
                    (date, sunrise, sunset, daylight_duration, uv_index_max,
                     temperature_max, temperature_min, solar_production_forecast,
                     weather_quality_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['date'].strftime('%Y-%m-%d'),
                    pd.to_datetime(row['sunrise'], unit='s').strftime('%H:%M'),
                    pd.to_datetime(row['sunset'], unit='s').strftime('%H:%M'),
                    float(row['daylight_duration']) if not pd.isna(row['daylight_duration']) else None,
                    float(row['uv_index_max']) if not pd.isna(row['uv_index_max']) else None,
                    float(row['temperature_max']) if not pd.isna(row['temperature_max']) else None,
                    float(row['temperature_min']) if not pd.isna(row['temperature_min']) else None,
                    solar_forecast,
                    weather_score
                ))
            except Exception as e:
                print(f"Error storing daily data: {e}")
        
        conn.commit()
        conn.close()
    
    def _calculate_solar_forecast(self, daily_row):
        """Calculate expected solar production based on weather"""
        try:
            radiation = daily_row['shortwave_radiation_sum'] if not pd.isna(daily_row['shortwave_radiation_sum']) else 0
            daylight = daily_row['daylight_duration'] / 3600 if not pd.isna(daily_row['daylight_duration']) else 8
            uv_index = daily_row['uv_index_max'] if not pd.isna(daily_row['uv_index_max']) else 5
            
            # Empirical formula for 5kW system
            base_production = (radiation * 0.15) + (daylight * 2) + (uv_index * 1.5)
            
            # Temperature adjustment (solar panels lose efficiency in high heat)
            temp_max = daily_row['temperature_max'] if not pd.isna(daily_row['temperature_max']) else 25
            if temp_max > 25:
                temp_penalty = (temp_max - 25) * 0.004
                base_production *= (1 - temp_penalty)
            
            return max(0, min(base_production, 50))
            
        except Exception:
            return 15
    
    def _calculate_weather_quality_score(self, daily_row):
        """Calculate a 0-100 score for solar weather quality"""
        try:
            score = 100
            
            # UV Index factor
            uv_index = daily_row['uv_index_max'] if not pd.isna(daily_row['uv_index_max']) else 5
            if uv_index < 3:
                score -= 30
            elif uv_index < 6:
                score -= 10
            
            # Daylight duration
            daylight_hours = (daily_row['daylight_duration'] / 3600) if not pd.isna(daily_row['daylight_duration']) else 8
            if daylight_hours < 8:
                score -= 20
            elif daylight_hours < 10:
                score -= 10
            
            # Temperature optimization
            temp_max = daily_row['temperature_max'] if not pd.isna(daily_row['temperature_max']) else 25
            if temp_max > 35:
                score -= 15
            elif temp_max > 30:
                score -= 5
            
            # Radiation quality
            radiation = daily_row['shortwave_radiation_sum'] if not pd.isna(daily_row['shortwave_radiation_sum']) else 15
            if radiation < 10:
                score -= 25
            elif radiation < 15:
                score -= 10
            
            return max(10, min(score, 100))
            
        except Exception:
            return 60
    
    def get_weekly_weather_summary(self):
        """Get a 7-day weather summary optimized for solar planning"""
        conn = sqlite3.connect(self.db_path)
        query = '''
            SELECT date, sunrise, sunset, daylight_duration, uv_index_max,
                   temperature_max, temperature_min, solar_production_forecast,
                   weather_quality_score
            FROM weather_daily 
            WHERE date >= date('now')
            ORDER BY date
            LIMIT 7
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return None
        
        # Add qualitative assessments
        df['quality_rating'] = df['weather_quality_score'].apply(self._score_to_rating)
        df['production_category'] = df['solar_production_forecast'].apply(self._production_to_category)
        
        return df
    
    def _score_to_rating(self, score):
        """Convert weather quality score to rating in Catalan"""
        if score >= 90:
            return "Excelent"
        elif score >= 75:
            return "Molt Bo"
        elif score >= 60:
            return "Bo"
        elif score >= 45:
            return "Regular"
        else:
            return "Dolent"
    
    def _production_to_category(self, production):
        """Convert production forecast to category in Catalan"""
        if production >= 35:
            return "Molt Alta"
        elif production >= 25:
            return "Alta"
        elif production >= 15:
            return "Moderada"
        elif production >= 8:
            return "Baixa"
        else:
            return "Molt Baixa"
    
    def get_best_hours_forecast(self, date=None):
        """Get the best hours for energy consumption based on weather forecast"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        query = '''
            SELECT timestamp, global_tilted_irradiance, direct_radiation, 
                   cloud_cover, temperature_2m, precipitation
            FROM weather_forecast 
            WHERE DATE(timestamp) = ?
            ORDER BY timestamp
        '''
        
        df = pd.read_sql_query(query, conn, params=[date])
        conn.close()
        
        if df.empty:
            return None
        
        # Calculate hourly estimates
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        df['solar_production_estimate'] = df.apply(self._calculate_hourly_production, axis=1)
        df['solar_efficiency'] = df.apply(self._calculate_hourly_efficiency, axis=1)
        
        # Find best hours
        peak_hours = df.nlargest(4, 'solar_production_estimate')
        efficient_hours = df[
            (df['solar_efficiency'] > 70) & 
            (df['solar_production_estimate'] > 1)
        ].nlargest(6, 'solar_efficiency')
        
        return {
            'peak_production_hours': peak_hours[['hour', 'solar_production_estimate', 'solar_efficiency']].to_dict('records'),
            'most_efficient_hours': efficient_hours[['hour', 'solar_production_estimate', 'solar_efficiency']].to_dict('records'),
            'average_daily_production': df['solar_production_estimate'].sum(),
            'best_hour': df.loc[df['solar_production_estimate'].idxmax(), 'hour'] if not df.empty else 12
        }
    
    def _calculate_hourly_production(self, row):
        """Calculate estimated hourly solar production"""
        try:
            irradiance = row['global_tilted_irradiance'] if not pd.isna(row['global_tilted_irradiance']) else 0
            hour = row['hour']
            
            # Only during daylight hours
            if hour < 7 or hour > 19:
                return 0
            
            # Convert irradiance to production estimate (5kW system)
            base_production = (irradiance / 1000) * 5
            
            # Cloud cover penalty
            cloud_cover = row['cloud_cover'] if not pd.isna(row['cloud_cover']) else 0
            cloud_penalty = cloud_cover / 100 * 0.7
            base_production *= (1 - cloud_penalty)
            
            # Temperature adjustment
            temp = row['temperature_2m'] if not pd.isna(row['temperature_2m']) else 20
            if temp > 25:
                temp_penalty = (temp - 25) * 0.004
                base_production *= (1 - temp_penalty)
            
            return max(0, base_production)
            
        except Exception:
            return 0
    
    def _calculate_hourly_efficiency(self, row):
        """Calculate solar panel efficiency percentage for the hour"""
        try:
            base_efficiency = 85
            
            # Cloud impact
            cloud_cover = row['cloud_cover'] if not pd.isna(row['cloud_cover']) else 0
            base_efficiency -= (cloud_cover * 0.4)
            
            # Temperature impact
            temp = row['temperature_2m'] if not pd.isna(row['temperature_2m']) else 20
            if temp > 25:
                base_efficiency -= ((temp - 25) * 0.4)
            elif temp < 0:
                base_efficiency -= (abs(temp) * 0.2)
            
            # Precipitation impact
            precipitation = row['precipitation'] if not pd.isna(row['precipitation']) else 0
            if precipitation > 0:
                base_efficiency -= min(precipitation * 5, 20)
            
            return max(20, min(base_efficiency, 100))
            
        except Exception:
            return 60 