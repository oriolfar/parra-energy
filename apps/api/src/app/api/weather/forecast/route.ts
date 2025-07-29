import { NextRequest, NextResponse } from 'next/server';
import axios from 'axios';

// Direct Open-Meteo API call for Agramunt, Spain
const API_BASE_URL = 'https://api.open-meteo.com/v1/forecast';
const LOCATION = {
  latitude: 41.7869,
  longitude: 1.0968,
  name: 'Agramunt, Spain'
};

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const days = parseInt(searchParams.get('days') || '7');
    const solarCapacity = parseInt(searchParams.get('capacity') || '2200');
    
    const response = await axios.get(API_BASE_URL, {
      params: {
        latitude: LOCATION.latitude,
        longitude: LOCATION.longitude,
        daily: [
          'temperature_2m_max',
          'temperature_2m_min',
          'uv_index_max',
          'cloud_cover_mean',
          'precipitation_probability_max',
          'wind_speed_10m_max',
          'weather_code'
        ].join(','),
        hourly: [
          'temperature_2m',
          'cloud_cover',
          'uv_index',
          'global_tilted_irradiance',
          'precipitation_probability',
          'wind_speed_10m',
          'weather_code'
        ].join(','),
        timezone: 'Europe/Madrid',
        forecast_days: days
      },
      timeout: 10000
    });

    const daily = response.data.daily;
    const hourly = response.data.hourly;
    const weatherForecast = [];
    const solarForecast = [];

    for (let i = 0; i < daily.time.length && i < days; i++) {
      const currentDate = daily.time[i];
      
      // Calculate estimated solar radiation based on UV index and cloud cover
      const estimatedSolarRadiation = daily.uv_index_max[i] * 100 * (1 - daily.cloud_cover_mean[i] / 100);
      const expectedSolarProduction = calculateExpectedSolarProduction(
        estimatedSolarRadiation,
        daily.cloud_cover_mean[i],
        daily.uv_index_max[i]
      );

      const confidence = calculateForecastConfidence({
        cloud_cover: daily.cloud_cover_mean[i],
        precipitation_probability: daily.precipitation_probability_max[i]
      });

      // Calculate real peak hour from hourly solar radiation data
      const peakHour = calculatePeakHour(hourly, currentDate);

      weatherForecast.push({
        date: currentDate,
        location: LOCATION.name,
        temperature_min: daily.temperature_2m_min[i],
        temperature_max: daily.temperature_2m_max[i],
        cloud_cover: daily.cloud_cover_mean[i],
        uv_index: daily.uv_index_max[i],
        solar_radiation: estimatedSolarRadiation,
        precipitation_probability: daily.precipitation_probability_max[i],
        wind_speed: daily.wind_speed_10m_max[i],
        weather_code: daily.weather_code[i],
        weather_description: getWeatherDescription(daily.weather_code[i]),
        expected_solar_production: expectedSolarProduction,
        forecast_created_at: new Date().toISOString(),
      });

      solarForecast.push({
        date: currentDate,
        estimated_production_kwh: expectedSolarProduction * solarCapacity / 1000,
        peak_production_hour: peakHour,
        weather_factor: expectedSolarProduction,
        confidence_level: confidence,
        // Add enhanced hourly analysis
        hourly_analysis: analyzeHourlyProduction(hourly, currentDate, solarCapacity),
      });
    }
    
    return NextResponse.json({
      weather: weatherForecast,
      solar: solarForecast,
      timestamp: new Date().toISOString()
    }, {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
    });
  } catch (error) {
    console.error('Forecast API error:', error);
    return NextResponse.json(
      { 
        error: 'Failed to fetch forecast data',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    );
  }
}

