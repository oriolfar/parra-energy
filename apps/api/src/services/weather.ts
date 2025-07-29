/**
 * Weather Service - Real Weather Data Integration
 * ==============================================
 * 
 * Integration with Open-Meteo API for Agramunt, Spain.
 * Provides weather data for solar forecasting and optimization.
 * Based on the Python weather service implementation.
 */

import axios from 'axios';
import type { WeatherData, WeatherForecast, WeatherApiResponse, SolarForecast } from '@repo/types';
import { DatabaseManager } from '@repo/database';

export class WeatherService {
  private apiBaseUrl: string;
  private location: { latitude: number; longitude: number; name: string };
  private db: DatabaseManager;
  private cacheKey: string;
  private lastFetchTime: number = 0;
  private cacheDuration: number = 30 * 60 * 1000; // 30 minutes

  constructor(dbPath?: string) {
    this.apiBaseUrl = 'https://api.open-meteo.com/v1/forecast';
    this.location = {
      latitude: 41.7869,
      longitude: 1.0968,
      name: 'Agramunt, Spain'
    };
    this.db = new DatabaseManager(dbPath);
    this.cacheKey = `weather_${this.location.latitude}_${this.location.longitude}`;
  }

  /**
   * Get current weather data
   */
  async getCurrentWeather(): Promise<WeatherData> {
    try {
      const response = await axios.get<WeatherApiResponse>(this.apiBaseUrl, {
        params: {
          latitude: this.location.latitude,
          longitude: this.location.longitude,
          current: [
            'temperature_2m',
            'relative_humidity_2m',
            'cloud_cover',
            'uv_index',
            'global_tilted_irradiance',
            'wind_speed_10m',
            'precipitation',
            'weather_code'
          ].join(','),
          timezone: 'Europe/Madrid',
        },
        timeout: 10000
      });

      const current = response.data.current;
      const weatherData: WeatherData = {
        timestamp: new Date().toISOString(),
        location: this.location.name,
        temperature: current.temperature_2m,
        humidity: current.relative_humidity_2m,
        cloud_cover: current.cloud_cover,
        uv_index: current.uv_index,
        solar_radiation: current.global_tilted_irradiance,
        wind_speed: current.wind_speed_10m,
        precipitation: current.precipitation,
        weather_description: this.getWeatherDescription(current.weather_code),
      };

      // Store in database
      this.db.insertCurrentWeather(weatherData);

      return weatherData;
    } catch (error) {
      console.error('Failed to fetch current weather:', error);
      
      // Try to get from database as fallback
      const fallbackWeather = await this.getLatestWeatherFromDb();
      if (fallbackWeather) {
        return fallbackWeather;
      }
      
      throw new Error(`Weather service unavailable: ${error}`);
    }
  }

  /**
   * Get weather forecast for the next 7 days
   */
  async getWeatherForecast(days: number = 7): Promise<WeatherForecast[]> {
    try {
      const response = await axios.get<WeatherApiResponse>(this.apiBaseUrl, {
        params: {
          latitude: this.location.latitude,
          longitude: this.location.longitude,
          daily: [
            'temperature_2m_max',
            'temperature_2m_min',
            'uv_index_max',
            'cloud_cover_mean',
            'precipitation_probability_max',
            'wind_speed_10m_max',
            'weather_code',
            'global_tilted_irradiance_max'
          ].join(','),
          timezone: 'Europe/Madrid',
          forecast_days: days
        },
        timeout: 10000
      });

      const daily = response.data.daily;
      const forecasts: WeatherForecast[] = [];

      for (let i = 0; i < daily.time.length && i < days; i++) {
        const forecast: WeatherForecast = {
          date: daily.time[i],
          location: this.location.name,
          temperature_min: daily.temperature_2m_min[i],
          temperature_max: daily.temperature_2m_max[i],
          cloud_cover: daily.cloud_cover_mean[i],
          uv_index: daily.uv_index_max[i],
          solar_radiation: daily.global_tilted_irradiance_max[i],
          precipitation_probability: daily.precipitation_probability_max[i],
          wind_speed: daily.wind_speed_10m_max[i],
          weather_code: daily.weather_code[i],
          weather_description: this.getWeatherDescription(daily.weather_code[i]),
          expected_solar_production: this.calculateExpectedSolarProduction(
            daily.global_tilted_irradiance_max[i],
            daily.cloud_cover_mean[i],
            daily.uv_index_max[i]
          ),
          forecast_created_at: new Date().toISOString(),
        };

        forecasts.push(forecast);
        
        // Store in database
        this.db.insertWeatherForecast(forecast);
      }

      return forecasts;
    } catch (error) {
      console.error('Failed to fetch weather forecast:', error);
      
      // Try to get from database as fallback
      const fallbackForecasts = this.db.getWeatherForecast(this.location.name, days);
      if (fallbackForecasts.length > 0) {
        return fallbackForecasts;
      }
      
      throw new Error(`Weather forecast unavailable: ${error}`);
    }
  }

