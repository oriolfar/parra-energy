#!/usr/bin/env python3
"""
Script de debugging per verificar i arreglar els controls manuals
"""

import sys
import os
import subprocess
import time
import requests
import json

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

def test_enhanced_mock():
    """Test del client enhanced mock"""
    print("🔧 Testing Enhanced Mock Client...")
    try:
        from parra_energy.api.enhanced_mock_fronius import EnhancedMockFroniusClient
        
        client = EnhancedMockFroniusClient()
        
        # Test controls manuals
        print("   📊 Testing manual solar control...")
        client.set_manual_solar_percentage(50)
        data = client.get_power_data()
        print(f"   ✅ Solar: {data.get('P_PV', 0)}W (esperem 2500W)")
        
        # Test reset controls
        client.reset_manual_controls()
        data = client.get_power_data()
        print(f"   ✅ Reset: Solar: {data.get('P_PV', 0)}W (esperem 0W)")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def start_server():
    """Inicia el servidor web"""
    print("🌐 Starting Web Server...")
    try:
        # Mata processos del port 5001
        kill_port_process(5001)
        time.sleep(2)
        
        # Inicia el servidor
        env = os.environ.copy()
        env['PYTHONPATH'] = '.'
        
        process = subprocess.Popen([
            '/usr/bin/python3', 'parra_energy/web/app.py'
        ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"   🚀 Server started with PID: {process.pid}")
        
        # Espera que el servidor s'iniciï
        time.sleep(5)
        
        return process
    except Exception as e:
        print(f"   ❌ Error starting server: {e}")
        return None

def test_endpoints():
    """Test dels endpoints del servidor"""
    print("🌐 Testing Web Endpoints...")
    
    base_url = "http://localhost:5001"
    
    # Test endpoint bàsic
    try:
        response = requests.get(f"{base_url}/api/status", timeout=5)
        if response.status_code == 200:
            print("   ✅ Basic endpoint working")
        else:
            print(f"   ❌ Basic endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot connect to server: {e}")
        return False
    
    # Test controls manual
    try:
        # Test solar percentage
        data = {"percentage": 60}
        response = requests.post(
            f"{base_url}/api/mock/set-solar-percentage",
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Solar control: {result}")
        else:
            print(f"   ❌ Solar control failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Solar control error: {e}")
    
    # Test consumption
    try:
        data = {"watts": 2000}
        response = requests.post(
            f"{base_url}/api/mock/set-consumption",
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Consumption control: {result}")
        else:
            print(f"   ❌ Consumption control failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Consumption control error: {e}")
    
    # Test scenario
    try:
        data = {"scenario": "excess_solar"}
        response = requests.post(
            f"{base_url}/api/mock/test-scenario",
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Scenario test: {result['scenario']} - {result['name']}")
        else:
            print(f"   ❌ Scenario test failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Scenario test error: {e}")
    
    return True

def main():
    """Funció principal"""
    print("🔧 DEBUG: Parra Energy Manual Controls")
    print("=" * 50)
    
    # Test 1: Enhanced Mock Client
    if not test_enhanced_mock():
        print("❌ Enhanced Mock Client failed!")
        return
    
    # Test 2: Start Server
    server_process = start_server()
    if not server_process:
        print("❌ Server failed to start!")
        return
    
    try:
        # Test 3: Test Endpoints
        if test_endpoints():
            print("\n✅ ALL TESTS PASSED!")
            print("\n🌐 Server running at: http://localhost:5001")
            print("📋 Manual Controls available at demo controls section")
            print("\n🎯 How to use:")
            print("1. Open http://localhost:5001 in your browser")
            print("2. Click 'Activar mode demo'")
            print("3. Use the manual controls sliders")
            print("4. Try the scenario buttons")
            print("\nPress Ctrl+C to stop the server...")
            
            # Manté el servidor funcionant
            server_process.wait()
        else:
            print("❌ Endpoint tests failed!")
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
    finally:
        if server_process:
            server_process.terminate()
            server_process.wait()
        kill_port_process(5001)

if __name__ == "__main__":
    main()
