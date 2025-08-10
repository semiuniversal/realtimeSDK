"""
Network-related G-code instructions.

This module provides semantic instruction classes for network-related G-code commands,
such as configuring WiFi settings and managing network interfaces.
"""
import re
from typing import Optional, ClassVar, List, Dict, Any, Union

from .base import GInstruction, register_instruction


@register_instruction
class SetNetworkState(GInstruction):
    """
    Set IP address, enable/disable network interface.
    
    Example G-code: M552 S1 (enable networking as a client)
    Example G-code: M552 S2 (enable networking as an access point)
    Example G-code: M552 S0 (disable networking)
    Example G-code: M552 P"MyNetwork" (connect to specific SSID)
    Example G-code: M552 I1 S1 (enable WiFi interface on Duet 3)
    """
    code = "M552"
    accepted_args = ["I", "P", "S"]
    
    def __init__(self, S: int, P: Optional[str] = None, I: Optional[int] = None):
        """
        Initialize a network state setting instruction.
        
        Args:
            S: Network state (0=disable, 1=enable as client, 2=enable as AP, -1=disable WiFi module)
            P: SSID to connect to (optional)
            I: Interface number (0=Ethernet, 1=WiFi on Duet 3) (optional)
        """
        args = {"S": S}
        if P is not None:
            args["P"] = P
        if I is not None:
            args["I"] = I
        super().__init__(**args)
    
    def to_gcode(self) -> str:
        """
        Convert to G-code string.
        
        Returns:
            str: G-code representation (e.g., "M552 S1")
        """
        result = f"M552 S{self.args['S']}"
        
        if "I" in self.args:
            result += f" I{self.args['I']}"
            
        if "P" in self.args:
            result += f' P"{self.args["P"]}"'
            
        return result
    
    @classmethod
    def from_gcode(cls, line: str) -> Optional['SetNetworkState']:
        """
        Parse a G-code string into a SetNetworkState instruction.
        
        Args:
            line: The G-code string to parse
            
        Returns:
            SetNetworkState: An instance, or None if the line doesn't match
        """
        # Check if this is an M552 command
        if not line.strip().startswith("M552"):
            return None
        
        # Extract parameters
        params: Dict[str, Any] = {}
        
        # Extract S parameter (required)
        s_match = re.search(r'S(-?\d+)', line)
        if s_match:
            params["S"] = int(s_match.group(1))
        else:
            return None  # S parameter is required
        
        # Extract I parameter (optional)
        i_match = re.search(r'I(\d+)', line)
        if i_match:
            params["I"] = int(i_match.group(1))
        
        # Extract P parameter (optional, quoted SSID)
        p_match = re.search(r'\bP"([^"]*)"', line)
        if p_match:
            params["P"] = p_match.group(1)
        
        return cls(**params)
    
    def describe(self) -> str:
        """
        Provide a human-readable description.
        
        Returns:
            str: Description of the instruction
        """
        states = {
            0: "disable networking",
            1: "enable networking as a client",
            2: "enable networking as an access point",
            -1: "disable WiFi module"
        }
        
        state_str = states.get(self.args["S"], f"set network state to {self.args['S']}")
        interface_str = f" on interface {self.args['I']}" if "I" in self.args else ""
        ssid_str = f" and connect to '{self.args['P']}'" if "P" in self.args else ""
        
        return f"{state_str}{interface_str}{ssid_str}"


@register_instruction
class ReportNetworkInterfaces(GInstruction):
    """
    Report network interfaces.
    
    Example G-code: M552.1 (report network interfaces)
    """
    code = "M552.1"
    accepted_args: List[str] = []  # No parameters
    
    def to_gcode(self) -> str:
        """
        Convert to G-code string.
        
        Returns:
            str: G-code representation (e.g., "M552.1")
        """
        return "M552.1"
    
    @classmethod
    def from_gcode(cls, line: str) -> Optional['ReportNetworkInterfaces']:
        """
        Parse a G-code string into a ReportNetworkInterfaces instruction.
        
        Args:
            line: The G-code string to parse
            
        Returns:
            ReportNetworkInterfaces: An instance, or None if the line doesn't match
        """
        # Check if this is an M552.1 command
        if line.strip() == "M552.1":
            return cls()
        return None
    
    def describe(self) -> str:
        """
        Provide a human-readable description.
        
        Returns:
            str: Description of the instruction
        """
        return "Report network interfaces"


