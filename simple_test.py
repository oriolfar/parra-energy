#!/usr/bin/env python3
import sys
sys.path.append('.')

print("�� SIMPLE TEST: Consumption Button")
print("="*40)

from parra_energy.web.app import app
import webbrowser
from threading import Timer

def open_browser():
    webbrowser.open("http://localhost:5001")

timer = Timer(2.0, open_browser)
timer.start()

print("✅ Server starting...")
print("🔧 Added debug: onclick='console.log(\"🔧 Button clicked!\"); setConsumption();'")
print("")
print("🎯 Test steps:")
print("   1. Click consumption 'Aplicar' button")
print("   2. Look for '🔧 Button clicked!' in console")
print("   3. Look for '🔧 setConsumption() function called!' in console")
print("   4. Look for '🔧 DEBUG: Received set-consumption request' in terminal")
print("")
print("   If you see ALL messages → SUCCESS! ✅")
print("   If you see NONE → Button not working ❌")

try:
    app.run(debug=False, host='0.0.0.0', port=5001)
except KeyboardInterrupt:
    print("\n🛑 Test complete")
