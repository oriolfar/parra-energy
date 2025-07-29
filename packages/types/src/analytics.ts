/**
 * Analytics Types for Parra Energy System
 * =======================================
 * 
 * TypeScript interfaces for energy analytics, optimization insights,
 * and personalized recommendations.
 */

export type TipPriority = 'high' | 'medium' | 'low';
export type TipCategory = 'timing' | 'efficiency' | 'waste_reduction' | 'weather' | 'automation';
export type InsightType = 'efficiency' | 'savings' | 'consumption' | 'production' | 'forecast';

export interface OptimizationTip {
  id: string;
  title: string;
  description: string;
  category: TipCategory;
  priority: TipPriority;
  potential_savings_kwh: number;
  potential_savings_euros: number;
  actionable: boolean;
  context?: string;
  created_at: string;
  is_elderly_friendly?: boolean;
  catalan_description?: string;
}

export interface EnergyInsight {
  id: string;
  type: InsightType;
  title: string;
  description: string;
  value: number;
  unit: string;
  trend: 'improving' | 'declining' | 'stable';
  period: string;
  confidence: number;
  created_at: string;
}

export interface EfficiencyMetrics {
  self_consumption_rate: number;
  autonomy_rate: number;
  efficiency_score: number;
  solar_utilization: number;
  grid_dependency: number;
  daily_savings: number;
  monthly_trend: number;
  yearly_projection: number;
}

export interface EnergyPattern {
  hour: number;
  avg_production: number;
  avg_consumption: number;
  typical_surplus: number;
  recommendation: string;
}

export interface ConsumptionAnalysis {
  period: string;
  total_consumption: number;
  peak_hours: number[];
  off_peak_hours: number[];
  waste_opportunities: string[];
  optimization_potential: number;
}

export interface ProductionAnalysis {
  period: string;
  total_production: number;
  peak_production_hour: number;
  weather_correlation: number;
  seasonal_factor: number;
  forecast_accuracy: number;
}

export interface OptimizationReport {
  date: string;
  efficiency_score: number;
  recommendations: OptimizationTip[];
  insights: EnergyInsight[];
  metrics: EfficiencyMetrics;
  patterns: EnergyPattern[];
  weather_impact: number;
  savings_summary: SavingsSummary;
}

export interface SavingsSummary {
  daily_savings_euros: number;
  monthly_projection: number;
  yearly_projection: number;
  co2_saved_kg: number;
  grid_independence_hours: number;
}

export interface ElderlyAdvice {
  id: string;
  title_catalan: string;
  description_catalan: string;
  simple_action: string;
  timing_recommendation: string;
  potential_benefit: string;
  weather_context?: string;
  priority: TipPriority;
} 