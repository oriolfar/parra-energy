"""
Device Simulator Module

This module provides a base class for simulating electrical devices.
It can be used to simulate any device that can be turned on/off and has
a known power consumption.

The simulator tracks:
- Device state (on/off)
- Power consumption
- Uptime (how long the device has been on)
"""

from typing import Dict, Optional
import time

class Device:
    def __init__(self, name: str, power_consumption: float):
        """Initialize a simulated device.
        
        Args:
            name: Device name/identifier (e.g., "Water Heater", "Washing Machine")
            power_consumption: Power consumption in watts when turned on
        """
        self.name = name
        self.power_consumption = power_consumption
        self.is_on = False
        # Track when the device was last turned on/off
        self.last_state_change = time.time()
        
    def turn_on(self) -> bool:
        """Turn the device on.
        
        This method simulates turning on a physical device.
        It will only turn on if the device is currently off.
        
        Returns:
            bool: True if the device was turned on, False if it was already on
        """
        if not self.is_on:
            self.is_on = True
            self.last_state_change = time.time()
            print(f"{self.name} turned ON")
            return True
        return False
        
    def turn_off(self) -> bool:
        """Turn the device off.
        
        This method simulates turning off a physical device.
        It will only turn off if the device is currently on.
        
        Returns:
            bool: True if the device was turned off, False if it was already off
        """
        if self.is_on:
            self.is_on = False
            self.last_state_change = time.time()
            print(f"{self.name} turned OFF")
            return True
        return False
        
    def get_status(self) -> Dict:
        """Get the current status of the device.
        
        This method returns a dictionary containing all relevant
        information about the device's current state.
        
        Returns:
            Dict containing:
                - name: Device name
                - is_on: Current power state
                - power_consumption: Current power draw (0 if off)
                - uptime: How long the device has been on (0 if off)
        """
        return {
            'name': self.name,
            'is_on': self.is_on,
            'power_consumption': self.power_consumption if self.is_on else 0,
            'uptime': time.time() - self.last_state_change if self.is_on else 0
        } 