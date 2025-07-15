"""
Smart Fronius API Client - Intelligent Inverter Detection System
===============================================================

This module provides an intelligent client that automatically detects whether
the real Fronius solar inverter is available and seamlessly falls back to an
enhanced mock client when the real inverter is not accessible.

SYSTEM ARCHITECTURE:
The SmartFroniusClient acts as a transparent proxy between the application
and two possible data sources:

1. REAL FRONIUS INVERTER (Primary):
   - Direct communication with physical Fronius inverter
   - Located at 192.168.1.128 on local network
   - Provides actual real-time solar production data
   - Only available when on the same network as the inverter

2. ENHANCED MOCK CLIENT (Fallback):
   - Sophisticated simulation using real weather data
   - Weather integration via Open-Meteo API for Agramunt, Spain
   - Realistic solar production patterns and household consumption
   - Advanced features for elderly users and testing scenarios

AUTOMATIC DETECTION SYSTEM:
- Continuous monitoring of real inverter availability
- Periodic connectivity checks (configurable interval)
- Seamless switching between real and mock data
- No interruption to application functionality
- Transparent operation - application code remains unchanged

USE CASES:
- HOME NETWORK: Automatically uses real inverter data
- REMOTE ACCESS: Automatically falls back to realistic mock data
- DEMOS: Can be forced to mock mode for consistent presentations
- DEVELOPMENT: Mock mode allows testing without hardware dependency
- ELDERLY USERS: Enhanced mock provides specialized advice and recommendations

SMART FEATURES:
- Zero-configuration operation
- Graceful error handling and recovery
- Status monitoring and reporting
- Manual mode switching for testing
- Enhanced mock features (weather, elderly advice, scenarios)
"""

from typing import Dict
import time
from .fronius import FroniusClient
from .enhanced_mock_fronius import EnhancedMockFroniusClient


