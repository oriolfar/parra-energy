"""
Unit Tests for Parra Energy Utilities
=====================================

Tests for helper functions, validators, and utility modules
used throughout the Parra Energy system.
"""

import pytest
import sqlite3
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import sys

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.helpers import (
    format_power, format_energy, format_percentage, safe_divide,
    calculate_self_consumption_rate, calculate_autonomy_rate,
    parse_timestamp, get_time_range, is_peak_solar_hours
)
from utils.validators import (
    validate_power_data, validate_coordinates, validate_config,
    validate_timestamp, ValidationResult
)
from utils.database import (
    DatabaseManager, create_tables, store_energy_reading,
    get_energy_data
)


class TestHelperFunctions:
    """Test utility helper functions."""
    
    def test_format_power(self):
        """Test power formatting with different units."""
        assert format_power(500) == "500.0 W"
        assert format_power(1500) == "1.5 kW"
        assert format_power(2500000) == "2.5 MW"
        assert format_power(1500, precision=0) == "2 kW"
    
    def test_format_energy(self):
        """Test energy formatting with different units."""
        assert format_energy(1.5) == "1.50 kWh"
        assert format_energy(0.5) == "500 Wh"
        assert format_energy(1500) == "1.50 MWh"
        assert format_energy(0.001) == "1 Wh"
    
    def test_format_percentage(self):
        """Test percentage formatting."""
        assert format_percentage(85.6) == "85.6%"
        assert format_percentage(100, precision=0) == "100%"
        assert format_percentage(33.333, precision=2) == "33.33%"
    
    def test_safe_divide(self):
        """Test safe division with zero handling."""
        assert safe_divide(10, 2) == 5.0
        assert safe_divide(10, 0) == 0.0
        assert safe_divide(10, 0, default=99) == 99.0
    
    def test_calculate_self_consumption_rate(self):
        """Test self-consumption rate calculation."""
        # Full self-consumption
        assert calculate_self_consumption_rate(1000, 1000) == 100.0
        
        # Partial self-consumption (excess solar)
        assert calculate_self_consumption_rate(1000, 500) == 50.0
        
        # No solar production
        assert calculate_self_consumption_rate(0, 500) == 0.0
        
        # With grid export
        assert calculate_self_consumption_rate(1000, 500, grid_export=300) == 70.0
    
    def test_calculate_autonomy_rate(self):
        """Test autonomy rate calculation."""
        # Full autonomy
        assert calculate_autonomy_rate(1000, 500) == 100.0
        
        # Partial autonomy (need grid import)
        assert calculate_autonomy_rate(500, 1000) == 50.0
        
        # No consumption
        assert calculate_autonomy_rate(1000, 0) == 100.0
        
        # With grid import
        assert calculate_autonomy_rate(500, 1000, grid_import=300) == 70.0
    
    def test_parse_timestamp(self):
        """Test timestamp parsing with various formats."""
        # ISO format
        dt1 = parse_timestamp("2024-01-15 14:30:00")
        assert dt1.year == 2024
        assert dt1.month == 1
        assert dt1.day == 15
        assert dt1.hour == 14
        assert dt1.minute == 30
        
        # T separator
        dt2 = parse_timestamp("2024-01-15T14:30:00")
        assert dt2 == dt1
        
        # Date only
        dt3 = parse_timestamp("2024-01-15")
        assert dt3.date() == dt1.date()
        
        # Invalid format
        assert parse_timestamp("invalid") is None
    
    def test_get_time_range(self):
        """Test time range generation for dates."""
        start, end = get_time_range("2024-01-15")
        
        assert start.year == 2024
        assert start.month == 1
        assert start.day == 15
        assert start.hour == 0
        assert start.minute == 0
        
        assert end.year == 2024
        assert end.month == 1
        assert end.day == 15
        assert end.hour == 23
        assert end.minute == 59
    
    def test_is_peak_solar_hours(self):
        """Test peak solar hours detection."""
        # Peak hours (10 AM - 4 PM)
        assert is_peak_solar_hours(datetime(2024, 1, 15, 12, 0))  # Noon
        assert is_peak_solar_hours(datetime(2024, 1, 15, 10, 0))  # 10 AM
        assert is_peak_solar_hours(datetime(2024, 1, 15, 15, 59))  # 3:59 PM
        
        # Non-peak hours
        assert not is_peak_solar_hours(datetime(2024, 1, 15, 9, 59))  # 9:59 AM
        assert not is_peak_solar_hours(datetime(2024, 1, 15, 16, 0))  # 4 PM
        assert not is_peak_solar_hours(datetime(2024, 1, 15, 20, 0))  # 8 PM


