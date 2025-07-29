/**
 * Automation Types for Parra Energy System
 * ========================================
 * 
 * TypeScript interfaces for smart device automation and control
 * based on solar surplus availability.
 */

export type DevicePriority = 'essential' | 'high' | 'medium' | 'low';
export type DeviceStatus = 'on' | 'off' | 'auto' | 'manual';
export type DeviceCategory = 'heating' | 'appliance' | 'lighting' | 'ev_charging' | 'pool' | 'other';

export interface Device {
  id: string;
  name: string;
  power_consumption: number;
  priority: DevicePriority;
  category: DeviceCategory;
  status: DeviceStatus;
  is_automated: boolean;
  description?: string;
  location?: string;
  manual_override?: boolean;
  schedule?: DeviceSchedule;
  created_at: string;
  updated_at: string;
}

export interface DeviceSchedule {
  enabled: boolean;
  start_time?: string;
  end_time?: string;
  days_of_week?: number[];
  min_surplus_required?: number;
}

export interface AutomationEvent {
  id: string;
  device_id: string;
  event_type: 'turn_on' | 'turn_off' | 'schedule_start' | 'schedule_end' | 'manual_override';
  trigger_reason: string;
  surplus_watts: number;
  timestamp: string;
  success: boolean;
  error_message?: string;
}

export interface AutomationRule {
  id: string;
  name: string;
  condition: AutomationCondition;
  action: AutomationAction;
  enabled: boolean;
  priority: number;
}

export interface AutomationCondition {
  type: 'surplus_threshold' | 'time_range' | 'weather_condition' | 'device_state';
  value: any;
  operator: 'gt' | 'lt' | 'eq' | 'between';
}

export interface AutomationAction {
  type: 'turn_on' | 'turn_off' | 'schedule' | 'notify';
  device_ids: string[];
  parameters?: Record<string, any>;
}

export interface AutomationStats {
  total_automated_energy: number;
  automation_events: number;
  last_surplus: number;
  active_devices: number;
  energy_saved_today: number;
}

export interface DeviceControl {
  device_id: string;
  action: 'turn_on' | 'turn_off' | 'toggle';
  manual: boolean;
  duration?: number;
} 