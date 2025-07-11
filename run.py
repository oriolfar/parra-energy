"""
Main entry point for the Parra Energy application.
Run this file to start the web dashboard.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parra_energy.web.app import app

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000) 