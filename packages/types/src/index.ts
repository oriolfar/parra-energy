/**
 * Parra Energy Types - TypeScript Interfaces
 * ==========================================
 * 
 * Centralized type definitions for the Parra Energy solar monitoring
 * and automation system.
 */

// Energy data types
export * from './energy';

// Weather and forecasting types
export * from './weather';

// Device automation types
export * from './automation';

// Analytics and optimization types
export * from './analytics';

// System configuration and utilities
export interface SystemConfig {
  solar_capacity_watts: number;
  inverter_host: string;
  location: string;
  web_port: number;
  db_path: string;
  weather_forecast_days: number;
  data_retention_days: number;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface TimeRange {
  start: string;
  end: string;
}

export interface Coordinates {
  latitude: number;
  longitude: number;
}

// Dashboard interface types
export type DashboardMode = 'technical' | 'elderly';
export type ThemeMode = 'light' | 'dark' | 'auto';

export interface DashboardConfig {
  mode: DashboardMode;
  theme: ThemeMode;
  language: 'en' | 'ca' | 'es';
  refresh_interval: number;
  show_advanced_metrics: boolean;
}

export interface UserPreferences {
  dashboard: DashboardConfig;
  notifications: {
    email_enabled: boolean;
    push_enabled: boolean;
    thresholds: {
      low_production: number;
      high_consumption: number;
      grid_export_threshold: number;
    };
  };
} 