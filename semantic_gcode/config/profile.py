"""
Machine profile for capability discovery and configuration.

This module provides the MachineProfile class for representing machine capabilities,
limitations, and configuration. It serves as a central reference for machine operations.
"""
from typing import Dict, Any, List, Optional, Union, Set
from dataclasses import dataclass, field
from pathlib import Path
import os
import re

from .alias import AliasSystem
from ..utils.exceptions import ConfigurationError


@dataclass
class AxisConfig:
    """Configuration for a machine axis."""
    name: str
    limits: List[float] = field(default_factory=lambda: [0.0, 0.0])
    steps_per_mm: Optional[float] = None
    max_speed: Optional[float] = None
    max_acceleration: Optional[float] = None
    homing_method: Optional[str] = None
    endstops: Dict[str, bool] = field(default_factory=dict)


@dataclass
class ToolConfig:
    """Configuration for a machine tool."""
    number: int
    name: str = ""
    offsets: Dict[str, float] = field(default_factory=dict)
    extruder: Optional[int] = None
    heater: Optional[int] = None
    fan: Optional[int] = None


@dataclass
class HeaterConfig:
    """Configuration for a machine heater."""
    number: int
    name: str = ""
    max_temp: float = 0.0
    min_temp: float = 0.0


@dataclass
class FanConfig:
    """Configuration for a machine fan."""
    number: int
    name: str = ""
    thermostatic: bool = False
    inverted: bool = False


