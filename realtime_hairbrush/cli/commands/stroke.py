"""
Stroke command for the Realtime Hairbrush SDK CLI.

This module provides commands for executing different types of strokes.
"""

import click
import time
import math
from typing import List, Tuple

from semantic_gcode.gcode.base import GCodeInstruction
from realtime_hairbrush.instructions.airbrush_instruction import AirbrushInstruction
from realtime_hairbrush.execution.validator import create_default_validator


@click.group()
def stroke():
    """
    Execute different types of strokes.
    """
    pass


@stroke.command()
@click.option('--tool', '-t', type=int, required=True, help='Tool index (0=black, 1=white)')
@click.option('--x1', type=float, required=True, help='Start X position')
@click.option('--y1', type=float, required=True, help='Start Y position')
@click.option('--x2', type=float, required=True, help='End X position')
@click.option('--y2', type=float, required=True, help='End Y position')
@click.option('--width', '-w', type=float, default=1.0, help='Stroke width (0.0-1.0)')
@click.option('--opacity', '-o', type=float, default=1.0, help='Stroke opacity (0.0-1.0)')
@click.pass_context
def line(ctx, tool, x1, y1, x2, y2, width, opacity):
    """
    Execute a straight line stroke.
    """
    from realtime_hairbrush.instructions.mixins.sequence import SequenceMixin
    
    transport = ctx.obj.get('transport')
    if not transport:
        click.echo("Error: Not connected")
        return
    
    # Validate the tool index
    if tool not in [0, 1]:
        click.echo(f"Error: Invalid tool index: {tool}")
        return
    
    # Create a sequence mixin instance
    sequence_mixin = SequenceMixin()
    
    # Generate the stroke sequence
    path_points = [(x1, y1), (x2, y2)]
    stroke_sequence = sequence_mixin.execute_stroke(
        tool_index=tool,
        path_points=path_points,
        width=width,
        opacity=opacity
    )
    
    # Execute the sequence
    click.echo(f"Executing line stroke from ({x1}, {y1}) to ({x2}, {y2}) with tool {tool}...")
    
    for i, instruction in enumerate(stroke_sequence):
        click.echo(f"  {i+1}/{len(list(stroke_sequence))}: {str(instruction)}")
        result = transport.send_line(str(instruction))
        if not result:
            click.echo(f"Execution failed: {transport.get_last_error()}")
            return
        time.sleep(0.1)  # Small delay between commands
    
    click.echo("Line stroke complete")


@stroke.command()
@click.option('--tool', '-t', type=int, required=True, help='Tool index (0=black, 1=white)')
@click.option('--cx', type=float, required=True, help='Center X position')
@click.option('--cy', type=float, required=True, help='Center Y position')
@click.option('--radius', '-r', type=float, required=True, help='Circle radius')
@click.option('--segments', '-s', type=int, default=36, help='Number of segments')
@click.option('--width', '-w', type=float, default=1.0, help='Stroke width (0.0-1.0)')
@click.option('--opacity', '-o', type=float, default=1.0, help='Stroke opacity (0.0-1.0)')
@click.pass_context
def circle(ctx, tool, cx, cy, radius, segments, width, opacity):
    """
    Execute a circle stroke.
    """
    from realtime_hairbrush.instructions.mixins.sequence import SequenceMixin
    
    transport = ctx.obj.get('transport')
    if not transport:
        click.echo("Error: Not connected")
        return
    
    # Validate the tool index
    if tool not in [0, 1]:
        click.echo(f"Error: Invalid tool index: {tool}")
        return
    
    # Generate the circle path
    path_points = []
    for i in range(segments + 1):  # +1 to close the circle
        angle = 2 * math.pi * i / segments
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        path_points.append((x, y))
    
    # Create a sequence mixin instance
    sequence_mixin = SequenceMixin()
    
    # Generate the stroke sequence
    stroke_sequence = sequence_mixin.execute_stroke(
        tool_index=tool,
        path_points=path_points,
        width=width,
        opacity=opacity
    )
    
    # Execute the sequence
    click.echo(f"Executing circle stroke at ({cx}, {cy}) with radius {radius} and tool {tool}...")
    
    for i, instruction in enumerate(stroke_sequence):
        click.echo(f"  {i+1}/{len(list(stroke_sequence))}: {str(instruction)}")
        result = transport.send_line(str(instruction))
        if not result:
            click.echo(f"Execution failed: {transport.get_last_error()}")
            return
        time.sleep(0.1)  # Small delay between commands
    
    click.echo("Circle stroke complete")


