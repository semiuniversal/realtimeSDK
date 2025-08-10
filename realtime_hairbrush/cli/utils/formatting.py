"""
Formatting utilities for the Realtime Hairbrush SDK CLI.

This module provides utilities for formatting CLI output.
"""

import click
import json
from typing import Dict, Any, List, Optional


def format_table(headers: List[str], rows: List[List[str]], padding: int = 2) -> str:
    """
    Format data as a table.
    
    Args:
        headers: List of column headers
        rows: List of rows, each row is a list of strings
        padding: Padding between columns
        
    Returns:
        str: Formatted table
    """
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Format header
    header = " " * padding
    for i, h in enumerate(headers):
        header += h.ljust(col_widths[i] + padding)
    
    # Format separator
    separator = " " * padding
    for i, w in enumerate(col_widths):
        separator += "-" * w + " " * padding
    
    # Format rows
    formatted_rows = []
    for row in rows:
        formatted_row = " " * padding
        for i, cell in enumerate(row):
            if i < len(col_widths):
                formatted_row += str(cell).ljust(col_widths[i] + padding)
        formatted_rows.append(formatted_row)
    
    # Combine all parts
    return "\n".join([header, separator] + formatted_rows)


def format_json(data: Dict[str, Any], indent: int = 2) -> str:
    """
    Format data as JSON.
    
    Args:
        data: Data to format
        indent: Indentation level
        
    Returns:
        str: Formatted JSON
    """
    return json.dumps(data, indent=indent)


def format_status(status: Dict[str, Any]) -> str:
    """
    Format status information.
    
    Args:
        status: Status dictionary
        
    Returns:
        str: Formatted status
    """
    # Extract key status information
    connected = status.get("connected", False)
    error = status.get("error")
    
    if not connected:
        return f"Status: Not connected\nError: {error}" if error else "Status: Not connected"
    
    # Format connected status
    lines = ["Status: Connected"]
    
    # Add other status information
    for key, value in status.items():
        if key not in ["connected", "error"]:
            lines.append(f"{key}: {value}")
    
    return "\n".join(lines)


def format_error(message: str) -> str:
    """
    Format an error message.
    
    Args:
        message: Error message
        
    Returns:
        str: Formatted error message
    """
    return f"Error: {message}"


def print_success(message: str) -> None:
    """
    Print a success message.
    
    Args:
        message: Success message
    """
    click.echo(click.style(message, fg="green"))


def print_error(message: str) -> None:
    """
    Print an error message.
    
    Args:
        message: Error message
    """
    click.echo(click.style(f"Error: {message}", fg="red"))


def print_warning(message: str) -> None:
    """
    Print a warning message.
    
    Args:
        message: Warning message
    """
    click.echo(click.style(f"Warning: {message}", fg="yellow"))


def print_info(message: str) -> None:
    """
    Print an info message.
    
    Args:
        message: Info message
    """
    click.echo(click.style(message, fg="blue"))


def print_status(status: Dict[str, Any]) -> None:
    """
    Print status information.
    
    Args:
        status: Status dictionary
    """
    connected = status.get("connected", False)
    error = status.get("error")
    
    if not connected:
        if error:
            print_error(f"Not connected: {error}")
        else:
            print_error("Not connected")
        return
    
    print_success("Connected")
    
    # Print other status information
    for key, value in status.items():
        if key not in ["connected", "error"]:
            click.echo(f"{key}: {value}")
