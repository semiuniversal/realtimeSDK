"""
Transport layer for G-code communication.

This package provides transport implementations for communicating with G-code devices
using different protocols (HTTP, Serial, Telnet).
"""
from .base import Transport
from .http import HttpTransport

# Import SerialTransport conditionally
try:
    from .serial import SerialTransport, SERIAL_AVAILABLE
except ImportError:
    SERIAL_AVAILABLE = False

__all__ = ['Transport', 'HttpTransport']

# Add SerialTransport to __all__ if available
if SERIAL_AVAILABLE:
    __all__.append('SerialTransport')
