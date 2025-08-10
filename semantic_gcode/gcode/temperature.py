"""
Temperature-related G-code instructions.

This module provides semantic instruction classes for temperature-related G-code commands,
such as setting extruder and bed temperatures.
"""
import re
from typing import Optional, ClassVar, List, Dict, Any

from .base import GInstruction, register_instruction


@register_instruction
class SetExtruderTemp(GInstruction):
    """
    Set extruder temperature.
    
    Example G-code: M104 S200 (set extruder to 200°C)
    Example G-code: M104 S200 T1 (set extruder 1 to 200°C)
    """
    code = "M104"
    accepted_args = ["S", "T"]  # S is temperature, T is tool number
    
    def __init__(self, S: float, T: int = 0):
        """
        Initialize an extruder temperature setting instruction.
        
        Args:
            S: The target temperature in degrees Celsius
            T: The tool number (default: 0)
        """
        super().__init__(S=S, T=T)
    
    def to_gcode(self) -> str:
        """
        Convert to G-code string.
        
        Returns:
            str: G-code representation (e.g., "M104 S200 T0")
        """
        return f"M104 S{self.args['S']}" + (f" T{self.args['T']}" if self.args['T'] != 0 else "")
    
    @classmethod
    def from_gcode(cls, line: str) -> Optional['SetExtruderTemp']:
        """
        Parse a G-code string into a SetExtruderTemp instruction.
        
        Args:
            line: The G-code string to parse
            
        Returns:
            SetExtruderTemp: An instance of SetExtruderTemp, or None if the line doesn't match
        """
        # Check if this is an M104 command
        if not line.strip().startswith("M104"):
            return None
        
        # Extract parameters
        params: Dict[str, Any] = {}
        parts = line.strip().split()
        
        for part in parts[1:]:  # Skip the M104 part
            if part[0] in cls.accepted_args:
                try:
                    params[part[0]] = float(part[1:])
                except ValueError:
                    continue
        
        # M104 requires an S parameter (temperature)
        if "S" not in params:
            return None
        
        # Convert T to int if present
        if "T" in params:
            params["T"] = int(params["T"])
        else:
            params["T"] = 0
        
        return cls(**params)
    
    def describe(self) -> str:
        """
        Provide a human-readable description.
        
        Returns:
            str: Description of the instruction
        """
        tool_str = f" (tool {self.args['T']})" if self.args['T'] != 0 else ""
        return f"Set extruder temperature to {self.args['S']}°C{tool_str}"


@register_instruction
class SetExtruderTempAndWait(GInstruction):
    """
    Set extruder temperature and wait for it to be reached.
    
    Example G-code: M109 S200 (set extruder to 200°C and wait)
    Example G-code: M109 S200 T1 (set extruder 1 to 200°C and wait)
    """
    code = "M109"
    accepted_args = ["S", "T", "R"]  # S is temperature, T is tool number, R is temperature and wait but allow cooling
    
    def __init__(self, S: Optional[float] = None, R: Optional[float] = None, T: int = 0):
        """
        Initialize an extruder temperature setting and waiting instruction.
        
        Args:
            S: The target temperature in degrees Celsius (wait for heating only)
            R: The target temperature in degrees Celsius (wait for heating or cooling)
            T: The tool number (default: 0)
        """
        if S is None and R is None:
            raise ValueError("Either S or R parameter must be provided")
        
        if S is not None and R is not None:
            raise ValueError("Only one of S or R parameters should be provided")
            
        args = {"T": T}
        if S is not None:
            args["S"] = S
        if R is not None:
            args["R"] = R
            
        super().__init__(**args)
    
    def to_gcode(self) -> str:
        """
        Convert to G-code string.
        
        Returns:
            str: G-code representation (e.g., "M109 S200 T0")
        """
        temp_param = f"S{self.args['S']}" if "S" in self.args else f"R{self.args['R']}"
        tool_param = f" T{self.args['T']}" if self.args['T'] != 0 else ""
        return f"M109 {temp_param}{tool_param}"
    
    @classmethod
    def from_gcode(cls, line: str) -> Optional['SetExtruderTempAndWait']:
        """
        Parse a G-code string into a SetExtruderTempAndWait instruction.
        
        Args:
            line: The G-code string to parse
            
        Returns:
            SetExtruderTempAndWait: An instance, or None if the line doesn't match
        """
        # Check if this is an M109 command
        if not line.strip().startswith("M109"):
            return None
        
        # Extract parameters
        params: Dict[str, Any] = {}
        parts = line.strip().split()
        
        for part in parts[1:]:  # Skip the M109 part
            if part[0] in cls.accepted_args:
                try:
                    params[part[0]] = float(part[1:])
                except ValueError:
                    continue
        
        # M109 requires either an S or R parameter (temperature)
        if "S" not in params and "R" not in params:
            return None
        
        # Convert T to int if present
        if "T" in params:
            params["T"] = int(params["T"])
        else:
            params["T"] = 0
        
        return cls(**params)
    
    def describe(self) -> str:
        """
        Provide a human-readable description.
        
        Returns:
            str: Description of the instruction
        """
        temp_value = self.args.get("S", self.args.get("R", 0))
        wait_type = "wait for heating" if "S" in self.args else "wait for heating/cooling"
        tool_str = f" (tool {self.args['T']})" if self.args['T'] != 0 else ""
        return f"Set extruder temperature to {temp_value}°C and {wait_type}{tool_str}"


