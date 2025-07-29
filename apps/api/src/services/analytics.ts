/**
 * Energy Analytics and Optimization Engine
 * =======================================
 * 
 * Intelligent analysis of energy data to generate personalized optimization
 * recommendations, efficiency insights, and predictive planning advice.
 * Based on the Python analytics optimizer implementation.
 */

import { DatabaseManager } from '@repo/database';
import WeatherService from './weather';
import type {
  OptimizationTip,
  EnergyInsight,
  EfficiencyMetrics,
  EnergyPattern,
  ConsumptionAnalysis,
  ProductionAnalysis,
  OptimizationReport,
  SavingsSummary,
  ElderlyAdvice,
  PowerData,
  EnergyRecord,
  DailyEnergyRecord,
  TipPriority,
  TipCategory,
} from '@repo/types';

export class EnergyAnalytics {
  private db: DatabaseManager;
  private weatherService: WeatherService;
  private solarCapacity: number;

  constructor(dbPath?: string, solarCapacity: number = 2200) {
    this.db = new DatabaseManager(dbPath);
    this.weatherService = new WeatherService(dbPath);
    this.solarCapacity = solarCapacity;
  }

  /**
   * Generate optimization tips based on historical data and current conditions
   */
  async generateOptimizationTips(currentData: PowerData, elderlyFriendly: boolean = false): Promise<OptimizationTip[]> {
    const tips: OptimizationTip[] = [];
    const surplus = currentData.P_PV - currentData.P_Load;
    const hour = new Date().getHours();

    // High surplus opportunities
    if (surplus > 500) {
      tips.push({
        id: `surplus-${Date.now()}`,
        title: 'High Solar Surplus Available',
        description: 'You have significant excess solar energy. This is the perfect time to run high-power appliances.',
        category: 'timing',
        priority: 'high',
        potential_savings_kwh: surplus / 1000,
        potential_savings_euros: (surplus / 1000) * 0.12,
        actionable: true,
        context: `Current surplus: ${Math.round(surplus)}W`,
        created_at: new Date().toISOString(),
        is_elderly_friendly: elderlyFriendly,
        catalan_description: elderlyFriendly ? 
          'Tens molta energia solar disponible! Ara és un bon moment per usar electrodomèstics que consumeixen molt.' : undefined,
      });
    }

    // Peak solar hours optimization
    if (hour >= 11 && hour <= 14) {
      tips.push({
        id: `peak-solar-${Date.now()}`,
        title: 'Peak Solar Production Hours',
        description: 'This is peak solar time. Consider running dishwasher, washing machine, or charging electric vehicles.',
        category: 'timing',
        priority: 'high',
        potential_savings_kwh: 2.0,
        potential_savings_euros: 0.24,
        actionable: true,
        context: 'Peak solar hours: 11 AM - 2 PM',
        created_at: new Date().toISOString(),
        is_elderly_friendly: elderlyFriendly,
        catalan_description: elderlyFriendly ? 
          'És l\'hora de màxima producció solar! Perfecte per posar rentadora o rentaplats.' : undefined,
      });
    }

    // Evening preparation
    if (hour >= 15 && hour <= 17 && currentData.P_PV > 800) {
      tips.push({
        id: `evening-prep-${Date.now()}`,
        title: 'Prepare for Evening',
        description: 'Use remaining solar energy to heat water or charge devices before evening consumption peak.',
        category: 'timing',
        priority: 'medium',
        potential_savings_kwh: 1.5,
        potential_savings_euros: 0.18,
        actionable: true,
        context: 'Last chance to use solar before evening',
        created_at: new Date().toISOString(),
        is_elderly_friendly: elderlyFriendly,
        catalan_description: elderlyFriendly ? 
          'Aprofita les últimes hores de sol per escalfar aigua!' : undefined,
      });
    }

    // Weather-based tips
    try {
      const weatherTips = await this.generateWeatherBasedTips(elderlyFriendly);
      tips.push(...weatherTips);
    } catch (error) {
      console.log('Could not generate weather-based tips:', error);
    }

    return tips;
  }

