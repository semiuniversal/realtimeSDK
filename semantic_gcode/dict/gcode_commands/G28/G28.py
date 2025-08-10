"""
G28: Home

This command moves the specified axes to their home position.
If no axes are specified, all axes are homed.
"""

from typing import Dict, Optional, List, Union
from semantic_gcode.gcode.base import GCodeInstruction, register_gcode_instruction, ModalInstruction

@register_gcode_instruction
class G28_Home(GCodeInstruction, ModalInstruction):
    """
    G28: Home axes
    
    This command moves the specified axes to their home position.
    If no axes are specified, all axes are homed.
    
    Parameters:
    - X: Flag to home the X axis
    - Y: Flag to home the Y axis
    - Z: Flag to home the Z axis
    - U, V, W, A, B, C, D: Flags to home additional axes
    
    Examples:
    - G28     ; Home all axes
    - G28 X Y ; Home X and Y axes
    - G28 Z   ; Home Z axis only
    """
    code_type = "G"
    code_number = 28
    
    # Valid parameters for this command
    valid_parameters = ["X", "Y", "Z", "U", "V", "W", "A", "B", "C", "D"]
    
    @classmethod
    def create(cls, axes: Optional[List[str]] = None) -> 'G28_Home':
        """
        Create a G28 homing instruction.
        
        Args:
            axes: List of axes to home (e.g., ["X", "Y"]), or None to home all axes
            
        Returns:
            G28_Home: A homing instruction
        """
        parameters = {}
        
        # If axes are specified, add them as parameters
        if axes:
            for axis in axes:
                if axis in cls.valid_parameters:
                    parameters[axis] = 0
            
            comment = f"Home {', '.join(axes)} axes"
        else:
            comment = "Home all axes"
        
        return cls(
            code_type="G",
            code_number=28,
            parameters=parameters,
            comment=comment
        )
    
    def affects_modal_state(self) -> bool:
        """
        G28 affects the modal state by changing the machine position.
        
        Returns:
            bool: True
        """
        return True
    
    def apply(self, state: dict) -> dict:
        """
        Update the machine state after homing.
        
        Args:
            state: Current machine state
            
        Returns:
            dict: Updated machine state
        """
        # Create position state if it doesn't exist
        if "position" not in state:
            state["position"] = {}
        
        # If no axes specified, home all axes
        if not self.parameters:
            # Set all axes to their home positions (typically 0)
            for axis in self.valid_parameters:
                state["position"][axis.lower()] = 0
        else:
            # Set only the specified axes to their home positions
            for axis in self.parameters:
                state["position"][axis.lower()] = 0
        
        return state

# For backward compatibility
def g28():
    """
    Implementation for G28: Home
    """
    return G28_Home.create()

if __name__ == "__main__":
    print("GCode command: G28")
    instruction = g28()
    print(str(instruction))