@register_instruction
class SetBedTemp(GInstruction):
    """
    Set bed temperature.
    
    Example G-code: M140 S60 (set bed to 60°C)
    """
    code = "M140"
    accepted_args = ["S"]  # S is temperature
    
    def __init__(self, S: float):
        """
        Initialize a bed temperature setting instruction.
        
        Args:
            S: The target temperature in degrees Celsius
        """
        super().__init__(S=S)
    
    def to_gcode(self) -> str:
        """
        Convert to G-code string.
        
        Returns:
            str: G-code representation (e.g., "M140 S60")
        """
        return f"M140 S{self.args['S']}"
    
    @classmethod
    def from_gcode(cls, line: str) -> Optional['SetBedTemp']:
        """
        Parse a G-code string into a SetBedTemp instruction.
        
        Args:
            line: The G-code string to parse
            
        Returns:
            SetBedTemp: An instance of SetBedTemp, or None if the line doesn't match
        """
        # Check if this is an M140 command
        if not line.strip().startswith("M140"):
            return None
        
        # Extract parameters
        params: Dict[str, Any] = {}
        parts = line.strip().split()
        
        for part in parts[1:]:  # Skip the M140 part
            if part[0] in cls.accepted_args:
                try:
                    params[part[0]] = float(part[1:])
                except ValueError:
                    continue
        
        # M140 requires an S parameter (temperature)
        if "S" not in params:
            return None
        
        return cls(**params)
    
    def describe(self) -> str:
        """
        Provide a human-readable description.
        
        Returns:
            str: Description of the instruction
        """
        return f"Set bed temperature to {self.args['S']}°C"


@register_instruction
class SetBedTempAndWait(GInstruction):
    """
    Set bed temperature and wait for it to be reached.
    
    Example G-code: M190 S60 (set bed to 60°C and wait)
    """
    code = "M190"
    accepted_args = ["S", "R"]  # S is temperature (wait for heating), R is temperature (wait for heating or cooling)
    
    def __init__(self, S: Optional[float] = None, R: Optional[float] = None):
        """
        Initialize a bed temperature setting and waiting instruction.
        
        Args:
            S: The target temperature in degrees Celsius (wait for heating only)
            R: The target temperature in degrees Celsius (wait for heating or cooling)
        """
        if S is None and R is None:
            raise ValueError("Either S or R parameter must be provided")
        
        if S is not None and R is not None:
            raise ValueError("Only one of S or R parameters should be provided")
            
        args = {}
        if S is not None:
            args["S"] = S
        if R is not None:
            args["R"] = R
            
        super().__init__(**args)
    
    def to_gcode(self) -> str:
        """
        Convert to G-code string.
        
        Returns:
            str: G-code representation (e.g., "M190 S60")
        """
        temp_param = f"S{self.args['S']}" if "S" in self.args else f"R{self.args['R']}"
        return f"M190 {temp_param}"
    
    @classmethod
    def from_gcode(cls, line: str) -> Optional['SetBedTempAndWait']:
        """
        Parse a G-code string into a SetBedTempAndWait instruction.
        
        Args:
            line: The G-code string to parse
            
        Returns:
            SetBedTempAndWait: An instance, or None if the line doesn't match
        """
        # Check if this is an M190 command
        if not line.strip().startswith("M190"):
            return None
        
        # Extract parameters
        params: Dict[str, Any] = {}
        parts = line.strip().split()
        
        for part in parts[1:]:  # Skip the M190 part
            if part[0] in cls.accepted_args:
                try:
                    params[part[0]] = float(part[1:])
                except ValueError:
                    continue
        
        # M190 requires either an S or R parameter (temperature)
        if "S" not in params and "R" not in params:
            return None
        
        return cls(**params)
    
    def describe(self) -> str:
        """
        Provide a human-readable description.
        
        Returns:
            str: Description of the instruction
        """
        temp_value = self.args.get("S", self.args.get("R", 0))
        wait_type = "wait for heating" if "S" in self.args else "wait for heating/cooling"
        return f"Set bed temperature to {temp_value}°C and {wait_type}"


@register_instruction
class GetTemperatures(GInstruction):
    """
    Request temperature report.
    
    Example G-code: M105 (report temperatures)
    """
    code = "M105"
    accepted_args: List[str] = []  # No parameters
    
    def to_gcode(self) -> str:
        """
        Convert to G-code string.
        
        Returns:
            str: G-code representation (e.g., "M105")
        """
        return "M105"
    
    @classmethod
    def from_gcode(cls, line: str) -> Optional['GetTemperatures']:
        """
        Parse a G-code string into a GetTemperatures instruction.
        
        Args:
            line: The G-code string to parse
            
        Returns:
            GetTemperatures: An instance, or None if the line doesn't match
        """
        # Check if this is an M105 command
        if line.strip() == "M105":
            return cls()
        return None
    
    def describe(self) -> str:
        """
        Provide a human-readable description.
        
        Returns:
            str: Description of the instruction
        """
        return "Request temperature report"
