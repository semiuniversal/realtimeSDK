"""
Sequence command for the Realtime Hairbrush SDK CLI.

This module provides commands for managing and executing sequences of instructions.
"""

import click
import time
import json
import os
from typing import List, Tuple

from semantic_gcode.gcode.base import GCodeInstruction
from realtime_hairbrush.instructions.airbrush_instruction import AirbrushInstruction
from realtime_hairbrush.execution.validator import create_default_validator


@click.group()
def sequence():
    """
    Manage and execute instruction sequences.
    """
    pass


@sequence.command()
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
    
    # 3. Move to start position
    instructions.append(AirbrushInstruction.create_move(x=x1, y=y1, feedrate=3000))
    
    # 4. Lower to spray height
    instructions.append(AirbrushInstruction.create_spray_z_move())
    
    # 5. Start air
    instructions.append(AirbrushInstruction.create_air_control(tool, True))
    
    # 6. Wait for air to stabilize
    instructions.append(AirbrushInstruction.create_dwell(50))
    
    # 7. Start paint flow
    instructions.extend(AirbrushInstruction.create_paint_flow_start(tool, width, opacity))
    
    # 8. Move to end position
    instructions.append(AirbrushInstruction.create_move(x=x2, y=y2, feedrate=1500))
    
    # 9. Stop paint flow
    instructions.append(AirbrushInstruction.create_paint_flow_stop(tool))
    
    # 10. Wait for paint tail to clear
    instructions.append(AirbrushInstruction.create_dwell(50))
    
    # 11. Stop air
    instructions.append(AirbrushInstruction.create_air_control(tool, False))
    
    # 12. Raise to safe height
    instructions.append(AirbrushInstruction.create_safe_z_move())
    
    # Validate the sequence
    validator = create_default_validator()
    valid, issues = validator.validate_sequence(instructions)
    
    if not valid:
        click.echo("Sequence validation failed:")
        for issue in issues:
            click.echo(f"  {issue['message']} at instruction {issue['index']}")
        
        if not click.confirm("Continue anyway?"):
            return
    
    # Execute the sequence
    click.echo(f"Executing line stroke from ({x1}, {y1}) to ({x2}, {y2}) with tool {tool}...")
    
    for i, instruction in enumerate(instructions):
        click.echo(f"  {i+1}/{len(instructions)}: {str(instruction)}")
        result = transport.send_line(str(instruction))
        if not result:
            click.echo(f"Execution failed: {transport.get_last_error()}")
            return
        time.sleep(0.1)  # Small delay between commands
    
    click.echo("Line stroke complete")


@sequence.command()
@click.option('--file', '-f', required=True, help='JSON file containing the sequence')
@click.option('--validate/--no-validate', default=True, help='Validate the sequence before execution')
@click.pass_context
def execute(ctx, file, validate):
    """
    Execute a sequence from a JSON file.
    """
    transport = ctx.obj.get('transport')
    if not transport:
        click.echo("Error: Not connected")
        return
    
    # Load the sequence from the file
    if not os.path.exists(file):
        click.echo(f"Error: File not found: {file}")
        return
    
    try:
        with open(file, 'r') as f:
            sequence_data = json.load(f)
    except json.JSONDecodeError:
        click.echo(f"Error: Invalid JSON file: {file}")
        return
    
    # Convert the sequence data to instructions
    instructions = []
    for item in sequence_data:
        code_type = item.get('code_type')
        code_number = item.get('code_number')
        parameters = item.get('parameters', {})
        comment = item.get('comment')
        
        if code_type and code_number is not None:
            instruction = AirbrushInstruction(
                code_type=code_type,
                code_number=code_number,
                parameters=parameters,
                comment=comment
            )
            instructions.append(instruction)
    
    if not instructions:
        click.echo("Error: No valid instructions found in the file")
        return
    
    # Validate the sequence if requested
    if validate:
        validator = create_default_validator()
        valid, issues = validator.validate_sequence(instructions)
        
        if not valid:
            click.echo("Sequence validation failed:")
            for issue in issues:
                click.echo(f"  {issue['message']} at instruction {issue['index']}")
            
            if not click.confirm("Continue anyway?"):
                return
    
    # Execute the sequence
    click.echo(f"Executing sequence from {file} ({len(instructions)} instructions)...")
    
    for i, instruction in enumerate(instructions):
        click.echo(f"  {i+1}/{len(instructions)}: {str(instruction)}")
        result = transport.send_line(str(instruction))
        if not result:
            click.echo(f"Execution failed: {transport.get_last_error()}")
            return
        time.sleep(0.1)  # Small delay between commands
    
    click.echo("Sequence execution complete")


