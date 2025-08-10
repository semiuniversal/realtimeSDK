"""
Utility functions for Duet board configuration.

This module provides helper functions for configuring Duet boards,
particularly focused on network setup and board detection.
"""
import re
import time
import json
from typing import Dict, Any, List, Optional, Tuple, Union

# Import will be resolved when the module is used
# Avoid circular imports by using string type annotations
from ..transport.serial import SerialTransport
from ..gcode.network import SetNetworkState, ConfigureWiFiSettings


def scan_for_duet_boards() -> List[Dict[str, Any]]:
    """
    Scan for Duet boards connected via serial.
    
    Returns:
        List[Dict[str, Any]]: List of dictionaries with board information
    """
    duet_boards = []
    
    try:
        from ..transport.serial import SerialTransport
        available_ports = SerialTransport.list_ports()
        
        for port in available_ports:
            try:
                # Try to connect and detect Duet
                transport = SerialTransport(port=port, auto_detect_board=True)
                if transport.connect():
                    # Check if it's a Duet board
                    if transport.is_duet:
                        board_info = {
                            "port": port,
                            "firmware_name": transport.firmware_name,
                            "firmware_version": transport.firmware_version,
                            "board_type": transport.board_type
                        }
                        duet_boards.append(board_info)
                    transport.disconnect()
            except Exception as e:
                print(f"Error checking port {port}: {str(e)}")
                continue
    except ImportError:
        print("pyserial is required for scanning Duet boards")
    
    return duet_boards


def detect_duet_board(transport: 'SerialTransport') -> Dict[str, str]:
    """
    Detect if a transport is connected to a Duet board.
    
    Args:
        transport: A connected SerialTransport instance
        
    Returns:
        Dict[str, str]: Board information if it's a Duet board, empty dict otherwise
    """
    board_info = {}
    
    try:
        # Send M115 to get firmware information
        response = transport.query("M115")
        if not response:
            return {}
            
        # Check for Duet in the response
        if "FIRMWARE_NAME:RepRapFirmware" in response:
            # Extract firmware version and board type
            firmware_match = re.search(r'FIRMWARE_NAME:([^ ]+)', response)
            if firmware_match:
                board_info["firmware_name"] = firmware_match.group(1)
                
            version_match = re.search(r'FIRMWARE_VERSION:([^ ]+)', response)
            if version_match:
                board_info["firmware_version"] = version_match.group(1)
                
            board_match = re.search(r'ELECTRONICS:([^ ]+)', response)
            if board_match:
                board_info["board_type"] = board_match.group(1)
            
            return board_info
    except Exception as e:
        print(f"Error detecting Duet board: {str(e)}")
    
    return {}


def setup_wifi(transport: 'SerialTransport', ssid: str, password: str, 
               wait_for_connection: bool = True, timeout: int = 30) -> Dict[str, Any]:
    """
    Set up WiFi on a Duet board.
    
    First checks if WiFi is already connected to the desired SSID.
    If not, follows the correct sequence for reliable WiFi connection:
    1. Disable WiFi (M552 S0)
    2. Scan for networks (M588) to ensure WiFi module is active
    3. Configure WiFi settings (M587)
    4. Enable WiFi (M552 S1)
    5. Wait for connection (optional)
    
    Args:
        transport: SerialTransport instance
        ssid: WiFi network SSID
        password: WiFi network password
        wait_for_connection: Whether to wait for connection to be established
        timeout: Timeout in seconds for waiting for connection
        
    Returns:
        Dict with connection status information
    """
    result = {
        "success": False,
        "message": "",
        "ip_address": None,
        "state": None,
        "errors": []
    }
    
    if not transport.is_connected():
        result["message"] = "Transport not connected"
        return result
    
    board_info = detect_duet_board(transport)
    if not board_info:
        result["message"] = "Not a Duet board"
        return result
    
    try:
        # First check if WiFi is already connected to the desired SSID
        response = transport.send_line("M552")
        current_status = get_network_status(transport)
        
        # If already connected to the desired SSID, we're done
        if (current_status.get("state") == "active" and 
            current_status.get("ssid") == ssid):
            result["success"] = True
            result["message"] = f"Already connected to {ssid}"
            result["ip_address"] = current_status.get("ip")
            result["state"] = "active"
            return result
            
        # If connected to a different SSID or not connected, proceed with reconnection
        
        # Step 1: Disable WiFi
        transport.send_line("M552 S0")
        time.sleep(1)  # Give the board time to process
        
        # Step 2: Scan for networks to ensure WiFi module is active
        transport.send_line(f'M588 S"{ssid}"')
        time.sleep(1)  # Give the board time to process
        
        # Step 3: Configure WiFi settings
        transport.send_line(f'M587 S"{ssid}" P"{password}"')
        transport.send_line("M500")  # Save settings to config-override.g
        time.sleep(1)  # Give the board time to process
        
        # Step 4: Enable WiFi
        transport.send_line("M552 S1")
        result["success"] = True
        result["message"] = "WiFi configuration sent"
        
        if wait_for_connection:
            result["message"] = "Waiting for connection..."
            
            for _ in range(timeout):
                status = get_network_status(transport)
                result["state"] = status.get("state")
                
                # Check for authentication errors
                response = transport.get_last_response()
                if "Authentication failed" in response:
                    result["errors"].append("Authentication failed - check password")
                
                if status.get("state") == "active":
                    result["ip_address"] = status.get("ip")
                    result["message"] = f"Connected to WiFi. IP: {status.get('ip', 'unknown')}"
                    break
                    
                time.sleep(1)
            
            if not result["ip_address"]:
                result["message"] = "Timed out waiting for WiFi connection"
                result["success"] = False
    
    except Exception as e:
        result["message"] = f"Error setting up WiFi: {str(e)}"
        result["success"] = False
    
    return result


