"""
Airbrush-specific transport implementation for the Realtime Hairbrush SDK.

This module provides a transport implementation that extends the base Transport class
with airbrush-specific functionality for connecting to the Duet board.
"""

import os
import json
import time
from typing import Dict, Any, Optional, Union, List
import threading

from semantic_gcode.transport.base import Transport
from semantic_gcode.transport.serial import SerialTransport
from semantic_gcode.transport.http import HttpTransport

from realtime_hairbrush.transport.config import ConnectionConfig


# Global transport instance for connection persistence between CLI commands
_global_transport = None


class AirbrushTransport:
    """
    Airbrush-specific transport implementation that provides a unified interface
    for both serial and HTTP connections to the Duet board.
    """
    
    def __init__(self, config: ConnectionConfig):
        """
        Initialize the airbrush transport with the given configuration.

        Args:
            config: Connection configuration
        """
        self.config = config
        self.transport: Optional[Transport] = None
        self._connected = False
        self._last_error = None
        self._io_lock = threading.Lock()
        
        # Use the global transport if available
        global _global_transport
        if _global_transport is not None:
            self.transport = _global_transport
            self._connected = self.transport.is_connected()

    def connect(self) -> bool:
        """
        Connect to the Duet board using the configured transport type.

        Returns:
            bool: True if connection was successful, False otherwise
        """
        try:
            # If already connected, return True
            if self.transport and self.transport.is_connected():
                return True
                
            if self.config.transport_type == "serial":
                base = SerialTransport(
                    port=self.config.serial_port,
                    baud_rate=self.config.serial_baudrate,
                    timeout=self.config.timeout
                )
            elif self.config.transport_type == "http":
                url = f"http://{self.config.http_host}"
                base = HttpTransport(
                    url=url,
                    password=self.config.http_password,
                    timeout=self.config.timeout
                )
            else:
                self._last_error = f"Unsupported transport type: {self.config.transport_type}"
                return False

            # Wrap with logging decorator if enabled (default on)
            try:
                from .logging_wrapper import LoggingTransport
                # Always enable logging in this branch unless explicitly disabled
                if os.getenv("AIRBRUSH_LOG", "1") in ("0", "false", "False"):
                    self.transport = base
                else:
                    self.transport = LoggingTransport(base)
            except Exception:
                self.transport = base

            self._connected = self.transport.connect()
            if self._connected:
                # Store the transport globally for persistence between CLI commands
                global _global_transport
                _global_transport = self.transport
            else:
                self._last_error = "Failed to connect to the Duet board"
            
            return self._connected
        except Exception as e:
            self._last_error = str(e)
            self._connected = False
            return False

    def disconnect(self) -> None:
        """
        Disconnect from the Duet board.
        """
        if self.transport and self._connected:
            self.transport.disconnect()
            self._connected = False
            
            # Clear the global transport
            global _global_transport
            _global_transport = None

    def is_connected(self) -> bool:
        """
        Check if the transport is currently connected.

        Returns:
            bool: True if connected, False otherwise
        """
        if not self.transport:
            return False
        
        # Update the connected state from the transport
        self._connected = self.transport.is_connected()
        return self._connected

    def send_line(self, line: str) -> bool:
        """
        Send a single line of G-code to the device.

        Args:
            line: The G-code command to send

        Returns:
            bool: True if the command was sent successfully, False otherwise
        """
        if not self.is_connected():
            self._last_error = "Not connected"
            return False

        try:
            with self._io_lock:
                return self.transport.send_line(line)
        except Exception as e:
            self._last_error = str(e)
            return False

    def query(self, query_cmd: str) -> Optional[str]:
        """
        Send a query command and get the response.

        Args:
            query_cmd: The query command to send

        Returns:
            Optional[str]: The response from the device, or None if no response
        """
        if not self.is_connected():
            self._last_error = "Not connected"
            return None

        try:
            with self._io_lock:
                return self.transport.query(query_cmd)
        except Exception as e:
            self._last_error = str(e)
            return None

    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the device.

        Returns:
            Dict[str, Any]: A dictionary containing the device status
        """
        if not self.is_connected():
            return {"connected": False, "error": self._last_error or "Not connected"}

        try:
            status = self.transport.get_status()
            status["connected"] = True
            return status
        except Exception as e:
            self._last_error = str(e)
            return {"connected": False, "error": self._last_error}

    def get_last_error(self) -> Optional[str]:
        """
        Get the last error message.

        Returns:
            Optional[str]: The last error message, or None if no error
        """
        return self._last_error

    def wait_for_idle(self, poll_interval: float = 0.2, timeout: float = 60.0, verbose: bool = False) -> bool:
        """
        Wait for all motion to complete using M400.
        
        This method sends M400 to wait for all motion to complete and waits for the 'ok' response.
        
        Args:
            poll_interval: Time between polls in seconds (not used with M400)
            timeout: Maximum time to wait in seconds
            verbose: Whether to print status updates
            
        Returns:
            bool: True if the machine became idle within the timeout, False otherwise
        """
        if not self.is_connected():
            self._last_error = "Not connected"
            return False
            
        if verbose:
            print("Sending M400 to wait for motion to complete...")
            
        try:
            # Import the M400 command class
            from semantic_gcode.dict.gcode_commands.M400.M400 import M400_WaitForMoves
            
            # Create and execute the M400 command
            m400_cmd = M400_WaitForMoves.create()
            
            # Start timeout timer
            start_time = time.time()
            
            # Send the command and get the initial response
            response = self.query(str(m400_cmd))
            
            # Use the command's validate_response method to check for acknowledgement
            while not m400_cmd.validate_response(response):
                # Check for timeout
                if time.time() - start_time > timeout:
                    self._last_error = "Timeout waiting for motion to complete"
                    if verbose:
                        print("Timeout waiting for motion to complete")
                    return False
                
                # Wait a bit before checking again
                time.sleep(0.1)
                
                # Read more response data if available
                additional_response = self.query("")
                if additional_response:
                    response += additional_response
            
            if verbose:
                print("Motion complete")
            return True
                
        except ImportError:
            # Fall back to simpler implementation if M400 class is not available
            self._last_error = "M400 command implementation not available"
            if verbose:
                print("M400 command implementation not available, using basic query")
            
            # Simple implementation using direct query
            response = self.query("M400")
            
            # Check if we got an 'ok' response
            if response and "ok" in response.lower():
                if verbose:
                    print("Motion complete")
                return True
            else:
                self._last_error = "Did not receive 'ok' response to M400 command"
                if verbose:
                    print(f"Unexpected response: {response}")
                return False
        except Exception as e:
            self._last_error = f"Error waiting for motion to complete: {str(e)}"
            if verbose:
                print(f"Error: {str(e)}")
            return False

    def send_command_with_retry(self, command: str, retries: int = 3, delay: float = 0.5) -> bool:
        """
        Send a command with retry logic.

        Args:
            command: The command to send
            retries: Number of retries
            delay: Delay between retries in seconds

        Returns:
            bool: True if the command was sent successfully, False otherwise
        """
        for attempt in range(retries + 1):
            if self.send_line(command):
                return True
            if attempt < retries:
                time.sleep(delay)
        return False

    def switch_to_http(self) -> bool:
        """
        Switch from serial to HTTP transport.
        This is useful when initially connecting via serial to configure WiFi,
        then switching to HTTP for better performance.

        Returns:
            bool: True if the switch was successful, False otherwise
        """
        if self.config.transport_type != "serial":
            self._last_error = "Current transport is not serial"
            return False

        # Store the current connection state
        was_connected = self._connected

        # Disconnect from the serial transport
        if was_connected:
            self.disconnect()

        # Update the configuration
        self.config.transport_type = "http"

        # Connect using HTTP if we were previously connected
        if was_connected:
            return self.connect()
        return True
        
    @staticmethod
    def save_connection_state(filepath: str = None) -> bool:
        """
        Save the current connection state to a file.
        
        Args:
            filepath: Path to save the connection state. If None, uses a default path.
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        if filepath is None:
            home_dir = os.path.expanduser("~")
            filepath = os.path.join(home_dir, ".airbrush_connection")
            
        global _global_transport
        if _global_transport is None:
            # No connection to save
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except:
                    pass
            return True
            
        try:
            # Get connection info based on transport type
            connection_info = {
                "connected": _global_transport.is_connected()
            }
            
            if isinstance(_global_transport, SerialTransport):
                connection_info["type"] = "serial"
                connection_info["port"] = _global_transport._port
                connection_info["baud_rate"] = _global_transport._baud_rate
            elif isinstance(_global_transport, HttpTransport):
                connection_info["type"] = "http"
                connection_info["url"] = _global_transport.base_url
                
            # Save to file
            with open(filepath, 'w') as f:
                json.dump(connection_info, f)
            return True
        except Exception:
            return False
            
    @staticmethod
    def load_connection_state(filepath: str = None) -> Optional[Dict[str, Any]]:
        """
        Load the connection state from a file.
        
        Args:
            filepath: Path to load the connection state from. If None, uses a default path.
            
        Returns:
            Optional[Dict[str, Any]]: The connection state, or None if not found
        """
        if filepath is None:
            home_dir = os.path.expanduser("~")
            filepath = os.path.join(home_dir, ".airbrush_connection")
            
        if not os.path.exists(filepath):
            return None
            
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception:
            return None 

    def update_network_info(self, ip_address: Optional[str] = None, network_state: Optional[str] = None) -> None:
        """
        Update network information based on command responses.
        
        This method is called by network-related commands (like M552) to update
        the transport's knowledge of network status.
        
        Args:
            ip_address: The detected IP address, if any
            network_state: The detected network state, if any
        """
        # Store the information in the transport object
        if ip_address:
            self._ip_address = ip_address
            
        if network_state:
            self._network_state = network_state
            
        # If we're using HTTP transport and get an IP address, update the host
        if self.config.transport_type == "http" and ip_address and not self.config.http_host:
            self.config.http_host = ip_address
            
    def update_firmware_info(self, firmware_info: Dict[str, str]) -> None:
        """
        Update firmware information based on command responses.
        
        This method is called by firmware-related commands (like M115) to update
        the transport's knowledge of the firmware.
        
        Args:
            firmware_info: Dictionary containing firmware information
        """
        # Store the firmware information in the transport object
        self._firmware_info = firmware_info
        
        # Extract and store specific pieces of information
        if 'name' in firmware_info:
            self._firmware_name = firmware_info['name']
        
        if 'version' in firmware_info:
            self._firmware_version = firmware_info['version']
            
        if 'board' in firmware_info:
            self._board_type = firmware_info['board']
            
    def get_ip_address(self) -> Optional[str]:
        """
        Get the detected IP address of the device.
        
        Returns:
            Optional[str]: The IP address, or None if not detected
        """
        return getattr(self, '_ip_address', None)
        
    def get_network_state(self) -> Optional[str]:
        """
        Get the detected network state of the device.
        
        Returns:
            Optional[str]: The network state, or None if not detected
        """
        return getattr(self, '_network_state', None) 

    def get_firmware_info(self) -> Dict[str, str]:
        """
        Get the detected firmware information.
        
        Returns:
            Dict[str, str]: The firmware information, or an empty dict if not detected
        """
        return getattr(self, '_firmware_info', {})
        
    def get_firmware_name(self) -> Optional[str]:
        """
        Get the detected firmware name.
        
        Returns:
            Optional[str]: The firmware name, or None if not detected
        """
        return getattr(self, '_firmware_name', None)
        
    def get_firmware_version(self) -> Optional[str]:
        """
        Get the detected firmware version.
        
        Returns:
            Optional[str]: The firmware version, or None if not detected
        """
        return getattr(self, '_firmware_version', None)
        
    def get_board_type(self) -> Optional[str]:
        """
        Get the detected board type.
        
        Returns:
            Optional[str]: The board type, or None if not detected
        """
        return getattr(self, '_board_type', None) 