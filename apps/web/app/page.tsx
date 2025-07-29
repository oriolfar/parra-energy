'use client';

import { useState, useEffect } from 'react';
import styles from "./page.module.css";
import PowerFlowCardPlus from '../components/PowerFlowCardPlus';
import ConnectionModal from '../components/ConnectionModal';
import WeatherCard from '../components/WeatherCard';
import SmartTipsCard from '../components/SmartTipsCard';
import { getFlowColor } from '../utils/getFlowColor';
import ForecastModal from '../components/ForecastModal';
import { TIPS_LIBRARY, filterTipsByConditions, getCurrentSeason, getWeatherCondition } from '../utils/tipsLibrary';

interface EnergyData {
  solarProduction: number;
  consumption: number;
  gridPower: number;
  timestamp?: string;
  scenario?: number;
}

// Tesla-style energy data interface
interface TeslaEnergyData {
  solarProduction: number;
  homeConsumption: number;
  gridImport: number;
}

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

interface SmartTip {
  type: 'weather' | 'opportunity' | 'timing' | 'optimization' | 'maintenance' | 'seasonal' | 'emergency' | 'efficiency';
  priority: 'high' | 'medium' | 'low';
  icon: string;
  title: string;
  message: string;
  action: string;
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
    hourly_data?: Array<{
      hour: number;
      irradiance: number;
      cloudCover?: number;
      precipitation?: number;
      temperature?: number;
      uvIndex?: number;
      weatherCode?: number;
    }>;
  };
}

interface FroniusStatus {
  online: boolean;
  error?: string;
  mode?: string;
  timestamp?: string;
  errorCount?: number;
}

// Clean scenario generator - Shows ACTUAL energy flows clearly
function generateMockEnergyData(): EnergyData {
  const now = new Date();
  const minute = now.getMinutes();
  const scenario = Math.floor(minute / 10) % 4; // Changes every 10 minutes for easier testing
  
  let solarProduction = 0;
  let consumption = 0;
  let scenarioName = '';
  
  switch (scenario) {
    case 0: // Only Solar → Home (perfect match)
      solarProduction = 900;
      consumption = 900;
      scenarioName = 'solar_direct';
      break;
    case 1: // Solar → Home + Solar → Grid (overproducing)
      solarProduction = 1400;
      consumption = 800;
      scenarioName = 'solar_selling';
      break;
    case 2: // Solar → Home + Grid → Home (mixed)
      solarProduction = 500;
      consumption = 1200;
      scenarioName = 'solar_grid_mix';
      break;
    case 3: // Only Grid → Home (no solar)
      solarProduction = 0;
      consumption = 1000;
      scenarioName = 'grid_only';
      break;
  }
  
  // Add small realistic variation (±5%)
  const variation = 0.05;
  solarProduction *= (1 + (Math.random() - 0.5) * variation);
  consumption *= (1 + (Math.random() - 0.5) * variation);
  
  // Ensure minimum values
  solarProduction = Math.max(0, solarProduction);
  consumption = Math.max(200, consumption);
  
  return {
    solarProduction: Math.round(solarProduction),
    consumption: Math.round(consumption),
    gridPower: Math.round(consumption - solarProduction),
    timestamp: now.toISOString(),
    scenario: scenario
  };
}

