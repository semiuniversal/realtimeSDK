"""
Serial port selection utilities.

This module provides utilities for listing and selecting serial ports
in an interactive manner, with support for different platforms.
"""
import os
import sys
from typing import List, Optional, Dict, Any, Tuple

from .platform import get_platform, PlatformType, get_serial_port_for_wsl

# Try to import pyserial
try:
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False


def get_port_details(port) -> Dict[str, Any]:
    """
    Get detailed information about a serial port.
    
    Args:
        port: A port object from serial.tools.list_ports
        
    Returns:
        Dict[str, Any]: Port details including device, description, hwid, etc.
    """
    details = {
        "device": port.device,
        "description": port.description if hasattr(port, "description") else "Unknown",
        "hwid": port.hwid if hasattr(port, "hwid") else "Unknown",
        "manufacturer": port.manufacturer if hasattr(port, "manufacturer") else "Unknown",
        "product": port.product if hasattr(port, "product") else "Unknown",
        "vid": getattr(port, "vid", None),
        "pid": getattr(port, "pid", None),
        "serial_number": getattr(port, "serial_number", None),
    }
    return details


def list_available_ports() -> List[Dict[str, Any]]:
    """
    List all available serial ports with detailed information.
    
    Returns:
        List[Dict[str, Any]]: List of port details
    """
    if not SERIAL_AVAILABLE:
        return []
    
    try:
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append(get_port_details(port))
        return ports
    except Exception as e:
        print(f"Error listing serial ports: {e}")
        return []


def filter_ports_by_vid_pid(ports: List[Dict[str, Any]], vid: int, pid: int) -> List[Dict[str, Any]]:
    """
    Filter ports by vendor ID and product ID.
    
    Args:
        ports: List of port details
        vid: Vendor ID
        pid: Product ID
        
    Returns:
        List[Dict[str, Any]]: Filtered list of port details
    """
    return [port for port in ports if port["vid"] == vid and port["pid"] == pid]


def filter_ports_by_description(ports: List[Dict[str, Any]], description: str) -> List[Dict[str, Any]]:
    """
    Filter ports by description (case-insensitive substring match).
    
    Args:
        ports: List of port details
        description: Description to match
        
    Returns:
        List[Dict[str, Any]]: Filtered list of port details
    """
    description = description.lower()
    return [port for port in ports if description in port["description"].lower()]


def print_port_details(port: Dict[str, Any], index: Optional[int] = None) -> None:
    """
    Print details of a serial port.
    
    Args:
        port: Port details
        index: Optional index for listing
    """
    prefix = f"{index}. " if index is not None else ""
    print(f"{prefix}Device: {port['device']}")
    print(f"   Description: {port['description']}")
    print(f"   Hardware ID: {port['hwid']}")
    
    if port['manufacturer'] != "Unknown":
        print(f"   Manufacturer: {port['manufacturer']}")
    
    if port['product'] != "Unknown":
        print(f"   Product: {port['product']}")
    
    if port['vid'] is not None and port['pid'] is not None:
        print(f"   VID:PID: {port['vid']:04X}:{port['pid']:04X}")


