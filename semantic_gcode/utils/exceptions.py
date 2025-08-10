"""
Custom exceptions for the Semantic G-code SDK.
"""


class GCodeError(Exception):
    """Base exception for all G-code related errors."""
    pass


class TransportError(GCodeError):
    """Exception raised for errors in the transport layer."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.details = details or {}


class ConnectionError(TransportError):
    """Exception raised for connection-related issues."""
    pass


class TimeoutError(TransportError):
    """Exception raised when an operation times out."""
    pass


class AuthenticationError(ConnectionError):
    """Exception raised when authentication fails."""
    pass


class CommandError(GCodeError):
    """Exception raised for errors related to command execution."""
    pass


class InvalidCommandError(CommandError):
    """Exception raised for invalid or unsupported G-code commands."""
    pass


class ExecutionFailedError(CommandError):
    """Exception raised when a command execution fails."""
    pass


class StateError(GCodeError):
    """Exception raised when the machine state is unknown or inconsistent."""
    pass


class OperationError(GCodeError):
    """Exception raised when a high-level operation fails."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.details = details or {}


class ConfigurationError(GCodeError):
    """Exception raised for errors related to machine configuration."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.details = details or {}
