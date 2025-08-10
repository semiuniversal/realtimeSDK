"""
State management system for the Semantic G-code SDK.

This package provides classes for tracking and validating machine state
across operations. It organizes state into domains (motion, tool, temperature, etc.)
and provides methods for pushing/popping state for context management.
"""

from .domains import (
    Position,
    StateDomain,
    MotionState,
    ToolState,
    TemperatureState,
    CoordinateState,
    IOState
)

from .manager import (
    StateManager,
    StateContext
)

__all__ = [
    'Position',
    'StateDomain',
    'MotionState',
    'ToolState',
    'TemperatureState',
    'CoordinateState',
    'IOState',
    'StateManager',
    'StateContext'
]
