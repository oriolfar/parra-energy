export interface SmartTip {
  type: 'weather' | 'opportunity' | 'timing' | 'optimization' | 'maintenance' | 'seasonal' | 'emergency' | 'efficiency';
  priority: 'high' | 'medium' | 'low';
  icon: string;
  title: string;
  message: string;
  action: string;
  conditions?: {
    solarProduction?: { min?: number; max?: number };
    cloudCover?: { min?: number; max?: number };
    temperature?: { min?: number; max?: number };
    timeOfDay?: { start?: number; end?: number };
    dayOfWeek?: number[];
    season?: string[];
    weatherCondition?: string[];
  };
}

export const TIPS_LIBRARY: SmartTip[] = [
  // ===== CURRENT PRODUCTION BASED TIPS =====
  {
    type: 'opportunity',
    priority: 'high',
    icon: '🧺',
    title: 'Perfect Time for Laundry!',
    message: 'Panels working at maximum capacity. Start washing machine now for 100% free energy.',
    action: 'Start washing machine immediately',
    conditions: { solarProduction: { min: 2000 } }
  },
  {
    type: 'opportunity',
    priority: 'high',
    icon: '🍽️',
    title: 'Dishwasher Time!',
    message: 'High solar production detected. Perfect time to run dishwasher.',
    action: 'Start dishwasher now',
    conditions: { solarProduction: { min: 1800 } }
  },
  {
    type: 'opportunity',
    priority: 'medium',
    icon: '🔋',
    title: 'Charge Everything!',
    message: 'Good solar production. Charge phones, tablets, and laptops.',
    action: 'Plug in all devices',
    conditions: { solarProduction: { min: 1200, max: 1799 } }
  },
  {
    type: 'opportunity',
    priority: 'medium',
    icon: '🌡️',
    title: 'Air Conditioning OK',
    message: 'Sufficient solar power for air conditioning without grid dependency.',
    action: 'Use AC comfortably',
    conditions: { solarProduction: { min: 1500 } }
  },
  {
    type: 'opportunity',
    priority: 'low',
    icon: '💡',
    title: 'LED Lighting Only',
    message: 'Low solar production. Use only LED lights to minimize grid usage.',
    action: 'Switch to LED lights only',
    conditions: { solarProduction: { min: 200, max: 599 } }
  },
  {
    type: 'emergency',
    priority: 'high',
    icon: '⚡',
    title: 'No Solar Production!',
    message: 'Panels not generating power. Avoid high-power appliances.',
    action: 'Use only essential devices',
    conditions: { solarProduction: { max: 50 } }
  },

  // ===== WEATHER-BASED TIPS =====
  {
    type: 'weather',
    priority: 'high',
    icon: '☀️',
    title: 'Perfect Sunny Day!',
    message: 'Clear skies detected. Maximum solar efficiency expected.',
    action: 'Use all high-power appliances',
    conditions: { cloudCover: { max: 10 } }
  },
  {
    type: 'weather',
    priority: 'medium',
    icon: '⛅',
    title: 'Partly Cloudy - Good Production',
    message: 'Light cloud cover. Solar panels still working efficiently.',
    action: 'Use medium-power appliances',
    conditions: { cloudCover: { min: 11, max: 30 } }
  },
  {
    type: 'weather',
    priority: 'medium',
    icon: '☁️',
    title: 'Cloudy Day - Reduced Production',
    message: 'Heavy cloud cover detected. Solar production will be lower.',
    action: 'Use only essential appliances',
    conditions: { cloudCover: { min: 31, max: 70 } }
  },
  {
    type: 'weather',
    priority: 'high',
    icon: '🌧️',
    title: 'Rain Expected - Low Production',
    message: 'Rainy weather will significantly reduce solar production.',
    action: 'Postpone non-essential appliances',
    conditions: { weatherCondition: ['rain', 'storm'] }
  },
  {
    type: 'weather',
    priority: 'low',
    icon: '❄️',
    title: 'Cold Weather - Check Panels',
    message: 'Cold temperatures can affect panel efficiency. Monitor production.',
    action: 'Check panel performance',
    conditions: { temperature: { max: 5 } }
  },
  {
    type: 'weather',
    priority: 'medium',
    icon: '🌡️',
    title: 'Hot Weather - Monitor Efficiency',
    message: 'High temperatures may reduce panel efficiency slightly.',
    action: 'Monitor production levels',
    conditions: { temperature: { min: 35 } }
  },

  // ===== TIME-BASED TIPS =====
  {
    type: 'timing',
    priority: 'high',
    icon: '🌅',
    title: 'Early Morning - Low Production',
    message: 'Sunrise hours. Solar production just starting.',
    action: 'Wait for peak hours',
    conditions: { timeOfDay: { start: 6, end: 9 } }
  },
  {
    type: 'timing',
    priority: 'high',
    icon: '☀️',
    title: 'Peak Solar Hours!',
    message: 'Maximum solar production period. Use all appliances.',
    action: 'Start high-power appliances now',
    conditions: { timeOfDay: { start: 10, end: 16 } }
  },
  {
    type: 'timing',
    priority: 'medium',
    icon: '🌇',
    title: 'Late Afternoon - Declining Production',
    message: 'Solar production decreasing. Use remaining power wisely.',
    action: 'Finish appliance cycles',
    conditions: { timeOfDay: { start: 16, end: 19 } }
  },
  {
    type: 'timing',
    priority: 'high',
    icon: '🌙',
    title: 'Night Hours - No Solar',
    message: 'No solar production. Use grid power sparingly.',
    action: 'Use only essential devices',
    conditions: { timeOfDay: { start: 20, end: 6 } }
  },
  {
    type: 'timing',
    priority: 'medium',
    icon: '⏰',
    title: 'Weekend - Extended Usage',
    message: 'Weekend allows for flexible appliance scheduling.',
    action: 'Plan appliance usage around peak hours',
    conditions: { dayOfWeek: [0, 6] }
  },

  // ===== APPLIANCE-SPECIFIC TIPS =====
  {
    type: 'optimization',
    priority: 'high',
    icon: '🧺',
    title: 'Washing Machine - Cold Water',
    message: 'Use cold water settings to reduce energy consumption.',
    action: 'Set washing machine to cold water',
    conditions: { solarProduction: { min: 1000 } }
  },
  {
    type: 'optimization',
    priority: 'medium',
    icon: '🍽️',
    title: 'Dishwasher - Eco Mode',
    message: 'Use eco mode for longer cycles but lower energy usage.',
    action: 'Select eco mode on dishwasher',
    conditions: { solarProduction: { min: 800 } }
  },
  {
    type: 'optimization',
    priority: 'low',
    icon: '🌡️',
    title: 'Water Heater - Solar Priority',
    message: 'Heat water during peak solar hours for maximum efficiency.',
    action: 'Schedule water heating for peak hours',
    conditions: { timeOfDay: { start: 11, end: 15 } }
  },
  {
    type: 'optimization',
    priority: 'medium',
    icon: '❄️',
    title: 'Refrigerator - Optimal Settings',
    message: 'Keep refrigerator at optimal temperature to reduce energy waste.',
    action: 'Check refrigerator temperature settings',
    conditions: { solarProduction: { min: 500 } }
  },
  {
    type: 'optimization',
    priority: 'low',
    icon: '💻',
    title: 'Computer - Battery Mode',
    message: 'Use laptop battery mode during low solar production.',
    action: 'Switch to battery mode',
    conditions: { solarProduction: { max: 300 } }
  },

  // ===== MAINTENANCE TIPS =====
  {
    type: 'maintenance',
    priority: 'medium',
    icon: '🧹',
    title: 'Clean Solar Panels',
    message: 'Dirty panels reduce efficiency. Clean them for better production.',
    action: 'Schedule panel cleaning',
    conditions: { solarProduction: { max: 1500 } }
  },
  {
    type: 'maintenance',
    priority: 'low',
    icon: '🔍',
    title: 'Check Panel Connections',
    message: 'Regular inspection of panel connections ensures optimal performance.',
    action: 'Inspect panel connections',
    conditions: { solarProduction: { max: 1000 } }
  },
  {
    type: 'maintenance',
    priority: 'medium',
    icon: '📊',
    title: 'Monitor Production Trends',
    message: 'Track daily production to identify performance issues.',
    action: 'Review production data',
    conditions: { solarProduction: { max: 1200 } }
  },
  {
    type: 'maintenance',
    priority: 'low',
    icon: '🌱',
    title: 'Trim Nearby Trees',
    message: 'Overhanging branches can shade panels and reduce production.',
    action: 'Check for tree shading',
    conditions: { solarProduction: { max: 800 } }
  },

  // ===== SEASONAL TIPS =====
  {
    type: 'seasonal',
    priority: 'high',
    icon: '🌞',
    title: 'Summer Peak Season',
    message: 'Summer provides maximum solar production. Use appliances freely.',
    action: 'Maximize appliance usage',
    conditions: { season: ['summer'] }
  },
  {
    type: 'seasonal',
    priority: 'medium',
    icon: '🍂',
    title: 'Autumn - Declining Production',
    message: 'Shorter days mean less solar production. Plan usage carefully.',
    action: 'Optimize appliance timing',
    conditions: { season: ['autumn'] }
  },
  {
    type: 'seasonal',
    priority: 'high',
    icon: '❄️',
    title: 'Winter - Minimal Production',
    message: 'Winter provides minimal solar production. Use grid power efficiently.',
    action: 'Minimize appliance usage',
    conditions: { season: ['winter'] }
  },
  {
    type: 'seasonal',
    priority: 'medium',
    icon: '🌸',
    title: 'Spring - Increasing Production',
    message: 'Spring brings increasing solar production. Gradually increase usage.',
    action: 'Start using more appliances',
    conditions: { season: ['spring'] }
  },

  // ===== EFFICIENCY TIPS =====
  {
    type: 'efficiency',
    priority: 'high',
    icon: '⚡',
    title: 'Peak Hour Optimization',
    message: 'Use high-power appliances during peak solar hours for maximum efficiency.',
    action: 'Schedule appliances for peak hours',
    conditions: { timeOfDay: { start: 11, end: 15 } }
  },
  {
    type: 'efficiency',
    priority: 'medium',
    icon: '🔋',
    title: 'Battery Storage Opportunity',
    message: 'Consider storing excess solar energy in batteries for later use.',
    action: 'Research battery storage options',
    conditions: { solarProduction: { min: 2000 } }
  },
  {
    type: 'efficiency',
    priority: 'low',
    icon: '💡',
    title: 'LED Lighting Upgrade',
    message: 'Replace old bulbs with LED lights to reduce overall energy consumption.',
    action: 'Upgrade to LED lighting',
    conditions: { solarProduction: { max: 1000 } }
  },
  {
    type: 'efficiency',
    priority: 'medium',
    icon: '🌡️',
    title: 'Smart Thermostat',
    message: 'Use smart thermostat to optimize heating/cooling with solar production.',
    action: 'Install smart thermostat',
    conditions: { solarProduction: { min: 1500 } }
  },

  // ===== EMERGENCY TIPS =====
  {
    type: 'emergency',
    priority: 'high',
    icon: '🚨',
    title: 'Grid Outage - Solar Available',
    message: 'Grid power down but solar panels working. Use solar power carefully.',
    action: 'Use only essential devices',
    conditions: { solarProduction: { min: 500 } }
  },
  {
    type: 'emergency',
    priority: 'high',
    icon: '⚡',
    title: 'System Error Detected',
    message: 'Solar system showing errors. Contact technician for inspection.',
    action: 'Contact solar technician',
    conditions: { solarProduction: { max: 100 } }
  },
  {
    type: 'emergency',
    priority: 'medium',
    icon: '🌪️',
    title: 'Storm Warning',
    message: 'Severe weather approaching. Secure outdoor equipment.',
    action: 'Secure solar equipment',
    conditions: { weatherCondition: ['storm', 'hurricane'] }
  },

  // ===== ADVANCED OPTIMIZATION TIPS =====
  {
    type: 'optimization',
    priority: 'medium',
    icon: '📱',
    title: 'Smart Home Integration',
    message: 'Connect appliances to smart home system for automated solar optimization.',
    action: 'Set up smart home automation',
    conditions: { solarProduction: { min: 1000 } }
  },
  {
    type: 'optimization',
    priority: 'low',
    icon: '🌍',
    title: 'Carbon Footprint Tracking',
    message: 'Monitor your carbon footprint reduction through solar usage.',
    action: 'Track environmental impact',
    conditions: { solarProduction: { min: 500 } }
  },
  {
    type: 'optimization',
    priority: 'medium',
    icon: '💰',
    title: 'Energy Bill Savings',
    message: 'Calculate your monthly savings from solar panel usage.',
    action: 'Review energy bill savings',
    conditions: { solarProduction: { min: 800 } }
  },

  // ===== EDUCATIONAL TIPS =====
  {
    type: 'optimization',
    priority: 'low',
    icon: '📚',
    title: 'Solar Education',
    message: 'Learn more about solar energy to maximize your system benefits.',
    action: 'Read solar energy guides',
    conditions: { solarProduction: { min: 200 } }
  },
  {
    type: 'optimization',
    priority: 'low',
    icon: '🔧',
    title: 'DIY Maintenance',
    message: 'Learn basic solar panel maintenance to keep your system optimal.',
    action: 'Learn maintenance basics',
    conditions: { solarProduction: { min: 300 } }
  },

  // ===== FUTURE PLANNING TIPS =====
  {
    type: 'timing',
    priority: 'medium',
    icon: '📅',
    title: 'Weekly Usage Planning',
    message: 'Plan your weekly appliance usage around solar production forecasts.',
    action: 'Create weekly usage plan',
    conditions: { solarProduction: { min: 500 } }
  },
  {
    type: 'timing',
    priority: 'low',
    icon: '🎯',
    title: 'Monthly Goals',
    message: 'Set monthly energy independence goals to maximize solar benefits.',
    action: 'Set monthly energy goals',
    conditions: { solarProduction: { min: 400 } }
  },

  // ===== WEATHER FORECAST TIPS =====
  {
    type: 'weather',
    priority: 'high',
    icon: '🌤️',
    title: 'Tomorrow - Perfect Solar Day',
    message: 'Tomorrow forecast shows excellent solar conditions. Plan heavy usage.',
    action: 'Schedule heavy appliances for tomorrow',
    conditions: { cloudCover: { max: 10 } }
  },
  {
    type: 'weather',
    priority: 'medium',
    icon: '🌧️',
    title: 'Tomorrow - Rain Expected',
    message: 'Tomorrow forecast shows rain. Reduce appliance usage plans.',
    action: 'Use appliances today instead',
    conditions: { weatherCondition: ['rain'] }
  },
  {
    type: 'weather',
    priority: 'low',
    icon: '🌫️',
    title: 'Foggy Conditions',
    message: 'Fog can reduce solar panel efficiency temporarily.',
    action: 'Wait for fog to clear',
    conditions: { weatherCondition: ['fog'] }
  },

  // ===== TIME-SENSITIVE TIPS =====
  {
    type: 'timing',
    priority: 'high',
    icon: '⏰',
    title: 'Peak Hour Starting',
    message: 'Peak solar hours beginning. Prepare high-power appliances.',
    action: 'Get appliances ready',
    conditions: { timeOfDay: { start: 10, end: 11 } }
  },
  {
    type: 'timing',
    priority: 'medium',
    icon: '⏰',
    title: 'Peak Hour Ending',
    message: 'Peak solar hours ending. Finish appliance cycles.',
    action: 'Complete appliance cycles',
    conditions: { timeOfDay: { start: 15, end: 16 } }
  },

  // ===== PRODUCTION MONITORING TIPS =====
  {
    type: 'efficiency',
    priority: 'medium',
    icon: '📊',
    title: 'Production Below Average',
    message: 'Today\'s production is below average. Check for issues.',
    action: 'Investigate production issues',
    conditions: { solarProduction: { max: 1000 } }
  },
  {
    type: 'efficiency',
    priority: 'high',
    icon: '📈',
    title: 'Production Above Average',
    message: 'Excellent production today! Use appliances freely.',
    action: 'Maximize appliance usage',
    conditions: { solarProduction: { min: 2000 } }
  },

  // ===== COST SAVINGS TIPS =====
  {
    type: 'optimization',
    priority: 'high',
    icon: '💵',
    title: 'Maximum Savings Mode',
    message: 'Current conditions perfect for maximum energy bill savings.',
    action: 'Use all available appliances',
    conditions: { solarProduction: { min: 1800 } }
  },
  {
    type: 'optimization',
    priority: 'medium',
    icon: '💰',
    title: 'Moderate Savings',
    message: 'Good conditions for energy savings. Use appliances wisely.',
    action: 'Use medium-power appliances',
    conditions: { solarProduction: { min: 1000, max: 1799 } }
  },

  // ===== ENVIRONMENTAL TIPS =====
  {
    type: 'optimization',
    priority: 'low',
    icon: '🌱',
    title: 'Carbon Neutral Day',
    message: 'Your solar usage today is carbon neutral. Great for the environment!',
    action: 'Continue solar usage',
    conditions: { solarProduction: { min: 1500 } }
  },
  {
    type: 'optimization',
    priority: 'low',
    icon: '🌍',
    title: 'Environmental Impact',
    message: 'Every hour of solar usage reduces your carbon footprint.',
    action: 'Track environmental benefits',
    conditions: { solarProduction: { min: 500 } }
  },

  // ===== SYSTEM HEALTH TIPS =====
  {
    type: 'maintenance',
    priority: 'high',
    icon: '🏥',
    title: 'System Health Check',
    message: 'Regular system health monitoring ensures optimal performance.',
    action: 'Run system diagnostics',
    conditions: { solarProduction: { max: 1200 } }
  },
  {
    type: 'maintenance',
    priority: 'medium',
    icon: '🔧',
    title: 'Preventive Maintenance',
    message: 'Schedule preventive maintenance to avoid future issues.',
    action: 'Book maintenance appointment',
    conditions: { solarProduction: { max: 1500 } }
  },

  // ===== USER BEHAVIOR TIPS =====
  {
    type: 'optimization',
    priority: 'medium',
    icon: '👥',
    title: 'Family Usage Coordination',
    message: 'Coordinate family appliance usage to maximize solar benefits.',
    action: 'Plan family usage schedule',
    conditions: { solarProduction: { min: 1000 } }
  },
  {
    type: 'optimization',
    priority: 'low',
    icon: '📱',
    title: 'App Notifications',
    message: 'Enable app notifications for optimal solar usage timing.',
    action: 'Enable solar notifications',
    conditions: { solarProduction: { min: 300 } }
  },

  // ===== TECHNICAL TIPS =====
  {
    type: 'efficiency',
    priority: 'medium',
    icon: '⚙️',
    title: 'Inverter Optimization',
    message: 'Check inverter settings for optimal solar panel performance.',
    action: 'Review inverter settings',
    conditions: { solarProduction: { max: 1400 } }
  },
  {
    type: 'efficiency',
    priority: 'low',
    icon: '🔌',
    title: 'Connection Check',
    message: 'Verify all electrical connections for maximum efficiency.',
    action: 'Check electrical connections',
    conditions: { solarProduction: { max: 1000 } }
  },

  // ===== LIFESTYLE TIPS =====
  {
    type: 'optimization',
    priority: 'low',
    icon: '🏠',
    title: 'Home Energy Audit',
    message: 'Consider a home energy audit to identify additional savings opportunities.',
    action: 'Schedule energy audit',
    conditions: { solarProduction: { min: 800 } }
  },
  {
    type: 'optimization',
    priority: 'low',
    icon: '🌿',
    title: 'Green Lifestyle',
    message: 'Combine solar usage with other green lifestyle choices.',
    action: 'Explore green living options',
    conditions: { solarProduction: { min: 500 } }
  }
];