class MachineProfile:
    """
    Profile representing machine capabilities and configuration.
    
    This class provides a structured representation of a machine's capabilities,
    limitations, and configuration. It serves as a central reference for:
    - Available axes and their ranges
    - Available tools and their capabilities
    - Temperature limits
    - Movement constraints
    - Special features
    """
    
    def __init__(self):
        """Initialize an empty machine profile."""
        self.machine_name: str = "Unknown Machine"
        self.firmware_name: str = "Unknown"
        self.firmware_version: str = "Unknown"
        self.board_type: str = "Unknown"
        
        self.axes: Dict[str, AxisConfig] = {}
        self.tools: Dict[int, ToolConfig] = {}
        self.heaters: Dict[int, HeaterConfig] = {}
        self.fans: Dict[int, FanConfig] = {}
        
        self.kinematics: str = "cartesian"
        self.max_speeds: Dict[str, float] = {}
        self.max_accelerations: Dict[str, float] = {}
        
        self.capabilities: Set[str] = set()
        self.config_settings: Dict[str, Any] = {}
        
        # Alias system for semantic mapping
        self.alias_system: Optional[AliasSystem] = None
    
    def load_alias_system(self, file_path: Union[str, Path]) -> None:
        """
        Load an alias system from a file.
        
        Args:
            file_path: Path to the alias system file
            
        Raises:
            ConfigurationError: If the file cannot be loaded
        """
        self.alias_system = AliasSystem()
        self.alias_system.load_from_file(file_path)
    
    def create_alias_system(self) -> AliasSystem:
        """
        Create a new alias system for this profile.
        
        Returns:
            AliasSystem: A new alias system initialized with profile data
        """
        alias_system = AliasSystem()
        alias_system.machine_name = self.machine_name
        alias_system.machine_type = self.board_type
        alias_system.machine_info = {
            "firmware_name": self.firmware_name,
            "firmware_version": self.firmware_version,
            "kinematics": self.kinematics,
            "capabilities": list(self.capabilities)
        }
        
        return alias_system
    
    def has_capability(self, capability: str) -> bool:
        """
        Check if the machine has a specific capability.
        
        Args:
            capability: The capability to check for
            
        Returns:
            bool: True if the machine has the capability, False otherwise
        """
        return capability in self.capabilities
    
    def add_capability(self, capability: str) -> None:
        """
        Add a capability to the machine profile.
        
        Args:
            capability: The capability to add
        """
        self.capabilities.add(capability)
    
    def add_axis(self, name: str, config: AxisConfig) -> None:
        """
        Add or update an axis configuration.
        
        Args:
            name: The axis name (e.g., "X", "Y", "Z")
            config: The axis configuration
        """
        self.axes[name] = config
    
    def add_tool(self, number: int, config: ToolConfig) -> None:
        """
        Add or update a tool configuration.
        
        Args:
            number: The tool number
            config: The tool configuration
        """
        self.tools[number] = config
    
    def add_heater(self, number: int, config: HeaterConfig) -> None:
        """
        Add or update a heater configuration.
        
        Args:
            number: The heater number
            config: The heater configuration
        """
        self.heaters[number] = config
    
    def add_fan(self, number: int, config: FanConfig) -> None:
        """
        Add or update a fan configuration.
        
        Args:
            number: The fan number
            config: The fan configuration
        """
        self.fans[number] = config
    
    def get_axis_limits(self, axis: str) -> List[float]:
        """
        Get the limits for an axis.
        
        Args:
            axis: The axis name
            
        Returns:
            List[float]: The axis limits [min, max]
            
        Raises:
            KeyError: If the axis does not exist
        """
        if axis not in self.axes:
            raise KeyError(f"Axis {axis} not found in profile")
        
        return self.axes[axis].limits
    
    def validate_position(self, position: Dict[str, float]) -> List[str]:
        """
        Validate a position against axis limits.
        
        Args:
            position: Dictionary mapping axis names to positions
            
        Returns:
            List[str]: List of validation errors, empty if valid
        """
        errors = []
        
        for axis, value in position.items():
            if axis in self.axes:
                limits = self.axes[axis].limits
                if value < limits[0]:
                    errors.append(f"{axis} position {value} below minimum {limits[0]}")
                elif value > limits[1]:
                    errors.append(f"{axis} position {value} above maximum {limits[1]}")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the profile to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the profile
        """
        return {
            "machine_name": self.machine_name,
            "firmware_name": self.firmware_name,
            "firmware_version": self.firmware_version,
            "board_type": self.board_type,
            "kinematics": self.kinematics,
            "capabilities": list(self.capabilities),
            "axes": {
                name: {
                    "limits": axis.limits,
                    "steps_per_mm": axis.steps_per_mm,
                    "max_speed": axis.max_speed,
                    "max_acceleration": axis.max_acceleration,
                    "homing_method": axis.homing_method,
                    "endstops": axis.endstops
                }
                for name, axis in self.axes.items()
            },
            "tools": {
                str(number): {
                    "name": tool.name,
                    "offsets": tool.offsets,
                    "extruder": tool.extruder,
                    "heater": tool.heater,
                    "fan": tool.fan
                }
                for number, tool in self.tools.items()
            },
            "heaters": {
                str(number): {
                    "name": heater.name,
                    "max_temp": heater.max_temp,
                    "min_temp": heater.min_temp
                }
                for number, heater in self.heaters.items()
            },
            "fans": {
                str(number): {
                    "name": fan.name,
                    "thermostatic": fan.thermostatic,
                    "inverted": fan.inverted
                }
                for number, fan in self.fans.items()
            },
            "max_speeds": self.max_speeds,
            "max_accelerations": self.max_accelerations,
            "config_settings": self.config_settings
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MachineProfile':
        """
        Create a profile from a dictionary.
        
        Args:
            data: Dictionary representation of the profile
            
        Returns:
            MachineProfile: A new machine profile
        """
        profile = cls()
        
        # Basic information
        profile.machine_name = data.get("machine_name", "Unknown Machine")
        profile.firmware_name = data.get("firmware_name", "Unknown")
        profile.firmware_version = data.get("firmware_version", "Unknown")
        profile.board_type = data.get("board_type", "Unknown")
        profile.kinematics = data.get("kinematics", "cartesian")
        
        # Capabilities
        profile.capabilities = set(data.get("capabilities", []))
        
        # Axes
        for name, axis_data in data.get("axes", {}).items():
            profile.add_axis(name, AxisConfig(
                name=name,
                limits=axis_data.get("limits", [0.0, 0.0]),
                steps_per_mm=axis_data.get("steps_per_mm"),
                max_speed=axis_data.get("max_speed"),
                max_acceleration=axis_data.get("max_acceleration"),
                homing_method=axis_data.get("homing_method"),
                endstops=axis_data.get("endstops", {})
            ))
        
        # Tools
        for number_str, tool_data in data.get("tools", {}).items():
            try:
                number = int(number_str)
                profile.add_tool(number, ToolConfig(
                    number=number,
                    name=tool_data.get("name", ""),
                    offsets=tool_data.get("offsets", {}),
                    extruder=tool_data.get("extruder"),
                    heater=tool_data.get("heater"),
                    fan=tool_data.get("fan")
                ))
            except ValueError:
                # Skip invalid tool numbers
                pass
        
        # Heaters
        for number_str, heater_data in data.get("heaters", {}).items():
            try:
                number = int(number_str)
                profile.add_heater(number, HeaterConfig(
                    number=number,
                    name=heater_data.get("name", ""),
                    max_temp=heater_data.get("max_temp", 0.0),
                    min_temp=heater_data.get("min_temp", 0.0)
                ))
            except ValueError:
                # Skip invalid heater numbers
                pass
        
        # Fans
        for number_str, fan_data in data.get("fans", {}).items():
            try:
                number = int(number_str)
                profile.add_fan(number, FanConfig(
                    number=number,
                    name=fan_data.get("name", ""),
                    thermostatic=fan_data.get("thermostatic", False),
                    inverted=fan_data.get("inverted", False)
                ))
            except ValueError:
                # Skip invalid fan numbers
                pass
        
        # Other settings
        profile.max_speeds = data.get("max_speeds", {})
        profile.max_accelerations = data.get("max_accelerations", {})
        profile.config_settings = data.get("config_settings", {})
        
        return profile
    
    @classmethod
    def from_config_g(cls, file_path: Union[str, Path]) -> 'MachineProfile':
        """
        Create a profile from a config.g file.
        
        Args:
            file_path: Path to the config.g file
            
        Returns:
            MachineProfile: A new machine profile
            
        Raises:
            ConfigurationError: If the file cannot be parsed
        """
        # This is a placeholder for the config.g parser
        # The actual implementation will be added in the next phase
        raise NotImplementedError("Config.g parsing not implemented yet")
    
    @classmethod
    def from_machine(cls, device) -> 'MachineProfile':
        """
        Create a profile from a connected machine.
        
        Args:
            device: The connected machine device
            
        Returns:
            MachineProfile: A new machine profile
            
        Raises:
            ConfigurationError: If the machine information cannot be retrieved
        """
        # This is a placeholder for the machine profile discovery
        # The actual implementation will be added in the next phase
        raise NotImplementedError("Machine profile discovery not implemented yet") 