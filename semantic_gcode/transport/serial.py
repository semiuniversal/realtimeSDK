"""
Serial transport implementation for G-code devices.

This module provides a transport implementation that communicates with
a G-code device via a serial port.
"""
import os
import time
import re
import json
from typing import Dict, Any, Optional, List, Union, Tuple

try:
    import serial
    from serial.serialutil import SerialException
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    # Define SerialException for type checking when serial is not available
    class SerialException(Exception):
        pass

from .base import Transport
from ..utils.exceptions import ConnectionError, TimeoutError, TransportError
from ..utils.platform import get_platform, PlatformType, get_serial_port_for_wsl


class SerialTransport(Transport):
    """
    Serial transport for communicating with G-code devices.
    
    This transport uses a serial port for sending G-code commands
    and receiving responses.
    """
    
    def __init__(self, port: Optional[str] = None, baud_rate: int = 115200, 
                 timeout: float = 5.0, auto_detect_board: bool = True,
                 disable_wifi_on_connect: bool = False, debug: bool = False):
        """
        Initialize a serial transport.
        
        Args:
            port: Serial port to connect to. If None, will attempt to auto-detect.
            baud_rate: Baud rate for serial communication
            timeout: Timeout for serial operations in seconds
            auto_detect_board: Whether to automatically detect the board type on connect
            disable_wifi_on_connect: Whether to disable WiFi on connect (Duet boards only)
            debug: Whether to print debug information
        """
        self._port = port
        self._baud_rate = baud_rate
        self._timeout = timeout
        self._serial = None
        self._connected = False
        self._auto_detect_board = auto_detect_board
        self._disable_wifi_on_connect = disable_wifi_on_connect
        self._debug = debug
        
        # Board-specific information
        self.is_duet = False
        self.firmware_name = None
        self.firmware_version = None
        self.board_type = None
        
        # Response tracking
        self._last_response = ""
    
    def connect(self) -> bool:
        """
        Connect to the serial device.
        
        Returns:
            bool: True if connection was successful, False otherwise
            
        Raises:
            ConnectionError: If connection fails
        """
        try:
            # Handle WSL-specific port mapping
            from ..utils.platform import get_platform, PlatformType, get_serial_port_for_wsl
            
            platform_type = get_platform()
            port = self._port
            
            if platform_type == PlatformType.WSL and port and port.startswith("COM"):
                port = get_serial_port_for_wsl(port)
                if self._debug:
                    print(f"DEBUG: Mapped Windows {self._port} to WSL {port}")
            
            # Check if port exists (except for Windows COM ports)
            if port and not os.path.exists(port) and not port.startswith("COM"):
                raise ConnectionError(f"Serial port {port} does not exist")
            
            # Create serial connection
            try:
                self._serial = serial.Serial(
                    port=port,
                    baudrate=self._baud_rate,
                    timeout=self._timeout
                )
            except serial.SerialException as e:
                # Provide more helpful error messages for Windows users
                if "FileNotFoundError" in str(e) and port and port.startswith("COM"):
                    error_msg = (
                        f"Could not open port {port}. The port may not exist or may be in use by another application.\n"
                        f"Try the following:\n"
                        f"1. Check Device Manager to verify the port exists\n"
                        f"2. Close any other applications that might be using the port\n"
                        f"3. Try a different port\n"
                        f"4. Run the program with administrator privileges"
                    )
                    raise ConnectionError(error_msg)
                else:
                    raise
            
            # Clear buffers
            self._serial.reset_input_buffer()
            self._serial.reset_output_buffer()
            
            self._connected = True
            
            # Auto-detect board type if requested
            if self._auto_detect_board:
                self._detect_board_type()
            
            return True
            
        except serial.SerialException as e:
            self._connected = False
            raise ConnectionError(f"Serial connection error: {str(e)}")
        except Exception as e:
            self._connected = False
            raise ConnectionError(f"Unexpected error connecting to serial port: {str(e)}")
    
    def disconnect(self) -> None:
        """
        Close the connection to the device.
        """
        if self._serial:
            try:
                self._serial.close()
            except Exception:
                pass
            finally:
                self._serial = None
                self._connected = False
    
    def is_connected(self) -> bool:
        """
        Check if the transport is connected.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self._connected and self._serial is not None
    
    def _detect_board_type(self) -> bool:
        """
        Detect the board type by sending M115.
        
        Returns:
            bool: True if a Duet board was detected, False otherwise
        """
        try:
            # Send M115 to get firmware information
            response = self.send_line("M115")
            
            # Parse the response
            firmware_info = response.strip()
            
            # Check if it's a Duet board
            if "RepRapFirmware" in firmware_info:
                self.is_duet = True
                
                # Extract firmware name
                firmware_match = re.search(r'FIRMWARE_NAME:\s*(RepRapFirmware[^,\n]*)', firmware_info)
                if firmware_match:
                    self.firmware_name = firmware_match.group(1)
                else:
                    self.firmware_name = "RepRapFirmware"
                
                # Extract version
                version_match = re.search(r'FIRMWARE_VERSION:\s*([0-9.]+)', firmware_info)
                if version_match:
                    self.firmware_version = version_match.group(1)
                    
                # Extract board type
                board_match = re.search(r'ELECTRONICS:\s*([^,\n]+)', firmware_info)
                if board_match:
                    self.board_type = board_match.group(1).strip()
                
                if self._debug:
                    print(f"DEBUG: Detected Duet board: {self.board_type}, Firmware: {self.firmware_name} {self.firmware_version}")
                    print(f"DEBUG: Full response: {firmware_info}")
                
                # Disable WiFi module if requested
                if self._disable_wifi_on_connect:
                    try:
                        self.send_line("M552 S-1")
                        if self._debug:
                            print("DEBUG: Disabled Duet WiFi module")
                    except Exception as e:
                        if self._debug:
                            print(f"DEBUG: Failed to disable WiFi module: {e}")
                
                return True
            
            return False
        except Exception as e:
            if self._debug:
                print(f"DEBUG: Error detecting board type: {e}")
            return False
    
    def _read_until_timeout(self, timeout: float) -> str:
        """
        Read from the serial port until a timeout occurs.
        
        Args:
            timeout: The timeout in seconds
            
        Returns:
            str: The data read from the port
        """
        if not self._serial:
            return ""
            
        # Save the original timeout
        original_timeout = self._serial.timeout
        self._serial.timeout = timeout
        
        try:
            # Read until timeout
            data = b""
            start_time = time.time()
            
            while (time.time() - start_time) < timeout:
                if self._serial.in_waiting > 0:
                    chunk = self._serial.read(self._serial.in_waiting)
                    data += chunk
                    
                    # If we got data, extend the timeout a bit to see if more is coming
                    if chunk:
                        start_time = time.time()
                else:
                    # Small sleep to avoid hammering the CPU
                    time.sleep(0.01)
            
            # Convert to string
            return data.decode("utf-8", errors="replace")
        finally:
            # Restore the original timeout
            self._serial.timeout = original_timeout
    
    def send_line(self, line: str) -> str:
        """
        Send a line of G-code to the device.
        
        Args:
            line: The G-code line to send
            
        Returns:
            str: The response from the device
            
        Raises:
            TransportError: If the transport is not connected or an error occurs
        """
        if not self.is_connected():
            raise TransportError("Not connected")
            
        try:
            # Add newline if not present
            if not line.endswith('\n'):
                line += '\n'
                
            # Send the command
            self._serial.write(line.encode())
            self._serial.flush()
            
            # Read the response
            response = ""
            
            # For Duet boards, wait for "ok" or "Error:"
            if self.is_duet:
                while True:
                    line = self._serial.readline().decode('utf-8', errors='replace').strip()
                    if line:
                        response += line + "\n"
                        if line == "ok" or line.startswith("Error:"):
                            break
                    else:
                        # No more data, timeout
                        if not response:
                            raise TimeoutError("No response received")
                        break
            else:
                # For other boards, read until timeout
                response = self._read_until_timeout(timeout=self._timeout)
                
            # Store the last response
            self._last_response = response
            
            return response.strip()
            
        except Exception as e:
            raise TransportError(f"Error sending command: {str(e)}")
            
    def query(self, line: str) -> str:
        """
        Send a query and get the response.
        
        Args:
            line: The G-code query to send
            
        Returns:
            str: The response from the device
            
        Raises:
            TransportError: If the transport is not connected or an error occurs
        """
        if not self.is_connected():
            raise TransportError("Not connected")
        
        # Short-circuit empty reads to avoid serial churn
        if not line or not str(line).strip():
            return ""
        
        try:
            # Send the command
            if not line.endswith('\n'):
                line += '\n'
            
            self._serial.write(line.encode())
            self._serial.flush()
            
            # Read the response
            response = ""
            
            # For Duet boards, wait for "ok" or "Error:"
            if self.is_duet:
                while True:
                    line = self._serial.readline().decode('utf-8', errors='replace').strip()
                    if line:
                        response += line + "\n"
                        if line == "ok" or line.startswith("Error:"):
                            break
                    else:
                        # No more data, timeout
                        if not response:
                            raise TimeoutError("No response received")
                        break
            else:
                # For other boards, read until timeout
                response = self._read_until_timeout(timeout=self._timeout)
                
            # Store the last response
            self._last_response = response
            
            return response.strip()
            
        except Exception as e:
            raise TransportError(f"Error querying: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the device.
        
        Returns:
            Dict[str, Any]: A dictionary containing the device status
            
        Raises:
            ConnectionError: If not connected
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to device")
        
        status = {
            "position": {},
            "temperatures": {},
            "firmware": {},
            "network": {}
        }
        
        # For Duet boards, use the object model
        if self.is_duet:
            try:
                # Try to get the object model (newer firmware)
                response = self.query("M409")
                if response and "result" in response:
                    try:
                        data = json.loads(response)
                        model = data.get("result", {})
                        
                        # Extract position
                        if "move" in model and "axes" in model["move"]:
                            axes = model["move"]["axes"]
                            for i, axis in enumerate(axes):
                                if "letter" in axis:
                                    status["position"][axis["letter"]] = axis.get("machinePosition", 0.0)
                        
                        # Extract temperatures
                        if "heat" in model:
                            heat = model["heat"]
                            
                            # Extract bed temperature
                            if "beds" in heat and len(heat["beds"]) > 0:
                                bed = heat["beds"][0]
                                status["temperatures"]["bed"] = {
                                    "current": bed.get("current", 0.0),
                                    "target": bed.get("active", 0.0)
                                }
                            
                            # Extract tool temperatures
                            if "tools" in heat:
                                for i, tool in enumerate(heat["tools"]):
                                    if "heaters" in tool and len(tool["heaters"]) > 0:
                                        heater_idx = tool["heaters"][0]
                                        if "heaters" in heat and heater_idx < len(heat["heaters"]):
                                            heater = heat["heaters"][heater_idx]
                                            status["temperatures"][f"tool{i}"] = {
                                                "current": heater.get("current", 0.0),
                                                "target": heater.get("active", 0.0)
                                            }
                        
                        # Extract network status
                        if "network" in model:
                            network = model["network"]
                            status["network"] = {
                                "state": network.get("state", "unknown")
                            }
                            
                            # Extract interface info
                            if "interfaces" in network and len(network["interfaces"]) > 0:
                                interface = network["interfaces"][0]
                                status["network"]["ip"] = interface.get("actualIP", None)
                                status["network"]["mac"] = interface.get("mac", None)
                        
                        # Extract firmware info
                        if "electronics" in model:
                            status["firmware"]["board"] = model["electronics"].get("type", "unknown")
                        if "firmware" in model:
                            status["firmware"]["name"] = model["firmware"].get("name", "unknown")
                            status["firmware"]["version"] = model["firmware"].get("version", "unknown")
                        
                        return status
                    except json.JSONDecodeError:
                        pass
            except Exception as e:
                if self._debug:
                    print(f"DEBUG: Error getting object model: {e}")
        
        # Fallback to individual queries
        try:
            # Get position
            try:
                pos_response = self.query("M114")
                if pos_response:
                    status["position"] = self._parse_position(pos_response)
            except Exception as e:
                if self._debug:
                    print(f"DEBUG: Error getting position: {e}")
            
            # Get temperatures
            try:
                temp_response = self.query("M105")
                if temp_response:
                    status["temperatures"] = self._parse_temperatures(temp_response)
            except Exception as e:
                if self._debug:
                    print(f"DEBUG: Error getting temperatures: {e}")
            
            # Get firmware info
            try:
                if self.firmware_name:
                    status["firmware"]["name"] = self.firmware_name
                if self.firmware_version:
                    status["firmware"]["version"] = self.firmware_version
                if self.board_type:
                    status["firmware"]["board"] = self.board_type
            except Exception as e:
                if self._debug:
                    print(f"DEBUG: Error getting firmware info: {e}")
            
            # Get network status for Duet boards
            if self.is_duet:
                try:
                    net_response = self.query("M552")
                    if net_response:
                        # Extract IP address
                        ip_match = re.search(r'IP address = (\d+\.\d+\.\d+\.\d+)', net_response)
                        if ip_match:
                            status["network"]["ip"] = ip_match.group(1)
                            status["network"]["state"] = "active"
                        
                        # Check for WiFi status
                        if "WiFi module is disabled" in net_response:
                            status["network"]["state"] = "disabled"
                        elif "WiFi module is enabled" in net_response:
                            status["network"]["state"] = "enabled"
                        elif "WiFi module is starting" in net_response:
                            status["network"]["state"] = "starting"
                        elif "connected to access point" in net_response.lower():
                            status["network"]["state"] = "active"
                except Exception as e:
                    if self._debug:
                        print(f"DEBUG: Error getting network status: {e}")
        except Exception as e:
            if self._debug:
                print(f"DEBUG: Error getting status: {e}")
        
        return status
    
    def _parse_position(self, response: str) -> Dict[str, float]:
        """
        Parse position information from M114 response.
        
        Args:
            response: The response from M114
            
        Returns:
            Dict[str, float]: A dictionary of axis positions
        """
        position = {}
        
        # Extract X, Y, Z, E positions
        for axis in ["X", "Y", "Z", "E"]:
            match = re.search(rf'{axis}:(-?\d+\.?\d*)', response)
            if match:
                try:
                    position[axis.lower()] = float(match.group(1))
                except ValueError:
                    pass
        
        return position
    
    def _parse_temperatures(self, response: str) -> Dict[str, Dict[str, float]]:
        """
        Parse temperature information from M105 response.
        
        Args:
            response: The response from M105
            
        Returns:
            Dict[str, Dict[str, float]]: A dictionary of temperature information
        """
        temperatures = {}
        
        # Extract tool temperatures (T0, T1, etc.)
        for match in re.finditer(r'T(\d+):\s*(\d+\.?\d*)\s*\/(\d+\.?\d*)', response):
            try:
                tool_num = int(match.group(1))
                current = float(match.group(2))
                target = float(match.group(3))
                temperatures[f"tool{tool_num}"] = {
                    "current": current,
                    "target": target
                }
            except ValueError:
                pass
        
        # Extract bed temperature
        bed_match = re.search(r'B:\s*(\d+\.?\d*)\s*\/(\d+\.?\d*)', response)
        if bed_match:
            try:
                current = float(bed_match.group(1))
                target = float(bed_match.group(2))
                temperatures["bed"] = {
                    "current": current,
                    "target": target
                }
            except ValueError:
                pass
        
        return temperatures
    
    def configure_wifi(self, ssid: str, password: str) -> bool:
        """
        Configure WiFi settings on a Duet board.
        
        Args:
            ssid: The WiFi network SSID
            password: The WiFi network password
            
        Returns:
            bool: True if configuration was successful, False otherwise
            
        Raises:
            ConnectionError: If not connected
            TransportError: If the device is not a Duet board
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to device")
            
        if not self.is_duet:
            raise TransportError("Device is not a Duet board")
            
        try:
            # Configure WiFi credentials
            self.send_line(f'M587 S"{ssid}" P"{password}"')
            
            # Store parameters
            self.send_line("M500")
            
            # Enable WiFi
            self.send_line("M552 S1")
            
            return True
        except Exception as e:
            if self._debug:
                print(f"DEBUG: Error configuring WiFi: {e}")
            return False
    
    def get_network_status(self) -> Dict[str, Any]:
        """
        Get the current network status of a Duet board.
        
        Returns:
            Dict[str, Any]: Network status information
            
        Raises:
            ConnectionError: If not connected
            TransportError: If the device is not a Duet board
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to device")
            
        if not self.is_duet:
            raise TransportError("Device is not a Duet board")
            
        status = {
            "state": "unknown",
            "ip": None,
            "mac": None,
            "subnet": None,
            "gateway": None
        }
        
        # Try using object model first (newer firmware)
        try:
            response = self.query("M409 K\"network\"")
            if response and "result" in response:
                try:
                    data = json.loads(response)
                    network_data = data.get("result", {})
                    
                    if "state" in network_data:
                        status["state"] = network_data["state"]
                    if "interfaces" in network_data and len(network_data["interfaces"]) > 0:
                        interface = network_data["interfaces"][0]
                        status["ip"] = interface.get("actualIP", None)
                        status["mac"] = interface.get("mac", None)
                        status["subnet"] = interface.get("subnet", None)
                        status["gateway"] = interface.get("gateway", None)
                    
                    return status
                except json.JSONDecodeError:
                    pass
        except Exception:
            pass
        
        # Fallback to M552 for older firmware
        try:
            response = self.query("M552")
            if response:
                # Extract IP address
                ip_match = re.search(r'IP address = (\d+\.\d+\.\d+\.\d+)', response)
                if ip_match:
                    status["ip"] = ip_match.group(1)
                    status["state"] = "active"
                
                # Check for WiFi status
                if "WiFi module is disabled" in response:
                    status["state"] = "disabled"
                elif "WiFi module is enabled" in response:
                    status["state"] = "enabled"
                elif "WiFi module is starting" in response:
                    status["state"] = "starting"
                elif "connected to access point" in response.lower():
                    status["state"] = "active"
        except Exception:
            pass
        
        return status
    
    def get_last_response(self) -> str:
        """
        Get the last response received from the board.
        
        Returns:
            str: The last response received
        """
        return self._last_response
    
    @staticmethod
    def list_ports() -> List[str]:
        """
        List available serial ports.
        
        Returns:
            List[str]: A list of available serial ports
        """
        if not SERIAL_AVAILABLE:
            return []
            
        try:
            import serial.tools.list_ports
            from ..utils.platform import get_platform, PlatformType
            
            platform_type = get_platform()
            
            # For WSL, we need to handle COM ports differently
            if platform_type == PlatformType.WSL:
                # In WSL, we can't directly access Windows COM ports
                # but we can list them for information purposes
                try:
                    # Try to run PowerShell command to list COM ports
                    import subprocess
                    result = subprocess.run(
                        ["powershell.exe", "-Command", "[System.IO.Ports.SerialPort]::GetPortNames()"],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        # Parse the output to get COM port names
                        ports = [line.strip() for line in result.stdout.splitlines() if line.strip()]
                        return ports
                except Exception:
                    # If PowerShell command fails, return an empty list
                    return []
            else:
                # For other platforms, use pyserial's list_ports
                return [port.device for port in serial.tools.list_ports.comports()]
        except Exception as e:
            print(f"Error listing ports: {str(e)}")
            return []
