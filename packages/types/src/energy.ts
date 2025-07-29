/**
 * Energy Data Types for Parra Energy System
 * ==========================================
 * 
 * TypeScript interfaces matching the Python project's data structures
 * for energy production, consumption, and grid interaction.
 */

export interface PowerData {
  /** Solar production in watts */
  P_PV: number;
  /** House consumption in watts */
  P_Load: number;
  /** Grid power flow (+import, -export) in watts */
  P_Grid: number;
  /** Timestamp of the reading */
  timestamp: string;
}

export interface EnergyRecord {
  timestamp: string;
  production: number;
  consumption: number;
  grid_import: number;
  grid_export: number;
  self_consumption_rate?: number;
  autonomy_rate?: number;
  created_at: string;
}

export interface DailyEnergyRecord {
  date: string;
  total_production: number;
  total_consumption: number;
  total_grid_import: number;
  total_grid_export: number;
  peak_production: number;
  peak_consumption: number;
  self_consumption_rate: number;
  autonomy_rate: number;
  efficiency_score: number;
  savings_euros: number;
  created_at: string;
}

export interface EnergyStatus {
  current: PowerData;
  daily: DailyEnergyRecord;
  isProducing: boolean;
  isExporting: boolean;
  surplus: number;
}

export interface EnergyTrend {
  period: string;
  avg_production: number;
  avg_consumption: number;
  avg_self_consumption: number;
  efficiency_trend: number;
} 