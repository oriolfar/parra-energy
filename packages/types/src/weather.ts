/**
 * Weather Data Types for Parra Energy System
 * ==========================================
 * 
 * TypeScript interfaces for weather integration and solar forecasting.
 * Based on Open-Meteo API for Agramunt
 */

export interface WeatherData {
  timestamp: string;
  location: string;
  temperature: number;
  humidity: number;
  cloud_cover: number;
  uv_index: number;
  solar_radiation: number;
  wind_speed: number;
  precipitation: number;
  weather_description: string;
}

export interface WeatherForecast {
  date: string;
  location: string;
  temperature_min: number;
  temperature_max: number;
  cloud_cover: number;
  uv_index: number;
  solar_radiation: number;
  precipitation_probability: number;
  wind_speed: number;
  weather_code: number;
  weather_description: string;
  expected_solar_production: number;
  forecast_created_at: string;
}

export interface SolarForecast {
  date: string;
  estimated_production_kwh: number;
  peak_production_hour: number;
  weather_factor: number;
  confidence_level: number;
  hourly_analysis?: {
    production_start: number;
    production_end: number;
    peak_hour: number;
    optimal_windows: Array<{
      start: number;
      end: number;
      description: string;
    }>;
    total_production_hours: number;
    max_irradiance: number;
  };
}

export interface WeatherApiResponse {
  latitude: number;
  longitude: number;
  timezone: string;
  current: {
    time: string;
    temperature_2m: number;
    relative_humidity_2m: number;
    cloud_cover: number;
    uv_index: number;
    global_tilted_irradiance: number;
    wind_speed_10m: number;
    precipitation: number;
    weather_code: number;
  };
  daily: {
    time: string[];
    temperature_2m_max: number[];
    temperature_2m_min: number[];
    uv_index_max: number[];
    cloud_cover_mean: number[];
    precipitation_probability_max: number[];
    wind_speed_10m_max: number[];
    weather_code: number[];
    global_tilted_irradiance_max: number[];
  };
}

export interface WeatherCondition {
  code: number;
  description: string;
  category: 'clear' | 'partly_cloudy' | 'cloudy' | 'rainy' | 'stormy';
  solar_efficiency_factor: number;
} 