#!/usr/bin/env python3
import sys
sys.path.append('.')

print("🔧 DEBUG: Consumption Button - Final Test")
print("="*50)

# Quick test
from parra_energy.api.enhanced_mock_fronius import EnhancedMockFroniusClient
client = EnhancedMockFroniusClient()
print("✅ Backend ready")

# Start server  
from parra_energy.web.app import app
import webbrowser
from threading import Timer

def open_browser():
    webbrowser.open("http://localhost:5001")

timer = Timer(3.0, open_browser)
timer.start()

print("\n🔧 ADDED EXTENSIVE DEBUG:")
print("   - '🔧 setConsumption() function called!'")
print("   - '🔧 Setting consumption: X'")
print("   - '🔧 About to make fetch request...'")
print("   - '✅ Consumption button found with onclick'")
print("")
print("🎯 Test sequence:")
print("   1. Open F12 > Console")
print("   2. Look for '✅ Consumption button found with onclick'")
print("   3. Move consumption slider")
print("   4. Click 'Aplicar' button")
print("   5. Check for ALL debug messages")
print("")
print("   If NO messages → onclick problem")
print("   If partial messages → fetch problem")
print("   If all messages → SUCCESS!")

try:
    app.run(debug=False, host='0.0.0.0', port=5001)
except KeyboardInterrupt:
    print("\n🛑 Debug complete")
