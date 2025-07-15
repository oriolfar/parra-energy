"""
Command Line Interface for Parra Energy System
==============================================

Provides command-line tools for managing and interacting with
the Parra Energy solar monitoring and automation system.

Available Commands:
    - start: Start the web server and monitoring system
    - status: Check system status and connectivity
    - setup: Initialize database and configuration
    - data: Data management and export tools
    - config: Configuration management
    - test: System testing and validation tools
"""

from .main import main, cli

__all__ = [
    'main',
    'cli',
] 