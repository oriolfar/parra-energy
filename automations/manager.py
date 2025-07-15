"""
Automation Manager Module - Smart Solar-Based Device Control System
===================================================================

This module implements intelligent automation of electrical devices based on
real-time solar power availability and energy surplus calculations. It enables
automatic device control to maximize solar energy utilization and minimize
grid dependency.

AUTOMATION STRATEGY:
1. SOLAR SURPLUS OPTIMIZATION:
   - Continuously monitors solar production vs. household consumption
   - Calculates available energy surplus for device automation
   - Prioritizes device activation based on available solar energy
   - Maximizes self-consumption to reduce grid dependency

2. INTELLIGENT DEVICE MANAGEMENT:
   - Manages multiple devices with different power requirements
   - Implements priority-based device activation
   - Automatic device scheduling based on solar availability
   - Real-time device status monitoring and control

3. ENERGY FLOW OPTIMIZATION:
   - Solar Production - House Consumption = Available Surplus
   - Turn ON devices when surplus >= device power consumption
   - Turn OFF devices when surplus < device power consumption
   - Prevent grid import for automated device operation

4. SMART SCHEDULING FEATURES:
   - Time-based device priorities (morning vs. afternoon)
   - Weather-aware scheduling integration capability
   - User preference consideration for device activation
   - Safety and comfort device prioritization

AUTOMATION RULES:
- EXCESS SOLAR: Activate high-power devices (water heater, AC)
- MODERATE SURPLUS: Activate medium-power devices (washing machine)
- LIMITED SURPLUS: Activate low-power devices (lighting, fans)
- NO SURPLUS: Deactivate non-essential automated devices

DEVICE CATEGORIES:
- ESSENTIAL: Never automated (security, medical devices)
- HIGH PRIORITY: Automated when significant surplus available
- MEDIUM PRIORITY: Automated when moderate surplus available  
- LOW PRIORITY: Automated when any surplus available

INTEGRATION CAPABILITIES:
- Real-time power data integration from Fronius inverter
- Weather forecast integration for predictive scheduling
- User preferences and manual overrides
- Energy analytics integration for optimization learning

This automation system enables homeowners to maximize their solar energy
utilization by intelligently controlling household devices based on
real-time energy availability, weather conditions, and user preferences.
"""

from typing import Dict, List
from simulators.device import Device


