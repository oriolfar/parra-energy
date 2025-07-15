#!/usr/bin/env python3
"""
Parra Energy - Quiet Startup Script
===================================

This script starts the Parra Energy system with minimal console output,
perfect for production use or when you don't want verbose logging.

Usage:
    python start_quiet.py

The system will start silently and only show important messages like:
- Startup completion
- Error messages
- System status changes

For full verbose output, use: python run.py
"""

import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Force quiet mode by setting environment variable
os.environ['PARRA_LOGGING_QUIET_MODE'] = 'true'
os.environ['PARRA_LOGGING_CONSOLE_LEVEL'] = 'WARNING'

# Redirect stdout to suppress initialization messages
import io
from contextlib import redirect_stdout

# Capture all the verbose initialization output
print("🚀 Starting Parra Energy System (Quiet Mode)")
print("🔧 Initializing components...")

with redirect_stdout(io.StringIO()):
    from web.app import app
    from utils.logger import setup_logger
    from config.settings import Config

if __name__ == '__main__':
    # Load configuration
    config = Config()
    
    # Setup logging with quiet settings
    logger = setup_logger(
        name="parra_energy_quiet",
        console_level="WARNING",  # Only warnings and errors
        file_level="INFO"
    )
    
    print("✅ Components initialized successfully")
    print(f"🌐 Dashboard: http://localhost:{config.web.port}")
    print("⏹️  Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        # Start Flask app in quiet mode
        app.run(
            host=config.web.host,
            port=config.web.port,
            debug=False,  # Disable Flask debug output
            use_reloader=False,  # Disable reloader to reduce output
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Parra Energy System stopped")
    except Exception as e:
        print(f"❌ Error starting system: {e}")
        sys.exit(1) 