def interactive_port_selection(
    prompt: str = "Select a serial port",
    filter_vid: Optional[int] = None,
    filter_pid: Optional[int] = None,
    filter_description: Optional[str] = None,
    default_port: Optional[str] = None
) -> Optional[str]:
    """
    Interactively select a serial port.
    
    Args:
        prompt: Prompt to display
        filter_vid: Optional vendor ID filter
        filter_pid: Optional product ID filter
        filter_description: Optional description filter
        default_port: Optional default port to suggest
        
    Returns:
        Optional[str]: Selected port device, or None if no port was selected
    """
    if not SERIAL_AVAILABLE:
        print("pyserial is not installed. Cannot list serial ports.")
        return None
    
    # Get available ports
    ports = list_available_ports()
    
    if not ports:
        print("No serial ports found.")
        return None
    
    # Apply filters if specified
    if filter_vid is not None and filter_pid is not None:
        filtered_ports = filter_ports_by_vid_pid(ports, filter_vid, filter_pid)
        if filtered_ports:
            print(f"Found {len(filtered_ports)} ports matching VID:PID {filter_vid:04X}:{filter_pid:04X}")
            ports = filtered_ports
    
    if filter_description is not None:
        filtered_ports = filter_ports_by_description(ports, filter_description)
        if filtered_ports:
            print(f"Found {len(filtered_ports)} ports matching description '{filter_description}'")
            ports = filtered_ports
    
    # Handle WSL-specific port mapping
    platform_type = get_platform()
    if platform_type == PlatformType.WSL:
        print("\nRunning in Windows Subsystem for Linux (WSL)")
        print("Note: Windows COM ports are mapped to /dev/ttyS* devices in WSL")
        print("Example: COM3 -> /dev/ttyS2")
    
    # Display available ports
    print(f"\n{prompt} (found {len(ports)}):")
    for i, port in enumerate(ports):
        print_port_details(port, i + 1)
        print("")  # Empty line between ports
    
    # Suggest default port if available
    default_index = None
    if default_port:
        for i, port in enumerate(ports):
            if port["device"] == default_port:
                default_index = i + 1
                break
    
    # Get user selection
    try:
        if default_index:
            selection = input(f"Enter port number (1-{len(ports)}) or press Enter for default [{default_index}]: ")
            if not selection:
                selection = str(default_index)
        else:
            selection = input(f"Enter port number (1-{len(ports)}): ")
        
        if selection.isdigit() and 1 <= int(selection) <= len(ports):
            selected_port = ports[int(selection) - 1]
            print(f"Selected: {selected_port['device']} - {selected_port['description']}")
            return selected_port["device"]
        else:
            print("Invalid selection.")
            return None
    except (ValueError, IndexError, KeyboardInterrupt):
        print("\nPort selection cancelled.")
        return None


def select_port_for_device(
    device_name: str,
    known_devices: Dict[str, Tuple[int, int, str]] = None
) -> Optional[str]:
    """
    Select a port for a specific device based on known VID/PID combinations.
    
    Args:
        device_name: Name of the device
        known_devices: Dictionary mapping device names to (VID, PID, description) tuples
        
    Returns:
        Optional[str]: Selected port device, or None if no port was selected
    """
    if known_devices is None:
        # Default known devices
        known_devices = {
            "duet2": (0x1D50, 0x60EC, "Duet"),  # Duet 2 WiFi/Ethernet
            "duet3": (0x1D50, 0x60ED, "Duet"),  # Duet 3
            "arduino": (0x2341, 0x0043, "Arduino"),  # Arduino Uno
            "teensy": (0x16C0, 0x0483, "Teensy"),  # Teensy
        }
    
    if device_name.lower() not in known_devices:
        print(f"Unknown device: {device_name}")
        return interactive_port_selection(f"Select a port for {device_name}")
    
    vid, pid, description = known_devices[device_name.lower()]
    
    print(f"Looking for {device_name} (VID:PID {vid:04X}:{pid:04X}, Description: {description})...")
    
    ports = list_available_ports()
    filtered_ports = filter_ports_by_vid_pid(ports, vid, pid)
    
    if not filtered_ports and description:
        print(f"No ports found with VID:PID {vid:04X}:{pid:04X}, trying description match...")
        filtered_ports = filter_ports_by_description(ports, description)
    
    if len(filtered_ports) == 1:
        port = filtered_ports[0]
        print(f"Found single matching port: {port['device']} - {port['description']}")
        confirm = input("Use this port? (Y/n): ")
        if confirm.lower() != "n":
            return port["device"]
    
    return interactive_port_selection(
        f"Select a port for {device_name}",
        filter_vid=vid,
        filter_pid=pid,
        filter_description=description
    )


if __name__ == "__main__":
    # Example usage
    port = interactive_port_selection()
    if port:
        print(f"You selected: {port}")
    else:
        print("No port selected.") 