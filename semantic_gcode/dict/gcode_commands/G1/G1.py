"""
G1: Controlled linear move

This command moves the tool in a straight line from the current position to the specified position.
"""

from typing import Dict, Optional, Union
from semantic_gcode.gcode.base import GCodeInstruction, register_gcode_instruction, ModalInstruction

@register_gcode_instruction
class G1_LinearMove(GCodeInstruction, ModalInstruction):
    """
    G1: Controlled linear move
    
    This command moves the tool in a straight line from the current position to the specified position.
    
    Parameters:
    - X: X-axis position
    - Y: Y-axis position
    - Z: Z-axis position
    - E: Extruder position
    - F: Feedrate (speed)
    - U, V, W, A, B, C, D: Additional axis positions
    
    Examples:
    - G1 X100 Y100    ; Move to X=100, Y=100
    - G1 Z10 F1000    ; Move to Z=10 at feedrate 1000
    - G1 X50 Y50 Z5   ; Move to X=50, Y=50, Z=5
    """
    code_type = "G"
    code_number = 1
    
    # Valid parameters for this command
    valid_parameters = ["X", "Y", "Z", "E", "F", "U", "V", "W", "A", "B", "C", "D"]
    
    @classmethod
    def create(cls, 
               x: Optional[float] = None, 
               y: Optional[float] = None, 
               z: Optional[float] = None,
               e: Optional[float] = None,
               feedrate: Optional[float] = None,
               **kwargs) -> 'G1_LinearMove':
        """
        Create a G1 linear move instruction.
        
        Args:
            x: X-axis position
            y: Y-axis position
            z: Z-axis position
            e: Extruder position
            feedrate: Movement speed (F parameter)
            **kwargs: Additional axis positions (U, V, etc.)
            
        Returns:
            G1_LinearMove: A linear move instruction
        """
        parameters = {}
        
        # Add position parameters
        if x is not None:
            parameters['X'] = x
        if y is not None:
            parameters['Y'] = y
        if z is not None:
            parameters['Z'] = z
        if e is not None:
            parameters['E'] = e
        if feedrate is not None:
            parameters['F'] = feedrate
            
        # Add any additional axis parameters
        for axis, value in kwargs.items():
            if axis.upper() in cls.valid_parameters and value is not None:
                parameters[axis.upper()] = value
        
        # Create comment based on the move
        axes_moved = []
        for axis in "XYZEF":
            if axis in parameters:
                axes_moved.append(f"{axis}={parameters[axis]}")
        
        for axis in kwargs:
            if axis.upper() in parameters:
                axes_moved.append(f"{axis.upper()}={parameters[axis.upper()]}")
        
        comment = f"Move {', '.join(axes_moved)}" if axes_moved else "Move"
        
        return cls(
            code_type="G",
            code_number=1,
            parameters=parameters,
            comment=comment
        )
    
    def affects_modal_state(self) -> bool:
        """
        G1 affects the modal state by changing the machine position.
        
        Returns:
            bool: True
        """
        return True
    
    def apply(self, state: dict) -> dict:
        """
        Update the machine state after a move.
        
        Args:
            state: Current machine state
            
        Returns:
            dict: Updated machine state
        """
        # Create position state if it doesn't exist
        if "position" not in state:
            state["position"] = {}
        
        # Update position for each specified axis
        for axis, value in self.parameters.items():
            if axis != 'F':  # Skip feedrate parameter
                state["position"][axis.lower()] = value
        
        # Update feedrate if specified
        if 'F' in self.parameters:
            state["feedrate"] = self.parameters['F']
        
        return state

# For backward compatibility
def g1(x=None, y=None, z=None, e=None, f=None, **kwargs):
    """
    Implementation for G1: Controlled linear move
    """
    return G1_LinearMove.create(x=x, y=y, z=z, e=e, feedrate=f, **kwargs)

if __name__ == "__main__":
    print("GCode command: G1")
    instruction = g1(x=100, y=100, f=3000)
    print(str(instruction))
