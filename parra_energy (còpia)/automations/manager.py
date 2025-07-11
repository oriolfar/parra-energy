"""
Automation Manager Module

This module manages the automation of electrical devices based on solar power availability.
It implements rules to turn devices on/off based on the current solar surplus.

The manager:
- Tracks multiple devices
- Calculates available solar surplus
- Applies automation rules to control devices
- Provides status information about all managed devices
"""

from typing import Dict, List
from parra_energy.simulators.device import Device

class AutomationManager:
    def __init__(self):
        """Initialize the automation manager.
        
        Creates an empty list to store managed devices.
        """
        self.devices: List[Device] = []
        
    def add_device(self, device: Device) -> None:
        """Add a device to be managed.
        
        Args:
            device: Device instance to be managed (must be a Device or subclass)
        """
        self.devices.append(device)
        
    def update(self, power_data: Dict) -> None:
        """Update device states based on current power data.
        
        This method implements the core automation logic:
        1. Calculate available solar surplus
        2. Turn on devices if there's enough surplus
        3. Turn off devices if there's not enough surplus
        
        The current implementation uses a simple rule:
        - Turn on devices if solar surplus >= device power consumption
        - Turn off devices if solar surplus < device power consumption
        
        Args:
            power_data: Dictionary containing:
                - P_PV: Solar production in watts
                - P_Load: House consumption in watts
                - P_Grid: Grid power flow in watts
        """
        # Calculate solar surplus (production minus current load)
        ppv = power_data.get('P_PV')
        pload = power_data.get('P_Load')
        if ppv is None:
            ppv = 0
        if pload is None:
            pload = 0
        solar_surplus = ppv - pload
        
        # Simple automation rule: turn on devices if there's enough surplus
        for device in self.devices:
            if not device.is_on and solar_surplus >= device.power_consumption:
                # Turn on device if we have enough surplus
                if device.turn_on():
                    solar_surplus -= device.power_consumption
            elif device.is_on and solar_surplus < device.power_consumption:
                # Turn off device if we don't have enough surplus
                device.turn_off()
                
    def get_status(self) -> Dict:
        """Get the current status of all managed devices.
        
        Returns:
            Dict containing:
                - devices: List of device status dictionaries
        """
        return {
            'devices': [device.get_status() for device in self.devices]
        } 