class TestValidators:
    """Test data validation functions."""
    
    def test_validate_power_data_valid(self):
        """Test power data validation with valid input."""
        data = {
            'P_PV': 1500.0,
            'P_Load': 800.0,
            'P_Grid': -700.0  # Exporting
        }
        
        result = validate_power_data(data)
        assert result.is_valid
        assert len(result.errors) == 0
        assert result.normalized_data['P_PV'] == 1500.0
        assert result.normalized_data['P_Load'] == 800.0
    
    def test_validate_power_data_missing_fields(self):
        """Test power data validation with missing required fields."""
        data = {'P_PV': 1500.0}  # Missing P_Load
        
        result = validate_power_data(data)
        assert not result.is_valid
        assert any("Missing required field: P_Load" in error for error in result.errors)
    
    def test_validate_power_data_invalid_types(self):
        """Test power data validation with invalid data types."""
        data = {
            'P_PV': "invalid",  # Should be numeric
            'P_Load': 800.0
        }
        
        result = validate_power_data(data)
        assert not result.is_valid
        assert any("must be numeric" in error for error in result.errors)
    
    def test_validate_power_data_negative_production(self):
        """Test power data validation with negative solar production."""
        data = {
            'P_PV': -100.0,  # Negative solar production
            'P_Load': 800.0
        }
        
        result = validate_power_data(data)
        assert not result.is_valid
        assert any("cannot be negative" in error for error in result.errors)
    
    def test_validate_coordinates_valid(self):
        """Test coordinate validation with valid Spanish coordinates."""
        result = validate_coordinates(41.7869, 1.0968, "Agramunt, Spain")
        
        assert result.is_valid
        assert len(result.errors) == 0
        assert result.normalized_data['latitude'] == 41.7869
        assert result.normalized_data['longitude'] == 1.0968
    
    def test_validate_coordinates_out_of_range(self):
        """Test coordinate validation with out-of-range values."""
        # Invalid latitude
        result1 = validate_coordinates(95.0, 1.0, "Invalid")
        assert not result1.is_valid
        assert any("must be between -90 and 90" in error for error in result1.errors)
        
        # Invalid longitude
        result2 = validate_coordinates(41.0, 185.0, "Invalid")
        assert not result2.is_valid
        assert any("must be between -180 and 180" in error for error in result2.errors)
    
    def test_validate_config_valid(self):
        """Test configuration validation with valid settings."""
        config = {
            'solar_capacity_watts': 2200,
            'inverter_host': '192.168.1.128',
            'inverter_port': 80,
            'data_collection_interval': 5,
            'web_port': 5001
        }
        
        result = validate_config(config)
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_config_invalid_ranges(self):
        """Test configuration validation with values outside valid ranges."""
        config = {
            'solar_capacity_watts': -100,  # Negative capacity
            'inverter_port': 70000,        # Port too high
            'data_collection_interval': 0  # Interval too low
        }
        
        result = validate_config(config)
        assert not result.is_valid
        assert len(result.errors) >= 3
    
    def test_validate_timestamp_valid(self):
        """Test timestamp validation with valid timestamps."""
        now = datetime.now()
        past = now - timedelta(hours=1)
        
        # Past timestamp (should be valid)
        result = validate_timestamp(past.isoformat())
        assert result.is_valid
        assert result.normalized_data == past
    
    def test_validate_timestamp_future_not_allowed(self):
        """Test timestamp validation with future timestamps when not allowed."""
        future = datetime.now() + timedelta(hours=1)
        
        result = validate_timestamp(future.isoformat(), allow_future=False)
        assert not result.is_valid
        assert any("Future timestamp not allowed" in error for error in result.errors)
    
    def test_validate_timestamp_future_allowed(self):
        """Test timestamp validation with future timestamps when allowed."""
        future = datetime.now() + timedelta(hours=1)
        
        result = validate_timestamp(future.isoformat(), allow_future=True)
        assert result.is_valid


