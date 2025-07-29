/**
 * Automation Manager - Smart Solar-Based Device Control
 * ====================================================
 * 
 * Intelligent automation of electrical devices based on real-time solar
 * power availability and energy surplus calculations.
 * Based on the Python automation manager implementation.
 */

import { DatabaseManager } from '@repo/database';
import type {
  Device,
  DevicePriority,
  DeviceStatus,
  DeviceCategory,
  AutomationEvent,
  AutomationStats,
  DeviceControl,
  PowerData,
} from '@repo/types';

export class AutomationManager {
  private db: DatabaseManager;
  private devices: Map<string, Device>;
  private automationStats: AutomationStats;
  private lastSurplus: number = 0;
  private minSurplusThreshold: number = 100; // Minimum watts to trigger automation

  constructor(dbPath?: string) {
    this.db = new DatabaseManager(dbPath);
    this.devices = new Map();
    this.automationStats = {
      total_automated_energy: 0,
      automation_events: 0,
      last_surplus: 0,
      active_devices: 0,
      energy_saved_today: 0,
    };
    this.initializeDefaultDevices();
  }

  /**
   * Initialize default devices for a typical Spanish home
   */
  private async initializeDefaultDevices(): Promise<void> {
    const defaultDevices: Omit<Device, 'created_at' | 'updated_at'>[] = [
      {
        id: 'water-heater',
        name: 'Water Heater',
        power_consumption: 2000,
        priority: 'high',
        category: 'heating',
        status: 'off',
        is_automated: true,
        description: 'Electric water heater for domestic hot water',
        location: 'Utility room',
        manual_override: false,
      },
      {
        id: 'washing-machine',
        name: 'Washing Machine',
        power_consumption: 1200,
        priority: 'medium',
        category: 'appliance',
        status: 'off',
        is_automated: true,
        description: 'Front-loading washing machine',
        location: 'Utility room',
        manual_override: false,
      },
      {
        id: 'dishwasher',
        name: 'Dishwasher',
        power_consumption: 1800,
        priority: 'medium',
        category: 'appliance',
        status: 'off',
        is_automated: true,
        description: 'Built-in dishwasher',
        location: 'Kitchen',
        manual_override: false,
      },
      {
        id: 'pool-pump',
        name: 'Pool Pump',
        power_consumption: 800,
        priority: 'low',
        category: 'pool',
        status: 'off',
        is_automated: true,
        description: 'Swimming pool circulation pump',
        location: 'Pool area',
        manual_override: false,
      },
      {
        id: 'ev-charger',
        name: 'EV Charger',
        power_consumption: 3200,
        priority: 'medium',
        category: 'ev_charging',
        status: 'off',
        is_automated: true,
        description: 'Electric vehicle charging station',
        location: 'Garage',
        manual_override: false,
      },
      {
        id: 'air-conditioning',
        name: 'Air Conditioning',
        power_consumption: 2500,
        priority: 'essential',
        category: 'heating',
        status: 'auto',
        is_automated: false, // Usually manually controlled for comfort
        description: 'Central air conditioning system',
        location: 'House',
        manual_override: true,
      },
    ];

    // Load devices into database and memory
    for (const device of defaultDevices) {
      await this.db.insertDevice(device);
      this.devices.set(device.id, {
        ...device,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });
    }
  }

  /**
   * Execute smart automation logic based on current energy data
   */
  async update(powerData: PowerData): Promise<void> {
    const solarProduction = powerData.P_PV;
    const houseConsumption = powerData.P_Load;
    const surplus = solarProduction - houseConsumption;
    
    this.lastSurplus = surplus;
    this.automationStats.last_surplus = surplus;

    // Only perform automation if surplus is significant
    if (Math.abs(surplus) < this.minSurplusThreshold) {
      return;
    }

    // Get current hour for time-based decisions
    const currentHour = new Date().getHours();
    
    // Apply automation rules based on surplus and priority
    if (surplus > 0) {
      await this.handleSolarSurplus(surplus, currentHour);
    } else {
      await this.handleEnergyDeficit(Math.abs(surplus), currentHour);
    }

    // Update active devices count
    this.automationStats.active_devices = Array.from(this.devices.values())
      .filter(device => device.status === 'on' && device.is_automated).length;
  }

  /**
   * Handle situations with solar energy surplus
   */
  private async handleSolarSurplus(surplus: number, currentHour: number): Promise<void> {
    // Get available devices sorted by priority and power consumption
    const availableDevices = this.getAvailableDevicesForActivation();
    
    let remainingSurplus = surplus;
    
    for (const device of availableDevices) {
      // Check if device can be activated based on surplus and time constraints
      if (this.canActivateDevice(device, remainingSurplus, currentHour)) {
        await this.activateDevice(device.id, `Solar surplus: ${Math.round(surplus)}W`);
        remainingSurplus -= device.power_consumption;
        
        // If remaining surplus is too small, stop activating devices
        if (remainingSurplus < this.minSurplusThreshold) {
          break;
        }
      }
    }
  }

