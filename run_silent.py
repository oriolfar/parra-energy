#!/usr/bin/env python3
"""
Parra Energy - Silent Startup Script
====================================

This script starts the Parra Energy system with NO console output
during initialization, perfect for production use.

Only shows:
- Final "ready" message
- Dashboard URL
- Errors (if any)
"""

import sys
import os
import io
from contextlib import redirect_stdout, redirect_stderr

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Force quiet mode
os.environ['PARRA_LOGGING_QUIET_MODE'] = 'true'
os.environ['PARRA_LOGGING_CONSOLE_LEVEL'] = 'ERROR'

def main():
    print("🚀 Parra Energy System")
    print("🔧 Loading...")
    
    try:
        # Completely suppress all initialization output
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            from web.app import app
            from config.settings import Config
            
        # Load configuration
        config = Config()
        
        # Show final ready message
        print(f"✅ Ready! Dashboard: http://localhost:{config.web.port}")
        print("⏹️  Press Ctrl+C to stop")
        
        # Start Flask app silently
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)  # Suppress Flask startup messages
        
        app.run(
            host=config.web.host,
            port=config.web.port,
            debug=False,
            use_reloader=False,
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 