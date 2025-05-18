import pytest
from simulators.device import Device

def test_device_initialization():
    """Test device initialization with correct values."""
    device = Device("Test Device", 1000)
    assert device.name == "Test Device"
    assert device.power_consumption == 1000
    assert not device.is_on

def test_device_turn_on():
    """Test turning device on."""
    device = Device("Test Device", 1000)
    assert device.turn_on()
    assert device.is_on
    assert not device.turn_on()  # Should return False when already on

def test_device_turn_off():
    """Test turning device off."""
    device = Device("Test Device", 1000)
    device.turn_on()
    assert device.turn_off()
    assert not device.is_on
    assert not device.turn_off()  # Should return False when already off

def test_device_status():
    """Test device status reporting."""
    device = Device("Test Device", 1000)
    status = device.get_status()
    assert status['name'] == "Test Device"
    assert status['power_consumption'] == 0
    assert not status['is_on']
    
    device.turn_on()
    status = device.get_status()
    assert status['power_consumption'] == 1000
    assert status['is_on'] 