"""
Centralized Configuration Settings for Parra Energy System
==========================================================

This module provides centralized configuration management using dataclasses
to define system-wide settings, environment configurations, and default values
for all components of the Parra Energy system.

Configuration Categories:
    - SystemConfig: Solar system specifications and hardware settings
    - WebConfig: Flask web application configuration
    - DatabaseConfig: Database connection and storage settings
    - WeatherConfig: Weather service and location settings
    - LoggingConfig: Logging levels and output configuration

The configuration system supports:
    - Environment variable overrides
    - Development vs production settings
    - Validation of configuration values
    - Type safety with dataclasses
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class SystemConfig:
    """
    Solar system hardware and physical configuration.
    
    Defines the physical characteristics of the solar installation,
    target hardware, and operational parameters.
    """
    # Solar System Specifications
    solar_capacity_watts: int = 2200  # 2.2kW solar panel capacity
    inverter_host: str = "192.168.1.128"  # Fronius inverter IP address
    inverter_port: int = 80  # Fronius inverter HTTP port
    
    # System Location (Agramunt, Spain - Grandfather's house)
    latitude: float = 41.7869  # Degrees North
    longitude: float = 1.0968  # Degrees East
    timezone: str = "Europe/Madrid"
    location_name: str = "Agramunt, Spain"
    
    # Operational Parameters
    data_collection_interval: int = 5  # Seconds between real-time updates
    database_storage_interval: int = 300  # Seconds between database storage (5 minutes)
    inverter_check_interval: int = 300  # Seconds between inverter availability checks
    
    # Device Automation Settings
    automation_enabled: bool = True
    surplus_threshold_watts: int = 100  # Minimum surplus for device activation


@dataclass  
class WebConfig:
    """
    Flask web application configuration.
    
    Defines web server settings, session configuration,
    and dashboard behavior.
    """
    # Web Server Settings
    host: str = "localhost"
    port: int = 5001
    debug: bool = False
    auto_open_browser: bool = True
    browser_delay_seconds: int = 3
    
    # Session Configuration
    secret_key: str = "parra_energy_secret_key_change_in_production"
    session_timeout_hours: int = 24
    
    # Dashboard Configuration
    default_dashboard_mode: str = "technical"  # "technical" or "elderly"
    supported_languages: list = None
    
    def __post_init__(self):
        if self.supported_languages is None:
            self.supported_languages = ["ca", "es", "en"]  # Catalan, Spanish, English


@dataclass
class DatabaseConfig:
    """
    Database configuration and connection settings.
    
    Defines database file locations, connection parameters,
    and data retention policies.
    """
    # Database File Paths
    main_db_path: str = "data/energy_data.db"
    backup_db_path: str = "data/backups/energy_data_backup.db"
    
    # Data Retention Settings
    keep_raw_data_days: int = 365  # Keep 1 year of 5-minute data
    keep_hourly_data_days: int = 1095  # Keep 3 years of hourly averages
    keep_daily_data_days: int = 3650  # Keep 10 years of daily summaries
    
    # Database Performance
    connection_timeout: int = 30  # Seconds
    enable_wal_mode: bool = True  # Write-Ahead Logging for better performance
    vacuum_interval_days: int = 30  # Database optimization interval


@dataclass
class WeatherConfig:
    """
    Weather service configuration and API settings.
    
    Defines weather data source, caching behavior,
    and forecast parameters.
    """
    # Weather API Configuration
    api_base_url: str = "https://api.open-meteo.com/v1/forecast"
    cache_duration_hours: int = 1  # Cache weather data for 1 hour
    retry_attempts: int = 5
    retry_delay_seconds: float = 0.2
    
    # Forecast Settings
    forecast_days: int = 7  # Number of days to forecast
    historical_days: int = 30  # Days of historical weather to keep
    
    # Weather Quality Scoring
    excellent_cloud_cover_max: int = 10  # % cloud cover for excellent conditions
    good_cloud_cover_max: int = 30  # % cloud cover for good conditions
    fair_cloud_cover_max: int = 60  # % cloud cover for fair conditions


@dataclass
class LoggingConfig:
    """
    Logging configuration and output settings.
    
    Defines logging levels, file outputs, and
    console formatting options.
    """
    # Logging Levels
    console_level: str = "WARNING"  # DEBUG, INFO, WARNING, ERROR, CRITICAL (reduced verbosity)
    file_level: str = "INFO"  # Reduced from DEBUG
    quiet_mode: bool = True  # Suppress verbose startup and operation messages
    
    # Log File Configuration
    log_file_path: str = "logs/parra_energy.log"
    max_file_size_mb: int = 10
    backup_count: int = 5  # Number of rotated log files to keep
    
    # Output Formatting
    include_timestamps: bool = True
    include_module_names: bool = True
    colored_console_output: bool = True


class Config:
    """
    Main configuration class that aggregates all system settings.
    
    This class provides a single point of access to all configuration
    settings and handles environment variable overrides.
    """
    
    def __init__(self, environment: str = "development"):
        """
        Initialize configuration with environment-specific settings.
        
        Args:
            environment: "development", "production", or "testing"
        """
        self.environment = environment
        
        # Initialize configuration components
        self.system = SystemConfig()
        self.web = WebConfig()
        self.database = DatabaseConfig()
        self.weather = WeatherConfig()
        self.logging = LoggingConfig()
        
        # Apply environment-specific overrides
        self._apply_environment_overrides()
        self._apply_environment_variables()
    
    def _apply_environment_overrides(self):
        """Apply environment-specific configuration overrides."""
        
        if self.environment == "production":
            # Production settings
            self.web.debug = False
            self.web.secret_key = os.getenv("FLASK_SECRET_KEY", self.web.secret_key)
            self.logging.console_level = "WARNING"
            self.logging.colored_console_output = False
            
        elif self.environment == "testing":
            # Testing settings
            self.database.main_db_path = "test_data/test_energy_data.db"
            self.system.data_collection_interval = 1  # Faster for tests
            self.web.auto_open_browser = False
            self.logging.console_level = "DEBUG"
            
        elif self.environment == "development":
            # Development settings (defaults are already suitable)
            self.web.debug = True
            self.logging.console_level = "DEBUG"
            self.logging.colored_console_output = True
    
    def _apply_environment_variables(self):
        """Apply environment variable overrides for sensitive settings."""
        
        # Database configuration
        if os.getenv("DATABASE_PATH"):
            self.database.main_db_path = os.getenv("DATABASE_PATH")
        
        # Web configuration
        if os.getenv("WEB_HOST"):
            self.web.host = os.getenv("WEB_HOST")
        if os.getenv("WEB_PORT"):
            self.web.port = int(os.getenv("WEB_PORT"))
        if os.getenv("FLASK_SECRET_KEY"):
            self.web.secret_key = os.getenv("FLASK_SECRET_KEY")
        
        # System configuration
        if os.getenv("INVERTER_HOST"):
            self.system.inverter_host = os.getenv("INVERTER_HOST")
        if os.getenv("INVERTER_PORT"):
            self.system.inverter_port = int(os.getenv("INVERTER_PORT"))
        
        # Logging configuration
        if os.getenv("LOG_LEVEL"):
            self.logging.console_level = os.getenv("LOG_LEVEL").upper()
    
    def validate(self) -> bool:
        """
        Validate configuration settings for consistency and correctness.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Validate system configuration
            assert 0 < self.system.solar_capacity_watts <= 50000, "Solar capacity must be reasonable"
            assert 1 <= self.system.data_collection_interval <= 3600, "Collection interval must be 1-3600 seconds"
            
            # Validate web configuration  
            assert 1024 <= self.web.port <= 65535, "Web port must be in valid range"
            assert self.web.default_dashboard_mode in ["technical", "elderly"], "Invalid dashboard mode"
            
            # Validate database configuration
            assert self.database.keep_raw_data_days > 0, "Data retention must be positive"
            
            # Validate weather configuration
            assert 1 <= self.weather.forecast_days <= 14, "Forecast days must be 1-14"
            
            return True
            
        except AssertionError as e:
            print(f"Configuration validation error: {e}")
            return False
    
    def get_database_url(self) -> str:
        """Get SQLite database connection URL."""
        return f"sqlite:///{self.database.main_db_path}"
    
    def get_weather_coordinates(self) -> tuple[float, float]:
        """Get weather service coordinates as (latitude, longitude) tuple."""
        return (self.system.latitude, self.system.longitude)
    
    def __repr__(self) -> str:
        return f"Config(environment='{self.environment}', solar_capacity={self.system.solar_capacity_watts}W)"


# Create default configuration instance
default_config = Config()

# Export common configurations for convenience
Config.DEVELOPMENT = Config("development")
Config.PRODUCTION = Config("production") 
Config.TESTING = Config("testing") 