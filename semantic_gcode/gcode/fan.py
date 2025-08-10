"""
Fan control G-code instructions.

This module provides semantic instruction classes for fan control G-code commands,
such as setting fan speed and turning fans off.
"""
import re
from typing import Optional, ClassVar, List, Dict, Any

from .base import GInstruction, register_instruction


@register_instruction
class SetFanSpeed(GInstruction):
    """
    Set fan speed.
    
    Example G-code: M106 S255 (set fan to full speed)
    Example G-code: M106 P1 S128 (set fan 1 to half speed)
    """
    code = "M106"
    accepted_args = ["S", "P", "I"]  # S is speed (0-255), P is fan number, I is invert (0/1)
    
    def __init__(self, S: float = 255, P: int = 0, I: Optional[int] = None):
        """
        Initialize a fan speed setting instruction.
        
        Args:
            S: The fan speed (0-255, default: 255)
            P: The fan number (default: 0)
            I: Invert the fan speed (0/1, default: None)
        """
        args = {"S": S, "P": P}
        if I is not None:
            args["I"] = I
        super().__init__(**args)
    
    def to_gcode(self) -> str:
        """
        Convert to G-code string.
        
        Returns:
            str: G-code representation (e.g., "M106 S255")
        """
        parts = ["M106"]
        
        # Add fan number if not the default
        if self.args["P"] != 0:
            parts.append(f"P{self.args['P']}")
        
        # Add speed
        parts.append(f"S{self.args['S']}")
        
        # Add invert if specified
        if "I" in self.args:
            parts.append(f"I{self.args['I']}")
        
        return " ".join(parts)
    
    @classmethod
    def from_gcode(cls, line: str) -> Optional['SetFanSpeed']:
        """
        Parse a G-code string into a SetFanSpeed instruction.
        
        Args:
            line: The G-code string to parse
            
        Returns:
            SetFanSpeed: An instance of SetFanSpeed, or None if the line doesn't match
        """
        # Check if this is an M106 command
        if not line.strip().startswith("M106"):
            return None
        
        # Extract parameters
        params: Dict[str, Any] = {}
        parts = line.strip().split()
        
        for part in parts[1:]:  # Skip the M106 part
            if part[0] in cls.accepted_args:
                try:
                    params[part[0]] = float(part[1:])
                except ValueError:
                    continue
        
        # Set default values if not specified
        if "S" not in params:
            params["S"] = 255
        if "P" not in params:
            params["P"] = 0
        
        # Convert P to int
        params["P"] = int(params["P"])
        
        # Convert I to int if present
        if "I" in params:
            params["I"] = int(params["I"])
        
        return cls(**params)
    
    def describe(self) -> str:
        """
        Provide a human-readable description.
        
        Returns:
            str: Description of the instruction
        """
        fan_str = f"fan {self.args['P']}" if self.args["P"] != 0 else "fan"
        speed_percent = round(self.args["S"] / 255 * 100)
        invert_str = " (inverted)" if self.args.get("I", 0) == 1 else ""
        return f"Set {fan_str} to {speed_percent}% speed{invert_str}"


@register_instruction
class FanOff(GInstruction):
    """
    Turn fan off.
    
    Example G-code: M107 (turn fan off)
    Example G-code: M107 P1 (turn fan 1 off)
    """
    code = "M107"
    accepted_args = ["P"]  # P is fan number
    
    def __init__(self, P: int = 0):
        """
        Initialize a fan off instruction.
        
        Args:
            P: The fan number (default: 0)
        """
        super().__init__(P=P)
    
    def to_gcode(self) -> str:
        """
        Convert to G-code string.
        
        Returns:
            str: G-code representation (e.g., "M107")
        """
        return f"M107" + (f" P{self.args['P']}" if self.args["P"] != 0 else "")
    
    @classmethod
    def from_gcode(cls, line: str) -> Optional['FanOff']:
        """
        Parse a G-code string into a FanOff instruction.
        
        Args:
            line: The G-code string to parse
            
        Returns:
            FanOff: An instance of FanOff, or None if the line doesn't match
        """
        # Check if this is an M107 command
        line = line.strip()
        if not line.startswith("M107"):
            return None
        
        # Default fan number
        fan_number = 0
        
        # Check for fan number parameter
        match = re.search(r'P(\d+)', line)
        if match:
            fan_number = int(match.group(1))
        
        return cls(P=fan_number)
    
    def describe(self) -> str:
        """
        Provide a human-readable description.
        
        Returns:
            str: Description of the instruction
        """
        fan_str = f"fan {self.args['P']}" if self.args["P"] != 0 else "fan"
        return f"Turn {fan_str} off"