  /**
   * Handle situations with energy deficit (consuming more than producing)
   */
  private async handleEnergyDeficit(deficit: number, currentHour: number): Promise<void> {
    // Get active automated devices sorted by priority (lowest priority first)
    const activeDevices = this.getActiveAutomatedDevices();
    
    let remainingDeficit = deficit;
    
    for (const device of activeDevices) {
      // Deactivate non-essential devices during high deficit
      if (this.shouldDeactivateDevice(device, remainingDeficit, currentHour)) {
        await this.deactivateDevice(device.id, `Energy deficit: ${Math.round(deficit)}W`);
        remainingDeficit -= device.power_consumption;
        
        // If deficit is manageable, stop deactivating devices
        if (remainingDeficit < this.minSurplusThreshold) {
          break;
        }
      }
    }
  }

  /**
   * Get available devices for activation, sorted by priority and efficiency
   */
  private getAvailableDevicesForActivation(): Device[] {
    const priorityOrder: Record<DevicePriority, number> = {
      'essential': 4,
      'high': 3,
      'medium': 2,
      'low': 1,
    };

    return Array.from(this.devices.values())
      .filter(device => 
        device.status === 'off' && 
        device.is_automated && 
        !device.manual_override
      )
      .sort((a, b) => {
        // Sort by priority first, then by power consumption (lower consumption first)
        const priorityDiff = priorityOrder[b.priority] - priorityOrder[a.priority];
        if (priorityDiff !== 0) return priorityDiff;
        return a.power_consumption - b.power_consumption;
      });
  }

  /**
   * Get active automated devices, sorted by priority (lowest first for deactivation)
   */
  private getActiveAutomatedDevices(): Device[] {
    const priorityOrder: Record<DevicePriority, number> = {
      'essential': 4,
      'high': 3,
      'medium': 2,
      'low': 1,
    };

    return Array.from(this.devices.values())
      .filter(device => 
        device.status === 'on' && 
        device.is_automated && 
        !device.manual_override
      )
      .sort((a, b) => {
        // Sort by priority (lowest first for deactivation)
        return priorityOrder[a.priority] - priorityOrder[b.priority];
      });
  }

  /**
   * Check if a device can be activated based on surplus and constraints
   */
  private canActivateDevice(device: Device, surplus: number, currentHour: number): boolean {
    // Device must consume less than available surplus
    if (device.power_consumption > surplus) {
      return false;
    }

    // Time-based constraints
    switch (device.category) {
      case 'appliance':
        // Appliances are best used during peak solar hours
        return currentHour >= 10 && currentHour <= 16;
      
      case 'heating':
        // Water heating can be done anytime with surplus
        return true;
      
      case 'pool':
        // Pool pump should run during day hours
        return currentHour >= 8 && currentHour <= 18;
      
      case 'ev_charging':
        // EV charging can happen anytime, but prefer daytime
        return surplus > 2000; // Only if significant surplus
      
      default:
        return true;
    }
  }

  /**
   * Check if a device should be deactivated during energy deficit
   */
  private shouldDeactivateDevice(device: Device, deficit: number, currentHour: number): boolean {
    // Never deactivate essential devices
    if (device.priority === 'essential') {
      return false;
    }

    // Deactivate low priority devices first
    if (device.priority === 'low') {
      return true;
    }

    // Deactivate medium priority devices if deficit is significant
    if (device.priority === 'medium' && deficit > 1000) {
      return true;
    }

    // Time-based deactivation
    if (currentHour >= 18 && currentHour <= 22) {
      // Evening peak hours - be more aggressive about deactivation
      return device.priority !== 'high';
    }

    return false;
  }

  /**
   * Activate a device and log the event
   */
  async activateDevice(deviceId: string, reason: string): Promise<boolean> {
    const device = this.devices.get(deviceId);
    if (!device || device.status === 'on' || device.manual_override) {
      return false;
    }

    try {
      // Update device status
      device.status = 'on';
      device.updated_at = new Date().toISOString();
      this.devices.set(deviceId, device);
      
      // Update database
      await this.db.insertDevice(device);

      // Log automation event
      const event: AutomationEvent = {
        id: `evt-${Date.now()}-${deviceId}`,
        device_id: deviceId,
        event_type: 'turn_on',
        trigger_reason: reason,
        surplus_watts: this.lastSurplus,
        timestamp: new Date().toISOString(),
        success: true,
      };
      
      await this.db.insertAutomationEvent(event);
      
      // Update statistics
      this.automationStats.automation_events++;
      this.automationStats.energy_saved_today += device.power_consumption / 1000; // Convert to kWh

      console.log(`✅ Activated ${device.name}: ${reason}`);
      return true;
    } catch (error) {
      console.error(`❌ Failed to activate ${device.name}:`, error);
      return false;
    }
  }

