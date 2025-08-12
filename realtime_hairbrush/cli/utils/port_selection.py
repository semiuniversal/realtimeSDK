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


def _probe_duet_on_port(port: str, baud: int) -> bool:
    """Probe a single port/baud for a Duet by sending M115 (and fallback M408) and
    scanning responses for RRF fingerprints within a short window.
    """
    try:
        ser = serial.Serial(port, baudrate=baud, timeout=1.0, write_timeout=1.0)
        try:
            # Clear buffers and wake the device
            try:
                ser.reset_input_buffer(); ser.reset_output_buffer()
            except Exception:
                pass
            try:
                ser.dtr = True
            except Exception:
                pass
            ser.write(b"\n"); ser.flush()
            time.sleep(0.1)

            # First attempt: M115
            ser.write(b"M115\n"); ser.flush()
            end = time.time() + 1.8
            buf = ""
            while time.time() < end:
                line = ser.readline().decode(errors='ignore',)
                if line:
                    buf += line
                    low = line.lower()
                    if ("reprapfirmware" in low) or ("firmware_name" in low) or ("electronics:" in low):
                        return True
                    if low.strip() == "ok":
                        # keep reading a bit more in case info preceded ok
                        continue
            # Fallback: try a lightweight object-model query
            ser.write(b"M408 S0\n"); ser.flush()
            end = time.time() + 1.2
            while time.time() < end:
                line = ser.readline().decode(errors='ignore')
                if line:
                    low = line.lower()
                    if ("\"status\"" in low) or ("rrf" in low) or ("reprapfirmware" in low):
                        return True
            return False
        finally:
            try:
                ser.close()
            except Exception:
                pass
    except Exception:
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
        for port_info in ports:
            port = port_info['device']
            for baud in baud_rates:
                if _probe_duet_on_port(port, baud):
                    return port
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