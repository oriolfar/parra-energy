"""
Database Management Utilities for Parra Energy System
=====================================================

Centralized database operations and utilities for the Parra Energy system.
Provides common database patterns, connection management, table creation,
and data access methods used across multiple modules.

Key Features:
    - Connection management with context managers
    - Common table creation and initialization
    - Standardized CRUD operations
    - Error handling and logging
    - Database schema migrations
    - Performance optimization utilities
    - Backup and maintenance operations

This module eliminates code duplication and provides a consistent
database interface across all system components.
"""

import sqlite3
import os
import logging
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Centralized database management for the Parra Energy system.
    
    This class provides a unified interface for all database operations,
    connection management, and common data access patterns used throughout
    the system.
    """
    
    def __init__(self, db_path: str = "data/energy_data.db"):
        """
        Initialize database manager with connection parameters.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.ensure_directory_exists()
        logger.info(f"Database manager initialized: {db_path}")
    
    def ensure_directory_exists(self):
        """Ensure the database directory exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            logger.info(f"Created database directory: {db_dir}")
    
    @contextmanager
    def get_connection(self, row_factory: bool = False):
        """
        Context manager for database connections.
        
        Args:
            row_factory: If True, enable row factory for dict-like access
            
        Yields:
            sqlite3.Connection: Database connection
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            
            if row_factory:
                conn.row_factory = sqlite3.Row
            
            # Enable WAL mode for better performance
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            
            yield conn
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: tuple = (), row_factory: bool = False) -> List[Any]:
        """
        Execute a SELECT query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            row_factory: If True, return dict-like rows
            
        Returns:
            List of query results
        """
        with self.get_connection(row_factory=row_factory) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Execute an INSERT/UPDATE/DELETE query.
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            
        Returns:
            Number of affected rows
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """
        Execute multiple queries with different parameters.
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
            
        Returns:
            Number of affected rows
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount


def create_tables(db_path: str = "data/energy_data.db"):
    """
    Create all required database tables for the Parra Energy system.
    
    This function initializes the complete database schema including:
    - Energy production and consumption data
    - Weather forecast and historical data
    - Analytics and optimization insights
    - Device automation logs
    - System configuration and metadata
    
    Args:
        db_path: Path to SQLite database file
    """
    db_manager = DatabaseManager(db_path)
    
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        
        logger.info("Creating Parra Energy database tables...")
        
        # =================================================================
        # CORE ENERGY DATA TABLES
        # =================================================================
        
        # Main energy production and consumption data (5-minute intervals)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS energy (
                timestamp TEXT PRIMARY KEY,                -- ISO datetime
                production REAL NOT NULL,                  -- Solar production (W)
                consumption REAL NOT NULL,                 -- House consumption (W)
                grid_import REAL DEFAULT 0,                -- Grid power import (W)
                grid_export REAL DEFAULT 0,                -- Grid power export (W)
                self_consumption_rate REAL,                -- Self consumption percentage
                autonomy_rate REAL,                        -- Energy autonomy percentage
                created_at TEXT DEFAULT CURRENT_TIMESTAMP  -- Record creation time
            )
        ''')
        
        # Daily energy summaries for faster analytics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_energy (
                date TEXT PRIMARY KEY,                     -- Date in YYYY-MM-DD format
                total_production REAL NOT NULL,            -- Total solar production (kWh)
                total_consumption REAL NOT NULL,           -- Total house consumption (kWh)
                total_grid_import REAL DEFAULT 0,          -- Total grid import (kWh)
                total_grid_export REAL DEFAULT 0,          -- Total grid export (kWh)
                avg_self_consumption_rate REAL,            -- Average self consumption
                avg_autonomy_rate REAL,                    -- Average autonomy
                peak_production REAL,                      -- Peak production moment (W)
                peak_consumption REAL,                     -- Peak consumption moment (W)
                weather_quality_score REAL,               -- Weather quality for the day
                efficiency_score REAL,                     -- Energy efficiency score
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # =================================================================
        # WEATHER DATA TABLES
        # =================================================================
        
        # Weather forecast data from Open-Meteo API
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_forecast (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,                   -- ISO datetime for forecast hour
                temperature_2m REAL,                      -- Temperature at 2m height (°C)
                cloud_cover REAL,                         -- Cloud cover percentage (0-100%)
                direct_radiation REAL,                    -- Direct solar radiation (W/m²)
                diffuse_radiation REAL,                   -- Diffuse solar radiation (W/m²)
                global_tilted_irradiance REAL,            -- Global tilted irradiance (W/m²)
                shortwave_radiation REAL,                 -- Shortwave radiation (W/m²)
                wind_speed_10m REAL,                      -- Wind speed at 10m height (m/s)
                precipitation REAL,                       -- Precipitation amount (mm)
                uv_index REAL,                            -- UV index (0-11+)
                forecast_date TEXT NOT NULL,              -- Date when forecast was made
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(timestamp, forecast_date)          -- Prevent duplicate forecasts
            )
        ''')
        
        # Daily weather summaries
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_daily (
                date TEXT PRIMARY KEY,                    -- Date in YYYY-MM-DD format
                sunrise TEXT,                             -- Sunrise time (HH:MM)
                sunset TEXT,                              -- Sunset time (HH:MM)  
                daylight_duration REAL,                   -- Hours of daylight
                uv_index_max REAL,                        -- Maximum UV index
                temperature_max REAL,                     -- Maximum temperature (°C)
                temperature_min REAL,                     -- Minimum temperature (°C)
                avg_cloud_cover REAL,                     -- Average cloud cover (%)
                total_precipitation REAL,                 -- Total precipitation (mm)
                solar_production_forecast REAL,           -- Forecasted solar production (kWh)
                weather_quality_score REAL,               -- Weather quality score (0-100)
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Weather impact analysis on actual solar production
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_impact (
                date TEXT PRIMARY KEY,                    -- Date of analysis
                forecasted_production REAL,               -- Weather-based forecast (kWh)
                actual_production REAL,                   -- Actual measured production (kWh)
                forecast_accuracy REAL,                   -- Accuracy percentage (0-100%)
                weather_factor REAL,                      -- Weather impact factor (0-1)
                seasonal_adjustment REAL,                 -- Seasonal correction factor
                learning_weight REAL,                     -- Machine learning weight
                notes TEXT,                               -- Analysis notes
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # =================================================================
        # ANALYTICS AND OPTIMIZATION TABLES
        # =================================================================
        
        # Daily analytics aggregation
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_analytics (
                date TEXT PRIMARY KEY,                    -- Date in YYYY-MM-DD format
                total_production REAL,                    -- Total solar production (kWh)
                total_consumption REAL,                   -- Total house consumption (kWh)
                self_consumption_rate REAL,               -- Percentage of solar used directly
                grid_import REAL,                         -- Energy imported from grid (kWh)
                grid_export REAL,                         -- Energy exported to grid (kWh)
                efficiency_score REAL,                    -- Daily efficiency rating (0-100)
                weather_quality REAL,                     -- Weather quality score for the day
                optimization_potential REAL,              -- Estimated improvement potential
                cost_savings REAL,                        -- Estimated cost savings (€)
                carbon_footprint_reduction REAL,          -- CO2 reduction (kg)
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Optimization insights and recommendations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimization_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,                       -- Date insight was generated
                insight_type TEXT NOT NULL,               -- 'tip', 'warning', 'opportunity'
                category TEXT NOT NULL,                   -- 'timing', 'efficiency', 'waste_reduction'
                priority TEXT NOT NULL,                   -- 'high', 'medium', 'low'
                title TEXT NOT NULL,                      -- Short insight title
                description TEXT NOT NULL,                -- Detailed insight description
                potential_savings REAL,                   -- Estimated daily savings (kWh)
                target_audience TEXT DEFAULT 'general',   -- 'general', 'elderly', 'technical'
                language TEXT DEFAULT 'en',               -- 'en', 'es', 'ca'
                is_active BOOLEAN DEFAULT 1,              -- Whether insight is still relevant
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Usage pattern analysis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,               -- 'daily', 'weekly', 'seasonal'
                time_range TEXT NOT NULL,                 -- Time range identifier
                avg_consumption REAL,                     -- Average consumption (W)
                peak_consumption REAL,                    -- Peak consumption (W)
                consumption_variance REAL,                -- Consumption variance
                solar_availability REAL,                  -- Average solar availability
                automation_opportunities TEXT,            -- JSON list of automation opportunities
                confidence_score REAL,                    -- Pattern confidence (0-1)
                sample_size INTEGER,                      -- Number of data points analyzed
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # =================================================================
        # DEVICE AUTOMATION TABLES
        # =================================================================
        
        # Device management and status
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,                -- Device name
                device_type TEXT NOT NULL,                -- Device category
                power_consumption REAL NOT NULL,          -- Power consumption (W)
                priority INTEGER DEFAULT 5,               -- Automation priority (1-10)
                is_automated BOOLEAN DEFAULT 1,           -- Whether device is automated
                is_essential BOOLEAN DEFAULT 0,           -- Whether device is essential
                location TEXT,                            -- Device location
                description TEXT,                         -- Device description
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Device automation events log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS automation_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,                  -- Event timestamp
                device_name TEXT NOT NULL,                -- Device affected
                action TEXT NOT NULL,                     -- 'turn_on', 'turn_off', 'schedule'
                trigger_reason TEXT,                      -- Reason for action
                solar_surplus REAL,                       -- Available solar surplus (W)
                energy_saved REAL,                        -- Estimated energy saved (kWh)
                automation_rule TEXT,                     -- Which rule triggered action
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # =================================================================
        # SYSTEM CONFIGURATION TABLES
        # =================================================================
        
        # System configuration and metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_config (
                key TEXT PRIMARY KEY,                     -- Configuration key
                value TEXT NOT NULL,                      -- Configuration value
                data_type TEXT DEFAULT 'string',          -- 'string', 'integer', 'float', 'boolean'
                description TEXT,                         -- Configuration description
                category TEXT DEFAULT 'general',          -- Configuration category
                is_user_configurable BOOLEAN DEFAULT 1,   -- Whether user can modify
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # System performance monitoring
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,                  -- Measurement timestamp
                cpu_usage REAL,                          -- CPU usage percentage
                memory_usage REAL,                       -- Memory usage percentage
                disk_usage REAL,                         -- Disk usage percentage
                database_size REAL,                      -- Database size (MB)
                api_response_time REAL,                  -- Average API response time (ms)
                data_collection_errors INTEGER DEFAULT 0, -- Number of collection errors
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # =================================================================
        # CREATE INDEXES FOR PERFORMANCE
        # =================================================================
        
        # Indexes for energy data queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_energy_timestamp ON energy(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_energy_date ON energy(date(timestamp))')
        
        # Indexes for weather data queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_weather_forecast_timestamp ON weather_forecast(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_weather_daily_date ON weather_daily(date)')
        
        # Indexes for analytics queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_analytics_date ON daily_analytics(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_optimization_insights_date ON optimization_insights(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_optimization_insights_active ON optimization_insights(is_active)')
        
        # Indexes for automation queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_automation_events_timestamp ON automation_events(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_automation_events_device ON automation_events(device_name)')
        
        conn.commit()
        logger.info("✅ All Parra Energy database tables created successfully")


def get_energy_data(db_path: str, start_date: str, end_date: str = None) -> List[Dict]:
    """
    Retrieve energy data for a date range.
    
    Args:
        db_path: Database file path
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format (optional)
        
    Returns:
        List of energy data records as dictionaries
    """
    db_manager = DatabaseManager(db_path)
    
    if end_date is None:
        end_date = start_date
    
    start_datetime = f"{start_date} 00:00:00"
    end_datetime = f"{end_date} 23:59:59"
    
    query = """
        SELECT timestamp, production, consumption, grid_import, grid_export,
               self_consumption_rate, autonomy_rate
        FROM energy 
        WHERE timestamp >= ? AND timestamp <= ?
        ORDER BY timestamp
    """
    
    return [dict(row) for row in db_manager.execute_query(query, (start_datetime, end_datetime), row_factory=True)]


def store_energy_reading(db_path: str, timestamp: str, production: float, consumption: float, 
                        grid_import: float = 0, grid_export: float = 0) -> bool:
    """
    Store a single energy reading in the database.
    
    Args:
        db_path: Database file path
        timestamp: ISO timestamp string
        production: Solar production in watts
        consumption: House consumption in watts
        grid_import: Grid import in watts (optional)
        grid_export: Grid export in watts (optional)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        db_manager = DatabaseManager(db_path)
        
        # Calculate derived metrics
        self_consumption_rate = min(100, (consumption / production * 100)) if production > 0 else 0
        autonomy_rate = min(100, (production / consumption * 100)) if consumption > 0 else 100
        
        query = """
            INSERT OR REPLACE INTO energy 
            (timestamp, production, consumption, grid_import, grid_export, 
             self_consumption_rate, autonomy_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        db_manager.execute_update(query, (
            timestamp, production, consumption, grid_import, grid_export,
            self_consumption_rate, autonomy_rate
        ))
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to store energy reading: {e}")
        return False


def store_bulk_energy_data(db_path: str, readings: List[Dict]) -> int:
    """
    Store multiple energy readings efficiently.
    
    Args:
        db_path: Database file path
        readings: List of energy reading dictionaries
        
    Returns:
        Number of records stored successfully
    """
    try:
        db_manager = DatabaseManager(db_path)
        
        # Prepare data for bulk insert
        params_list = []
        for reading in readings:
            production = reading.get('production', 0)
            consumption = reading.get('consumption', 0)
            
            # Calculate derived metrics
            self_consumption_rate = min(100, (consumption / production * 100)) if production > 0 else 0
            autonomy_rate = min(100, (production / consumption * 100)) if consumption > 0 else 100
            
            params_list.append((
                reading['timestamp'],
                production,
                consumption,
                reading.get('grid_import', 0),
                reading.get('grid_export', 0),
                self_consumption_rate,
                autonomy_rate
            ))
        
        query = """
            INSERT OR REPLACE INTO energy 
            (timestamp, production, consumption, grid_import, grid_export, 
             self_consumption_rate, autonomy_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        return db_manager.execute_many(query, params_list)
        
    except Exception as e:
        logger.error(f"Failed to store bulk energy data: {e}")
        return 0


def cleanup_old_data(db_path: str, days_to_keep: int = 365) -> int:
    """
    Clean up old data beyond retention period.
    
    Args:
        db_path: Database file path
        days_to_keep: Number of days to retain
        
    Returns:
        Number of records deleted
    """
    try:
        db_manager = DatabaseManager(db_path)
        
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
        
        # Delete old energy data
        energy_deleted = db_manager.execute_update(
            "DELETE FROM energy WHERE timestamp < ?", (cutoff_date,)
        )
        
        # Delete old weather forecast data  
        weather_deleted = db_manager.execute_update(
            "DELETE FROM weather_forecast WHERE timestamp < ?", (cutoff_date,)
        )
        
        # Delete old automation events
        automation_deleted = db_manager.execute_update(
            "DELETE FROM automation_events WHERE timestamp < ?", (cutoff_date,)
        )
        
        total_deleted = energy_deleted + weather_deleted + automation_deleted
        logger.info(f"Cleaned up {total_deleted} old records (older than {days_to_keep} days)")
        
        return total_deleted
        
    except Exception as e:
        logger.error(f"Failed to cleanup old data: {e}")
        return 0


def vacuum_database(db_path: str) -> bool:
    """
    Optimize database by running VACUUM operation.
    
    Args:
        db_path: Database file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        db_manager = DatabaseManager(db_path)
        
        with db_manager.get_connection() as conn:
            conn.execute("VACUUM")
            conn.execute("ANALYZE")
            
        logger.info("Database vacuum and analyze completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to vacuum database: {e}")
        return False 