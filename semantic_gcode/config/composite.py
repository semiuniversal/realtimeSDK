"""
Composite function implementation.

This module provides classes for creating and managing composite functions,
which combine multiple component operations into high-level, semantically
meaningful operations.
"""
from typing import Dict, Any, List, Optional, Union, Callable, Tuple, Set
import re

from .component import Component, ComponentRegistry


class CompositeFunction:
    """
    A function composed of multiple component operations.
    
    Composite functions allow creating high-level, semantically meaningful
    operations by combining multiple low-level hardware operations.
    """
    
    def __init__(self, name: str, machine: Any, config: Dict[str, Any]):
        """
        Initialize a composite function.
        
        Args:
            name: The function name
            machine: The machine controller
            config: The function configuration
        """
        self.name = name
        self.machine = machine
        self.config = config
        self.description = config.get("description", "")
        self.components = config.get("components", [])
        self.operations = config.get("operations", {})
    
    def __getattr__(self, name: str) -> Callable:
        """
        Allow dynamic access to defined operations.
        
        Args:
            name: The operation name
            
        Returns:
            Callable: A function that executes the operation
            
        Raises:
            AttributeError: If the operation is not defined
        """
        if name in self.operations:
            # Return a function that executes this operation
            return lambda *args: self._execute_operation(name, args)
        
        # Not found
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")
    
    def _execute_operation(self, operation: str, args: Tuple[Any, ...]) -> List[Any]:
        """
        Execute a defined operation.
        
        Args:
            operation: The operation name
            args: The operation arguments
            
        Returns:
            List[Any]: The results of the operation steps
            
        Raises:
            ValueError: If the operation is not defined
        """
        if operation not in self.operations:
            raise ValueError(f"Operation '{operation}' not defined for '{self.name}'")
        
        steps = self.operations[operation]
        results = []
        
        for step in steps:
            component_id = step["component"]
            action = step.get("action", "set")
            value = step.get("value")
            
            # Handle parameter substitution
            if isinstance(value, str) and "PARAM" in value:
                if not args:
                    raise ValueError(f"Operation '{operation}' requires parameters but none provided")
                
                # Simple parameter substitution
                if value == "PARAM":
                    value = args[0]
                elif value == "PARAM2":
                    if len(args) < 2:
                        raise ValueError(f"Operation '{operation}' requires at least 2 parameters")
                    value = args[1]
                elif value.startswith("PARAM2 "):
                    # Expression with second parameter
                    if len(args) < 2:
                        raise ValueError(f"Operation '{operation}' requires at least 2 parameters")
                    expr = value[7:]  # Get the expression after "PARAM2 "
                    try:
                        value = eval(f"{args[1]}{expr}")
                    except Exception as e:
                        raise ValueError(f"Error evaluating expression '{value}': {str(e)}") from e
                else:
                    # Handle numbered parameters (PARAM, PARAM2, PARAM3, etc.)
                    for i, arg in enumerate(args):
                        param_name = f"PARAM{i+1}" if i > 0 else "PARAM"
                        if param_name in value:
                            # Replace the parameter name with its string representation
                            value = value.replace(param_name, str(arg))
                    
                    # Evaluate expressions like "PARAM * 0.01"
                    if re.search(r'[+\-*/]', value):
                        try:
                            value = eval(value)
                        except Exception as e:
                            raise ValueError(f"Error evaluating expression '{value}': {str(e)}") from e
            
            # Execute the component action
            component = self.machine.get_component(component_id)
            result = component.execute_action(action, value)
            results.append(result)
        
        return results
    
    def list_operations(self) -> List[str]:
        """
        List all available operations.
        
        Returns:
            List[str]: List of operation names
        """
        return list(self.operations.keys())
    
    def get_operation_info(self, operation: str) -> Dict[str, Any]:
        """
        Get information about an operation.
        
        Args:
            operation: The operation name
            
        Returns:
            Dict[str, Any]: Information about the operation
            
        Raises:
            ValueError: If the operation is not defined
        """
        if operation not in self.operations:
            raise ValueError(f"Operation '{operation}' not defined for '{self.name}'")
        
        steps = self.operations[operation]
        return {
            "name": operation,
            "steps": len(steps),
            "components": [step["component"] for step in steps],
            "description": next((step.get("description") for step in steps if "description" in step), None)
        }
    
    def get_operation_steps(self, operation: str) -> List[Dict[str, Any]]:
        """
        Get the steps for an operation.
        
        Args:
            operation: The operation name
            
        Returns:
            List[Dict[str, Any]]: The operation steps
            
        Raises:
            ValueError: If the operation is not defined
        """
        if operation not in self.operations:
            raise ValueError(f"Operation '{operation}' not defined for '{self.name}'")
        
        return self.operations[operation]
    
    def validate(self, registry: ComponentRegistry) -> List[str]:
        """
        Validate the composite function.
        
        Args:
            registry: The component registry
            
        Returns:
            List[str]: List of validation errors, empty if valid
        """
        errors = []
        
        # Check that all components exist
        for component_id in self.components:
            try:
                registry.get_component(component_id)
            except ValueError:
                errors.append(f"Component '{component_id}' not found in registry")
        
        # Check that all operation steps reference valid components
        for operation, steps in self.operations.items():
            for i, step in enumerate(steps):
                component_id = step.get("component")
                if not component_id:
                    errors.append(f"Step {i} in operation '{operation}' has no component")
                    continue
                
                try:
                    component = registry.get_component(component_id)
                except ValueError:
                    errors.append(f"Component '{component_id}' in operation '{operation}' step {i} not found in registry")
                    continue
                
                # Check that the action is valid for the component
                action = step.get("action", "set")
                if f"action_{action}" not in dir(component):
                    errors.append(f"Action '{action}' in operation '{operation}' step {i} not supported by component '{component_id}'")
        
        return errors


class CompositeFunctionRegistry:
    """
    Registry of composite functions.
    
    This class provides methods for registering and managing composite functions.
    """
    
    def __init__(self, machine: Any):
        """
        Initialize a composite function registry.
        
        Args:
            machine: The machine controller
        """
        self.machine = machine
        self.functions: Dict[str, CompositeFunction] = {}
    
    def register_function(self, name: str, config: Dict[str, Any]) -> CompositeFunction:
        """
        Register a composite function.
        
        Args:
            name: The function name
            config: The function configuration
            
        Returns:
            CompositeFunction: The created function
        """
        function = CompositeFunction(name, self.machine, config)
        self.functions[name] = function
        return function
    
    def get_function(self, name: str) -> CompositeFunction:
        """
        Get a composite function by name.
        
        Args:
            name: The function name
            
        Returns:
            CompositeFunction: The composite function
            
        Raises:
            ValueError: If the function is not found
        """
        if name not in self.functions:
            raise ValueError(f"Composite function not found: {name}")
        return self.functions[name]
    
    def list_functions(self) -> List[str]:
        """
        List all registered composite functions.
        
        Returns:
            List[str]: List of function names
        """
        return list(self.functions.keys())
    
    def validate_all(self, registry: ComponentRegistry) -> Dict[str, List[str]]:
        """
        Validate all composite functions.
        
        Args:
            registry: The component registry
            
        Returns:
            Dict[str, List[str]]: Dictionary mapping function names to validation errors
        """
        errors = {}
        for name, function in self.functions.items():
            function_errors = function.validate(registry)
            if function_errors:
                errors[name] = function_errors
        return errors 