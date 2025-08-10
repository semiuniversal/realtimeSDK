"""
Machine configuration and capability discovery system.

This package provides tools for discovering machine capabilities,
parsing configuration files, and creating machine profiles.
"""

from .alias import AliasSystem, ComponentAlias, CompositeFunction as AliasCompositeFunction
from .profile import MachineProfile
from .parser import ConfigParser
from .interviewer import ConfigurationInterviewer
from .component import Component, ComponentRegistry, AxisComponent, FanComponent, ToolComponent, HeaterComponent
from .composite import CompositeFunction as OperationCompositeFunction
from .composite import CompositeFunctionRegistry
from .controller import MachineController

__all__ = [
    'AliasSystem',
    'ComponentAlias',
    'AliasCompositeFunction',
    'MachineProfile',
    'ConfigParser',
    'ConfigurationInterviewer',
    'Component',
    'ComponentRegistry',
    'AxisComponent',
    'FanComponent',
    'ToolComponent',
    'HeaterComponent',
    'OperationCompositeFunction',
    'CompositeFunctionRegistry',
    'MachineController',
] 