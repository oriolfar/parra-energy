"""
Helper Functions and Utilities for Parra Energy System
======================================================

Common helper functions, formatting utilities, and data processing
functions used across multiple components of the Parra Energy system.

Categories:
    - Data formatting: Power, energy, percentage formatting
    - Mathematical utilities: Safe division, rounding, calculations
    - Time utilities: Timestamp formatting, time zone handling
    - Energy calculations: Self-consumption, autonomy, efficiency
    - Data validation: Input sanitization and validation
    - File utilities: Path handling, file operations

These utilities provide consistent behavior and eliminate code
duplication across the system.
"""

import math
from datetime import datetime, timedelta, timezone
from typing import Union, Optional, Dict, Any, List
from pathlib import Path


def format_power(watts: Union[int, float], precision: int = 1) -> str:
    """
    Format power values with appropriate units (W, kW, MW).
    
    Args:
        watts: Power value in watts
        precision: Decimal places for formatting
        
    Returns:
        Formatted power string with units
        
    Examples:
        format_power(1500) -> "1.5 kW"
        format_power(500) -> "500 W"
        format_power(2500000) -> "2.5 MW"
    """
    if abs(watts) >= 1_000_000:
        return f"{watts / 1_000_000:.{precision}f} MW"
    elif abs(watts) >= 1_000:
        return f"{watts / 1_000:.{precision}f} kW"
    else:
        return f"{watts:.{precision}f} W"


def format_energy(kwh: Union[int, float], precision: int = 2) -> str:
    """
    Format energy values with appropriate units (Wh, kWh, MWh).
    
    Args:
        kwh: Energy value in kilowatt-hours
        precision: Decimal places for formatting
        
    Returns:
        Formatted energy string with units
        
    Examples:
        format_energy(1.5) -> "1.50 kWh"
        format_energy(0.5) -> "500 Wh"
        format_energy(1500) -> "1.50 MWh"
    """
    if abs(kwh) >= 1_000:
        return f"{kwh / 1_000:.{precision}f} MWh"
    elif abs(kwh) >= 1:
        return f"{kwh:.{precision}f} kWh"
    else:
        return f"{kwh * 1_000:.0f} Wh"


def format_percentage(value: Union[int, float], precision: int = 1) -> str:
    """
    Format percentage values with consistent precision.
    
    Args:
        value: Percentage value (0-100)
        precision: Decimal places for formatting
        
    Returns:
        Formatted percentage string
        
    Examples:
        format_percentage(85.6) -> "85.6%"
        format_percentage(100) -> "100.0%"
    """
    return f"{value:.{precision}f}%"


def format_currency(amount: Union[int, float], currency: str = "€", precision: int = 2) -> str:
    """
    Format currency values with appropriate symbol and precision.
    
    Args:
        amount: Currency amount
        currency: Currency symbol
        precision: Decimal places for formatting
        
    Returns:
        Formatted currency string
    """
    return f"{amount:.{precision}f} {currency}"


def safe_divide(numerator: Union[int, float], denominator: Union[int, float], 
                default: Union[int, float] = 0) -> float:
    """
    Safely divide two numbers, handling division by zero.
    
    Args:
        numerator: Dividend
        denominator: Divisor
        default: Value to return if division by zero
        
    Returns:
        Division result or default value
    """
    if denominator == 0:
        return float(default)
    return numerator / denominator


def safe_percentage(part: Union[int, float], total: Union[int, float], 
                   default: float = 0.0) -> float:
    """
    Safely calculate percentage, handling division by zero.
    
    Args:
        part: Partial value
        total: Total value
        default: Value to return if total is zero
        
    Returns:
        Percentage (0-100) or default value
    """
    if total == 0:
        return default
    return min(100.0, max(0.0, (part / total) * 100))


def calculate_self_consumption_rate(production: float, consumption: float, 
                                  grid_export: float = 0) -> float:
    """
    Calculate solar self-consumption rate.
    
    Self-consumption rate = (Production - Export) / Production * 100
    
    Args:
        production: Solar production (W or kWh)
        consumption: House consumption (W or kWh)
        grid_export: Energy exported to grid (W or kWh)
        
    Returns:
        Self-consumption rate as percentage (0-100)
    """
    if production <= 0:
        return 0.0
    
    self_consumed = production - grid_export
    return safe_percentage(self_consumed, production)


def calculate_autonomy_rate(production: float, consumption: float, 
                           grid_import: float = 0) -> float:
    """
    Calculate energy autonomy rate.
    
    Autonomy rate = (Consumption - Import) / Consumption * 100
    
    Args:
        production: Solar production (W or kWh)
        consumption: House consumption (W or kWh)
        grid_import: Energy imported from grid (W or kWh)
        
    Returns:
        Autonomy rate as percentage (0-100)
    """
    if consumption <= 0:
        return 100.0
    
    self_supplied = consumption - grid_import
    return safe_percentage(self_supplied, consumption)


def calculate_energy_efficiency_score(production: float, consumption: float,
                                    weather_quality: float = 100) -> float:
    """
    Calculate overall energy efficiency score.
    
    Considers production vs consumption ratio, adjusted for weather conditions.
    
    Args:
        production: Solar production (kWh)
        consumption: House consumption (kWh)
        weather_quality: Weather quality score (0-100)
        
    Returns:
        Efficiency score (0-100)
    """
    if consumption <= 0:
        return 100.0
    
    # Base efficiency: production to consumption ratio
    production_ratio = safe_percentage(production, consumption)
    
    # Adjust for weather conditions
    weather_factor = weather_quality / 100
    adjusted_production = production_ratio * weather_factor
    
    # Scale to 0-100 range with diminishing returns
    efficiency = min(100, adjusted_production)
    
    return efficiency


