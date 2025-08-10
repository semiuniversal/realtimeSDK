"""
State domain classes for the Semantic G-code SDK.

This module defines the various state domains that are tracked by the state management system.
Each domain represents a specific aspect of machine state (motion, tool, temperature, etc.).
"""
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Position:
    """
    Represents a position in 3D space with optional extruder position.
    """
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    e: Optional[float] = None
    
    def serialize(self) -> Dict[str, float]:
        """Convert position to dictionary."""
        result = {'x': self.x, 'y': self.y, 'z': self.z}
        if self.e is not None:
            result['e'] = self.e
        return result
    
    @classmethod
    def deserialize(cls, data: Dict[str, float]) -> 'Position':
        """Create position from dictionary."""
        return cls(
            x=data.get('x', 0.0),
            y=data.get('y', 0.0),
            z=data.get('z', 0.0),
            e=data.get('e')
        )


class StateDomain:
    """
    Base class for all state domains.
    
    A state domain represents a specific aspect of machine state, such as motion,
    tool settings, temperature, etc.
    """
    
    def serialize(self) -> Dict[str, Any]:
        """
        Serialize domain state to a dictionary.
        
        Returns:
            Dict[str, Any]: Serialized state data
        """
        raise NotImplementedError("Subclasses must implement serialize()")
    
    def deserialize(self, data: Dict[str, Any]) -> None:
        """
        Restore domain state from a dictionary.
        
        Args:
            data: Serialized state data
        """
        raise NotImplementedError("Subclasses must implement deserialize()")
    
    def reset(self) -> None:
        """
        Reset domain to default state.
        """
        raise NotImplementedError("Subclasses must implement reset()")
    
    def validate(self, instruction: Any) -> bool:
        """
        Validate if an instruction can be executed in the current state.
        
        Args:
            instruction: The instruction to validate
            
        Returns:
            bool: True if the instruction can be executed, False otherwise
        """
        # Default implementation allows all instructions
        return True


class MotionState(StateDomain):
    """
    Represents motion-related state (positioning mode, units, position, etc.).
    """
    
    def __init__(self):
        """Initialize with default values."""
        self.positioning_mode: str = "absolute"  # "absolute" or "relative"
        self.units: str = "mm"  # "mm" or "inch"
        self.position: Position = Position()
        self.feed_rate: float = 0.0
        self.active_plane: str = "XY"  # "XY", "XZ", or "YZ" for arc movements
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize motion state to dictionary."""
        return {
            'positioning_mode': self.positioning_mode,
            'units': self.units,
            'position': self.position.serialize(),
            'feed_rate': self.feed_rate,
            'active_plane': self.active_plane
        }
    
    def deserialize(self, data: Dict[str, Any]) -> None:
        """Restore motion state from dictionary."""
        self.positioning_mode = data.get('positioning_mode', "absolute")
        self.units = data.get('units', "mm")
        pos_data = data.get('position', {})
        self.position = Position.deserialize(pos_data)
        self.feed_rate = data.get('feed_rate', 0.0)
        self.active_plane = data.get('active_plane', "XY")
    
    def reset(self) -> None:
        """Reset motion state to defaults."""
        self.__init__()
    
    def validate(self, instruction: Any) -> bool:
        """
        Validate motion-related instructions.
        
        Args:
            instruction: The instruction to validate
            
        Returns:
            bool: True if the instruction can be executed, False otherwise
        """
        # This will be expanded with actual validation logic
        return True


class ToolState(StateDomain):
    """
    Represents tool-related state (selected tool, extruder mode, etc.).
    """
    
    def __init__(self):
        """Initialize with default values."""
        self.selected_tool: int = 0
        self.extruder_mode: str = "relative"  # "absolute" or "relative"
        self.tool_offsets: Dict[int, Position] = {}  # Tool number -> offset
        self.defined_tools: List[int] = [0]  # List of defined tool numbers
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize tool state to dictionary."""
        return {
            'selected_tool': self.selected_tool,
            'extruder_mode': self.extruder_mode,
            'tool_offsets': {
                str(tool): offset.serialize() 
                for tool, offset in self.tool_offsets.items()
            },
            'defined_tools': self.defined_tools
        }
    
    def deserialize(self, data: Dict[str, Any]) -> None:
        """Restore tool state from dictionary."""
        self.selected_tool = data.get('selected_tool', 0)
        self.extruder_mode = data.get('extruder_mode', "relative")
        
        self.tool_offsets = {}
        offsets_data = data.get('tool_offsets', {})
        for tool_str, offset_data in offsets_data.items():
            tool = int(tool_str)
            self.tool_offsets[tool] = Position.deserialize(offset_data)
        
        self.defined_tools = data.get('defined_tools', [0])
    
    def reset(self) -> None:
        """Reset tool state to defaults."""
        self.__init__()
    
    def validate(self, instruction: Any) -> bool:
        """
        Validate tool-related instructions.
        
        Args:
            instruction: The instruction to validate
            
        Returns:
            bool: True if the instruction can be executed, False otherwise
        """
        # This will be expanded with actual validation logic
        return True


