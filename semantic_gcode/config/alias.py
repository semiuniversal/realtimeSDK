"""
Machine configuration alias system.

This module provides classes for mapping hardware components to their real-world functions
using a YAML-based alias system. It enables creating high-level, semantically meaningful
operations by combining multiple low-level hardware operations.
"""
from typing import Dict, Any, List, Optional, Union, Callable, Set, Tuple
from dataclasses import dataclass
import os
import re
import yaml
from pathlib import Path

from ..utils.exceptions import ConfigurationError


@dataclass
class ComponentAlias:
    """
    Alias for a machine component that maps hardware to its real-world function.
    
    Attributes:
        component_id: The hardware component ID (e.g., "fan:2", "axis:Z")
        function: The real-world function of the component
        type: The component type (e.g., "binary", "linear", "pwm")
        description: Human-readable description of the component
        config: Additional configuration for the component
    """
    component_id: str
    function: str
    type: str
    description: str
    config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}
    
    @property
    def hardware_type(self) -> str:
        """Get the hardware type from the component ID."""
        return self.component_id.split(':')[0] if ':' in self.component_id else ""
    
    @property
    def hardware_id(self) -> str:
        """Get the hardware ID from the component ID."""
        return self.component_id.split(':')[1] if ':' in self.component_id else self.component_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the alias to a dictionary for serialization."""
        result = {
            "function": self.function,
            "type": self.type,
            "description": self.description,
        }
        
        # Add all config items
        if self.config:
            for key, value in self.config.items():
                result[key] = value
                
        return result
    
    @classmethod
    def from_dict(cls, component_id: str, data: Dict[str, Any]) -> 'ComponentAlias':
        """
        Create a component alias from a dictionary.
        
        Args:
            component_id: The component ID
            data: The component data dictionary
            
        Returns:
            ComponentAlias: A new component alias
        """
        # Extract required fields
        function = data.get("function", component_id)
        type_ = data.get("type", "generic")
        description = data.get("description", "")
        
        # Extract additional configuration
        config = {k: v for k, v in data.items() 
                 if k not in ["function", "type", "description"]}
        
        return cls(
            component_id=component_id,
            function=function,
            type=type_,
            description=description,
            config=config
        )


@dataclass
class OperationStep:
    """
    A single step in a composite function operation.
    
    Attributes:
        component: The component to operate on
        action: The action to perform
        value: The value to use for the action
        description: Human-readable description of the step
    """
    component: str
    action: str = "set"
    value: Any = None
    description: str = ""


@dataclass
class CompositeFunction:
    """
    A function composed of multiple component operations.
    
    Attributes:
        name: The name of the function
        description: Human-readable description of the function
        components: List of components used by this function
        operations: Dictionary of operations, each containing a list of steps
    """
    name: str
    description: str
    components: List[str]
    operations: Dict[str, List[OperationStep]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the composite function to a dictionary for serialization."""
        operations_dict = {}
        for op_name, steps in self.operations.items():
            operations_dict[op_name] = [
                {
                    "component": step.component,
                    **({"action": step.action} if step.action != "set" else {}),
                    **({"value": step.value} if step.value is not None else {}),
                    **({"description": step.description} if step.description else {})
                }
                for step in steps
            ]
        
        return {
            "description": self.description,
            "components": self.components,
            "operations": operations_dict
        }
    
    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> 'CompositeFunction':
        """
        Create a composite function from a dictionary.
        
        Args:
            name: The function name
            data: The function data dictionary
            
        Returns:
            CompositeFunction: A new composite function
        """
        description = data.get("description", "")
        components = data.get("components", [])
        
        operations = {}
        for op_name, steps_data in data.get("operations", {}).items():
            steps = []
            for step_data in steps_data:
                component = step_data.get("component")
                if not component:
                    raise ConfigurationError(f"Missing component in operation {op_name}")
                
                steps.append(OperationStep(
                    component=component,
                    action=step_data.get("action", "set"),
                    value=step_data.get("value"),
                    description=step_data.get("description", "")
                ))
            operations[op_name] = steps
        
        return cls(
            name=name,
            description=description,
            components=components,
            operations=operations
        )


