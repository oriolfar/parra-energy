/**
 * Smart Fronius Client with Fallback Logic
 * ========================================
 * 
 * Intelligent client that automatically falls back from real inverter
 * to enhanced mock to basic mock based on availability and configuration.
 * Based on the Python smart_fronius.py implementation.
 */

import { FroniusClient } from './fronius';
import { EnhancedMockFroniusClient } from './enhanced-mock-fronius';
import type { PowerData, WeatherData } from '@repo/types';
import { config } from '@repo/config';

export enum FroniusMode {
  REAL = 'real',
  ENHANCED_MOCK = 'enhanced_mock', 
  BASIC_MOCK = 'basic_mock'
}

export interface FroniusStatus {
  mode: FroniusMode;
  connected: boolean;
  lastUpdate: Date;
  errorCount: number;
  lastError?: string;
}

export class SmartFroniusClient {
  private realClient?: FroniusClient;
  private enhancedMockClient: EnhancedMockFroniusClient;
  private currentMode: FroniusMode;
  private status: FroniusStatus;
  private maxRetries: number = 3;
  private retryDelay: number = 1000; // ms
  private connectionTestInterval: number = 60000; // 1 minute

  constructor() {
    // Initialize clients
    this.enhancedMockClient = new EnhancedMockFroniusClient(
      config.solar.capacityWatts,
      config.solar.location
    );

    // Try to initialize real client if enabled
    if (config.fronius.enabled && config.fronius.host) {
      this.realClient = new FroniusClient(
        config.fronius.host,
        config.fronius.timeout
      );
    }

    // Start with enhanced mock as default
    this.currentMode = this.realClient ? FroniusMode.REAL : FroniusMode.ENHANCED_MOCK;
    
    this.status = {
      mode: this.currentMode,
      connected: false,
      lastUpdate: new Date(),
      errorCount: 0
    };

    // Start connection monitoring
    this.startConnectionMonitoring();
  }

  /**
   * Get current power data with automatic fallback
   */
  async getCurrentData(weather?: WeatherData): Promise<PowerData> {
    for (let mode of this.getFallbackSequence()) {
      try {
        const data = await this.getCurrentDataFromMode(mode, weather);
        
        // Update status on success
        this.updateStatus(mode, true);
        return data;
        
      } catch (error) {
        console.warn(`Failed to get power data from ${mode}:`, error);
        this.updateStatus(mode, false, error instanceof Error ? error.message : 'Unknown error');
        
        // If this was the real client, fall back to mock
        if (mode === FroniusMode.REAL) {
          console.log('Real inverter unavailable, falling back to enhanced mock');
          this.currentMode = FroniusMode.ENHANCED_MOCK;
        }
      }
    }

    // Ultimate fallback to basic mock
    console.warn('All Fronius clients failed, using basic mock');
    this.currentMode = FroniusMode.BASIC_MOCK;
    return this.getBasicMockData();
  }

  /**
   * Get power data from specific mode
   */
  private async getCurrentDataFromMode(mode: FroniusMode, weather?: WeatherData): Promise<PowerData> {
    switch (mode) {
      case FroniusMode.REAL:
        if (!this.realClient) {
          throw new Error('Real Fronius client not available');
        }
        return await this.realClient.getCurrentData();

      case FroniusMode.ENHANCED_MOCK:
        return await this.enhancedMockClient.getCurrentData(weather);

      case FroniusMode.BASIC_MOCK:
        return this.getBasicMockData();

      default:
        throw new Error(`Unknown Fronius mode: ${mode}`);
    }
  }

  /**
   * Get fallback sequence based on current mode and availability
   */
  private getFallbackSequence(): FroniusMode[] {
    const sequence: FroniusMode[] = [];
    
    // Always try current mode first
    sequence.push(this.currentMode);
    
    // Add other modes as fallbacks
    if (this.currentMode !== FroniusMode.REAL && this.realClient) {
      sequence.push(FroniusMode.REAL);
    }
    
    if (this.currentMode !== FroniusMode.ENHANCED_MOCK) {
      sequence.push(FroniusMode.ENHANCED_MOCK);
    }
    
    if (this.currentMode !== FroniusMode.BASIC_MOCK) {
      sequence.push(FroniusMode.BASIC_MOCK);
    }
    
    return sequence;
  }

  /**
   * Basic mock data for ultimate fallback
   */
  private getBasicMockData(): PowerData {
    const now = new Date();
    const hour = now.getHours();
    
    // Simple time-based solar production
    let solarProduction = 0;
    if (hour >= 7 && hour <= 19) {
      const noonDistance = Math.abs(hour - 12);
      solarProduction = Math.max(0, (5 - noonDistance) * 200); // Peak ~1000W at noon
    }
    
    // Typical household consumption
    const baseConsumption = hour >= 7 && hour <= 22 ? 800 : 400;
    const consumption = baseConsumption + (Math.random() * 400 - 200);
    
    const gridPower = consumption - solarProduction;
    
    return {
      solarProduction,
      consumption,
      gridPower,
      batteryPower: 0,
      timestamp: now.toISOString(),
      inverterTemp: 25 + Math.random() * 10,
      efficiency: 95 + Math.random() * 3
    };
  }

  /**
   * Test connection to real inverter
   */
  async testConnection(): Promise<boolean> {
    if (!this.realClient) {
      return false;
    }

    try {
      const isConnected = await this.realClient.testConnection();
      if (isConnected && this.currentMode !== FroniusMode.REAL) {
        console.log('Real inverter reconnected, switching back');
        this.currentMode = FroniusMode.REAL;
      }
      return isConnected;
    } catch (error) {
      console.warn('Real inverter connection test failed:', error);
      return false;
    }
  }

  /**
   * Update status tracking
   */
  private updateStatus(mode: FroniusMode, connected: boolean, error?: string): void {
    this.status = {
      mode,
      connected,
      lastUpdate: new Date(),
      errorCount: connected ? 0 : this.status.errorCount + 1,
      lastError: error
    };
  }

  /**
   * Start background connection monitoring
   */
  private startConnectionMonitoring(): void {
    setInterval(async () => {
      if (this.currentMode !== FroniusMode.REAL && this.realClient) {
        // Periodically test if real inverter is back online
        const isConnected = await this.testConnection();
        if (isConnected) {
          console.log('Real inverter is back online');
          this.currentMode = FroniusMode.REAL;
        }
      }
    }, this.connectionTestInterval);
  }

  /**
   * Manually set mode (for testing/debugging)
   */
  setMode(mode: FroniusMode): void {
    console.log(`Manually switching to ${mode} mode`);
    this.currentMode = mode;
    this.status.mode = mode;
  }

  /**
   * Get current status
   */
  getStatus(): FroniusStatus {
    return { ...this.status };
  }

  /**
   * Get available modes
   */
  getAvailableModes(): FroniusMode[] {
    const modes = [FroniusMode.ENHANCED_MOCK, FroniusMode.BASIC_MOCK];
    if (this.realClient) {
      modes.unshift(FroniusMode.REAL);
    }
    return modes;
  }

  /**
   * Force refresh connection status
   */
  async refreshStatus(): Promise<void> {
    if (this.realClient) {
      const connected = await this.testConnection();
      this.updateStatus(this.currentMode, connected);
    }
  }
}

// Export singleton instance
export const smartFroniusClient = new SmartFroniusClient(); 