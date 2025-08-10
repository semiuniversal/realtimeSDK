"""
Command parser utilities for the Realtime Hairbrush SDK.

This module provides functions for parsing the commands.yaml file and creating
completers for the interactive shell.
"""

import os
import yaml
from typing import Dict, Any, Optional, List, Union
from prompt_toolkit.completion import NestedCompleter


def parse_commands_yaml(yaml_path: str) -> Dict[str, Any]:
    """
    Parse commands.yaml into a structured format for auto-completion.
    
    Args:
        yaml_path: Path to the commands.yaml file
        
    Returns:
        Dict containing the parsed command structure
    """
    if not os.path.exists(yaml_path):
        return {}
    
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    
    commands = {}
    
    # Handle both list-style and dict-style formats
    if isinstance(data.get('commands', []), list):
        # Current format (list of dicts)
        for cmd in data['commands']:
            cmd_name = list(cmd.keys())[0]
            cmd_def = cmd[cmd_name]
            commands[cmd_name] = cmd_def
    else:
        # New format (direct dict)
        commands = data.get('commands', {})
    
    return commands


class CommandParameterCompleter:
    """Factory for creating a nested completer from commands.yaml"""
    
    @classmethod
    def create_completer(cls, yaml_path: str) -> NestedCompleter:
        """
        Create a NestedCompleter from commands.yaml
        
        Args:
            yaml_path: Path to the commands.yaml file
            
        Returns:
            NestedCompleter configured with commands and parameters
        """
        from prompt_toolkit.completion import NestedCompleter
        
        commands = parse_commands_yaml(yaml_path)
        completer_dict = cls._build_completer_dict(commands)
        
        return NestedCompleter.from_nested_dict(completer_dict)
    
    @classmethod
    def _build_completer_dict(cls, commands: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build the nested completer dictionary structure
        
        Args:
            commands: Parsed command definitions
            
        Returns:
            Dictionary structure for NestedCompleter
        """
        result = {}
        
        for cmd_name, cmd_def in commands.items():
            # Build parameter completions for this command
            param_dict = {}
            
            # Handle different parameter formats
            params = cmd_def.get('params', [])
            if isinstance(params, list):
                # List-style params
                for param in params:
                    if isinstance(param, dict):
                        # New format with named keys
                        for param_name, param_def in param.items():
                            param_dict[param_name] = cls._build_param_completions(param_def)
                    else:
                        # Legacy format with single name
                        param_name = param
                        param_dict[param_name] = None
            elif isinstance(params, dict):
                # Dict-style params
                for param_name, param_def in params.items():
                    param_dict[param_name] = cls._build_param_completions(param_def)
            
            result[cmd_name] = param_dict
        
        return result
    
    @classmethod
    def _build_param_completions(cls, param_def: Optional[Dict[str, Any]]) -> Optional[Dict[str, None]]:
        """
        Build completions for parameter values
        
        Args:
            param_def: Parameter definition from YAML
            
        Returns:
            Dictionary of accepted values or None
        """
        if not param_def or not isinstance(param_def, dict):
            return None
            
        accepts = param_def.get('accepts', [])
        if not accepts:
            return None
            
        # Create completions for accepted values
        return {str(val): None for val in accepts}


def parse_command_args(command: str, arg_string: str, command_def: Dict[str, Any]) -> tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Parse and validate command arguments based on YAML definition.
    
    Args:
        command: Command name
        arg_string: Argument string to parse
        command_def: Command definition from YAML
        
    Returns:
        Tuple of (args_dict, error_message)
        If parsing succeeds, error_message is None
        If parsing fails, args_dict is None and error_message contains the error
    """
    args = {}
    parts = arg_string.split()
    
    # Get parameter definitions
    params = command_def.get('params', {})
    if isinstance(params, list):
        # Convert list-style params to dict for easier lookup
        param_dict = {}
        for param in params:
            if isinstance(param, dict):
                for param_name, param_def in param.items():
                    param_dict[param_name] = param_def
            else:
                param_dict[param] = {}
        params = param_dict
    
    # Track position for positional parameters
    i = 0
    
    while i < len(parts):
        part = parts[i]
        
        # Check if this is a named parameter
        if part in params:
            param_name = part
            param_def = params[param_name]
            
            # Check if there's a value following this parameter name
            if i + 1 < len(parts):
                value = parts[i + 1]
                
                # Validate against accepts list if present
                accepts = param_def.get('accepts', [])
                if accepts and value not in [str(a) for a in accepts]:
                    return None, f"Invalid value for {param_name}: {value}. Accepted values: {', '.join(str(a) for a in accepts)}"
                
                args[param_name] = value
                i += 2  # Skip the parameter name and value
            else:
                # Parameter with no value
                args[param_name] = True
                i += 1
        else:
            # Positional parameter - find the next undefined required parameter
            found = False
            for param_name, param_def in params.items():
                if param_name not in args and not param_def.get('optional', False):
                    args[param_name] = part
                    found = True
                    break
            
            if not found:
                # No required parameter found, try optional ones
                for param_name, param_def in params.items():
                    if param_name not in args and param_def.get('optional', True):
                        args[param_name] = part
                        found = True
                        break
            
            if not found:
                return None, f"Unexpected argument: {part}"
            
            i += 1
    
    # Check for missing required parameters
    for param_name, param_def in params.items():
        if not param_def.get('optional', True) and param_name not in args:
            return None, f"Missing required parameter: {param_name}"
    
    return args, None 