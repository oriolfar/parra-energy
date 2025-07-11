"""
Smart Fronius API Client Module

This module provides an intelligent client that automatically detects whether
the real Fronius inverter is available and falls back to an enhanced mock client for
demo purposes when the real inverter is not accessible.

This allows the application to work seamlessly both:
- On the local network (with real data)
- Outside the local network (with realistic mock data using real weather)
"""

from typing import Dict
import time
from .fronius import FroniusClient
from .enhanced_mock_fronius import EnhancedMockFroniusClient


class SmartFroniusClient:
    def __init__(self, host: str = "192.168.1.128", port: int = 80, check_interval: int = 300):
        """Initialize the smart Fronius client.
        
        Args:
            host: The IP address of the real Fronius inverter
            port: The port number (default: 80)
            check_interval: How often to check if real inverter is available (seconds)
        """
        self.host = host
        self.port = port
        self.check_interval = check_interval
        
        # Initialize both clients
        self.real_client = FroniusClient(host, port)
        self.mock_client = EnhancedMockFroniusClient()  # Now using enhanced mock!
        
        # Track which client we're using
        self._using_real = False
        self._last_check = 0
        
        # Perform initial availability check
        self._check_availability()
        
    def get_power_data(self) -> Dict:
        """Get power data from the appropriate client (real or enhanced mock).
        
        Returns:
            Dict containing power data from either real or enhanced mock inverter
        """
        # Periodically check if the real inverter has become available
        current_time = time.time()
        if current_time - self._last_check > self.check_interval:
            self._check_availability()
        
        # Get data from the appropriate client
        if self._using_real:
            try:
                data = self.real_client.get_power_data()
                # Check if we got zero values (which might indicate connection issues)
                if data.get('P_PV', 0) == 0 and data.get('P_Load', 0) == 0:
                    # Maybe the real client is having issues, do a quick availability check
                    if not self.real_client.is_available():
                        print("Real Fronius client seems to be having issues, switching to enhanced mock")
                        self._using_real = False
                        return self.mock_client.get_power_data()
                return data
            except Exception as e:
                print(f"Error with real client, switching to enhanced mock: {e}")
                self._using_real = False
                return self.mock_client.get_power_data()
        else:
            return self.mock_client.get_power_data()
    
    def _check_availability(self):
        """Check if the real Fronius inverter is available."""
        self._last_check = time.time()
        
        if self.real_client.is_available():
            if not self._using_real:
                print(f"✅ Real Fronius inverter detected at {self.host}. Switching to real data.")
            self._using_real = True
        else:
            if self._using_real:
                print(f"❌ Real Fronius inverter at {self.host} not available. Switching to enhanced mock data.")
            self._using_real = False
    
    def is_using_real_data(self) -> bool:
        """Check if currently using real data.
        
        Returns:
            bool: True if using real inverter, False if using enhanced mock
        """
        return self._using_real
    
    def force_mock_mode(self):
        """Force the client to use enhanced mock data (useful for testing/demos)."""
        print("🔧 Forcing enhanced mock mode for demo purposes")
        self._using_real = False
    
    def force_real_mode(self):
        """Force the client to try using real data."""
        print("🔧 Forcing real mode - checking availability...")
        self._check_availability()
    
    def get_status(self) -> Dict:
        """Get status information about the client.
        
        Returns:
            Dict containing client status information
        """
        return {
            'using_real_data': self._using_real,
            'real_inverter_host': self.host,
            'real_inverter_available': self.real_client.is_available(),
            'last_availability_check': self._last_check,
            'check_interval_seconds': self.check_interval,
            'mock_client_type': 'enhanced'  # NEW: Indicate we're using enhanced mock
        }
    
    def get_elderly_recommendations(self) -> Dict:
        """Get elderly-specific recommendations from the enhanced mock client.
        
        This method is only available when using the enhanced mock client.
        
        Returns:
            Dict containing elderly-specific recommendations
        """
        if not self._using_real:
            return self.mock_client.get_elderly_recommendations()
        else:
            return {
                'message': 'Elderly recommendations are only available in enhanced mock mode',
                'switch_to_mock': 'Call force_mock_mode() to access elderly recommendations'
            }
    
    def set_manual_solar_percentage(self, percentage: float):
        """Set manual solar production percentage for testing (only works in mock mode).
        
        Args:
            percentage: Solar production percentage (0-100), or None to use automatic mode
        """
        if not self._using_real:
            return self.mock_client.set_manual_solar_percentage(percentage)
        else:
            return {
                'status': 'error',
                'message': 'Manual solar control only available in mock mode'
            }
    
    def set_manual_consumption_watts(self, watts: float):
        """Set manual consumption for testing (only works in mock mode).
        
        Args:
            watts: Consumption in watts, or None to use automatic mode
        """
        if not self._using_real:
            return self.mock_client.set_manual_consumption_watts(watts)
        else:
            return {
                'status': 'error',
                'message': 'Manual consumption control only available in mock mode'
            }
    
    def get_manual_controls(self) -> Dict:
        """Get current manual control settings."""
        if not self._using_real:
            return self.mock_client.get_manual_controls()
        else:
            return {
                'status': 'error',
                'message': 'Manual controls only available in mock mode'
            }
    
    def reset_manual_controls(self):
        """Reset all manual controls to automatic mode."""
        if not self._using_real:
            return self.mock_client.reset_manual_controls()
        else:
            return {
                'status': 'error',
                'message': 'Manual controls only available in mock mode'
            }
