"""
Main CLI Interface for Parra Energy System
==========================================

Command-line interface for managing the Parra Energy solar monitoring
and automation system. Provides convenient access to all system functions
through subcommands.
"""

import click
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Define version here since we don't have a package __init__.py anymore
__version__ = "1.0.0"

from config import Config
from utils.logger import setup_logger, log_system_info


@click.group()
@click.version_option(version=__version__, prog_name="Parra Energy")
@click.option('--config-file', '-c', type=click.Path(), help='Configuration file path')
@click.option('--environment', '-e', default='development', 
              type=click.Choice(['development', 'production', 'testing']),
              help='Environment configuration')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--quiet', '-q', is_flag=True, help='Suppress non-essential output')
@click.pass_context
def cli(ctx, config_file, environment, verbose, quiet):
    """
    Parra Energy - Intelligent Solar Energy Monitoring and Automation System
    
    A comprehensive home energy management system for 2.2kW solar installations.
    Provides real-time monitoring, intelligent device automation, and dual-mode
    dashboards for technical and elderly users.
    
    Examples:
        parra start                    # Start web server and monitoring
        parra status                   # Check system status
        parra setup --init-db          # Initialize database
        parra data export 2024-01-15   # Export data for date
        parra config show              # Show current configuration
    """
    # Initialize context object for sharing between commands
    ctx.ensure_object(dict)
    
    # Set up configuration
    ctx.obj['config'] = Config(environment=environment)
    ctx.obj['verbose'] = verbose
    ctx.obj['quiet'] = quiet
    
    # Set up logging based on verbosity
    if verbose:
        log_level = 'DEBUG'
    elif quiet:
        log_level = 'WARNING'
    else:
        log_level = 'INFO'
    
    logger = setup_logger(console_level=log_level)
    ctx.obj['logger'] = logger
    
    # Load custom config file if provided
    if config_file:
        # TODO: Implement config file loading
        click.echo(f"Custom config file: {config_file}")


@cli.command()
@click.option('--host', '-h', default=None, help='Web server host (default: localhost)')
@click.option('--port', '-p', type=int, default=None, help='Web server port (default: 5001)')
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.option('--no-browser', is_flag=True, help='Do not open browser automatically')
@click.pass_context
def start(ctx, host, port, debug, no_browser):
    """Start the Parra Energy web server and monitoring system."""
    from .commands import start_command
    
    config = ctx.obj['config']
    logger = ctx.obj['logger']
    
    # Override config with command line options
    if host:
        config.web.host = host
    if port:
        config.web.port = port
    if debug:
        config.web.debug = True
    if no_browser:
        config.web.auto_open_browser = False
    
    # Log system information
    if not ctx.obj['quiet']:
        log_system_info(logger)
    
    start_command(config, logger)


@cli.command()
@click.option('--check-inverter', is_flag=True, help='Check Fronius inverter connectivity')
@click.option('--check-database', is_flag=True, help='Check database connectivity')
@click.option('--check-weather', is_flag=True, help='Check weather service connectivity')
@click.option('--format', 'output_format', default='text', 
              type=click.Choice(['text', 'json']), help='Output format')
@click.pass_context
def status(ctx, check_inverter, check_database, check_weather, output_format):
    """Check system status and connectivity."""
    from .commands import status_command
    
    config = ctx.obj['config']
    logger = ctx.obj['logger']
    
    checks = {
        'inverter': check_inverter,
        'database': check_database,
        'weather': check_weather
    }
    
    # If no specific checks requested, run all
    if not any(checks.values()):
        checks = {k: True for k in checks}
    
    status_command(config, logger, checks, output_format)


@cli.command()
@click.option('--init-db', is_flag=True, help='Initialize database tables')
@click.option('--create-config', is_flag=True, help='Create default configuration file')
@click.option('--test-data', is_flag=True, help='Insert test data for development')
@click.option('--force', is_flag=True, help='Overwrite existing configuration')
@click.pass_context
def setup(ctx, init_db, create_config, test_data, force):
    """Initialize system setup and configuration."""
    from .commands import setup_command
    
    config = ctx.obj['config']
    logger = ctx.obj['logger']
    
    setup_options = {
        'init_db': init_db,
        'create_config': create_config,
        'test_data': test_data,
        'force': force
    }
    
    setup_command(config, logger, setup_options)