  /**
   * Generate weather-based optimization tips
   */
  private async generateWeatherBasedTips(elderlyFriendly: boolean): Promise<OptimizationTip[]> {
    const tips: OptimizationTip[] = [];
    const forecast = await this.weatherService.getWeatherForecast(1);
    
    if (forecast.length > 0) {
      const today = forecast[0];
      
      // Cloudy day advice
      if (today.cloud_cover > 70) {
        tips.push({
          id: `cloudy-${Date.now()}`,
          title: 'Cloudy Day Strategy',
          description: 'Today is cloudy. Consider postponing high-energy activities until clearer weather.',
          category: 'weather',
          priority: 'medium',
          potential_savings_kwh: 1.0,
          potential_savings_euros: 0.12,
          actionable: true,
          context: `Cloud cover: ${Math.round(today.cloud_cover)}%`,
          created_at: new Date().toISOString(),
          is_elderly_friendly: elderlyFriendly,
          catalan_description: elderlyFriendly ? 
            'Avui està ennuvolat. Millor deixar les tasques que consumeixen molt per demà.' : undefined,
        });
      }
      
      // Clear day optimization
      if (today.cloud_cover < 30 && today.uv_index > 6) {
        tips.push({
          id: `clear-${Date.now()}`,
          title: 'Perfect Solar Day',
          description: 'Excellent solar conditions today! This is the best day this week for high-energy activities.',
          category: 'weather',
          priority: 'high',
          potential_savings_kwh: 3.0,
          potential_savings_euros: 0.36,
          actionable: true,
          context: `UV Index: ${today.uv_index}, Clear sky`,
          created_at: new Date().toISOString(),
          is_elderly_friendly: elderlyFriendly,
          catalan_description: elderlyFriendly ? 
            'Dia perfecte de sol! Aprofita per fer totes les tasques de casa.' : undefined,
        });
      }
    }

    return tips;
  }

  /**
   * Calculate current efficiency metrics
   */
  async calculateEfficiencyMetrics(currentData: PowerData): Promise<EfficiencyMetrics> {
    // Get recent data for calculations
    const endDate = new Date().toISOString();
    const startDate = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(); // Last 24 hours
    const recentRecords = await this.db.getEnergyRecords(startDate, endDate);

    if (recentRecords.length === 0) {
      // Return default metrics if no historical data
      return {
        self_consumption_rate: 0,
        autonomy_rate: 0,
        efficiency_score: 0,
        solar_utilization: 0,
        grid_dependency: 100,
        daily_savings: 0,
        monthly_trend: 0,
        yearly_projection: 0,
      };
    }

    // Calculate metrics from recent data
    const totalProduction = recentRecords.reduce((sum, record) => sum + record.production, 0);
    const totalConsumption = recentRecords.reduce((sum, record) => sum + record.consumption, 0);
    const totalGridImport = recentRecords.reduce((sum, record) => sum + record.grid_import, 0);
    const totalGridExport = recentRecords.reduce((sum, record) => sum + record.grid_export, 0);

    // Self-consumption rate: how much of produced energy is used directly
    const selfConsumptionRate = totalProduction > 0 ? 
      Math.min(100, ((totalProduction - totalGridExport) / totalProduction) * 100) : 0;

    // Autonomy rate: how much of consumption is covered by own production
    const autonomyRate = totalConsumption > 0 ? 
      Math.min(100, ((totalConsumption - totalGridImport) / totalConsumption) * 100) : 0;

    // Solar utilization: how much of available solar potential is being captured
    const theoreticalMaxProduction = this.solarCapacity * 8; // 8 hours equivalent full sun
    const solarUtilization = Math.min(100, (totalProduction / theoreticalMaxProduction) * 100);

    // Grid dependency
    const gridDependency = 100 - autonomyRate;

    // Efficiency score (combination of self-consumption and autonomy)
    const efficiencyScore = (selfConsumptionRate + autonomyRate) / 2;

    // Daily savings estimation
    const gridEnergyAvoided = totalConsumption - totalGridImport;
    const dailySavings = (gridEnergyAvoided / 1000) * 0.12; // 0.12€ per kWh

    return {
      self_consumption_rate: Math.round(selfConsumptionRate * 10) / 10,
      autonomy_rate: Math.round(autonomyRate * 10) / 10,
      efficiency_score: Math.round(efficiencyScore * 10) / 10,
      solar_utilization: Math.round(solarUtilization * 10) / 10,
      grid_dependency: Math.round(gridDependency * 10) / 10,
      daily_savings: Math.round(dailySavings * 100) / 100,
      monthly_trend: 0, // Would need more historical data
      yearly_projection: dailySavings * 365,
    };
  }

