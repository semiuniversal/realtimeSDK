"""
Port selection utilities for the Realtime Hairbrush SDK.

This module provides functions for selecting serial ports, with support for
auto-detecting specific devices like Duet boards.
"""

import sys
import time
from typing import Optional, List, Dict, Any

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False


def get_available_ports() -> List[Dict[str, Any]]:
    """
    Get a list of available serial ports with detailed information.
    
    Returns:
        List[Dict[str, Any]]: List of dictionaries containing port information
    """
    if not SERIAL_AVAILABLE:
        return []
    
    ports = []
    for port in serial.tools.list_ports.comports():
        port_info = {
            'device': port.device,
            'name': port.name,
            'description': port.description,
            'hwid': port.hwid,
            'vid': port.vid,
            'pid': port.pid,
            'serial_number': port.serial_number,
            'manufacturer': port.manufacturer,
            'product': port.product,
            'interface': getattr(port, 'interface', None),
        }
        ports.append(port_info)
    
    return ports


def is_duet_board(port_info: Dict[str, Any]) -> bool:
    """
    Check if a port is likely to be a Duet board.
    
    Args:
        port_info: Dictionary containing port information
    
    Returns:
        bool: True if the port is likely a Duet board, False otherwise
    """
    # Check for common Duet board identifiers
    description = str(port_info.get('description', '') or '').lower()
    manufacturer = str(port_info.get('manufacturer', '') or '').lower()
    product = str(port_info.get('product', '') or '').lower()
    
    # Duet 2 typically uses FTDI chips
    if 'ftdi' in description or 'ftdi' in manufacturer:
        return True
    
    # Duet 3 uses different USB identifiers
    if 'duet' in description or 'duet' in product:
        return True
    
    # Check for specific VID/PID combinations
    # FTDI VID is 0x0403, Duet 3 uses different VIDs
    vid = port_info.get('vid')
    if vid == 0x0403:  # FTDI
        return True
    
    return False


def is_arduino(port_info: Dict[str, Any]) -> bool:
    """
    Check if a port is likely to be an Arduino.
    
    Args:
        port_info: Dictionary containing port information
    
    Returns:
        bool: True if the port is likely an Arduino, False otherwise
    """
    description = str(port_info.get('description', '') or '').lower()
    manufacturer = str(port_info.get('manufacturer', '') or '').lower()
    product = str(port_info.get('product', '') or '').lower()
    
    if 'arduino' in description or 'arduino' in manufacturer or 'arduino' in product:
        return True
    
    # Arduino UNO uses ATmega16U2
    if 'atmega' in description:
        return True
    
    # Check for Arduino VID (0x2341)
    vid = port_info.get('vid')
    if vid == 0x2341:  # Arduino
        return True
    
    return False