function calculateExpectedSolarProduction(
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

function calculateForecastConfidence(forecast: { cloud_cover: number; precipitation_probability: number }): number {
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

function getWeatherDescription(weatherCode: number): string {
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
 * Calculate the peak production hour based on hourly solar radiation data
 */
function calculatePeakHour(hourlyData: any, targetDate: string): number {
  try {
    // Find the day's data
    const dayStart = new Date(targetDate);
    const dayEnd = new Date(targetDate);
    dayEnd.setDate(dayEnd.getDate() + 1);
    
    const dayStartStr = dayStart.toISOString().split('T')[0] || targetDate;
    const dayEndStr = dayEnd.toISOString().split('T')[0] || targetDate;
    
    // Get hourly data for this specific day
    const dayHourlyData = hourlyData.time
      .map((time: string, index: number) => ({
        time,
        irradiance: hourlyData.global_tilted_irradiance[index],
        hour: new Date(time).getHours()
      }))
      .filter((item: any) => {
        const itemDate = item.time.split('T')[0];
        return itemDate >= dayStartStr && itemDate < dayEndStr;
      });
    
    // Find hour with maximum solar radiation
    if (dayHourlyData.length === 0) {
      return 13; // Fallback to typical peak
    }
    
    const peakHour = dayHourlyData.reduce((max: any, current: any) => 
      current.irradiance > max.irradiance ? current : max
    );
    
    return peakHour.hour;
  } catch (error) {
    console.error('Error calculating peak hour:', error);
    return 13; // Fallback to typical peak
  }
} 

/**
 * Analyze hourly production to provide optimization insights based on real weather data
 */
function analyzeHourlyProduction(hourlyData: any, targetDate: string, solarCapacity: number): any {
  try {
    // Find the day's data
    const dayStart = new Date(targetDate);
    const dayEnd = new Date(targetDate);
    dayEnd.setDate(dayEnd.getDate() + 1);
    
    const dayStartStr = dayStart.toISOString().split('T')[0] || targetDate;
    const dayEndStr = dayEnd.toISOString().split('T')[0] || targetDate;
    
    // Get hourly data for this specific day
    const dayHourlyData = hourlyData.time
      .map((time: string, index: number) => ({
        time,
        hour: new Date(time).getHours(),
        irradiance: hourlyData.global_tilted_irradiance[index],
        cloudCover: hourlyData.cloud_cover[index],
        temperature: hourlyData.temperature_2m[index],
        uvIndex: hourlyData.uv_index[index],
        precipitation: hourlyData.precipitation_probability[index],
        weatherCode: hourlyData.weather_code[index]
      }))
      .filter((item: any) => {
        const itemDate = item.time.split('T')[0];
        return itemDate >= dayStartStr && itemDate < dayEndStr;
      });
    
    if (dayHourlyData.length === 0) {
      return {
        production_start: 8,
        production_end: 18,
        peak_hour: 13,
        optimal_windows: [
          { start: 11, end: 15, description: 'Peak solar hours' }
        ],
        total_production_hours: 8,
        max_irradiance: 500
      };
    }
    
    // Calculate production windows based on REAL solar radiation
    // Only include hours with meaningful solar production (>100 W/m²)
    const productionHours = dayHourlyData.filter((item: any) => item.irradiance > 100);
    const productionStart = productionHours.length > 0 ? Math.min(...productionHours.map((h: any) => h.hour)) : 8;
    const productionEnd = productionHours.length > 0 ? Math.max(...productionHours.map((h: any) => h.hour)) : 18;
    
    // Find optimal usage windows based on weather conditions
    const optimalWindows = [];
    
    // High production window: hours with excellent conditions
    const excellentHours = dayHourlyData.filter((item: any) => 
      item.irradiance > 400 && 
      item.cloudCover < 30 && 
      item.precipitation < 20
    );
    
    if (excellentHours.length > 0) {
      const excellentStart = Math.min(...excellentHours.map((h: any) => h.hour));
      const excellentEnd = Math.max(...excellentHours.map((h: any) => h.hour));
      
      optimalWindows.push({
        start: excellentStart,
        end: excellentEnd,
        description: 'Millor moment per electrodomèstics'
      });
    }
    
    // Good production window: hours with good conditions
    const goodHours = dayHourlyData.filter((item: any) => 
      item.irradiance > 200 && 
      item.cloudCover < 60 && 
      item.precipitation < 40
    );
    
    if (goodHours.length > 0 && optimalWindows.length === 0) {
      const goodStart = Math.min(...goodHours.map((h: any) => h.hour));
      const goodEnd = Math.max(...goodHours.map((h: any) => h.hour));
      
      optimalWindows.push({
        start: goodStart,
        end: goodEnd,
        description: 'Bon moment per ús'
      });
    }
    
    // Moderate production window: hours with acceptable conditions
    const moderateHours = dayHourlyData.filter((item: any) => 
      item.irradiance > 100 && 
      item.cloudCover < 80 && 
      item.precipitation < 60
    );
    
    if (moderateHours.length > 0 && optimalWindows.length === 0) {
      const moderateStart = Math.min(...moderateHours.map((h: any) => h.hour));
      const moderateEnd = Math.max(...moderateHours.map((h: any) => h.hour));
      
      optimalWindows.push({
        start: moderateStart,
        end: moderateEnd,
        description: 'Moment acceptable'
      });
    }
    
    // If no optimal windows found, create a fallback based on best available hours
    if (optimalWindows.length === 0) {
      const bestHours = dayHourlyData.filter((item: any) => item.irradiance > 50);
      if (bestHours.length > 0) {
        const bestStart = Math.min(...bestHours.map((h: any) => h.hour));
        const bestEnd = Math.max(...bestHours.map((h: any) => h.hour));
        
        optimalWindows.push({
          start: bestStart,
          end: bestEnd,
          description: 'Millor moment disponible'
        });
      }
    }
    
    // Find peak hour (hour with maximum solar radiation)
    const peakHour = dayHourlyData.reduce((max: any, current: any) => 
      current.irradiance > max.irradiance ? current : max
    );
    
    // Calculate total production hours (hours with meaningful production)
    const totalProductionHours = productionHours.length;
    
    // Calculate max irradiance
    const maxIrradiance = Math.max(...dayHourlyData.map((h: any) => h.irradiance));
    
    return {
      production_start: productionStart,
      production_end: productionEnd,
      peak_hour: peakHour.hour,
      optimal_windows: optimalWindows,
      total_production_hours: totalProductionHours,
      max_irradiance: maxIrradiance,
      hourly_data: dayHourlyData // Include detailed hourly data for frontend
    };
  } catch (error) {
    console.error('Error analyzing hourly production:', error);
    return {
      production_start: 8,
      production_end: 18,
      peak_hour: 13,
      optimal_windows: [
        { start: 11, end: 15, description: 'Peak solar hours' }
      ],
      total_production_hours: 8,
      max_irradiance: 500
    };
  }
} 