  /**
   * Analyze energy consumption patterns
   */
  async analyzeConsumptionPatterns(): Promise<ConsumptionAnalysis> {
    const endDate = new Date().toISOString();
    const startDate = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(); // Last 7 days
    const records = await this.db.getEnergyRecords(startDate, endDate);

    if (records.length === 0) {
      return {
        period: 'last_7_days',
        total_consumption: 0,
        peak_hours: [19, 20, 21],
        off_peak_hours: [2, 3, 4, 5],
        waste_opportunities: [],
        optimization_potential: 0,
      };
    }

    const totalConsumption = records.reduce((sum, record) => sum + record.consumption, 0);

    // Analyze hourly patterns
    const hourlyConsumption: { [hour: number]: number } = {};
    for (let i = 0; i < 24; i++) {
      hourlyConsumption[i] = 0;
    }

    records.forEach(record => {
      const hour = new Date(record.timestamp).getHours();
      hourlyConsumption[hour] += record.consumption;
    });

    // Find peak and off-peak hours
    const hourlyAverages = Object.entries(hourlyConsumption)
      .map(([hour, consumption]) => ({ hour: parseInt(hour), consumption }))
      .sort((a, b) => b.consumption - a.consumption);

    const peakHours = hourlyAverages.slice(0, 3).map(h => h.hour);
    const offPeakHours = hourlyAverages.slice(-4).map(h => h.hour);

    // Identify waste opportunities
    const wasteOpportunities: string[] = [];
    
    // High consumption during low solar hours
    if (hourlyConsumption[20] > hourlyConsumption[13]) {
      wasteOpportunities.push('High evening consumption - consider shifting activities to midday');
    }
    
    // Base load analysis
    const minConsumption = Math.min(...Object.values(hourlyConsumption));
    if (minConsumption > 500) {
      wasteOpportunities.push('High base load - check for standby power consumption');
    }

    return {
      period: 'last_7_days',
      total_consumption: Math.round(totalConsumption),
      peak_hours: peakHours,
      off_peak_hours: offPeakHours,
      waste_opportunities: wasteOpportunities,
      optimization_potential: wasteOpportunities.length * 0.1, // 10% potential per opportunity
    };
  }

  /**
   * Generate comprehensive optimization report
   */
  async generateOptimizationReport(currentData: PowerData, elderlyFriendly: boolean = false): Promise<OptimizationReport> {
    const [
      recommendations,
      metrics,
      consumptionAnalysis,
      weatherQuality,
    ] = await Promise.all([
      this.generateOptimizationTips(currentData, elderlyFriendly),
      this.calculateEfficiencyMetrics(currentData),
      this.analyzeConsumptionPatterns(),
      this.weatherService.getWeatherQualityScore(),
    ]);

    // Generate energy patterns for the next 24 hours
    const patterns = this.generateEnergyPatterns();

    // Generate basic insights
    const insights: EnergyInsight[] = [
      {
        id: `insight-efficiency-${Date.now()}`,
        type: 'efficiency',
        title: 'System Efficiency',
        description: `Your solar system is operating at ${metrics.efficiency_score}% efficiency`,
        value: metrics.efficiency_score,
        unit: '%',
        trend: metrics.efficiency_score > 70 ? 'improving' : 'stable',
        period: 'daily',
        confidence: 0.9,
        created_at: new Date().toISOString(),
      },
      {
        id: `insight-savings-${Date.now()}`,
        type: 'savings',
        title: 'Daily Savings',
        description: `You saved ${metrics.daily_savings}€ today using solar energy`,
        value: metrics.daily_savings,
        unit: '€',
        trend: 'improving',
        period: 'daily',
        confidence: 0.85,
        created_at: new Date().toISOString(),
      }
    ];

    const savingsSummary: SavingsSummary = {
      daily_savings_euros: metrics.daily_savings,
      monthly_projection: metrics.daily_savings * 30,
      yearly_projection: metrics.yearly_projection,
      co2_saved_kg: (currentData.P_PV / 1000) * 0.4, // 0.4 kg CO2 per kWh
      grid_independence_hours: (metrics.autonomy_rate / 100) * 24,
    };

    return {
      date: new Date().toISOString().split('T')[0],
      efficiency_score: metrics.efficiency_score,
      recommendations,
      insights,
      metrics,
      patterns,
      weather_impact: weatherQuality,
      savings_summary: savingsSummary,
    };
  }

