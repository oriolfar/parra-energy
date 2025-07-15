"""
Unit Tests for Device Simulator Class
=====================================

Tests for the device simulation functionality used in the
Parra Energy automation system.
"""

import pytest
import sys
import os

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from simulators.device import Device


class TestDeviceInitialization:
    """Test device initialization and basic properties."""
    
    def test_device_initialization_valid_params(self):
        """Test device initialization with valid parameters."""
        device = Device("Test Device", 1000)
        assert device.name == "Test Device"
        assert device.power_consumption == 1000
        assert not device.is_on
        assert device.device_type == "unknown"
        assert device.priority == 5
    
    def test_device_initialization_with_optional_params(self):
        """Test device initialization with all parameters."""
        device = Device(
            name="Water Heater",
            power_consumption=2500,
            device_type="water_heater",
            priority=8,
            location="Basement"
        )
        assert device.name == "Water Heater"
        assert device.power_consumption == 2500
        assert device.device_type == "water_heater"
        assert device.priority == 8
        assert device.location == "Basement"
    
    def test_device_initialization_edge_cases(self):
        """Test device initialization with edge case values."""
        # Minimum values
        device_min = Device("Min Device", 1)
        assert device_min.power_consumption == 1
        
        # Large values
        device_large = Device("Large Device", 15000)
        assert device_large.power_consumption == 15000


class TestDeviceOperations:
    """Test device on/off operations and state management."""
    
    def test_device_turn_on(self):
        """Test turning device on."""
        device = Device("Test Device", 1000)
        
        # Initially off
        assert not device.is_on
        
        # Turn on should succeed
        assert device.turn_on()
        assert device.is_on
        
        # Turn on again should fail (already on)
        assert not device.turn_on()
        assert device.is_on
    
    def test_device_turn_off(self):
        """Test turning device off."""
        device = Device("Test Device", 1000)
        device.turn_on()
        
        # Should be on
        assert device.is_on
        
        # Turn off should succeed
        assert device.turn_off()
        assert not device.is_on
        
        # Turn off again should fail (already off)
        assert not device.turn_off()
        assert not device.is_on
    
    def test_device_toggle(self):
        """Test device toggle functionality."""
        device = Device("Test Device", 1000)
        
        # Start off, toggle to on
        device.toggle()
        assert device.is_on
        
        # Toggle back to off
        device.toggle()
        assert not device.is_on


class TestDeviceStatus:
    """Test device status reporting and information."""
    
    def test_device_status_off(self):
        """Test device status when off."""
        device = Device("Test Device", 1000)
        status = device.get_status()
        
        assert status['name'] == "Test Device"
        assert status['power_consumption'] == 1000
        assert status['is_on'] is False
        assert status['current_consumption'] == 0
        assert status['device_type'] == "unknown"
        assert status['priority'] == 5
    
    def test_device_status_on(self):
        """Test device status when on."""
        device = Device("Test Device", 1000)
        device.turn_on()
        status = device.get_status()
        
        assert status['name'] == "Test Device"
        assert status['is_on'] is True
        assert status['current_consumption'] == 1000
    
    def test_device_current_consumption(self):
        """Test current consumption calculation."""
        device = Device("Test Device", 2500)
        
        # Off = 0 consumption
        assert device.get_current_consumption() == 0
        
        # On = full consumption
        device.turn_on()
        assert device.get_current_consumption() == 2500


class TestDeviceValidation:
    """Test device parameter validation and error handling."""
    
    def test_invalid_name(self):
        """Test device creation with invalid names."""
        with pytest.raises((ValueError, TypeError)):
            Device("", 1000)  # Empty name
        
        with pytest.raises((ValueError, TypeError)):
            Device(None, 1000)  # None name
    
    def test_invalid_power_consumption(self):
        """Test device creation with invalid power consumption."""
        with pytest.raises((ValueError, TypeError)):
            Device("Test", -100)  # Negative power
        
        with pytest.raises((ValueError, TypeError)):
            Device("Test", "invalid")  # Non-numeric power
        
        with pytest.raises((ValueError, TypeError)):
            Device("Test", None)  # None power
    
    def test_invalid_priority(self):
        """Test device creation with invalid priority."""
        with pytest.raises((ValueError, TypeError)):
            Device("Test", 1000, priority=-1)  # Below range
        
        with pytest.raises((ValueError, TypeError)):
            Device("Test", 1000, priority=11)  # Above range


class TestDeviceAutomation:
    """Test device automation-related functionality."""
    
    def test_automation_priority_comparison(self):
        """Test device priority comparison for automation."""
        high_priority = Device("Critical", 1000, priority=9)
        low_priority = Device("Optional", 500, priority=2)
        
        assert high_priority.priority > low_priority.priority
    
    def test_device_categorization(self):
        """Test device categorization by type."""
        water_heater = Device("Water Heater", 2500, device_type="water_heater")
        ev_charger = Device("EV Charger", 7000, device_type="ev_charger")
        lighting = Device("LED Lights", 50, device_type="lighting")
        
        assert water_heater.device_type == "water_heater"
        assert ev_charger.device_type == "ev_charger"
        assert lighting.device_type == "lighting"
    
    def test_energy_consumption_calculation(self):
        """Test energy consumption over time calculation."""
        device = Device("Test Device", 1000)  # 1kW device
        
        # Device off = 0 energy
        energy_off = device.calculate_energy_consumption(hours=1)
        assert energy_off == 0
        
        # Device on = power * time
        device.turn_on()
        energy_1h = device.calculate_energy_consumption(hours=1)
        assert energy_1h == 1.0  # 1kWh
        
        energy_30min = device.calculate_energy_consumption(hours=0.5)
        assert energy_30min == 0.5  # 0.5kWh


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 