@cli.group()
@click.pass_context
def data(ctx):
    """Data management and export tools."""
    pass


@data.command('export')
@click.argument('date', required=True)
@click.option('--format', 'output_format', default='csv',
              type=click.Choice(['csv', 'json', 'xlsx']), help='Export format')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--include-weather', is_flag=True, help='Include weather data')
@click.pass_context
def export_data(ctx, date, output_format, output, include_weather):
    """Export energy data for a specific date."""
    from .commands import export_data_command
    
    config = ctx.obj['config']
    logger = ctx.obj['logger']
    
    export_options = {
        'date': date,
        'format': output_format,
        'output_file': output,
        'include_weather': include_weather
    }
    
    export_data_command(config, logger, export_options)


@data.command('cleanup')
@click.option('--days', type=int, default=365, help='Keep data for this many days')
@click.option('--vacuum', is_flag=True, help='Vacuum database after cleanup')
@click.option('--dry-run', is_flag=True, help='Show what would be deleted without deleting')
@click.pass_context
def cleanup_data(ctx, days, vacuum, dry_run):
    """Clean up old data beyond retention period."""
    from .commands import cleanup_data_command
    
    config = ctx.obj['config']
    logger = ctx.obj['logger']
    
    cleanup_options = {
        'days': days,
        'vacuum': vacuum,
        'dry_run': dry_run
    }
    
    cleanup_data_command(config, logger, cleanup_options)


@cli.group()
@click.pass_context
def config_group(ctx):
    """Configuration management."""
    pass


@config_group.command('show')
@click.option('--section', type=click.Choice(['system', 'web', 'database', 'weather', 'logging']),
              help='Show specific configuration section')
@click.pass_context
def show_config(ctx, section):
    """Show current configuration."""
    from .commands import show_config_command
    
    config = ctx.obj['config']
    logger = ctx.obj['logger']
    
    show_config_command(config, logger, section)


@config_group.command('validate')
@click.pass_context
def validate_config(ctx):
    """Validate current configuration."""
    from .commands import validate_config_command
    
    config = ctx.obj['config']
    logger = ctx.obj['logger']
    
    validate_config_command(config, logger)


@cli.command()
@click.option('--test-type', default='all',
              type=click.Choice(['unit', 'integration', 'system', 'all']),
              help='Type of tests to run')
@click.option('--verbose', is_flag=True, help='Verbose test output')
@click.pass_context
def test(ctx, test_type, verbose):
    """Run system tests and validation."""
    from .commands import test_command
    
    config = ctx.obj['config']
    logger = ctx.obj['logger']
    
    test_options = {
        'test_type': test_type,
        'verbose': verbose
    }
    
    test_command(config, logger, test_options)


@cli.command()
@click.option('--list-devices', is_flag=True, help='List all configured devices')
@click.option('--add-device', help='Add new device (format: name,power,type,priority)')
@click.option('--remove-device', help='Remove device by name')
@click.option('--enable-automation', is_flag=True, help='Enable automation system')
@click.option('--disable-automation', is_flag=True, help='Disable automation system')
@click.pass_context
def automation(ctx, list_devices, add_device, remove_device, enable_automation, disable_automation):
    """Manage device automation system."""
    from .commands import automation_command
    
    config = ctx.obj['config']
    logger = ctx.obj['logger']
    
    automation_options = {
        'list_devices': list_devices,
        'add_device': add_device,
        'remove_device': remove_device,
        'enable_automation': enable_automation,
        'disable_automation': disable_automation
    }
    
    automation_command(config, logger, automation_options)


def main():
    """Main entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n⚠️  Operation cancelled by user", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main() 