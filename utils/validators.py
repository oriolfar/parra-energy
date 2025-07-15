"""
Data Validation Utilities for Parra Energy System
=================================================

Input validation, data verification, and configuration validation
functions for the Parra Energy system. Ensures data integrity
and system reliability through comprehensive validation.

Validation Categories:
    - Power data validation: Solar production, consumption, grid flow
    - Configuration validation: System settings, limits, ranges
    - Location validation: Coordinates, timezone, weather data
    - Timestamp validation: Date ranges, formats, chronology
    - Device validation: Device parameters, automation settings
    - API validation: Request parameters, response data

These validators help prevent errors, ensure data quality,
and provide meaningful error messages for debugging.
"""

import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """
    Result of a validation operation.
    
    Attributes:
        is_valid: Whether validation passed
        errors: List of error messages (empty if valid)
        warnings: List of warning messages
        normalized_data: Validated and normalized data (if applicable)
    """
    is_valid: bool
    errors: List[str]
    warnings: List[str] = None
    normalized_data: Any = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


def validate_power_data(data: Dict[str, Any]) -> ValidationResult:
    """
    Validate power data from Fronius inverter or mock client.
    
    Args:
        data: Power data dictionary containing P_PV, P_Load, P_Grid, etc.
        
    Returns:
        ValidationResult with validation status and normalized data
    """
    errors = []
    warnings = []
    normalized = {}
    
    # Required fields for power data
    required_fields = ['P_PV', 'P_Load']
    
    # Check required fields
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(data[field], (int, float)):
            errors.append(f"Field {field} must be numeric, got {type(data[field])}")
        else:
            normalized[field] = float(data[field])
    
    # If basic validation failed, return early
    if errors:
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
    
    # Validate power ranges (reasonable limits for 2.2kW system)
    max_solar_power = 3000  # 3kW max (20% over rated capacity)
    max_consumption = 10000  # 10kW max consumption
    
    # Solar production validation
    if normalized['P_PV'] < 0:
        errors.append("Solar production (P_PV) cannot be negative")
    elif normalized['P_PV'] > max_solar_power:
        warnings.append(f"Solar production ({normalized['P_PV']}W) exceeds expected maximum ({max_solar_power}W)")
    
    # Consumption validation
    if normalized['P_Load'] < 0:
        warnings.append("House consumption (P_Load) is negative - unusual but possible")
    elif normalized['P_Load'] > max_consumption:
        warnings.append(f"House consumption ({normalized['P_Load']}W) is very high ({max_consumption}W+)")
    
    # Grid power validation (if provided)
    if 'P_Grid' in data:
        if isinstance(data['P_Grid'], (int, float)):
            normalized['P_Grid'] = float(data['P_Grid'])
            
            # Basic energy balance check
            calculated_grid = normalized['P_Load'] - normalized['P_PV']
            actual_grid = normalized['P_Grid']
            
            # Allow 10% tolerance for measurement errors
            tolerance = 0.1 * max(abs(calculated_grid), 100)  # At least 100W tolerance
            
            if abs(calculated_grid - actual_grid) > tolerance:
                warnings.append(
                    f"Energy balance mismatch: calculated grid {calculated_grid:.0f}W, "
                    f"actual grid {actual_grid:.0f}W (tolerance: {tolerance:.0f}W)"
                )
    
    # Calculate derived metrics if not provided
    if 'self_consumption_rate' not in data:
        if normalized['P_PV'] > 0:
            self_consumed = min(normalized['P_PV'], normalized['P_Load'])
            normalized['self_consumption_rate'] = (self_consumed / normalized['P_PV']) * 100
        else:
            normalized['self_consumption_rate'] = 0.0
    
    if 'autonomy_rate' not in data:
        if normalized['P_Load'] > 0:
            self_supplied = min(normalized['P_PV'], normalized['P_Load'])
            normalized['autonomy_rate'] = (self_supplied / normalized['P_Load']) * 100
        else:
            normalized['autonomy_rate'] = 100.0
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        normalized_data=normalized
    )


