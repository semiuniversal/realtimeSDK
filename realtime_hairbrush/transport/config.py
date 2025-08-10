"""
Connection configuration for the Realtime Hairbrush SDK.

This module provides a configuration class for managing connection settings
for both serial and HTTP connections to the Duet board.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import json
import os


@dataclass
class ConnectionConfig:
    """
    Configuration for connecting to the Duet board.
    """
    # Transport type: "serial" or "http"
    transport_type: str = "serial"
    
    # Serial connection settings
    serial_port: str = ""
    serial_baudrate: int = 115200
    
    # HTTP connection settings
    http_host: str = "duet3.local"
    http_password: Optional[str] = None
    
    # Common settings
    timeout: float = 5.0
    
    # Additional settings
    additional_settings: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ConnectionConfig':
        """
        Create a ConnectionConfig from a dictionary.
        
        Args:
            config_dict: Dictionary containing configuration values
            
        Returns:
            ConnectionConfig: Configuration object
        """
        # Extract known fields
        transport_type = config_dict.pop("transport_type", "serial")
        serial_port = config_dict.pop("serial_port", "")
        serial_baudrate = config_dict.pop("serial_baudrate", 115200)
        http_host = config_dict.pop("http_host", "duet3.local")
        http_password = config_dict.pop("http_password", None)
        timeout = config_dict.pop("timeout", 5.0)
        
        # Any remaining keys go into additional_settings
        return cls(
            transport_type=transport_type,
            serial_port=serial_port,
            serial_baudrate=serial_baudrate,
            http_host=http_host,
            http_password=http_password,
            timeout=timeout,
            additional_settings=config_dict
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ConnectionConfig':
        """
        Create a ConnectionConfig from a JSON string.
        
        Args:
            json_str: JSON string containing configuration values
            
        Returns:
            ConnectionConfig: Configuration object
        """
        config_dict = json.loads(json_str)
        return cls.from_dict(config_dict)
    
    @classmethod
    def from_file(cls, file_path: str) -> 'ConnectionConfig':
        """
        Create a ConnectionConfig from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            ConnectionConfig: Configuration object
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        with open(file_path, 'r') as f:
            config_dict = json.load(f)
        
        return cls.from_dict(config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the configuration
        """
        result = {
            "transport_type": self.transport_type,
            "serial_port": self.serial_port,
            "serial_baudrate": self.serial_baudrate,
            "http_host": self.http_host,
            "timeout": self.timeout
        }
        
        # Only include password if it's set
        if self.http_password:
            result["http_password"] = self.http_password
        
        # Add additional settings
        result.update(self.additional_settings)
        
        return result
    
    def to_json(self) -> str:
        """
        Convert the configuration to a JSON string.
        
        Returns:
            str: JSON representation of the configuration
        """
        return json.dumps(self.to_dict(), indent=2)
    
    def save_to_file(self, file_path: str) -> None:
        """
        Save the configuration to a JSON file.
        
        Args:
            file_path: Path to the JSON file
        """
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def validate(self) -> bool:
        """
        Validate the configuration.
        
        Returns:
            bool: True if the configuration is valid, False otherwise
        """
        if self.transport_type not in ["serial", "http"]:
            return False
        
        if self.transport_type == "serial" and not self.serial_port:
            return False
        
        if self.transport_type == "http" and not self.http_host:
            return False
        
        return True 