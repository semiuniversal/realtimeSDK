"""
Tool-related G-code instructions.

This module provides semantic instruction classes for tool-related G-code commands,
such as tool selection and tool offset setting.
"""
import re
from typing import Optional, ClassVar, List, Dict, Any

from ..base import GInstruction, register_instruction
from semantic_gcode.state import StateManager


@register_instruction
class SelectTool(GInstruction):
    """
    Select a tool for use.
    
    Example G-code: T0, T1, etc.
    """
    code = "T"  # Special case: T followed by a number
    accepted_args = ["P"]  # P is the tool number
    
    def __init__(self, P: int):
        """
        Initialize a tool selection instruction.
        
        Args:
            P: The tool number to select
        """
        super().__init__(P=P)
    
    def to_gcode(self) -> str:
        """
        Convert to G-code string.
        
        Returns:
            str: G-code representation (e.g., "T0")
        """
        return f"T{self.args['P']}"
    
    @classmethod
    def from_gcode(cls, line: str) -> Optional['SelectTool']:
        """
        Parse a G-code string into a SelectTool instruction.
        
        Args:
            line: The G-code string to parse
            
        Returns:
            SelectTool: An instance of SelectTool, or None if the line doesn't match
        """
        # Match T followed by a number
        match = re.match(r'^T(\d+)', line.strip())
        if match:
            tool_number = int(match.group(1))
            return cls(P=tool_number)
        return None
    
    def describe(self) -> str:
        """
        Provide a human-readable description.
        
        Returns:
            str: Description of the instruction
        """
        return f"Select tool {self.args['P']}"
    
    def apply_to_state(self, state_manager: StateManager) -> None:
        """Apply this instruction to the state manager."""
        state_manager.tool.active_tool = self.args['P']


@register_instruction
class DefineTool(GInstruction):
    """
    Define tool parameters.
    
    Example G-code: G10 P0 X0 Y0 Z0 (set tool 0 offset)
    """
    code = "G10"
    accepted_args = ["P", "X", "Y", "Z", "R", "S"]
    
    def __init__(self, P: int, **kwargs):
        """
        Initialize a tool definition instruction.
        
        Args:
            P: The tool number to define
            **kwargs: Tool parameters (X, Y, Z for offsets, R for radius, S for standby temp)
        """
        all_args = {"P": P, **kwargs}
        super().__init__(**all_args)
    
    def to_gcode(self) -> str:
        """
        Convert to G-code string.
        
        Returns:
            str: G-code representation (e.g., "G10 P0 X10 Y0 Z0")
        """
        args_str = " ".join(f"{k}{v}" for k, v in self.args.items())
        return f"G10 {args_str}"
    
    @classmethod
    def from_gcode(cls, line: str) -> Optional['DefineTool']:
        """
        Parse a G-code string into a DefineTool instruction.
        
        Args:
            line: The G-code string to parse
            
        Returns:
            DefineTool: An instance of DefineTool, or None if the line doesn't match
        """
        # Check if this is a G10 command
        if not line.strip().startswith("G10"):
            return None
        
        # Extract parameters
        params: Dict[str, Any] = {}
        parts = line.strip().split()
        
        for part in parts[1:]:  # Skip the G10 part
            if part[0] in cls.accepted_args:
                try:
                    params[part[0]] = float(part[1:])
                except ValueError:
                    continue
        
        # G10 requires a P parameter (tool number)
        if "P" not in params:
            return None
        
        # Convert P to int
        params["P"] = int(params["P"])
        
        return cls(**params)
    
    def describe(self) -> str:
        """
        Provide a human-readable description.
        
        Returns:
            str: Description of the instruction
        """
        tool_num = self.args.get("P", 0)
        if "X" in self.args or "Y" in self.args or "Z" in self.args:
            offsets = ", ".join(f"{k}={v}" for k, v in self.args.items() if k in ["X", "Y", "Z"])
            return f"Set tool {tool_num} offsets: {offsets}"
        elif "R" in self.args:
            return f"Set tool {tool_num} radius: {self.args['R']}"
        elif "S" in self.args:
            return f"Set tool {tool_num} standby temperature: {self.args['S']}"
        else:
            return f"Define tool {tool_num} parameters"
    
    def apply_to_state(self, state_manager: StateManager) -> None:
        """Apply this instruction to the state manager."""
        tool_num = self.args.get("P", 0)
        
        # Ensure the tool exists in the state
        if tool_num not in state_manager.tool.tool_offsets:
            state_manager.tool.tool_offsets[tool_num] = {"X": 0.0, "Y": 0.0, "Z": 0.0}
        
        # Update offsets
        for axis in ["X", "Y", "Z"]:
            if axis in self.args:
                state_manager.tool.tool_offsets[tool_num][axis] = self.args[axis]