  /**
   * Get solar production forecast based on weather
   */
  async getSolarForecast(solarCapacity: number = 2200): Promise<SolarForecast[]> {
    const weatherForecasts = await this.getWeatherForecast(7);
    
    return weatherForecasts.map(forecast => {
      const confidence = this.calculateForecastConfidence(forecast);
      
      // Calculate peak production hour based on solar radiation and weather conditions
      const peakHour = this.calculatePeakProductionHour(forecast);
      
      return {
        date: forecast.date,
        estimated_production_kwh: forecast.expected_solar_production * solarCapacity / 1000,
        peak_production_hour: peakHour,
        weather_factor: forecast.expected_solar_production,
        confidence_level: confidence,
      };
    });
  }

  /**
   * Calculate expected solar production factor (0-1) based on weather
   */
  private calculateExpectedSolarProduction(
    solarRadiation: number,
    cloudCover: number,
    uvIndex: number
  ): number {
    // Base production factor from solar radiation
    const radiationFactor = Math.min(solarRadiation / 800, 1); // Normalize to typical max
    
    // Cloud cover reduction
    const cloudFactor = 1 - (cloudCover / 100) * 0.7;
    
    // UV index factor
    const uvFactor = Math.min(uvIndex / 8, 1);
    
    // Combined factor
    return Math.max(0, radiationFactor * cloudFactor * uvFactor);
  }

  /**
   * Calculate forecast confidence based on weather conditions
   */
  private calculateForecastConfidence(forecast: WeatherForecast): number {
    // Higher confidence for stable weather conditions
    let confidence = 0.8; // Base confidence
    
    // Reduce confidence for high cloud variability
    if (forecast.cloud_cover > 70) {
      confidence -= 0.2;
    }
    
    // Reduce confidence for precipitation
    if (forecast.precipitation_probability > 50) {
      confidence -= 0.15;
    }
    
    // Increase confidence for clear weather
    if (forecast.cloud_cover < 20 && forecast.precipitation_probability < 20) {
      confidence = Math.min(0.95, confidence + 0.1);
    }
    
    return Math.max(0.3, confidence);
  }

  /**
   * Get weather description from weather code
   */
  private getWeatherDescription(weatherCode: number): string {
    const weatherCodes: Record<number, string> = {
      0: 'Clear sky',
      1: 'Mainly clear',
      2: 'Partly cloudy',
      3: 'Overcast',
      45: 'Fog',
      48: 'Depositing rime fog',
      51: 'Light drizzle',
      53: 'Moderate drizzle',
      55: 'Dense drizzle',
      56: 'Light freezing drizzle',
      57: 'Dense freezing drizzle',
      61: 'Slight rain',
      63: 'Moderate rain',
      65: 'Heavy rain',
      66: 'Light freezing rain',
      67: 'Heavy freezing rain',
      71: 'Slight snow fall',
      73: 'Moderate snow fall',
      75: 'Heavy snow fall',
      77: 'Snow grains',
      80: 'Slight rain showers',
      81: 'Moderate rain showers',
      82: 'Violent rain showers',
      85: 'Slight snow showers',
      86: 'Heavy snow showers',
      95: 'Thunderstorm',
      96: 'Thunderstorm with slight hail',
      99: 'Thunderstorm with heavy hail',
    };
    
    return weatherCodes[weatherCode] || 'Unknown';
  }