def get_network_status(transport: 'SerialTransport') -> Dict[str, Any]:
    """
    Get the network status from a Duet board.
    
    Args:
        transport: SerialTransport instance
        
    Returns:
        Dict with network status information (state, ip, ssid)
    """
    status = {
        "state": "unknown",
        "ip": None,
        "ssid": None
    }
    
    if not transport.is_connected():
        return status
    
    try:
        # First try using the object model (M409)
        if transport.is_duet:
            response = transport.send_line('M409 K"network"')
            
            # Try to parse JSON response
            try:
                # Extract JSON part from the response
                json_match = re.search(r'{\s*"network"\s*:.*}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    data = json.loads(json_str)
                    
                    if "network" in data:
                        network = data["network"]
                        
                        # Extract state
                        if "state" in network:
                            status["state"] = network["state"]
                            
                        # Extract IP address
                        if "interfaces" in network and len(network["interfaces"]) > 0:
                            for interface in network["interfaces"]:
                                if "actualIP" in interface and interface["actualIP"]:
                                    status["ip"] = interface["actualIP"]
                                    break
                                    
                        # Extract SSID
                        if "interfaces" in network and len(network["interfaces"]) > 0:
                            for interface in network["interfaces"]:
                                if "ssid" in interface and interface["ssid"]:
                                    status["ssid"] = interface["ssid"]
                                    break
                        
                        return status
            except:
                pass  # Fall back to M552
        
        # Fall back to M552
        response = transport.send_line("M552")
        
        # Extract state
        if "WiFi module is connected to access point" in response:
            status["state"] = "active"
            
            # Extract SSID and IP
            match = re.search(r'WiFi module is connected to access point ([^,]+), IP address ([0-9.]+)', response)
            if match:
                status["ssid"] = match.group(1)
                status["ip"] = match.group(2)
        elif "WiFi is connected to access point" in response:
            status["state"] = "active"
            
            # Extract SSID and IP
            match = re.search(r'WiFi is connected to access point ([^,]+), IP address ([0-9.]+)', response)
            if match:
                status["ssid"] = match.group(1)
                status["ip"] = match.group(2)
        elif "WiFi module is idle" in response:
            status["state"] = "idle"
        elif "WiFi module is disabled" in response:
            status["state"] = "disabled"
        elif "WiFi module is starting" in response:
            status["state"] = "starting"
        elif "WiFi module is enabled" in response:
            status["state"] = "enabled"
        
    except Exception as e:
        print(f"Error getting network status: {str(e)}")
    
    return status


def scan_wifi_networks(transport: 'SerialTransport', timeout: int = 10) -> List[Dict[str, Any]]:
    """
    Scan for available WiFi networks.
    
    Args:
        transport: A connected SerialTransport instance
        timeout: Maximum time to wait for scan results in seconds
        
    Returns:
        List[Dict[str, Any]]: List of available WiFi networks
    """
    networks = []
    
    if not transport.is_connected():
        return networks
    
    try:
        # Start scan
        transport.send_line("M588")
        
        # Wait for results
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = transport.query("M408 S0")
            if response and "scanResult" in response:
                try:
                    data = json.loads(response)
                    if "scanResult" in data and data["scanResult"] != "":
                        scan_results = data["scanResult"].split("\n")
                        for result in scan_results:
                            if result.strip():
                                parts = result.split(",")
                                if len(parts) >= 3:
                                    network = {
                                        "ssid": parts[0],
                                        "rssi": int(parts[1]),
                                        "channel": int(parts[2]),
                                        "encryption": parts[3] if len(parts) > 3 else "unknown"
                                    }
                                    networks.append(network)
                        break
                except (json.JSONDecodeError, ValueError):
                    pass
            
            time.sleep(1)
    except Exception as e:
        print(f"Error scanning WiFi networks: {str(e)}")
    
    return networks


def configure_access_point(transport: 'SerialTransport', ssid: str, password: Optional[str] = None,
                          channel: Optional[int] = None) -> bool:
    """
    Configure the Duet board as a WiFi access point.
    
    Args:
        transport: A connected SerialTransport instance
        ssid: SSID for the access point
        password: Password for the access point (optional)
        channel: WiFi channel (optional)
        
    Returns:
        bool: True if configuration was successful, False otherwise
    """
    if not transport.is_connected():
        return False
    
    try:
        # Build command
        command = f'M589 S"{ssid}"'
        if password:
            command += f' P"{password}"'
        if channel:
            command += f' C{channel}'
        
        # Send command
        transport.send_line(command)
        
        # Store parameters
        transport.send_line("M500")
        
        # Enable WiFi as access point
        transport.send_line("M552 S2")
        
        return True
    except Exception as e:
        print(f"Error configuring access point: {str(e)}")
        return False


def enable_network_protocol(transport: 'SerialTransport', protocol: int, enable: bool = True) -> bool:
    """
    Enable or disable a network protocol.
    
    Args:
        transport: A connected SerialTransport instance
        protocol: Protocol number (0=HTTP, 1=FTP, 2=Telnet, 3=MQTT)
        enable: True to enable, False to disable
        
    Returns:
        bool: True if configuration was successful, False otherwise
    """
    if not transport.is_connected():
        return False
    
    try:
        # Build command
        state = 1 if enable else 0
        command = f"M586 P{protocol} S{state}"
        
        # Send command
        transport.send_line(command)
        
        # Store parameters
        transport.send_line("M500")
        
        return True
    except Exception as e:
        print(f"Error configuring network protocol: {str(e)}")
        return False


def get_board_diagnostics(transport: 'SerialTransport') -> Dict[str, Any]:
    """
    Get diagnostic information from the Duet board.
    
    Args:
        transport: A connected SerialTransport instance
        
    Returns:
        Dict[str, Any]: Diagnostic information
    """
    diagnostics = {}
    
    if not transport.is_connected():
        return diagnostics
    
    try:
        # Get firmware information
        response = transport.query("M115")
        if response:
            diagnostics["firmware"] = parse_firmware_info(response)
        
        # Get network status
        diagnostics["network"] = get_network_status(transport)
        
        # Get detailed diagnostics
        response = transport.query("M122")
        if response:
            diagnostics["details"] = response
    except Exception as e:
        print(f"Error getting board diagnostics: {str(e)}")
    
    return diagnostics


def parse_firmware_info(response: str) -> Dict[str, str]:
    """
    Parse firmware information from M115 response.
    
    Args:
        response: Response from M115 command
        
    Returns:
        Dict[str, str]: Firmware information
    """
    info = {}
    
    # Extract key information
    firmware_match = re.search(r'FIRMWARE_NAME:([^ ]+)', response)
    if firmware_match:
        info["name"] = firmware_match.group(1)
        
    version_match = re.search(r'FIRMWARE_VERSION:([^ ]+)', response)
    if version_match:
        info["version"] = version_match.group(1)
        
    board_match = re.search(r'ELECTRONICS:([^ ]+)', response)
    if board_match:
        info["board"] = board_match.group(1)
    
    # Extract all other parameters
    for match in re.finditer(r'([A-Z_]+):([^ ]+)', response):
        key = match.group(1).lower()
        value = match.group(2)
        if key not in info:
            info[key] = value
    
    return info 