class TestDatabaseManager:
    """Test database management utilities."""
    
    def setup_method(self):
        """Set up test database for each test."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self.db_manager = DatabaseManager(self.db_path)
    
    def teardown_method(self):
        """Clean up test database after each test."""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_database_manager_initialization(self):
        """Test database manager initialization."""
        assert self.db_manager.db_path == self.db_path
        assert os.path.exists(os.path.dirname(self.db_path))
    
    def test_get_connection_context_manager(self):
        """Test database connection context manager."""
        with self.db_manager.get_connection() as conn:
            assert isinstance(conn, sqlite3.Connection)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1
    
    def test_execute_query(self):
        """Test query execution."""
        # Create a test table
        with self.db_manager.get_connection() as conn:
            conn.execute("CREATE TABLE test (id INTEGER, value TEXT)")
            conn.execute("INSERT INTO test VALUES (1, 'hello'), (2, 'world')")
            conn.commit()
        
        # Query the table
        results = self.db_manager.execute_query("SELECT * FROM test ORDER BY id")
        assert len(results) == 2
        assert results[0] == (1, 'hello')
        assert results[1] == (2, 'world')
    
    def test_execute_query_with_row_factory(self):
        """Test query execution with row factory for dict-like access."""
        # Create and populate test table
        with self.db_manager.get_connection() as conn:
            conn.execute("CREATE TABLE test (id INTEGER, value TEXT)")
            conn.execute("INSERT INTO test VALUES (1, 'hello')")
            conn.commit()
        
        # Query with row factory
        results = self.db_manager.execute_query("SELECT * FROM test", row_factory=True)
        assert len(results) == 1
        assert results[0]['id'] == 1
        assert results[0]['value'] == 'hello'
    
    def test_execute_update(self):
        """Test update/insert/delete operations."""
        # Create test table
        with self.db_manager.get_connection() as conn:
            conn.execute("CREATE TABLE test (id INTEGER, value TEXT)")
            conn.commit()
        
        # Insert data
        rows_affected = self.db_manager.execute_update(
            "INSERT INTO test VALUES (?, ?)", (1, 'test')
        )
        assert rows_affected == 1
        
        # Update data
        rows_affected = self.db_manager.execute_update(
            "UPDATE test SET value = ? WHERE id = ?", ('updated', 1)
        )
        assert rows_affected == 1
        
        # Verify update
        results = self.db_manager.execute_query("SELECT value FROM test WHERE id = 1")
        assert results[0][0] == 'updated'
    
    def test_create_tables(self):
        """Test database table creation."""
        create_tables(self.db_path)
        
        # Verify main tables exist
        tables = self.db_manager.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        table_names = [table[0] for table in tables]
        
        expected_tables = [
            'energy', 'daily_energy', 'weather_forecast', 'weather_daily',
            'daily_analytics', 'optimization_insights', 'devices', 'automation_events'
        ]
        
        for table in expected_tables:
            assert table in table_names
    
    def test_store_energy_reading(self):
        """Test storing energy readings."""
        create_tables(self.db_path)
        
        timestamp = datetime.now().isoformat()
        success = store_energy_reading(
            self.db_path, timestamp, 1500.0, 800.0, 0.0, 700.0
        )
        
        assert success
        
        # Verify data was stored
        results = self.db_manager.execute_query(
            "SELECT production, consumption FROM energy WHERE timestamp = ?",
            (timestamp,)
        )
        assert len(results) == 1
        assert results[0][0] == 1500.0
        assert results[0][1] == 800.0
    
    def test_get_energy_data(self):
        """Test retrieving energy data."""
        create_tables(self.db_path)
        
        # Store test data
        date_str = "2024-01-15"
        timestamp1 = f"{date_str} 12:00:00"
        timestamp2 = f"{date_str} 13:00:00"
        
        store_energy_reading(self.db_path, timestamp1, 1500.0, 800.0)
        store_energy_reading(self.db_path, timestamp2, 1800.0, 900.0)
        
        # Retrieve data
        data = get_energy_data(self.db_path, date_str)
        
        assert len(data) == 2
        assert data[0]['production'] == 1500.0
        assert data[1]['production'] == 1800.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 