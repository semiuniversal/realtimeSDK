"""
Configuration manager for the Realtime Hairbrush SDK.

This module provides a configuration manager that handles loading, saving,
and accessing configuration values.
"""

import os
import json
from typing import Dict, Any, Optional, List, Tuple, Union

# Remove pkg_resources import
# import pkg_resources

from realtime_hairbrush.transport.config import ConnectionConfig


class ConfigManager:
    """
    Configuration manager for the Realtime Hairbrush SDK.
    
    This class handles loading, saving, and accessing configuration values.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Path to the configuration file. If None, the default
                         configuration will be used.
        """
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """
        Load the default configuration.
        
        Returns:
            Dict[str, Any]: Default configuration
        """
        default_config_path = os.path.join(
            os.path.dirname(__file__), 
            'default_config.json'
        )
        
        try:
            with open(default_config_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Fallback to minimal default configuration
            return {
                "connection": {
                    "transport_type": "serial",
                    "serial_port": "/dev/ttyACM0",
                    "serial_baudrate": 115200,
                    "http_host": "duet3.local",
                    "timeout": 5.0
                },
                "machine": {
                    "name": "H.Airbrush",
                    "safe_z_height": 5.0,
                    "spray_z_height": 1.5,
                    "tool_offsets": [
                        {"X": 0, "Y": 0, "Z": 0},
                        {"X": 100, "Y": -25, "Z": 0}
                    ]
                }
            }
    
    def _load_config(self) -> None:
        """
        Load the configuration from the file or use the default configuration.
        """
        # Start with the default configuration
        self.config = self._load_default_config()
        
        # If a config file is specified and exists, load it
        if self.config_file and os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                
                # Merge the user configuration with the default configuration
                self._merge_configs(self.config, user_config)
            except json.JSONDecodeError:
                # If the file is not valid JSON, use the default configuration
                pass
    
    def _merge_configs(self, base_config: Dict[str, Any], override_config: Dict[str, Any]) -> None:
        """
        Merge the override configuration into the base configuration.
        
        Args:
            base_config: Base configuration to merge into
            override_config: Configuration to merge from
        """
        for key, value in override_config.items():
            if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
                # Recursively merge dictionaries
                self._merge_configs(base_config[key], value)
            else:
                # Override or add the value
                base_config[key] = value
    
    def save_config(self, config_file: Optional[str] = None) -> None:
        """
        Save the configuration to a file.
        
        Args:
            config_file: Path to the configuration file. If None, the current
                         config_file will be used.
        """
        file_path = config_file or self.config_file
        if not file_path:
            raise ValueError("No configuration file specified")
        
        with open(file_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        # Update the config_file if a new one was specified
        if config_file:
            self.config_file = config_file
    
    def save_connection_config(self, connection_settings: Dict[str, Any]) -> None:
        """
        Save the connection configuration.
        
        Args:
            connection_settings: Connection settings to save
        """
        # Update the connection settings in the config
        if "connection" not in self.config:
            self.config["connection"] = {}
            
        # Update only the provided settings
        for key, value in connection_settings.items():
            if value is not None:  # Only update if the value is not None
                self.config["connection"][key] = value
        
        # Save the config to the file if one is specified
        if self.config_file:
            try:
                self.save_config()
            except Exception as e:
                print(f"Warning: Failed to save connection settings: {e}")
        
        # Also save to a settings.yaml file in the user's home directory
        try:
            import yaml
            settings_dir = os.path.expanduser("~/.realtime_hairbrush")
            os.makedirs(settings_dir, exist_ok=True)
            settings_file = os.path.join(settings_dir, "settings.yaml")
            
            # Load existing settings if available
            settings = {}
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = yaml.safe_load(f) or {}
            
            # Update connection settings
            if "connection" not in settings:
                settings["connection"] = {}
            for key, value in connection_settings.items():
                if value is not None:
                    settings["connection"][key] = value
            
            # Save settings
            with open(settings_file, 'w') as f:
                yaml.dump(settings, f, default_flow_style=False)
        except Exception as e:
            print(f"Warning: Failed to save settings to settings.yaml: {e}")
    
    def get_connection_config(self) -> ConnectionConfig:
        """
        Get the connection configuration.
        
        Returns:
            ConnectionConfig: Connection configuration
        """
        return ConnectionConfig.from_dict(self.config.get("connection", {}))
    
    def get_machine_config(self) -> Dict[str, Any]:
        """
        Get the machine configuration.
        
        Returns:
            Dict[str, Any]: Machine configuration
        """
        return self.config.get("machine", {})
    
    def get_air_control_config(self) -> Dict[str, Any]:
        """
        Get the air control configuration.
        
        Returns:
            Dict[str, Any]: Air control configuration
        """
        return self.config.get("air_control", {})
    
    def get_paint_flow_config(self) -> Dict[str, Any]:
        """
        Get the paint flow configuration.
        
        Returns:
            Dict[str, Any]: Paint flow configuration
        """
        return self.config.get("paint_flow", {})
    
    def get_motion_config(self) -> Dict[str, Any]:
        """
        Get the motion configuration.
        
        Returns:
            Dict[str, Any]: Motion configuration
        """
        return self.config.get("motion", {})
    
    def get_cli_config(self) -> Dict[str, Any]:
        """
        Get the CLI configuration.
        
        Returns:
            Dict[str, Any]: CLI configuration
        """
        return self.config.get("cli", {})
    
    def get_value(self, path: str, default: Any = None) -> Any:
        """
        Get a configuration value by path.
        
        Args:
            path: Path to the configuration value (e.g., "machine.name")
            default: Default value to return if the path does not exist
            
        Returns:
            Any: Configuration value
        """
        parts = path.split('.')
        value = self.config
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        
        return value
    
    def set_value(self, path: str, value: Any) -> None:
        """
        Set a configuration value by path.
        
        Args:
            path: Path to the configuration value (e.g., "machine.name")
            value: Value to set
        """
        parts = path.split('.')
        config = self.config
        
        # Navigate to the parent of the value to set
        for part in parts[:-1]:
            if part not in config:
                config[part] = {}
            config = config[part]
        
        # Set the value
        config[parts[-1]] = value
    
    def get_tool_offset(self, tool_index: int) -> Dict[str, float]:
        """
        Get the offset for the specified tool.
        
        Args:
            tool_index: Tool index (0 or 1)
            
        Returns:
            Dict[str, float]: Tool offset
        """
        tool_offsets = self.get_value("machine.tool_offsets", [{"X": 0, "Y": 0, "Z": 0}])
        if tool_index < len(tool_offsets):
            return tool_offsets[tool_index]
        return {"X": 0, "Y": 0, "Z": 0}
    
    def get_fan_index(self, tool_index: int) -> int:
        """
        Get the fan index for the specified tool.
        
        Args:
            tool_index: Tool index (0 or 1)
            
        Returns:
            int: Fan index
        """
        air_control = self.get_air_control_config()
        if tool_index == 0:
            return air_control.get("tool_0_fan_index", 2)
        else:
            return air_control.get("tool_1_fan_index", 3)
    
    def get_flow_axis(self, tool_index: int) -> str:
        """
        Get the flow axis for the specified tool.
        
        Args:
            tool_index: Tool index (0 or 1)
            
        Returns:
            str: Flow axis
        """
        paint_flow = self.get_paint_flow_config()
        if tool_index == 0:
            return paint_flow.get("tool_0_axis", "U")
        else:
            return paint_flow.get("tool_1_axis", "V")
    
    def get_safe_z_height(self) -> float:
        """
        Get the safe Z height.
        
        Returns:
            float: Safe Z height
        """
        return self.get_value("machine.safe_z_height", 5.0)
    
    def get_spray_z_height(self) -> float:
        """
        Get the spray Z height.
        
        Returns:
            float: Spray Z height
        """
        return self.get_value("machine.spray_z_height", 1.5)
    
    def get_motion_limits(self) -> Dict[str, List[float]]:
        """
        Get the motion limits.
        
        Returns:
            Dict[str, List[float]]: Motion limits
        """
        return self.get_value("machine.motion_limits", {
            "X": [0, 695],
            "Y": [0, 1080],
            "Z": [0, 84],
            "U": [0, 4],
            "V": [0, 4]
        }) 