class TemperatureState(StateDomain):
    """
    Represents temperature-related state (heater targets, current temps, etc.).
    """
    
    def __init__(self):
        """Initialize with default values."""
        self.tool_temps: Dict[int, float] = {}  # Tool number -> current temp
        self.tool_targets: Dict[int, float] = {}  # Tool number -> target temp
        self.bed_temp: float = 0.0
        self.bed_target: float = 0.0
        self.chamber_temp: Optional[float] = None
        self.chamber_target: Optional[float] = None
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize temperature state to dictionary."""
        result = {
            'tool_temps': self.tool_temps,
            'tool_targets': self.tool_targets,
            'bed_temp': self.bed_temp,
            'bed_target': self.bed_target
        }
        
        if self.chamber_temp is not None:
            result['chamber_temp'] = self.chamber_temp
        if self.chamber_target is not None:
            result['chamber_target'] = self.chamber_target
            
        return result
    
    def deserialize(self, data: Dict[str, Any]) -> None:
        """Restore temperature state from dictionary."""
        self.tool_temps = {
            int(tool): float(temp) 
            for tool, temp in data.get('tool_temps', {}).items()
        }
        self.tool_targets = {
            int(tool): float(target) 
            for tool, target in data.get('tool_targets', {}).items()
        }
        self.bed_temp = data.get('bed_temp', 0.0)
        self.bed_target = data.get('bed_target', 0.0)
        self.chamber_temp = data.get('chamber_temp')
        self.chamber_target = data.get('chamber_target')
    
    def reset(self) -> None:
        """Reset temperature state to defaults."""
        self.__init__()
    
    def validate(self, instruction: Any) -> bool:
        """
        Validate temperature-related instructions.
        
        Args:
            instruction: The instruction to validate
            
        Returns:
            bool: True if the instruction can be executed, False otherwise
        """
        # This will be expanded with actual validation logic
        return True


class CoordinateState(StateDomain):
    """
    Represents coordinate system state (work offsets, etc.).
    """
    
    def __init__(self):
        """Initialize with default values."""
        # G54-G59 coordinate systems (work offsets)
        self.work_offsets: Dict[str, Position] = {
            'G54': Position(),
            'G55': Position(),
            'G56': Position(),
            'G57': Position(),
            'G58': Position(),
            'G59': Position()
        }
        self.active_coordinate_system: str = 'G54'
        self.machine_position: Position = Position()  # Absolute machine position
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize coordinate state to dictionary."""
        return {
            'work_offsets': {
                cs: offset.serialize() 
                for cs, offset in self.work_offsets.items()
            },
            'active_coordinate_system': self.active_coordinate_system,
            'machine_position': self.machine_position.serialize()
        }
    
    def deserialize(self, data: Dict[str, Any]) -> None:
        """Restore coordinate state from dictionary."""
        offsets_data = data.get('work_offsets', {})
        self.work_offsets = {}
        for cs, offset_data in offsets_data.items():
            self.work_offsets[cs] = Position.deserialize(offset_data)
        
        self.active_coordinate_system = data.get('active_coordinate_system', 'G54')
        
        machine_pos_data = data.get('machine_position', {})
        self.machine_position = Position.deserialize(machine_pos_data)
    
    def reset(self) -> None:
        """Reset coordinate state to defaults."""
        self.__init__()
    
    def validate(self, instruction: Any) -> bool:
        """
        Validate coordinate-related instructions.
        
        Args:
            instruction: The instruction to validate
            
        Returns:
            bool: True if the instruction can be executed, False otherwise
        """
        # This will be expanded with actual validation logic
        return True


class IOState(StateDomain):
    """
    Represents I/O state (fans, inputs, outputs, etc.).
    """
    
    def __init__(self):
        """Initialize with default values."""
        self.fan_speeds: Dict[int, float] = {0: 0.0}  # Fan number -> speed (0-1)
        self.outputs: Dict[int, bool] = {}  # Output pin -> state
        self.inputs: Dict[int, bool] = {}  # Input pin -> state
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize I/O state to dictionary."""
        return {
            'fan_speeds': self.fan_speeds,
            'outputs': self.outputs,
            'inputs': self.inputs
        }
    
    def deserialize(self, data: Dict[str, Any]) -> None:
        """Restore I/O state from dictionary."""
        self.fan_speeds = {
            int(fan): float(speed) 
            for fan, speed in data.get('fan_speeds', {0: 0.0}).items()
        }
        self.outputs = {
            int(pin): bool(state) 
            for pin, state in data.get('outputs', {}).items()
        }
        self.inputs = {
            int(pin): bool(state) 
            for pin, state in data.get('inputs', {}).items()
        }
    
    def reset(self) -> None:
        """Reset I/O state to defaults."""
        self.__init__()
    
    def validate(self, instruction: Any) -> bool:
        """
        Validate I/O-related instructions.
        
        Args:
            instruction: The instruction to validate
            
        Returns:
            bool: True if the instruction can be executed, False otherwise
        """
        # This will be expanded with actual validation logic
        return True
