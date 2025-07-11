#!/usr/bin/env python3
import sys
sys.path.append('.')

print("🔧 QUICK TEST: Consumption Issue")

# Test backend
from parra_energy.api.enhanced_mock_fronius import EnhancedMockFroniusClient
client = EnhancedMockFroniusClient()
client.set_manual_consumption_watts(1500)
data = client.get_power_data()
print(f"✅ Backend works: {data.get('P_Load', 0)}W")

# Start server
print("🌐 Starting server...")
from parra_energy.web.app import app

import webbrowser
from threading import Timer
def open_browser():
    webbrowser.open("http://localhost:5001")
timer = Timer(2.0, open_browser)
timer.start()

print("🔍 TEST CONSUMPTION BUTTON:")
print("1. Open F12 Developer Tools")
print("2. Click consumption 'Aplicar' button")
print("3. Check console for 'Setting consumption:' message")
print("4. Check terminal for '🔧 DEBUG: Received set-consumption request'")

app.run(debug=False, host='0.0.0.0', port=5001)
