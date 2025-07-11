#!/usr/bin/env python3
import sys
sys.path.append('.')

print("🚀 Starting Parra Energy with 2,2kW system...")
print("✅ Max solar: 2200W (2,2kW)")
print("✅ Consumption slider: Fixed")
print("✅ Scenario buttons: Fixed")
print("🌐 Opening http://localhost:5001")

import webbrowser
from threading import Timer

def open_browser():
    webbrowser.open("http://localhost:5001")

timer = Timer(3.0, open_browser)
timer.start()

from parra_energy.web.app import app
app.run(debug=False, host='0.0.0.0', port=5001)
