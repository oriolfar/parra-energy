/**
 * Database Management for Parra Energy System
 * ===========================================
 * 
 * SQLite database operations and utilities using sqlite3.
 * Based on the Python database utility module.
 */

import sqlite3 from 'sqlite3';
import { join, dirname } from 'path';
import { mkdirSync, existsSync } from 'fs';
import { promisify } from 'util';
import type {
  EnergyRecord,
  DailyEnergyRecord,
  WeatherData,
  WeatherForecast,
  Device,
  AutomationEvent,
  OptimizationTip,
  EnergyInsight,
} from '@repo/types';

export class DatabaseManager {
  private db: sqlite3.Database;
  private dbPath: string;

  constructor(dbPath: string = 'data/energy_data.db') {
    this.dbPath = dbPath;
    this.ensureDirectoryExists();
    this.db = new sqlite3.Database(dbPath);
    this.initializeTables();
  }

  private ensureDirectoryExists(): void {
    const dir = dirname(this.dbPath);
    if (!existsSync(dir)) {
      mkdirSync(dir, { recursive: true });
    }
  }

  private async initializeTables(): Promise<void> {
    await this.createEnergyTables();
    await this.createWeatherTables();
    await this.createAutomationTables();
    await this.createAnalyticsTables();
  }

  private async run(sql: string, params: any[] = []): Promise<any> {
    return new Promise((resolve, reject) => {
      this.db.run(sql, params, function(err) {
        if (err) reject(err);
        else resolve({ lastID: this.lastID, changes: this.changes });
      });
    });
  }

  private async get(sql: string, params: any[] = []): Promise<any> {
    return new Promise((resolve, reject) => {
      this.db.get(sql, params, (err, row) => {
        if (err) reject(err);
        else resolve(row);
      });
    });
  }

  private async all(sql: string, params: any[] = []): Promise<any[]> {
    return new Promise((resolve, reject) => {
      this.db.all(sql, params, (err, rows) => {
        if (err) reject(err);
        else resolve(rows || []);
      });
    });
  }

