'use client';

import styles from './WeatherCard.module.css';

interface WeatherData {
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

interface SolarForecast {
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

interface WeatherCardProps {
  weatherData: WeatherData | null;
  solarForecast: SolarForecast[];
  language: 'en' | 'ca';
  getWeatherAdvice: () => string;
  getUsageTip: () => string;
  getCurrentScenario: () => string;
  energyData: any;
  getApplianceEquivalent: (watts: number) => string;
  getSavingsMessage: () => string;
}

export default function WeatherCard({
  weatherData,
  solarForecast,
  language,
  getWeatherAdvice,
  getUsageTip,
  getCurrentScenario,
  energyData,
  getApplianceEquivalent,
  getSavingsMessage
}: WeatherCardProps) {
  // Get today's forecast
  const todayForecast = solarForecast.find(day => {
    const today = new Date().toDateString();
    const dayDate = new Date(day.date).toDateString();
    return today === dayDate;
  });

  return (
    <div className={styles.weatherCard}>
      <div className={styles.weatherInfo}>
        <div className={styles.temperature}>
          {weatherData ? `${Math.round(weatherData.temperature)}°C` : '0°C'}
        </div>
        <div className={styles.weatherStatus}>
          {getWeatherAdvice()}
        </div>
        {weatherData && (
          <div className={styles.weatherDetails}>
            <span>☁️ {weatherData.cloud_cover}%</span>
            <span>💨 {weatherData.wind_speed} km/h</span>
            <span>💧 {weatherData.humidity}%</span>
          </div>
        )}
      </div>


    </div>
  );
} 