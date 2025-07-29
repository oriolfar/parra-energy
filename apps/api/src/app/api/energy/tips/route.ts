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
    const language = searchParams.get('lang') || 'ca';
    
    // Get current weather data
    const weatherResponse = await axios.get(API_BASE_URL, {
      params: {
        latitude: LOCATION.latitude,
        longitude: LOCATION.longitude,
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
        daily: [
          'cloud_cover_mean',
          'precipitation_probability_max'
        ].join(','),
        timezone: 'Europe/Madrid',
        forecast_days: 1
      },
      timeout: 10000
    });

    const currentWeather = weatherResponse.data.current;
    const todayForecast = weatherResponse.data.daily;
    
    // Calculate weather quality score
    const weatherQuality = calculateWeatherQualityScore(currentWeather);
    
    // Get optimal usage times
    const optimalTimes = getOptimalUsageTimes(todayForecast, language);
    
    // Generate smart tips
    const tips = generateSmartTips(currentWeather, optimalTimes, weatherQuality, language);
    
    return NextResponse.json({
      tips,
      weather_quality_score: weatherQuality,
      optimal_times: optimalTimes,
      current_weather: {
        timestamp: new Date().toISOString(),
        location: LOCATION.name,
        temperature: currentWeather.temperature_2m,
        humidity: currentWeather.relative_humidity_2m,
        cloud_cover: currentWeather.cloud_cover,
        uv_index: currentWeather.uv_index,
        solar_radiation: currentWeather.global_tilted_irradiance,
        wind_speed: currentWeather.wind_speed_10m,
        precipitation: currentWeather.precipitation,
        weather_description: getWeatherDescription(currentWeather.weather_code),
      },
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
    console.error('Tips API error:', error);
    return NextResponse.json(
      { 
        error: 'Failed to generate tips',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    );
  }
}

function calculateWeatherQualityScore(weather: any): number {
  // Calculate quality score based on solar production potential
  let score = 100;
  
  // Reduce score based on cloud cover
  score -= weather.cloud_cover * 0.7;
  
  // Reduce score for precipitation
  if (weather.precipitation > 0) {
    score -= 30;
  }
  
  // Factor in UV index
  score = score * Math.min(weather.uv_index / 8, 1);
  
  return Math.max(0, Math.min(100, score));
}

function getOptimalUsageTimes(forecast: any, language: string): Array<{
  hour: number;
  recommendation: string;
  confidence: number;
}> {
  const recommendations = [];
  const cloudCover = forecast.cloud_cover_mean?.[0] || 50;
  
  // Peak solar hours (11 AM - 3 PM)
  if (cloudCover < 50) {
    recommendations.push({
      hour: 11,
      recommendation: language === 'ca' 
        ? 'Inicia electrodomèstics d\'alta potència (rentadora, rentaplats)'
        : 'Start high-energy appliances (dishwasher, washing machine)',
      confidence: 0.9
    });
    
    recommendations.push({
      hour: 13,
      recommendation: language === 'ca'
        ? 'Hora punta solar - ideal per cuinar i escalfar aigua'
        : 'Peak solar time - ideal for cooking and water heating',
      confidence: 0.95
    });
  }
  
  // Afternoon (2 PM - 5 PM)
  if (cloudCover < 60) {
    recommendations.push({
      hour: 15,
      recommendation: language === 'ca'
        ? 'Bon moment per bombes de piscina i càrrega de cotxe elèctric'
        : 'Good time for pool pumps and EV charging',
      confidence: 0.8
    });
  }
  
  return recommendations;
}

function generateSmartTips(
  weather: any, 
  optimalTimes: any[], 
  weatherQuality: number, 
  language: string
) {
  const tips = [];
  const now = new Date();
  const currentHour = now.getHours();
  
  // Weather-based tips
  if (weather.cloud_cover > 70) {
    tips.push({
      type: 'weather',
      priority: 'high',
      icon: '☁️',
      title: language === 'ca' ? 'Cel ennuvolat detectat' : 'Cloudy sky detected',
      message: language === 'ca' 
        ? 'Reduïu l\'ús d\'electrodomèstics d\'alta potència fins que millori el temps'
        : 'Reduce high-power appliance usage until weather improves',
      action: language === 'ca' ? 'Esperar millor temps' : 'Wait for better weather'
    });
  }
  
  if (weather.global_tilted_irradiance > 600) {
    tips.push({
      type: 'opportunity',
      priority: 'high',
      icon: '☀️',
      title: language === 'ca' ? 'Excel·lent generació solar' : 'Excellent solar generation',
      message: language === 'ca'
        ? 'Ara és el moment perfecte per posar la rentadora, rentaplats o carregar el cotxe'
        : 'Now is the perfect time to run washing machine, dishwasher or charge your car',
      action: language === 'ca' ? 'Aproveitar ara' : 'Take advantage now'
    });
  }
  
  // Time-based tips
  if (currentHour >= 11 && currentHour <= 15) {
    tips.push({
      type: 'timing',
      priority: 'medium',
      icon: '⏰',
      title: language === 'ca' ? 'Hora punta solar' : 'Solar peak hours',
      message: language === 'ca'
        ? 'Els panells solars estan al màxim rendiment. Programeu tasques que consumeixin molta energia'
        : 'Solar panels are at maximum efficiency. Schedule high-energy tasks',
      action: language === 'ca' ? 'Programar tasques' : 'Schedule tasks'
    });
  }
  
  if (currentHour >= 18 || currentHour <= 6) {
    tips.push({
      type: 'timing',
      priority: 'medium',
      icon: '🌙',
      title: language === 'ca' ? 'Hores nocturnes' : 'Night hours',
      message: language === 'ca'
        ? 'No hi ha generació solar. Eviteu electrodomèstics d\'alta potència'
        : 'No solar generation. Avoid high-power appliances',
      action: language === 'ca' ? 'Reduir consum' : 'Reduce consumption'
    });
  }
  
  // Weather quality tips
  if (weatherQuality > 80) {
    tips.push({
      type: 'optimization',
      priority: 'high',
      icon: '🚀',
      title: language === 'ca' ? 'Condicions òptimes' : 'Optimal conditions',
      message: language === 'ca'
        ? 'El temps és perfecte per la generació solar. Aproveiteu al màxim!'
        : 'Weather is perfect for solar generation. Make the most of it!',
      action: language === 'ca' ? 'Maximitzar ús' : 'Maximize usage'
    });
  }
  
  return tips;
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