class AliasSystem:
    """
    System for managing component aliases and composite functions.
    
    This class provides methods for loading, saving, and managing
    component aliases and composite functions from YAML files.
    """
    
    def __init__(self):
        """Initialize an empty alias system."""
        self.aliases: Dict[str, ComponentAlias] = {}
        self.functions: Dict[str, CompositeFunction] = {}
        self.machine_name: str = "Unknown Machine"
        self.machine_type: str = "Unknown"
        self.machine_info: Dict[str, Any] = {}
    
    def load_from_file(self, file_path: Union[str, Path]) -> None:
        """
        Load aliases and functions from a YAML file.
        
        Args:
            file_path: Path to the YAML file
            
        Raises:
            ConfigurationError: If the file cannot be loaded or has invalid format
        """
        try:
            with open(file_path, 'r') as f:
                config = yaml.safe_load(f)
            
            if not isinstance(config, dict):
                raise ConfigurationError(f"Invalid configuration format in {file_path}")
            
            # Load machine information
            self.machine_name = config.get("machine_name", "Unknown Machine")
            self.machine_type = config.get("machine_type", "Unknown")
            
            # Extract machine info (excluding special keys)
            special_keys = {"machine_name", "machine_type", "aliases", "composite_functions"}
            self.machine_info = {k: v for k, v in config.items() 
                                if k not in special_keys}
            
            # Load component aliases
            for component_id, alias_data in config.get("aliases", {}).items():
                try:
                    alias = ComponentAlias.from_dict(component_id, alias_data)
                    self.aliases[component_id] = alias
                except Exception as e:
                    raise ConfigurationError(
                        f"Error loading alias for {component_id}: {str(e)}"
                    ) from e
            
            # Load composite functions
            for func_name, func_data in config.get("composite_functions", {}).items():
                try:
                    function = CompositeFunction.from_dict(func_name, func_data)
                    self.functions[func_name] = function
                except Exception as e:
                    raise ConfigurationError(
                        f"Error loading function {func_name}: {str(e)}"
                    ) from e
                    
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Error parsing YAML file {file_path}: {str(e)}") from e
        except IOError as e:
            raise ConfigurationError(f"Error reading file {file_path}: {str(e)}") from e
    
    def save_to_file(self, file_path: Union[str, Path]) -> None:
        """
        Save aliases and functions to a YAML file.
        
        Args:
            file_path: Path to the YAML file
            
        Raises:
            ConfigurationError: If the file cannot be saved
        """
        try:
            # Create configuration dictionary
            config = {
                "machine_name": self.machine_name,
                "machine_type": self.machine_type,
                **self.machine_info,
                "aliases": {
                    component_id: alias.to_dict()
                    for component_id, alias in self.aliases.items()
                },
                "composite_functions": {
                    func.name: func.to_dict()
                    for func in self.functions.values()
                }
            }
            
            # Save to file
            with open(file_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
                
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Error generating YAML: {str(e)}") from e
        except IOError as e:
            raise ConfigurationError(f"Error writing to file {file_path}: {str(e)}") from e
    
    def add_alias(self, component_id: str, alias: ComponentAlias) -> None:
        """
        Add or update a component alias.
        
        Args:
            component_id: The component ID
            alias: The component alias
        """
        self.aliases[component_id] = alias
    
    def remove_alias(self, component_id: str) -> bool:
        """
        Remove a component alias.
        
        Args:
            component_id: The component ID
            
        Returns:
            bool: True if the alias was removed, False if it didn't exist
        """
        if component_id in self.aliases:
            del self.aliases[component_id]
            return True
        return False
    
    def get_alias(self, component_id: str) -> Optional[ComponentAlias]:
        """
        Get a component alias by ID.
        
        Args:
            component_id: The component ID
            
        Returns:
            Optional[ComponentAlias]: The component alias, or None if not found
        """
        return self.aliases.get(component_id)
    
    def add_function(self, function: CompositeFunction) -> None:
        """
        Add or update a composite function.
        
        Args:
            function: The composite function
        """
        self.functions[function.name] = function
    
    def remove_function(self, function_name: str) -> bool:
        """
        Remove a composite function.
        
        Args:
            function_name: The function name
            
        Returns:
            bool: True if the function was removed, False if it didn't exist
        """
        if function_name in self.functions:
            del self.functions[function_name]
            return True
        return False
    
    def get_function(self, function_name: str) -> Optional[CompositeFunction]:
        """
        Get a composite function by name.
        
        Args:
            function_name: The function name
            
        Returns:
            Optional[CompositeFunction]: The composite function, or None if not found
        """
        return self.functions.get(function_name)
    
    def get_aliases_by_type(self, alias_type: str) -> Dict[str, ComponentAlias]:
        """
        Get all aliases of a specific type.
        
        Args:
            alias_type: The alias type to filter by
            
        Returns:
            Dict[str, ComponentAlias]: Dictionary of component IDs to aliases
        """
        return {
            component_id: alias
            for component_id, alias in self.aliases.items()
            if alias.type == alias_type
        }
    
    def get_aliases_by_hardware_type(self, hardware_type: str) -> Dict[str, ComponentAlias]:
        """
        Get all aliases for a specific hardware type.
        
        Args:
            hardware_type: The hardware type to filter by (e.g., "fan", "axis")
            
        Returns:
            Dict[str, ComponentAlias]: Dictionary of component IDs to aliases
        """
        return {
            component_id: alias
            for component_id, alias in self.aliases.items()
            if alias.hardware_type == hardware_type
        }
    
    def validate(self) -> List[str]:
        """
        Validate the alias system configuration.
        
        Returns:
            List[str]: List of validation errors, empty if valid
        """
        errors = []
        
        # Check for composite functions with missing component references
        for func_name, function in self.functions.items():
            for component_id in function.components:
                if component_id not in self.aliases:
                    errors.append(
                        f"Function '{func_name}' references undefined component '{component_id}'"
                    )
            
            # Check operation steps
            for op_name, steps in function.operations.items():
                for i, step in enumerate(steps):
                    if step.component not in self.aliases:
                        errors.append(
                            f"Operation '{op_name}' in function '{func_name}' step {i} "
                            f"references undefined component '{step.component}'"
                        )
        
        return errors 