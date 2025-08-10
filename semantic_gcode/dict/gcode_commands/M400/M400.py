"""
M400: Wait for current moves to finish

This command finishes all current moves and clears the buffer.
It waits until all motion stops before allowing any further commands to execute.
"""

from typing import Optional, Dict, Any
from semantic_gcode.gcode.base import GCodeInstruction, register_gcode_instruction
from semantic_gcode.gcode.mixins import BlocksExecution, ExpectsAcknowledgement

@register_gcode_instruction
class M400_WaitForMoves(GCodeInstruction, BlocksExecution, ExpectsAcknowledgement):
    """
    M400: Wait for current moves to finish
    
    This command finishes all current moves and clears the buffer.
    It waits until all motion stops before allowing any further commands to execute.
    
    Parameters:
    - S: (RRF 3.5.0+ only) 0 = release axes/extruders not needed by current tool,
         1 = do not release axes or extruders
    
    Examples:
    - M400     ; Wait until motion stops, release unused axes/extruders
    - M400 S1  ; Wait until motion stops, do not release axes/extruders
    
    Notes:
    - Similar to G4 P0 except that G4 P0 does not release axes or extruders
    - Blocks execution until the machine confirms all motion has stopped
    - Expects "ok" acknowledgement when motion has completed
    """
    code_type = "M"
    code_number = 400
    
    # Valid parameters for this command
    valid_parameters = ["S"]
    
    @classmethod
    def create(cls, release_mode: Optional[int] = None) -> 'M400_WaitForMoves':
        """
        Create an M400 wait for moves instruction.
        
        Args:
            release_mode: 0 = release unused axes/extruders, 1 = do not release
            
        Returns:
            M400_WaitForMoves: A wait for moves instruction
        """
        parameters = {}
        
        if release_mode is not None:
            if release_mode not in [0, 1]:
                raise ValueError("Release mode must be 0 or 1")
            parameters['S'] = release_mode
            comment = f"Wait for moves to finish (release mode {release_mode})"
        else:
            comment = "Wait for moves to finish"
        
        return cls(
            code_type="M",
            code_number=400,
            parameters=parameters,
            comment=comment
        )
    
    def apply(self, state: dict) -> dict:
        """
        Update machine state after waiting for moves to finish.
        
        Args:
            state: Current machine state
            
        Returns:
            dict: Updated machine state with motion_complete flag set to True
        """
        # Create motion state if it doesn't exist
        if "motion" not in state:
            state["motion"] = {}
        
        # Set motion_complete flag to True
        state["motion"]["motion_complete"] = True
        
        # Handle release mode if specified
        if 'S' in self.parameters:
            release_mode = self.parameters['S']
            state["motion"]["release_mode"] = release_mode
        
        return state
    
    def validate_response(self, response: str) -> bool:
        """
        Accept acknowledgement when either:
        - 'ok' appears (serial/rr_gcode case), or
        - Object-model JSON reports idle (status "I" or state "idle").
        """
        if not response:
            return False
        text = response.strip()
        lower = text.lower()
        if "ok" in lower:
            return True
        # Heuristic: detect JSON object model with idle status
        compact = lower.replace(" ", "")
        if '"status":"i"' in compact or '"state":"idle"' in compact:
            return True
        return False

    def execute(self, device) -> Optional[str]:
        """
        Send the M400 command to the device and wait for acknowledgement.
        
        This method overrides the default execute method to ensure that
        we wait for the "ok" response before continuing.
        
        Args:
            device: The device to send the command to
            
        Returns:
            Optional[str]: The response from the device, or None if no response
        """
        # Send the command
        response = device.send(str(self))
        
        # Wait for acknowledgement
        if response and not self.validate_response(response):
            # If we didn't get an "ok", wait for it
            while True:
                additional_response = device.read_response()
                if not additional_response:
                    break
                    
                response += additional_response
                if self.validate_response(response):
                    break
        
        return response

# For backward compatibility
def m400(release_mode=None):
    """
    Implementation for M400: Wait for current moves to finish
    
    Args:
        release_mode: 0 = release unused axes/extruders, 1 = do not release
    """
    return M400_WaitForMoves.create(release_mode=release_mode)

if __name__ == "__main__":
    print("GCode command: M400")
    instruction = m400()
    print(str(instruction))
    
    # Example with release mode
    instruction = m400(release_mode=1)
    print(str(instruction))
