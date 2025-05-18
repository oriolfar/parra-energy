from typing import Dict, Optional
import time

class Device:
    def __init__(self, name: str, power_consumption: float):
        """Initialize a simulated device.
        
        Args:
            name: Device name/identifier
            power_consumption: Power consumption in watts when turned on
        """
        self.name = name
        self.power_consumption = power_consumption
        self.is_on = False
        self.last_state_change = time.time()
        
    def turn_on(self) -> bool:
        """Turn the device on.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_on:
            self.is_on = True
            self.last_state_change = time.time()
            print(f"{self.name} turned ON")
            return True
        return False
        
    def turn_off(self) -> bool:
        """Turn the device off.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if self.is_on:
            self.is_on = False
            self.last_state_change = time.time()
            print(f"{self.name} turned OFF")
            return True
        return False
        
    def get_status(self) -> Dict:
        """Get the current status of the device.
        
        Returns:
            Dict containing device status information
        """
        return {
            'name': self.name,
            'is_on': self.is_on,
            'power_consumption': self.power_consumption if self.is_on else 0,
            'uptime': time.time() - self.last_state_change if self.is_on else 0
        } 