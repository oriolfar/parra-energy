/**
 * Fronius Inverter Client Service
 * ==============================
 * 
 * TypeScript implementation of the Fronius solar inverter API client.
 * Based on the Python implementation with real inverter communication.
 */

import axios from 'axios';
import type { PowerData } from '@repo/types';

export interface FroniusApiResponse {
  Body: {
    Data: {
      PAC?: {
        Values: {
          '1': number;
        };
      };
      P_Load?: {
        Values: {
          '1': number;
        };
      };
      P_Grid?: {
        Values: {
          '1': number;
        };
      };
      P_PV?: {
        Values: {
          '1': number;
        };
      };
    };
  };
  Head: {
    Status: {
      Code: number;
      Reason: string;
    };
    TimeStamp: string;
  };
}

export class FroniusClient {
  private host: string;
  private timeout: number;
  private deviceId: string;

  constructor(host: string = '192.168.1.128', timeout: number = 10000) {
    this.host = host;
    this.timeout = timeout;
    this.deviceId = '1'; // Default device ID for Fronius inverters
  }

  /**
   * Test connection to the Fronius inverter
   */
  async testConnection(): Promise<boolean> {
    try {
      const response = await axios.get(
        `http://${this.host}/solar_api/v1/GetInverterInfo.cgi`,
        { timeout: this.timeout }
      );
      return response.status === 200;
    } catch (error) {
      console.log(`Fronius connection test failed: ${error}`);
      return false;
    }
  }

  /**
   * Get current power data from the Fronius inverter
   */
  async getCurrentData(): Promise<PowerData> {
    try {
      const response = await axios.get<FroniusApiResponse>(
        `http://${this.host}/solar_api/v1/GetPowerFlowRealtimeData.fcgi`,
        { timeout: this.timeout }
      );

      if (response.data.Head.Status.Code !== 0) {
        throw new Error(`Fronius API error: ${response.data.Head.Status.Reason}`);
      }

      const data = response.data.Body.Data;
      
      // Extract power values with defaults
      const P_PV = data.P_PV?.Values?.['1'] || 0;
      const P_Load = data.P_Load?.Values?.['1'] || 0;
      const P_Grid = data.P_Grid?.Values?.['1'] || 0;

      return {
        P_PV: Math.max(0, P_PV), // Solar production (always positive)
        P_Load: Math.max(0, Math.abs(P_Load)), // House consumption (always positive)
        P_Grid: P_Grid, // Grid power (positive = import, negative = export)
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      console.error(`Failed to get Fronius data: ${error}`);
      throw new Error(`Fronius communication failed: ${error}`);
    }
  }

  /**
   * Get inverter information
   */
  async getInverterInfo(): Promise<any> {
    try {
      const response = await axios.get(
        `http://${this.host}/solar_api/v1/GetInverterInfo.cgi`,
        { timeout: this.timeout }
      );
      return response.data;
    } catch (error) {
      console.error(`Failed to get inverter info: ${error}`);
      throw error;
    }
  }

  /**
   * Get historical power data (if available)
   */
  async getHistoricalData(date: string): Promise<any> {
    try {
      const response = await axios.get(
        `http://${this.host}/solar_api/v1/GetArchiveData.cgi?Scope=Device&DeviceId=${this.deviceId}&StartDate=${date}&EndDate=${date}`,
        { timeout: this.timeout }
      );
      return response.data;
    } catch (error) {
      console.error(`Failed to get historical data: ${error}`);
      throw error;
    }
  }

  /**
   * Check if the inverter is currently producing power
   */
  async isProducing(): Promise<boolean> {
    try {
      const data = await this.getCurrentData();
      return data.P_PV > 0;
    } catch (error) {
      return false;
    }
  }

  /**
   * Get system status and health information
   */
  async getSystemStatus(): Promise<{
    isOnline: boolean;
    isProducing: boolean;
    lastUpdate: string;
    errorCount: number;
  }> {
    try {
      const isOnline = await this.testConnection();
      const isProducing = isOnline ? await this.isProducing() : false;
      
      return {
        isOnline,
        isProducing,
        lastUpdate: new Date().toISOString(),
        errorCount: 0,
      };
    } catch (error) {
      return {
        isOnline: false,
        isProducing: false,
        lastUpdate: new Date().toISOString(),
        errorCount: 1,
      };
    }
  }
}

export default FroniusClient; 