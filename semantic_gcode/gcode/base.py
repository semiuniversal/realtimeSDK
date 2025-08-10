"""
Base classes for G-code instruction representation.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, ClassVar, List, Type, Union

# --- Utility Types ---
Numeric = Union[int, float]

# --- Base Mixin Interfaces ---
class ModalInstruction:
    def affects_modal_state(self) -> bool:
        return True

class ImmediateInstruction:
    def is_immediate(self) -> bool:
        return True

class DelayedExecution:
    def has_delayed_effect(self) -> bool:
        return True

class ScopedInstruction:
    def opens_scope(self) -> bool:
        return hasattr(self, 'begin_scope')

class ValidatedInstruction:
    def validate(self, state: dict) -> bool:
        raise NotImplementedError("Validation logic not implemented.")

@dataclass
class GCodeInstruction:
    """
    Base dataclass for all G-code instructions.
    
    This class provides a flexible foundation for representing G-code instructions
    with support for mixins to add specialized behaviors.
    """
    code_type: str  # G, M, T, etc.
    code_number: int
    parameters: Dict[str, Numeric] = field(default_factory=dict)
    comment: Optional[str] = None

    # Contextual Metadata
    source_line: Optional[str] = None
    line_number: Optional[int] = None
    timestamp: Optional[str] = None
    
    # Class registry for instruction types
    _registry: ClassVar[Dict[str, Type['GCodeInstruction']]] = {}
    
    @classmethod
    def register(cls, instruction_class: Type['GCodeInstruction']) -> Type['GCodeInstruction']:
        """
        Register a G-code instruction class.
        
        Args:
            instruction_class: The instruction class to register
            
        Returns:
            The registered instruction class (for decorator use)
        """
        code_key = f"{instruction_class.code_type}{instruction_class.code_number}"
        cls._registry[code_key] = instruction_class
        return instruction_class

    @classmethod
    def parse(cls, line: str) -> Optional['GCodeInstruction']:
        """
        Parse a G-code string into the appropriate instruction object.
        
        Args:
            line: The G-code string to parse
            
        Returns:
            GCodeInstruction: An instance of the appropriate instruction class,
                          or None if no matching instruction was found
        """
        # Extract the code from the line (e.g., "G1" from "G1 X10 Y20")
        parts = line.strip().split()
        if not parts:
            return None
        
        # Try to extract code_type and code_number
        code = parts[0]
        if not code:
            return None
            
        # Handle T codes which might not have a number
        if code.startswith('T') and len(code) == 1:
            code_type = 'T'
            code_number = 0
        else:
            # Extract code type (G, M, etc.) and number
            for i, char in enumerate(code):
                if char.isdigit():
                    code_type = code[:i]
                    try:
                        code_number = int(code[i:])
                        break
                    except ValueError:
                        return None
            else:
                return None
        
        # Check if we have a registered instruction for this code
        code_key = f"{code_type}{code_number}"
        instruction_class = cls._registry.get(code_key)
        
        if instruction_class:
            # Parse parameters
            params = {}
            for part in parts[1:]:
                # Handle comments
                if part.startswith(';'):
                    comment = ' '.join(parts[parts.index(part):]).strip(';').strip()
                    break
                    
                # Handle parameters like X10, Y20
                if len(part) > 1 and part[0].isalpha():
                    try:
                        key = part[0]
                        value = float(part[1:])
                        params[key] = value
                    except ValueError:
                        pass
            
            # Create the instruction
            return instruction_class(
                code_type=code_type,
                code_number=code_number,
                parameters=params,
                source_line=line
            )
        
        # If no registered class, create a generic instruction
        return cls(
            code_type=code_type,
            code_number=code_number,
            source_line=line
        )

    # Hooks for behavior injection
    def execute(self, device) -> Optional[str]:
        """Send the command to the device. Optionally overridden by mixin."""
        return device.send(str(self))

    def apply(self, state: dict) -> dict:
        """Update internal state prediction. Overridden by modal mixin."""
        return state

    def describe(self) -> str:
        """Human-readable description for UI or logs."""
        return f"{self.code_type}{self.code_number} with params {self.parameters}"

    def __str__(self) -> str:
        """Render the instruction as raw G-code."""
        param_str = ' '.join(f"{k}{v}" for k, v in self.parameters.items())
        comment_str = f" ; {self.comment}" if self.comment else ""
        return f"{self.code_type}{self.code_number} {param_str}{comment_str}".strip()

    def is_nop(self) -> bool:
        """Check if this is a no-op instruction."""
        return not self.parameters and not self.code_number

    def to_dict(self) -> dict:
        return {
            "type": self.code_type,
            "number": self.code_number,
            "parameters": self.parameters,
            "comment": self.comment,
            "source_line": self.source_line,
            "line_number": self.line_number,
            "timestamp": self.timestamp,
        }
    
    def to_gcode(self) -> str:
        """
        Convert the instruction to a G-code string.
        Compatible with the original GInstruction interface.
        
        Returns:
            str: The G-code representation of this instruction
        """
        return str(self)


# For backward compatibility with existing code
class GInstruction(ABC):
    """
    Legacy abstract base class for G-code instructions.
    
    This class is maintained for backward compatibility.
    New code should use GCodeInstruction instead.
    """
    
    # Class variables to be defined by subclasses
    code: ClassVar[str]  # The G-code identifier (e.g., "G1", "M104")
    accepted_args: ClassVar[List[str]]  # Valid arguments for this instruction
    
    def __init__(self, **kwargs):
        """
        Initialize a G-code instruction with the given parameters.
        
        Args:
            **kwargs: Parameters for the instruction (e.g., X=10, Y=20, F=3000)
        """
        # Validate arguments
        for arg in kwargs:
            if arg not in self.accepted_args:
                raise ValueError(f"Invalid argument '{arg}' for {self.__class__.__name__}")
        
        self.args = kwargs
    
    @abstractmethod
    def to_gcode(self) -> str:
        """
        Convert the instruction to a G-code string.
        
        Returns:
            str: The G-code representation of this instruction
        """
        pass
    
    @classmethod
    @abstractmethod
    def from_gcode(cls, line: str) -> Optional['GInstruction']:
        """
        Create an instruction from a G-code string.
        
        Args:
            line: The G-code string to parse
            
        Returns:
            GInstruction: An instance of the appropriate instruction class,
                          or None if the line doesn't match this instruction
        """
        pass
    
    def describe(self) -> str:
        """
        Provide a human-readable description of this instruction.
        
        Returns:
            str: A description of what this instruction does
        """
        return f"{self.__class__.__name__} {self.args}"


class GCodeRegistry:
    """
    Legacy registry for mapping between G-code strings and instruction classes.
    
    This class is maintained for backward compatibility.
    New code should use GCodeInstruction.register instead.
    """
    _registry: Dict[str, Type[GInstruction]] = {}
    
    @classmethod
    def register(cls, instruction_class: Type[GInstruction]) -> Type[GInstruction]:
        """
        Register a G-code instruction class.
        
        Args:
            instruction_class: The instruction class to register
            
        Returns:
            The registered instruction class (for decorator use)
        """
        cls._registry[instruction_class.code] = instruction_class
        return instruction_class
    
    @classmethod
    def parse(cls, line: str) -> Optional[GInstruction]:
        """
        Parse a G-code string into the appropriate instruction object.
        
        Args:
            line: The G-code string to parse
            
        Returns:
            GInstruction: An instance of the appropriate instruction class,
                          or None if no matching instruction was found
        """
        # Extract the code from the line (e.g., "G1" from "G1 X10 Y20")
        parts = line.strip().split()
        if not parts:
            return None
        
        code = parts[0]
        
        # Check if we have a registered instruction for this code
        instruction_class = cls._registry.get(code)
        if instruction_class:
            return instruction_class.from_gcode(line)
        
        return None


def register_instruction(cls):
    """
    Decorator for registering G-code instruction classes.
    
    Example:
        @register_instruction
        class MoveTo(GInstruction):
            code = "G1"
            ...
    """
    return GCodeRegistry.register(cls)


def register_gcode_instruction(cls):
    """
    Decorator for registering GCodeInstruction subclasses.
    
    Example:
        @register_gcode_instruction
        class G1_LinearMove(GCodeInstruction):
            code_type = "G"
            code_number = 1
            ...
    """
    # Handle classes that don't have class-level code_type and code_number attributes
    # This is for classes like AirbrushInstruction that are meant to be instantiated
    # with different code types and numbers
    if not hasattr(cls, 'code_type') or not hasattr(cls, 'code_number'):
        return cls
        
    return GCodeInstruction.register(cls)
