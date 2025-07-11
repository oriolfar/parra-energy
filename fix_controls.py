#!/usr/bin/env python3
"""
Script final per solucionar tots els problemes dels controls manuals
"""

import sys
import os
import subprocess
import time
import webbrowser
from threading import Timer

# Afegir el directori actual al path
sys.path.append('.')

def kill_port_process(port):
    """Mata qualsevol procés que usi el port especificat"""
    try:
        result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    subprocess.run(['kill', '-9', pid], capture_output=True)
                    print(f"🔧 Matat procés {pid} del port {port}")
    except Exception as e:
        print(f"⚠️  Error matant processos del port {port}: {e}")

def open_browser():
    """Obre el navegador web"""
    url = "http://localhost:5001"
    print(f"🌐 Opening browser at {url}")
    webbrowser.open(url)

def main():
    """Funció principal"""
    print("🔧 SOLUCIÓ COMPLETA: Parra Energy Manual Controls")
    print("=" * 55)
    
    # Pas 1: Mata processos del port 5001
    kill_port_process(5001)
    time.sleep(1)
    
    # Pas 2: Test del client enhanced mock
    print("🔧 Testing Enhanced Mock Client...")
    try:
        from parra_energy.api.enhanced_mock_fronius import EnhancedMockFroniusClient
        client = EnhancedMockFroniusClient()
        client.set_manual_solar_percentage(50)
        data = client.get_power_data()
        print(f"   ✅ Solar: {data.get('P_PV', 0)}W - Enhanced Mock OK!")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Pas 3: Inicia el servidor
    print("🌐 Starting Web Server...")
    try:
        from parra_energy.web.app import app
        
        # Programa l'obertura del navegador després de 3 segons
        timer = Timer(3.0, open_browser)
        timer.start()
        
        print("   🚀 Server starting at http://localhost:5001")
        print("   📋 Browser will open automatically")
        print("   🎯 Look for 'Controls manuals' section in the demo")
        print("   ⚡ Use the sliders to control solar/consumption")
        print("   📊 Try the scenario buttons")
        print("")
        print("   Press Ctrl+C to stop the server...")
        
        # Inicia el servidor
        app.run(debug=False, host='0.0.0.0', port=5001)
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
    except Exception as e:
        print(f"   ❌ Server error: {e}")
    finally:
        kill_port_process(5001)

if __name__ == "__main__":
    main()
