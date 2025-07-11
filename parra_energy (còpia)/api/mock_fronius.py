"""
Mock Fronius API Client Module

This module provides a mock client that simulates Fronius solar inverter data
for demo purposes when the real inverter is not accessible (e.g., when not 
on the local network).

The mock generates realistic solar production patterns that:
- Follow the sun's daily cycle
- Include realistic weather variations
- Simulate typical household consumption patterns
- Match the data format of the real Fronius API
"""

import random
import math
from datetime import datetime, timedelta
from typing import Dict, Optional
import time


class MockFroniusClient:
    def __init__(self, host: str = "mock", port: int = 80):
        """Initialize the mock Fronius API client.
        
        Args:
            host: Ignored for mock (included for compatibility)
            port: Ignored for mock (included for compatibility)
        """
        self.host = host
        self.port = port
        
        # System configuration (5kW solar system)
        self.max_solar_power = 5000  # 5kW peak capacity
        self.base_consumption = 300  # Base household consumption in watts
        
        # Initialize cumulative energy counters
        self._daily_energy = 0
        self._total_energy = 145000  # Simulated total since installation
        self._yearly_energy = 12500  # Simulated yearly production so far
        self._last_update = datetime.now()
        self._last_day = datetime.now().day
        
        # Weather simulation state
        self._weather_pattern = self._generate_weather_pattern()
        
    def get_power_data(self) -> Dict:
        """Generate mock power data that simulates real Fronius inverter output.
        
        Returns:
            Dict containing realistic solar and consumption data matching
            the real Fronius API format
        """
        current_time = datetime.now()
        
        # Reset daily counter at midnight
        if current_time.day != self._last_day:
            self._daily_energy = 0
            self._last_day = current_time.day
            self._weather_pattern = self._generate_weather_pattern()
        
        # Calculate solar production based on time of day and weather
        solar_power = self._calculate_solar_production(current_time)
        
        # Calculate household consumption with realistic variations
        consumption_power = self._calculate_consumption(current_time)
        
        # Calculate grid power (positive = importing, negative = exporting)
        grid_power = consumption_power - solar_power
        
        # Update energy counters
        time_delta = (current_time - self._last_update).total_seconds() / 3600  # hours
        energy_increment = solar_power * time_delta
        self._daily_energy += energy_increment
        self._total_energy += energy_increment
        self._yearly_energy += energy_increment
        self._last_update = current_time
        
        # Calculate efficiency metrics
        if consumption_power > 0:
            self_consumed = min(solar_power, consumption_power)
            autonomy = (self_consumed / consumption_power) * 100
        else:
            autonomy = 100 if solar_power > 0 else 0
            
        if solar_power > 0:
            self_consumption_rate = (min(solar_power, consumption_power) / solar_power) * 100
        else:
            self_consumption_rate = 0
        
        return {
            'P_PV': round(solar_power, 1),  # Solar production in watts
            'P_Load': round(consumption_power, 1),  # House consumption in watts  
            'P_Grid': round(grid_power, 1),  # Grid power flow in watts
            'P_Akku': 0,  # No battery in this simulation
            'E_Day': round(self._daily_energy, 1),  # Energy produced today in Wh
            'E_Total': round(self._total_energy, 1),  # Total energy produced in Wh
            'E_Year': round(self._yearly_energy, 1),  # Energy produced this year in Wh
            'rel_Autonomy': round(autonomy, 1),  # Percentage of energy autonomy
            'rel_SelfConsumption': round(self_consumption_rate, 1)  # Percentage of self-consumption
        }
    
    def _calculate_solar_production(self, current_time: datetime) -> float:
        """Calculate realistic solar production based on time and weather."""
        hour = current_time.hour
        minute = current_time.minute
        
        # No production during night (before 7 AM and after 7 PM)
        if hour < 7 or hour >= 19:
            return 0
        
        # Calculate sun position effect (bell curve throughout the day)
        # Peak at 13:00 (1 PM)
        time_factor = hour + minute / 60.0
        sun_angle = math.sin(math.pi * (time_factor - 7) / 12)  # From 7 AM to 7 PM
        
        if sun_angle <= 0:
            return 0
        
        # Base production from sun angle
        base_production = self.max_solar_power * sun_angle
        
        # Apply weather effects
        weather_factor = self._weather_pattern.get(hour, 1.0)
        
        # Add small random variations (±5%)
        variation = random.uniform(0.95, 1.05)
        
        # Apply seasonal effects (lower in winter months)
        month = current_time.month
        seasonal_factor = self._get_seasonal_factor(month)
        
        production = base_production * weather_factor * seasonal_factor * variation
        
        return max(0, production)
    
    def _calculate_consumption(self, current_time: datetime) -> float:
        """Calculate realistic household consumption patterns."""
        hour = current_time.hour
        
        # Base consumption patterns throughout the day
        if 6 <= hour < 9:  # Morning peak
            base_factor = 2.0
        elif 9 <= hour < 17:  # Day time (lower consumption)
            base_factor = 1.2
        elif 17 <= hour < 21:  # Evening peak
            base_factor = 2.5
        elif 21 <= hour < 23:  # Evening 
            base_factor = 1.8
        else:  # Night time
            base_factor = 0.8
        
        base_consumption = self.base_consumption * base_factor
        
        # Add random variations for appliances turning on/off
        variation = random.uniform(0.7, 1.4)
        
        # Occasionally simulate high-consumption appliances
        if random.random() < 0.1:  # 10% chance
            appliance_boost = random.uniform(1000, 2500)  # Dishwasher, washing machine, etc.
        else:
            appliance_boost = 0
        
        consumption = base_consumption * variation + appliance_boost
        
        return max(50, consumption)  # Minimum 50W consumption
    
    def _generate_weather_pattern(self) -> Dict[int, float]:
        """Generate a daily weather pattern affecting solar production."""
        pattern = {}
        
        # Choose weather type for the day
        weather_types = [
            ('sunny', 1.0, 0.05),      # Clear day, high production, low variation
            ('partly_cloudy', 0.7, 0.3),  # Some clouds, reduced production, high variation
            ('cloudy', 0.3, 0.2),      # Overcast, low production, medium variation
            ('very_cloudy', 0.15, 0.1), # Heavy clouds, very low production, low variation
        ]
        
        weather_type, base_factor, variation_range = random.choice(weather_types)
        
        # Generate hourly factors
        for hour in range(24):
            if 7 <= hour < 19:  # Daylight hours
                # Add some hour-to-hour variation for clouds moving
                variation = random.uniform(-variation_range, variation_range)
                pattern[hour] = max(0.1, base_factor + variation)
            else:
                pattern[hour] = 0
        
        return pattern
    
    def _get_seasonal_factor(self, month: int) -> float:
        """Get seasonal factor affecting solar production."""
        # Based on typical solar irradiation patterns in Spain
        seasonal_factors = {
            1: 0.6,   # January
            2: 0.7,   # February  
            3: 0.8,   # March
            4: 0.9,   # April
            5: 0.95,  # May
            6: 1.0,   # June (peak)
            7: 1.0,   # July (peak)
            8: 0.98,  # August
            9: 0.9,   # September
            10: 0.8,  # October
            11: 0.65, # November
            12: 0.55  # December
        }
        
        return seasonal_factors.get(month, 0.8)
    
    def is_available(self) -> bool:
        """Check if the mock client is available (always True for mock)."""
        return True 