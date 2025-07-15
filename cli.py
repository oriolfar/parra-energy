#!/usr/bin/env python3
"""
Parra Energy CLI Entry Point
===========================

Command-line interface entry point for the Parra Energy solar monitoring
and automation system. This script provides access to all system functions
through a unified command-line interface.

Usage:
    python cli.py [COMMAND] [OPTIONS]
    
Available Commands:
    start       Start the web server and monitoring system
    status      Check system status and connectivity
    setup       Initialize database and configuration
    data        Data management and export tools
    config      Configuration management
    test        System testing and validation
    automation  Device automation management

Examples:
    python cli.py start                    # Start web server
    python cli.py status                   # Check system status
    python cli.py setup --init-db          # Initialize database
    python cli.py data export 2024-01-15   # Export data
    python cli.py config show              # Show configuration
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run the CLI
from cli.main import main

if __name__ == '__main__':
    main() 