export default function SolarEnergyDashboard() {
  const [energyData, setEnergyData] = useState<EnergyData | null>(null);
  const [froniusStatus, setFroniusStatus] = useState<FroniusStatus | null>(null);
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null);
  const [smartTips, setSmartTips] = useState<SmartTip[]>([]);
  const [solarForecast, setSolarForecast] = useState<SolarForecast[]>([]);
  const [language, setLanguage] = useState<'en' | 'ca'>('ca');
  const [lastUpdate, setLastUpdate] = useState<string>('');
  const [isCheckingConnection, setIsCheckingConnection] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isForecastModalOpen, setIsForecastModalOpen] = useState(false);
  const [selectedDay, setSelectedDay] = useState<any>(null);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  
  // Manual control states
  const [isManualMode, setIsManualMode] = useState(false);
  const [manualSolarProduction, setManualSolarProduction] = useState(1100); // watts (default ~50% of 2.2kW)
  const [manualHomeConsumption, setManualHomeConsumption] = useState(1200); // watts (default ~25% of 5kW)

  useEffect(() => {
    fetchEnergyData();
    fetchFroniusStatus();
    fetchWeatherData();
    fetchSmartTips();
    fetchSolarForecast();
    
    const energyInterval = setInterval(fetchEnergyData, 30000);
    const statusInterval = setInterval(fetchFroniusStatus, 60000); // Check status every minute
    const weatherInterval = setInterval(fetchWeatherData, 300000); // 5 minutes
    const tipsInterval = setInterval(fetchSmartTips, 600000); // 10 minutes
    
    return () => {
      clearInterval(energyInterval);
      clearInterval(statusInterval);
      clearInterval(weatherInterval);
      clearInterval(tipsInterval);
    };
  }, []);

  useEffect(() => {
    const handleScroll = () => {
      // Add scroll handling if needed
    };

    // Add click outside handler for dropdown
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Element;
      if (!target.closest(`.${styles.dropdownContainer}`)) {
        setIsDropdownOpen(false);
      }
    };

    if (isDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isDropdownOpen]);

  const fetchEnergyData = async () => {
    try {
      if (isManualMode) {
        // Use manual slider values
        const manualData: EnergyData = {
          solarProduction: manualSolarProduction,
          consumption: manualHomeConsumption,
          gridPower: manualHomeConsumption - manualSolarProduction,
          timestamp: new Date().toISOString(),
          scenario: 4 // Manual mode scenario
        };
        setEnergyData(manualData);
      } else {
        // Use demo/system data
      setEnergyData(generateMockEnergyData());
      }
      setLastUpdate(new Date().toLocaleTimeString());
    } catch (error) {
      console.error('Failed to generate energy data:', error);
    }
  };

  // Update energy data when manual values change
  useEffect(() => {
    if (isManualMode) {
      fetchEnergyData();
    }
  }, [isManualMode, manualSolarProduction, manualHomeConsumption]);

  // Auto-regenerate tips when data changes (live updates)
  useEffect(() => {
    const newTips = generateSmartTips();
    setSmartTips(newTips);
  }, [energyData, weatherData, solarForecast, language]); // Regenerate tips when any data changes

  const fetchFroniusStatus = async () => {
    try {
      const response = await fetch('http://localhost:3002/api/fronius/status');
      if (response.ok) {
        const status = await response.json();
        setFroniusStatus(status);
      } else {
        // If API is not responding properly, set demo mode
        setFroniusStatus({ online: false, error: 'API not responding' });
      }
    } catch (error) {
      console.error('Failed to fetch Fronius status:', error);
      // If fetch fails, set demo mode
      setFroniusStatus({ online: false, error: 'Connection failed' });
    }
  };

  const forceReconnect = async () => {
    setIsCheckingConnection(true);
    try {
      const response = await fetch('http://localhost:3002/api/fronius/status', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action: 'force_reconnect' }),
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('Reconnection result:', result);
        // Refresh status after reconnection attempt
        await fetchFroniusStatus();
      }
    } catch (error) {
      console.error('Failed to force reconnection:', error);
    } finally {
      setIsCheckingConnection(false);
    }
  };

  const fetchWeatherData = async () => {
    try {
      const response = await fetch('http://localhost:3002/api/weather/current');
      if (response.ok) {
        const data = await response.json();
        setWeatherData(data);
      }
    } catch (error) {
      console.error('Failed to fetch weather data:', error);
    }
  };

  const generateSmartTips = (): SmartTip[] => {
    const now = new Date();
    const currentHour = now.getHours();
    const currentDay = now.getDay();
    
    const tips: SmartTip[] = [];
    
    // Get current live data
    const currentSolarProduction = energyData?.solarProduction || 0;
    const currentConsumption = energyData?.consumption || 0;
    const currentGridPower = energyData?.gridPower || 0;
    const currentCloudCover = weatherData?.cloud_cover || 0;
    const currentTemperature = weatherData?.temperature || 20;
    const currentWeatherDesc = weatherData?.weather_description || '';
    const isDaytime = currentHour >= 6 && currentHour <= 20;
    const isPeakSun = currentHour >= 10 && currentHour <= 16;
    
    // Calculate live metrics
    const solarEfficiency = currentSolarProduction > 0 ? Math.round((currentSolarProduction / 2200) * 100) : 0;
    const isSellingToGrid = currentGridPower < -50; // Selling more than 50W
    const isBuyingFromGrid = currentGridPower > 50; // Buying more than 50W
    const isSelfSufficient = Math.abs(currentGridPower) <= 50; // Within 50W of self-sufficiency
    const excessPower = Math.abs(currentGridPower);
    const hourlySavings = isSellingToGrid ? (excessPower * 0.0003).toFixed(2) : '0.00';
    const hourlyCost = isBuyingFromGrid ? (currentGridPower * 0.0003).toFixed(2) : '0.00';

    // TIP 1: Live Production Status (Always show this first)
    if (energyData) {
      if (currentSolarProduction === 0 && isDaytime) {
        // No production during daytime - potential issue
        tips.push({
          type: 'emergency',
          priority: 'high',
          icon: '⚡',
          title: language === 'ca' ? 'No Hi Ha Producció Solar!' : 'No Solar Production!',
          message: language === 'ca'
            ? `Els panells no generen energia (${currentSolarProduction}W). Verifiqui el sistema.`
            : `Panels not generating power (${currentSolarProduction}W). Check system.`,
          action: language === 'ca' ? 'Contacti tècnic solar' : 'Contact solar technician'
        });
      } else if (currentSolarProduction > 0 && isDaytime) {
        if (solarEfficiency >= 80) {
          // Excellent production - encourage heavy usage
          tips.push({
            type: 'opportunity',
            priority: 'high',
            icon: '🧺',
            title: language === 'ca' ? 'Producció Excel·lent!' : 'Excellent Production!',
            message: language === 'ca'
              ? `Els panells funcionen al ${solarEfficiency}% (${currentSolarProduction}W). Ús lliure d'electrodomèstics!`
              : `Panels working at ${solarEfficiency}% (${currentSolarProduction}W). Free appliance usage!`,
            action: language === 'ca' ? 'Posi rentadora i rentavelles ara!' : 'Start washing machine and dishwasher now!'
          });
        } else if (solarEfficiency >= 60) {
          // Good production - moderate usage
          tips.push({
            type: 'opportunity',
            priority: 'medium',
            icon: '🍽️',
            title: language === 'ca' ? 'Bona Producció Solar' : 'Good Solar Production',
            message: language === 'ca'
              ? `Els panells generen ${currentSolarProduction}W (${solarEfficiency}%). Podeu utilitzar electrodomèstics.`
              : `Panels generating ${currentSolarProduction}W (${solarEfficiency}%). You can use appliances.`,
            action: language === 'ca' ? 'Utilitzi electrodomèstics moderadament' : 'Use appliances moderately'
          });
        } else if (solarEfficiency >= 30) {
          // Moderate production - light usage
          tips.push({
            type: 'timing',
            priority: 'medium',
            icon: '🔋',
            title: language === 'ca' ? 'Producció Moderada' : 'Moderate Production',
            message: language === 'ca'
              ? `Els panells generen ${currentSolarProduction}W (${solarEfficiency}%). Carregui dispositius.`
              : `Panels generating ${currentSolarProduction}W (${solarEfficiency}%). Charge devices.`,
            action: language === 'ca' ? 'Carregui telèfons i tablets' : 'Charge phones and tablets'
          });
        } else {
          // Low production - minimal usage
          tips.push({
            type: 'timing',
            priority: 'medium',
            icon: '⏰',
            title: language === 'ca' ? 'Producció Baixa' : 'Low Production',
            message: language === 'ca'
              ? `Els panells generen ${currentSolarProduction}W (${solarEfficiency}%). Esperi millors condicions.`
              : `Panels generating ${currentSolarProduction}W (${solarEfficiency}%). Wait for better conditions.`,
            action: language === 'ca' ? 'Utilitzi només dispositius essencials' : 'Use only essential devices'
          });
        }
      } else if (!isDaytime) {
        // Night hours - no solar production
        tips.push({
          type: 'timing',
          priority: 'high',
          icon: '🌙',
          title: language === 'ca' ? 'Hores Nocturnes' : 'Night Hours',
          message: language === 'ca'
            ? `No hi ha generació solar. Consum actual: ${currentConsumption}W.`
            : `No solar generation. Current consumption: ${currentConsumption}W.`,
          action: language === 'ca' ? 'Utilitzi només il·luminació LED' : 'Use only LED lighting'
        });
      }
    }

    // TIP 2: Live Energy Flow Status (Always show this second)
    if (energyData) {
      if (isSellingToGrid) {
        // Selling excess energy - encourage more usage
        tips.push({
          type: 'opportunity',
          priority: 'high',
          icon: '💰',
          title: language === 'ca' ? 'Venent Energia!' : 'Selling Energy!',
          message: language === 'ca'
            ? `Excedent de ${excessPower}W. Estalviant €${hourlySavings}/hora. Aprofiti per més electrodomèstics!`
            : `Excess of ${excessPower}W. Saving €${hourlySavings}/hour. Take advantage for more appliances!`,
          action: language === 'ca' ? 'Utilitzi més electrodomèstics ara!' : 'Use more appliances now!'
        });
      } else if (isBuyingFromGrid) {
        // Buying from grid - reduce usage
        tips.push({
          type: 'timing',
          priority: 'medium',
          icon: '⚡',
          title: language === 'ca' ? 'Comprant de la Xarxa' : 'Buying from Grid',
          message: language === 'ca'
            ? `Consumant ${currentGridPower}W de la xarxa. Cost: €${hourlyCost}/hora.`
            : `Consuming ${currentGridPower}W from grid. Cost: €${hourlyCost}/hour.`,
          action: language === 'ca' ? 'Redueixi el consum d\'energia' : 'Reduce energy consumption'
        });
      } else if (isSelfSufficient) {
        // Perfect balance - maintain usage
        tips.push({
          type: 'efficiency',
          priority: 'high',
          icon: '⚖️',
          title: language === 'ca' ? 'Autosuficiència Energètica!' : 'Energy Self-Sufficiency!',
          message: language === 'ca'
            ? `Producció: ${currentSolarProduction}W, Consum: ${currentConsumption}W. Perfect equilibri!`
            : `Production: ${currentSolarProduction}W, Consumption: ${currentConsumption}W. Perfect balance!`,
          action: language === 'ca' ? 'Mantingui aquest equilibri!' : 'Maintain this balance!'
        });
      }
    }

    // TIP 3: Live Weather + Forecast Recommendation (Always show this third)
    if (weatherData) {
      // Current weather conditions
      if (currentCloudCover <= 10) {
        // Perfect sunny day
        tips.push({
          type: 'weather',
          priority: 'high',
          icon: '☀️',
          title: language === 'ca' ? 'Dia Perfecte!' : 'Perfect Day!',
          message: language === 'ca'
            ? `Només ${currentCloudCover}% de núvols i ${currentTemperature}°C. Màxima eficiència solar.`
            : `Only ${currentCloudCover}% clouds and ${currentTemperature}°C. Maximum solar efficiency.`,
          action: language === 'ca' ? 'Aprofiti per electrodomèstics d\'alta potència!' : 'Take advantage for high-power appliances!'
        });
      } else if (currentCloudCover <= 30) {
        // Partly cloudy - still good
        tips.push({
          type: 'weather',
          priority: 'medium',
          icon: '⛅',
          title: language === 'ca' ? 'Dia Bo' : 'Good Day',
          message: language === 'ca'
            ? `${currentCloudCover}% de núvols, ${currentTemperature}°C. Producció solar adequada.`
            : `${currentCloudCover}% clouds, ${currentTemperature}°C. Adequate solar production.`,
          action: language === 'ca' ? 'Utilitzi electrodomèstics moderadament' : 'Use appliances moderately'
        });
      } else if (currentCloudCover <= 70) {
        // Cloudy - reduced production
        tips.push({
          type: 'weather',
          priority: 'medium',
          icon: '☁️',
          title: language === 'ca' ? 'Dia Núvol' : 'Cloudy Day',
          message: language === 'ca'
            ? `${currentCloudCover}% de núvols. Producció solar reduïda.`
            : `${currentCloudCover}% clouds. Reduced solar production.`,
          action: language === 'ca' ? 'Utilitzi només electrodomèstics essencials' : 'Use only essential appliances'
        });
      } else {
        // Very cloudy - minimal production
        tips.push({
          type: 'weather',
          priority: 'high',
          icon: '🌧️',
          title: language === 'ca' ? 'Dia Molt Núvol' : 'Very Cloudy Day',
          message: language === 'ca'
            ? `${currentCloudCover}% de núvols. Producció solar mínima esperada.`
            : `${currentCloudCover}% clouds. Minimal solar production expected.`,
          action: language === 'ca' ? 'Eviti electrodomèstics d\'alta potència' : 'Avoid high-power appliances'
        });
      }
    } else if (solarForecast && solarForecast.length > 0) {
      // If no current weather, use forecast data
      const today = solarForecast[0];
      if (today) {
        const todayEfficiency = Math.round((today.estimated_production_kwh / 22) * 100);
        
        if (todayEfficiency >= 70) {
          tips.push({
            type: 'weather',
            priority: 'high',
            icon: '🌤️',
            title: language === 'ca' ? 'Previsió Excel·lent!' : 'Excellent Forecast!',
            message: language === 'ca'
              ? `Avui es preveu ${todayEfficiency}% de producció solar.`
              : `Today expects ${todayEfficiency}% solar production.`,
            action: language === 'ca' ? 'Aprofiti per electrodomèstics!' : 'Take advantage for appliances!'
          });
        } else if (todayEfficiency >= 50) {
          tips.push({
            type: 'weather',
            priority: 'medium',
            icon: '🌤️',
            title: language === 'ca' ? 'Previsió Bona' : 'Good Forecast',
            message: language === 'ca'
              ? `Avui es preveu ${todayEfficiency}% de producció solar.`
              : `Today expects ${todayEfficiency}% solar production.`,
            action: language === 'ca' ? 'Utilitzi electrodomèstics moderadament' : 'Use appliances moderately'
          });
        } else {
          tips.push({
            type: 'weather',
            priority: 'medium',
            icon: '🌤️',
            title: language === 'ca' ? 'Previsió Baixa' : 'Low Forecast',
            message: language === 'ca'
              ? `Avui es preveu ${todayEfficiency}% de producció solar.`
              : `Today expects ${todayEfficiency}% solar production.`,
            action: language === 'ca' ? 'Utilitzi només electrodomèstics essencials' : 'Use only essential appliances'
          });
        }
      }
    }

    // Ensure we always have exactly 3 tips
    while (tips.length < 3) {
      // Add fallback tips based on available data
      if (tips.length === 0) {
        // No data available
        tips.push({
          type: 'optimization',
          priority: 'medium',
          icon: '💡',
          title: language === 'ca' ? 'Consell General Solar' : 'General Solar Tip',
          message: language === 'ca'
            ? 'Els panells solars funcionen millor entre les 10:00 i les 16:00 hores.'
            : 'Solar panels work best between 10:00 AM and 4:00 PM.',
          action: language === 'ca' ? 'Utilitzeu electrodomèstics en aquestes hores' : 'Use appliances during these hours'
        });
      } else if (tips.length === 1) {
        // Only one tip - add timing advice
        tips.push({
          type: 'timing',
          priority: 'medium',
          icon: '⏰',
          title: language === 'ca' ? 'Programació Intel·ligent' : 'Smart Scheduling',
          message: language === 'ca'
            ? 'Programeu electrodomèstics durant les hores de màxima producció solar.'
            : 'Schedule appliances during peak solar production hours.',
          action: language === 'ca' ? 'Programeu tasques per les 12:00-15:00' : 'Schedule tasks for 12:00-15:00'
        });
      } else {
        // Two tips - add optimization advice
        tips.push({
          type: 'optimization',
          priority: 'low',
          icon: '🔋',
          title: language === 'ca' ? 'Carregar Dispositius' : 'Charge Devices',
          message: language === 'ca'
            ? 'Carregueu telèfons i tablets durant les hores de sol per充分利用 l\'energia gratuïta.'
            : 'Charge phones and tablets during sunny hours to use free energy.',
          action: language === 'ca' ? 'Carregueu ara si hi ha sol' : 'Charge now if sunny'
        });
      }
    }

    // Return exactly 3 tips
    return tips.slice(0, 3);
  };

  // Helper function to format date
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString(language === 'ca' ? 'ca-ES' : 'en-US', { 
      month: 'short', 
      day: 'numeric' 
    });
  };

  const fetchSmartTips = async () => {
    try {
      // Generate tips based on current live data
      const generatedTips = generateSmartTips();
      setSmartTips(generatedTips);
    } catch (error) {
      console.error('Failed to generate smart tips:', error);
      // Fallback to basic tips - always provide exactly 3 tips
      setSmartTips([
        {
          type: 'optimization',
          priority: 'medium',
          icon: '💡',
          title: language === 'ca' ? 'Consell General Solar' : 'General Solar Tip',
          message: language === 'ca'
            ? 'Els panells solars funcionen millor entre les 10:00 i les 16:00 hores.'
            : 'Solar panels work best between 10:00 AM and 4:00 PM.',
          action: language === 'ca' ? 'Utilitzeu electrodomèstics en aquestes hores' : 'Use appliances during these hours'
        },
        {
          type: 'timing',
          priority: 'medium',
          icon: '⏰',
          title: language === 'ca' ? 'Programació Intel·ligent' : 'Smart Scheduling',
          message: language === 'ca'
            ? 'Programeu electrodomèstics durant les hores de màxima producció solar.'
            : 'Schedule appliances during peak solar production hours.',
          action: language === 'ca' ? 'Programeu tasques per les 12:00-15:00' : 'Schedule tasks for 12:00-15:00'
        },
        {
          type: 'optimization',
          priority: 'low',
          icon: '🔋',
          title: language === 'ca' ? 'Carregar Dispositius' : 'Charge Devices',
          message: language === 'ca'
            ? 'Carregueu telèfons i tablets durant les hores de sol per充分利用 l\'energia gratuïta.'
            : 'Charge phones and tablets during sunny hours to use free energy.',
          action: language === 'ca' ? 'Carregueu ara si hi ha sol' : 'Charge now if sunny'
        }
      ]);
    }
  };



  const fetchSolarForecast = async () => {
    try {
      const response = await fetch('http://localhost:3002/api/weather/forecast?days=7&capacity=2200');
      if (response.ok) {
        const data = await response.json();
        // Utilitzar directament les dades de l'API que ja inclouen l'anàlisi horària real
        setSolarForecast(data.solar || []);
      }
    } catch (error) {
      console.error('Failed to fetch solar forecast:', error);
    }
  };

  const getConnectionStatusIcon = () => {
    if (!froniusStatus) return '��';
    
    const { online } = froniusStatus;
    
    if (online) {
      return '��';
    }
    return '🔴';
  };

  const getConnectionStatusText = () => {
    if (!froniusStatus) {
      return language === 'ca' ? 'Versió Demo' : 'Demo Version';
    }
    
    if (isActuallyConnected()) {
      return language === 'ca' ? 'Connectat' : 'Connected';
    } else {
      return language === 'ca' ? 'Versió Demo - Dades simulades' : 'Demo Version - Simulated data';
    }
  };

  // Check if we're actually connected to real Fronius data
  const isActuallyConnected = () => {
    // If it's a mock service, consider it as demo mode
    if (froniusStatus?.mode && froniusStatus.mode.includes('Mock')) {
      return false;
    }
    return froniusStatus?.online === true && !froniusStatus?.error;
  };

  // Get connection status icon with proper emojis
  const getConnectionIcon = () => {
    if (!froniusStatus) return '🤖';
    
    if (isActuallyConnected()) {
      return '🔌';
    }
    return '🤖';
  };

  // Add scroll animation to header
  useEffect(() => {
    const handleScroll = () => {
      const titleSection = document.querySelector('.titleSection');
      if (titleSection) {
        if (window.scrollY > 50) {
          titleSection.classList.add('header-scrolled');
        } else {
          titleSection.classList.remove('header-scrolled');
        }
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);





  // Helper functions for easy understanding
  const getApplianceEquivalent = (watts: number): string => {
    if (language === 'ca') {
      if (watts >= 2000) return `${Math.round(watts/2000)} rentadores`;
      if (watts >= 1500) return `1 planxa + 1 TV`;
      if (watts >= 1000) return `1 microones + 1 nevera`;
      if (watts >= 500) return `2-3 TVs grans`;
      if (watts >= 200) return `4-5 bombetes LED`;
      if (watts >= 100) return `2-3 bombetes LED`;
      return `menys d'1 bombeta`;
    } else {
      if (watts >= 2000) return `${Math.round(watts/2000)} washing machines`;
      if (watts >= 1500) return `1 iron + 1 TV`;
      if (watts >= 1000) return `1 microwave + 1 fridge`;
      if (watts >= 500) return `2-3 large TVs`;
      if (watts >= 200) return `4-5 LED bulbs`;
      if (watts >= 100) return `2-3 LED bulbs`;
      return `less than 1 light bulb`;
    }
  };

  const getSavingsMessage = (): string => {
    if (!energyData) return '';
    const savings = Math.abs(energyData.gridPower);
    const dailySavings = (savings * 10) / 1000;
    
    if (language === 'ca') {
      if (energyData.gridPower < 0) {
        return `Estalvieu aproximadament ${dailySavings.toFixed(1)}€ avui`;
      } else {
        return `Gasteu aproximadament ${dailySavings.toFixed(1)}€ extra avui`;
      }
    } else {
      if (energyData.gridPower < 0) {
        return `Saving approximately €${dailySavings.toFixed(1)} today`;
      } else {
        return `Spending approximately €${dailySavings.toFixed(1)} extra today`;
      }
    }
  };

  const getWeatherAdvice = (): string => {
    if (weatherData) {
      if (weatherData.cloud_cover < 20) {
        return language === 'ca' ? '☀️ Dia perfecte per la energia solar!' : '☀️ Perfect day for solar energy!';
      } else if (weatherData.cloud_cover < 50) {
        return language === 'ca' ? '⛅ Bon dia per generar energia' : '⛅ Good day for energy generation';
      } else if (weatherData.cloud_cover < 80) {
        return language === 'ca' ? '☁️ Energia moderada dels panells' : '☁️ Moderate panel energy';
      } else {
        return language === 'ca' ? '🌧️ Poca generació solar avui' : '🌧️ Low solar generation today';
      }
    }
    
    // Fallback to scenario-based advice
    if (!energyData?.scenario) return '';
    const scenario = energyData.scenario;
    
    if (language === 'ca') {
      if (scenario === 0) return '☀️ Dia perfecte per la energia solar!';
      if (scenario === 1) return '⛅ Bon dia per generar energia';
      if (scenario === 2) return '☁️ Energia moderada dels panells';
      return '🌧️ Poca generació solar avui';
    } else {
      if (scenario === 0) return '☀️ Perfect day for solar energy!';
      if (scenario === 1) return '⛅ Good day for energy generation';
      if (scenario === 2) return '☁️ Moderate panel energy';
      return '🌧️ Low solar generation today';
    }
  };

  const getUsageTip = (): string => {
    if (weatherData && weatherData.solar_radiation > 600) {
      return language === 'ca' 
        ? '💡 Excel·lent radiació solar - moment perfecte per electrodomèstics'
        : '💡 Excellent solar radiation - perfect time for appliances';
    }
    
    if (weatherData && weatherData.cloud_cover > 70) {
      return language === 'ca'
        ? '☁️ Cel ennuvolat - reduïu el consum d\'alta potència'
        : '☁️ Cloudy sky - reduce high-power consumption';
    }
    
    // Fallback to energy-based tips
    if (!energyData) return '';
    const surplus = energyData.solarProduction - energyData.consumption;
    
    if (language === 'ca') {
      if (surplus > 1000) return '💡 Bon moment per posar la rentadora o planxar';
      if (surplus > 500) return '🔥 Podeu escalfar aigua o cuinar sense cost';
      if (surplus > 0) return '📱 Energia gratuïta per carregar dispositius';
      return '⚡ Intenteu reduir el consum ara';
    } else {
      if (surplus > 1000) return '💡 Great time to run washing machine or iron';
      if (surplus > 500) return '🔥 You can heat water or cook for free';
      if (surplus > 0) return '📱 Free energy to charge devices';
      return '⚡ Try to reduce consumption now';
    }
  };

  const openForecastModal = (day: any) => {
    setSelectedDay(day);
    setIsForecastModalOpen(true);
  };

  const closeForecastModal = () => {
    setIsForecastModalOpen(false);
    setSelectedDay(null);
  };

  const getCurrentScenario = (): string => {
    if (!energyData) return '';
    
    const solarToHome = Math.min(energyData.solarProduction, energyData.consumption);
    const solarToGrid = Math.max(0, energyData.solarProduction - energyData.consumption);
    const gridToHome = Math.max(0, energyData.consumption - energyData.solarProduction);
    
    if (language === 'ca') {
      if (energyData.solarProduction <= 50) {
        return '🔌 Usant 100% xarxa elèctrica';
      } else if (solarToGrid > 50 && gridToHome <= 50) {
        return '💰 Venent energia solar excedent';
      } else if (gridToHome > 50 && solarToHome > 50) {
        return '⚡ Combinant energia solar i xarxa';
      } else if (solarToHome > 50 && gridToHome <= 50) {
        return '☀️ Usant energia solar directa';
      }
      return '⚖️ Sistema equilibrat';
    } else {
      if (energyData.solarProduction <= 50) {
        return '🔌 Using 100% grid electricity';
      } else if (solarToGrid > 50 && gridToHome <= 50) {
        return '💰 Selling excess solar energy';
      } else if (gridToHome > 50 && solarToHome > 50) {
        return '⚡ Combining solar and grid energy';
      } else if (solarToHome > 50 && gridToHome <= 50) {
        return '☀️ Using direct solar energy';
      }
      return '⚖️ System balanced';
    }
  };

  // Determine scenario for background color (reuse logic from PowerFlowCardPlus)
  function getEnergyScenario(solarToHome: number, solarToGrid: number, gridToHome: number) {
    if (solarToGrid > 0 && solarToHome > 0 && gridToHome === 0) return 'selling'; // Green
    if (solarToGrid === 0 && solarToHome > 0 && gridToHome === 0) return 'solarOnly'; // Yellow
    if (solarToHome > 0 && gridToHome > 0) return 'mix'; // Orange
    if (solarToHome === 0 && gridToHome > 0) return 'gridOnly'; // Red
    return 'unknown';
  }

  // Calculate scenario from energyData (in W)
  let scenario = 'unknown';
  if (energyData) {
    const solarToHome = Math.max(Math.min(energyData.solarProduction, energyData.consumption), 0);
    const solarToGrid = Math.max(energyData.solarProduction - energyData.consumption, 0);
    const gridToHome = Math.max(energyData.consumption - energyData.solarProduction, 0);
    scenario = getEnergyScenario(solarToHome, solarToGrid, gridToHome);
  }

  const bgColor = energyData
    ? getFlowColor({ solar: energyData.solarProduction, home: energyData.consumption })
    : '#222'; // fallback

  return (
    <div
      className={styles.solarDashboard}
      style={{ backgroundColor: bgColor, transition: 'background-color 1.2s cubic-bezier(0.4,0,0.2,1)' }}
    >
      {/* Main Content Container */}
      <div className={styles.mainContent}>
        {/* Title Section with Controls and Weather */}
        <div className={styles.titleSection}>
          <div className={styles.titleRow}>
            {/* Left: Title */}
            <div className={styles.titleLeft}>
              <h1 className={styles.mainTitle}>
                {language === 'ca' ? '🌞 Bones avi!' : '🌞 Hey Grandad!'}
              </h1>
            </div>

            {/* Center: Weather Info */}
            <div className={styles.weatherCenter}>
              {weatherData ? (
                <div className={styles.weatherInfo}>
                  <div className={styles.weatherMain}>
                    <div className={styles.weatherIcon}>
                      {weatherData.cloud_cover < 20 ? '☀️' : 
                       weatherData.cloud_cover < 50 ? '⛅' : 
                       weatherData.cloud_cover < 80 ? '☁️' : '🌧️'}
                    </div>
                    <div className={styles.weatherTemp}>
                      {Math.round(weatherData.temperature)}°C
                    </div>
                    <div className={styles.weatherLocation}>
                      Agramunt
                    </div>
                  </div>
                  <div className={styles.weatherDetails}>
                    <div className={styles.weatherDetail}>
                      <span className={styles.detailIcon}>☁️</span>
                      <span className={styles.detailValue}>{weatherData.cloud_cover}%</span>
                    </div>
                    <div className={styles.weatherDetail}>
                      <span className={styles.detailIcon}>💧</span>
                      <span className={styles.detailValue}>{weatherData.humidity}%</span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className={styles.weatherInfo}>
                  <div className={styles.weatherMain}>
                    <div className={styles.weatherIcon}>🌤️</div>
                    <div className={styles.weatherTemp}>--°C</div>
                    <div className={styles.weatherLocation}>Agramunt</div>
                  </div>
                  <div className={styles.weatherDetails}>
                    <div className={styles.weatherDetail}>
                      <span className={styles.detailIcon}>☁️</span>
                      <span className={styles.detailValue}>--%</span>
                    </div>
                    <div className={styles.weatherDetail}>
                      <span className={styles.detailIcon}>💧</span>
                      <span className={styles.detailValue}>--%</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Right: Control Buttons */}
            <div className={styles.controlButtons}>
              <div className={styles.buttonGroup}>
                <button 
                  className={styles.controlButton}
                  onClick={() => setIsModalOpen(true)}
                  title={language === 'ca' ? 'Estat de connexió' : 'Connection status'}
                >
                  <span className={styles.buttonIcon}>🔌</span>
                </button>
                
                <button 
                  className={styles.controlButton}
                  onClick={() => setLanguage(language === 'ca' ? 'en' : 'ca')}
                  title={language === 'ca' ? 'Canviar idioma' : 'Change language'}
                >
                  <span className={styles.buttonIcon}>
                    {language === 'ca' ? '🇬🇧' : '🏴󠁥󠁳󠁣󠁴󠁿'}
                  </span>
                </button>
                <div className={styles.dropdownContainer}>
                <button 
                  className={styles.dropdownButton}
                  onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                  title={language === 'ca' ? 'Control manual' : 'Manual control'}
                >
                  <span className={styles.buttonIcon}>⚙️</span>
                </button>
                {isDropdownOpen && (
                  <div className={styles.dropdownMenu}>
                    <div className={styles.manualControlHeader}>
                      <h3>{language === 'ca' ? 'Control Manual' : 'Manual Control'}</h3>
                      <button 
                        className={styles.modeToggle}
                        onClick={() => setIsManualMode(!isManualMode)}
                      >
                        {isManualMode ? '🔄' : '🤖'} {language === 'ca' ? 'Mode Manual' : 'Manual Mode'}
                      </button>
                    </div>
                    
                    {isManualMode && (
                      <div className={styles.manualControls}>
                        {/* Solar Production Slider */}
                        <div className={styles.sliderGroup}>
                          <label className={styles.sliderLabel}>
                            ☀️ {language === 'ca' ? 'Producció Solar' : 'Solar Production'}
                          </label>
                          <div className={styles.sliderContainer}>
                            <input
                              type="range"
                              min="0"
                              max="2200"
                              value={manualSolarProduction}
                              onChange={(e) => setManualSolarProduction(Number(e.target.value))}
                              className={styles.slider}
                            />
                            <span className={styles.sliderValue}>{manualSolarProduction}W</span>
                          </div>
                        </div>

                        {/* Home Consumption Slider */}
                        <div className={styles.sliderGroup}>
                          <label className={styles.sliderLabel}>
                            🏠 {language === 'ca' ? 'Consum Casa' : 'Home Consumption'}
                          </label>
                          <div className={styles.sliderContainer}>
                            <input
                              type="range"
                              min="0"
                              max="5000"
                              value={manualHomeConsumption}
                              onChange={(e) => setManualHomeConsumption(Number(e.target.value))}
                              className={styles.slider}
                            />
                            <span className={styles.sliderValue}>{manualHomeConsumption}W</span>
                          </div>
                        </div>

                        {/* Current Status Display */}
                        <div className={styles.manualStatus}>
                          <div className={styles.statusItem}>
                            <span className={styles.statusLabel}>
                              {language === 'ca' ? 'Xarxa:' : 'Grid:'}
                            </span>
                            <span className={styles.statusValue}>
                              {manualHomeConsumption - manualSolarProduction > 0 
                                ? `+${manualHomeConsumption - manualSolarProduction}W` 
                                : `${manualHomeConsumption - manualSolarProduction}W`}
                            </span>
                          </div>
                          <div className={styles.statusItem}>
                            <span className={styles.statusLabel}>
                              {language === 'ca' ? 'Estalvi:' : 'Savings:'}
                            </span>
                            <span className={styles.statusValue}>
                              {manualHomeConsumption - manualSolarProduction < 0 
                                ? `€${Math.abs(manualHomeConsumption - manualSolarProduction) * 0.0003}/h` 
                                : '€0.00/h'}
                            </span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
              </div>
              

            </div>
          </div>
        </div>
        
        {/* 5-Day Solar Forecast - Moved to top */}
        {solarForecast.length > 0 && (
          <div className={styles.forecastSection}>
            <div className={styles.forecastGrid}>
              {solarForecast.slice(0, 6).map((day, index) => {
                // Calculate best day among all 6 days (including today)
                const allDays = solarForecast.slice(0, 6);
                const isBestDay = day.estimated_production_kwh === Math.max(...allDays.map(d => d.estimated_production_kwh));
                const productionPercentage = Math.round((day.estimated_production_kwh / 15) * 100); // Assuming 15kWh is max
                
                // Format time more user-friendly
                const formatTime = (hour: number) => {
                  const timeString = `${hour.toString().padStart(2, '0')}:00`;
                  return language === 'ca' ? `${timeString}h` : timeString;
                };
                
                // Format time range
                const formatTimeRange = (start: number, end: number) => {
                  return `${formatTime(start)} - ${formatTime(end)}`;
                };
                
                // Generate hourly production data (same as modal's generateHourlyData)
                const generateHourlyProductionData = (day: any) => {
                  const hourlyData = day.hourly_analysis?.hourly_data || [];
                  const productionData = [];
                  
                  for (let hour = 5; hour <= 23; hour++) {
                    const hourData = hourlyData.find((h: any) => h.hour === hour);
                    
                    if (hourData) {
                      // Use REAL weather data from API (same as modal)
                      const irradiance = hourData.irradiance || 0;
                      const cloudCover = hourData.cloudCover || 100;
                      const precipitation = hourData.precipitation || 0;
                      const temperature = hourData.temperature || 0;
                      const uvIndex = hourData.uvIndex || 0;
                      const weatherCode = hourData.weatherCode || 3;
                      
                      // Calculate production percentage based on irradiance (same as modal)
                      let production = Math.min((irradiance / 1000) * 100, 100);
                      
                      // Apply weather penalties (exactly same as modal)
                      let weatherPenalty = 1.0;
                      
                      // Cloud cover penalty (same as modal)
                      if (cloudCover > 80) weatherPenalty *= 0.3;
                      else if (cloudCover > 60) weatherPenalty *= 0.5;
                      else if (cloudCover > 40) weatherPenalty *= 0.7;
                      else if (cloudCover > 20) weatherPenalty *= 0.85;
                      
                      // Precipitation penalty (same as modal)
                      if (precipitation > 80) weatherPenalty *= 0.2;
                      else if (precipitation > 60) weatherPenalty *= 0.4;
                      else if (precipitation > 40) weatherPenalty *= 0.6;
                      else if (precipitation > 20) weatherPenalty *= 0.8;
                      
                      // Calculate final production (same as modal)
                      production = Math.round(production * weatherPenalty);
                      production = Math.min(100, Math.max(0, production));
                      
                      productionData.push({ hour, production });
                    } else {
                      // Fallback for hours without data (same as modal)
                      if (hour >= 6 && hour <= 20) {
                        productionData.push({ hour, production: 30 }); // Default moderate production
                      } else {
                        productionData.push({ hour, production: 0 }); // Night
                      }
                    }
                  }
                  
                  return productionData;
                };

                // Calculate the actual peak hour based on production data (same as modal)
                const getActualPeakHour = (day: any) => {
                  const productionData = generateHourlyProductionData(day);
                  if (productionData.length === 0) return day.peak_production_hour || 13;
                  
                  // Find the hour with the highest production (same as modal)
                  const peakHour = productionData.reduce((max: any, current: any) => {
                    return current.production > max.production ? current : max;
                  });
                  
                  return peakHour.hour;
                };

                // Calculate average production percentage for solar hours
                const getAverageProduction = (day: any) => {
                  const productionData = generateHourlyProductionData(day);
                  if (productionData.length === 0) return 0;
                  
                  let totalProduction = 0;
                  let solarHoursCount = 0;
                  
                  // Use the same production data as getActualPeakHour
                  productionData.forEach((hourData: any) => {
                    // Only count hours with solar production (6-20)
                    if (hourData.hour >= 6 && hourData.hour <= 20) {
                      totalProduction += hourData.production;
                      solarHoursCount++;
                    }
                  });
                  
                  return solarHoursCount > 0 ? Math.round(totalProduction / solarHoursCount) : 0;
                };

                // Generate 24-hour bar showing best/worst hours
                const generateHourlyBar = (day: any) => {
                  if (!day.hourly_analysis) return null;
                  
                                      const hours = [];
                    // Use same range as modal: 5h to 23h (19 hours total)
                  for (let hour = 5; hour <= 23; hour++) {
                    let color = '#1f2937'; // Darker gray for night
                    let production = 0;
                    let isNight = false;
                    
                    // Find hourly data for this specific hour
                    const hourData = day.hourly_analysis.hourly_data?.find((h: any) => h.hour === hour);
                    
                    if (hourData) {
                      // Use same calculation as modal
                      const irradiance = hourData.irradiance || 0;
                      const cloudCover = hourData.cloudCover || 100;
                      const precipitation = hourData.precipitation || 0;
                      
                      // Calculate production percentage based on irradiance
                      production = Math.min((irradiance / 1000) * 100, 100);
                      
                      // Apply weather penalties (same as modal)
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
                      
                      // Use same color logic as modal
                      if (production >= 75) {
                        color = '#fbbf24'; // Gold
                      } else if (production >= 60) {
                        color = '#22c55e'; // Green
                      } else if (production >= 30) {
                        color = '#facc15'; // Yellow
                      } else if (production > 0) {
                        color = '#f97316'; // Orange
                      } else {
                        color = '#ef4444'; // Red
                      }
                    } else {
                      // Fallback for hours without data
                      if (hour >= 6 && hour <= 20) {
                        color = '#f97316'; // Orange for unknown day hours
                      } else {
                        color = '#1f2937'; // Darker gray for night
                        isNight = true;
                      }
                    }
                    
                    // Check if it's night time (no solar production)
                    if (hour < 6 || hour > 20 || (hourData && hourData.irradiance === 0)) {
                      color = '#1f2937'; // Darker gray for night
                      isNight = true;
                    }
                    
                    hours.push(
                      <div 
                        key={hour}
                        className={styles.hourSegment}
                        style={{ backgroundColor: color }}
                        title={`${hour}:00 - ${isNight ? 'Nit' : `${production}%`}`}
                      />
                    );
                    

                  }
                  
                  return (
                    <div className={styles.hourlyBarWrapper}>
                      <div className={styles.hourlyBarWithLabels}>
                        <div className={styles.hourLabelLeft}>5h</div>
                        <div className={styles.hourlyBarContainer}>
                          {hours}
                        </div>
                        <div className={styles.hourLabelRight}>23h</div>
                      </div>
                    </div>
                  );
                };
                
                // Check if it's today or tomorrow
                const today = new Date().toDateString();
                const tomorrow = new Date();
                tomorrow.setDate(tomorrow.getDate() + 1);
                const tomorrowString = tomorrow.toDateString();
                const dayDate = new Date(day.date).toDateString();
                
                const isToday = dayDate === today;
                const isTomorrow = dayDate === tomorrowString;
                
                return (
                  <div 
                    key={index} 
                    className={`${styles.forecastCard} ${isBestDay ? styles.bestDay : ''}`}
                    onClick={() => openForecastModal(day)}
                    style={{ cursor: 'pointer' }}
                  >
                    <div className={styles.forecastDate}>
                      {new Date(day.date).toLocaleDateString(language === 'ca' ? 'ca-ES' : 'en-US', { 
                        weekday: 'short', 
                        month: 'short', 
                        day: 'numeric' 
                      })}
                    </div>
                    {(isToday || isTomorrow) && (
                      <div className={styles.dayTag}>
                        {isToday ? (language === 'ca' ? 'avui' : 'today') : (language === 'ca' ? 'demà' : 'tomorrow')}
                      </div>
                    )}

                    <div className={styles.forecastIcon}>
                      {day.weather_factor > 0.8 ? '☀️' : day.weather_factor > 0.6 ? '⛅' : day.weather_factor > 0.4 ? '☁️' : '🌧️'}
                    </div>
                    <div className={styles.forecastTime}>
                      {language === 'ca' ? 'Millor hora' : 'Best time'}: {formatTime(getActualPeakHour(day))}
                    </div>
                    <div className={styles.hourlyBar}>
                      {generateHourlyBar(day)}
                    </div>

                    {isBestDay && (
                      <div className={styles.bestDayBadge}>
                        {language === 'ca' ? '🌟 MILLOR DIA' : '🌟 BEST DAY'}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Main Energy Dashboard Row - 50% Flow, 50% Tips */}
        <div className={styles.mainDashboardContainer}>
          <div className={styles.mainDashboardRow}>
            {/* Energy Flow Diagram - 50% */}
            <div className={styles.energyFlowSection}>
              {energyData && (
                <div className={styles.energyFlowCard}>
                  <h3 className={styles.energyFlowTitle}>
                    {language === 'ca' ? 'BALANÇ D\'ENERGIA' : 'ENERGY BALANCE'}
                  </h3>
                  
                  <PowerFlowCardPlus 
                    energyData={{
                      solarProduction: energyData.solarProduction / 1000, // Convert W to kW
                      homeConsumption: energyData.consumption / 1000,     // Convert W to kW
                      gridImport: energyData.gridPower / 1000             // Convert W to kW (positive = importing, negative = exporting)
                    }}
                    language={language === 'ca' ? 'cat' : 'en'}
                  />

                  {/* Energy Balance Status */}
                  <div className={styles.energyStatus}>
                    <div className={styles.statusCard}>
                      {energyData.gridPower > 100 ? (
                        <>
                          <div className={styles.statusIcon}>🔋</div>
                          <div className={styles.statusInfo}>
                            <div className={styles.statusText}>
                              {language === 'ca' ? 'Comprant energia' : 'Buying energy'}
                            </div>
                            <div className={styles.statusSubtext}>
                              {language === 'ca' ? 'Solar insuficient' : 'Solar insufficient'}
                            </div>
                          </div>
                          <div className={styles.statusValue}>
                            -{(Math.abs(energyData.gridPower) * 0.25 / 1000).toFixed(2)}€/h
                          </div>
                        </>
                      ) : energyData.gridPower < -100 ? (
                        <>
                          <div className={styles.statusIcon}>💰</div>
                          <div className={styles.statusInfo}>
                            <div className={styles.statusText}>
                              {language === 'ca' ? 'Venent energia' : 'Selling energy'}
                            </div>
                            <div className={styles.statusSubtext}>
                              {language === 'ca' ? 'Excedent solar' : 'Solar surplus'}
                            </div>
                          </div>
                          <div className={styles.statusValue}>
                            +{(Math.abs(energyData.gridPower) * 0.15 / 1000).toFixed(2)}€/h
                          </div>
                        </>
                      ) : (
                        <>
                          <div className={styles.statusIcon}>⚖️</div>
                          <div className={styles.statusInfo}>
                            <div className={styles.statusText}>
                              {language === 'ca' ? 'Equilibrat' : 'Balanced'}
                            </div>
                            <div className={styles.statusSubtext}>
                              {language === 'ca' ? 'Consum = Producció' : 'Consumption = Production'}
                            </div>
                          </div>
                          <div className={styles.statusValue}>
                            0.00€/h
                          </div>
                        </>
                      )}
                    </div>
                    
                    <div className={styles.efficiencyCard}>
                      <div className={styles.efficiencyInfo}>
                        <div className={styles.efficiencyLabel}>
                          {language === 'ca' ? 'Producció solar' : 'Solar production'}
                        </div>
                        <div className={styles.efficiencyValue}>
                          {Math.round((energyData.solarProduction / 2200) * 100)}% 
                          <span className={styles.efficiencyMax}>/ 2.2kW</span>
                        </div>
                      </div>
                      <div className={styles.efficiencyBar}>
                        <div 
                          className={styles.efficiencyFill}
                          style={{ 
                            width: `${Math.min(100, (energyData.solarProduction / 2200) * 100)}%` 
                          }}
                        ></div>
                      </div>
                      <div className={styles.weatherHint}>
                        {energyData.scenario !== undefined && (
                          <span>
                            {energyData.scenario === 0 
                              ? (language === 'ca' ? '☀️ Dia excel·lent' : '☀️ Excellent day')
                              : energyData.scenario === 1 
                              ? (language === 'ca' ? '⛅ Dia bo' : '⛅ Good day')
                              : (language === 'ca' ? '☁️ Dia ennuvolat' : '☁️ Cloudy day')
                            }
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Smart Tips - 40% */}
            <div className={styles.smartTipsSection}>
              <SmartTipsCard
                tips={smartTips}
                language={language}
              />
            </div>
          </div>
        </div>



      </div> {/* Close mainContent */}

      {/* Footer with update info */}
      <div className={styles.footer}>
        <div className={styles.updateInfo}>
          <span>
            {language === 'ca' ? 'Última actualització' : 'Last update'}: {lastUpdate}
          </span>
          <span className={styles.location}>📍 Agramunt, Lleida</span>
          <span className={styles.dataSource}>
            {isActuallyConnected()
              ? (language === 'ca' ? 'Dades: Fronius Real' : 'Data: Real Fronius')
              : (language === 'ca' ? 'Dades: Demo Simulades' : 'Data: Demo Simulated')
            } | {energyData?.scenario} | 
            {language === 'ca' ? 'Canvia cada 10min' : 'Changes every 10min'}
          </span>
        </div>
      </div>

      {/* Connection Modal */}
      <ConnectionModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        froniusStatus={froniusStatus}
        isCheckingConnection={isCheckingConnection}
        onForceReconnect={forceReconnect}
        language={language}
      />

      {/* Forecast Modal */}
              <ForecastModal
          isOpen={isForecastModalOpen}
          onClose={closeForecastModal}
          day={selectedDay}
          language={language}
          forecastData={solarForecast}
        />
    </div>
  );
}