@sequence.command()
@click.option('--file', '-f', required=True, help='JSON file to save the sequence to')
@click.pass_context
def save_template(ctx, file):
    """
    Save a template sequence to a JSON file.
    """
    # Create a template sequence for a line stroke
    template = [
        {
            "code_type": "T",
            "code_number": 0,
            "parameters": {},
            "comment": "Select black airbrush"
        },
        {
            "code_type": "G",
            "code_number": 1,
            "parameters": {"Z": 5.0, "F": 1000},
            "comment": "Move to safe Z height"
        },
        {
            "code_type": "G",
            "code_number": 0,
            "parameters": {"X": 100.0, "Y": 100.0, "F": 3000},
            "comment": "Move to start position"
        },
        {
            "code_type": "G",
            "code_number": 1,
            "parameters": {"Z": 1.5, "F": 500},
            "comment": "Lower to spray height"
        },
        {
            "code_type": "M",
            "code_number": 106,
            "parameters": {"P": 2, "S": 1.0},
            "comment": "Air ON"
        },
        {
            "code_type": "G",
            "code_number": 4,
            "parameters": {"P": 50},
            "comment": "Wait for air to stabilize"
        },
        {
            "code_type": "G",
            "code_number": 91,
            "parameters": {},
            "comment": "Relative positioning"
        },
        {
            "code_type": "G",
            "code_number": 1,
            "parameters": {"U": 2.0, "F": 300},
            "comment": "Start paint flow"
        },
        {
            "code_type": "G",
            "code_number": 90,
            "parameters": {},
            "comment": "Absolute positioning"
        },
        {
            "code_type": "G",
            "code_number": 1,
            "parameters": {"X": 200.0, "Y": 200.0, "F": 1500},
            "comment": "Move to end position"
        },
        {
            "code_type": "M",
            "code_number": 18,
            "parameters": {"U": None},
            "comment": "Stop paint flow"
        },
        {
            "code_type": "G",
            "code_number": 4,
            "parameters": {"P": 50},
            "comment": "Wait for paint tail to clear"
        },
        {
            "code_type": "M",
            "code_number": 106,
            "parameters": {"P": 2, "S": 0.0},
            "comment": "Air OFF"
        },
        {
            "code_type": "G",
            "code_number": 1,
            "parameters": {"Z": 5.0, "F": 1000},
            "comment": "Raise to safe height"
        }
    ]
    
    # Save the template to the file
    try:
        with open(file, 'w') as f:
            json.dump(template, f, indent=2)
        click.echo(f"Template sequence saved to {file}")
    except Exception as e:
        click.echo(f"Error saving template: {e}")


@sequence.command()
@click.option('--file', '-f', required=True, help='JSON file containing the sequence')
@click.pass_context
def validate(ctx, file):
    """
    Validate a sequence from a JSON file.
    """
    # Load the sequence from the file
    if not os.path.exists(file):
        click.echo(f"Error: File not found: {file}")
        return
    
    try:
        with open(file, 'r') as f:
            sequence_data = json.load(f)
    except json.JSONDecodeError:
        click.echo(f"Error: Invalid JSON file: {file}")
        return
    
    # Convert the sequence data to instructions
    instructions = []
    for item in sequence_data:
        code_type = item.get('code_type')
        code_number = item.get('code_number')
        parameters = item.get('parameters', {})
        comment = item.get('comment')
        
        if code_type and code_number is not None:
            instruction = AirbrushInstruction(
                code_type=code_type,
                code_number=code_number,
                parameters=parameters,
                comment=comment
            )
            instructions.append(instruction)
    
    if not instructions:
        click.echo("Error: No valid instructions found in the file")
        return
    
    # Validate the sequence
    validator = create_default_validator()
    valid, issues = validator.validate_sequence(instructions)
    
    if valid:
        click.echo(f"Sequence is valid ({len(instructions)} instructions)")
    else:
        click.echo(f"Sequence validation failed ({len(issues)} issues):")
        for issue in issues:
            click.echo(f"  {issue['message']} at instruction {issue['index']}")
