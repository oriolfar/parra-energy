/**
 * Enhanced Mock Fronius Client - Sophisticated Solar Simulation
 * =============================================================
 * 
 * Advanced mock client that simulates realistic solar production using
 * real weather data and sophisticated consumption patterns.
 * Based on the Python enhanced mock implementation.
 */

import type { PowerData, WeatherData, ElderlyAdvice } from '@repo/types';

export class EnhancedMockFroniusClient {
  private solarCapacityWatts: number;
  private location: string;
  private manualOverrides: {
    solarPercentage?: number;
    consumptionWatts?: number;
  } = {};

  constructor(solarCapacityWatts: number = 2200, location: string = 'Agramunt, Spain') {
    this.solarCapacityWatts = solarCapacityWatts;
    this.location = location;
  }

  /**
   * Always returns true for mock client
   */
  async testConnection(): Promise<boolean> {
    return true;
  }

  /**
   * Generate realistic solar production based on time and weather
   */
  private calculateSolarProduction(weather?: WeatherData): number {
    const now = new Date();
    const hour = now.getHours();
    const minute = now.getMinutes();
    const timeDecimal = hour + minute / 60;

    // Manual override takes precedence
    if (this.manualOverrides.solarPercentage !== undefined) {
      return (this.solarCapacityWatts * this.manualOverrides.solarPercentage) / 100;
    }

    // Solar production curve: 7 AM to 7 PM
    if (timeDecimal < 7 || timeDecimal > 19) {
      return 0; // No solar production at night
    }

    // Bell curve for solar production throughout the day
    const midday = 13; // Peak solar at 1 PM
    const span = 6; // 6 hours on each side
    const normalizedTime = (timeDecimal - midday) / span;
    let baseProduction = Math.exp(-0.5 * normalizedTime * normalizedTime);

    // Apply seasonal variation (Spain has good sun year-round)
    const month = now.getMonth() + 1;
    const seasonalFactor = this.getSeasonalFactor(month);
    baseProduction *= seasonalFactor;

    // Apply weather conditions if available
    if (weather) {
      const weatherFactor = this.getWeatherFactor(weather);
      baseProduction *= weatherFactor;
    } else {
      // Default weather factor for clear day
      baseProduction *= 0.85;
    }

    // Add some realistic variation (±5%)
    const variation = 1 + (Math.random() - 0.5) * 0.1;
    baseProduction *= variation;

    return Math.max(0, baseProduction * this.solarCapacityWatts);
  }

  /**
   * Get seasonal production factor for Spain
   */
  private getSeasonalFactor(month: number): number {
    const seasonalFactors = {
      1: 0.60,  // January - winter
      2: 0.70,  // February
      3: 0.80,  // March - spring starts
      4: 0.90,  // April
      5: 0.95,  // May
      6: 1.00,  // June - peak summer
      7: 1.00,  // July - peak summer
      8: 0.95,  // August
      9: 0.85,  // September
      10: 0.75, // October
      11: 0.65, // November
      12: 0.55  // December - winter
    };
    return seasonalFactors[month as keyof typeof seasonalFactors] || 0.8;
  }

  /**
   * Calculate weather impact on solar production
   */
  private getWeatherFactor(weather: WeatherData): number {
    // Cloud cover impact (0-100%)
    const cloudFactor = 1 - (weather.cloud_cover / 100) * 0.7;
    
    // UV index impact (0-12)
    const uvFactor = Math.min(weather.uv_index / 8, 1);
    
    // Temperature impact (panels lose efficiency when too hot)
    let tempFactor = 1;
    if (weather.temperature > 25) {
      tempFactor = 1 - ((weather.temperature - 25) * 0.004); // -0.4% per degree above 25°C
    }
    
    // Precipitation impact
    const precipitationFactor = weather.precipitation > 0 ? 0.3 : 1;
    
    return cloudFactor * uvFactor * tempFactor * precipitationFactor;
  }

  /**
   * Generate realistic household consumption patterns
   */
  private calculateHouseholdConsumption(): number {
    const now = new Date();
    const hour = now.getHours();
    const dayOfWeek = now.getDay(); // 0 = Sunday, 6 = Saturday
    
    // Manual override takes precedence
    if (this.manualOverrides.consumptionWatts !== undefined) {
      return this.manualOverrides.consumptionWatts;
    }

    // Base load (always-on devices)
    let baseLoad = 300; // Fridge, router, standby devices
    
    // Time-based consumption patterns
    let timeMultiplier = 1;
    
    if (hour >= 6 && hour < 10) {
      // Morning routine: 6-10 AM
      timeMultiplier = 1.8; // Breakfast, showers, etc.
    } else if (hour >= 12 && hour < 14) {
      // Lunch time: 12-14 PM
      timeMultiplier = 2.2; // Cooking lunch
    } else if (hour >= 17 && hour < 21) {
      // Evening peak: 17-21 PM
      timeMultiplier = 2.5; // Dinner, TV, lighting
    } else if (hour >= 21 || hour < 6) {
      // Night rest: 21-6 AM
      timeMultiplier = 0.6; // Minimal consumption
    }
    
    // Weekend factor (slightly higher consumption)
    if (dayOfWeek === 0 || dayOfWeek === 6) {
      timeMultiplier *= 1.1;
    }
    
    // Add some realistic variation (±10%)
    const variation = 1 + (Math.random() - 0.5) * 0.2;
    
    return Math.max(baseLoad, baseLoad * timeMultiplier * variation);
  }

