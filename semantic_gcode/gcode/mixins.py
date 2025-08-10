"""
Mixins for G-code instruction behaviors.

This module provides mixins that can be applied to G-code instructions
to define their behavior and characteristics.
"""

from typing import Optional, Dict, Any, List


class ModalInstruction:
    """
    Mixin indicating that a command affects the modal state of the machine.
    
    Modal instructions change the state of the machine in a way that affects
    subsequent commands. For example, G90 (absolute positioning) changes how
    subsequent movement commands are interpreted.
    """
    
    def affects_modal_state(self) -> bool:
        """
        Indicates that this command affects the modal state.
        
        Returns:
            bool: True
        """
        return True


class ImmediateInstruction:
    """
    Mixin indicating that a command executes immediately.
    
    Immediate instructions are executed as soon as they are received,
    without waiting for previous commands to complete.
    """
    
    def is_immediate(self) -> bool:
        """
        Indicates that this command executes immediately.
        
        Returns:
            bool: True
        """
        return True


class BlocksExecution:
    """
    Mixin indicating that a command blocks execution until completed.
    
    Blocking instructions prevent subsequent commands from being executed
    until they have completed. For example, M400 (wait for moves to complete)
    blocks execution until all motion has stopped.
    """
    
    def blocks_execution(self) -> bool:
        """
        Indicates that this command blocks execution until it completes.
        
        Returns:
            bool: True
        """
        return True


class ExpectsAcknowledgement:
    """
    Mixin indicating that a command expects an acknowledgement response.
    
    Commands with this mixin expect a specific acknowledgement string in the
    response, typically "ok". The command is not considered complete until
    this acknowledgement is received.
    """
    
    def get_expected_acknowledgement(self) -> str:
        """
        Get the expected acknowledgement string.
        
        Returns:
            str: The expected acknowledgement string (typically "ok")
        """
        return "ok"
    
    def validate_response(self, response: str) -> bool:
        """
        Validate if the response contains the expected acknowledgement.
        
        Args:
            response: The response from the device
            
        Returns:
            bool: True if the response contains the expected acknowledgement
        """
        expected = self.get_expected_acknowledgement()
        return expected in response.lower()


class NetworkStatusProvider:
    """
    Mixin indicating that a command provides network status information.
    
    Commands with this mixin can extract network status information from
    their response, such as IP addresses and network state.
    """
    
    def provides_network_status(self) -> bool:
        """
        Indicates that this command provides network status information.
        
        Returns:
            bool: True
        """
        return True
    
    def extract_ip_address(self, response: str) -> Optional[str]:
        """
        Extract the IP address from the command response.
        
        Args:
            response: The response from the device
            
        Returns:
            Optional[str]: The extracted IP address, or None if not found
        """
        import re
        
        # Try different patterns for IP address extraction
        patterns = [
            r'IP address = (\d+\.\d+\.\d+\.\d+)',  # RepRapFirmware format
            r'IP address (\d+\.\d+\.\d+\.\d+)',     # Alternative format
            r'IP: (\d+\.\d+\.\d+\.\d+)',           # Simplified format
            r'(\d+\.\d+\.\d+\.\d+)'                # Any IP address in the response
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response)
            if match:
                return match.group(1)
        
        return None
    
    def extract_network_state(self, response: str) -> Optional[str]:
        """
        Extract the network state from the command response.
        
        Args:
            response: The response from the device
            
        Returns:
            Optional[str]: The extracted network state, or None if not found
        """
        import re
        
        # Try different patterns for network state extraction
        patterns = [
            r'WiFi module is (\w+)',                # WiFi state
            r'Network state: (\w+)',                # General network state
            r'Ethernet is (\w+)',                   # Ethernet state
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response)
            if match:
                return match.group(1).lower()
        
        return None


class TemperatureProvider:
    """
    Mixin indicating that a command provides temperature information.
    
    Commands with this mixin can extract temperature information from
    their response, such as hotend and bed temperatures.
    """
    
    def provides_temperature(self) -> bool:
        """
        Indicates that this command provides temperature information.
        
        Returns:
            bool: True
        """
        return True
    
    def extract_temperatures(self, response: str) -> Dict[str, Dict[str, float]]:
        """
        Extract temperature information from the command response.
        
        Args:
            response: The response from the device
            
        Returns:
            Dict[str, Dict[str, float]]: Dictionary of temperature information
        """
        import re
        
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


class PositionProvider:
    """
    Mixin indicating that a command provides position information.
    
    Commands with this mixin can extract position information from
    their response, such as current axis positions.
    """
    
    def provides_position(self) -> bool:
        """
        Indicates that this command provides position information.
        
        Returns:
            bool: True
        """
        return True
    
    def extract_position(self, response: str) -> Dict[str, float]:
        """
        Extract position information from the command response.
        
        Args:
            response: The response from the device
            
        Returns:
            Dict[str, float]: Dictionary of axis positions
        """
        import re
        
        position = {}
        
        # Extract X, Y, Z, E positions
        for axis in ["X", "Y", "Z", "E", "U", "V", "W"]:
            match = re.search(rf'{axis}:(-?\d+\.?\d*)', response)
            if match:
                try:
                    position[axis.lower()] = float(match.group(1))
                except ValueError:
                    pass
        
        return position


class FirmwareInfoProvider:
    """
    Mixin indicating that a command provides firmware information.
    
    Commands with this mixin can extract firmware information from
    their response, such as firmware name, version, and board type.
    """
    
    def provides_firmware_info(self) -> bool:
        """
        Indicates that this command provides firmware information.
        
        Returns:
            bool: True
        """
        return True
    
    def extract_firmware_info(self, response: str) -> Dict[str, str]:
        """
        Extract firmware information from the command response.
        
        Args:
            response: The response from the device
            
        Returns:
            Dict[str, str]: Dictionary of firmware information
        """
        import re
        
        info = {}
        
        # Extract firmware name
        name_match = re.search(r'FIRMWARE_NAME:\s*([^,\n]+)', response)
        if name_match:
            info["name"] = name_match.group(1).strip()
        
        # Extract firmware version
        version_match = re.search(r'FIRMWARE_VERSION:\s*([0-9.]+)', response)
        if version_match:
            info["version"] = version_match.group(1).strip()
        
        # Extract board type
        board_match = re.search(r'ELECTRONICS:\s*([^,\n]+)', response)
        if board_match:
            info["board"] = board_match.group(1).strip()
        
        # Extract firmware date
        date_match = re.search(r'FIRMWARE_DATE:\s*([^,\n]+)', response)
        if date_match:
            info["date"] = date_match.group(1).strip()
        
        return info 