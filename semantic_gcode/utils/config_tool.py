#!/usr/bin/env python3
"""
Command-line utility for machine configuration.

This utility provides a command-line interface for creating and managing
machine configuration alias files.
"""
import os
import sys
import argparse
from pathlib import Path
from typing import Optional, List

from ..config import ConfigParser, ConfigurationInterviewer, AliasSystem


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Machine Configuration Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a new configuration from a config.g file
  config_tool.py create --config /path/to/config.g --output machine_profile.yaml
  
  # Validate an existing configuration file
  config_tool.py validate --config machine_profile.yaml
  
  # Show information about a configuration file
  config_tool.py info --config machine_profile.yaml
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new configuration")
    create_parser.add_argument("--config", "-c", help="Path to config.g file")
    create_parser.add_argument("--output", "-o", default="machine_profile.yaml", help="Output file path")
    create_parser.add_argument("--non-interactive", "-n", action="store_true", help="Non-interactive mode")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate a configuration file")
    validate_parser.add_argument("--config", "-c", required=True, help="Path to configuration file")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show information about a configuration file")
    info_parser.add_argument("--config", "-c", required=True, help="Path to configuration file")
    
    return parser.parse_args()


def create_config(args: argparse.Namespace) -> int:
    """
    Create a new configuration.
    
    Args:
        args: Command-line arguments
        
    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    if args.non_interactive:
        print("Non-interactive mode not implemented yet")
        return 1
    
    interviewer = ConfigurationInterviewer(args.config if args.config else None)
    interviewer.run_interview()
    
    return 0


def validate_config(args: argparse.Namespace) -> int:
    """
    Validate a configuration file.
    
    Args:
        args: Command-line arguments
        
    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    try:
        alias_system = AliasSystem()
        alias_system.load_from_file(args.config)
        
        errors = alias_system.validate()
        if errors:
            print(f"Validation errors in {args.config}:")
            for error in errors:
                print(f"- {error}")
            return 1
        
        print(f"Configuration file {args.config} is valid.")
        return 0
        
    except Exception as e:
        print(f"Error validating configuration: {str(e)}")
        return 1


def show_info(args: argparse.Namespace) -> int:
    """
    Show information about a configuration file.
    
    Args:
        args: Command-line arguments
        
    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    try:
        alias_system = AliasSystem()
        alias_system.load_from_file(args.config)
        
        print(f"Machine: {alias_system.machine_name}")
        print(f"Type: {alias_system.machine_type}")
        
        if alias_system.machine_info:
            print("\nMachine Information:")
            for key, value in alias_system.machine_info.items():
                print(f"  {key}: {value}")
        
        print(f"\nComponents: {len(alias_system.aliases)}")
        hardware_types = set(alias.hardware_type for alias in alias_system.aliases.values())
        for hardware_type in sorted(hardware_types):
            aliases = alias_system.get_aliases_by_hardware_type(hardware_type)
            print(f"  {hardware_type}: {len(aliases)}")
        
        print(f"\nComposite Functions: {len(alias_system.functions)}")
        for name, function in alias_system.functions.items():
            print(f"  {name}: {function.description}")
            print(f"    Operations: {', '.join(function.operations.keys())}")
        
        return 0
        
    except Exception as e:
        print(f"Error reading configuration: {str(e)}")
        return 1


def main() -> int:
    """Main entry point."""
    args = parse_args()
    
    if args.command == "create":
        return create_config(args)
    elif args.command == "validate":
        return validate_config(args)
    elif args.command == "info":
        return show_info(args)
    else:
        print("Please specify a command. Use --help for more information.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 