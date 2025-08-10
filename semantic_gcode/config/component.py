"""
Machine component registry and base classes.

This module provides classes for registering and managing machine components,
which are used by the composite function system.
"""
from typing import Dict, Any, List, Optional, Union, Callable, Type
from abc import ABC, abstractmethod

from ..utils.exceptions import ConfigurationError


class Component(ABC):
    """
    Base class for machine components.
    
    Components represent physical parts of the machine (axes, fans, tools, etc.)
    and provide methods to interact with them.
    """
    
    def __init__(self, component_id: str, machine: Any, config: Optional[Dict[str, Any]] = None):
        """
        Initialize a component.
        
        Args:
            component_id: The component ID (e.g., "axis:X", "fan:0")
            machine: The machine controller
            config: Optional configuration for the component
        """
        self.component_id = component_id
        self.machine = machine
        self.config = config or {}
        
        # Parse the component type and ID
        parts = component_id.split(':', 1)
        self.type = parts[0] if len(parts) > 1 else "generic"
        self.id = parts[1] if len(parts) > 1 else component_id
    
    def execute_action(self, action: str, value: Any = None) -> Any:
        """
        Execute an action on this component.
        
        Args:
            action: The action to execute
            value: The value to use for the action
            
        Returns:
            Any: The result of the action
            
        Raises:
            ValueError: If the action is not supported
        """
        method_name = f"action_{action}"
        if not hasattr(self, method_name):
            raise ValueError(f"Unsupported action '{action}' for component {self.component_id}")
        
        method = getattr(self, method_name)
        return method(value)
    
    def list_actions(self) -> List[str]:
        """
        List all available actions for this component.
        
        Returns:
            List[str]: List of available actions
        """
        actions = []
        for name in dir(self):
            if name.startswith("action_"):
                actions.append(name[7:])  # Remove "action_" prefix
        return actions
    
    def get_action_info(self, action: str) -> Dict[str, Any]:
        """
        Get information about an action.
        
        Args:
            action: The action name
            
        Returns:
            Dict[str, Any]: Information about the action
            
        Raises:
            ValueError: If the action is not supported
        """
        method_name = f"action_{action}"
        if not hasattr(self, method_name):
            raise ValueError(f"Unsupported action '{action}' for component {self.component_id}")
        
        method = getattr(self, method_name)
        return {
            "name": action,
            "doc": method.__doc__ or "",
            "component_id": self.component_id,
            "component_type": self.type
        }


class AxisComponent(Component):
    """
    Component representing a machine axis.
    
    Provides actions for moving and homing axes.
    """
    
    def action_move(self, value: Union[int, float]) -> Any:
        """
        Move the axis to a specific position.
        
        Args:
            value: The position to move to
            
        Returns:
            Any: The result of the operation
        """
        axis = self.id
        return self.machine.send_gcode(f"G1 {axis}{value}")
    
    def action_home(self, value: Any = None) -> Any:
        """
        Home the axis.
        
        Args:
            value: Ignored
            
        Returns:
            Any: The result of the operation
        """
        axis = self.id
        return self.machine.send_gcode(f"G28 {axis}")
    
    def action_relative_move(self, value: Union[int, float]) -> Any:
        """
        Move the axis by a relative amount.
        
        Args:
            value: The amount to move by
            
        Returns:
            Any: The result of the operation
        """
        axis = self.id
        return self.machine.send_gcode(f"G91\nG1 {axis}{value}\nG90")


class FanComponent(Component):
    """
    Component representing a fan or similar PWM-controlled output.
    
    Provides actions for controlling fan speed.
    """
    
    def action_set(self, value: Union[int, float]) -> Any:
        """
        Set the fan value (0-255).
        
        Args:
            value: The fan value (0-255)
            
        Returns:
            Any: The result of the operation
        """
        fan_num = self.id
        return self.machine.send_gcode(f"M106 P{fan_num} S{value}")
    
    def action_off(self, value: Any = None) -> Any:
        """
        Turn the fan off.
        
        Args:
            value: Ignored
            
        Returns:
            Any: The result of the operation
        """
        fan_num = self.id
        return self.machine.send_gcode(f"M106 P{fan_num} S0")
    
    def action_on(self, value: Any = None) -> Any:
        """
        Turn the fan on at full speed.
        
        Args:
            value: Ignored
            
        Returns:
            Any: The result of the operation
        """
        fan_num = self.id
        return self.machine.send_gcode(f"M106 P{fan_num} S255")


