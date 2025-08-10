"""
M552: Set IP address, enable/disable network interface

This command has multiple distinct operational modes:
1. Query mode (no parameters): Reports current network state and IP address
2. WiFi hardware control (S=-1): Disables WiFi at the hardware level
3. Network state control (S=0/1/2): Disables/enables networking or sets access point mode
4. IP configuration (P parameter): Sets static IP or connects to WiFi network
"""

from typing import Optional, Dict, Any, Tuple, List, Callable
import re
from semantic_gcode.gcode.base import GCodeInstruction, register_gcode_instruction
from semantic_gcode.gcode.mixins import NetworkStatusProvider, ExpectsAcknowledgement

# Define operational modes for M552
class M552Mode:
    """Enumeration of operational modes for M552 command."""
    QUERY = "query"                # No parameters, query status
    WIFI_HARDWARE = "wifi_hw"      # S=-1, control WiFi hardware
    NETWORK_STATE = "network_state" # S=0/1/2, control network state
    IP_CONFIG = "ip_config"        # P parameter, set IP or SSID
    COMBINED = "combined"          # Multiple parameters combined

@register_gcode_instruction
class M552_NetworkControl(GCodeInstruction, NetworkStatusProvider, ExpectsAcknowledgement):
    """
    M552: Set IP address, enable/disable network interface
    
    This command has multiple distinct operational modes:
    1. Query mode (no parameters): Reports current network state and IP address
    2. WiFi hardware control (S=-1): Disables WiFi at the hardware level
    3. Network state control (S=0/1/2): Disables/enables networking or sets access point mode
    4. IP configuration (P parameter): Sets static IP or connects to WiFi network
    
    Parameters:
    - I: Network interface number (optional, defaults to 0)
    - P: IP address or SSID (depending on context)
    - S: Network state:
        -1 = disable WiFi module at hardware level
        0 = disable networking (put WiFi in idle mode)
        1 = enable networking as client
        2 = enable networking as access point
    - R: HTTP port (deprecated in RepRapFirmware 1.17+)
    
    Examples:
    - M552                    ; Query mode: Report current network state and IP address
    - M552 S-1                ; WiFi hardware mode: Disable WiFi at hardware level
    - M552 S0                 ; Network state mode: Disable networking (idle mode)
    - M552 S1                 ; Network state mode: Enable networking as client
    - M552 S2                 ; Network state mode: Enable networking as access point
    - M552 P192.168.1.14      ; IP config mode: Set static IP address
    - M552 S1 P192.168.1.14   ; Combined mode: Enable networking with static IP
    - M552 S1 P"MyNetwork"    ; Combined mode: Connect to WiFi network with SSID "MyNetwork"
    - M552 I1 S1 P0.0.0.0     ; Combined mode: Set second interface to use DHCP and enable it
    
    Notes:
    - M552 with no parameters reports the current network state and IP address
    - In SBC mode, sending this command makes a persistent change
    """
    code_type = "M"
    code_number = 552
    
    # Valid parameters for this command
    valid_parameters = ["I", "P", "S", "R"]
    
    # Network state descriptions
    network_states = {
        -1: "WiFi module disabled at hardware level",
        0: "Networking disabled (WiFi in idle mode)",
        1: "Networking enabled as client",
        2: "Networking enabled as access point"
    }
    
    @classmethod
    def create(cls, 
               interface: Optional[int] = None,
               ip_address: Optional[str] = None,
               ssid: Optional[str] = None,
               state: Optional[int] = None,
               http_port: Optional[int] = None) -> 'M552_NetworkControl':
        """
        Create an M552 network control instruction.
        
        Args:
            interface: Network interface number (I parameter)
            ip_address: IP address (P parameter if it looks like an IP)
            ssid: WiFi SSID (P parameter if it doesn't look like an IP)
            state: Network state (S parameter, -1=disable hardware, 0=disable, 1=enable, 2=AP mode)
            http_port: HTTP port (R parameter, deprecated)
            
        Returns:
            M552_NetworkControl: A network control instruction
            
        Raises:
            ValueError: If both ip_address and ssid are specified
        """
        parameters = {}
        
        # Validate that only one P parameter type is specified
        if ip_address is not None and ssid is not None:
            raise ValueError("Cannot specify both IP address and SSID for P parameter")
        
        # Add parameters if specified
        if interface is not None:
            parameters['I'] = interface
        
        if ip_address is not None:
            parameters['P'] = ip_address
        elif ssid is not None:
            parameters['P'] = f'"{ssid}"'
        
        if state is not None:
            if state not in [-1, 0, 1, 2]:
                raise ValueError("State must be -1, 0, 1, or 2")
            parameters['S'] = state
        
        if http_port is not None:
            parameters['R'] = http_port
        
        # Create comment based on the operation mode
        mode = cls._determine_mode(parameters)
        
        if mode == M552Mode.QUERY:
            comment = "Query network status"
        elif mode == M552Mode.WIFI_HARDWARE:
            comment = "Disable WiFi module at hardware level"
        elif mode == M552Mode.NETWORK_STATE:
            state_value = parameters['S']
            comment = cls.network_states.get(state_value, "Configure network state")
        elif mode == M552Mode.IP_CONFIG:
            if 'P' in parameters:
                p_value = parameters['P']
                if isinstance(p_value, str) and p_value.startswith('"') and p_value.endswith('"'):
                    comment = f"Configure WiFi network {p_value}"
                else:
                    comment = f"Set IP address to {p_value}"
            else:
                comment = "Configure network"
        else:  # COMBINED
            # Build a more descriptive comment for combined operations
            parts = []
            
            if 'S' in parameters:
                parts.append(cls.network_states.get(parameters['S'], "Configure network"))
                
            if 'P' in parameters:
                p_value = parameters['P']
                if isinstance(p_value, str) and p_value.startswith('"') and p_value.endswith('"'):
                    parts.append(f"with SSID {p_value}")
                else:
                    parts.append(f"with IP {p_value}")
                    
            if 'I' in parameters:
                parts.append(f"on interface {parameters['I']}")
                
            comment = " ".join(parts)
        
        return cls(
            code_type="M",
            code_number=552,
            parameters=parameters,
            comment=comment
        )
    
    @staticmethod
    def _determine_mode(parameters: Dict[str, Any]) -> str:
        """
        Determine the operational mode of the M552 command based on parameters.
        
        Args:
            parameters: The command parameters
            
        Returns:
            str: The operational mode
        """
        if not parameters:
            return M552Mode.QUERY
            
        if 'S' in parameters and parameters['S'] == -1:
            return M552Mode.WIFI_HARDWARE
            
        if 'S' in parameters and 'P' not in parameters:
            return M552Mode.NETWORK_STATE
            
        if 'P' in parameters and 'S' not in parameters:
            return M552Mode.IP_CONFIG
            
        return M552Mode.COMBINED
    
    def get_mode(self) -> str:
        """
        Get the operational mode of this M552 command instance.
        
        Returns:
            str: The operational mode
        """
        return self._determine_mode(self.parameters)
    
    def get_description(self) -> str:
        """
        Get a human-readable description of what this command instance does.
        
        Returns:
            str: Description of the command's action
        """
        mode = self.get_mode()
        
        if mode == M552Mode.QUERY:
            return "Query network status and IP address"
            
        if mode == M552Mode.WIFI_HARDWARE:
            return "Disable WiFi module at hardware level"
            
        if mode == M552Mode.NETWORK_STATE:
            state_value = self.parameters['S']
            return self.network_states.get(state_value, "Configure network state")
            
        if mode == M552Mode.IP_CONFIG:
            p_value = self.parameters['P']
            if isinstance(p_value, str) and p_value.startswith('"') and p_value.endswith('"'):
                ssid = p_value.strip('"')
                return f"Configure WiFi network with SSID {ssid}"
            else:
                return f"Set IP address to {p_value}"
                
        # COMBINED mode
        parts = []
        
        if 'S' in self.parameters:
            s_value = self.parameters['S']
            if s_value == 0:
                parts.append("Disable networking")
            elif s_value == 1:
                parts.append("Enable networking as client")
            elif s_value == 2:
                parts.append("Enable networking as access point")
                
        if 'P' in self.parameters:
            p_value = self.parameters['P']
            if isinstance(p_value, str) and p_value.startswith('"') and p_value.endswith('"'):
                ssid = p_value.strip('"')
                parts.append(f"connect to WiFi SSID {ssid}")
            else:
                parts.append(f"set IP address to {p_value}")
                
        if 'I' in self.parameters:
            parts.append(f"on interface {self.parameters['I']}")
            
        return ", ".join(parts)
    
    def apply(self, state: dict) -> dict:
        """
        Update machine state with network configuration.
        
        Args:
            state: Current machine state
            
        Returns:
            dict: Updated machine state with network configuration
        """
        # Create network state if it doesn't exist
        if "network" not in state:
            state["network"] = {}
        
        # Get the operational mode
        mode = self.get_mode()
        
        # Update network state based on operational mode and parameters
        if mode == M552Mode.QUERY:
            # Query mode doesn't change state
            pass
            
        elif mode == M552Mode.WIFI_HARDWARE:
            # WiFi hardware mode
            state["network"]["wifi_enabled"] = False
            state["network"]["hardware_state"] = "disabled"
            
        elif mode == M552Mode.NETWORK_STATE:
            # Network state mode
            s_value = self.parameters['S']
            if s_value == 0:
                state["network"]["enabled"] = False
                state["network"]["state"] = "disabled"
            elif s_value == 1:
                state["network"]["enabled"] = True
                state["network"]["state"] = "client"
            elif s_value == 2:
                state["network"]["enabled"] = True
                state["network"]["state"] = "access_point"
                
        elif mode == M552Mode.IP_CONFIG:
            # IP config mode
            p_value = self.parameters['P']
            if isinstance(p_value, str) and p_value.startswith('"') and p_value.endswith('"'):
                # It's an SSID
                state["network"]["ssid"] = p_value.strip('"')
            else:
                # It's an IP address
                state["network"]["ip_address"] = p_value
                
        else:  # COMBINED mode
            # Update interface if specified
            if 'I' in self.parameters:
                state["network"]["interface"] = self.parameters['I']
            
            # Update network state if specified
            if 'S' in self.parameters:
                s_value = self.parameters['S']
                if s_value == -1:
                    state["network"]["wifi_enabled"] = False
                    state["network"]["hardware_state"] = "disabled"
                elif s_value == 0:
                    state["network"]["enabled"] = False
                    state["network"]["state"] = "disabled"
                elif s_value == 1:
                    state["network"]["enabled"] = True
                    state["network"]["state"] = "client"
                elif s_value == 2:
                    state["network"]["enabled"] = True
                    state["network"]["state"] = "access_point"
            
            # Update IP/SSID if specified
            if 'P' in self.parameters:
                p_value = self.parameters['P']
                if isinstance(p_value, str) and p_value.startswith('"') and p_value.endswith('"'):
                    # It's an SSID
                    state["network"]["ssid"] = p_value.strip('"')
                else:
                    # It's an IP address
                    state["network"]["ip_address"] = p_value
            
            # Update HTTP port if specified
            if 'R' in self.parameters:
                state["network"]["http_port"] = self.parameters['R']
        
        return state
    
    def execute(self, device) -> Optional[str]:
        """
        Send the M552 command to the device and process the response.
        
        This method overrides the default execute method to extract
        network status information from the response.
        
        Args:
            device: The device to send the command to
            
        Returns:
            Optional[str]: The response from the device, or None if no response
        """
        # Send the command
        response = device.send(str(self))
        
        if response:
            # Extract network information from response
            ip_address = self.extract_ip_address(response)
            network_state = self.extract_network_state(response)
            
            # Update device state if information was found
            if hasattr(device, 'update_network_info') and (ip_address or network_state):
                device.update_network_info(ip_address, network_state)
        
        return response
    
    def get_help(self) -> str:
        """
        Get detailed help information about the M552 command.
        
        Returns:
            str: Multi-line help text explaining the command's modes and parameters
        """
        help_text = [
            "M552: Set IP address, enable/disable network interface",
            "",
            "Operational Modes:",
            "1. Query mode (M552): Reports current network state and IP address",
            "2. WiFi hardware control (M552 S-1): Disables WiFi at the hardware level",
            "3. Network state control:",
            "   - M552 S0: Disable networking (put WiFi in idle mode)",
            "   - M552 S1: Enable networking as client",
            "   - M552 S2: Enable networking as access point",
            "4. IP configuration:",
            "   - M552 P192.168.1.14: Set static IP address",
            "   - M552 P\"MyNetwork\": Configure WiFi network SSID",
            "",
            "Parameters:",
            "- I: Network interface number (optional, defaults to 0)",
            "- P: IP address (e.g., 192.168.1.14) or SSID (e.g., \"MyNetwork\")",
            "- S: Network state (-1=disable hardware, 0=disable, 1=enable client, 2=enable AP)",
            "- R: HTTP port (deprecated in RepRapFirmware 1.17+)",
            "",
            "Examples:",
            "- M552                    ; Query network status",
            "- M552 S-1                ; Disable WiFi module at hardware level",
            "- M552 S0                 ; Disable networking",
            "- M552 S1                 ; Enable networking as client",
            "- M552 S1 P192.168.1.14   ; Enable networking with static IP",
            "- M552 S1 P\"MyNetwork\"    ; Connect to WiFi network",
            "- M552 I1 S1 P0.0.0.0     ; Set second interface to use DHCP and enable it"
        ]
        
        return "\n".join(help_text)

