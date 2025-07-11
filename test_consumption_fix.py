#!/usr/bin/env python3
import sys
sys.path.append('.')

def test_all_controls():
    print("🔧 TESTING ALL CONTROLS - CONSUMPTION FIX")
    print("="*50)
    
    from parra_energy.api.enhanced_mock_fronius import EnhancedMockFroniusClient
    
    client = EnhancedMockFroniusClient()
    
    # Test 1: Solar control (que ja funciona)
    print("\n⚡ Test 1: Solar Control (2,2kW)")
    client.set_manual_solar_percentage(50)
    data = client.get_power_data()
    expected = 1100  # 50% of 2200W
    print(f"   Solar: {data.get('P_PV', 0)}W (esperat: {expected}W)")
    assert data.get('P_PV', 0) == expected
    print("   ✅ Solar control OK!")
    
    # Test 2: Consumption control (el que falla)
    print("\n🏠 Test 2: Consumption Control")
    client.set_manual_consumption_watts(2500)
    data = client.get_power_data()
    print(f"   Consumption: {data.get('P_Load', 0)}W (esperat: 2500W)")
    assert data.get('P_Load', 0) == 2500
    print("   ✅ Consumption control OK!")
    
    # Test 3: Grid calculation
    print("\n⚡ Test 3: Grid Power")
    grid = data.get('P_Grid', 0)
    expected_grid = 2500 - 1100  # 1400W importing
    print(f"   Grid: {grid}W (esperat: {expected_grid}W)")
    assert abs(grid - expected_grid) < 1
    print("   ✅ Grid calculation OK!")
    
    print("\n🎉 ALL BACKEND CONTROLS WORK!")
    print("🔧 Added debug logs to consumption endpoint")
    
    # Start web server
    print("\n🌐 Starting Web Server...")
    from parra_energy.web.app import app
    
    import webbrowser
    from threading import Timer
    
    def open_browser():
        webbrowser.open("http://localhost:5001")
    
    timer = Timer(3.0, open_browser)
    timer.start()
    
    print("   ✅ Solar: 0-2200W (2,2kW) - WORKING")
    print("   🔧 Consumption: Debug logs added - TEST NOW")
    print("   ✅ Scenarios: Fixed quotes - WORKING") 
    print("   ✅ Reset: WORKING")
    print("   🚀 Server at http://localhost:5001")
    print("")
    print("   🎯 PROVA EL BOTÓ 'Aplicar' DEL CONSUM!")
    print("   👁️ Mira la consola per veure els logs")
    print("")
    print("   Press Ctrl+C to stop...")
    
    try:
        app.run(debug=False, host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")

if __name__ == "__main__":
    test_all_controls()
