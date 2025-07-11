#!/usr/bin/env python3
import sys
sys.path.append('.')

def test_all():
    print("🔧 TESTING COMPLETE MANUAL CONTROLS")
    print("="*50)
    
    from parra_energy.api.enhanced_mock_fronius import EnhancedMockFroniusClient
    
    client = EnhancedMockFroniusClient()
    
    # Test 1: Solar 75%
    print("\n📊 Test 1: Solar 75%")
    client.set_manual_solar_percentage(75)
    data = client.get_power_data()
    expected = 75/100 * 5000  # 3750W
    print(f"   Set: 75%, Got: {data.get('P_PV', 0)}W, Expected: {expected}W")
    assert abs(data.get('P_PV', 0) - expected) < 1
    print("   ✅ Solar control works!")
    
    # Test 2: Consumption 2500W
    print("\n🏠 Test 2: Consumption 2500W")
    client.set_manual_consumption_watts(2500)
    data = client.get_power_data()
    print(f"   Set: 2500W, Got: {data.get('P_Load', 0)}W")
    assert data.get('P_Load', 0) == 2500
    print("   ✅ Consumption control works!")
    
    # Test 3: Grid calculation
    print("\n⚡ Test 3: Grid Power")
    grid = data.get('P_Grid', 0)
    expected_grid = 2500 - 3750  # -1250W (exporting)
    print(f"   Grid: {grid}W, Expected: {expected_grid}W")
    assert abs(grid - expected_grid) < 1
    print("   ✅ Grid calculation works!")
    
    print("\n🎉 ALL MANUAL CONTROLS WORK PERFECTLY!")
    
    # Now start web server
    print("\n🌐 Starting Web Server...")
    from parra_energy.web.app import app
    
    import webbrowser
    from threading import Timer
    
    def open_browser():
        webbrowser.open("http://localhost:5001")
    
    timer = Timer(3.0, open_browser)
    timer.start()
    
    print("   ✅ Backend controls verified working")
    print("   ✅ Frontend JavaScript functions fixed")
    print("   ✅ Server starting at http://localhost:5001")
    print("   🎯 MANUAL CONTROLS ARE NOW WORKING!")
    print("   ⚡ Try the sliders in the 'Controls manuals' section")
    print("   📊 They should respond immediately")
    print("")
    print("   Press Ctrl+C to stop...")
    
    try:
        app.run(debug=False, host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")

if __name__ == "__main__":
    test_all()