def round_to_nearest(value: float, nearest: float = 0.5) -> float:
    """
    Round value to nearest specified increment.
    
    Args:
        value: Value to round
        nearest: Increment to round to
        
    Returns:
        Rounded value
        
    Examples:
        round_to_nearest(1.7, 0.5) -> 1.5
        round_to_nearest(1.8, 0.5) -> 2.0
    """
    return round(value / nearest) * nearest


def clamp(value: Union[int, float], min_val: Union[int, float], 
          max_val: Union[int, float]) -> Union[int, float]:
    """
    Clamp value to specified range.
    
    Args:
        value: Value to clamp
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        Clamped value
    """
    return max(min_val, min(max_val, value))


def format_timestamp(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime with consistent format.
    
    Args:
        dt: Datetime object
        format_str: Format string
        
    Returns:
        Formatted timestamp string
    """
    return dt.strftime(format_str)


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """
    Parse timestamp string with common formats.
    
    Args:
        timestamp_str: Timestamp string
        
    Returns:
        Parsed datetime or None if parsing fails
    """
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(timestamp_str, fmt)
        except ValueError:
            continue
    
    return None


def get_time_range(date_str: str) -> tuple[datetime, datetime]:
    """
    Get start and end datetime for a date string.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        
    Returns:
        Tuple of (start_datetime, end_datetime)
    """
    date = datetime.strptime(date_str, '%Y-%m-%d')
    start = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1) - timedelta(microseconds=1)
    return start, end


def is_business_hours(dt: datetime) -> bool:
    """
    Check if datetime falls within business hours (9 AM - 6 PM, weekdays).
    
    Args:
        dt: Datetime to check
        
    Returns:
        True if within business hours
    """
    return (dt.weekday() < 5 and  # Monday = 0, Friday = 4
            9 <= dt.hour < 18)


def is_peak_solar_hours(dt: datetime) -> bool:
    """
    Check if datetime falls within peak solar hours (10 AM - 4 PM).
    
    Args:
        dt: Datetime to check
        
    Returns:
        True if within peak solar hours
    """
    return 10 <= dt.hour < 16


def calculate_daylight_factor(dt: datetime, latitude: float = 41.7869) -> float:
    """
    Calculate daylight factor based on time of day and season.
    
    Simplified calculation for solar production estimation.
    
    Args:
        dt: Datetime to calculate for
        latitude: Location latitude (default: Agramunt, Spain)
        
    Returns:
        Daylight factor (0-1)
    """
    hour = dt.hour + dt.minute / 60
    
    # Day of year for seasonal adjustment
    day_of_year = dt.timetuple().tm_yday
    
    # Seasonal daylight variation (simplified)
    seasonal_factor = 0.15 * math.cos(2 * math.pi * (day_of_year - 172) / 365)
    base_daylight = 12 + seasonal_factor  # Hours of daylight
    
    # Calculate sunrise and sunset times (simplified)
    sunrise = 12 - base_daylight / 2
    sunset = 12 + base_daylight / 2
    
    # No daylight outside sunrise/sunset
    if hour < sunrise or hour > sunset:
        return 0.0
    
    # Peak daylight at solar noon (12:00)
    solar_noon = 12
    hours_from_noon = abs(hour - solar_noon)
    max_hours_from_noon = base_daylight / 2
    
    # Cosine curve for daylight intensity
    if hours_from_noon >= max_hours_from_noon:
        return 0.0
    
    daylight_factor = math.cos(math.pi * hours_from_noon / max_hours_from_noon)
    return max(0.0, daylight_factor)


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure directory exists, creating it if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        Path object for the directory
    """
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def clean_filename(filename: str) -> str:
    """
    Clean filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Cleaned filename safe for filesystem use
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks of specified size.
    
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple dictionaries, with later dicts taking precedence.
    
    Args:
        *dicts: Dictionaries to merge
        
    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        result.update(d)
    return result


def get_nested_value(data: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    Get nested dictionary value using dot notation.
    
    Args:
        data: Dictionary to search
        key_path: Dot-separated key path (e.g., "level1.level2.key")
        default: Default value if key not found
        
    Returns:
        Found value or default
        
    Examples:
        get_nested_value({"a": {"b": {"c": 42}}}, "a.b.c") -> 42
    """
    keys = key_path.split('.')
    value = data
    
    try:
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default


def flatten_dict(data: Dict[str, Any], prefix: str = "", separator: str = ".") -> Dict[str, Any]:
    """
    Flatten nested dictionary with dot notation keys.
    
    Args:
        data: Dictionary to flatten
        prefix: Key prefix for recursion
        separator: Key separator character
        
    Returns:
        Flattened dictionary
    """
    result = {}
    
    for key, value in data.items():
        new_key = f"{prefix}{separator}{key}" if prefix else key
        
        if isinstance(value, dict):
            result.update(flatten_dict(value, new_key, separator))
        else:
            result[new_key] = value
    
    return result


# Export all helper functions
__all__ = [
    # Formatting functions
    'format_power',
    'format_energy',
    'format_percentage',
    'format_currency',
    'format_timestamp',
    
    # Mathematical utilities
    'safe_divide',
    'safe_percentage',
    'round_to_nearest',
    'clamp',
    
    # Energy calculations
    'calculate_self_consumption_rate',
    'calculate_autonomy_rate',
    'calculate_energy_efficiency_score',
    
    # Time utilities
    'parse_timestamp',
    'get_time_range',
    'is_business_hours',
    'is_peak_solar_hours',
    'calculate_daylight_factor',
    
    # File utilities
    'ensure_directory',
    'clean_filename',
    
    # Data utilities
    'chunk_list',
    'merge_dicts',
    'get_nested_value',
    'flatten_dict',
] 