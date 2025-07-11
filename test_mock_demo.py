#!/usr/bin/env python3
"""
Test script to demonstrate the mock Fronius functionality

This script shows how the mock client generates realistic solar data
and can be used for demos when the real Fronius inverter is not available.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parra_energy.api.mock_fronius import MockFroniusClient
from parra_energy.api.smart_fronius import SmartFroniusClient
import time
from datetime import datetime


def test_mock_client():
    """Test the mock Fronius client directly."""
    print("🔧 Testing Mock Fronius Client")
    print("=" * 50)
    
    mock_client = MockFroniusClient()
    
    for i in range(5):
        data = mock_client.get_power_data()
        current_time = datetime.now().strftime("%H:%M:%S")
        
        print(f"[{current_time}] Mock Data:")
        print(f"  Solar Production: {data['P_PV']:6.1f} W")
        print(f"  House Consumption: {data['P_Load']:6.1f} W")  
        print(f"  Grid Power: {data['P_Grid']:6.1f} W {'(importing)' if data['P_Grid'] > 0 else '(exporting)' if data['P_Grid'] < 0 else '(balanced)'}")
        print(f"  Daily Energy: {data['E_Day']:6.1f} Wh")
        print(f"  Self Consumption: {data['rel_SelfConsumption']:5.1f}%")
        print(f"  Autonomy: {data['rel_Autonomy']:5.1f}%")
        print()
        
        if i < 4:  # Don't sleep on the last iteration
            time.sleep(2)


def test_smart_client():
    """Test the smart Fronius client (should fall back to mock)."""
    print("🧠 Testing Smart Fronius Client")
    print("=" * 50)
    
    # This should automatically detect that the real inverter is not available
    # and fall back to mock mode
    smart_client = SmartFroniusClient(host="192.168.1.128")
    
    print("Initial status:")
    status = smart_client.get_status()
    print(f"  Using real data: {status['using_real_data']}")
    print(f"  Real inverter available: {status['real_inverter_available']}")
    print()
    
    print("Getting data from smart client:")
    for i in range(3):
        data = smart_client.get_power_data()
        current_time = datetime.now().strftime("%H:%M:%S")
        
        print(f"[{current_time}] Smart Client Data:")
        print(f"  Solar Production: {data['P_PV']:6.1f} W")
        print(f"  House Consumption: {data['P_Load']:6.1f} W")
        print(f"  Grid Power: {data['P_Grid']:6.1f} W")
        print(f"  Using real data: {smart_client.is_using_real_data()}")
        print()
        
        if i < 2:
            time.sleep(2)


def demonstrate_daily_pattern():
    """Demonstrate how the mock generates different data throughout the day."""
    print("📊 Mock Daily Pattern Demo")
    print("=" * 50)
    
    mock_client = MockFroniusClient()
    
    # Simulate different times of day
    times_to_test = [
        ("Early Morning", 6),
        ("Morning", 9), 
        ("Midday", 13),
        ("Afternoon", 16),
        ("Evening", 19),
        ("Night", 22)
    ]
    
    print("Solar production varies throughout the day:")
    for period, hour in times_to_test:
        # Get some sample data (the mock uses current time, but we can see the pattern)
        data = mock_client.get_power_data()
        print(f"  {period:12} ({hour:2}h): {data['P_PV']:6.1f} W solar production")
        time.sleep(0.5)


def main():
    """Run all tests."""
    print("🌞 Parra Energy Mock System Demo")
    print("=" * 70)
    print()
    
    try:
        test_mock_client()
        print("\n" + "=" * 70 + "\n")
        
        test_smart_client()
        print("\n" + "=" * 70 + "\n")
        
        demonstrate_daily_pattern()
        print("\n" + "=" * 70)
        
        print("✅ Demo completed successfully!")
        print()
        print("💡 To use the web interface:")
        print("   1. Run: python run.py")
        print("   2. Open: http://localhost:5000")
        print("   3. The system will automatically use mock data when real inverter is not available")
        print("   4. Use the 'Activar mode demo' button to force mock mode")
        print()
        print("🔧 The mock generates realistic data based on:")
        print("   - Time of day (solar production follows sun cycle)")
        print("   - Weather patterns (clouds, seasonal effects)")
        print("   - Household consumption patterns")
        print("   - Realistic appliance usage")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 