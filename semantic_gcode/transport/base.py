"""
Base transport interface for G-code communication.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class Transport(ABC):
    """
    Abstract base class for G-code transport mechanisms.
    
    This class defines the interface for sending G-code commands to a device
    and querying its status. Concrete implementations handle specific protocols
    like HTTP, Serial, or Telnet.
    """
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Establish a connection to the device.
        
        Returns:
            bool: True if connection was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """
        Close the connection to the device.
        """
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if the transport is currently connected.
        
        Returns:
            bool: True if connected, False otherwise
        """
        pass
    
    @abstractmethod
    def send_line(self, line: str) -> bool:
        """
        Send a single line of G-code to the device.
        
        Args:
            line: The G-code command to send
            
        Returns:
            bool: True if the command was sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def query(self, query_cmd: str) -> Optional[str]:
        """
        Send a query command and get the response.
        
        Args:
            query_cmd: The query command to send
            
        Returns:
            Optional[str]: The response from the device, or None if no response
        """
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the device.
        
        Returns:
            Dict[str, Any]: A dictionary containing the device status
        """
        pass