  /**
   * Deactivate a device and log the event
   */
  async deactivateDevice(deviceId: string, reason: string): Promise<boolean> {
    const device = this.devices.get(deviceId);
    if (!device || device.status === 'off' || device.manual_override) {
      return false;
    }

    try {
      // Update device status
      device.status = 'off';
      device.updated_at = new Date().toISOString();
      this.devices.set(deviceId, device);
      
      // Update database
      await this.db.insertDevice(device);

      // Log automation event
      const event: AutomationEvent = {
        id: `evt-${Date.now()}-${deviceId}`,
        device_id: deviceId,
        event_type: 'turn_off',
        trigger_reason: reason,
        surplus_watts: this.lastSurplus,
        timestamp: new Date().toISOString(),
        success: true,
      };
      
      await this.db.insertAutomationEvent(event);
      
      // Update statistics
      this.automationStats.automation_events++;

      console.log(`⏹️ Deactivated ${device.name}: ${reason}`);
      return true;
    } catch (error) {
      console.error(`❌ Failed to deactivate ${device.name}:`, error);
      return false;
    }
  }

  /**
   * Manually control a device (override automation)
   */
  async controlDevice(control: DeviceControl): Promise<boolean> {
    const device = this.devices.get(control.device_id);
    if (!device) {
      return false;
    }

    const newStatus: DeviceStatus = control.action === 'turn_on' ? 'on' : 'off';
    
    // Update device
    device.status = newStatus;
    device.manual_override = control.manual;
    device.updated_at = new Date().toISOString();
    this.devices.set(control.device_id, device);
    
    // Update database
    await this.db.insertDevice(device);

    // Log manual control event
    const event: AutomationEvent = {
      id: `evt-${Date.now()}-${control.device_id}`,
      device_id: control.device_id,
      event_type: control.action === 'turn_on' ? 'turn_on' : 'turn_off',
      trigger_reason: control.manual ? 'Manual control' : 'Automated control',
      surplus_watts: this.lastSurplus,
      timestamp: new Date().toISOString(),
      success: true,
    };
    
    await this.db.insertAutomationEvent(event);

    return true;
  }

  /**
   * Get all managed devices
   */
  getDevices(): Device[] {
    return Array.from(this.devices.values());
  }

  /**
   * Get device by ID
   */
  getDevice(deviceId: string): Device | undefined {
    return this.devices.get(deviceId);
  }

  /**
   * Get automation statistics
   */
  getAutomationStats(): AutomationStats {
    return { ...this.automationStats };
  }

  /**
   * Get recent automation events
   */
  async getRecentEvents(limit: number = 50): Promise<AutomationEvent[]> {
    return await this.db.getAutomationEvents(undefined, limit);
  }

  /**
   * Reset manual overrides for all devices
   */
  async clearManualOverrides(): Promise<void> {
    for (const device of this.devices.values()) {
      if (device.manual_override) {
        device.manual_override = false;
        device.updated_at = new Date().toISOString();
        await this.db.insertDevice(device);
      }
    }
  }

  /**
   * Get automation recommendations based on current conditions
   */
  getAutomationRecommendations(powerData: PowerData): Array<{
    device_id: string;
    device_name: string;
    action: 'activate' | 'deactivate' | 'schedule';
    reason: string;
    potential_savings: number;
  }> {
    const recommendations = [];
    const surplus = powerData.P_PV - powerData.P_Load;
    const currentHour = new Date().getHours();

    // Recommendations for surplus energy
    if (surplus > 500) {
      const availableDevices = this.getAvailableDevicesForActivation();
      
      for (const device of availableDevices.slice(0, 3)) { // Top 3 recommendations
        if (device.power_consumption <= surplus) {
          recommendations.push({
            device_id: device.id,
            device_name: device.name,
            action: 'activate' as const,
            reason: `Excess solar: ${Math.round(surplus)}W available`,
            potential_savings: (device.power_consumption / 1000) * 0.12, // €0.12 per kWh
          });
        }
      }
    }

    // Recommendations for high consumption periods
    if (surplus < -200) {
      const activeDevices = this.getActiveAutomatedDevices();
      
      for (const device of activeDevices.slice(0, 2)) { // Top 2 recommendations
        if (device.priority !== 'essential') {
          recommendations.push({
            device_id: device.id,
            device_name: device.name,
            action: 'deactivate' as const,
            reason: `High consumption period - reduce grid import`,
            potential_savings: (device.power_consumption / 1000) * 0.12,
          });
        }
      }
    }

    return recommendations;
  }

  /**
   * Set automation configuration
   */
  setConfiguration(config: {
    minSurplusThreshold?: number;
    enabledCategories?: DeviceCategory[];
  }): void {
    if (config.minSurplusThreshold !== undefined) {
      this.minSurplusThreshold = config.minSurplusThreshold;
    }
    
    if (config.enabledCategories) {
      // Enable/disable devices based on categories
      for (const device of this.devices.values()) {
        device.is_automated = config.enabledCategories.includes(device.category);
      }
    }
  }
}

export default AutomationManager; 