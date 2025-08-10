"""
Motion-related G-code instructions.
"""
from typing import Optional, ClassVar, List, Dict, Any
import re

from .base import GInstruction, register_instruction


@register_instruction
class MoveTo(GInstruction):
    """
    G1: Linear move with specified feed rate.
    """
    code: ClassVar[str] = "G1"
    accepted_args: ClassVar[List[str]] = ["X", "Y", "Z", "E", "F"]
    
    def to_gcode(self) -> str:
        """Convert to G-code string."""
        parts = [self.code]
        
        for arg, value in self.args.items():
            parts.append(f"{arg}{value}")
        
        return " ".join(parts)
    
    @classmethod
    def from_gcode(cls, line: str) -> Optional['MoveTo']:
        """Create from G-code string."""
        if not line.strip().startswith(cls.code):
            return None
        
        args = {}
        pattern = r'([A-Z])(-?\d*\.?\d+)'
        matches = re.findall(pattern, line)
        
        for param, value in matches:
            if param in cls.accepted_args:
                args[param] = float(value)
        
        return cls(**args)
    
    def describe(self) -> str:
        """Human-readable description."""
        desc = "Move to"
        
        for axis in ["X", "Y", "Z", "E"]:
            if axis in self.args:
                desc += f" {axis}={self.args[axis]}"
        
        if "F" in self.args:
            desc += f" at speed F={self.args['F']}"
        
        return desc
    
    def apply_to_state(self, state_manager) -> None:
        """Apply this instruction to the state manager."""
        # Update feed rate if specified
        if "F" in self.args:
            state_manager.motion.feed_rate = self.args["F"]
        
        # Update position based on positioning mode
        position = state_manager.motion.position
        
        if state_manager.motion.positioning_mode == "absolute":
            # Absolute positioning
            if "X" in self.args:
                position.x = self.args["X"]
            if "Y" in self.args:
                position.y = self.args["Y"]
            if "Z" in self.args:
                position.z = self.args["Z"]
        else:
            # Relative positioning
            if "X" in self.args:
                position.x += self.args["X"]
            if "Y" in self.args:
                position.y += self.args["Y"]
            if "Z" in self.args:
                position.z += self.args["Z"]
        
        # Handle extruder movement based on extruder mode
        if "E" in self.args:
            if position.e is None:
                position.e = 0.0
                
            if state_manager.tool.extruder_mode == "absolute":
                position.e = self.args["E"]
            else:
                position.e += self.args["E"]


@register_instruction
class RapidMove(GInstruction):
    """
    G0: Rapid move (maximum speed).
    """
    code: ClassVar[str] = "G0"
    accepted_args: ClassVar[List[str]] = ["X", "Y", "Z", "E", "F"]
    
    def to_gcode(self) -> str:
        """Convert to G-code string."""
        parts = [self.code]
        
        for arg, value in self.args.items():
            parts.append(f"{arg}{value}")
        
        return " ".join(parts)
    
    @classmethod
    def from_gcode(cls, line: str) -> Optional['RapidMove']:
        """Create from G-code string."""
        if not line.strip().startswith(cls.code):
            return None
        
        args = {}
        pattern = r'([A-Z])(-?\d*\.?\d+)'
        matches = re.findall(pattern, line)
        
        for param, value in matches:
            if param in cls.accepted_args:
                args[param] = float(value)
        
        return cls(**args)
    
    def describe(self) -> str:
        """Human-readable description."""
        desc = "Rapid move to"
        
        for axis in ["X", "Y", "Z", "E"]:
            if axis in self.args:
                desc += f" {axis}={self.args[axis]}"
        
        if "F" in self.args:
            desc += f" at speed F={self.args['F']}"
        
        return desc
    
    def apply_to_state(self, state_manager) -> None:
        """Apply this instruction to the state manager."""
        # G0 behaves the same as G1 for state tracking purposes
        # Update feed rate if specified
        if "F" in self.args:
            state_manager.motion.feed_rate = self.args["F"]
        
        # Update position based on positioning mode
        position = state_manager.motion.position
        
        if state_manager.motion.positioning_mode == "absolute":
            # Absolute positioning
            if "X" in self.args:
                position.x = self.args["X"]
            if "Y" in self.args:
                position.y = self.args["Y"]
            if "Z" in self.args:
                position.z = self.args["Z"]
        else:
            # Relative positioning
            if "X" in self.args:
                position.x += self.args["X"]
            if "Y" in self.args:
                position.y += self.args["Y"]
            if "Z" in self.args:
                position.z += self.args["Z"]
        
        # Handle extruder movement based on extruder mode
        if "E" in self.args:
            if position.e is None:
                position.e = 0.0
                
            if state_manager.tool.extruder_mode == "absolute":
                position.e = self.args["E"]
            else:
                position.e += self.args["E"]