@register_instruction
class ConfigureWiFiSettings(GInstruction):
    """
    Configure WiFi network credentials.
    
    Example G-code: M587 S"MyNetwork" P"MyPassword" (configure WiFi credentials)
    Example G-code: M587 S"MyNetwork" P"MyPassword" I1 (configure WiFi credentials for interface 1)
    Example G-code: M587 S"MyNetwork" P"MyPassword" E1 (enable DHCP)
    Example G-code: M587 S"MyNetwork" P"MyPassword" IP"192.168.1.100" NM"255.255.255.0" GW"192.168.1.1" (static IP)
    """
    code = "M587"
    accepted_args = ["S", "P", "I", "E", "IP", "NM", "GW"]
    
    def __init__(self, S: str, P: str, I: Optional[int] = None, E: Optional[int] = None,
                 IP: Optional[str] = None, NM: Optional[str] = None, GW: Optional[str] = None):
        """
        Initialize a WiFi settings configuration instruction.
        
        Args:
            S: SSID of the WiFi network
            P: Password for the WiFi network
            I: Interface number (optional)
            E: DHCP enable (1) or disable (0) (optional)
            IP: Static IP address (optional)
            NM: Subnet mask (optional)
            GW: Gateway address (optional)
        """
        args = {"S": S, "P": P}
        if I is not None:
            args["I"] = I
        if E is not None:
            args["E"] = E
        if IP is not None:
            args["IP"] = IP
        if NM is not None:
            args["NM"] = NM
        if GW is not None:
            args["GW"] = GW
        super().__init__(**args)
    
    def to_gcode(self) -> str:
        """
        Convert to G-code string.
        
        Returns:
            str: G-code representation (e.g., "M587 S\"MyNetwork\" P\"MyPassword\"")
        """
        result = f'M587 S"{self.args["S"]}" P"{self.args["P"]}"'
        
        if "I" in self.args:
            result += f" I{self.args['I']}"
        if "E" in self.args:
            result += f" E{self.args['E']}"
        if "IP" in self.args:
            result += f' IP"{self.args["IP"]}"'
        if "NM" in self.args:
            result += f' NM"{self.args["NM"]}"'
        if "GW" in self.args:
            result += f' GW"{self.args["GW"]}"'
            
        return result
    
    @classmethod
    def from_gcode(cls, line: str) -> Optional['ConfigureWiFiSettings']:
        """
        Parse a G-code string into a ConfigureWiFiSettings instruction.
        
        Args:
            line: The G-code string to parse
            
        Returns:
            ConfigureWiFiSettings: An instance, or None if the line doesn't match
        """
        # Check if this is an M587 command
        if not line.strip().startswith("M587"):
            return None
        
        # Extract parameters
        params: Dict[str, Any] = {}
        
        # Extract S parameter (required, quoted SSID)
        s_match = re.search(r'\bS"([^"]*)"', line)
        if s_match:
            params["S"] = s_match.group(1)
        else:
            return None  # S parameter is required
        
        # Extract P parameter (required, quoted password)
        p_match = re.search(r'\bP"([^"]*)"', line)
        if p_match:
            params["P"] = p_match.group(1)
        else:
            return None  # P parameter is required
        
        # Extract I parameter (optional)
        i_match = re.search(r'I(\d+)', line)
        if i_match:
            params["I"] = int(i_match.group(1))
        
        # Extract E parameter (optional)
        e_match = re.search(r'E(\d+)', line)
        if e_match:
            params["E"] = int(e_match.group(1))
        
        # Extract IP parameter (optional, quoted IP)
        ip_match = re.search(r'\bIP"([^"]*)"', line)
        if ip_match:
            params["IP"] = ip_match.group(1)
        
        # Extract NM parameter (optional, quoted netmask)
        nm_match = re.search(r'\bNM"([^"]*)"', line)
        if nm_match:
            params["NM"] = nm_match.group(1)
        
        # Extract GW parameter (optional, quoted gateway)
        gw_match = re.search(r'\bGW"([^"]*)"', line)
        if gw_match:
            params["GW"] = gw_match.group(1)
        
        return cls(**params)
    
    def describe(self) -> str:
        """
        Provide a human-readable description.
        
        Returns:
            str: Description of the instruction
        """
        description = f"Configure WiFi credentials for network '{self.args['S']}'"
        
        if "I" in self.args:
            description += f" on interface {self.args['I']}"
        
        if "E" in self.args:
            description += f", DHCP {'enabled' if self.args['E'] == 1 else 'disabled'}"
        
        if "IP" in self.args:
            description += f", static IP {self.args['IP']}"
        
        return description