# For backward compatibility
def m552(interface=None, ip_address=None, ssid=None, state=None, http_port=None):
    """
    Implementation for M552: Set IP address, enable/disable network interface
    
    Args:
        interface: Network interface number (I parameter)
        ip_address: IP address (P parameter if it looks like an IP)
        ssid: WiFi SSID (P parameter if it doesn't look like an IP)
        state: Network state (S parameter, -1=disable hardware, 0=disable, 1=enable, 2=AP mode)
        http_port: HTTP port (R parameter, deprecated)
    """
    return M552_NetworkControl.create(
        interface=interface,
        ip_address=ip_address,
        ssid=ssid,
        state=state,
        http_port=http_port
    )

if __name__ == "__main__":
    print("GCode command: M552")
    
    # Test different modes
    print("\nQuery mode:")
    instruction = m552()
    print(f"- Command: {str(instruction)}")
    print(f"- Mode: {instruction.get_mode()}")
    print(f"- Description: {instruction.get_description()}")
    
    print("\nWiFi hardware mode:")
    instruction = m552(state=-1)
    print(f"- Command: {str(instruction)}")
    print(f"- Mode: {instruction.get_mode()}")
    print(f"- Description: {instruction.get_description()}")
    
    print("\nNetwork state mode:")
    instruction = m552(state=0)
    print(f"- Command: {str(instruction)}")
    print(f"- Mode: {instruction.get_mode()}")
    print(f"- Description: {instruction.get_description()}")
    
    print("\nIP config mode:")
    instruction = m552(ip_address="192.168.1.14")
    print(f"- Command: {str(instruction)}")
    print(f"- Mode: {instruction.get_mode()}")
    print(f"- Description: {instruction.get_description()}")
    
    print("\nCombined mode:")
    instruction = m552(ip_address="192.168.1.14", state=1)
    print(f"- Command: {str(instruction)}")
    print(f"- Mode: {instruction.get_mode()}")
    print(f"- Description: {instruction.get_description()}")
    
    print("\nHelp information:")
    print(instruction.get_help())