def validate_coordinates(latitude: float, longitude: float, 
                        location_name: str = "Unknown") -> ValidationResult:
    """
    Validate geographical coordinates.
    
    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        location_name: Human-readable location name
        
    Returns:
        ValidationResult with validation status
    """
    errors = []
    warnings = []
    
    # Validate latitude range
    if not isinstance(latitude, (int, float)):
        errors.append(f"Latitude must be numeric, got {type(latitude)}")
    elif not -90 <= latitude <= 90:
        errors.append(f"Latitude {latitude} must be between -90 and 90 degrees")
    
    # Validate longitude range
    if not isinstance(longitude, (int, float)):
        errors.append(f"Longitude must be numeric, got {type(longitude)}")
    elif not -180 <= longitude <= 180:
        errors.append(f"Longitude {longitude} must be between -180 and 180 degrees")
    
    # If basic validation passed, check for reasonable values
    if not errors:
        # Check if coordinates are in a reasonable range for Spain
        spain_lat_range = (35.0, 44.0)  # Approximate latitude range for Spain
        spain_lon_range = (-10.0, 5.0)  # Approximate longitude range for Spain
        
        if not (spain_lat_range[0] <= latitude <= spain_lat_range[1] and
                spain_lon_range[0] <= longitude <= spain_lon_range[1]):
            warnings.append(
                f"Coordinates ({latitude}, {longitude}) for '{location_name}' "
                f"appear to be outside Spain - please verify"
            )
        
        # Check for exact zeros (often indicates missing data)
        if latitude == 0.0 and longitude == 0.0:
            warnings.append("Coordinates (0, 0) likely indicate missing location data")
    
    normalized_data = {
        'latitude': float(latitude) if not errors else None,
        'longitude': float(longitude) if not errors else None,
        'location_name': location_name
    }
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        normalized_data=normalized_data
    )


def validate_config(config: Dict[str, Any]) -> ValidationResult:
    """
    Validate system configuration parameters.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        ValidationResult with validation status
    """
    errors = []
    warnings = []
    normalized = config.copy()
    
    # Define expected configuration parameters with validation rules
    config_rules = {
        'solar_capacity_watts': {
            'type': (int, float),
            'min': 100,
            'max': 50000,
            'description': 'Solar capacity in watts'
        },
        'inverter_host': {
            'type': str,
            'pattern': r'^(\d{1,3}\.){3}\d{1,3}$',  # Basic IP pattern
            'description': 'Inverter IP address'
        },
        'inverter_port': {
            'type': int,
            'min': 1,
            'max': 65535,
            'description': 'Inverter port number'
        },
        'data_collection_interval': {
            'type': int,
            'min': 1,
            'max': 3600,
            'description': 'Data collection interval in seconds'
        },
        'web_port': {
            'type': int,
            'min': 1024,
            'max': 65535,
            'description': 'Web server port'
        }
    }
    
    # Validate each configuration parameter
    for param, rules in config_rules.items():
        if param in config:
            value = config[param]
            
            # Type validation
            if not isinstance(value, rules['type']):
                errors.append(
                    f"{rules['description']} ({param}) must be {rules['type']}, "
                    f"got {type(value)}"
                )
                continue
            
            # Range validation
            if 'min' in rules and value < rules['min']:
                errors.append(
                    f"{rules['description']} ({param}) must be >= {rules['min']}, "
                    f"got {value}"
                )
            
            if 'max' in rules and value > rules['max']:
                errors.append(
                    f"{rules['description']} ({param}) must be <= {rules['max']}, "
                    f"got {value}"
                )
            
            # Pattern validation (for strings)
            if 'pattern' in rules and isinstance(value, str):
                if not re.match(rules['pattern'], value):
                    errors.append(
                        f"{rules['description']} ({param}) format is invalid: {value}"
                    )
    
    # Cross-parameter validation
    if 'web_port' in config and 'inverter_port' in config:
        if config['web_port'] == config['inverter_port']:
            warnings.append("Web port and inverter port are the same - this may cause conflicts")
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        normalized_data=normalized
    )


