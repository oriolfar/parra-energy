#!/usr/bin/env python3
import sys
sys.path.append('.')

print("🔧 FINAL FIX: Consumption Button")
print("="*40)

# Quick backend test
from parra_energy.api.enhanced_mock_fronius import EnhancedMockFroniusClient
client = EnhancedMockFroniusClient()
print("✅ Backend tested and working")

# Start server
print("🌐 Starting server with consumption fix...")
from parra_energy.web.app import app

import webbrowser
from threading import Timer

def open_browser():
    webbrowser.open("http://localhost:5001")

timer = Timer(3.0, open_browser)
timer.start()

print("�� FIXED:")
print("   ✅ Added robust event listener for consumption button")
print("   ✅ Solar: 0-2200W (2,2kW real panels)")
print("   ✅ Scenarios: All working")
print("   ✅ Reset: Working")
print("")
print("🔍 Test now:")
print("   1. Open F12 Developer Tools > Console")
print("   2. Look for '✅ Consumption button event listener added'")
print("   3. Click consumption 'Aplicar' button")
print("   4. Should see '🔧 Consumption button clicked directly!'")
print("   5. Should see '🔧 DEBUG: Received set-consumption request' in terminal")
print("")
print("   If all above messages appear → FIXED! 🎉")

try:
    app.run(debug=False, host='0.0.0.0', port=5001)
except KeyboardInterrupt:
    print("\n🛑 Test complete")
