"""
System-related G-code instructions.

This module provides semantic instruction classes for system-related G-code commands,
such as emergency stop and firmware information.
"""
import re
from typing import Optional, ClassVar, List, Dict, Any

from .base import GInstruction, register_instruction


@register_instruction
class EmergencyStop(GInstruction):
    """
    Emergency stop.
    
    Example G-code: M112 (emergency stop)
    """
    code = "M112"
    accepted_args: List[str] = []  # No parameters
    
    def to_gcode(self) -> str:
        """
        Convert to G-code string.
        
        Returns:
            str: G-code representation (e.g., "M112")
        """
        return "M112"
    
    @classmethod
    def from_gcode(cls, line: str) -> Optional['EmergencyStop']:
        """
        Parse a G-code string into an EmergencyStop instruction.
        
        Args:
            line: The G-code string to parse
            
        Returns:
            EmergencyStop: An instance, or None if the line doesn't match
        """
        # Check if this is an M112 command
        if line.strip() == "M112":
            return cls()
        return None
    
    def describe(self) -> str:
        """
        Provide a human-readable description.
        
        Returns:
            str: Description of the instruction
        """
        return "Emergency stop"


@register_instruction
class GetFirmwareVersion(GInstruction):
    """
    Request firmware information.
    
    Example G-code: M115 (get firmware version)
    """
    code = "M115"
    accepted_args: List[str] = []  # No parameters
    
    def to_gcode(self) -> str:
        """
        Convert to G-code string.
        
        Returns:
            str: G-code representation (e.g., "M115")
        """
        return "M115"
    
    @classmethod
    def from_gcode(cls, line: str) -> Optional['GetFirmwareVersion']:
        """
        Parse a G-code string into a GetFirmwareVersion instruction.
        
        Args:
            line: The G-code string to parse
            
        Returns:
            GetFirmwareVersion: An instance, or None if the line doesn't match
        """
        # Check if this is an M115 command
        if line.strip() == "M115":
            return cls()
        return None
    
    def describe(self) -> str:
        """
        Provide a human-readable description.
        
        Returns:
            str: Description of the instruction
        """
        return "Request firmware version information"


@register_instruction
class DisplayMessage(GInstruction):
    """
    Display a message on the printer's screen.
    
    Example G-code: M117 Hello World (display "Hello World" on the screen)
    """
    code = "M117"
    accepted_args = ["message"]  # Special case: message is everything after M117
    
    def __init__(self, message: str = ""):
        """
        Initialize a display message instruction.
        
        Args:
            message: The message to display
        """
        super().__init__(message=message)
    
    def to_gcode(self) -> str:
        """
        Convert to G-code string.
        
        Returns:
            str: G-code representation (e.g., "M117 Hello World")
        """
        return f"M117 {self.args['message']}"
    
    @classmethod
    def from_gcode(cls, line: str) -> Optional['DisplayMessage']:
        """
        Parse a G-code string into a DisplayMessage instruction.
        
        Args:
            line: The G-code string to parse
            
        Returns:
            DisplayMessage: An instance, or None if the line doesn't match
        """
        # Check if this is an M117 command
        if not line.strip().startswith("M117"):
            return None
        
        # Extract the message (everything after M117)
        parts = line.strip().split(maxsplit=1)
        message = parts[1] if len(parts) > 1 else ""
        
        return cls(message=message)
    
    def describe(self) -> str:
        """
        Provide a human-readable description.
        
        Returns:
            str: Description of the instruction
        """
        if self.args['message']:
            return f"Display message: \"{self.args['message']}\""
        else:
            return "Clear display message"


@register_instruction
class SendMessage(GInstruction):
    """
    Send a message to the host.
    
    Example G-code: M118 P0 Hello Host (send "Hello Host" to the host)
    """
    code = "M118"
    accepted_args = ["P", "message"]  # P is destination, message is everything after P parameter
    
    def __init__(self, message: str, P: int = 0):
        """
        Initialize a send message instruction.
        
        Args:
            message: The message to send
            P: The destination (0=USB, 1=LCD, 2=both, default: 0)
        """
        super().__init__(message=message, P=P)
    
    def to_gcode(self) -> str:
        """
        Convert to G-code string.
        
        Returns:
            str: G-code representation (e.g., "M118 P0 Hello Host")
        """
        return f"M118 P{self.args['P']} {self.args['message']}"
    
    @classmethod
    def from_gcode(cls, line: str) -> Optional['SendMessage']:
        """
        Parse a G-code string into a SendMessage instruction.
        
        Args:
            line: The G-code string to parse
            
        Returns:
            SendMessage: An instance, or None if the line doesn't match
        """
        # Check if this is an M118 command
        if not line.strip().startswith("M118"):
            return None
        
        # Default destination
        destination = 0
        
        # Extract the P parameter if present
        match = re.search(r'P(\d+)', line)
        if match:
            destination = int(match.group(1))
            # Remove the P parameter from the line
            line = re.sub(r'P\d+', '', line)
        
        # Extract the message (everything after M118 and optional P parameter)
        parts = line.strip().split(maxsplit=1)
        message = parts[1] if len(parts) > 1 else ""
        
        return cls(message=message, P=destination)
    
    def describe(self) -> str:
        """
        Provide a human-readable description.
        
        Returns:
            str: Description of the instruction
        """
        destinations = {0: "USB", 1: "LCD", 2: "USB and LCD"}
        destination_str = destinations.get(self.args['P'], f"destination {self.args['P']}")
        return f"Send message to {destination_str}: \"{self.args['message']}\""