def validate_timestamp(timestamp: Union[str, datetime], 
                      allow_future: bool = False,
                      max_age_days: Optional[int] = None) -> ValidationResult:
    """
    Validate timestamp format and reasonableness.
    
    Args:
        timestamp: Timestamp string or datetime object
        allow_future: Whether future timestamps are allowed
        max_age_days: Maximum age in days (None for no limit)
        
    Returns:
        ValidationResult with validation status and parsed datetime
    """
    errors = []
    warnings = []
    parsed_datetime = None
    
    # Parse timestamp if it's a string
    if isinstance(timestamp, str):
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
        ]
        
        for fmt in formats:
            try:
                parsed_datetime = datetime.strptime(timestamp, fmt)
                break
            except ValueError:
                continue
        
        if parsed_datetime is None:
            errors.append(f"Invalid timestamp format: {timestamp}")
            return ValidationResult(is_valid=False, errors=errors)
    
    elif isinstance(timestamp, datetime):
        parsed_datetime = timestamp
    else:
        errors.append(f"Timestamp must be string or datetime, got {type(timestamp)}")
        return ValidationResult(is_valid=False, errors=errors)
    
    # Validate timestamp reasonableness
    now = datetime.now()
    
    # Future timestamp check
    if not allow_future and parsed_datetime > now:
        errors.append(f"Future timestamp not allowed: {parsed_datetime}")
    
    # Age check
    if max_age_days is not None:
        max_age = timedelta(days=max_age_days)
        if now - parsed_datetime > max_age:
            warnings.append(f"Timestamp is older than {max_age_days} days: {parsed_datetime}")
    
    # Very old timestamp check (likely indicates data error)
    epoch_start = datetime(1970, 1, 1)
    if parsed_datetime < epoch_start:
        errors.append(f"Timestamp predates Unix epoch: {parsed_datetime}")
    
    # Very future timestamp check (likely indicates data error)
    far_future = now + timedelta(days=365 * 10)  # 10 years in future
    if parsed_datetime > far_future:
        warnings.append(f"Timestamp is far in future: {parsed_datetime}")
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        normalized_data=parsed_datetime
    )


def validate_device_params(name: str, power_consumption: float, 
                          device_type: str = "unknown",
                          priority: int = 5) -> ValidationResult:
    """
    Validate device parameters for automation system.
    
    Args:
        name: Device name
        power_consumption: Power consumption in watts
        device_type: Device category/type
        priority: Automation priority (1-10)
        
    Returns:
        ValidationResult with validation status
    """
    errors = []
    warnings = []
    
    # Validate device name
    if not isinstance(name, str):
        errors.append(f"Device name must be string, got {type(name)}")
    elif len(name.strip()) == 0:
        errors.append("Device name cannot be empty")
    elif len(name) > 100:
        errors.append(f"Device name too long ({len(name)} chars, max 100)")
    
    # Validate power consumption
    if not isinstance(power_consumption, (int, float)):
        errors.append(f"Power consumption must be numeric, got {type(power_consumption)}")
    elif power_consumption < 0:
        errors.append("Power consumption cannot be negative")
    elif power_consumption == 0:
        warnings.append("Device has zero power consumption")
    elif power_consumption > 15000:  # 15kW is very high for household device
        warnings.append(f"Power consumption is very high: {power_consumption}W")
    
    # Validate priority
    if not isinstance(priority, int):
        errors.append(f"Priority must be integer, got {type(priority)}")
    elif not 1 <= priority <= 10:
        errors.append(f"Priority must be 1-10, got {priority}")
    
    # Validate device type
    valid_types = [
        'lighting', 'heating', 'cooling', 'appliance', 'ev_charger', 
        'pool_pump', 'water_heater', 'ventilation', 'security', 'unknown'
    ]
    
    if device_type not in valid_types:
        warnings.append(f"Unknown device type: {device_type}")
    
    normalized_data = {
        'name': name.strip() if isinstance(name, str) else name,
        'power_consumption': float(power_consumption) if not errors else None,
        'device_type': device_type,
        'priority': priority
    }
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        normalized_data=normalized_data
    )


