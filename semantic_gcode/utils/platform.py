"""
Platform detection and OS-specific utilities.

This module provides utilities for detecting the operating system and
handling platform-specific functionality, particularly for serial port access.
"""
import os
import platform
import sys
from enum import Enum
from typing import List, Optional


class PlatformType(Enum):
    """Enum representing supported platform types."""
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    WSL = "wsl"  # Windows Subsystem for Linux
    UNKNOWN = "unknown"


def get_platform() -> PlatformType:
    """
    Detect the current platform.
    
    Returns:
        PlatformType: The detected platform type
    """
    system = platform.system().lower()
    
    if system == "linux":
        # Check if running in WSL
        if os.path.exists("/proc/version"):
            with open("/proc/version", "r") as f:
                if "microsoft" in f.read().lower():
                    return PlatformType.WSL
        return PlatformType.LINUX
    elif system == "darwin":
        return PlatformType.MACOS
    elif system == "windows":
        return PlatformType.WINDOWS
    else:
        return PlatformType.UNKNOWN


def list_serial_ports() -> List[str]:
    """
    List available serial ports on the current platform.
    
    Returns:
        List[str]: List of available serial ports
    """
    try:
        import serial.tools.list_ports
        return [port.device for port in serial.tools.list_ports.comports()]
    except ImportError:
        print("pyserial is not installed. Install it with 'pip install pyserial'")
        return []
    except Exception as e:
        print(f"Error listing serial ports: {e}")
        return []


def get_serial_port_for_wsl(windows_port: str) -> str:
    """
    Convert a Windows serial port name to the corresponding WSL device.
    
    Args:
        windows_port: Windows port name (e.g., "COM3")
        
    Returns:
        str: WSL device path (e.g., "/dev/ttyS3")
    """
    # Extract the number from the COM port
    try:
        port_num = int(''.join(filter(str.isdigit, windows_port)))
        return f"/dev/ttyS{port_num - 1}"  # COM3 -> /dev/ttyS2
    except (ValueError, TypeError):
        return ""


def is_serial_available() -> bool:
    """
    Check if serial port access is available on the current platform.
    
    Returns:
        bool: True if serial port access is available, False otherwise
    """
    try:
        import serial
        return True
    except ImportError:
        return False


def get_default_serial_port() -> Optional[str]:
    """
    Get the default serial port for the current platform.
    
    Returns:
        Optional[str]: Default serial port, or None if no ports are available
    """
    ports = list_serial_ports()
    
    if not ports:
        return None
    
    platform_type = get_platform()
    
    # For WSL, we need special handling
    if platform_type == PlatformType.WSL:
        # Try to find a valid WSL serial port
        for i in range(10):  # Check ttyS0 through ttyS9
            port = f"/dev/ttyS{i}"
            if os.path.exists(port):
                return port
    
    # For other platforms, return the first available port
    return ports[0] 