@stroke.command()
@click.option('--tool', '-t', type=int, required=True, help='Tool index (0=black, 1=white)')
@click.option('--x', type=float, required=True, help='X position')
@click.option('--y', type=float, required=True, help='Y position')
@click.option('--width', '-w', type=float, default=1.0, help='Stroke width (0.0-1.0)')
@click.option('--opacity', '-o', type=float, default=1.0, help='Stroke opacity (0.0-1.0)')
@click.option('--duration', '-d', type=float, default=1.0, help='Duration in seconds')
@click.pass_context
def dot(ctx, tool, x, y, width, opacity, duration):
    """
    Execute a dot stroke (single point).
    """
    transport = ctx.obj.get('transport')
    if not transport:
        click.echo("Error: Not connected")
        return
    
    # Validate the tool index
    if tool not in [0, 1]:
        click.echo(f"Error: Invalid tool index: {tool}")
        return
    
    # Get configuration values
    config_manager = ctx.obj.get('config_manager')
    safe_z_height = 5.0
    spray_z_height = 1.5
    if config_manager:
        safe_z_height = config_manager.get_safe_z_height()
        spray_z_height = config_manager.get_spray_z_height()
    
    # Create the sequence of instructions
    instructions = []
    
    # 1. Select tool
    instructions.append(AirbrushInstruction.create_tool_select(tool))
    
    # 2. Move to safe Z height
    instructions.append(AirbrushInstruction.create_safe_z_move())
    
    # 3. Move to position
    instructions.append(AirbrushInstruction.create_move(x=x, y=y, feedrate=3000))
    
    # 4. Lower to spray height
    instructions.append(AirbrushInstruction.create_spray_z_move())
    
    # 5. Start air
    instructions.append(AirbrushInstruction.create_air_control(tool, True))
    
    # 6. Wait for air to stabilize
    instructions.append(AirbrushInstruction.create_dwell(50))
    
    # 7. Start paint flow
    instructions.extend(AirbrushInstruction.create_paint_flow_start(tool, width, opacity))
    
    # 8. Wait for the specified duration
    dwell_ms = int(duration * 1000)
    instructions.append(AirbrushInstruction.create_dwell(dwell_ms))
    
    # 9. Stop paint flow
    instructions.append(AirbrushInstruction.create_paint_flow_stop(tool))
    
    # 10. Wait for paint tail to clear
    instructions.append(AirbrushInstruction.create_dwell(50))
    
    # 11. Stop air
    instructions.append(AirbrushInstruction.create_air_control(tool, False))
    
    # 12. Raise to safe height
    instructions.append(AirbrushInstruction.create_safe_z_move())
    
    # Execute the sequence
    click.echo(f"Executing dot stroke at ({x}, {y}) with tool {tool} for {duration}s...")
    
    for i, instruction in enumerate(instructions):
        click.echo(f"  {i+1}/{len(instructions)}: {str(instruction)}")
        result = transport.send_line(str(instruction))
        if not result:
            click.echo(f"Execution failed: {transport.get_last_error()}")
            return
        time.sleep(0.1)  # Small delay between commands
    
    click.echo("Dot stroke complete")


@stroke.command()
@click.option('--tool', '-t', type=int, required=True, help='Tool index (0=black, 1=white)')
@click.option('--x1', type=float, required=True, help='Start X position')
@click.option('--y1', type=float, required=True, help='Start Y position')
@click.option('--x2', type=float, required=True, help='End X position')
@click.option('--y2', type=float, required=True, help='End Y position')
@click.option('--segments', '-s', type=int, default=10, help='Number of segments')
@click.option('--width', '-w', type=float, default=1.0, help='Stroke width (0.0-1.0)')
@click.option('--opacity', '-o', type=float, default=1.0, help='Stroke opacity (0.0-1.0)')
@click.pass_context
def gradient(ctx, tool, x1, y1, x2, y2, segments, width, opacity):
    """
    Execute a gradient stroke with varying opacity.
    """
    from realtime_hairbrush.instructions.mixins.sequence import SequenceMixin
    
    transport = ctx.obj.get('transport')
    if not transport:
        click.echo("Error: Not connected")
        return
    
    # Validate the tool index
    if tool not in [0, 1]:
        click.echo(f"Error: Invalid tool index: {tool}")
        return
    
    # Generate the path with segments
    path_points = []
    for i in range(segments + 1):
        t = i / segments
        x = x1 + (x2 - x1) * t
        y = y1 + (y2 - y1) * t
        path_points.append((x, y))
    
    # Create a sequence mixin instance
    sequence_mixin = SequenceMixin()
    
    # Generate the stroke sequence
    stroke_sequence = sequence_mixin.execute_stroke(
        tool_index=tool,
        path_points=path_points,
        width=width,
        opacity=opacity
    )
    
    # Execute the sequence
    click.echo(f"Executing gradient stroke from ({x1}, {y1}) to ({x2}, {y2}) with tool {tool}...")
    
    for i, instruction in enumerate(stroke_sequence):
        click.echo(f"  {i+1}/{len(list(stroke_sequence))}: {str(instruction)}")
        result = transport.send_line(str(instruction))
        if not result:
            click.echo(f"Execution failed: {transport.get_last_error()}")
            return
        time.sleep(0.1)  # Small delay between commands
    
    click.echo("Gradient stroke complete")