@register_instruction
class ListWiFiNetworks(GInstruction):
    """
    Scan for available WiFi networks.
    
    Example G-code: M588 (scan for WiFi networks)
    Example G-code: M588 I1 (scan for WiFi networks on interface 1)
    """
    code = "M588"
    accepted_args = ["I"]
    
    def __init__(self, I: Optional[int] = None):
        """
        Initialize a WiFi network scanning instruction.
        
        Args:
            I: Interface number (optional)
        """
        args = {}
        if I is not None:
            args["I"] = I
        super().__init__(**args)
    
    def to_gcode(self) -> str:
        """
        Convert to G-code string.
        
        Returns:
            str: G-code representation (e.g., "M588")
        """
        result = "M588"
        
        if "I" in self.args:
            result += f" I{self.args['I']}"
            
        return result
    
    @classmethod
    def from_gcode(cls, line: str) -> Optional['ListWiFiNetworks']:
        """
        Parse a G-code string into a ListWiFiNetworks instruction.
        
        Args:
            line: The G-code string to parse
            
        Returns:
            ListWiFiNetworks: An instance, or None if the line doesn't match
        """
        # Check if this is an M588 command
        if not line.strip().startswith("M588"):
            return None
        
        # Extract parameters
        params: Dict[str, Any] = {}
        
        # Extract I parameter (optional)
        i_match = re.search(r'I(\d+)', line)
        if i_match:
            params["I"] = int(i_match.group(1))
        
        return cls(**params)
    
    def describe(self) -> str:
        """
        Provide a human-readable description.
        
        Returns:
            str: Description of the instruction
        """
        interface_str = f" on interface {self.args['I']}" if "I" in self.args else ""
        return f"Scan for available WiFi networks{interface_str}"