def select_port_for_device(device_type: str) -> Optional[str]:
    """
    Auto-select a port for a specific device type using probe-and-parse detection for Duet.
    
    Args:
        device_type: Type of device to select ('duet2', 'duet3', 'duet', 'arduino')
        
    Returns:
        Optional[str]: Selected port or None if no matching port found
    """
    if not SERIAL_AVAILABLE:
        print("Error: pyserial is not installed.")
        return None
    
    ports = get_available_ports()
    if not ports:
        print("No serial ports found.")
        return None
    
    # For Duet, probe each port
    if device_type.lower() in ("duet2", "duet3", "duet"):
        # Try standard baud rates in descending order (highest first)
        baud_rates = [115200, 57600, 38400, 19200, 9600]
        
        # Try to import the M115 command class
        try:
            from semantic_gcode.dict.gcode_commands.M115.M115 import M115_GetFirmwareInfo
            m115_cmd = M115_GetFirmwareInfo.create()
            use_m115_class = True
        except ImportError:
            # Fall back to simple string if class not available
            m115_cmd = "M115"
            use_m115_class = False
        
        for port_info in ports:
            port = port_info['device']
            
            for baud in baud_rates:
                try:
                    ser = serial.Serial(port, baudrate=baud, timeout=2)
                    ser.reset_input_buffer()
                    time.sleep(0.2)
                    
                    # Send M115 to check if it's a Duet board
                    ser.write(f"{str(m115_cmd)}\n".encode())
                    ser.flush()
                    time.sleep(0.3)
                    
                    response = ""
                    for _ in range(3):  # Read a few lines to get the complete response
                        line = ser.readline().decode(errors='ignore').strip()
                        if line:
                            response += line + "\n"
                    
                    ser.close()
                    
                    # Check if the response indicates a Duet board
                    resp_lower = response.lower()
                    if use_m115_class:
                        try:
                            info = m115_cmd.parse_info(response)
                        except Exception:
                            info = {}
                        if (
                            (info.get("firmware_name", "").lower().find("reprapfirmware") != -1)
                            or ("duet" in info.get("electronics", "").lower())
                            or ("duet" in resp_lower)
                            or ("firmware_name" in resp_lower)
                        ):
                            return port
                    else:
                        if any(s in resp_lower for s in ["reprapfirmware", "duet", "firmware_name"]):
                            return port
                        
                except Exception:
                    # Just silently continue to the next baud rate or port
                    pass
        
        # If we get here, no Duet board was found
        return None
    
    # For Arduino, use legacy logic
    matching_ports = []
    for port_info in ports:
        if device_type.lower() == 'arduino' and is_arduino(port_info):
            matching_ports.append(port_info)
    
    if not matching_ports:
        return None
    
    if len(matching_ports) == 1:
        return matching_ports[0]['device']
    
    # If multiple Arduino devices found, let the user choose
    print(f"Multiple {device_type} devices found. Please select one:")
    for i, port_info in enumerate(matching_ports):
        print(f"{i+1}. {port_info['device']} - {port_info['description']}")
    
    try:
        choice = input("Enter choice (or 'c' to cancel): ")
        if choice.lower() == 'c':
            return None
        index = int(choice) - 1
        if 0 <= index < len(matching_ports):
            return matching_ports[index]['device']
        else:
            print("Invalid choice.")
            return None
    except (ValueError, IndexError):
        print("Invalid selection.")
        return None


def interactive_port_selection() -> Optional[str]:
    """
    Interactively select a serial port from a list of available ports.
    
    Returns:
        Optional[str]: Selected port or None if no port selected
    """
    if not SERIAL_AVAILABLE:
        print("Error: pyserial is not installed.")
        return None
    
    ports = get_available_ports()
    if not ports:
        print("No serial ports found.")
        return None
    
    print("\nAvailable serial ports:")
    for i, port_info in enumerate(ports):
        device_type = ""
        if is_duet_board(port_info):
            device_type = " (Duet)"
        elif is_arduino(port_info):
            device_type = " (Arduino)"
        
        # Ensure description is not None before calling lower()
        description = port_info.get('description', '')
        if description is None:
            description = ''
        
        print(f"{i+1}. {port_info['device']} - {description}{device_type}")
    
    try:
        choice = input("\nEnter port number (or 'c' to cancel): ")
        if choice.lower() == 'c':
            return None
        
        index = int(choice) - 1
        if 0 <= index < len(ports):
            return ports[index]['device']
        else:
            print("Invalid choice.")
            return None
    except (ValueError, IndexError):
        print("Invalid selection.")
        return None


def test_port_connection(port: str, baud_rate: int = 115200, timeout: float = 2.0) -> bool:
    """
    Test if a connection can be established with the specified port.
    
    Args:
        port: Serial port to test
        baud_rate: Baud rate to use
        timeout: Connection timeout in seconds
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    if not SERIAL_AVAILABLE:
        return False
    
    try:
        ser = serial.Serial(port, baud_rate, timeout=timeout)
        ser.close()
        return True
    except Exception:
        return False 