@register_instruction
class ArcMove(GInstruction):
    """
    G2/G3: Arc move (clockwise/counterclockwise).
    """
    code: ClassVar[str] = "G2"  # Default to clockwise, subclass for G3
    accepted_args: ClassVar[List[str]] = ["X", "Y", "Z", "I", "J", "K", "R", "F"]
    
    def to_gcode(self) -> str:
        """Convert to G-code string."""
        parts = [self.code]
        
        for arg, value in self.args.items():
            parts.append(f"{arg}{value}")
        
        return " ".join(parts)
    
    @classmethod
    def from_gcode(cls, line: str) -> Optional['ArcMove']:
        """Create from G-code string."""
        if not line.strip().startswith(cls.code):
            return None
        
        args = {}
        pattern = r'([A-Z])(-?\d*\.?\d+)'
        matches = re.findall(pattern, line)
        
        for param, value in matches:
            if param in cls.accepted_args:
                args[param] = float(value)
        
        return cls(**args)
    
    def describe(self) -> str:
        """Human-readable description."""
        direction = "clockwise" if self.code == "G2" else "counterclockwise"
        desc = f"Arc move {direction} to"
        
        for axis in ["X", "Y", "Z"]:
            if axis in self.args:
                desc += f" {axis}={self.args[axis]}"
        
        return desc
    
    def apply_to_state(self, state_manager) -> None:
        """Apply this instruction to the state manager."""
        # Update feed rate if specified
        if "F" in self.args:
            state_manager.motion.feed_rate = self.args["F"]
        
        # For state tracking purposes, we only care about the end position
        # The arc itself is not represented in the state
        position = state_manager.motion.position
        
        if state_manager.motion.positioning_mode == "absolute":
            # Absolute positioning
            if "X" in self.args:
                position.x = self.args["X"]
            if "Y" in self.args:
                position.y = self.args["Y"]
            if "Z" in self.args:
                position.z = self.args["Z"]
        else:
            # Relative positioning
            if "X" in self.args:
                position.x += self.args["X"]
            if "Y" in self.args:
                position.y += self.args["Y"]
            if "Z" in self.args:
                position.z += self.args["Z"]
        
        # Handle extruder movement based on extruder mode
        if "E" in self.args:
            if position.e is None:
                position.e = 0.0
                
            if state_manager.tool.extruder_mode == "absolute":
                position.e = self.args["E"]
            else:
                position.e += self.args["E"]


@register_instruction
class ArcMoveCounterclockwise(ArcMove):
    """
    G3: Arc move counterclockwise.
    """
    code: ClassVar[str] = "G3"


@register_instruction
class Dwell(GInstruction):
    """
    G4: Dwell (pause) for a specified amount of time.
    """
    code: ClassVar[str] = "G4"
    accepted_args: ClassVar[List[str]] = ["P", "S"]
    
    def to_gcode(self) -> str:
        """Convert to G-code string."""
        parts = [self.code]
        
        for arg, value in self.args.items():
            parts.append(f"{arg}{value}")
        
        return " ".join(parts)
    
    @classmethod
    def from_gcode(cls, line: str) -> Optional['Dwell']:
        """Create from G-code string."""
        if not line.strip().startswith(cls.code):
            return None
        
        args = {}
        pattern = r'([PS])(\d*\.?\d+)'
        matches = re.findall(pattern, line)
        
        for param, value in matches:
            if param in cls.accepted_args:
                args[param] = float(value)
        
        return cls(**args)
    
    def describe(self) -> str:
        """Human-readable description."""
        if "P" in self.args:
            return f"Dwell for {self.args['P']} milliseconds"
        elif "S" in self.args:
            return f"Dwell for {self.args['S']} seconds"
        else:
            return "Dwell (pause)"
    
    def apply_to_state(self, state_manager) -> None:
        """Apply this instruction to the state manager."""
        # Dwell doesn't change the state, it just pauses execution
        pass
