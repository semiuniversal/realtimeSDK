"""
Configuration session for Duet boards.

This module provides a high-level session class for configuring Duet boards,
including WiFi setup and transitioning from serial to WiFi connectivity.
"""
import time
from typing import Dict, Any, Optional, List, Tuple, Union

from ..transport.base import Transport
from ..transport.serial import SerialTransport
from ..transport.http import HttpTransport
from ..utils.duet_config import (
    detect_duet_board, 
    setup_wifi, 
    get_network_status,
    scan_wifi_networks,
    configure_access_point,
    enable_network_protocol,
    get_board_diagnostics
)


class ConfigSession:
    """
    Session for configuring Duet boards.
    
    This class provides high-level methods for configuring Duet boards,
    including WiFi setup and transitioning from serial to WiFi connectivity.
    """
    
    def __init__(self, transport: Transport, debug: bool = False):
        """
        Initialize a configuration session.
        
        Args:
            transport: The transport to use for communication
            debug: Whether to enable debug output
        """
        self.transport = transport
        self.debug = debug
        self.board_info = {}
        self._is_duet = False
        
        # Set debug mode on the transport if it's a SerialTransport
        if isinstance(self.transport, SerialTransport):
            self.transport.debug = debug
    
    def connect(self) -> bool:
        """
        Connect to the board and gather information.
        
        Returns:
            bool: True if connection was successful, False otherwise
        """
        if not self.transport.connect():
            return False
        
        # Check if it's a Duet board
        if isinstance(self.transport, SerialTransport):
            self._is_duet = self.transport.is_duet
            if self._is_duet:
                self.board_info = {
                    "firmware_name": self.transport.firmware_name,
                    "firmware_version": self.transport.firmware_version,
                    "board_type": self.transport.board_type
                }
        else:
            # For HTTP transport, we assume it's a Duet board
            self._is_duet = True
            
            # Try to get firmware info
            try:
                status = self.transport.get_status()
                if "firmware" in status:
                    self.board_info = status["firmware"]
            except Exception as e:
                if self.debug:
                    print(f"DEBUG: Error getting board info: {e}")
        
        return True
    
    def is_duet_board(self) -> bool:
        """
        Check if the connected board is a Duet board.
        
        Returns:
            bool: True if the board is a Duet board, False otherwise
        """
        return self._is_duet
    
    def get_board_info(self) -> Dict[str, str]:
        """
        Get information about the connected board.
        
        Returns:
            Dict[str, str]: Board information
        """
        return self.board_info
    
    def setup_wifi(self, ssid: str, password: str, 
                   wait_for_connection: bool = True, timeout: int = 30) -> Dict[str, Any]:
        """
        Set up WiFi on the board.
        
        Args:
            ssid: WiFi SSID
            password: WiFi password
            wait_for_connection: Whether to wait for the connection to be established
            timeout: Maximum time to wait for connection in seconds
            
        Returns:
            Dict[str, Any]: Status information including success and IP address if available
            
        Raises:
            TypeError: If the transport is not a SerialTransport
            ValueError: If the board is not a Duet board
        """
        if not isinstance(self.transport, SerialTransport):
            raise TypeError("WiFi setup requires a serial transport")
        
        if not self._is_duet:
            raise ValueError("The connected board is not a Duet board")
        
        return setup_wifi(self.transport, ssid, password, wait_for_connection, timeout)
    
    def get_network_status(self) -> Dict[str, Any]:
        """
        Get the current network status of the board.
        
        Returns:
            Dict[str, Any]: Network status information
            
        Raises:
            ValueError: If the board is not a Duet board
        """
        if not self._is_duet:
            raise ValueError("The connected board is not a Duet board")
        
        return get_network_status(self.transport)
    
    def scan_wifi_networks(self, timeout: int = 10) -> List[Dict[str, Any]]:
        """
        Scan for available WiFi networks.
        
        Args:
            timeout: Maximum time to wait for scan results in seconds
            
        Returns:
            List[Dict[str, Any]]: List of available WiFi networks
            
        Raises:
            TypeError: If the transport is not a SerialTransport
            ValueError: If the board is not a Duet board
        """
        if not isinstance(self.transport, SerialTransport):
            raise TypeError("WiFi scanning requires a serial transport")
        
        if not self._is_duet:
            raise ValueError("The connected board is not a Duet board")
        
        return scan_wifi_networks(self.transport, timeout)
    
    def configure_access_point(self, ssid: str, password: Optional[str] = None,
                              channel: Optional[int] = None) -> bool:
        """
        Configure the board as a WiFi access point.
        
        Args:
            ssid: SSID for the access point
            password: Password for the access point (optional)
            channel: WiFi channel (optional)
            
        Returns:
            bool: True if configuration was successful, False otherwise
            
        Raises:
            TypeError: If the transport is not a SerialTransport
            ValueError: If the board is not a Duet board
        """
        if not isinstance(self.transport, SerialTransport):
            raise TypeError("Access point configuration requires a serial transport")
        
        if not self._is_duet:
            raise ValueError("The connected board is not a Duet board")
        
        return configure_access_point(self.transport, ssid, password, channel)
    
    def enable_network_protocol(self, protocol: int, enable: bool = True) -> bool:
        """
        Enable or disable a network protocol.
        
        Args:
            protocol: Protocol number (0=HTTP, 1=FTP, 2=Telnet, 3=MQTT)
            enable: True to enable, False to disable
            
        Returns:
            bool: True if configuration was successful, False otherwise
            
        Raises:
            ValueError: If the board is not a Duet board
        """
        if not self._is_duet:
            raise ValueError("The connected board is not a Duet board")
        
        return enable_network_protocol(self.transport, protocol, enable)
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """
        Get diagnostic information from the board.
        
        Returns:
            Dict[str, Any]: Diagnostic information
            
        Raises:
            ValueError: If the board is not a Duet board
        """
        if not self._is_duet:
            raise ValueError("The connected board is not a Duet board")
        
        return get_board_diagnostics(self.transport)
    
    def transition_to_wifi(self, ssid: str, password: str, timeout: int = 30) -> Optional[HttpTransport]:
        """
        Transition from serial to WiFi connectivity.
        
        Args:
            ssid: WiFi SSID
            password: WiFi password
            timeout: Maximum time to wait for connection in seconds
            
        Returns:
            Optional[HttpTransport]: A new HTTP transport if successful, None otherwise
            
        Raises:
            TypeError: If the transport is not a SerialTransport
            ValueError: If the board is not a Duet board
        """
        if not isinstance(self.transport, SerialTransport):
            raise TypeError("Transition requires a serial transport")
        
        if not self._is_duet:
            raise ValueError("The connected board is not a Duet board")
        
        # Configure WiFi
        result = self.setup_wifi(ssid, password, wait_for_connection=True, timeout=timeout)
        if not result["success"]:
            if self.debug:
                print(f"DEBUG: WiFi setup failed: {result['message']}")
            return None
        
        # Get IP address
        ip_address = result.get("ip_address")
        if not ip_address:
            if self.debug:
                print("DEBUG: No IP address obtained")
            return None
        
        # Create HTTP transport
        if self.debug:
            print(f"DEBUG: Creating HTTP transport with IP {ip_address}")
            
        http_transport = HttpTransport(f"http://{ip_address}")
        
        # Test connection
        try:
            if http_transport.connect():
                if self.debug:
                    print("DEBUG: HTTP connection successful")
                return http_transport
            else:
                if self.debug:
                    print("DEBUG: HTTP connection failed")
                return None
        except Exception as e:
            if self.debug:
                print(f"DEBUG: Error connecting via HTTP: {e}")
            return None
    
    def disconnect(self) -> None:
        """
        Disconnect from the board.
        """
        if self.transport:
            self.transport.disconnect() 