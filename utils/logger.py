"""
Centralized Logging System for Parra Energy
===========================================

Provides unified logging configuration and utilities for the entire
Parra Energy system. Supports configurable log levels, file outputs,
colored console output, and module-specific loggers.

Features:
    - Configurable logging levels per module
    - Colored console output for better readability
    - File rotation and size management
    - Structured logging with timestamps and module names
    - Performance logging for optimization
    - Error tracking and analysis

This module ensures consistent logging across all system components
while providing flexibility for different environments and use cases.
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional, Dict

# ANSI color codes for console output
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Regular colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to console output."""
    
    def __init__(self, include_module: bool = True, colored: bool = True):
        """
        Initialize colored formatter.
        
        Args:
            include_module: Include module name in log messages
            colored: Enable colored output
        """
        self.include_module = include_module
        self.colored = colored
        
        # Base format with optional module name
        if include_module:
            base_format = '[%(asctime)s] %(levelname)s [%(name)s] %(message)s'
        else:
            base_format = '[%(asctime)s] %(levelname)s %(message)s'
        
        # Define colors for each log level
        self.COLORS = {
            'DEBUG': Colors.CYAN,
            'INFO': Colors.GREEN,
            'WARNING': Colors.YELLOW,
            'ERROR': Colors.RED,
            'CRITICAL': Colors.BRIGHT_RED + Colors.BOLD,
        }
        
        super().__init__(base_format, datefmt='%Y-%m-%d %H:%M:%S')
    
    def format(self, record):
        """Format the log record with colors if enabled."""
        if not self.colored or not hasattr(sys.stderr, 'isatty') or not sys.stderr.isatty():
            # No colors for non-terminal output or if disabled
            return super().format(record)
        
        # Apply colors to the level name
        level_color = self.COLORS.get(record.levelname, '')
        if level_color:
            record.levelname = f"{level_color}{record.levelname}{Colors.RESET}"
        
        # Format the message
        formatted = super().format(record)
        
        return formatted


def setup_logger(
    name: str = "parra_energy",
    console_level: str = "INFO",
    file_level: str = "DEBUG",
    log_file: Optional[str] = None,
    include_module_names: bool = True,
    colored_console: bool = True,
    max_file_size_mb: int = 10,
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up centralized logging for Parra Energy system.
    
    Args:
        name: Logger name (typically module name)
        console_level: Console logging level
        file_level: File logging level  
        log_file: Log file path (if None, uses default)
        include_module_names: Include module names in log output
        colored_console: Enable colored console output
        max_file_size_mb: Maximum log file size before rotation
        backup_count: Number of backup log files to keep
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Prevent duplicate handlers if logger already configured
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.DEBUG)  # Set to lowest level, handlers will filter
    
    # =================================================================
    # CONSOLE HANDLER SETUP
    # =================================================================
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, console_level.upper()))
    
    console_formatter = ColoredFormatter(
        include_module=include_module_names,
        colored=colored_console
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # =================================================================
    # FILE HANDLER SETUP
    # =================================================================
    
    if log_file is None:
        log_file = "logs/parra_energy.log"
    
    # Ensure log directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Use rotating file handler to manage log file size
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_file_size_mb * 1024 * 1024,  # Convert MB to bytes
        backupCount=backup_count
    )
    file_handler.setLevel(getattr(logging, file_level.upper()))
    
    # File formatter (no colors, but include all details)
    file_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Module name for the logger
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"parra_energy.{name}")


class PerformanceLogger:
    """
    Context manager for performance logging.
    
    Measures execution time of code blocks and logs performance metrics.
    """
    
    def __init__(self, logger: logging.Logger, operation_name: str, level: str = "DEBUG"):
        """
        Initialize performance logger.
        
        Args:
            logger: Logger instance to use
            operation_name: Name of the operation being measured
            level: Log level for performance messages
        """
        self.logger = logger
        self.operation_name = operation_name
        self.level = getattr(logging, level.upper())
        self.start_time = None
    
    def __enter__(self):
        """Start timing the operation."""
        self.start_time = datetime.now()
        self.logger.log(self.level, f"🚀 Starting {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and log the duration."""
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            
            if exc_type is None:
                # Operation completed successfully
                self.logger.log(self.level, f"✅ {self.operation_name} completed in {duration:.3f}s")
            else:
                # Operation failed
                self.logger.log(logging.ERROR, f"❌ {self.operation_name} failed after {duration:.3f}s: {exc_val}")


def log_system_info(logger: logging.Logger):
    """
    Log system information and configuration at startup.
    
    Args:
        logger: Logger instance to use
    """
    import platform
    import psutil
    
    logger.info("=" * 60)
    logger.info("🔧 PARRA ENERGY SYSTEM STARTUP")
    logger.info("=" * 60)
    
    # System information
    logger.info(f"🖥️  Platform: {platform.system()} {platform.release()}")
    logger.info(f"🐍 Python: {platform.python_version()}")
    logger.info(f"💾 Memory: {psutil.virtual_memory().total // (1024**3):.1f} GB")
    logger.info(f"💽 CPU: {psutil.cpu_count()} cores")
    
    # Parra Energy configuration
    logger.info(f"⚡ Solar Capacity: 2.2kW")
    logger.info(f"📍 Location: Agramunt, Spain")
    logger.info(f"🌐 Web Port: 5001")
    logger.info(f"📊 Database: SQLite")
    
    logger.info("=" * 60)


# Module-specific loggers for convenience
api_logger = get_logger("api")
web_logger = get_logger("web")
analytics_logger = get_logger("analytics")
automation_logger = get_logger("automation")
weather_logger = get_logger("weather")
database_logger = get_logger("database")
utils_logger = get_logger("utils")

# Create main system logger
system_logger = setup_logger()

# Export commonly used loggers
__all__ = [
    'setup_logger',
    'get_logger',
    'PerformanceLogger',
    'log_system_info',
    'ColoredFormatter',
    'system_logger',
    'api_logger',
    'web_logger',
    'analytics_logger',
    'automation_logger',
    'weather_logger',
    'database_logger',
    'utils_logger',
] 