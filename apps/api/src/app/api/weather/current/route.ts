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
    const response = await axios.get(API_BASE_URL, {
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
        timezone: 'Europe/Madrid',
      },
      timeout: 10000
    });

    const current = response.data.current;
    const weatherData = {
      timestamp: new Date().toISOString(),
      location: LOCATION.name,
      temperature: current.temperature_2m,
      humidity: current.relative_humidity_2m,
      cloud_cover: current.cloud_cover,
      uv_index: current.uv_index,
      solar_radiation: current.global_tilted_irradiance,
      wind_speed: current.wind_speed_10m,
      precipitation: current.precipitation,
      weather_description: getWeatherDescription(current.weather_code),
    };
    
    return NextResponse.json(weatherData, {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
    });
  } catch (error) {
    console.error('Weather API error:', error);
    return NextResponse.json(
      { 
        error: 'Failed to fetch weather data',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    );
  }
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