class SmartFroniusClient:
    """
    Intelligent Fronius inverter client with automatic real/mock detection.
    
    This client automatically determines whether to use real inverter data
    or fall back to enhanced mock data based on network connectivity and
    inverter availability. It provides a transparent interface that works
    seamlessly in any environment.
    """
    
    def __init__(self, host: str = "192.168.1.128", port: int = 80, check_interval: int = 300):
        """
        Initialize the smart Fronius client with automatic detection.
        
        Args:
            host: IP address of the real Fronius inverter (default: 192.168.1.128)
            port: Port number for inverter communication (default: 80)
            check_interval: Seconds between availability checks (default: 300 = 5 minutes)
            
        The client will immediately attempt to connect to the real inverter
        and fall back to enhanced mock mode if unavailable.
        """
        # Store connection parameters
        self.host = host
        self.port = port
        self.check_interval = check_interval
        
        print(f"🔧 Initializing Smart Fronius Client")
        print(f"   Target inverter: {host}:{port}")
        print(f"   Check interval: {check_interval} seconds")
        
        # Initialize both client types
        # Real client for actual Fronius inverter communication
        self.real_client = FroniusClient(host, port)
        
        # Enhanced mock client with weather integration and advanced features
        self.mock_client = EnhancedMockFroniusClient()
        
        # Internal state tracking
        self._using_real = False  # Current data source (True = real, False = mock)
        self._last_check = 0     # Timestamp of last availability check
        
        # Perform initial availability check to determine which client to use
        print("🔍 Performing initial inverter detection...")
        self._check_availability()
        
    def get_power_data(self) -> Dict:
        """
        Get current power data from the appropriate client (real or mock).
        
        This method automatically handles:
        - Periodic availability checks for the real inverter
        - Seamless switching between real and mock data
        - Error recovery and fallback mechanisms
        - Consistent data format regardless of source
        
        Returns:
            Dict containing power data with keys:
            - P_PV: Solar production (watts)
            - P_Load: House consumption (watts)
            - P_Grid: Grid power (+ importing, - exporting)
            - Additional metrics depending on client type
        """
        # Check if it's time for a periodic availability check
        current_time = time.time()
        if current_time - self._last_check > self.check_interval:
            self._check_availability()
        
        # Route request to appropriate client
        if self._using_real:
            try:
                # Attempt to get data from real inverter
                data = self.real_client.get_power_data()
                
                # Sanity check: if we get all zeros, the inverter might be having issues
                if data.get('P_PV', 0) == 0 and data.get('P_Load', 0) == 0:
                    # Perform quick availability check
                    if not self.real_client.is_available():
                        print("⚠️  Real Fronius client returning zeros - connection issues detected")
                        print("🔄 Switching to enhanced mock data temporarily")
                        self._using_real = False
                        return self.mock_client.get_power_data()
                
                return data
                
            except Exception as e:
                # Handle any errors with real client by falling back to mock
                print(f"❌ Error with real Fronius client: {e}")
                print("🔄 Switching to enhanced mock data")
                self._using_real = False
                return self.mock_client.get_power_data()
        else:
            # Use enhanced mock client
            return self.mock_client.get_power_data()
    
    def _check_availability(self):
        """
        Check if the real Fronius inverter is currently available.
        
        This method:
        1. Updates the last check timestamp
        2. Tests connectivity to the real inverter
        3. Switches data source if availability status changed
        4. Logs status changes for debugging
        """
        self._last_check = time.time()
        
        # Test real inverter availability
        is_available = self.real_client.is_available()
        
        if is_available:
            # Real inverter is available
            if not self._using_real:
                # Status change: switching from mock to real
                print(f"✅ Real Fronius inverter detected at {self.host}")
                print("🔄 Switching to real inverter data")
            self._using_real = True
        else:
            # Real inverter is not available
            if self._using_real:
                # Status change: switching from real to mock
                print(f"❌ Real Fronius inverter at {self.host} not available")
                print("🔄 Switching to enhanced mock data with real weather")
            self._using_real = False
    
    def is_using_real_data(self) -> bool:
        """
        Check if currently using real inverter data.
        
        Returns:
            bool: True if using real Fronius inverter, False if using enhanced mock
        """
        return self._using_real
    
    def force_mock_mode(self):
        """
        Force the client to use enhanced mock data.
        
        This is useful for:
        - Consistent demo presentations
        - Testing enhanced mock features
        - Accessing elderly-specific recommendations
        - Development without hardware dependency
        """
        print("🔧 MANUAL OVERRIDE: Forcing enhanced mock mode")
        print("   Use case: Demo/testing with consistent data")
        self._using_real = False
    
    def force_real_mode(self):
        """
        Force the client to attempt using real inverter data.
        
        This performs an immediate availability check and switches
        to real data if the inverter is accessible.
        """
        print("🔧 MANUAL OVERRIDE: Attempting to use real inverter data")
        print("   Performing immediate availability check...")
        self._check_availability()
        
        if self._using_real:
            print("✅ Successfully connected to real inverter")
        else:
            print("❌ Real inverter still not available - remaining in mock mode")
    
    def get_status(self) -> Dict:
        """
        Get comprehensive status information about the smart client.
        
        Returns:
            Dict containing:
            - using_real_data: Boolean indicating current data source
            - real_inverter_host: IP address of target inverter
            - real_inverter_available: Current availability status
            - last_availability_check: Timestamp of last check
            - check_interval_seconds: Configured check interval
            - mock_client_type: Type of mock client (enhanced)
        """
        return {
            'using_real_data': self._using_real,
            'real_inverter_host': self.host,
            'real_inverter_available': self.real_client.is_available(),
            'last_availability_check': self._last_check,
            'check_interval_seconds': self.check_interval,
            'mock_client_type': 'enhanced_with_weather',
            'features': {
                'weather_integration': not self._using_real,
                'elderly_recommendations': not self._using_real,
                'manual_testing_controls': not self._using_real,
                'scenario_testing': not self._using_real
            }
        }
    
    # =============================================================================
    # ENHANCED MOCK FEATURES (Only available when using mock client)
    # =============================================================================
    
    def get_elderly_recommendations(self) -> Dict:
        """
        Get elderly-specific energy recommendations.
        
        This feature is only available when using the enhanced mock client,
        which provides specialized advice for elderly users in Catalan.
        
        Returns:
            Dict containing elderly-specific recommendations or error if using real data
        """
        if not self._using_real:
            return self.mock_client.get_elderly_recommendations()
        else:
            return {
                'status': 'unavailable',
                'message': 'Elderly recommendations are only available in enhanced mock mode',
                'suggestion': 'Call force_mock_mode() to access elderly-specific features'
            }
    
    def set_manual_solar_percentage(self, percentage: float):
        """
        Set manual solar production percentage for testing scenarios.
        
        This testing feature is only available in mock mode to allow
        simulation of various solar production conditions.
        
        Args:
            percentage: Solar production percentage (0-100), or None for automatic
            
        Returns:
            Result of operation or error if using real data
        """
        if not self._using_real:
            return self.mock_client.set_manual_solar_percentage(percentage)
        else:
            return {
                'status': 'error',
                'message': 'Manual solar control only available in enhanced mock mode',
                'suggestion': 'Call force_mock_mode() to access testing features'
            }
    
    def set_manual_consumption_watts(self, watts: float):
        """
        Set manual consumption for testing scenarios.
        
        This testing feature is only available in mock mode to allow
        simulation of various household consumption patterns.
        
        Args:
            watts: Consumption in watts, or None for automatic patterns
            
        Returns:
            Result of operation or error if using real data
        """
        if not self._using_real:
            return self.mock_client.set_manual_consumption_watts(watts)
        else:
            return {
                'status': 'error',
                'message': 'Manual consumption control only available in enhanced mock mode',
                'suggestion': 'Call force_mock_mode() to access testing features'
            }
    
    def get_manual_controls(self) -> Dict:
        """
        Get current manual control settings.
        
        Returns current testing override settings or error if using real data.
        """
        if not self._using_real:
            return self.mock_client.get_manual_controls()
        else:
            return {
                'status': 'error',
                'message': 'Manual controls only available in enhanced mock mode',
                'current_mode': 'real_data',
                'suggestion': 'Call force_mock_mode() to access testing controls'
            }
    
    def reset_manual_controls(self):
        """
        Reset all manual testing controls to automatic mode.
        
        Returns result of operation or error if using real data.
        """
        if not self._using_real:
            return self.mock_client.reset_manual_controls()
        else:
            return {
                'status': 'error',
                'message': 'Manual controls only available in enhanced mock mode',
                'suggestion': 'Call force_mock_mode() to access testing features'
            }