  /**
   * Generate hourly energy patterns for optimization
   */
  private generateEnergyPatterns(): EnergyPattern[] {
    const patterns: EnergyPattern[] = [];
    
    for (let hour = 0; hour < 24; hour++) {
      // Typical solar production curve
      let production = 0;
      if (hour >= 7 && hour <= 19) {
        const peak = 13; // 1 PM
        const hourFromPeak = Math.abs(hour - peak);
        production = Math.max(0, this.solarCapacity * Math.cos((hourFromPeak / 6) * Math.PI / 2));
      }

      // Typical consumption pattern
      let consumption = 300; // Base load
      if (hour >= 6 && hour < 10) consumption = 600; // Morning
      if (hour >= 12 && hour < 14) consumption = 800; // Lunch
      if (hour >= 17 && hour < 22) consumption = 1000; // Evening
      if (hour >= 22 || hour < 6) consumption = 400; // Night

      const surplus = production - consumption;
      
      let recommendation = 'Normal operation';
      if (surplus > 500) recommendation = 'Excellent time for high-power appliances';
      else if (surplus > 200) recommendation = 'Good time for moderate appliances';
      else if (surplus < -200) recommendation = 'Peak consumption - avoid unnecessary usage';

      patterns.push({
        hour,
        avg_production: Math.round(production),
        avg_consumption: Math.round(consumption),
        typical_surplus: Math.round(surplus),
        recommendation,
      });
    }

    return patterns;
  }

  /**
   * Generate elderly-friendly advice in Catalan
   */
  async generateElderlyAdvice(currentData: PowerData): Promise<ElderlyAdvice[]> {
    const advice: ElderlyAdvice[] = [];
    const surplus = currentData.P_PV - currentData.P_Load;
    const hour = new Date().getHours();

    // Morning advice
    if (hour >= 7 && hour <= 10) {
      advice.push({
        id: 'morning-advice',
        title_catalan: 'Bon dia! ☀️',
        description_catalan: 'Els panells solars ja estan produint energia. És un bon moment per preparar l\'esmorzar.',
        simple_action: 'Posa la cafetera i tosta el pa',
        timing_recommendation: 'Ara mateix',
        potential_benefit: 'Energia gratis per començar el dia',
        priority: 'medium',
      });
    }

    // High surplus advice
    if (surplus > 300) {
      advice.push({
        id: 'high-surplus',
        title_catalan: 'Tens energia solar de sobres! ⚡',
        description_catalan: 'Ara és el moment perfecte per usar electrodomèstics que consumeixen molt.',
        simple_action: 'Posa la rentadora o el rentaplats',
        timing_recommendation: 'Ara és ideal',
        potential_benefit: `Estalviaràs uns ${Math.round(surplus * 0.12 / 1000)} cèntims`,
        priority: 'high',
      });
    }

    // Lunch time advice
    if (hour >= 12 && hour <= 14) {
      advice.push({
        id: 'lunch-advice',
        title_catalan: 'Hora de dinar! 🍽️',
        description_catalan: 'És el millor moment del dia per cuinar amb energia solar.',
        simple_action: 'Usa el forn o la vitroceràmica',
        timing_recommendation: 'Les properes 2 hores',
        potential_benefit: 'Cuina completament gratis',
        priority: 'high',
      });
    }

    return advice;
  }
}

export default EnergyAnalytics; 