"""
G91: Set to Relative Positioning

All coordinates from now on are relative to the last position.
"""

from semantic_gcode.gcode.base import GCodeInstruction, register_gcode_instruction, ModalInstruction

@register_gcode_instruction
class G91_RelativePositioning(GCodeInstruction, ModalInstruction):
    """
    G91: Set to Relative Positioning
    
    All coordinates from now on are relative to the last position.
    
    Parameters:
    - No additional parameters
    
    Examples:
    - G91 ; Set to relative positioning
    
    Notes:
    - RepRapFirmware uses M83 to set the extruder to relative mode: extrusion is NOT set to relative using G91
    - Each input channel has its own flag for the absolute/relative positioning state
    """
    code_type = "G"
    code_number = 91
    
    @classmethod
    def create(cls) -> 'G91_RelativePositioning':
        """
        Create a G91 relative positioning instruction.
        
        Returns:
            G91_RelativePositioning: A relative positioning instruction
        """
        return cls(
            code_type="G",
            code_number=91,
            parameters={},
            comment="Set to relative positioning"
        )
    
    def affects_modal_state(self) -> bool:
        """
        G91 affects the modal state by changing the positioning mode.
        
        Returns:
            bool: True
        """
        return True
    
    def apply(self, state: dict) -> dict:
        """
        Update the machine state to use relative positioning.
        
        Args:
            state: Current machine state
            
        Returns:
            dict: Updated machine state
        """
        # Create positioning state if it doesn't exist
        if "positioning" not in state:
            state["positioning"] = {}
        
        # Set positioning mode to relative
        state["positioning"]["mode"] = "relative"
        
        return state

# For backward compatibility
def g91():
    """
    Implementation for G91: Set to Relative Positioning
    """
    return G91_RelativePositioning.create()

if __name__ == "__main__":
    print("GCode command: G91")
    instruction = g91()
    print(str(instruction))
