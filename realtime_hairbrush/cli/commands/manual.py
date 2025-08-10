"""
Manual control commands for the Realtime Hairbrush SDK CLI.

This module provides commands for manual control of the airbrush plotter.
"""

import click
import time

from semantic_gcode.gcode.base import GCodeInstruction
from realtime_hairbrush.instructions.airbrush_instruction import AirbrushInstruction


@click.group()
def manual():
    """
    Manual control commands.
    """
    pass


@manual.command()
@click.option('--axes', '-a', default='all', help='Axes to home (all, xy, z, u, v)')
@click.pass_context
def home(ctx, axes):
    """
    Home specified axes.
    """
    transport = ctx.obj.get('transport')
    if not transport:
        click.echo("Error: Not connected")
        return
    
    # Map axes string to actual axes
    axes_map = {
        'all': None,
        'xy': ['X', 'Y'],
        'z': ['Z'],
        'u': ['U'],
        'v': ['V']
    }
    
    # Get the axes to home
    axes_to_home = axes_map.get(axes.lower())
    if axes_to_home is None and axes.lower() != 'all':
        click.echo(f"Error: Invalid axes: {axes}")
        return
    
    # Create the homing instruction
    instruction = AirbrushInstruction.create_home(axes_to_home)
    
    # Send the instruction
    click.echo(f"Homing {axes}...")
    result = transport.send_line(str(instruction))
    
    if result:
        click.echo("Homing complete")
    else:
        click.echo(f"Homing failed: {transport.get_last_error()}")


@manual.command()
@click.option('--index', '-i', type=int, required=True, help='Tool index (0=black, 1=white)')
@click.pass_context
def tool(ctx, index):
    """
    Select tool.
    """
    transport = ctx.obj.get('transport')
    if not transport:
        click.echo("Error: Not connected")
        return
    
    # Validate the tool index
    if index not in [0, 1]:
        click.echo(f"Error: Invalid tool index: {index}")
        return
    
    # Create the tool selection instruction
    instruction = AirbrushInstruction.create_tool_select(index)
    
    # Send the instruction
    click.echo(f"Selecting tool {index}...")
    result = transport.send_line(str(instruction))
    
    if result:
        click.echo(f"Tool {index} selected")
    else:
        click.echo(f"Tool selection failed: {transport.get_last_error()}")


@manual.command()
@click.option('--x', type=float, help='X position')
@click.option('--y', type=float, help='Y position')
@click.option('--z', type=float, help='Z position')
@click.option('--feedrate', '-f', type=float, help='Movement speed')
@click.pass_context
def move(ctx, x, y, z, feedrate):
    """
    Move to position.
    """
    transport = ctx.obj.get('transport')
    if not transport:
        click.echo("Error: Not connected")
        return
    
    # Validate that at least one axis is specified
    if x is None and y is None and z is None:
        click.echo("Error: At least one axis must be specified")
        return
    
    # Create the move instruction
    instruction = AirbrushInstruction.create_move(x, y, z, feedrate)
    
    # Send the instruction
    move_str = []
    if x is not None:
        move_str.append(f"X{x}")
    if y is not None:
        move_str.append(f"Y{y}")
    if z is not None:
        move_str.append(f"Z{z}")
    click.echo(f"Moving to {' '.join(move_str)}...")
    
    result = transport.send_line(str(instruction))
    
    if result:
        click.echo("Move complete")
    else:
        click.echo(f"Move failed: {transport.get_last_error()}")


@manual.command()
@click.option('--feedrate', '-f', type=float, default=1000, help='Movement speed')
@click.pass_context
def safe_z(ctx, feedrate):
    """
    Move to safe Z height.
    """
    transport = ctx.obj.get('transport')
    if not transport:
        click.echo("Error: Not connected")
        return
    
    # Get the safe Z height from the configuration
    config_manager = ctx.obj.get('config_manager')
    safe_z_height = 5.0  # Default
    if config_manager:
        safe_z_height = config_manager.get_safe_z_height()
    
    # Create the move instruction
    instruction = AirbrushInstruction.create_move(z=safe_z_height, feedrate=feedrate)
    
    # Send the instruction
    click.echo(f"Moving to safe Z height ({safe_z_height})...")
    result = transport.send_line(str(instruction))
    
    if result:
        click.echo("Move complete")
    else:
        click.echo(f"Move failed: {transport.get_last_error()}")


@manual.command()
@click.option('--feedrate', '-f', type=float, default=500, help='Movement speed')
@click.pass_context
def spray_z(ctx, feedrate):
    """
    Move to spray Z height.
    """
    transport = ctx.obj.get('transport')
    if not transport:
        click.echo("Error: Not connected")
        return
    
    # Get the spray Z height from the configuration
    config_manager = ctx.obj.get('config_manager')
    spray_z_height = 1.5  # Default
    if config_manager:
        spray_z_height = config_manager.get_spray_z_height()
    
    # Create the move instruction
    instruction = AirbrushInstruction.create_move(z=spray_z_height, feedrate=feedrate)
    
    # Send the instruction
    click.echo(f"Moving to spray Z height ({spray_z_height})...")
    result = transport.send_line(str(instruction))
    
    if result:
        click.echo("Move complete")
    else:
        click.echo(f"Move failed: {transport.get_last_error()}")


