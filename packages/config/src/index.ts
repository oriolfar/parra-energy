/**
 * Configuration Management for Parra Energy System
 * ================================================
 * 
 * Centralized configuration with environment support and type safety.
 * Based on the Python configuration system with dataclasses.
 */

import { SystemConfig } from '@repo/types';

export interface SystemConfiguration {
  // Solar system specifications
  solar: {
    capacity_watts: number;
    inverter_host: string;
    location: string;
    coordinates: {
      latitude: number;
      longitude: number;
    };
  };

  // Web server configuration
  web: {
    host: string;
    port: number;
    auto_open_browser: boolean;
    cors_enabled: boolean;
  };

  // Database configuration
  database: {
    main_db_path: string;
    keep_raw_data_days: number;
    backup_enabled: boolean;
    backup_interval_hours: number;
  };

  // Weather service configuration
  weather: {
    forecast_days: number;
    api_base_url: string;
    update_interval_minutes: number;
    cache_duration_minutes: number;
  };

  // Logging configuration
  logging: {
    level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR';
    console_level: string;
    file_enabled: boolean;
    quiet_mode: boolean;
    max_file_size_mb: number;
    backup_count: number;
  };

  // Data polling configuration
  polling: {
    inverter_interval_seconds: number;
    weather_interval_minutes: number;
    database_save_interval_minutes: number;
    max_retries: number;
    retry_delay_seconds: number;
  };

  // Automation configuration
  automation: {
    enabled: boolean;
    min_surplus_threshold: number;
    device_control_enabled: boolean;
    safety_timeout_minutes: number;
  };

  // Analytics configuration
  analytics: {
    calculation_interval_hours: number;
    historical_days: number;
    forecasting_enabled: boolean;
    elderly_advice_enabled: boolean;
  };
}

export type Environment = 'development' | 'production' | 'testing';

/**
 * Configuration class that provides environment-aware settings
 */
export class Config {
  private config: SystemConfiguration;
  private environment: Environment;

  constructor(environment: Environment = 'development') {
    this.environment = environment;
    this.config = this.loadConfiguration();
  }

  private loadConfiguration(): SystemConfiguration {
    const baseConfig: SystemConfiguration = {
      solar: {
        capacity_watts: this.getEnvNumber('SOLAR_CAPACITY_WATTS', 2200),
        inverter_host: this.getEnvString('INVERTER_HOST', '192.168.1.128'),
        location: this.getEnvString('LOCATION', 'Agramunt, Spain'),
        coordinates: {
          latitude: this.getEnvNumber('LATITUDE', 41.7869),
          longitude: this.getEnvNumber('LONGITUDE', 1.0968),
        },
      },

      web: {
        host: this.getEnvString('WEB_HOST', 'localhost'),
        port: this.getEnvNumber('WEB_PORT', this.getDefaultPort()),
        auto_open_browser: this.getEnvBoolean('AUTO_OPEN_BROWSER', this.environment === 'development'),
        cors_enabled: this.getEnvBoolean('CORS_ENABLED', this.environment === 'development'),
      },

      database: {
        main_db_path: this.getEnvString('DB_PATH', this.getDefaultDbPath()),
        keep_raw_data_days: this.getEnvNumber('KEEP_RAW_DATA_DAYS', 365),
        backup_enabled: this.getEnvBoolean('DB_BACKUP_ENABLED', this.environment === 'production'),
        backup_interval_hours: this.getEnvNumber('DB_BACKUP_INTERVAL_HOURS', 24),
      },

      weather: {
        forecast_days: this.getEnvNumber('WEATHER_FORECAST_DAYS', 7),
        api_base_url: this.getEnvString('WEATHER_API_URL', 'https://api.open-meteo.com/v1/forecast'),
        update_interval_minutes: this.getEnvNumber('WEATHER_UPDATE_INTERVAL', 60),
        cache_duration_minutes: this.getEnvNumber('WEATHER_CACHE_DURATION', 30),
      },

      logging: {
        level: this.getEnvString('LOG_LEVEL', this.getDefaultLogLevel()) as any,
        console_level: this.getEnvString('CONSOLE_LOG_LEVEL', this.getDefaultLogLevel()),
        file_enabled: this.getEnvBoolean('LOG_FILE_ENABLED', true),
        quiet_mode: this.getEnvBoolean('QUIET_MODE', false),
        max_file_size_mb: this.getEnvNumber('LOG_MAX_FILE_SIZE_MB', 10),
        backup_count: this.getEnvNumber('LOG_BACKUP_COUNT', 5),
      },

      polling: {
        inverter_interval_seconds: this.getEnvNumber('INVERTER_POLL_INTERVAL', this.getDefaultPollInterval()),
        weather_interval_minutes: this.getEnvNumber('WEATHER_POLL_INTERVAL', 60),
        database_save_interval_minutes: this.getEnvNumber('DB_SAVE_INTERVAL', 5),
        max_retries: this.getEnvNumber('MAX_RETRIES', 3),
        retry_delay_seconds: this.getEnvNumber('RETRY_DELAY', 5),
      },

      automation: {
        enabled: this.getEnvBoolean('AUTOMATION_ENABLED', true),
        min_surplus_threshold: this.getEnvNumber('MIN_SURPLUS_THRESHOLD', 100),
        device_control_enabled: this.getEnvBoolean('DEVICE_CONTROL_ENABLED', this.environment !== 'testing'),
        safety_timeout_minutes: this.getEnvNumber('AUTOMATION_SAFETY_TIMEOUT', 60),
      },

      analytics: {
        calculation_interval_hours: this.getEnvNumber('ANALYTICS_INTERVAL', 6),
        historical_days: this.getEnvNumber('ANALYTICS_HISTORICAL_DAYS', 30),
        forecasting_enabled: this.getEnvBoolean('FORECASTING_ENABLED', true),
        elderly_advice_enabled: this.getEnvBoolean('ELDERLY_ADVICE_ENABLED', true),
      },
    };

    return baseConfig;
  }

