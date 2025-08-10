"""
G-code configuration file parser.

This module provides classes for parsing G-code configuration files (like config.g)
and extracting machine capabilities and settings.
"""
from typing import Dict, Any, List, Optional, Union, Set, Tuple, Pattern
import os
import re
from pathlib import Path
from dataclasses import dataclass, field

from ..utils.exceptions import ConfigurationError


@dataclass
class ConfigPattern:
    """Pattern for detecting interesting configurations in G-code files."""
    type: str
    description: str
    regex: Pattern
    component_group: Optional[int] = None
    value_group: Optional[int] = None
    suggestion: Optional[str] = None


class ConfigParser:
    """
    Parser for G-code configuration files.
    
    This class provides methods for parsing G-code configuration files (like config.g)
    and extracting machine capabilities and settings.
    """
    
    # Common patterns for RepRapFirmware config.g files
    PATTERNS = [
        # Machine name (M550)
        re.compile(r'M550\s+P"?([^"]*)"?'),
        
        # Kinematics (M669)
        re.compile(r'M669\s+K(\d+)'),
        
        # Axis mapping (M584)
        re.compile(r'M584\s+([XYZUVWABC]+\d+\s*)+'),
        
        # Axis limits (M208)
        re.compile(r'M208\s+([XYZUVWABC]-?\d+(?:\.\d+)?)+\s+S(\d+)'),
        
        # Steps per mm (M92)
        re.compile(r'M92\s+([XYZUVWABC]\d+(?:\.\d+)?)+'),
        
        # Max speeds (M203)
        re.compile(r'M203\s+([XYZUVWABC]\d+(?:\.\d+)?)+'),
        
        # Max accelerations (M201)
        re.compile(r'M201\s+([XYZUVWABC]\d+(?:\.\d+)?)+'),
        
        # Endstops (M574)
        re.compile(r'M574\s+([XYZUVWABC])(\d+)\s+S(\d+)'),
        
        # Tool definitions (M563)
        re.compile(r'M563\s+P(\d+)(?:\s+S"?([^"]*)"?)?(?:\s+F(\d+))?(?:\s+D(\d+))?(?:\s+H(\d+))?'),
        
        # Fan definitions (M950 F)
        re.compile(r'M950\s+F(\d+)\s+C"([^"]*)"'),
        
        # Heater definitions (M950 H)
        re.compile(r'M950\s+H(\d+)\s+C"([^"]*)"'),
        
        # Temperature limits (M143)
        re.compile(r'M143\s+H(\d+)\s+S(\d+(?:\.\d+)?)'),
    ]
    
    # Patterns for detecting unusual configurations
    UNUSUAL_PATTERNS = [
        # Unusual steps/mm (very high or very low)
        ConfigPattern(
            type="unusual_steps_per_mm",
            description="Unusually high steps/mm value",
            regex=re.compile(r'M92\s+([XYZUVWABC])(\d{4,}(?:\.\d+)?)'),
            component_group=1,
            value_group=2,
            suggestion="This might indicate a fine-precision mechanism or non-standard usage"
        ),
        ConfigPattern(
            type="unusual_steps_per_mm",
            description="Unusually low steps/mm value",
            regex=re.compile(r'M92\s+([XYZ])([0-4](?:\.\d+)?)'),
            component_group=1,
            value_group=2,
            suggestion="This might indicate a non-standard usage or unit configuration"
        ),
        
        # Binary fan usage (only 0 or 255 values)
        ConfigPattern(
            type="binary_fan",
            description="Fan used in binary mode (only 0/255 values)",
            regex=re.compile(r'M106\s+P(\d+)\s+S(0|255|1\.0)'),
            component_group=1,
            suggestion="This might indicate a solenoid valve or relay control"
        ),
        
        # Fan associated with tool
        ConfigPattern(
            type="tool_fan_association",
            description="Fan associated with a tool",
            regex=re.compile(r'M563\s+P(\d+).*\s+F(\d+)'),
            component_group=2,
            suggestion="This might indicate a special tool function like air control"
        ),
        
        # Unusual axis configuration (extra axes)
        ConfigPattern(
            type="unusual_axis",
            description="Non-standard axis configuration",
            regex=re.compile(r'M584\s+.*([UVWABC])\d+'),
            component_group=1,
            suggestion="This might indicate a specialized machine with additional axes"
        ),
    ]
    
    def __init__(self):
        """Initialize the config parser."""
        self.config_data: Dict[str, Any] = {
            "machine_name": None,
            "axes": {},
            "fans": {},
            "heaters": {},
            "tools": {},
            "endstops": {},
            "kinematics": None,
            "speeds": {},
            "accelerations": {},
            "steps_per_mm": {},
            "temperature_limits": {},
            "network": {},
        }
        self.detected_patterns: List[Dict[str, Any]] = []
    
    def parse_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Parse a G-code configuration file.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            Dict[str, Any]: Structured configuration data
            
        Raises:
            ConfigurationError: If the file cannot be parsed
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            return self.parse_content(content)
            
        except IOError as e:
            raise ConfigurationError(f"Error reading file {file_path}: {str(e)}") from e
    
    def parse_content(self, content: str) -> Dict[str, Any]:
        """
        Parse G-code configuration content.
        
        Args:
            content: G-code configuration content
            
        Returns:
            Dict[str, Any]: Structured configuration data
        """
        # Reset config data
        self.config_data = {
            "machine_name": None,
            "axes": {},
            "fans": {},
            "heaters": {},
            "tools": {},
            "endstops": {},
            "kinematics": None,
            "speeds": {},
            "accelerations": {},
            "steps_per_mm": {},
            "temperature_limits": {},
            "network": {},
        }
        self.detected_patterns = []
        
        # Process line by line
        for line in content.splitlines():
            # Remove comments
            line = re.sub(r';.*$', '', line).strip()
            if not line:
                continue
            
            # Parse basic configuration
            self._parse_line(line)
            
            # Detect unusual patterns
            self._detect_patterns(line)
        
        return {
            "config": self.config_data,
            "patterns": self.detected_patterns
        }
    
    def _parse_line(self, line: str) -> None:
        """
        Parse a single line of G-code configuration.
        
        Args:
            line: G-code configuration line
        """
        # Machine name (M550)
        match = re.search(r'M550\s+P"?([^"]*)"?', line)
        if match:
            self.config_data["machine_name"] = match.group(1)
            return
        
        # Kinematics (M669)
        match = re.search(r'M669\s+K(\d+)', line)
        if match:
            k_value = int(match.group(1))
            kinematics_map = {
                0: "cartesian",
                1: "corexy",
                2: "corexz",
                3: "delta",
                9: "hangprinter",
                10: "polar",
                11: "rotary_delta"
            }
            self.config_data["kinematics"] = kinematics_map.get(k_value, f"unknown_{k_value}")
            return
        
        # Axis mapping (M584)
        match = re.search(r'M584\s+((?:[XYZUVWABC]\d+\s*)+)', line)
        if match:
            mappings = re.findall(r'([XYZUVWABC])(\d+)', match.group(1))
            for axis, driver in mappings:
                if axis not in self.config_data["axes"]:
                    self.config_data["axes"][axis] = {}
                self.config_data["axes"][axis]["driver"] = int(driver)
            return
        
        # Axis limits (M208)
        match = re.search(r'M208\s+((?:[XYZUVWABC]-?\d+(?:\.\d+)?\s*)+)\s+S(\d+)', line)
        if match:
            limit_type = "min" if match.group(2) == "1" else "max"
            limits = re.findall(r'([XYZUVWABC])(-?\d+(?:\.\d+)?)', match.group(1))
            for axis, value in limits:
                if axis not in self.config_data["axes"]:
                    self.config_data["axes"][axis] = {}
                if "limits" not in self.config_data["axes"][axis]:
                    self.config_data["axes"][axis]["limits"] = [0.0, 0.0]
                
                index = 0 if limit_type == "min" else 1
                self.config_data["axes"][axis]["limits"][index] = float(value)
            return
        
        # Steps per mm (M92)
        match = re.search(r'M92\s+((?:[XYZUVWABC]\d+(?:\.\d+)?\s*)+)', line)
        if match:
            steps = re.findall(r'([XYZUVWABC])(\d+(?:\.\d+)?)', match.group(1))
            for axis, value in steps:
                self.config_data["steps_per_mm"][axis] = float(value)
                if axis not in self.config_data["axes"]:
                    self.config_data["axes"][axis] = {}
                self.config_data["axes"][axis]["steps_per_mm"] = float(value)
            return
        
        # Max speeds (M203)
        match = re.search(r'M203\s+((?:[XYZUVWABC]\d+(?:\.\d+)?\s*)+)', line)
        if match:
            speeds = re.findall(r'([XYZUVWABC])(\d+(?:\.\d+)?)', match.group(1))
            for axis, value in speeds:
                self.config_data["speeds"][axis] = float(value)
                if axis not in self.config_data["axes"]:
                    self.config_data["axes"][axis] = {}
                self.config_data["axes"][axis]["max_speed"] = float(value)
            return
        
        # Max accelerations (M201)
        match = re.search(r'M201\s+((?:[XYZUVWABC]\d+(?:\.\d+)?\s*)+)', line)
        if match:
            accels = re.findall(r'([XYZUVWABC])(\d+(?:\.\d+)?)', match.group(1))
            for axis, value in accels:
                self.config_data["accelerations"][axis] = float(value)
                if axis not in self.config_data["axes"]:
                    self.config_data["axes"][axis] = {}
                self.config_data["axes"][axis]["max_acceleration"] = float(value)
            return
        
        # Endstops (M574)
        match = re.search(r'M574\s+([XYZUVWABC])(\d+)\s+S(\d+)', line)
        if match:
            axis = match.group(1)
            position = int(match.group(2))  # 0=none, 1=low end, 2=high end
            type_ = int(match.group(3))     # 0=active low, 1=active high, etc.
            
            position_map = {0: "none", 1: "min", 2: "max"}
            type_map = {0: "active_low", 1: "active_high", 2: "z_probe", 3: "e_probe", 4: "motor_load"}
            
            if axis not in self.config_data["endstops"]:
                self.config_data["endstops"][axis] = {}
            
            self.config_data["endstops"][axis]["position"] = position_map.get(position, f"unknown_{position}")
            self.config_data["endstops"][axis]["type"] = type_map.get(type_, f"unknown_{type_}")
            
            if axis not in self.config_data["axes"]:
                self.config_data["axes"][axis] = {}
            if "endstops" not in self.config_data["axes"][axis]:
                self.config_data["axes"][axis]["endstops"] = {}
            
            self.config_data["axes"][axis]["endstops"][position_map.get(position, f"unknown_{position}")] = type_map.get(type_, f"unknown_{type_}")
            return
        
        # Tool definitions (M563)
        match = re.search(r'M563\s+P(\d+)(?:\s+S"?([^"]*)"?)?(?:\s+F(\d+))?(?:\s+D(\d+))?(?:\s+H(\d+))?', line)
        if match:
            tool_num = int(match.group(1))
            name = match.group(2) if match.group(2) else f"Tool {tool_num}"
            fan = int(match.group(3)) if match.group(3) else None
            extruder = int(match.group(4)) if match.group(4) else None
            heater = int(match.group(5)) if match.group(5) else None
            
            self.config_data["tools"][tool_num] = {
                "name": name,
                "fan": fan,
                "extruder": extruder,
                "heater": heater
            }
            return
        
        # Fan definitions (M950 F)
        match = re.search(r'M950\s+F(\d+)\s+C"([^"]*)"', line)
        if match:
            fan_num = int(match.group(1))
            pin = match.group(2)
            
            self.config_data["fans"][fan_num] = {
                "pin": pin
            }
            return
        
        # Heater definitions (M950 H)
        match = re.search(r'M950\s+H(\d+)\s+C"([^"]*)"', line)
        if match:
            heater_num = int(match.group(1))
            pin = match.group(2)
            
            self.config_data["heaters"][heater_num] = {
                "pin": pin
            }
            return
        
        # Temperature limits (M143)
        match = re.search(r'M143\s+H(\d+)\s+S(\d+(?:\.\d+)?)', line)
        if match:
            heater_num = int(match.group(1))
            temp_limit = float(match.group(2))
            
            self.config_data["temperature_limits"][heater_num] = temp_limit
            
            if heater_num not in self.config_data["heaters"]:
                self.config_data["heaters"][heater_num] = {}
            
            self.config_data["heaters"][heater_num]["max_temp"] = temp_limit
            return
    
    def _detect_patterns(self, line: str) -> None:
        """
        Detect unusual patterns in a G-code configuration line.
        
        Args:
            line: G-code configuration line
        """
        for pattern in self.UNUSUAL_PATTERNS:
            match = pattern.regex.search(line)
            if match:
                result = {
                    "type": pattern.type,
                    "description": pattern.description,
                    "line": line
                }
                
                if pattern.component_group is not None and match.group(pattern.component_group):
                    component = match.group(pattern.component_group)
                    result["component"] = component
                    
                    # Determine component ID
                    if pattern.type == "unusual_steps_per_mm" or pattern.type == "unusual_axis":
                        result["component_id"] = f"axis:{component}"
                    elif pattern.type == "binary_fan" or pattern.type == "tool_fan_association":
                        result["component_id"] = f"fan:{component}"
                
                if pattern.value_group is not None and match.group(pattern.value_group):
                    result["value"] = match.group(pattern.value_group)
                
                if pattern.suggestion:
                    result["suggestion"] = pattern.suggestion
                
                self.detected_patterns.append(result)
    
    def get_detected_patterns(self) -> List[Dict[str, Any]]:
        """
        Get the detected unusual patterns.
        
        Returns:
            List[Dict[str, Any]]: List of detected patterns
        """
        return self.detected_patterns 