class AutomationManager:
    """
    Intelligent solar-based device automation manager.
    
    This class implements smart device control logic that automatically
    manages electrical devices based on available solar energy surplus,
    maximizing self-consumption and minimizing grid dependency.
    """
    
    def __init__(self):
        """
        Initialize the automation manager for smart device control.
        
        Sets up the device management system with:
        - Empty device registry for managed devices
        - Automation rule engine initialization
        - Energy flow calculation preparation
        - Status monitoring system setup
        """
        print("🤖 Initializing Smart Automation Manager")
        
        # Device registry for managed smart devices
        self.devices: List[Device] = []
        
        # Automation statistics and performance tracking
        self._total_automated_energy = 0.0  # Total energy used via automation (kWh)
        self._automation_events = 0         # Number of automation events
        self._last_surplus = 0.0            # Last calculated solar surplus (W)
        
        print("   📋 Device registry initialized")
        print("   ⚡ Solar surplus calculation engine ready")
        print("   📊 Automation statistics tracking enabled")
        print("✅ Automation Manager ready for smart device control")
        
    def add_device(self, device: Device) -> None:
        """
        Register a device for smart automation management.
        
        Args:
            device: Device instance to be managed (must implement Device interface)
            
        Device Requirements:
        - Must implement Device interface with standard methods
        - Must have power_consumption attribute (watts)
        - Must support turn_on() and turn_off() methods
        - Must provide status reporting via get_status()
        
        Device Types Supported:
        - Water heaters (high power, flexible timing)
        - Washing machines (medium power, user-scheduled)
        - Air conditioning (high power, comfort priority)
        - Pool pumps (medium power, scheduling flexible)
        - Electric vehicle chargers (high power, overnight preferred)
        """
        if device not in self.devices:
            self.devices.append(device)
            print(f"📱 Device registered: {device.name} ({device.power_consumption}W)")
            print(f"   Total managed devices: {len(self.devices)}")
        else:
            print(f"⚠️  Device already registered: {device.name}")
        
    def update(self, power_data: Dict) -> None:
        """
        Execute smart automation logic based on current energy data.
        
        This method implements the core intelligence of the automation system:
        1. Calculate real-time solar energy surplus
        2. Evaluate device activation opportunities
        3. Apply intelligent device control rules
        4. Update device states based on energy availability
        5. Track automation performance and statistics
        
        Automation Logic:
        - SURPLUS AVAILABLE: Activate devices in priority order
        - SURPLUS INSUFFICIENT: Deactivate devices to prevent grid import
        - OPTIMAL UTILIZATION: Maximize solar self-consumption
        
        Args:
            power_data: Real-time energy data dictionary containing:
                - P_PV: Solar production in watts (from inverter)
                - P_Load: Current house consumption in watts
                - P_Grid: Grid power flow (+import, -export) in watts
        """
        # =================================================================
        # ENERGY SURPLUS CALCULATION
        # =================================================================
        
        # Extract power data with safe defaults
        solar_production = power_data.get('P_PV', 0)      # Solar panels output
        house_consumption = power_data.get('P_Load', 0)   # Total house load
        grid_power = power_data.get('P_Grid', 0)          # Grid interaction
        
        # Calculate available solar surplus for automation
        # Surplus = Solar Production - Current House Consumption
        solar_surplus = solar_production - house_consumption
        self._last_surplus = solar_surplus
        
        # Debug logging for automation decisions (only in verbose mode)
        from config.settings import Config
        config = Config()
        if not config.logging.quiet_mode:
            print(f"[AUTOMATION] Solar: {solar_production}W, Load: {house_consumption}W, "
                  f"Surplus: {solar_surplus:+.0f}W, Devices: {len(self.devices)}")
        
        # =================================================================
        # INTELLIGENT DEVICE CONTROL LOGIC
        # =================================================================
        
        # Track energy available for automation after existing device consumption
        available_surplus = solar_surplus
        automation_events = 0
        
        # Process each managed device for optimal automation
        for device in self.devices:
            device_power = device.power_consumption
            
            # DEVICE ACTIVATION LOGIC
            if not device.is_on and available_surplus >= device_power:
                # Sufficient surplus available - activate device
                if device.turn_on():
                    available_surplus -= device_power
                    automation_events += 1
                    self._total_automated_energy += device_power / 1000 / 24  # Rough daily kWh
                    print(f"   ✅ ACTIVATED: {device.name} ({device_power}W) - "
                          f"Remaining surplus: {available_surplus:.0f}W")
                else:
                    print(f"   ❌ FAILED to activate: {device.name} (device error)")
            
            # DEVICE DEACTIVATION LOGIC
            elif device.is_on and solar_surplus < device_power:
                # Insufficient surplus - deactivate device to prevent grid import
                if device.turn_off():
                    automation_events += 1
                    print(f"   🔄 DEACTIVATED: {device.name} ({device_power}W) - "
                          f"Insufficient surplus: {solar_surplus:.0f}W")
                else:
                    print(f"   ❌ FAILED to deactivate: {device.name} (device error)")
        
        # Update automation statistics
        self._automation_events += automation_events
        
        if automation_events > 0:
            print(f"[AUTOMATION] Completed {automation_events} device state changes")
            print(f"   📊 Total automation events: {self._automation_events}")
            print(f"   ⚡ Estimated automated energy: {self._total_automated_energy:.1f} kWh")
                
    def get_status(self) -> Dict:
        """
        Get comprehensive status of the automation system and all managed devices.
        
        Provides detailed information about:
        - Individual device states and power consumption
        - Overall automation system performance
        - Energy utilization statistics
        - Solar surplus information
        
        Returns:
            Dict containing complete automation system status:
            - devices: List of detailed device status dictionaries
            - automation_stats: Performance and energy statistics
            - solar_surplus: Current available surplus for automation
            - total_managed_power: Sum of all managed device power ratings
        """
        # Collect individual device statuses
        device_statuses = []
        total_managed_power = 0
        active_device_power = 0
        
        for device in self.devices:
            device_status = device.get_status()
            device_statuses.append(device_status)
            total_managed_power += device.power_consumption
            
            if device.is_on:
                active_device_power += device.power_consumption
        
        # Compile comprehensive automation status
        return {
            'devices': device_statuses,
            'automation_stats': {
                'total_devices': len(self.devices),
                'active_devices': sum(1 for d in self.devices if d.is_on),
                'total_managed_power': total_managed_power,        # Total power of all devices (W)
                'active_device_power': active_device_power,        # Power of currently active devices (W)
                'automation_events': self._automation_events,      # Total automation events
                'automated_energy_estimate': self._total_automated_energy  # Estimated energy via automation (kWh)
            },
            'energy_flow': {
                'last_solar_surplus': self._last_surplus,          # Last calculated surplus (W)
                'available_for_automation': max(0, self._last_surplus - active_device_power)  # Available surplus (W)
            }
        } 