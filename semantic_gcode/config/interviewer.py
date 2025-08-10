"""
Interactive configuration interviewer.

This module provides classes for guiding users through an interactive process
to create machine configuration alias files.
"""
from typing import Dict, Any, List, Optional, Union, Set, Tuple, Callable
import os
import re
from pathlib import Path
import yaml

from .alias import AliasSystem, ComponentAlias, CompositeFunction, OperationStep
from .parser import ConfigParser
from ..utils.exceptions import ConfigurationError


class ConfigurationInterviewer:
    """
    Interactive interviewer for creating machine configuration alias files.
    
    This class guides users through an interactive process to create alias files
    for their machine configurations, based on parsed config.g files.
    """
    
    def __init__(self, config_file: Optional[Union[str, Path]] = None):
        """
        Initialize the configuration interviewer.
        
        Args:
            config_file: Path to the config.g file (optional)
        """
        self.parser = ConfigParser()
        self.alias_system = AliasSystem()
        self.config_data: Dict[str, Any] = {}
        self.patterns: List[Dict[str, Any]] = []
        
        if config_file:
            self.load_config_file(config_file)
    
    def load_config_file(self, file_path: Union[str, Path]) -> None:
        """
        Load and parse a config.g file.
        
        Args:
            file_path: Path to the config.g file
            
        Raises:
            ConfigurationError: If the file cannot be parsed
        """
        result = self.parser.parse_file(file_path)
        self.config_data = result["config"]
        self.patterns = result["patterns"]
    
    def run_interview(self, input_func: Callable[[str], str] = input, print_func: Callable[[str], None] = print) -> None:
        """
        Run the interactive interview process.
        
        Args:
            input_func: Function to use for input (default: input)
            print_func: Function to use for output (default: print)
        """
        self._welcome(print_func)
        self._interview_machine_basics(input_func, print_func)
        self._interview_axes(input_func, print_func)
        self._interview_fans(input_func, print_func)
        self._interview_tools(input_func, print_func)
        self._interview_composite_functions(input_func, print_func)
        self._generate_yaml(input_func, print_func)
    
    def _welcome(self, print_func: Callable[[str], None]) -> None:
        """
        Display welcome message and basic information.
        
        Args:
            print_func: Function to use for output
        """
        print_func("=== Machine Configuration Interview ===\n")
        
        if self.config_data:
            print_func(f"Machine name: {self.config_data.get('machine_name', 'Unknown')}")
            print_func(f"Kinematics: {self.config_data.get('kinematics', 'Unknown')}")
            print_func(f"Axes: {', '.join(self.config_data.get('axes', {}).keys())}")
            print_func(f"Tools: {len(self.config_data.get('tools', {}))}")
            print_func(f"Fans: {len(self.config_data.get('fans', {}))}")
            
            if self.patterns:
                print_func("\nI've noticed some interesting patterns in your configuration:")
                for pattern in self.patterns:
                    print_func(f"- {pattern['description']}")
                    if 'suggestion' in pattern:
                        print_func(f"  Suggestion: {pattern['suggestion']}")
        else:
            print_func("No configuration file loaded. The interview will start from scratch.")
    
    def _interview_machine_basics(self, input_func: Callable[[str], str], print_func: Callable[[str], None]) -> None:
        """
        Interview about basic machine information.
        
        Args:
            input_func: Function to use for input
            print_func: Function to use for output
        """
        print_func("\n=== Basic Machine Information ===")
        
        # Machine name
        default_name = self.config_data.get("machine_name", "Unknown Machine")
        machine_name = input_func(f"What is the name of your machine? [{default_name}]: ") or default_name
        self.alias_system.machine_name = machine_name
        
        # Machine type
        machine_type = input_func("What type of machine is this? (e.g., 3D Printer, CNC, Laser, Plotter): ")
        self.alias_system.machine_type = machine_type
        
        # Machine purpose
        machine_purpose = input_func("What is the primary purpose of this machine? ")
        self.alias_system.machine_info["purpose"] = machine_purpose
        
        # Firmware information
        if self.config_data:
            self.alias_system.machine_info["kinematics"] = self.config_data.get("kinematics", "unknown")
    
    def _interview_axes(self, input_func: Callable[[str], str], print_func: Callable[[str], None]) -> None:
        """
        Interview about axes and their purposes.
        
        Args:
            input_func: Function to use for input
            print_func: Function to use for output
        """
        print_func("\n=== Axes Configuration ===")
        
        axes = self.config_data.get("axes", {})
        if not axes:
            print_func("No axes found in the configuration.")
            return
        
        for axis, info in axes.items():
            # Get default name based on common usage
            default_name = self._get_default_axis_name(axis)
            
            # Check if we have a pattern for this axis
            axis_patterns = [p for p in self.patterns if p.get("component_id") == f"axis:{axis}"]
            
            # If we have patterns, mention them
            if axis_patterns:
                for pattern in axis_patterns:
                    print_func(f"\nNote: {pattern['description']}")
                    if 'suggestion' in pattern:
                        print_func(f"Suggestion: {pattern['suggestion']}")
            
            # Get axis limits
            limits = info.get("limits", [0.0, 0.0])
            steps_per_mm = info.get("steps_per_mm")
            max_speed = info.get("max_speed")
            
            print_func(f"\nAxis {axis}:")
            if limits:
                print_func(f"  Range: {limits[0]} to {limits[1]} mm")
            if steps_per_mm:
                print_func(f"  Steps/mm: {steps_per_mm}")
            if max_speed:
                print_func(f"  Max speed: {max_speed} mm/min")
            
            # Ask about axis purpose
            purpose = input_func(f"What is the purpose of the {axis}-axis? [{default_name}]: ") or default_name
            
            # Create alias
            self.alias_system.add_alias(f"axis:{axis}", ComponentAlias(
                component_id=f"axis:{axis}",
                function=purpose,
                type="linear",
                description=f"{axis}-axis controls {purpose}",
                config={
                    "range": limits,
                    "unit": "mm",
                    "steps_per_mm": steps_per_mm,
                    "max_speed": max_speed
                }
            ))
            
            # If it has unusual steps/mm, ask about precision
            if steps_per_mm and steps_per_mm > 1000:
                precision = input_func(f"The {axis}-axis has {steps_per_mm} steps/mm, which is unusually high. "
                                     f"Does this axis require fine precision? [Y/n]: ")
                if precision.lower() != 'n':
                    alias = self.alias_system.get_alias(f"axis:{axis}")
                    if alias:
                        alias.config["high_precision"] = True
                        alias.description += " (high precision)"
    
    def _get_default_axis_name(self, axis: str) -> str:
        """
        Get default name for an axis based on common usage.
        
        Args:
            axis: The axis name
            
        Returns:
            str: Default function name for the axis
        """
        defaults = {
            'X': 'horizontal_movement',
            'Y': 'vertical_movement',
            'Z': 'height',
            'U': 'additional_axis_1',
            'V': 'additional_axis_2',
            'A': 'rotation_a',
            'B': 'rotation_b',
            'C': 'rotation_c',
        }
        return defaults.get(axis, f"{axis.lower()}_axis")
    
    def _interview_fans(self, input_func: Callable[[str], str], print_func: Callable[[str], None]) -> None:
        """
        Interview about fans and their purposes.
        
        Args:
            input_func: Function to use for input
            print_func: Function to use for output
        """
        print_func("\n=== Fan/Output Configuration ===")
        
        fans = self.config_data.get("fans", {})
        if not fans:
            print_func("No fans found in the configuration.")
            return
        
        for fan_num, info in fans.items():
            # Check if this fan is associated with a tool
            tool_association = None
            for tool_num, tool_info in self.config_data.get("tools", {}).items():
                if tool_info.get("fan") == fan_num:
                    tool_association = (tool_num, tool_info.get("name", f"Tool {tool_num}"))
            
            if tool_association:
                print_func(f"\nFan {fan_num} is associated with Tool {tool_association[0]} ({tool_association[1]})")
                
            # Check for binary usage pattern
            fan_patterns = [p for p in self.patterns if p.get("component_id") == f"fan:{fan_num}"]
            binary_pattern = any(p["type"] == "binary_fan" for p in fan_patterns)
            
            if binary_pattern:
                print_func(f"Fan {fan_num} shows a binary on/off usage pattern")
                is_binary = input_func(f"Is Fan {fan_num} controlling a binary device like a solenoid or relay? [Y/n]: ")
                if is_binary.lower() != 'n':
                    device_type = input_func(f"What type of device is Fan {fan_num} controlling? [solenoid]: ") or "solenoid"
                    purpose = input_func(f"What is the purpose of this {device_type}? (e.g., air valve, vacuum): ")
                    
                    self.alias_system.add_alias(f"fan:{fan_num}", ComponentAlias(
                        component_id=f"fan:{fan_num}",
                        function=f"{purpose}_{fan_num}",
                        type="binary",
                        description=f"{device_type.capitalize()} controlling {purpose}",
                        config={
                            "device_type": device_type
                        }
                    ))
                else:
                    purpose = input_func(f"What is the purpose of Fan {fan_num}? (e.g., cooling, exhaust): ")
                    self.alias_system.add_alias(f"fan:{fan_num}", ComponentAlias(
                        component_id=f"fan:{fan_num}",
                        function=f"{purpose}_fan",
                        type="pwm",
                        description=f"Fan controlling {purpose}"
                    ))
            else:
                purpose = input_func(f"What is the purpose of Fan {fan_num}? (e.g., cooling, exhaust): ")
                self.alias_system.add_alias(f"fan:{fan_num}", ComponentAlias(
                    component_id=f"fan:{fan_num}",
                    function=f"{purpose}_fan",
                    type="pwm",
                    description=f"Fan controlling {purpose}"
                ))
    
    def _interview_tools(self, input_func: Callable[[str], str], print_func: Callable[[str], None]) -> None:
        """
        Interview about tools and their purposes.
        
        Args:
            input_func: Function to use for input
            print_func: Function to use for output
        """
        print_func("\n=== Tool Configuration ===")
        
        tools = self.config_data.get("tools", {})
        if not tools:
            print_func("No tools found in the configuration.")
            return
        
        for tool_num, info in tools.items():
            name = info.get("name", f"Tool {tool_num}")
            print_func(f"\nTool {tool_num} ({name}):")
            
            if "fan" in info and info["fan"] is not None:
                print_func(f"  Associated fan: {info['fan']}")
            if "heater" in info and info["heater"] is not None:
                print_func(f"  Associated heater: {info['heater']}")
            if "extruder" in info and info["extruder"] is not None:
                print_func(f"  Associated extruder: {info['extruder']}")
            
            # Ask about tool purpose
            purpose = input_func(f"What is the purpose of {name}? (e.g., extruder, spindle, airbrush): ")
            
            # Create alias
            self.alias_system.add_alias(f"tool:{tool_num}", ComponentAlias(
                component_id=f"tool:{tool_num}",
                function=f"{purpose}_{tool_num}",
                type="tool",
                description=f"{name} - {purpose.capitalize()}",
                config={
                    "name": name,
                    "fan": info.get("fan"),
                    "heater": info.get("heater"),
                    "extruder": info.get("extruder")
                }
            ))
            
            # Ask about control mechanisms for special tools
            if purpose.lower() in ["airbrush", "spray", "paint"]:
                flow_control = input_func(f"How is the paint/material flow controlled for {name}? "
                                        "(e.g., servo, stepper, manual): ")
                
                if flow_control.lower() in ["servo", "stepper", "motor"]:
                    flow_axis = input_func(f"Which axis or output controls the flow for {name}? (e.g., U, servo0): ")
                    if flow_axis:
                        alias = self.alias_system.get_alias(f"tool:{tool_num}")
                        if alias:
                            alias.config["flow_control"] = flow_axis
                            
                            # Add to description
                            alias.description += f" (flow controlled by {flow_axis})"
    
    def _interview_composite_functions(self, input_func: Callable[[str], str], print_func: Callable[[str], None]) -> None:
        """
        Interview about composite functions.
        
        Args:
            input_func: Function to use for input
            print_func: Function to use for output
        """
        print_func("\n=== Composite Functions ===")
        
        create_composite = input_func("Would you like to create composite functions for common operations? [Y/n]: ")
        
        if create_composite.lower() == 'n':
            return
        
        # Find all tools
        for tool_key, tool_alias in self.alias_system.get_aliases_by_hardware_type("tool").items():
            tool_num = tool_alias.hardware_id
            tool_name = tool_alias.config.get("name", f"Tool {tool_num}")
            
            create_for_tool = input_func(f"\nCreate composite functions for {tool_name}? [Y/n]: ")
            if create_for_tool.lower() == 'n':
                continue
            
            function_name = input_func(f"Function name for {tool_name} operations? [{tool_alias.function}]: ") or tool_alias.function
            
            # Find associated components
            components = [tool_key]
            operations = {}
            
            # Check for associated fan
            fan_num = tool_alias.config.get("fan")
            if fan_num is not None:
                fan_key = f"fan:{fan_num}"
                if self.alias_system.get_alias(fan_key):
                    components.append(fan_key)
                    
                    # Add activate/deactivate operations if it's a binary fan
                    fan_alias = self.alias_system.get_alias(fan_key)
                    if fan_alias and fan_alias.type == "binary":
                        operations["activate"] = [
                            OperationStep(
                                component=tool_key,
                                action="select",
                                description=f"Select {tool_name}"
                            ),
                            OperationStep(
                                component=fan_key,
                                value=255,
                                description=f"Turn on {fan_alias.function}"
                            )
                        ]
                        
                        operations["deactivate"] = [
                            OperationStep(
                                component=fan_key,
                                value=0,
                                description=f"Turn off {fan_alias.function}"
                            )
                        ]
            
            # Check for flow control
            flow_control = tool_alias.config.get("flow_control")
            if flow_control:
                # If it's an axis, add the axis component
                if flow_control.upper() in "XYZUVWABC":
                    flow_component = f"axis:{flow_control.upper()}"
                    if self.alias_system.get_alias(flow_component):
                        components.append(flow_component)
                        
                        # Add set_flow operation
                        operations["set_flow"] = [
                            OperationStep(
                                component=flow_component,
                                action="move",
                                value="PARAM * 0.01",
                                description=f"Set {tool_name} flow to PARAM%"
                            )
                        ]
            
            # Create the composite function
            if operations:
                composite_function = CompositeFunction(
                    name=function_name,
                    description=f"Control {tool_name}",
                    components=components,
                    operations=operations
                )
                
                self.alias_system.add_function(composite_function)
                print_func(f"Created composite function '{function_name}' with operations: {', '.join(operations.keys())}")
            else:
                print_func(f"No operations created for {tool_name}. Skipping composite function.")
    
    def _generate_yaml(self, input_func: Callable[[str], str], print_func: Callable[[str], None]) -> None:
        """
        Generate YAML configuration file.
        
        Args:
            input_func: Function to use for input
            print_func: Function to use for output
        """
        # Validate the configuration
        errors = self.alias_system.validate()
        if errors:
            print_func("\nWarning: The following validation errors were found:")
            for error in errors:
                print_func(f"- {error}")
            
            proceed = input_func("Do you want to proceed with generating the YAML file? [Y/n]: ")
            if proceed.lower() == 'n':
                return
        
        # Get output file name
        output_file = input_func("\nOutput file name [machine_profile.yaml]: ") or "machine_profile.yaml"
        
        # Save to file
        try:
            self.alias_system.save_to_file(output_file)
            print_func(f"\nConfiguration saved to {os.path.abspath(output_file)}")
        except Exception as e:
            print_func(f"\nError saving configuration: {str(e)}")
    
    def get_alias_system(self) -> AliasSystem:
        """
        Get the alias system.
        
        Returns:
            AliasSystem: The alias system
        """
        return self.alias_system 