@manual.command()
@click.option('--tool', '-t', type=int, required=True, help='Tool index (0=black, 1=white)')
@click.option('--state', '-s', type=bool, required=True, help='Air state (True=on, False=off)')
@click.pass_context
def air(ctx, tool, state):
    """
    Control air solenoid.
    """
    transport = ctx.obj.get('transport')
    if not transport:
        click.echo("Error: Not connected")
        return
    
    # Validate the tool index
    if tool not in [0, 1]:
        click.echo(f"Error: Invalid tool index: {tool}")
        return
    
    # Get the fan index from the configuration
    config_manager = ctx.obj.get('config_manager')
    fan_index = 2 if tool == 0 else 3  # Default
    if config_manager:
        fan_index = config_manager.get_fan_index(tool)
    
    # Create the air control instruction
    instruction = AirbrushInstruction.create_air_control(tool, state, fan_index)
    
    # Send the instruction
    state_str = "ON" if state else "OFF"
    click.echo(f"Setting air {state_str} for tool {tool}...")
    result = transport.send_line(str(instruction))
    
    if result:
        click.echo(f"Air {state_str}")
    else:
        click.echo(f"Air control failed: {transport.get_last_error()}")


@manual.command()
@click.option('--tool', '-t', type=int, required=True, help='Tool index (0=black, 1=white)')
@click.option('--width', '-w', type=float, default=1.0, help='Stroke width (0.0-1.0)')
@click.option('--opacity', '-o', type=float, default=1.0, help='Stroke opacity (0.0-1.0)')
@click.pass_context
def paint_start(ctx, tool, width, opacity):
    """
    Start paint flow.
    """
    transport = ctx.obj.get('transport')
    if not transport:
        click.echo("Error: Not connected")
        return
    
    # Validate the tool index
    if tool not in [0, 1]:
        click.echo(f"Error: Invalid tool index: {tool}")
        return
    
    # Validate width and opacity
    if width < 0.0 or width > 1.0:
        click.echo(f"Error: Width must be between 0.0 and 1.0: {width}")
        return
    if opacity < 0.0 or opacity > 1.0:
        click.echo(f"Error: Opacity must be between 0.0 and 1.0: {opacity}")
        return
    
    # Create the paint flow start instructions
    instructions = AirbrushInstruction.create_paint_flow_start(tool, width, opacity)
    
    # Send the instructions
    click.echo(f"Starting paint flow for tool {tool} with width={width}, opacity={opacity}...")
    for instruction in instructions:
        result = transport.send_line(str(instruction))
        if not result:
            click.echo(f"Paint flow start failed: {transport.get_last_error()}")
            return
    
    click.echo("Paint flow started")


@manual.command()
@click.option('--tool', '-t', type=int, required=True, help='Tool index (0=black, 1=white)')
@click.pass_context
def paint_stop(ctx, tool):
    """
    Stop paint flow.
    """
    transport = ctx.obj.get('transport')
    if not transport:
        click.echo("Error: Not connected")
        return
    
    # Validate the tool index
    if tool not in [0, 1]:
        click.echo(f"Error: Invalid tool index: {tool}")
        return
    
    # Create the paint flow stop instruction
    instruction = AirbrushInstruction.create_paint_flow_stop(tool)
    
    # Send the instruction
    click.echo(f"Stopping paint flow for tool {tool}...")
    result = transport.send_line(str(instruction))
    
    if result:
        click.echo("Paint flow stopped")
    else:
        click.echo(f"Paint flow stop failed: {transport.get_last_error()}")


@manual.command()
@click.option('--milliseconds', '-m', type=int, default=50, help='Dwell time in milliseconds')
@click.pass_context
def dwell(ctx, milliseconds):
    """
    Wait for specified time.
    """
    transport = ctx.obj.get('transport')
    if not transport:
        click.echo("Error: Not connected")
        return
    
    # Create the dwell instruction
    instruction = AirbrushInstruction.create_dwell(milliseconds)
    
    # Send the instruction
    click.echo(f"Waiting for {milliseconds}ms...")
    result = transport.send_line(str(instruction))
    
    if result:
        click.echo("Dwell complete")
    else:
        click.echo(f"Dwell failed: {transport.get_last_error()}")


@manual.command()
@click.option('--command', '-c', required=True, help='Raw G-code command')
@click.pass_context
def gcode(ctx, command):
    """
    Send raw G-code command.
    """
    transport = ctx.obj.get('transport')
    if not transport:
        click.echo("Error: Not connected")
        return
    
    # Send the raw command
    click.echo(f"Sending: {command}")
    result = transport.send_line(command)
    
    if result:
        click.echo("Command sent")
    else:
        click.echo(f"Command failed: {transport.get_last_error()}") 