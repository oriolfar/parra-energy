"""
Main Entry Point for Parra Energy Solar Monitoring System
========================================================

This is the primary startup script for the Parra Energy home solar monitoring
and automation system. It initializes a Flask web server that provides:

- Real-time solar production monitoring
- Household consumption tracking  
- Energy optimization recommendations
- Dual interface modes (technical/elderly)
- Weather-based solar forecasting
- Device automation based on solar surplus

System Configuration:
- Solar system capacity: 2.2kW (2200W peak)
- Target inverter: Fronius at 192.168.1.128
- Web interface: http://localhost:5001
- Auto-browser opening: 3 seconds after startup
- Fallback: Enhanced mock with real weather data

Usage:
    python run.py

The system will automatically:
1. Try to connect to real Fronius inverter
2. Fall back to realistic mock data if unavailable  
3. Start web server on port 5001
4. Open browser automatically
5. Begin 5-second data polling cycle
"""

#!/usr/bin/env python3

# =============================================================================
# IMPORTS AND PATH SETUP
# =============================================================================

import sys
import os
import webbrowser
from threading import Timer

# Add current directory to Python path so we can import our modules
# This ensures all modules can be found regardless of where
# the script is run from
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the main Flask application and configuration
from web.app import app
from config import Config
from utils.logger import setup_logger, log_system_info

# =============================================================================
# SYSTEM STARTUP CONFIGURATION
# =============================================================================

# =============================================================================
# CONFIGURATION AND LOGGING SETUP
# =============================================================================

# Initialize configuration for development environment
config = Config(environment="development")

# Set up logging system
logger = setup_logger(
    console_level=config.logging.console_level,
    colored_console=config.logging.colored_console_output
)

# Log system startup information
log_system_info(logger)

# =============================================================================
# AUTO-BROWSER OPENING
# =============================================================================

def open_browser():
    """
    Automatically open the default web browser to the application URL.
    
    This provides a better user experience by eliminating the need to
    manually navigate to the application after startup.
    """
    if config.web.auto_open_browser:
        logger.info("🌐 Opening web browser...")
        webbrowser.open(f'http://{config.web.host}:{config.web.port}')

# Set up a timer to open the browser with configurable delay
if config.web.auto_open_browser:
    timer = Timer(config.web.browser_delay_seconds, open_browser)
    timer.start()

# =============================================================================
# FLASK SERVER STARTUP
# =============================================================================

if __name__ == '__main__':
    """
    Main execution block - starts the Flask development server.
    
    Server Configuration:
    - Uses configuration system for host, port, and debug settings
    - Configurable browser auto-opening and logging
    - Smart error handling and graceful shutdown
    
    The Flask app automatically:
    1. Initializes the smart Fronius client (real or mock)
    2. Starts background data collection thread
    3. Sets up all API endpoints and routes
    4. Begins serving the web dashboard
    """
    logger.info(f"🚀 Flask server starting on {config.web.host}:{config.web.port}")
    logger.info("📡 Background data collection will begin automatically")
    logger.info("🔄 Auto-detection: Real inverter → Mock fallback")
    logger.info("⏹️  Press Ctrl+C to stop the server")
    
    try:
        # Start the Flask development server with configuration
        app.run(
            debug=config.web.debug,
            host=config.web.host,
            port=config.web.port,
            threaded=True
        )
    except KeyboardInterrupt:
        logger.info("\n🛑 Server stopped by user")
        logger.info("📊 Session complete - data saved to database")
    except Exception as e:
        logger.error(f"\n❌ Server error: {e}")
        logger.info("🔧 Check logs for detailed error information") 