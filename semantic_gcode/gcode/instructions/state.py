"""
State-related G-code instructions.

These instructions modify the machine state (positioning mode, units, etc.).
"""
from typing import Optional, ClassVar, List
import re

from ..base import GInstruction, register_instruction
from semantic_gcode.state import StateManager


@register_instruction
class SetAbsolutePositioning(GInstruction):
    """
    G90: Set absolute positioning mode.
    """
    code: ClassVar[str] = "G90"
    accepted_args: ClassVar[List[str]] = []
    
    def to_gcode(self) -> str:
        """Convert to G-code string."""
        return self.code
    
    @classmethod
    def from_gcode(cls, line: str) -> Optional['SetAbsolutePositioning']:
        """Create from G-code string."""
        if line.strip() == cls.code:
            return cls()
        return None
    
    def describe(self) -> str:
        """Human-readable description."""
        return "Set absolute positioning mode"
    
    def apply_to_state(self, state_manager: StateManager) -> None:
        """Apply this instruction to the state manager."""
        state_manager.motion.positioning_mode = "absolute"


@register_instruction
class SetRelativePositioning(GInstruction):
    """
    G91: Set relative positioning mode.
    """
    code: ClassVar[str] = "G91"
    accepted_args: ClassVar[List[str]] = []
    
    def to_gcode(self) -> str:
        """Convert to G-code string."""
        return self.code
    
    @classmethod
    def from_gcode(cls, line: str) -> Optional['SetRelativePositioning']:
        """Create from G-code string."""
        if line.strip() == cls.code:
            return cls()
        return None
    
    def describe(self) -> str:
        """Human-readable description."""
        return "Set relative positioning mode"
    
    def apply_to_state(self, state_manager: StateManager) -> None:
        """Apply this instruction to the state manager."""
        state_manager.motion.positioning_mode = "relative"


@register_instruction
class SetUnitsMM(GInstruction):
    """
    G21: Set units to millimeters.
    """
    code: ClassVar[str] = "G21"
    accepted_args: ClassVar[List[str]] = []
    
    def to_gcode(self) -> str:
        """Convert to G-code string."""
        return self.code
    
    @classmethod
    def from_gcode(cls, line: str) -> Optional['SetUnitsMM']:
        """Create from G-code string."""
        if line.strip() == cls.code:
            return cls()
        return None
    
    def describe(self) -> str:
        """Human-readable description."""
        return "Set units to millimeters"
    
    def apply_to_state(self, state_manager: StateManager) -> None:
        """Apply this instruction to the state manager."""
        state_manager.motion.units = "mm"


@register_instruction
class SetUnitsInch(GInstruction):
    """
    G20: Set units to inches.
    """
    code: ClassVar[str] = "G20"
    accepted_args: ClassVar[List[str]] = []
    
    def to_gcode(self) -> str:
        """Convert to G-code string."""
        return self.code
    
    @classmethod
    def from_gcode(cls, line: str) -> Optional['SetUnitsInch']:
        """Create from G-code string."""
        if line.strip() == cls.code:
            return cls()
        return None
    
    def describe(self) -> str:
        """Human-readable description."""
        return "Set units to inches"
    
    def apply_to_state(self, state_manager: StateManager) -> None:
        """Apply this instruction to the state manager."""
        state_manager.motion.units = "inch"


@register_instruction
class SetPositionOrigin(GInstruction):
    """
    G92: Set current position as origin for specified axes.
    """
    code: ClassVar[str] = "G92"
    accepted_args: ClassVar[List[str]] = ["X", "Y", "Z", "E"]
    
    def to_gcode(self) -> str:
        """Convert to G-code string."""
        parts = [self.code]
        
        for arg, value in self.args.items():
            parts.append(f"{arg}{value}")
        
        return " ".join(parts)
    
    @classmethod
    def from_gcode(cls, line: str) -> Optional['SetPositionOrigin']:
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
        if not self.args:
            return "Set current position as origin for all axes"
        
        desc = "Set current position as origin for axes:"
        for axis, value in self.args.items():
            desc += f" {axis}={value}"
        
        return desc
    
    def apply_to_state(self, state_manager: StateManager) -> None:
        """Apply this instruction to the state manager."""
        # G92 sets the logical position while maintaining the same physical position
        # This effectively sets an offset between logical and machine coordinates
        
        # Update coordinate system offsets based on current position and requested values
        position = state_manager.motion.position
        
        # Get the active coordinate system
        active_cs = state_manager.coordinate.active_coordinate_system
        offset = state_manager.coordinate.work_offsets[active_cs]
        
        # For each specified axis, adjust the offset so that the logical position
        # becomes what was specified in the G92 command
        if "X" in self.args:
            offset.x = position.x - self.args["X"]
        if "Y" in self.args:
            offset.y = position.y - self.args["Y"]
        if "Z" in self.args:
            offset.z = position.z - self.args["Z"]
        if "E" in self.args and position.e is not None:
            offset.e = position.e - self.args["E"]


@register_instruction
class SetAbsoluteExtruderMode(GInstruction):
    """
    M82: Set absolute extruder mode.
    """
    code: ClassVar[str] = "M82"
    accepted_args: ClassVar[List[str]] = []
    
    def to_gcode(self) -> str:
        """Convert to G-code string."""
        return self.code
    
    @classmethod
    def from_gcode(cls, line: str) -> Optional['SetAbsoluteExtruderMode']:
        """Create from G-code string."""
        if line.strip() == cls.code:
            return cls()
        return None
    
    def describe(self) -> str:
        """Human-readable description."""
        return "Set absolute extruder mode"
    
    def apply_to_state(self, state_manager: StateManager) -> None:
        """Apply this instruction to the state manager."""
        state_manager.tool.extruder_mode = "absolute"


@register_instruction
class SetRelativeExtruderMode(GInstruction):
    """
    M83: Set relative extruder mode.
    """
    code: ClassVar[str] = "M83"
    accepted_args: ClassVar[List[str]] = []
    
    def to_gcode(self) -> str:
        """Convert to G-code string."""
        return self.code
    
    @classmethod
    def from_gcode(cls, line: str) -> Optional['SetRelativeExtruderMode']:
        """Create from G-code string."""
        if line.strip() == cls.code:
            return cls()
        return None
    
    def describe(self) -> str:
        """Human-readable description."""
        return "Set relative extruder mode"
    
    def apply_to_state(self, state_manager: StateManager) -> None:
        """Apply this instruction to the state manager."""
        state_manager.tool.extruder_mode = "relative" 