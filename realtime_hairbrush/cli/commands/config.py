"""
Config command for the Realtime Hairbrush SDK CLI.

This module provides commands for managing configuration.
"""

import os
import json
import click


@click.group(name='config')
def config_cmd():
    """
    Manage configuration.
    """
    pass


@config_cmd.command()
@click.pass_context
def show(ctx):
    """
    Show current configuration.
    """
    config_manager = ctx.obj.get('config_manager')
    if not config_manager:
        click.echo("Error: Configuration manager not initialized")
        return
    
    # Get the configuration as a dictionary
    config = config_manager.config
    
    # Pretty-print the configuration
    click.echo(json.dumps(config, indent=2))


@config_cmd.command()
@click.option('--name', '-n', required=True, help='Configuration parameter name')
@click.option('--value', '-v', required=True, help='Configuration parameter value')
@click.pass_context
def set(ctx, name, value):
    """
    Set a configuration parameter.
    """
    config_manager = ctx.obj.get('config_manager')
    if not config_manager:
        click.echo("Error: Configuration manager not initialized")
        return
    
    # Try to parse the value as JSON
    try:
        value = json.loads(value)
    except json.JSONDecodeError:
        # If it's not valid JSON, use the string value as is
        pass
    
    # Set the value
    config_manager.set_value(name, value)
    click.echo(f"Set {name} to {value}")


@config_cmd.command()
@click.option('--file', '-f', help='Configuration file')
@click.pass_context
def save(ctx, file):
    """
    Save current configuration to file.
    """
    config_manager = ctx.obj.get('config_manager')
    if not config_manager:
        click.echo("Error: Configuration manager not initialized")
        return
    
    # Use the specified file or the current config file
    file_path = file or config_manager.config_file
    if not file_path:
        click.echo("Error: No configuration file specified")
        return
    
    # Save the configuration
    try:
        config_manager.save_config(file_path)
        click.echo(f"Configuration saved to {file_path}")
    except Exception as e:
        click.echo(f"Error saving configuration: {e}")


@config_cmd.command()
@click.option('--file', '-f', required=True, help='Configuration file')
@click.pass_context
def load(ctx, file):
    """
    Load configuration from file.
    """
    if not os.path.exists(file):
        click.echo(f"Error: Configuration file not found: {file}")
        return
    
    # Create a new configuration manager with the specified file
    from realtime_hairbrush.config.manager import ConfigManager
    config_manager = ConfigManager(config_file=file)
    
    # Update the context
    ctx.obj['config_manager'] = config_manager
    ctx.obj['config_file'] = file
    
    click.echo(f"Configuration loaded from {file}")


@config_cmd.command()
@click.option('--section', '-s', help='Configuration section to show')
@click.pass_context
def get(ctx, section):
    """
    Get a specific configuration section.
    """
    config_manager = ctx.obj.get('config_manager')
    if not config_manager:
        click.echo("Error: Configuration manager not initialized")
        return
    
    if section:
        # Get the specified section
        value = config_manager.get_value(section)
        if value is None:
            click.echo(f"Section not found: {section}")
            return
            
        # Pretty-print the section
        if isinstance(value, dict):
            click.echo(json.dumps(value, indent=2))
        else:
            click.echo(value)
    else:
        # Show all sections
        click.echo("Available sections:")
        for key in config_manager.config.keys():
            click.echo(f"  {key}")


@config_cmd.command()
@click.pass_context
def tool_offsets(ctx):
    """
    Show tool offsets.
    """
    config_manager = ctx.obj.get('config_manager')
    if not config_manager:
        click.echo("Error: Configuration manager not initialized")
        return
    
    # Get the tool offsets
    offsets = config_manager.get_value("machine.tool_offsets")
    if not offsets:
        click.echo("Tool offsets not configured")
        return
    
    # Display the offsets
    for i, offset in enumerate(offsets):
        click.echo(f"Tool {i}: X={offset.get('X', 0)} Y={offset.get('Y', 0)} Z={offset.get('Z', 0)}")


@config_cmd.command()
@click.pass_context
def motion_limits(ctx):
    """
    Show motion limits.
    """
    config_manager = ctx.obj.get('config_manager')
    if not config_manager:
        click.echo("Error: Configuration manager not initialized")
        return
    
    # Get the motion limits
    limits = config_manager.get_motion_limits()
    if not limits:
        click.echo("Motion limits not configured")
        return
    
    # Display the limits
    for axis, (min_val, max_val) in limits.items():
        click.echo(f"Axis {axis}: Min={min_val} Max={max_val}")


@config_cmd.command()
@click.pass_context
def connection(ctx):
    """
    Show connection configuration.
    """
    config_manager = ctx.obj.get('config_manager')
    if not config_manager:
        click.echo("Error: Configuration manager not initialized")
        return
    
    # Get the connection configuration
    connection_config = config_manager.get_connection_config()
    
    # Display the connection configuration
    click.echo(f"Transport type: {connection_config.transport_type}")
    if connection_config.transport_type == "serial":
        click.echo(f"Serial port: {connection_config.serial_port}")
        click.echo(f"Baud rate: {connection_config.serial_baudrate}")
    else:
        click.echo(f"Host: {connection_config.http_host}")
    click.echo(f"Timeout: {connection_config.timeout} seconds") 