// Helper function to filter tips based on current conditions
export const filterTipsByConditions = (
  tips: SmartTip[],
  conditions: {
    solarProduction?: number;
    cloudCover?: number;
    temperature?: number;
    timeOfDay?: number;
    dayOfWeek?: number;
    season?: string;
    weatherCondition?: string;
  }
): SmartTip[] => {
  return tips.filter(tip => {
    if (!tip.conditions) return true;

    const { conditions: tipConditions } = tip;

    // Check solar production
    if (tipConditions.solarProduction && conditions.solarProduction !== undefined) {
      const { min, max } = tipConditions.solarProduction;
      if (min && conditions.solarProduction < min) return false;
      if (max && conditions.solarProduction > max) return false;
    }

    // Check cloud cover
    if (tipConditions.cloudCover && conditions.cloudCover !== undefined) {
      const { min, max } = tipConditions.cloudCover;
      if (min && conditions.cloudCover < min) return false;
      if (max && conditions.cloudCover > max) return false;
    }

    // Check temperature
    if (tipConditions.temperature && conditions.temperature !== undefined) {
      const { min, max } = tipConditions.temperature;
      if (min && conditions.temperature < min) return false;
      if (max && conditions.temperature > max) return false;
    }

    // Check time of day
    if (tipConditions.timeOfDay && conditions.timeOfDay !== undefined) {
      const { start, end } = tipConditions.timeOfDay;
      if (start && conditions.timeOfDay < start) return false;
      if (end && conditions.timeOfDay > end) return false;
    }

    // Check day of week
    if (tipConditions.dayOfWeek && conditions.dayOfWeek !== undefined) {
      if (!tipConditions.dayOfWeek.includes(conditions.dayOfWeek)) return false;
    }

    // Check season
    if (tipConditions.season && conditions.season) {
      if (!tipConditions.season.includes(conditions.season)) return false;
    }

    // Check weather condition
    if (tipConditions.weatherCondition && conditions.weatherCondition) {
      if (!tipConditions.weatherCondition.includes(conditions.weatherCondition)) return false;
    }

    return true;
  });
};

// Helper function to get current season
export const getCurrentSeason = (): string => {
  const month = new Date().getMonth();
  if (month >= 2 && month <= 4) return 'spring';
  if (month >= 5 && month <= 7) return 'summer';
  if (month >= 8 && month <= 10) return 'autumn';
  return 'winter';
};

// Helper function to get weather condition from description
export const getWeatherCondition = (description: string): string => {
  const desc = description.toLowerCase();
  if (desc.includes('rain') || desc.includes('drizzle')) return 'rain';
  if (desc.includes('storm') || desc.includes('thunder')) return 'storm';
  if (desc.includes('snow')) return 'snow';
  if (desc.includes('fog') || desc.includes('mist')) return 'fog';
  if (desc.includes('cloud')) return 'cloudy';
  if (desc.includes('clear') || desc.includes('sunny')) return 'clear';
  return 'unknown';
}; 