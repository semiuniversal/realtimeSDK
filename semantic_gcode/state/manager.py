"""
State management system for the Semantic G-code SDK.

This module provides the StateManager class, which is responsible for tracking
and validating machine state across operations.
"""
from typing import Dict, Any, Optional, List, Type, TypeVar, Generic, Union
import copy
import logging

from .domains import (
    StateDomain,
    MotionState,
    ToolState,
    TemperatureState,
    CoordinateState,
    IOState
)

# Set up logging
logger = logging.getLogger(__name__)


class StateManager:
    """
    Manages machine state across multiple domains.
    
    The StateManager is responsible for tracking the current state of the machine,
    validating instructions against that state, and updating the state when
    instructions are executed.
    
    It organizes state into domains (motion, tool, temperature, etc.) and provides
    methods for pushing/popping state for context management.
    """
    
    def __init__(self):
        """Initialize state manager with default domains."""
        # Initialize state domains
        self.motion = MotionState()
        self.tool = ToolState()
        self.temperature = TemperatureState()
        self.coordinate = CoordinateState()
        self.io = IOState()
        
        # Stack for push/pop operations
        self._state_stack: List[Dict[str, Any]] = []
        
        # Map of domain names to domain objects
        self._domains = {
            'motion': self.motion,
            'tool': self.tool,
            'temperature': self.temperature,
            'coordinate': self.coordinate,
            'io': self.io
        }
        
        logger.debug("StateManager initialized with default domains")
    
    def validate(self, instruction: Any) -> bool:
        """
        Validate if an instruction can be executed in the current state.
        
        This method checks if the instruction can be executed given the current
        state of all domains. It delegates to the validate() method of each domain.
        
        Args:
            instruction: The instruction to validate
            
        Returns:
            bool: True if the instruction can be executed, False otherwise
        """
        # If the instruction has its own validate_state method, use that
        if hasattr(instruction, 'validate_state'):
            return instruction.validate_state(self)
        
        # Otherwise, check with each domain
        for domain in self._domains.values():
            if not domain.validate(instruction):
                return False
        
        return True
    
    def apply(self, instruction: Any) -> None:
        """
        Apply an instruction to update the current state.
        
        This method updates the state of all domains based on the instruction.
        It delegates to the apply_to_state() method of the instruction.
        
        Args:
            instruction: The instruction to apply
        """
        # If the instruction has its own apply_to_state method, use that
        if hasattr(instruction, 'apply_to_state'):
            instruction.apply_to_state(self)
            logger.debug(f"Applied instruction {instruction} to state")
    
    def push(self) -> Dict[str, Any]:
        """
        Push current state onto stack.
        
        This method saves the current state to the stack so it can be restored later.
        
        Returns:
            Dict[str, Any]: The serialized state that was pushed
        """
        state_copy = self.serialize()
        self._state_stack.append(state_copy)
        logger.debug("Pushed state to stack")
        return state_copy
    
    def pop(self) -> Dict[str, Any]:
        """
        Pop state from stack and restore it.
        
        This method restores the state from the top of the stack.
        
        Returns:
            Dict[str, Any]: The serialized state that was popped
            
        Raises:
            ValueError: If the state stack is empty
        """
        if not self._state_stack:
            raise ValueError("State stack is empty")
        
        state = self._state_stack.pop()
        self.deserialize(state)
        logger.debug("Popped state from stack")
        return state
    
    def get_domain(self, domain_name: str) -> Optional[StateDomain]:
        """
        Get a specific state domain by name.
        
        Args:
            domain_name: The name of the domain to get
            
        Returns:
            StateDomain: The requested domain, or None if not found
        """
        return self._domains.get(domain_name)
    
    def serialize(self) -> Dict[str, Any]:
        """
        Serialize all state domains to a dictionary.
        
        Returns:
            Dict[str, Any]: Serialized state data
        """
        return {
            domain_name: domain.serialize()
            for domain_name, domain in self._domains.items()
        }
    
    def deserialize(self, state_dict: Dict[str, Any]) -> None:
        """
        Restore all state domains from a dictionary.
        
        Args:
            state_dict: Serialized state data
        """
        for domain_name, domain in self._domains.items():
            domain_data = state_dict.get(domain_name, {})
            domain.deserialize(domain_data)
        
        logger.debug("Deserialized state")
    
    def reset(self) -> None:
        """
        Reset all state domains to their default values.
        """
        for domain in self._domains.values():
            domain.reset()
        
        # Clear the state stack
        self._state_stack = []
        
        logger.debug("Reset all state domains")
    
    def __enter__(self) -> 'StateManager':
        """
        Enter a state context by pushing the current state.
        
        Returns:
            StateManager: Self, for use in with statements
        """
        self.push()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit a state context by popping the state.
        
        Args:
            exc_type: Exception type, if an exception was raised
            exc_val: Exception value, if an exception was raised
            exc_tb: Exception traceback, if an exception was raised
        """
        if exc_type is not None:
            logger.warning(f"Exception in state context: {exc_val}")
        
        try:
            self.pop()
        except ValueError:
            logger.error("Failed to pop state: stack is empty")


class StateContext:
    """
    Context manager for scoped state changes.
    
    This class provides a way to make temporary changes to state that are
    automatically reverted when the context is exited.
    
    Example:
        with StateContext(state_manager, motion_positioning_mode="relative"):
            # Do something in relative positioning mode
        # Back to previous positioning mode
    """
    
    def __init__(self, state_manager: StateManager, **kwargs):
        """
        Initialize a state context.
        
        Args:
            state_manager: The state manager to use
            **kwargs: State attributes to temporarily change
        """
        self.state_manager = state_manager
        self.changes = kwargs
        self.original_values = {}
    
    def __enter__(self) -> StateManager:
        """
        Enter the context by applying the specified changes.
        
        Returns:
            StateManager: The state manager with changes applied
        """
        # Save original values and apply changes
        for attr_name, new_value in self.changes.items():
            # Handle domain_attribute format (e.g., motion_positioning_mode)
            if '_' in attr_name:
                domain_name, attr = attr_name.split('_', 1)
                if hasattr(self.state_manager, domain_name):
                    domain = getattr(self.state_manager, domain_name)
                    if hasattr(domain, attr):
                        self.original_values[attr_name] = getattr(domain, attr)
                        setattr(domain, attr, new_value)
                    else:
                        raise AttributeError(f"Domain '{domain_name}' has no attribute '{attr}'")
                else:
                    raise AttributeError(f"StateManager has no domain '{domain_name}'")
            else:
                # Direct attribute of state manager
                if hasattr(self.state_manager, attr_name):
                    self.original_values[attr_name] = getattr(self.state_manager, attr_name)
                    setattr(self.state_manager, attr_name, new_value)
                else:
                    raise AttributeError(f"StateManager has no attribute '{attr_name}'")
        
        return self.state_manager
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit the context by restoring the original values.
        
        Args:
            exc_type: Exception type, if an exception was raised
            exc_val: Exception value, if an exception was raised
            exc_tb: Exception traceback, if an exception was raised
        """
        # Restore original values
        for attr_name, original_value in self.original_values.items():
            # Handle domain_attribute format (e.g., motion_positioning_mode)
            if '_' in attr_name:
                domain_name, attr = attr_name.split('_', 1)
                domain = getattr(self.state_manager, domain_name)
                setattr(domain, attr, original_value)
            else:
                # Direct attribute of state manager
                setattr(self.state_manager, attr_name, original_value)
