"""
G90: Set to Absolute Positioning

All coordinates from now on are absolute, relative to the origin of the machine.
"""

from semantic_gcode.gcode.base import GCodeInstruction, register_gcode_instruction, ModalInstruction

@register_gcode_instruction
class G90_AbsolutePositioning(GCodeInstruction, ModalInstruction):
    """
    G90: Set to Absolute Positioning
    
    All coordinates from now on are absolute, relative to the origin of the machine.
    
    Parameters:
    - No additional parameters
    
    Examples:
    - G90 ; Set to absolute positioning
    
    Notes:
    - RepRapFirmware uses M82 to set the extruder to absolute mode: extrusion is NOT set to absolute using G90
    - Each input channel has its own flag for the absolute/relative positioning state
    """
    code_type = "G"
    code_number = 90
    
    @classmethod
    def create(cls) -> 'G90_AbsolutePositioning':
        """
        Create a G90 absolute positioning instruction.
        
        Returns:
            G90_AbsolutePositioning: An absolute positioning instruction
        """
        return cls(
            code_type="G",
            code_number=90,
            parameters={},
            comment="Set to absolute positioning"
        )
    
    def affects_modal_state(self) -> bool:
        """
        G90 affects the modal state by changing the positioning mode.
        
        Returns:
            bool: True
        """
        return True
    
    def apply(self, state: dict) -> dict:
        """
        Update the machine state to use absolute positioning.
        
        Args:
            state: Current machine state
            
        Returns:
            dict: Updated machine state
        """
        # Create positioning state if it doesn't exist
        if "positioning" not in state:
            state["positioning"] = {}
        
        # Set positioning mode to absolute
        state["positioning"]["mode"] = "absolute"
        
        return state

# For backward compatibility
def g90():
    """
    Implementation for G90: Set to Absolute Positioning
    """
    return G90_AbsolutePositioning.create()

if __name__ == "__main__":
    print("GCode command: G90")
    instruction = g90()
    print(str(instruction))
