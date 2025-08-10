"""
Utility modules for the Semantic G-code SDK.
"""
from . import platform
from . import port_selection
from .exceptions import (
    GCodeError, TransportError, ConnectionError, TimeoutError,
    AuthenticationError, CommandError, InvalidCommandError,
    ExecutionFailedError, StateError
)

__all__ = [
    'platform',
    'port_selection',
    'GCodeError',
    'TransportError',
    'ConnectionError',
    'TimeoutError',
    'AuthenticationError',
    'CommandError',
    'InvalidCommandError',
    'ExecutionFailedError',
    'StateError'
]
