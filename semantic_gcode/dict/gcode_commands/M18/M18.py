"""
M18: Disable motors

Stops the idle hold on all axis and extruder, effectively disabling the specified motor, or all motors.
Disables motors and allows axes to move 'freely.'
"""

from typing import Optional, List
from semantic_gcode.gcode.base import GCodeInstruction, register_gcode_instruction

@register_gcode_instruction
class M18_DisableMotors(GCodeInstruction):
    """
    M18: Disable motors
    
    Stops the idle hold on all axis and extruder, effectively disabling the specified motor, or all motors.
    Disables motors and allows axes to move 'freely.'
    
    Parameters:
    - X: X axis
    - Y: Y axis
    - Z: Z axis
    - U: U axis
    - V: V axis
    - W: W axis
    - E[n]: Extruder drive(s)
    
    Examples:
    - M18      ; Disable all axis and extruder motors
    - M18 X E0 ; Disable X and extruder 0 motors
    
    Notes:
    - When used without parameters, all axis and extruder motors are disabled.
    - Individual motors can be disabled with the X, Y, Z etc axis switches.
    - Be aware that by disabling idle hold during printing, you will get quality issues.
    """
    code_type = "M"
    code_number = 18
    
    # Valid parameters for this command
    valid_parameters = ["X", "Y", "Z", "U", "V", "W", "E"]
    
    @classmethod
    def create(cls, axes: Optional[List[str]] = None) -> 'M18_DisableMotors':
        """
        Create an M18 disable motors instruction.
        
        Args:
            axes: List of axes to disable (e.g., ["X", "E0"]), or None to disable all motors
            
        Returns:
            M18_DisableMotors: A disable motors instruction
        """
        parameters = {}
        
        # If axes are specified, add them as parameters
        if axes:
            for axis in axes:
                # Handle extruder drives with numbers (E0, E1, etc.)
                if axis.startswith('E') and len(axis) > 1 and axis[1:].isdigit():
                    # For extruders with numbers, we use the special syntax E0:1:2 etc.
                    extruder_num = axis[1:]
                    if 'E' not in parameters:
                        parameters['E'] = extruder_num
                    else:
                        parameters['E'] += f":{extruder_num}"
                elif axis in cls.valid_parameters:
                    parameters[axis] = 0
            
            comment = f"Disable {', '.join(axes)} motors"
        else:
            comment = "Disable all motors"
        
        return cls(
            code_type="M",
            code_number=18,
            parameters=parameters,
            comment=comment
        )

# For backward compatibility
def m18(axes=None):
    """
    Implementation for M18: Disable motors
    
    Args:
        axes: List of axes to disable (e.g., ["X", "E0"]), or None to disable all motors
    """
    return M18_DisableMotors.create(axes=axes)

if __name__ == "__main__":
    print("GCode command: M18")
    instruction = m18()
    print(str(instruction))
    
    # Example with specific axes
    instruction = m18(axes=["X", "E0"])
    print(str(instruction))