class ToolComponent(Component):
    """
    Component representing a tool.
    
    Provides actions for selecting tools and setting temperatures.
    """
    
    def action_select(self, value: Any = None) -> Any:
        """
        Select this tool.
        
        Args:
            value: Ignored
            
        Returns:
            Any: The result of the operation
        """
        tool_num = self.id
        return self.machine.send_gcode(f"T{tool_num}")
    
    def action_set_temp(self, value: Union[int, float]) -> Any:
        """
        Set the tool temperature.
        
        Args:
            value: The temperature to set
            
        Returns:
            Any: The result of the operation
        """
        tool_num = self.id
        return self.machine.send_gcode(f"M104 T{tool_num} S{value}")
    
    def action_wait_temp(self, value: Union[int, float]) -> Any:
        """
        Set the tool temperature and wait for it to be reached.
        
        Args:
            value: The temperature to set
            
        Returns:
            Any: The result of the operation
        """
        tool_num = self.id
        return self.machine.send_gcode(f"M109 T{tool_num} S{value}")


class HeaterComponent(Component):
    """
    Component representing a heater.
    
    Provides actions for controlling heater temperature.
    """
    
    def action_set_temp(self, value: Union[int, float]) -> Any:
        """
        Set the heater temperature.
        
        Args:
            value: The temperature to set
            
        Returns:
            Any: The result of the operation
        """
        heater_num = self.id
        return self.machine.send_gcode(f"M140 H{heater_num} S{value}")
    
    def action_wait_temp(self, value: Union[int, float]) -> Any:
        """
        Set the heater temperature and wait for it to be reached.
        
        Args:
            value: The temperature to set
            
        Returns:
            Any: The result of the operation
        """
        heater_num = self.id
        return self.machine.send_gcode(f"M190 H{heater_num} S{value}")
    
    def action_off(self, value: Any = None) -> Any:
        """
        Turn the heater off.
        
        Args:
            value: Ignored
            
        Returns:
            Any: The result of the operation
        """
        heater_num = self.id
        return self.machine.send_gcode(f"M140 H{heater_num} S0")


class ComponentRegistry:
    """
    Registry of available machine components.
    
    This class provides methods for registering and managing machine components.
    """
    
    def __init__(self):
        """Initialize an empty component registry."""
        self.components: Dict[str, Component] = {}
        self._component_types: Dict[str, Type[Component]] = {
            "axis": AxisComponent,
            "fan": FanComponent,
            "tool": ToolComponent,
            "heater": HeaterComponent
        }
    
    def register_component(self, component_id: str, component: Component) -> None:
        """
        Register a component with the registry.
        
        Args:
            component_id: The component ID
            component: The component instance
        """
        self.components[component_id] = component
    
    def get_component(self, component_id: str) -> Component:
        """
        Get a component by ID.
        
        Args:
            component_id: The component ID
            
        Returns:
            Component: The component instance
            
        Raises:
            ValueError: If the component is not found
        """
        if component_id not in self.components:
            raise ValueError(f"Component not found: {component_id}")
        return self.components[component_id]
    
    def list_components(self) -> List[str]:
        """
        List all registered components.
        
        Returns:
            List[str]: List of component IDs
        """
        return list(self.components.keys())
    
    def get_components_by_type(self, component_type: str) -> Dict[str, Component]:
        """
        Get all components of a specific type.
        
        Args:
            component_type: The component type
            
        Returns:
            Dict[str, Component]: Dictionary of component IDs to components
        """
        return {
            component_id: component
            for component_id, component in self.components.items()
            if component.type == component_type
        }
    
    def register_component_type(self, type_name: str, component_class: Type[Component]) -> None:
        """
        Register a new component type.
        
        Args:
            type_name: The component type name
            component_class: The component class
        """
        self._component_types[type_name] = component_class
    
    def create_component(self, component_id: str, machine: Any, config: Optional[Dict[str, Any]] = None) -> Component:
        """
        Create a new component instance.
        
        Args:
            component_id: The component ID
            machine: The machine controller
            config: Optional configuration for the component
            
        Returns:
            Component: The new component instance
            
        Raises:
            ValueError: If the component type is not registered
        """
        parts = component_id.split(':', 1)
        if len(parts) < 2:
            # Generic component
            return Component(component_id, machine, config)
        
        component_type = parts[0]
        if component_type not in self._component_types:
            raise ValueError(f"Unknown component type: {component_type}")
        
        component_class = self._component_types[component_type]
        return component_class(component_id, machine, config) 