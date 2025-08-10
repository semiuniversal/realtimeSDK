"""
T: Select Tool

This command selects a tool for use, running appropriate tool change macros.
"""

from typing import Optional, Union
from semantic_gcode.gcode.base import GCodeInstruction, register_gcode_instruction, ModalInstruction

@register_gcode_instruction
class T_SelectTool(GCodeInstruction, ModalInstruction):
    """
    T: Select Tool
    
    This command selects a tool for use, running appropriate tool change macros.
    
    Parameters:
    - nnn: Tool number to select. A negative number deselects all tools.
    - R1: Select the tool that was active when the print was last paused
    - Pnnn: Bitmap of all the macros to be run (1=tfree, 2=tpre, 4=tpost)
    - Tnn: Alternative way to specify the tool number (RRF 3.4+)
    
    Examples:
    - T0    ; Select tool 0
    - T1 P0 ; Select tool 1 but don't run any tool change macro files
    - T-1   ; Deselect all tools
    - T     ; Report the current tool number
    
    Notes:
    - Tool numbering starts at 0 by default
    - Tool change macros (tfree#.g, tpre#.g, tpost#.g) are run during tool changes
    - Tool offsets are applied whenever there is a current tool
    """
    code_type = "T"
    code_number = None  # T command doesn't have a fixed number
    
    # Valid parameters for this command
    valid_parameters = ["P", "R", "T"]
    
    @classmethod
    def create(cls, 
               tool_number: Optional[int] = None, 
               macro_bitmap: Optional[int] = None,
               restore_paused: bool = False,
               alt_tool_number: Optional[Union[int, str]] = None) -> 'T_SelectTool':
        """
        Create a T tool selection instruction.
        
        Args:
            tool_number: Tool number to select (main parameter)
            macro_bitmap: Bitmap of macros to run (P parameter)
            restore_paused: Select the tool that was active when the print was paused (R1)
            alt_tool_number: Alternative way to specify the tool number (T parameter)
            
        Returns:
            T_SelectTool: A tool selection instruction
            
        Raises:
            ValueError: If both tool_number and alt_tool_number are specified
        """
        parameters = {}
        code_number = None
        
        # Handle tool number specification
        if tool_number is not None and alt_tool_number is not None:
            raise ValueError("Cannot specify both main tool number and alternative tool number (T parameter)")
        
        if tool_number is not None:
            code_number = tool_number
        elif alt_tool_number is not None:
            parameters['T'] = alt_tool_number
        
        # Add other parameters if specified
        if macro_bitmap is not None:
            parameters['P'] = macro_bitmap
        
        if restore_paused:
            parameters['R'] = 1
        
        # Create comment based on the operation
        if tool_number is not None:
            if tool_number < 0:
                comment = "Deselect all tools"
            else:
                comment = f"Select tool {tool_number}"
        elif alt_tool_number is not None:
            comment = f"Select tool {alt_tool_number}"
        elif restore_paused:
            comment = "Restore tool from pause"
        else:
            comment = "Report current tool"
        
        return cls(
            code_type="T",
            code_number=code_number,
            parameters=parameters,
            comment=comment
        )
    
    def affects_modal_state(self) -> bool:
        """
        T affects the modal state by changing the current tool.
        
        Returns:
            bool: True
        """
        return True
    
    def apply(self, state: dict) -> dict:
        """
        Update the machine state to use the selected tool.
        
        Args:
            state: Current machine state
            
        Returns:
            dict: Updated machine state
        """
        # Create tool state if it doesn't exist
        if "tool" not in state:
            state["tool"] = {}
        
        # Set current tool
        if self.code_number is not None:
            state["tool"]["current"] = self.code_number
        elif 'T' in self.parameters:
            # For alternative tool specification
            try:
                tool_num = int(self.parameters['T'])
                state["tool"]["current"] = tool_num
            except (ValueError, TypeError):
                # If it's an expression or non-integer, we can't evaluate it here
                pass
        
        return state

# For backward compatibility
def t(tool_number=None, **kwargs):
    """
    Implementation for T: Select Tool
    
    Args:
        tool_number: Tool number to select
        **kwargs: Additional parameters (macro_bitmap, restore_paused, alt_tool_number)
    """
    return T_SelectTool.create(
        tool_number=tool_number,
        macro_bitmap=kwargs.get('macro_bitmap'),
        restore_paused=kwargs.get('restore_paused', False),
        alt_tool_number=kwargs.get('alt_tool_number')
    )

if __name__ == "__main__":
    print("GCode command: T")
    instruction = t(0)
    print(str(instruction))
    
    # Example with deselect all tools
    instruction = t(-1)
    print(str(instruction))
    
    # Example with macro bitmap
    instruction = t(1, macro_bitmap=0)
    print(str(instruction))
