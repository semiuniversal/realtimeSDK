"""
G4: Dwell

Pause the machine for a period of time.
"""

from typing import Optional, Union
from semantic_gcode.gcode.base import GCodeInstruction, register_gcode_instruction

@register_gcode_instruction
class G4_Dwell(GCodeInstruction):
    """
    G4: Dwell
    
    Pause the machine for a period of time.
    
    Parameters:
    - P: Time to wait, in milliseconds
    - S: Time to wait, in seconds
    
    Examples:
    - G4 P200 ; wait for 200 milliseconds
    - G4 S1   ; wait for 1 second
    """
    code_type = "G"
    code_number = 4
    
    # Valid parameters for this command
    valid_parameters = ["P", "S"]
    
    @classmethod
    def create(cls, milliseconds: Optional[int] = None, seconds: Optional[float] = None) -> 'G4_Dwell':
        """
        Create a G4 dwell instruction.
        
        Args:
            milliseconds: Time to wait in milliseconds (P parameter)
            seconds: Time to wait in seconds (S parameter)
            
        Returns:
            G4_Dwell: A dwell instruction
            
        Raises:
            ValueError: If both milliseconds and seconds are specified
        """
        parameters = {}
        
        # Validate that only one time parameter is specified
        if milliseconds is not None and seconds is not None:
            raise ValueError("Cannot specify both milliseconds (P) and seconds (S) for G4 command")
        
        # Add the appropriate time parameter
        if milliseconds is not None:
            parameters['P'] = milliseconds
            comment = f"Dwell for {milliseconds}ms"
        elif seconds is not None:
            parameters['S'] = seconds
            comment = f"Dwell for {seconds}s"
        else:
            # Default to 0 milliseconds if neither is specified
            parameters['P'] = 0
            comment = "Dwell for 0ms"
        
        return cls(
            code_type="G",
            code_number=4,
            parameters=parameters,
            comment=comment
        )

# For backward compatibility
def g4(milliseconds=None, seconds=None):
    """
    Implementation for G4: Dwell
    
    Args:
        milliseconds: Time to wait in milliseconds (P parameter)
        seconds: Time to wait in seconds (S parameter)
    """
    return G4_Dwell.create(milliseconds=milliseconds, seconds=seconds)

if __name__ == "__main__":
    print("GCode command: G4")
    instruction = g4(milliseconds=200)
    print(str(instruction))