  private async createEnergyTables(): Promise<void> {
    // Main energy production and consumption data (5-minute intervals)
    await this.run(`
      CREATE TABLE IF NOT EXISTS energy (
        timestamp TEXT PRIMARY KEY,
        production REAL NOT NULL,
        consumption REAL NOT NULL,
        grid_import REAL DEFAULT 0,
        grid_export REAL DEFAULT 0,
        self_consumption_rate REAL,
        autonomy_rate REAL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Daily energy summaries
    await this.run(`
      CREATE TABLE IF NOT EXISTS daily_energy (
        date TEXT PRIMARY KEY,
        total_production REAL NOT NULL,
        total_consumption REAL NOT NULL,
        total_grid_import REAL DEFAULT 0,
        total_grid_export REAL DEFAULT 0,
        peak_production REAL DEFAULT 0,
        peak_consumption REAL DEFAULT 0,
        self_consumption_rate REAL DEFAULT 0,
        autonomy_rate REAL DEFAULT 0,
        efficiency_score REAL DEFAULT 0,
        savings_euros REAL DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Create indexes for performance
    await this.run(`CREATE INDEX IF NOT EXISTS idx_energy_timestamp ON energy(timestamp)`);
    await this.run(`CREATE INDEX IF NOT EXISTS idx_daily_energy_date ON daily_energy(date)`);
  }

  private async createWeatherTables(): Promise<void> {
    // Weather forecast data
    await this.run(`
      CREATE TABLE IF NOT EXISTS weather_forecast (
        date TEXT,
        location TEXT,
        temperature_min REAL,
        temperature_max REAL,
        cloud_cover REAL,
        uv_index REAL,
        solar_radiation REAL,
        precipitation_probability REAL,
        wind_speed REAL,
        weather_code INTEGER,
        weather_description TEXT,
        expected_solar_production REAL,
        forecast_created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (date, location)
      )
    `);

    // Current weather data
    await this.run(`
      CREATE TABLE IF NOT EXISTS weather_current (
        timestamp TEXT,
        location TEXT,
        temperature REAL,
        humidity REAL,
        cloud_cover REAL,
        uv_index REAL,
        solar_radiation REAL,
        wind_speed REAL,
        precipitation REAL,
        weather_description TEXT,
        PRIMARY KEY (timestamp, location)
      )
    `);

    await this.run(`CREATE INDEX IF NOT EXISTS idx_weather_forecast_date ON weather_forecast(date)`);
    await this.run(`CREATE INDEX IF NOT EXISTS idx_weather_current_timestamp ON weather_current(timestamp)`);
  }

  private async createAutomationTables(): Promise<void> {
    // Device registry
    await this.run(`
      CREATE TABLE IF NOT EXISTS devices (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        power_consumption REAL NOT NULL,
        priority TEXT NOT NULL,
        category TEXT NOT NULL,
        status TEXT NOT NULL,
        is_automated BOOLEAN DEFAULT 0,
        description TEXT,
        location TEXT,
        manual_override BOOLEAN DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Automation events log
    await this.run(`
      CREATE TABLE IF NOT EXISTS automation_events (
        id TEXT PRIMARY KEY,
        device_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        trigger_reason TEXT NOT NULL,
        surplus_watts REAL NOT NULL,
        timestamp TEXT NOT NULL,
        success BOOLEAN NOT NULL,
        error_message TEXT,
        FOREIGN KEY (device_id) REFERENCES devices (id)
      )
    `);

    await this.run(`CREATE INDEX IF NOT EXISTS idx_automation_events_device_id ON automation_events(device_id)`);
    await this.run(`CREATE INDEX IF NOT EXISTS idx_automation_events_timestamp ON automation_events(timestamp)`);
  }

  private async createAnalyticsTables(): Promise<void> {
    // Optimization insights
    await this.run(`
      CREATE TABLE IF NOT EXISTS optimization_insights (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        category TEXT NOT NULL,
        priority TEXT NOT NULL,
        potential_savings_kwh REAL DEFAULT 0,
        potential_savings_euros REAL DEFAULT 0,
        actionable BOOLEAN DEFAULT 1,
        context TEXT,
        is_elderly_friendly BOOLEAN DEFAULT 0,
        catalan_description TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Energy insights and analytics
    await this.run(`
      CREATE TABLE IF NOT EXISTS energy_insights (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        value REAL NOT NULL,
        unit TEXT NOT NULL,
        trend TEXT NOT NULL,
        period TEXT NOT NULL,
        confidence REAL DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
      )
    `);

    await this.run(`CREATE INDEX IF NOT EXISTS idx_optimization_insights_category ON optimization_insights(category)`);
    await this.run(`CREATE INDEX IF NOT EXISTS idx_energy_insights_type ON energy_insights(type)`);
  }

  // Energy data operations
  public async insertEnergyRecord(record: Omit<EnergyRecord, 'created_at'>): Promise<void> {
    await this.run(`
      INSERT OR REPLACE INTO energy (
        timestamp, production, consumption, grid_import, grid_export,
        self_consumption_rate, autonomy_rate
      ) VALUES (?, ?, ?, ?, ?, ?, ?)
    `, [
      record.timestamp,
      record.production,
      record.consumption,
      record.grid_import,
      record.grid_export,
      record.self_consumption_rate,
      record.autonomy_rate
    ]);
  }

  public async insertDailyEnergyRecord(record: Omit<DailyEnergyRecord, 'created_at'>): Promise<void> {
    await this.run(`
      INSERT OR REPLACE INTO daily_energy (
        date, total_production, total_consumption, total_grid_import, total_grid_export,
        peak_production, peak_consumption, self_consumption_rate, autonomy_rate,
        efficiency_score, savings_euros
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `, [
      record.date,
      record.total_production,
      record.total_consumption,
      record.total_grid_import,
      record.total_grid_export,
      record.peak_production,
      record.peak_consumption,
      record.self_consumption_rate,
      record.autonomy_rate,
      record.efficiency_score,
      record.savings_euros
    ]);
  }

  public async getEnergyRecords(startDate: string, endDate: string): Promise<EnergyRecord[]> {
    return await this.all(`
      SELECT * FROM energy 
      WHERE timestamp BETWEEN ? AND ? 
      ORDER BY timestamp
    `, [startDate, endDate]);
  }

  public async getLatestEnergyRecord(): Promise<EnergyRecord | null> {
    return await this.get(`
      SELECT * FROM energy 
      ORDER BY timestamp DESC 
      LIMIT 1
    `);
  }

  public async getDailyEnergyRecord(date: string): Promise<DailyEnergyRecord | null> {
    return await this.get(`
      SELECT * FROM daily_energy WHERE date = ?
    `, [date]);
  }

  // Weather data operations
  public async insertWeatherForecast(forecast: Omit<WeatherForecast, 'forecast_created_at'>): Promise<void> {
    await this.run(`
      INSERT OR REPLACE INTO weather_forecast (
        date, location, temperature_min, temperature_max, cloud_cover,
        uv_index, solar_radiation, precipitation_probability, wind_speed,
        weather_code, weather_description, expected_solar_production
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `, [
      forecast.date,
      forecast.location,
      forecast.temperature_min,
      forecast.temperature_max,
      forecast.cloud_cover,
      forecast.uv_index,
      forecast.solar_radiation,
      forecast.precipitation_probability,
      forecast.wind_speed,
      forecast.weather_code,
      forecast.weather_description,
      forecast.expected_solar_production
    ]);
  }

  public async insertCurrentWeather(weather: WeatherData): Promise<void> {
    await this.run(`
      INSERT OR REPLACE INTO weather_current (
        timestamp, location, temperature, humidity, cloud_cover,
        uv_index, solar_radiation, wind_speed, precipitation, weather_description
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `, [
      weather.timestamp,
      weather.location,
      weather.temperature,
      weather.humidity,
      weather.cloud_cover,
      weather.uv_index,
      weather.solar_radiation,
      weather.wind_speed,
      weather.precipitation,
      weather.weather_description
    ]);
  }

  public async getWeatherForecast(location: string, days: number = 7): Promise<WeatherForecast[]> {
    return await this.all(`
      SELECT * FROM weather_forecast 
      WHERE location = ? 
      ORDER BY date 
      LIMIT ?
    `, [location, days]);
  }

  // Device operations
  public async insertDevice(device: Omit<Device, 'created_at' | 'updated_at'>): Promise<void> {
    await this.run(`
      INSERT OR REPLACE INTO devices (
        id, name, power_consumption, priority, category, status,
        is_automated, description, location, manual_override
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `, [
      device.id,
      device.name,
      device.power_consumption,
      device.priority,
      device.category,
      device.status,
      device.is_automated ? 1 : 0,
      device.description,
      device.location,
      device.manual_override ? 1 : 0
    ]);
  }

  public async getDevices(): Promise<Device[]> {
    const rows = await this.all('SELECT * FROM devices ORDER BY name');
    return rows.map(row => ({
      ...row,
      is_automated: Boolean(row.is_automated),
      manual_override: Boolean(row.manual_override),
    }));
  }

  public async getDevice(id: string): Promise<Device | null> {
    const row = await this.get('SELECT * FROM devices WHERE id = ?', [id]);
    if (!row) return null;
    
    return {
      ...row,
      is_automated: Boolean(row.is_automated),
      manual_override: Boolean(row.manual_override),
    };
  }

  // Automation events
  public async insertAutomationEvent(event: AutomationEvent): Promise<void> {
    await this.run(`
      INSERT INTO automation_events (
        id, device_id, event_type, trigger_reason, surplus_watts,
        timestamp, success, error_message
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `, [
      event.id,
      event.device_id,
      event.event_type,
      event.trigger_reason,
      event.surplus_watts,
      event.timestamp,
      event.success ? 1 : 0,
      event.error_message
    ]);
  }

  public async getAutomationEvents(deviceId?: string, limit: number = 100): Promise<AutomationEvent[]> {
    let query = 'SELECT * FROM automation_events';
    const params: any[] = [];

    if (deviceId) {
      query += ' WHERE device_id = ?';
      params.push(deviceId);
    }

    query += ' ORDER BY timestamp DESC LIMIT ?';
    params.push(limit);

    const rows = await this.all(query, params);
    return rows.map(row => ({
      ...row,
      success: Boolean(row.success),
    }));
  }

  // Analytics operations
  public async insertOptimizationTip(tip: Omit<OptimizationTip, 'created_at'>): Promise<void> {
    await this.run(`
      INSERT OR REPLACE INTO optimization_insights (
        id, title, description, category, priority, potential_savings_kwh,
        potential_savings_euros, actionable, context, is_elderly_friendly, catalan_description
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `, [
      tip.id,
      tip.title,
      tip.description,
      tip.category,
      tip.priority,
      tip.potential_savings_kwh,
      tip.potential_savings_euros,
      tip.actionable ? 1 : 0,
      tip.context,
      tip.is_elderly_friendly ? 1 : 0,
      tip.catalan_description
    ]);
  }

  public async getOptimizationTips(category?: string, elderlyFriendly?: boolean): Promise<OptimizationTip[]> {
    let query = 'SELECT * FROM optimization_insights WHERE 1=1';
    const params: any[] = [];

    if (category) {
      query += ' AND category = ?';
      params.push(category);
    }

    if (elderlyFriendly !== undefined) {
      query += ' AND is_elderly_friendly = ?';
      params.push(elderlyFriendly ? 1 : 0);
    }

    query += ' ORDER BY priority DESC, created_at DESC';

    const rows = await this.all(query, params);
    return rows.map(row => ({
      ...row,
      actionable: Boolean(row.actionable),
      is_elderly_friendly: Boolean(row.is_elderly_friendly),
    }));
  }

  // Utility methods
  public async cleanup(retentionDays: number = 365): Promise<void> {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - retentionDays);
    const cutoffDateStr = cutoffDate.toISOString();

    // Clean old energy records
    await this.run('DELETE FROM energy WHERE timestamp < ?', [cutoffDateStr]);
    
    // Clean old automation events
    await this.run('DELETE FROM automation_events WHERE timestamp < ?', [cutoffDateStr]);
    
    // Vacuum to reclaim space
    await this.run('VACUUM');
  }

  public close(): void {
    this.db.close();
  }
}

// Export factory function
export function createDatabase(dbPath?: string): DatabaseManager {
  return new DatabaseManager(dbPath);
}

export default DatabaseManager; 