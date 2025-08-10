"""
Machine controller with component and composite function support.

This module provides the MachineController class, which integrates the component
registry and composite function system with the machine's transport layer.
"""
from typing import Dict, Any, List, Optional, Union, Callable, Type
from pathlib import Path
import yaml

from .component import Component, ComponentRegistry, AxisComponent, FanComponent, ToolComponent, HeaterComponent
from .composite import CompositeFunction, CompositeFunctionRegistry
from .alias import AliasSystem
from ..utils.exceptions import ConfigurationError


class MachineController:
    """
    Machine controller with support for components and composite functions.
    
    This class integrates the component registry and composite function system
    with the machine's transport layer, providing a high-level API for machine
    control.
    """
    
    def __init__(self, transport: Any, alias_file: Optional[Union[str, Path]] = None):
        """
        Initialize a machine controller.
        
        Args:
            transport: The transport layer
            alias_file: Optional path to an alias file
        """
        self.transport = transport
        self.component_registry = ComponentRegistry()
        self.function_registry = CompositeFunctionRegistry(self)
        
        # Initialize with aliases if provided
        if alias_file:
            self.load_aliases(alias_file)
    
    def load_aliases(self, file_path: Union[str, Path]) -> None:
        """
        Load aliases from a YAML file.
        
        Args:
            file_path: Path to the alias file
            
        Raises:
            ConfigurationError: If the file cannot be loaded
        """
        try:
            alias_system = AliasSystem()
            alias_system.load_from_file(file_path)
            
            # Register components from aliases
            for component_id, alias in alias_system.aliases.items():
                self._register_component_from_alias(component_id, alias.config)
            
            # Create composite functions
            for name, function in alias_system.functions.items():
                self._create_composite_function(name, {
                    "description": function.description,
                    "components": function.components,
                    "operations": {
                        op_name: [
                            {
                                "component": step.component,
                                "action": step.action,
                                "value": step.value,
                                "description": step.description
                            }
                            for step in steps
                        ]
                        for op_name, steps in function.operations.items()
                    }
                })
            
            # Validate the configuration
            self.validate()
            
        except Exception as e:
            raise ConfigurationError(f"Error loading aliases from {file_path}: {str(e)}") from e
    
    def _register_component_from_alias(self, component_id: str, config: Dict[str, Any]) -> Component:
        """
        Register a component based on its alias configuration.
        
        Args:
            component_id: The component ID
            config: The component configuration
            
        Returns:
            Component: The created component
        """
        component = self.component_registry.create_component(component_id, self, config)
        self.component_registry.register_component(component_id, component)
        return component
    
    def _create_composite_function(self, name: str, config: Dict[str, Any]) -> CompositeFunction:
        """
        Create a composite function.
        
        Args:
            name: The function name
            config: The function configuration
            
        Returns:
            CompositeFunction: The created function
        """
        function = self.function_registry.register_function(name, config)
        
        # Add it as an attribute for easy access
        if not hasattr(self, name) or name not in dir(self):
            setattr(self, name, function)
        
        return function
    
    def get_component(self, component_id: str) -> Component:
        """
        Get a component by ID.
        
        Args:
            component_id: The component ID
            
        Returns:
            Component: The component
            
        Raises:
            ValueError: If the component is not found
        """
        return self.component_registry.get_component(component_id)
    
    def list_components(self) -> List[str]:
        """
        List all registered components.
        
        Returns:
            List[str]: List of component IDs
        """
        return self.component_registry.list_components()
    
    def get_components_by_type(self, component_type: str) -> Dict[str, Component]:
        """
        Get all components of a specific type.
        
        Args:
            component_type: The component type
            
        Returns:
            Dict[str, Component]: Dictionary of component IDs to components
        """
        return self.component_registry.get_components_by_type(component_type)
    
    def list_composite_functions(self) -> List[str]:
        """
        List all composite functions.
        
        Returns:
            List[str]: List of function names
        """
        return self.function_registry.list_functions()
    
    def get_composite_function(self, name: str) -> CompositeFunction:
        """
        Get a composite function by name.
        
        Args:
            name: The function name
            
        Returns:
            CompositeFunction: The composite function
            
        Raises:
            ValueError: If the function is not found
        """
        return self.function_registry.get_function(name)
    
    def send_gcode(self, gcode: str) -> Any:
        """
        Send raw G-code to the machine.
        
        Args:
            gcode: The G-code to send
            
        Returns:
            Any: The result of the operation
        """
        return self.transport.send_line(gcode)
    
    def query_gcode(self, gcode: str) -> Any:
        """
        Send a G-code query to the machine and wait for a response.
        
        Args:
            gcode: The G-code to send
            
        Returns:
            Any: The response from the machine
        """
        return self.transport.query(gcode)
    
    def validate(self) -> Dict[str, List[str]]:
        """
        Validate the configuration.
        
        Returns:
            Dict[str, List[str]]: Dictionary mapping function names to validation errors
        """
        return self.function_registry.validate_all(self.component_registry)
    
    def register_component_type(self, type_name: str, component_class: Type[Component]) -> None:
        """
        Register a new component type.
        
        Args:
            type_name: The component type name
            component_class: The component class
        """
        self.component_registry.register_component_type(type_name, component_class)
    
    def create_component(self, component_id: str, config: Optional[Dict[str, Any]] = None) -> Component:
        """
        Create and register a new component.
        
        Args:
            component_id: The component ID
            config: Optional configuration for the component
            
        Returns:
            Component: The created component
        """
        component = self.component_registry.create_component(component_id, self, config)
        self.component_registry.register_component(component_id, component)
        return component 