def validate_weather_data(data: Dict[str, Any]) -> ValidationResult:
    """
    Validate weather data from Open-Meteo API or other sources.
    
    Args:
        data: Weather data dictionary
        
    Returns:
        ValidationResult with validation status
    """
    errors = []
    warnings = []
    normalized = {}
    
    # Define expected weather parameters with validation ranges
    weather_params = {
        'temperature_2m': {'min': -50, 'max': 60, 'unit': '°C'},
        'cloud_cover': {'min': 0, 'max': 100, 'unit': '%'},
        'direct_radiation': {'min': 0, 'max': 1500, 'unit': 'W/m²'},
        'wind_speed_10m': {'min': 0, 'max': 200, 'unit': 'm/s'},
        'precipitation': {'min': 0, 'max': 1000, 'unit': 'mm'},
        'uv_index': {'min': 0, 'max': 15, 'unit': 'index'},
    }
    
    # Validate each weather parameter
    for param, limits in weather_params.items():
        if param in data:
            value = data[param]
            
            # Type validation
            if not isinstance(value, (int, float, type(None))):
                errors.append(f"{param} must be numeric or None, got {type(value)}")
                continue
            
            # None values are acceptable for weather data
            if value is None:
                normalized[param] = None
                continue
            
            # Range validation
            if value < limits['min'] or value > limits['max']:
                warnings.append(
                    f"{param} value {value} {limits['unit']} is outside "
                    f"expected range ({limits['min']}-{limits['max']} {limits['unit']})"
                )
            
            normalized[param] = float(value)
    
    # Cross-parameter validation
    if 'cloud_cover' in normalized and 'direct_radiation' in normalized:
        cloud_cover = normalized.get('cloud_cover', 0)
        direct_radiation = normalized.get('direct_radiation', 0)
        
        # High radiation with high cloud cover is suspicious
        if cloud_cover > 80 and direct_radiation > 500:
            warnings.append(
                f"High direct radiation ({direct_radiation} W/m²) with high cloud cover "
                f"({cloud_cover}%) - unusual weather conditions"
            )
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        normalized_data=normalized
    )


def validate_energy_reading(production: float, consumption: float,
                           timestamp: Union[str, datetime]) -> ValidationResult:
    """
    Validate complete energy reading for database storage.
    
    Args:
        production: Solar production in watts
        consumption: House consumption in watts
        timestamp: Reading timestamp
        
    Returns:
        ValidationResult with validation status
    """
    errors = []
    warnings = []
    
    # Validate power data
    power_result = validate_power_data({
        'P_PV': production,
        'P_Load': consumption
    })
    
    errors.extend(power_result.errors)
    warnings.extend(power_result.warnings)
    
    # Validate timestamp
    timestamp_result = validate_timestamp(timestamp, allow_future=False, max_age_days=30)
    
    errors.extend(timestamp_result.errors)
    warnings.extend(timestamp_result.warnings)
    
    # Create normalized data if validation passed
    normalized_data = None
    if len(errors) == 0:
        normalized_data = {
            'production': power_result.normalized_data['P_PV'],
            'consumption': power_result.normalized_data['P_Load'],
            'timestamp': timestamp_result.normalized_data.isoformat(),
            'self_consumption_rate': power_result.normalized_data.get('self_consumption_rate'),
            'autonomy_rate': power_result.normalized_data.get('autonomy_rate')
        }
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        normalized_data=normalized_data
    )


# Export all validation functions
__all__ = [
    'ValidationResult',
    'validate_power_data',
    'validate_coordinates',
    'validate_config',
    'validate_timestamp',
    'validate_device_params',
    'validate_weather_data',
    'validate_energy_reading',
] 