  // Environment-specific defaults
  private getDefaultPort(): number {
    switch (this.environment) {
      case 'production': return 5001;
      case 'testing': return 5003;
      default: return 5001;
    }
  }

  private getDefaultDbPath(): string {
    switch (this.environment) {
      case 'production': return 'data/energy_data.db';
      case 'testing': return 'data/test_energy_data.db';
      default: return 'data/dev_energy_data.db';
    }
  }

  private getDefaultLogLevel(): string {
    switch (this.environment) {
      case 'production': return 'INFO';
      case 'testing': return 'WARNING';
      default: return 'DEBUG';
    }
  }

  private getDefaultPollInterval(): number {
    switch (this.environment) {
      case 'production': return 5;
      case 'testing': return 30;
      default: return 5;
    }
  }

  // Environment variable helpers
  private getEnvString(key: string, defaultValue: string): string {
    return process.env[key] || defaultValue;
  }

  private getEnvNumber(key: string, defaultValue: number): number {
    const value = process.env[key];
    return value ? parseInt(value, 10) : defaultValue;
  }

  private getEnvBoolean(key: string, defaultValue: boolean): boolean {
    const value = process.env[key];
    if (value === undefined) return defaultValue;
    return value.toLowerCase() === 'true' || value === '1';
  }

  // Public accessors
  public get solar() { return this.config.solar; }
  public get web() { return this.config.web; }
  public get database() { return this.config.database; }
  public get weather() { return this.config.weather; }
  public get logging() { return this.config.logging; }
  public get polling() { return this.config.polling; }
  public get automation() { return this.config.automation; }
  public get analytics() { return this.config.analytics; }
  public get env() { return this.environment; }

  /**
   * Get configuration as SystemConfig interface (for compatibility)
   */
  public toSystemConfig(): SystemConfig {
    return {
      solar_capacity_watts: this.solar.capacity_watts,
      inverter_host: this.solar.inverter_host,
      location: this.solar.location,
      web_port: this.web.port,
      db_path: this.database.main_db_path,
      weather_forecast_days: this.weather.forecast_days,
      data_retention_days: this.database.keep_raw_data_days,
    };
  }

  /**
   * Validate configuration settings
   */
  public validate(): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (this.solar.capacity_watts <= 0) {
      errors.push('Solar capacity must be greater than 0');
    }

    if (this.web.port < 1 || this.web.port > 65535) {
      errors.push('Web port must be between 1 and 65535');
    }

    if (this.weather.forecast_days < 1 || this.weather.forecast_days > 14) {
      errors.push('Weather forecast days must be between 1 and 14');
    }

    if (this.database.keep_raw_data_days < 1) {
      errors.push('Data retention days must be at least 1');
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }
}

// Export default config instance
export const config = new Config();

// Export factory function for different environments
export function createConfig(environment: Environment): Config {
  return new Config(environment);
} 