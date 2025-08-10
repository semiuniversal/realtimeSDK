"""
Interactive mode for the Realtime Hairbrush SDK CLI.

This module provides an interactive mode for controlling the airbrush plotter
using prompt_toolkit for cross-platform command-line interface support.
"""

import click
import os
import time
import sys
from typing import Dict, Any, Optional, List, Callable

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style

from semantic_gcode.gcode.base import GCodeInstruction
from realtime_hairbrush.instructions.airbrush_instruction import AirbrushInstruction
from realtime_hairbrush.operations.high_level import (
    MoveTo, DrawLine, SprayDot, Sequence, SafeZ, SprayZ, AirControl, PaintControl
)
from realtime_hairbrush.cli.utils.command_parser import CommandParameterCompleter, parse_commands_yaml, parse_command_args


class AirbrushShell:
    """
    Interactive shell for controlling the airbrush plotter.
    Uses prompt_toolkit for cross-platform support.
    """
    
    def __init__(self, ctx):
        """
        Initialize the shell.
        
        Args:
            ctx: Click context
        """
        self.ctx = ctx
        self.transport = ctx.obj.get('transport')
        self.config_manager = ctx.obj.get('config_manager')
        self.current_tool = None
        self.running = True
        # Optional runtime dispatcher injected by the interactive launcher
        self.dispatcher = ctx.obj.get('dispatcher')
        
        # Configure history file
        history_file = ".airbrush_history"
        if self.config_manager:
            cli_config = self.config_manager.get_cli_config()
            history_file = cli_config.get("history_file", history_file)
        
        self.history_file = os.path.expanduser(f"~/{history_file}")
        
        # Set up command registry
        self.commands = {}
        self._register_commands()
        
        # Load commands.yaml for enhanced completion and help
        self.yaml_path = os.path.join(os.path.dirname(__file__), '..', '..', 'commands.yaml')
        self.yaml_commands = parse_commands_yaml(self.yaml_path)
        
        # Set up prompt_toolkit session with enhanced completer
        self.completer = CommandParameterCompleter.create_completer(self.yaml_path)
        
        self.session = PromptSession(
            history=FileHistory(self.history_file),
            auto_suggest=AutoSuggestFromHistory(),
            completer=self.completer,
            style=Style.from_dict({
                'prompt': 'ansicyan bold',
            })
        )
    
    def _register_commands(self):
        """Register all available commands."""
        # Load commands.yaml first
        self.yaml_path = os.path.join(os.path.dirname(__file__), '..', '..', 'commands.yaml')
        self.yaml_commands = parse_commands_yaml(self.yaml_path)
        
        # Only register commands that are in the YAML file
        yaml_command_names = set(self.yaml_commands.keys())
        
        # Basic commands (always available)
        if 'help' in yaml_command_names:
            self.commands['help'] = (self.do_help, self.yaml_commands['help'].get('purpose', 'Show help for available commands'))
        else:
            self.commands['help'] = (self.do_help, 'Show help for available commands')
            
        if 'exit' in yaml_command_names:
            self.commands['exit'] = (self.do_exit, self.yaml_commands['exit'].get('purpose', 'Exit the interactive shell'))
        else:
            self.commands['exit'] = (self.do_exit, 'Exit the interactive shell')
            
        if 'quit' in yaml_command_names:
            self.commands['quit'] = (self.do_exit, self.yaml_commands['quit'].get('purpose', 'Exit the interactive shell'))
        else:
            self.commands['quit'] = (self.do_exit, 'Exit the interactive shell')
        
        # Machine control commands - only register if in YAML
        command_handlers = {
            'home': self.do_home,
            'tool': self.do_tool,
            'move': self.do_move,
            'safez': self.do_safe_z,
            'sprayz': self.do_spray_z,
            'air': self.do_air,
            'paint': self.do_paint,
            'dwell': self.do_dwell,
            'gcode': self.do_gcode,
            'line': self.do_line,
            'circle': self.do_circle,
            'dot': self.do_dot,
            'gradient': self.do_gradient
        }
        
        # Register only commands that are in the YAML file
        for cmd_name, handler in command_handlers.items():
            if cmd_name in yaml_command_names:
                self.commands[cmd_name] = (handler, self.yaml_commands[cmd_name].get('purpose', f'Execute {cmd_name} command'))
    
    def register_command(self, name: str, func: Callable, help_text: str):
        """Register a new command."""
        self.commands[name] = (func, help_text)
        # Update command list for the completer
        # Note: We don't need to update the completer here anymore as it's built from commands.yaml
    
    def do_help(self, arg: str) -> None:
        """Show help for available commands."""
        if arg:
            # First try to get help from YAML definitions
            if arg in self.yaml_commands:
                cmd_def = self.yaml_commands[arg]
                click.echo(f"{arg}: {cmd_def.get('purpose', '')}")
                
                # Show parameters
                params = cmd_def.get('params', [])
                if params:
                    click.echo("\nParameters:")
                    # Handle both list and dict formats
                    if isinstance(params, list):
                        for param in params:
                            if isinstance(param, dict):
                                for param_name, param_def in param.items():
                                    optional = " (optional)" if param_def.get('optional', True) else " (required)"
                                    click.echo(f"  {param_name}{optional}: {param_def.get('purpose', '')}")
                                    
                                    # Show accepted values
                                    accepts = param_def.get('accepts', [])
                                    if accepts:
                                        click.echo(f"    Accepts: {', '.join(str(val) for val in accepts)}")
                    elif isinstance(params, dict):
                        for param_name, param_def in params.items():
                            optional = " (optional)" if param_def.get('optional', True) else " (required)"
                            click.echo(f"  {param_name}{optional}: {param_def.get('purpose', '')}")
                            
                            # Show accepted values
                            accepts = param_def.get('accepts', [])
                            if accepts:
                                click.echo(f"    Accepts: {', '.join(str(val) for val in accepts)}")
                
                # Show usage examples
                examples = cmd_def.get('usage-examples', [])
                if examples:
                    click.echo("\nExamples:")
                    for example in examples:
                        click.echo(f"  {example}")
            # Fallback to registered commands
            elif arg in self.commands:
                _, help_text = self.commands[arg]
                click.echo(f"{arg}: {help_text}")
            else:
                click.echo(f"Unknown command: {arg}")
        else:
            # Show general help
            click.echo("Available commands:")
            
            # Get all commands from both YAML and registered commands
            all_commands = set(self.yaml_commands.keys()) | set(self.commands.keys())
            
            # Group commands by category if available
            categories = {}
            for cmd_name in all_commands:
                # Try to get category from YAML
                if cmd_name in self.yaml_commands:
                    cmd_def = self.yaml_commands[cmd_name]
                    category = cmd_def.get('category', 'General')
                    purpose = cmd_def.get('purpose', '')
                else:
                    category = 'General'
                    purpose = self.commands.get(cmd_name, ('', ''))[1]
                
                if category not in categories:
                    categories[category] = []
                categories[category].append((cmd_name, purpose))
            
            # Print commands by category
            for category, cmds in sorted(categories.items()):
                click.echo(f"\n{category}:")
                max_len = max(len(cmd) for cmd, _ in cmds)
                for cmd, purpose in sorted(cmds):
                    click.echo(f"  {cmd.ljust(max_len)}  {purpose}")
    
    def do_exit(self, arg: str) -> bool:
        """Exit the interactive shell."""
        click.echo("Exiting interactive shell")
        self.running = False
        # Use sys.exit(0) to cleanly exit the program
        import sys
        sys.exit(0)
        return True
    
    def do_home(self, arg: str) -> None:
        """Home specified axes."""
        if not self.transport:
            click.echo("Error: Not connected")
            return
        
        # Default to all axes if not specified
        axes = arg.strip().lower() if arg.strip() else 'all'
        
        # Map axes string to actual axes
        axes_map = {
            'all': None,
            'xy': ['X', 'Y'],
            'z': ['Z'],
            'u': ['U'],
            'v': ['V']
        }
        
        # Get the axes to home
        axes_to_home = axes_map.get(axes)
        if axes_to_home is None and axes != 'all':
            click.echo(f"Error: Invalid axes: {axes}")
            return
        
        # Prefer proper G-code classes with dispatcher
        try:
            from semantic_gcode.dict.gcode_commands.G28.G28 import G28_Home
            from semantic_gcode.dict.gcode_commands.M400.M400 import M400_WaitForMoves
            g28 = G28_Home.create(axes=axes_to_home)
            m400 = M400_WaitForMoves.create()
            click.echo(f"Homing {axes}...")
            if self.dispatcher:
                self.dispatcher.enqueue(g28)
                self.dispatcher.enqueue(m400)
                return
            # Fallback: direct transport
            if not self.transport.send_line(str(g28)):
                click.echo(f"Homing failed: {self.transport.get_last_error()}")
                return
            # Wait for completion via M400
            self.transport.query(str(m400))
            click.echo("Homing complete (no dispatcher)")
        except Exception:
            # Legacy fallback to AirbrushInstruction
            instruction = AirbrushInstruction.create_home(axes_to_home)
            click.echo(f"Homing {axes}...")
            result = self.transport.send_line(str(instruction))
            if not result:
                click.echo(f"Homing failed: {self.transport.get_last_error()}")
                return
            click.echo("Waiting for homing to complete...")
            if self.transport.wait_for_idle(verbose=True):
                click.echo("Homing complete")
            else:
                click.echo(f"Homing may not have completed: {self.transport.get_last_error()}")
    
    def do_tool(self, arg: str) -> None:
        """Select tool."""
        if not self.transport:
            click.echo("Error: Not connected")
            return
        
        try:
            index = int(arg.strip())
        except ValueError:
            click.echo("Error: Tool index must be a number")
            return
        
        # Validate the tool index
        if index not in [0, 1]:
            click.echo(f"Error: Invalid tool index: {index}")
            return
        
        # Prefer proper T command class via dispatcher
        try:
            from semantic_gcode.dict.gcode_commands.T.T import T_SelectTool
            from semantic_gcode.dict.gcode_commands.M400.M400 import M400_WaitForMoves
            tsel = T_SelectTool.create(tool_number=index)
            m400 = M400_WaitForMoves.create()
            click.echo(f"Selecting tool {index}...")
            if self.dispatcher:
                self.dispatcher.enqueue(tsel)
                self.dispatcher.enqueue(m400)
                self.current_tool = index
                return
            # Fallback direct
            if self.transport.send_line(str(tsel)):
                self.transport.query(str(m400))
                click.echo(f"Tool {index} selected (no dispatcher)")
                self.current_tool = index
            else:
                click.echo(f"Tool selection failed: {self.transport.get_last_error()}")
        except Exception:
            # Legacy fallback
            instruction = AirbrushInstruction.create_tool_select(index)
            click.echo(f"Selecting tool {index}...")
            result = self.transport.send_line(str(instruction))
            if result:
                click.echo(f"Tool {index} selected")
                self.current_tool = index
            else:
                click.echo(f"Tool selection failed: {self.transport.get_last_error()}")
    
    def do_move(self, arg: str) -> None:
        """Move to position."""
        if not self.transport:
            click.echo("Error: Not connected")
            return
        
        parts = arg.strip().split()
        if not parts:
            click.echo("Error: Provide coordinates, e.g., 'move x10 y20 [z5] [f1000]'")
            return
        # Support both positional (x y [z] [f]) and keyed (x10 y20 z5 f1000) forms
        x = y = z = feedrate = None
        keyed = {p[0].lower(): p[1:] for p in parts if len(p) >= 2 and p[0].lower() in ('x','y','z','f') and p[1:].replace('.','',1).replace('-','',1).isdigit()}
        if keyed:
            if 'x' in keyed:
                x = float(keyed['x'])
            if 'y' in keyed:
                y = float(keyed['y'])
            if 'z' in keyed:
                z = float(keyed['z'])
            if 'f' in keyed:
                feedrate = float(keyed['f'])
        else:
            # Positional fallback
            try:
                x = float(parts[0])
                y = float(parts[1]) if len(parts) > 1 else None
                z = float(parts[2]) if len(parts) > 2 else None
                feedrate = float(parts[3]) if len(parts) > 3 else None
            except ValueError:
                click.echo("Error: Invalid coordinates")
                return
        if x is None or y is None:
            click.echo("Error: At least X and Y are required")
            return
        
        # Prefer proper G1 via dispatcher
        try:
            from semantic_gcode.dict.gcode_commands.G1.G1 import G1_LinearMove
            from semantic_gcode.dict.gcode_commands.M400.M400 import M400_WaitForMoves
            params = {}
            if x is not None:
                params['x'] = x
            if y is not None:
                params['y'] = y
            if z is not None:
                params['z'] = z
            if feedrate is not None:
                params['feedrate'] = feedrate
            g1 = G1_LinearMove.create(**params)
            m400 = M400_WaitForMoves.create()
            click.echo(f"Moving to X{x} Y{y}{(' Z'+str(z)) if z is not None else ''}{(' F'+str(feedrate)) if feedrate is not None else ''}...")
            if self.dispatcher:
                self.dispatcher.enqueue(g1)
                self.dispatcher.enqueue(m400)
                return
            # Fallback direct
            self.transport.send_line(str(g1))
            self.transport.query(str(m400))
            click.echo("Move complete (no dispatcher)")
        except Exception:
            # Fallback to high-level operation
            move_op = MoveTo(x=x, y=y, z=z, feedrate=feedrate)
            move_op.execute(self.transport, verbose=True, wait_for_completion=True)
    
    def do_safe_z(self, arg: str) -> None:
        """Move to safe Z height."""
        if not self.transport:
            click.echo("Error: Not connected")
            return
        
        try:
            feedrate = float(arg.strip()) if arg.strip() else None
        except ValueError:
            click.echo("Error: Invalid feedrate")
            return
        
        # Use the high-level SafeZ operation
        safe_z_op = SafeZ(feedrate=feedrate)
        safe_z_op.execute(self.transport, verbose=True, wait_for_completion=True)
    
    def do_spray_z(self, arg: str) -> None:
        """Move to spray Z height."""
        if not self.transport:
            click.echo("Error: Not connected")
            return
        
        try:
            feedrate = float(arg.strip()) if arg.strip() else None
        except ValueError:
            click.echo("Error: Invalid feedrate")
            return
        
        # Use the high-level SprayZ operation
        spray_z_op = SprayZ(feedrate=feedrate)
        spray_z_op.execute(self.transport, verbose=True, wait_for_completion=True)
    
    def do_air(self, arg: str) -> None:
        """Control air."""
        if not self.transport:
            click.echo("Error: Not connected")
            return
        
        parts = arg.strip().split()
        if len(parts) < 2:
            click.echo("Error: Tool index and state are required")
            return
        
        try:
            tool = int(parts[0])
            state_str = parts[1].lower()
            
            if state_str in ['on', 'true', '1', 'yes']:
                state = True
            elif state_str in ['off', 'false', '0', 'no']:
                state = False
            else:
                click.echo("Error: State must be 'on' or 'off'")
                return
        except ValueError:
            click.echo("Error: Invalid parameters")
            return
        
        # Validate the tool index
        if tool not in [0, 1]:
            click.echo(f"Error: Invalid tool index: {tool}")
            return
        
        # Use the high-level AirControl operation
        air_op = AirControl(tool_index=tool, on=state)
        air_op.execute(self.transport, verbose=True, wait_for_completion=True)
    
    def do_paint(self, arg: str) -> None:
        """Control paint."""
        if not self.transport:
            click.echo("Error: Not connected")
            return
        
        parts = arg.strip().split()
        if not parts:
            click.echo("Error: Action (start/stop) is required")
            return
        
        action = parts[0].lower()
        
        if action == 'start':
            if len(parts) < 2:
                click.echo("Error: Tool index is required for paint start")
                return
            
            try:
                tool = int(parts[1])
                width = float(parts[2]) if len(parts) > 2 else 1.0
                opacity = float(parts[3]) if len(parts) > 3 else 1.0
            except ValueError:
                click.echo("Error: Invalid parameters")
                return
            
            # Validate the tool index and parameters
            if tool not in [0, 1]:
                click.echo(f"Error: Invalid tool index: {tool}")
                return
            
            if not (0.0 <= width <= 1.0):
                click.echo(f"Error: Width must be between 0.0 and 1.0")
                return
            
            if not (0.0 <= opacity <= 1.0):
                click.echo(f"Error: Opacity must be between 0.0 and 1.0")
                return
            
            # Use the high-level PaintControl operation
            paint_op = PaintControl(tool_index=tool, action='start', width=width, opacity=opacity)
            paint_op.execute(self.transport, verbose=True, wait_for_completion=True)
        
        elif action == 'stop':
            if len(parts) < 2:
                click.echo("Error: Tool index is required for paint stop")
                return
            
            try:
                tool = int(parts[1])
            except ValueError:
                click.echo("Error: Invalid tool index")
                return
            
            # Validate the tool index
            if tool not in [0, 1]:
                click.echo(f"Error: Invalid tool index: {tool}")
                return
            
            # Use the high-level PaintControl operation
            paint_op = PaintControl(tool_index=tool, action='stop')
            paint_op.execute(self.transport, verbose=True, wait_for_completion=True)
        
        else:
            click.echo(f"Error: Unknown action: {action}")
            click.echo("Valid actions: start, stop")
    
    def do_dwell(self, arg: str) -> None:
        """Dwell for specified time."""
        if not self.transport:
            click.echo("Error: Not connected")
            return
        
        try:
            milliseconds = int(arg.strip()) if arg.strip() else 50
        except ValueError:
            click.echo("Error: Invalid dwell time")
            return
        
        # Create the dwell instruction
        instruction = AirbrushInstruction.create_dwell(milliseconds)
        
        # Send the instruction
        click.echo(f"Dwelling for {milliseconds} ms...")
        result = self.transport.send_line(str(instruction))
        
        if result:
            # Actually wait for the dwell time to complete
            time.sleep(milliseconds / 1000.0)
            click.echo("Dwell complete")
        else:
            click.echo(f"Dwell failed: {self.transport.get_last_error()}")
    
    def do_gcode(self, arg: str) -> None:
        """Send raw G-code."""
        if not self.transport:
            click.echo("Error: Not connected")
            return
        
        if not arg.strip():
            click.echo("Error: G-code command is required")
            return
        
        # Send the raw G-code
        click.echo(f"Sending: {arg}")
        result = self.transport.send_line(arg)
        
        if result:
            click.echo("Command sent successfully")
        else:
            click.echo(f"Command failed: {self.transport.get_last_error()}")
    
    def do_line(self, arg: str) -> None:
        """Execute a line stroke."""
        if not self.transport:
            click.echo("Error: Not connected")
            return
        parts = arg.strip().split()
        if len(parts) < 5:
            click.echo("Usage: line <tool> <x1> <y1> <x2> <y2> [width] [opacity]")
            return
        try:
            tool = int(parts[0])
            x1 = float(parts[1])
            y1 = float(parts[2])
            x2 = float(parts[3])
            y2 = float(parts[4])
            width = float(parts[5]) if len(parts) > 5 else 1.0
            opacity = float(parts[6]) if len(parts) > 6 else 1.0
        except ValueError:
            click.echo("Error: Invalid arguments")
            return
        if tool not in [0, 1]:
            click.echo(f"Error: Invalid tool index: {tool}")
            return
        if not (0.0 <= width <= 1.0):
            click.echo("Error: Width must be between 0.0 and 1.0")
            return
        if not (0.0 <= opacity <= 1.0):
            click.echo("Error: Opacity must be between 0.0 and 1.0")
            return
        
        # Use the new high-level DrawLine operation
        line_op = DrawLine(x1=x1, y1=y1, x2=x2, y2=y2, width=width, opacity=opacity)
        line_op.execute(self.transport, verbose=True, wait_for_completion=True)

    def do_circle(self, arg: str) -> None:
        """Execute a circle stroke."""
        if not self.transport:
            click.echo("Error: Not connected")
            return
        parts = arg.strip().split()
        if len(parts) < 4:
            click.echo("Usage: circle <tool> <cx> <cy> <radius> [segments] [width] [opacity]")
            return
        try:
            tool = int(parts[0])
            cx = float(parts[1])
            cy = float(parts[2])
            radius = float(parts[3])
            segments = int(parts[4]) if len(parts) > 4 else 36
            width = float(parts[5]) if len(parts) > 5 else 1.0
            opacity = float(parts[6]) if len(parts) > 6 else 1.0
        except ValueError:
            click.echo("Error: Invalid arguments")
            return
        if tool not in [0, 1]:
            click.echo(f"Error: Invalid tool index: {tool}")
            return
        if not (0.0 <= width <= 1.0):
            click.echo("Error: Width must be between 0.0 and 1.0")
            return
        if not (0.0 <= opacity <= 1.0):
            click.echo("Error: Opacity must be between 0.0 and 1.0")
            return
        
        # Generate circle points
        import math
        path_points = [
            (
                cx + radius * math.cos(2 * math.pi * i / segments),
                cy + radius * math.sin(2 * math.pi * i / segments)
            )
            for i in range(segments + 1)
        ]
        
        # Create a sequence of MoveTo operations for the circle
        operations = []
        
        # First point is a MoveTo
        first_point = path_points[0]
        operations.append(MoveTo(x=first_point[0], y=first_point[1]))
        
        # Remaining points are DrawLine operations
        for i in range(1, len(path_points)):
            prev_point = path_points[i-1]
            curr_point = path_points[i]
            operations.append(DrawLine(
                x1=prev_point[0], y1=prev_point[1],
                x2=curr_point[0], y2=curr_point[1],
                width=width, opacity=opacity
            ))
        
        # Execute the sequence
        sequence = Sequence(operations)
        sequence.execute(self.transport, verbose=True, wait_for_completion=True)

    def do_dot(self, arg: str) -> None:
        """Execute a dot stroke."""
        if not self.transport:
            click.echo("Error: Not connected")
            return
        parts = arg.strip().split()
        if len(parts) < 3:
            click.echo("Usage: dot <tool> <x> <y> [width] [opacity] [duration]")
            return
        try:
            tool = int(parts[0])
            x = float(parts[1])
            y = float(parts[2])
            width = float(parts[3]) if len(parts) > 3 else 1.0
            opacity = float(parts[4]) if len(parts) > 4 else 1.0
            duration = float(parts[5]) if len(parts) > 5 else 1.0
        except ValueError:
            click.echo("Error: Invalid arguments")
            return
        if tool not in [0, 1]:
            click.echo(f"Error: Invalid tool index: {tool}")
            return
        if not (0.0 <= width <= 1.0):
            click.echo("Error: Width must be between 0.0 and 1.0")
            return
        if not (0.0 <= opacity <= 1.0):
            click.echo("Error: Opacity must be between 0.0 and 1.0")
            return
        
        # Use the high-level SprayDot operation
        dot_op = SprayDot(x=x, y=y, diameter=width, opacity=opacity, duration=duration)
        dot_op.execute(self.transport, verbose=True, wait_for_completion=True)

    def do_gradient(self, arg: str) -> None:
        """Execute a gradient stroke."""
        if not self.transport:
            click.echo("Error: Not connected")
            return
        parts = arg.strip().split()
        if len(parts) < 7:
            click.echo("Usage: gradient <tool> <x1> <y1> <x2> <y2> <segments> [width] [opacity]")
            return
        try:
            tool = int(parts[0])
            x1 = float(parts[1])
            y1 = float(parts[2])
            x2 = float(parts[3])
            y2 = float(parts[4])
            segments = int(parts[5])
            width = float(parts[6]) if len(parts) > 6 else 1.0
            opacity = float(parts[7]) if len(parts) > 7 else 1.0
        except ValueError:
            click.echo("Error: Invalid arguments")
            return
        if tool not in [0, 1]:
            click.echo(f"Error: Invalid tool index: {tool}")
            return
        if not (0.0 <= width <= 1.0):
            click.echo("Error: Width must be between 0.0 and 1.0")
            return
        if not (0.0 <= opacity <= 1.0):
            click.echo("Error: Opacity must be between 0.0 and 1.0")
            return
        from realtime_hairbrush.instructions.mixins.sequence import SequenceMixin
        sequence_mixin = SequenceMixin()
        stroke_sequence = sequence_mixin.execute_gradient(
            tool_index=tool,
            x1=x1,
            y1=y1,
            x2=x2,
            y2=y2,
            segments=segments,
            width=width,
            opacity=opacity
        )
        click.echo(f"Executing gradient stroke from ({x1}, {y1}) to ({x2}, {y2}) with tool {tool}...")
        for i, instruction in enumerate(stroke_sequence):
            click.echo(f"  {i+1}: {str(instruction)}")
            result = self.transport.send_line(str(instruction))
            if not result:
                click.echo(f"Execution failed: {self.transport.get_last_error()}")
                return
            time.sleep(0.1)
        click.echo("Gradient stroke complete")
    
    def cmdloop(self):
        """Run the command loop."""
        click.echo("Realtime Hairbrush SDK Interactive Shell. Type help or ? for help.")
        
        while self.running:
            try:
                text = self.session.prompt('airbrush> ')
                
                if not text.strip():
                    continue
                
                # Handle '?' as help
                if text.strip() == '?':
                    self.do_help('')
                    continue
                
                # Parse the command and arguments
                parts = text.split(maxsplit=1)
                cmd = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else ''
                
                # Execute the command
                if cmd in self.commands:
                    command_func, _ = self.commands[cmd]
                    
                    # If the command is in YAML, try to parse and validate arguments
                    if cmd in self.yaml_commands:
                        cmd_def = self.yaml_commands[cmd]
                        args_dict, error = parse_command_args(cmd, arg, cmd_def)
                        if error:
                            click.echo(f"Error: {error}")
                            continue
                        
                        # If parsing succeeded, we could pass args_dict to command_func
                        # But for now, we'll just pass the raw arg string for backward compatibility
                    
                    if command_func(arg):
                        break
                else:
                    click.echo(f"Unknown command: {cmd}")
                    click.echo("Type 'help' or '?' to see available commands.")
                
            except KeyboardInterrupt:
                click.echo("\nInterrupted. Use 'exit' to quit.")
            except EOFError:
                click.echo("\nEOF detected. Exiting.")
                break
            except Exception as e:
                click.echo(f"Error: {e}")
        
        return True


def start_interactive_mode(ctx):
    """
    Start the interactive mode.
    
    Args:
        ctx: Click context
    """
    # Check if connected
    transport = ctx.obj.get('transport')
    if not transport:
        click.echo("Not connected. Use 'connect' command to connect first.")
        return
    
    # Start the interactive shell
    shell = AirbrushShell(ctx)
    shell.cmdloop()