  /**
   * Get current power data with realistic simulation
   */
  async getCurrentData(weather?: WeatherData): Promise<PowerData> {
    const production = this.calculateSolarProduction(weather);
    const consumption = this.calculateHouseholdConsumption();
    const gridPower = consumption - production; // Positive = import, negative = export

    return {
      P_PV: Math.round(production),
      P_Load: Math.round(consumption),
      P_Grid: Math.round(gridPower),
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Set manual override for solar production (0-100%)
   */
  setSolarOverride(percentage: number): void {
    this.manualOverrides.solarPercentage = Math.max(0, Math.min(100, percentage));
  }

  /**
   * Set manual override for consumption (watts)
   */
  setConsumptionOverride(watts: number): void {
    this.manualOverrides.consumptionWatts = Math.max(0, watts);
  }

  /**
   * Clear all manual overrides
   */
  clearOverrides(): void {
    this.manualOverrides = {};
  }

  /**
   * Get current overrides status
   */
  getOverrides(): typeof this.manualOverrides {
    return { ...this.manualOverrides };
  }

  /**
   * Generate elderly-friendly advice in Catalan
   */
  generateElderlyAdvice(currentData: PowerData, weather?: WeatherData): ElderlyAdvice[] {
    const advice: ElderlyAdvice[] = [];
    const surplus = currentData.P_PV - currentData.P_Load;
    const hour = new Date().getHours();

    // High surplus situation
    if (surplus > 500) {
      advice.push({
        id: 'surplus-high',
        title_catalan: 'Tens molta energia solar disponible! ☀️',
        description_catalan: 'Ara és un bon moment per usar els electrodomèstics que consumeixen més energia.',
        simple_action: 'Posa la rentadora, rentaplats o escalfa l\'aigua',
        timing_recommendation: 'Ara mateix és perfecte',
        potential_benefit: `Estalviaràs uns ${Math.round(surplus * 0.12 / 1000)} cèntims per hora`,
        priority: 'high',
        weather_context: weather ? this.getWeatherContextCatalan(weather) : undefined,
      });
    }

    // Morning advice
    if (hour >= 7 && hour <= 10) {
      advice.push({
        id: 'morning-routine',
        title_catalan: 'Bon dia! Començem amb energia solar 🌅',
        description_catalan: 'Els panells solars ja estan començant a produir energia.',
        simple_action: 'Prepara l\'esmorzar i posa la cafetera',
        timing_recommendation: 'Perfecte per començar el dia',
        potential_benefit: 'Energia neta per començar bé',
        priority: 'medium',
      });
    }

    // Lunch time optimization
    if (hour >= 11 && hour <= 14 && surplus > 200) {
      advice.push({
        id: 'lunch-optimal',
        title_catalan: 'Hora perfecta per cuinar! 👩‍🍳',
        description_catalan: 'És el millor moment del dia per usar el forn i la vitroceràmica.',
        simple_action: 'Cuina quelcom especial utilitzant l\'energia solar',
        timing_recommendation: 'Ara tens la màxima energia solar',
        potential_benefit: 'Cuines gratis amb el sol',
        priority: 'high',
      });
    }

    // Evening preparation
    if (hour >= 16 && hour <= 18) {
      advice.push({
        id: 'evening-prep',
        title_catalan: 'Prepara\'t per al vespre 🌆',
        description_catalan: 'Aprofita les últimes hores de sol per escalfar l\'aigua.',
        simple_action: 'Escalfa l\'aigua ara per tenir-la calenta aquesta nit',
        timing_recommendation: 'Les properes 2 hores són ideals',
        potential_benefit: 'Aigua calenta gratis per aquesta nit',
        priority: 'medium',
      });
    }

    return advice;
  }

  /**
   * Get weather context in Catalan
   */
  private getWeatherContextCatalan(weather: WeatherData): string {
    if (weather.cloud_cover > 70) {
      return 'Tot i que està ennuvolat, encara tens energia solar disponible.';
    } else if (weather.cloud_cover > 30) {
      return 'Hi ha alguns núvols, però la producció solar és bona.';
    } else {
             return 'Dia assolellat perfecte per aprofitar l\'energia solar!';
    }
  }

  /**
   * Get system status for mock
   */
  async getSystemStatus(): Promise<{
    isOnline: boolean;
    isProducing: boolean;
    lastUpdate: string;
    errorCount: number;
    mode: string;
  }> {
    const currentData = await this.getCurrentData();
    
    return {
      isOnline: true,
      isProducing: currentData.P_PV > 0,
      lastUpdate: new Date().toISOString(),
      errorCount: 0,
      mode: 'Enhanced Mock (Weather-Aware)',
    };
  }

  /**
   * Get predefined test scenarios
   */
  getTestScenarios(): Array<{
    name: string;
    description: string;
    solarPercentage: number;
    consumptionWatts: number;
  }> {
    return [
      {
        name: 'High Solar Production',
        description: 'Peak solar with moderate consumption',
        solarPercentage: 90,
        consumptionWatts: 800,
      },
      {
        name: 'Excess Solar (Export)',
        description: 'High solar production, low consumption',
        solarPercentage: 85,
        consumptionWatts: 400,
      },
      {
        name: 'Evening Consumption',
        description: 'No solar, high evening consumption',
        solarPercentage: 0,
        consumptionWatts: 1500,
      },
      {
        name: 'Cloudy Day',
        description: 'Reduced solar production',
        solarPercentage: 25,
        consumptionWatts: 900,
      },
      {
        name: 'Optimal Balance',
        description: 'Solar production matches consumption',
        solarPercentage: 60,
        consumptionWatts: 1320,
      },
    ];
  }
}

export default EnhancedMockFroniusClient; 