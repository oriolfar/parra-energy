# 🔧 Mock Solar Panel System for Demos

## Overview

I've created a comprehensive mock system that simulates your Fronius solar inverter data for demo purposes. This allows your website to work seamlessly both when you're on the local network (with real data) and when you're away from home (with realistic simulated data).

## ✨ Features

### 1. **MockFroniusClient** - Realistic Solar Data Simulation
- **Daily solar cycles**: Production follows the sun from 7 AM to 7 PM
- **Weather patterns**: Random daily weather (sunny, partly cloudy, cloudy)
- **Seasonal variations**: Lower production in winter months
- **Realistic consumption**: Household usage patterns with morning/evening peaks
- **Appliance simulation**: Random high-consumption events (dishwasher, washing machine)
- **Energy metrics**: Self-consumption, autonomy, daily/total energy counters

### 2. **SmartFroniusClient** - Automatic Detection
- **Auto-fallback**: Automatically detects if real inverter is available
- **Seamless switching**: Falls back to mock when real inverter is unreachable
- **Periodic checking**: Regularly checks if real inverter becomes available again
- **Manual control**: Force mock or real mode for testing

### 3. **Web Interface Integration**
- **Visual indicators**: Shows whether you're viewing real or mock data
- **Demo controls**: Buttons to switch between real and mock modes
- **Real-time updates**: Mock data updates every 5 seconds just like real data

## 🚀 How It Works

### Automatic Detection
When the web app starts, the SmartFroniusClient:
1. Tries to connect to your real Fronius inverter (`192.168.1.128`)
2. If successful: Uses real data ✅
3. If failed: Automatically switches to mock data 🔧
4. Continues checking every 5 minutes if real inverter becomes available

### Mock Data Generation
The mock generates realistic data by considering:
- **Time of day**: No production at night, peak at midday
- **Weather**: Daily weather patterns affect production
- **Season**: Winter months have lower production
- **Consumption**: Realistic household usage with peaks during morning/evening
- **Appliances**: Occasional high-consumption events

## 📱 Using the Web Interface

### Visual Indicators
- **Green badge**: "✅ Dades reals del inversor" - Using real data
- **Blue badge**: "🔧 Dades simulades per demo" - Using mock data

### Demo Controls
When using mock data, you'll see control buttons:
- **"Activar mode demo"**: Force mock mode (useful for demos)
- **"Intentar dades reals"**: Try to reconnect to real inverter

## 🛠️ Setup and Installation

### Prerequisites
```bash
# Make sure you have the required dependencies
pip install flask requests

# Or install from requirements.txt
pip install -r requirements.txt
```

### Running the System
```bash
# Start the web application
python run.py

# Open your browser to:
http://localhost:5000
```

### Testing the Mock System
```bash
# Run the demo script to see mock data in action
python test_mock_demo.py
```

## 📊 API Endpoints

### New Endpoints for Mock Control
- `GET /api/fronius/status` - Get detailed client status
- `POST /api/fronius/force-mock` - Force mock mode for demos
- `POST /api/fronius/force-real` - Try to switch back to real data

### Enhanced Existing Endpoint
- `GET /api/status` - Now includes `client_status` showing real vs mock info

## 🎯 Use Cases

### 1. **Demo Mode**
Perfect for showing the system to others when not at home:
- Visit the website from anywhere
- System automatically uses mock data
- Shows realistic solar production patterns
- All features work exactly the same

### 2. **Development & Testing**
- Test website functionality without real hardware
- Predictable data patterns for testing
- No dependency on time of day or weather

### 3. **Presentations**
- Force mock mode for consistent demo experience
- Show different scenarios (high production, low production, etc.)
- Reliable data flow during presentations

## 📈 Mock Data Patterns

### Daily Solar Production
```
Night (22h-6h):     0 W      (No sun)
Morning (7h-9h):    500-1500 W    (Rising production)
Midday (10h-14h):   2000-5000 W   (Peak production)
Afternoon (15h-18h): 1000-3000 W   (Declining production)
Evening (19h-21h):  0 W      (Sun sets)
```

### Consumption Patterns
```
Night (23h-6h):     200-400 W     (Base load)
Morning (7h-9h):    600-1200 W    (Morning activity)
Day (10h-16h):      300-700 W     (Lower usage)
Evening (17h-21h):  750-1500 W    (Peak consumption)
```

### Weather Effects
- **Sunny days**: 90-100% of potential production
- **Partly cloudy**: 60-80% with variations
- **Cloudy**: 20-40% production
- **Seasonal**: 55% in winter, 100% in summer

## 🔄 How the Smart Client Works

```python
# The SmartFroniusClient automatically handles everything:

smart_client = SmartFroniusClient(host="192.168.1.128")

# This will:
# 1. Try to connect to real inverter
# 2. Fall back to mock if unavailable
# 3. Provide seamless data regardless of connection

data = smart_client.get_power_data()  # Always works!
```

## 🎉 Benefits

1. **Always Available**: Website works 24/7 regardless of network location
2. **Realistic Demos**: Mock data follows real solar patterns
3. **Seamless Experience**: Users can't tell the difference
4. **Easy Testing**: Developers can test without real hardware
5. **Reliable Presentations**: Consistent data for demos

## 🔧 Customization

### Adjusting Mock Parameters
Edit `parra_energy/api/mock_fronius.py`:
- `max_solar_power`: Change system capacity (default: 5000W)
- `base_consumption`: Adjust household base load (default: 300W)
- Weather patterns and seasonal factors

### Changing Detection Interval
Edit `SmartFroniusClient` initialization:
```python
# Check for real inverter every 60 seconds instead of 300
smart_client = SmartFroniusClient(host="192.168.1.128", check_interval=60)
```

## 📞 Support

The mock system is designed to be maintenance-free. It will:
- Automatically use real data when you're home
- Automatically switch to mock when you're away
- Provide realistic data patterns for demos
- Update every 5 seconds just like the real system

Perfect for showing your solar system to family, friends, or potential customers! 🌞 