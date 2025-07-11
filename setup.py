"""
Setup script for Parra Energy system.
This script initializes the system with test devices and starts the web dashboard.
"""

from parra_energy.simulators.device import Device
from parra_energy.automations.manager import AutomationManager
from parra_energy.web.app import app

def setup_test_devices():
    """Create and configure test devices."""
    # Create some test devices with realistic power consumption
    devices = [
        Device("Water Heater", 2000),      # 2kW water heater
        Device("Washing Machine", 1500),    # 1.5kW washing machine
        Device("Dishwasher", 1200),        # 1.2kW dishwasher
        Device("EV Charger", 7000),        # 7kW EV charger
        Device("Pool Pump", 1000),         # 1kW pool pump
    ]
    
    # Add devices to the automation manager
    for device in devices:
        app.automation_manager.add_device(device)
        print(f"Added device: {device.name} ({device.power_consumption}W)")

def main():
    """Main setup function."""
    print("Setting up Parra Energy system...")
    
    # Set up test devices
    setup_test_devices()
    
    print("\nSystem setup complete!")
    print("Starting web dashboard...")
    print("Access the dashboard at: http://localhost:5000")
    
    # Start the web dashboard
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main() 