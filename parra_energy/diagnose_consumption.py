#!/usr/bin/env python3
import sys
sys.path.append('.')

print("🔍 DIAGNOSTIC: Consumption Button Issue")
print("="*50)

# Test backend directly
from parra_energy.api.enhanced_mock_fronius import EnhancedMockFroniusClient

client = EnhancedMockFroniusClient()

print("\n✅ Backend Test:")
client.set_manual_consumption_watts(1800)
data = client.get_power_data()
print(f"   Direct API: {data.get('P_Load', 0)}W (should be 1800W)")

print("\n🌐 Starting server with enhanced debugging...")
from parra_energy.web.app import app

import webbrowser
from threading import Timer

def open_browser():
    webbrowser.open("http://localhost:5001")

timer = Timer(3.0, open_browser)
timer.start()

print("\n🔧 DIAGNOSIS STEPS:")
print("1. Open Developer Tools (F12)")
print("2. Go to Console tab")
print("3. Move consumption slider to any value")
print("4. Click 'Aplicar' button")
print("5. Check if you see:")
print("   - 'Setting consumption: XXX' message")
print("   - Any JavaScript errors")
print("   - '🔧 DEBUG: Received set-consumption request' in terminal")
print("\n6. If no 'Setting consumption' message appears:")
print("   - The function is not being called")
print("   - Check if button onclick works")
print("\n7. If you see 'Setting consumption' but no server log:")
print("   - Network issue or endpoint problem")
print("\n8. Try typing in console: setConsumption()")
print("   - To test function directly")
print("\nPress Ctrl+C to stop...")

try:
    app.run(debug=False, host='0.0.0.0', port=5001)
except KeyboardInterrupt:
    print("\n🛑 Diagnostic complete")
