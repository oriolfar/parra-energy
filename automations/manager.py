from typing import Dict, List
from ..simulators.device import Device

class AutomationManager:
    def __init__(self):
        """Initialize the automation manager."""
        self.devices: List[Device] = []
        
    def add_device(self, device: Device) -> None:
        """Add a device to be managed.
        
        Args:
            device: Device instance to be managed
        """
        self.devices.append(device)
        
    def update(self, power_data: Dict) -> None:
        """Update device states based on current power data.
        
        Args:
            power_data: Dictionary containing P_PV, P_Load, and P_Grid values
        """
        # Calculate solar surplus
        solar_surplus = power_data['P_PV'] - power_data['P_Load']
        
        # Simple automation rule: turn on devices if there's enough surplus
        for device in self.devices:
            if not device.is_on and solar_surplus >= device.power_consumption:
                if device.turn_on():
                    solar_surplus -= device.power_consumption
            elif device.is_on and solar_surplus < device.power_consumption:
                device.turn_off()
                
    def get_status(self) -> Dict:
        """Get the current status of all managed devices.
        
        Returns:
            Dict containing status of all devices
        """
        return {
            'devices': [device.get_status() for device in self.devices]
        } 