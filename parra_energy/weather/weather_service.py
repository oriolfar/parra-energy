import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
from datetime import datetime, timedelta
import numpy as np
import sqlite3
import os

class WeatherService:
    def __init__(self, db_path="parra_energy/data/energy_data.db"):
        """Initialize weather service with coordinates for Agramunt, Spain"""
        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        self.openmeteo = openmeteo_requests.Client(session=retry_session)
        
        # Coordinates for Agramunt, Spain (approximately where the house of my grandfather is)
        self.latitude = 41.7869
        self.longitude = 1.0968
        self.db_path = db_path
        
        # Initialize weather database
        self._init_weather_db()
    
    def _init_weather_db(self):
        """Initialize weather data storage"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create weather forecast table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_forecast (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                temperature_2m REAL,
                cloud_cover REAL,
                direct_radiation REAL,
                diffuse_radiation REAL,
                global_tilted_irradiance REAL,
                shortwave_radiation REAL,
                wind_speed_10m REAL,
                precipitation REAL,
                forecast_date TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(timestamp, forecast_date)
            )
        ''')
        
        # Create daily weather summary table  
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_daily (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE NOT NULL,
                sunrise TEXT,
                sunset TEXT,
                daylight_duration REAL,
                uv_index_max REAL,
                temperature_max REAL,
                temperature_min REAL,
                solar_production_forecast REAL,
                weather_quality_score REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
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