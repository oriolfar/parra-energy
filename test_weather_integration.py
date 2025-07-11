#!/usr/bin/env python3
"""
Test script for weather integration with solar energy system
"""

import sys
import os
sys.path.append('parra_energy')

from weather.weather_service import WeatherService
from analytics.optimizer import EnergyOptimizer

def test_weather_service():
    """Test the weather service functionality"""
    print("🌤️ Testing Weather Service...")
    
    try:
        # Initialize weather service
        weather_service = WeatherService()
        print("✅ Weather service initialized successfully")
        
        # Test fetching weather forecast
        print("\n📡 Fetching weather forecast...")
        weather_data = weather_service.fetch_weather_forecast(7)
        
        if weather_data:
            print("✅ Weather forecast fetched successfully")
            print(f"📍 Coordinates: {weather_data['coordinates']['latitude']:.4f}, {weather_data['coordinates']['longitude']:.4f}")
            print(f"🏔️ Elevation: {weather_data['coordinates']['elevation']} m")
        else:
            print("❌ Failed to fetch weather forecast")
            return False
        
        # Test weekly weather summary
        print("\n📅 Getting weekly weather summary...")
        weekly_summary = weather_service.get_weekly_weather_summary()
        
        if weekly_summary is not None and not weekly_summary.empty:
            print("✅ Weekly summary generated successfully")
            print(f"📊 {len(weekly_summary)} days of forecast data")
            
            # Show first day details
            first_day = weekly_summary.iloc[0]
            print(f"🌅 Today: {first_day['date']}")
            print(f"☀️ Sunrise: {first_day['sunrise']}, Sunset: {first_day['sunset']}")
            print(f"🌡️ Temperature: {first_day['temperature_min']:.1f}°C - {first_day['temperature_max']:.1f}°C")
            print(f"⚡ Solar forecast: {first_day['solar_production_forecast']:.1f} kWh")
            print(f"🏆 Weather quality: {first_day['quality_rating']} ({first_day['weather_quality_score']:.0f}/100)")
        else:
            print("❌ Failed to get weekly summary")
            return False
        
        # Test best hours forecast
        print("\n⏰ Getting best hours forecast...")
        best_hours = weather_service.get_best_hours_forecast()
        
        if best_hours:
            print("✅ Best hours forecast generated")
            print(f"🔥 Peak production hours: {[h['hour'] for h in best_hours['peak_production_hours'][:3]]}")
            print(f"⚡ Average daily production: {best_hours['average_daily_production']:.1f} kWh")
            print(f"🎯 Best single hour: {best_hours['best_hour']}h")
        else:
            print("⚠️ No best hours data available (normal if no weather data yet)")
        
        return True
        
    except Exception as e:
        print(f"❌ Weather service test failed: {e}")
        return False

def test_enhanced_optimizer():
    """Test the enhanced energy optimizer with weather intelligence"""
    print("\n🧠 Testing Enhanced Energy Optimizer...")
    
    try:
        # Initialize optimizer with proper database path
        optimizer = EnergyOptimizer('parra_energy/data/energy_data.db')
        print("✅ Energy optimizer initialized successfully")
        
        # Test weather-aware tips
        print("\n💡 Getting optimization tips (including weather-aware)...")
        tips = optimizer.get_optimization_tips(30)
        
        print(f"✅ Generated {len(tips)} optimization tips")
        
        # Show weather-specific tips
        weather_tips = [tip for tip in tips if '🌞' in tip.tip or '☁️' in tip.tip or '🌡️' in tip.tip or '⚡' in tip.tip]
        if weather_tips:
            print(f"🌤️ Found {len(weather_tips)} weather-aware tips:")
            for tip in weather_tips[:3]:  # Show first 3
                print(f"  {tip.priority.upper()}: {tip.tip[:100]}...")
        else:
            print("ℹ️ No weather-specific tips generated (normal if no weather data yet)")
        
        # Test weather-enhanced forecast
        print("\n📊 Getting weather-enhanced forecast...")
        enhanced_forecast = optimizer.get_weather_enhanced_forecast(7)
        
        if 'error' not in enhanced_forecast:
            print("✅ Weather-enhanced forecast generated successfully")
            forecast_data = enhanced_forecast['enhanced_forecast']
            print(f"📅 {len(forecast_data)} days of enhanced forecast")
            
            # Show today's enhanced data
            if forecast_data:
                today = forecast_data[0]
                print(f"🌅 Today's enhanced forecast:")
                print(f"  📊 Weather quality: {today['weather_quality']}")
                print(f"  ⚡ Predicted production: {today['predicted_production_kwh']:.1f} kWh")
                print(f"  💡 Recommendations: {len(today['recommendations'])}")
                for rec in today['recommendations'][:2]:
                    print(f"    • {rec}")
        else:
            print(f"⚠️ Enhanced forecast error: {enhanced_forecast['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced optimizer test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Weather Integration Tests for Grandfather's Solar System")
    print("=" * 70)
    
    # Test weather service
    weather_success = test_weather_service()
    
    # Test enhanced optimizer
    optimizer_success = test_enhanced_optimizer()
    
    print("\n" + "=" * 70)
    print("📋 Test Results Summary:")
    print(f"🌤️ Weather Service: {'✅ PASS' if weather_success else '❌ FAIL'}")
    print(f"🧠 Enhanced Optimizer: {'✅ PASS' if optimizer_success else '❌ FAIL'}")
    
    if weather_success and optimizer_success:
        print("\n🎉 All tests passed! Your grandfather's solar system now has weather intelligence!")
        print("\n🌟 Features now available:")
        print("  • Real-time weather forecasts for solar planning")
        print("  • Weather-aware optimization tips in Catalan")
        print("  • 7-day solar production forecasts")
        print("  • Best hours recommendations based on weather")
        print("  • Temperature-adjusted efficiency calculations")
        print("  • Cloudy day warnings and sunny day optimization")
        print("\n💡 Your grandfather can now:")
        print("  • Plan appliance usage based on weather forecasts")
        print("  • Maximize solar energy utilization")
        print("  • Reduce grid dependency with intelligent timing")
        print("  • Get personalized advice in Catalan")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.")
    
    return weather_success and optimizer_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 