  /**
   * Get latest weather from database (fallback)
   */
  private async getLatestWeatherFromDb(): Promise<WeatherData | null> {
    // This would need to be implemented in the database manager
    // For now, return null to indicate no fallback available
    return null;
  }

  /**
   * Check if cached weather data is still valid
   */
  private isCacheValid(): boolean {
    return Date.now() - this.lastFetchTime < this.cacheDuration;
  }

  /**
   * Get weather quality score for energy planning (0-100)
   */
  async getWeatherQualityScore(): Promise<number> {
    try {
      const currentWeather = await this.getCurrentWeather();
      
      // Calculate quality score based on solar production potential
      let score = 100;
      
      // Reduce score based on cloud cover
      score -= currentWeather.cloud_cover * 0.7;
      
      // Reduce score for precipitation
      if (currentWeather.precipitation > 0) {
        score -= 30;
      }
      
      // Factor in UV index
      score = score * Math.min(currentWeather.uv_index / 8, 1);
      
      return Math.max(0, Math.min(100, score));
    } catch (error) {
      return 50; // Default middle score if weather unavailable
    }
  }

  /**
   * Get optimal times for appliance usage based on weather forecast
   */
  async getOptimalUsageTimes(): Promise<Array<{
    hour: number;
    recommendation: string;
    confidence: number;
  }>> {
    try {
      const forecast = await this.getWeatherForecast(1);
      const todayForecast = forecast[0];
      
      if (!todayForecast) {
        return [];
      }
      
      const recommendations = [];
      const peakHour = this.calculatePeakProductionHour(todayForecast);
      
      // Peak solar hours based on calculated peak
      if (todayForecast.cloud_cover < 60) {
        // Pre-peak hour (1 hour before peak)
        recommendations.push({
          hour: Math.max(10, peakHour - 1),
          recommendation: 'Start high-energy appliances (dishwasher, washing machine)',
          confidence: 0.85
        });
        
        // Peak hour
        recommendations.push({
          hour: peakHour,
          recommendation: 'Peak solar time - ideal for cooking and water heating',
          confidence: 0.95
        });
        
        // Post-peak hour (1 hour after peak)
        recommendations.push({
          hour: Math.min(16, peakHour + 1),
          recommendation: 'Good time for pool pumps and EV charging',
          confidence: 0.8
        });
      }
      
      // Morning hours (if clear)
      if (todayForecast.cloud_cover < 40 && todayForecast.solar_radiation > 500) {
        recommendations.push({
          hour: 10,
          recommendation: 'Good morning solar - charge devices and run small appliances',
          confidence: 0.7
        });
      }
      
      // Afternoon hours (if still good conditions)
      if (todayForecast.cloud_cover < 70 && todayForecast.solar_radiation > 300) {
        recommendations.push({
          hour: 15,
          recommendation: 'Afternoon solar - continue with energy-intensive tasks',
          confidence: 0.75
        });
      }
      
      return recommendations.sort((a, b) => b.confidence - a.confidence);
    } catch (error) {
      return [];
    }
  }

  /**
   * Calculate the peak production hour based on weather conditions
   */
  private calculatePeakProductionHour(forecast: WeatherForecast): number {
    // Base peak hour for Spain (typically 12-14)
    let basePeakHour = 13;
    
    // Adjust based on cloud cover - earlier peak if cloudy
    if (forecast.cloud_cover > 70) {
      basePeakHour = 12; // Peak earlier when cloudy
    } else if (forecast.cloud_cover < 20) {
      basePeakHour = 14; // Peak later when clear
    }
    
    // Adjust based on temperature - earlier peak in summer
    const month = new Date(forecast.date).getMonth();
    if (month >= 5 && month <= 8) { // Summer months
      basePeakHour = Math.max(12, basePeakHour - 1);
    } else if (month >= 11 || month <= 2) { // Winter months
      basePeakHour = Math.min(14, basePeakHour + 1);
    }
    
    // Adjust based on solar radiation potential
    if (forecast.solar_radiation > 800) {
      basePeakHour = Math.max(12, basePeakHour - 1);
    } else if (forecast.solar_radiation < 400) {
      basePeakHour = Math.min(14, basePeakHour + 1);
    }
    
    return Math.max(10, Math.min(16, basePeakHour)); // Keep within 10-16 range
  }
}

export default WeatherService; 