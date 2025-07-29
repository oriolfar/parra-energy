import React, { useState } from 'react';
import styles from './ForecastModal.module.css';

interface HourlyData {
  hour: number;
  production: number; // 0-100 percentage
  weatherIcon: string;
  quality: 'excellent' | 'good' | 'moderate' | 'poor' | 'night';
  tip: string;
}

interface ForecastModalProps {
  isOpen: boolean;
  onClose: () => void;
  day: any;
  language: 'en' | 'ca';
  forecastData: any[];
}

const ForecastModal: React.FC<ForecastModalProps> = ({ isOpen, onClose, day, language, forecastData }) => {
  const [activeTooltip, setActiveTooltip] = useState<{ hour: number; tip: string; x: number; y: number } | null>(null);
  const [currentDayIndex, setCurrentDayIndex] = useState(0);
  const [touchStart, setTouchStart] = useState<number | null>(null);
  const [touchEnd, setTouchEnd] = useState<number | null>(null);

  // Initialize current day index when modal opens
  React.useEffect(() => {
    if (isOpen && forecastData.length > 0) {
      const dayIndex = forecastData.findIndex(d => d.date === day.date);
      setCurrentDayIndex(dayIndex >= 0 ? dayIndex : 0);
    }
  }, [isOpen, day, forecastData]);

  if (!isOpen || !day) return null;

  const handleHourCardInteraction = (hour: number, tip: string, event: React.MouseEvent) => {
    const rect = event.currentTarget.getBoundingClientRect();
    setActiveTooltip({
      hour,
      tip,
      x: rect.left + rect.width / 2,
      y: rect.top - 10
    });
  };

  const handleHourCardLeave = () => {
    setActiveTooltip(null);
  };

  const handleHourCardClick = (hour: number, tip: string, event: React.MouseEvent) => {
    // Toggle tooltip on click
    if (activeTooltip && activeTooltip.hour === hour) {
      setActiveTooltip(null);
    } else {
      handleHourCardInteraction(hour, tip, event);
    }
  };

  const handleHourCardEnter = (hour: number, tip: string, event: React.MouseEvent) => {
    handleHourCardInteraction(hour, tip, event);
  };

  // Navigation functions
  const goToPreviousDay = () => {
    if (currentDayIndex > 0) {
      setCurrentDayIndex(currentDayIndex - 1);
    }
  };

  const goToNextDay = () => {
    if (currentDayIndex < forecastData.length - 1) {
      setCurrentDayIndex(currentDayIndex + 1);
    }
  };

  // Touch/swipe handling
  const minSwipeDistance = 50;

  const onTouchStart = (e: React.TouchEvent) => {
    setTouchEnd(null);
    setTouchStart(e.targetTouches[0]?.clientX || null);
  };

  const onTouchMove = (e: React.TouchEvent) => {
    setTouchEnd(e.targetTouches[0]?.clientX || null);
  };

  const onTouchEnd = () => {
    if (!touchStart || !touchEnd) return;
    
    const distance = touchStart - touchEnd;
    const isLeftSwipe = distance > minSwipeDistance;
    const isRightSwipe = distance < -minSwipeDistance;

    if (isLeftSwipe && currentDayIndex < forecastData.length - 1) {
      goToNextDay();
    }
    if (isRightSwipe && currentDayIndex > 0) {
      goToPreviousDay();
    }
  };

  // Get current day from forecast data
  const currentDay = forecastData[currentDayIndex] || day;

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString(language === 'ca' ? 'ca-ES' : 'en-US', {
      weekday: 'long',
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  };

  const formatShortDate = (dateString: string) => {
    const date = new Date(dateString);
    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    return `${day}/${month}`;
  };

  const isToday = (dateString: string) => {
    const today = new Date();
    const date = new Date(dateString);
    return date.toDateString() === today.toDateString();
  };

  const getWeatherIcon = (weatherCode: number, irradiance: number, cloudCover: number) => {
    // For solar production, cloud cover is more important than general weather codes
    // Prioritize cloud cover data since it directly affects solar production
    
    // Night time (no solar production)
    if (irradiance === 0) return '🌙';
    
    // Clear conditions (low cloud cover)
    if (cloudCover < 20) return '☀️';
    
    // Partly cloudy conditions
    if (cloudCover < 50) return '⛅';
    
    // Mostly cloudy conditions
    if (cloudCover < 80) return '☁️';
    
    // Overcast conditions
    if (cloudCover >= 80) return '☁️';
    
    // Only use weather codes for extreme conditions (fog, rain, snow, storms)
    if (weatherCode >= 45 && weatherCode <= 48) return '🌫️'; // Fog
    if (weatherCode >= 51 && weatherCode <= 67) return '🌧️'; // Rain
    if (weatherCode >= 71 && weatherCode <= 77) return '❄️'; // Snow
    if (weatherCode >= 80 && weatherCode <= 82) return '🌧️'; // Rain showers
    if (weatherCode >= 85 && weatherCode <= 86) return '❄️'; // Snow showers
    if (weatherCode >= 95 && weatherCode <= 99) return '⛈️'; // Thunderstorm
    
    return '🌙'; // Night
  };

  const getProductionQuality = (irradiance: number, cloudCover: number, precipitation: number): 'excellent' | 'good' | 'moderate' | 'poor' | 'night' => {
    if (irradiance === 0) return 'night';
    
    // Calculate production percentage based on irradiance (max ~1000 W/m²)
    const productionPercent = Math.min((irradiance / 1000) * 100, 100);
    
    // Apply weather penalties
    let weatherPenalty = 1.0;
    
    // Cloud cover penalty
    if (cloudCover > 80) weatherPenalty *= 0.3;
    else if (cloudCover > 60) weatherPenalty *= 0.5;
    else if (cloudCover > 40) weatherPenalty *= 0.7;
    else if (cloudCover > 20) weatherPenalty *= 0.85;
    
    // Precipitation penalty
    if (precipitation > 80) weatherPenalty *= 0.2;
    else if (precipitation > 60) weatherPenalty *= 0.4;
    else if (precipitation > 40) weatherPenalty *= 0.6;
    else if (precipitation > 20) weatherPenalty *= 0.8;
    
    const finalProduction = productionPercent * weatherPenalty;
    
    // Determine quality based on final production
    if (finalProduction >= 80) return 'excellent';
    if (finalProduction >= 60) return 'good';
    if (finalProduction >= 30) return 'moderate';
    if (finalProduction > 0) return 'poor';
    return 'night';
  };

  const getQualityColor = (quality: string, production: number) => {
    // Use gold color for bars above 75% production
    if (production >= 75) return '#fbbf24'; // Gold
    
    switch (quality) {
      case 'excellent': return '#22c55e'; // Green
      case 'good': return '#facc15'; // Yellow
      case 'moderate': return '#f97316'; // Orange
      case 'poor': return '#ef4444'; // Red
      case 'night': return '#374151'; // Dark gray
      default: return '#374151';
    }
  };

  const getQualityText = (quality: string) => {
    if (language === 'ca') {
      switch (quality) {
        case 'excellent': return 'ALT';
        case 'good': return 'BO';
        case 'moderate': return 'MIG';
        case 'poor': return 'BAIX';
        case 'night': return 'NIT';
        default: return 'NIT';
      }
    } else {
      switch (quality) {
        case 'excellent': return 'HIGH';
        case 'good': return 'GOOD';
        case 'moderate': return 'MED';
        case 'poor': return 'LOW';
        case 'night': return 'NIGHT';
        default: return 'NIGHT';
      }
    }
  };

  const getTimeTip = (hour: number, irradiance: number, cloudCover: number, precipitation: number, temperature: number, uvIndex: number, language: 'en' | 'ca') => {
    if (irradiance === 0) {
      return language === 'ca' ? 'Nit - No hi ha producció solar' : 'Night - No solar production';
    }
    
    const productionPercent = Math.min((irradiance / 1000) * 100, 100);
    const weatherPenalty = 1.0 - (cloudCover / 100) * 0.7 - (precipitation / 100) * 0.5;
    const finalProduction = Math.round(productionPercent * weatherPenalty);
    
    return `${hour.toString().padStart(2, '0')}:00
${language === 'ca' ? 'Radiació' : 'Irradiance'}: ${irradiance} W/m²
${language === 'ca' ? 'Núvols' : 'Clouds'}: ${cloudCover}%
${language === 'ca' ? 'Pluja' : 'Rain'}: ${precipitation}%
${language === 'ca' ? 'Temperatura' : 'Temperature'}: ${temperature}°C
UV: ${uvIndex}
${language === 'ca' ? 'Producció' : 'Production'}: ${finalProduction}%`;
  };

  const generateHourlyData = (day: any): HourlyData[] => {
    const data: HourlyData[] = [];
    
    // Get hourly data from API
    const hourlyData = day.hourly_analysis?.hourly_data || [];
    
    // Only show hours from 5:00 to 23:00 (19 hours total)
    for (let hour = 5; hour <= 23; hour++) {
      let production = 0;
      let weatherIcon = '🌙';
      let quality: 'excellent' | 'good' | 'moderate' | 'poor' | 'night' = 'night';
      let tooltipData = '';
      
      // Find hourly data for this specific hour
      const hourData = hourlyData.find((h: any) => h.hour === hour);
      
      if (hourData) {
        // Use REAL weather data from API
        const irradiance = hourData.irradiance || 0;
        const cloudCover = hourData.cloudCover || 100;
        const precipitation = hourData.precipitation || 0;
        const temperature = hourData.temperature || 0;
        const uvIndex = hourData.uvIndex || 0;
        const weatherCode = hourData.weatherCode || 3;
        
        // Calculate production percentage based on irradiance
        production = Math.min((irradiance / 1000) * 100, 100);
        
        // Apply weather penalties
        let weatherPenalty = 1.0;
        
        // Cloud cover penalty
        if (cloudCover > 80) weatherPenalty *= 0.3;
        else if (cloudCover > 60) weatherPenalty *= 0.5;
        else if (cloudCover > 40) weatherPenalty *= 0.7;
        else if (cloudCover > 20) weatherPenalty *= 0.85;
        
        // Precipitation penalty
        if (precipitation > 80) weatherPenalty *= 0.2;
        else if (precipitation > 60) weatherPenalty *= 0.4;
        else if (precipitation > 40) weatherPenalty *= 0.6;
        else if (precipitation > 20) weatherPenalty *= 0.8;
        
        // Calculate final production
        production = Math.round(production * weatherPenalty);
        production = Math.min(100, Math.max(0, production));
        
        // Determine quality based on weather conditions
        quality = getProductionQuality(irradiance, cloudCover, precipitation);
        
        // Get weather icon based on weather code and conditions
        weatherIcon = getWeatherIcon(weatherCode, irradiance, cloudCover);
        
        // Create detailed tooltip
        tooltipData = getTimeTip(hour, irradiance, cloudCover, precipitation, temperature, uvIndex, language);
        
      } else {
        // Fallback for hours without data
        if (hour >= 6 && hour <= 20) {
          quality = 'moderate';
          weatherIcon = '☁️';
          production = 30; // Default moderate production
          tooltipData = `${hour.toString().padStart(2, '0')}:00
${language === 'ca' ? 'Dades no disponibles' : 'Data not available'}
${language === 'ca' ? 'Producció estimada' : 'Estimated production'}: ${production}%`;
        } else {
          quality = 'night';
          weatherIcon = '🌙';
          production = 0;
          tooltipData = `${hour.toString().padStart(2, '0')}:00
${language === 'ca' ? 'Nit - No hi ha producció solar' : 'Night - No solar production'}`;
        }
      }
      
      data.push({
        hour,
        production,
        weatherIcon,
        quality,
        tip: tooltipData
      });
    }
    
    return data;
  };

  const hourlyData = generateHourlyData(currentDay);

  // Calculate the actual peak hour based on production data (same as hourly bars)
  const getActualPeakHour = () => {
    const hourlyData = generateHourlyData(currentDay);
    if (hourlyData.length === 0) return currentDay.peak_production_hour || 13;
    
    // Find the hour with the highest production percentage (using the same calculation as the bars)
    const peakHour = hourlyData.reduce((max: any, current: any) => {
      return current.production > max.production ? current : max;
    });
    
    return peakHour.hour;
  };

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      {/* Side Navigation Arrows - Outside Modal */}
      {currentDayIndex > 0 && (
        <button 
          className={`${styles.sideArrow} ${styles.leftArrow}`}
          onClick={(e) => {
            e.stopPropagation();
            goToPreviousDay();
          }}
          title={language === 'ca' ? 'Dia anterior' : 'Previous day'}
        >
          ‹
        </button>
      )}
      
      {currentDayIndex < forecastData.length - 1 && (
        <button 
          className={`${styles.sideArrow} ${styles.rightArrow}`}
          onClick={(e) => {
            e.stopPropagation();
            goToNextDay();
          }}
          title={language === 'ca' ? 'Dia següent' : 'Next day'}
        >
          ›
        </button>
      )}

      <div 
        className={styles.modalContent} 
        onClick={(e) => e.stopPropagation()}
        onTouchStart={onTouchStart}
        onTouchMove={onTouchMove}
        onTouchEnd={onTouchEnd}
      >
        {/* Header */}
        <div className={styles.modalHeader}>
          <div className={styles.headerInfo}>
            <h2 className={styles.modalTitle}>{formatDate(currentDay.date)}</h2>
            <div className={styles.weatherSummary}>
              {getWeatherIcon(currentDay.weather_code || 3, currentDay.hourly_analysis?.max_irradiance || 500, currentDay.cloud_cover || 50)} {Math.round(currentDay.weather_factor * 100)}% {language === 'ca' ? 'eficiència solar' : 'solar efficiency'}
            </div>
          </div>
          
          {/* Mini Card Navigation */}
          <div className={styles.miniCardNavigation}>
            {forecastData.map((forecastDay: any, index: number) => (
              <button
                key={index}
                className={`${styles.miniCard} ${
                  index === currentDayIndex ? styles.miniCardActive : ''
                } ${isToday(forecastDay.date) ? styles.miniCardToday : ''}`}
                onClick={(e) => {
                  e.stopPropagation();
                  setCurrentDayIndex(index);
                }}
                title={formatDate(forecastDay.date)}
              >
                <div className={styles.miniCardDate}>{formatShortDate(forecastDay.date)}</div>
                {isToday(forecastDay.date) && (
                  <div className={styles.todayLabel}>
                    {language === 'ca' ? 'AVUI' : 'TODAY'}
                  </div>
                )}
              </button>
            ))}
          </div>
          
          <button className={styles.closeButton} onClick={onClose}>✕</button>
        </div>

        {/* Production Overview */}
        <div className={styles.productionOverview}>
          <div className={styles.overviewCard}>
            <div className={styles.overviewValue}>{currentDay.estimated_production_kwh.toFixed(1)} kWh</div>
            <div className={styles.overviewLabel}>{language === 'ca' ? 'Producció estimada' : 'Estimated production'}</div>
          </div>
          <div className={styles.overviewCard}>
            <div className={styles.overviewValue}>{currentDay.hourly_analysis?.total_production_hours || 12}h</div>
            <div className={styles.overviewLabel}>{language === 'ca' ? 'Hores de producció' : 'Production hours'}</div>
          </div>
          <div className={styles.overviewCard}>
            <div className={styles.overviewValue}>{getActualPeakHour()}:00h</div>
            <div className={styles.overviewLabel}>{language === 'ca' ? 'Hora màxima' : 'Peak hour'}</div>
          </div>
        </div>

        {/* 24-Hour Timeline */}
        <div className={styles.timelineSection}>
          <div className={styles.hourlyTimeline}>
            {hourlyData.map((hour) => (
              <div 
                key={hour.hour} 
                className={styles.hourCard}
                data-tooltip={hour.tip}
                onMouseEnter={(e) => handleHourCardEnter(hour.hour, hour.tip, e)}
                onMouseLeave={handleHourCardLeave}
                onClick={(e) => handleHourCardClick(hour.hour, hour.tip, e)}
              >
                <div className={styles.hourHeader}>
                  <div className={styles.hourTime}>{hour.hour.toString().padStart(2, '0')}:00</div>
                  <div className={styles.hourIcon}>{hour.weatherIcon}</div>
                </div>
                
                <div className={styles.productionBar}>
                  <div 
                    className={styles.productionFill}
                    style={{ 
                      height: `${hour.production}%`,
                      backgroundColor: getQualityColor(hour.quality, hour.production)
                    }}
                  />
                </div>
                
                <div className={styles.hourFooter}>
                  <div 
                    className={styles.qualityBadge}
                    style={{ backgroundColor: getQualityColor(hour.quality, hour.production) }}
                  >
                    {getQualityText(hour.quality)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Tooltip */}
        {activeTooltip && (
          <div
            className={styles.tooltip}
            style={{
              left: `${activeTooltip.x}px`,
              top: `${activeTooltip.y}px`
            }}
          >
            {activeTooltip.tip}
          </div>
        )}
      </div>
    </div>
  );
};

export default ForecastModal; 