@register_instruction
class ConfigureAccessPoint(GInstruction):
    """
    Configure access point settings.
    
    Example G-code: M589 S"DuetAP" P"password" (configure access point)
    Example G-code: M589 S"DuetAP" P"password" I1 (configure access point for interface 1)
    Example G-code: M589 S"DuetAP" P"password" C6 (configure access point on channel 6)
    """
    code = "M589"
    accepted_args = ["S", "P", "I", "C"]
    
    def __init__(self, S: str, P: Optional[str] = None, I: Optional[int] = None, C: Optional[int] = None):
        """
        Initialize an access point configuration instruction.
        
        Args:
            S: SSID for the access point
            P: Password for the access point (optional)
            I: Interface number (optional)
            C: WiFi channel (optional)
        """
        args = {"S": S}
        if P is not None:
            args["P"] = P
        if I is not None:
            args["I"] = I
        if C is not None:
            args["C"] = C
        super().__init__(**args)
    
    def to_gcode(self) -> str:
        """
        Convert to G-code string.
        
        Returns:
            str: G-code representation (e.g., "M589 S\"DuetAP\" P\"password\"")
        """
        result = f'M589 S"{self.args["S"]}"'
        
        if "P" in self.args:
            result += f' P"{self.args["P"]}"'
        if "I" in self.args:
            result += f" I{self.args['I']}"
        if "C" in self.args:
            result += f" C{self.args['C']}"
            
        return result
    
    @classmethod
    def from_gcode(cls, line: str) -> Optional['ConfigureAccessPoint']:
        """
        Parse a G-code string into a ConfigureAccessPoint instruction.
        
        Args:
            line: The G-code string to parse
            
        Returns:
            ConfigureAccessPoint: An instance, or None if the line doesn't match
        """
        # Check if this is an M589 command
        if not line.strip().startswith("M589"):
            return None
        
        # Extract parameters
        params: Dict[str, Any] = {}
        
        # Extract S parameter (required, quoted SSID)
        s_match = re.search(r'S"([^"]*)"', line)
        if s_match:
            params["S"] = s_match.group(1)
        else:
            return None  # S parameter is required
        
        # Extract P parameter (optional, quoted password)
        # Use a more specific pattern to match P followed by a quoted string
        p_match = re.search(r'\bP"([^"]*)"', line)
        if p_match:
            params["P"] = p_match.group(1)
        
        # Extract I parameter (optional)
        i_match = re.search(r'I(\d+)', line)
        if i_match:
            params["I"] = int(i_match.group(1))
        
        # Extract C parameter (optional)
        c_match = re.search(r'C(\d+)', line)
        if c_match:
            params["C"] = int(c_match.group(1))
        
        return cls(**params)
    
    def describe(self) -> str:
        """
        Provide a human-readable description.
        
        Returns:
            str: Description of the instruction
        """
        description = f"Configure access point with SSID '{self.args['S']}'"
        
        if "P" in self.args:
            description += " with password"
        else:
            description += " without password"
        
        if "I" in self.args:
            description += f" on interface {self.args['I']}"
        
        if "C" in self.args:
            description += f" on channel {self.args['C']}"
        
        return description


@register_instruction
class ConfigureNetworkProtocols(GInstruction):
    """
    Configure network protocols.
    
    Example G-code: M586 P0 S1 (enable HTTP)
    Example G-code: M586 P1 S0 (disable FTP)
    Example G-code: M586 P2 S1 (enable Telnet)
    """
    code = "M586"
    accepted_args = ["P", "S"]
    
    def __init__(self, P: int, S: int):
        """
        Initialize a network protocol configuration instruction.
        
        Args:
            P: Protocol (0=HTTP, 1=FTP, 2=Telnet, 3=MQTT)
            S: State (0=disable, 1=enable)
        """
        super().__init__(P=P, S=S)
    
    def to_gcode(self) -> str:
        """
        Convert to G-code string.
        
        Returns:
            str: G-code representation (e.g., "M586 P0 S1")
        """
        return f"M586 P{self.args['P']} S{self.args['S']}"
    
    @classmethod
    def from_gcode(cls, line: str) -> Optional['ConfigureNetworkProtocols']:
        """
        Parse a G-code string into a ConfigureNetworkProtocols instruction.
        
        Args:
            line: The G-code string to parse
            
        Returns:
            ConfigureNetworkProtocols: An instance, or None if the line doesn't match
        """
        # Check if this is an M586 command
        if not line.strip().startswith("M586"):
            return None
        
        # Extract parameters
        params: Dict[str, Any] = {}
        
        # Extract P parameter (required)
        p_match = re.search(r'P(\d+)', line)
        if p_match:
            params["P"] = int(p_match.group(1))
        else:
            return None  # P parameter is required
        
        # Extract S parameter (required)
        s_match = re.search(r'S(\d+)', line)
        if s_match:
            params["S"] = int(s_match.group(1))
        else:
            return None  # S parameter is required
        
        return cls(**params)
    
    def describe(self) -> str:
        """
        Provide a human-readable description.
        
        Returns:
            str: Description of the instruction
        """
        protocols = {
            0: "HTTP",
            1: "FTP",
            2: "Telnet",
            3: "MQTT"
        }
        
        protocol_str = protocols.get(self.args["P"], f"protocol {self.args['P']}")
        state_str = "enable" if self.args["S"] == 1 else "disable"
        
        return f"{state_str} {protocol_str} protocol" 