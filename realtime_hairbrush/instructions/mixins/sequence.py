"""
SequenceMixin for executing common command sequences.

This module provides a mixin for executing common command sequences for the airbrush plotter.
"""

from typing import Dict, Any, Optional, Union, List, Generator, Tuple
import time

from semantic_gcode.gcode.base import GCodeInstruction, Numeric


class SequenceMixin:
    """
    Mixin for executing predefined sequences of commands.
    """
    
    def execute_homing_sequence(self) -> Generator[GCodeInstruction, None, None]:
        """
        Execute the complete homing sequence for the machine.
        
        Yields:
            GCodeInstruction: G-code instructions for homing
        """
        # Home all axes
        yield GCodeInstruction(
            code_type="G",
            code_number=28,
            comment="Home all axes"
        )
        
        # Home U axis (black paint flow)
        yield GCodeInstruction(
            code_type="G",
            code_number=28,
            parameters={"U": None},
            comment="Home U axis (black paint flow)"
        )
        
        # Home V axis (white paint flow)
        yield GCodeInstruction(
            code_type="G",
            code_number=28,
            parameters={"V": None},
            comment="Home V axis (white paint flow)"
        )
    
    def execute_stroke(
        self,
        tool_index: int,
        path_points: List[Tuple[float, float]],
        width: float = 1.0,
        opacity: float = 1.0,
        safe_z_height: float = 5.0,
        spray_z_height: float = 1.5,
        travel_feedrate: float = 3000,
        spray_feedrate: float = 1500,
        z_safe_feedrate: float = 1000,
        z_spray_feedrate: float = 500
    ) -> Generator[GCodeInstruction, None, None]:
        """
        Execute a complete stroke with the specified tool along the given path.
        
        Args:
            tool_index: 0 for black, 1 for white
            path_points: List of (x,y) coordinates defining the path
            width: Stroke width parameter (0.0-1.0)
            opacity: Stroke opacity parameter (0.0-1.0)
            safe_z_height: Safe Z height for travel
            spray_z_height: Z height for spraying
            travel_feedrate: Feedrate for travel moves
            spray_feedrate: Feedrate for spray moves
            z_safe_feedrate: Feedrate for Z moves to safe height
            z_spray_feedrate: Feedrate for Z moves to spray height
            
        Yields:
            GCodeInstruction: G-code instructions for the stroke
        """
        if not path_points:
            return
        
        # 1. Select the appropriate tool
        yield GCodeInstruction(
            code_type="T",
            code_number=tool_index,
            comment=f"Select {'black' if tool_index == 0 else 'white'} airbrush"
        )
        
        # 2. Apply tool offset if needed
        if tool_index == 1:  # T1 (white)
            # Disable bounds checking
            yield GCodeInstruction(
                code_type="M",
                code_number=120,
                comment="Disable bounds checking"
            )
            
            # Apply offset
            yield GCodeInstruction(
                code_type="G",
                code_number=1,
                parameters={"X": 100, "Y": -25, "F": travel_feedrate},
                comment="Apply tool offset"
            )
        
        # 3. Raise Z to safe travel height
        yield GCodeInstruction(
            code_type="G",
            code_number=1,
            parameters={"Z": safe_z_height, "F": z_safe_feedrate},
            comment="Move to safe Z height"
        )
        
        # 4. Move to start position
        yield GCodeInstruction(
            code_type="G",
            code_number=0,
            parameters={"X": path_points[0][0], "Y": path_points[0][1], "F": travel_feedrate},
            comment="Move to start position"
        )
        
        # 5. Move Z to spray height
        yield GCodeInstruction(
            code_type="G",
            code_number=1,
            parameters={"Z": spray_z_height, "F": z_spray_feedrate},
            comment="Move to spray height"
        )
        
        # 6. Start air
        fan_index = 2 if tool_index == 0 else 3
        yield GCodeInstruction(
            code_type="M",
            code_number=106,
            parameters={"P": fan_index, "S": 1.0},
            comment="Air ON"
        )
        
        # 7. Wait for air to stabilize
        yield GCodeInstruction(
            code_type="G",
            code_number=4,
            parameters={"P": 50},
            comment="Wait for air to stabilize"
        )
        
        # 8. Start paint flow
        # Switch to relative positioning
        yield GCodeInstruction(
            code_type="G",
            code_number=91,
            comment="Relative positioning"
        )
        
        # Calculate flow value based on width and opacity
        flow_value = width * opacity * 4.0  # Scale to the 0-4mm range
        
        # Set flow for appropriate axis
        axis = "U" if tool_index == 0 else "V"
        yield GCodeInstruction(
            code_type="G",
            code_number=1,
            parameters={axis: flow_value, "F": 300},
            comment=f"Start paint flow: width={width}, opacity={opacity}"
        )
        
        # Return to absolute positioning
        yield GCodeInstruction(
            code_type="G",
            code_number=90,
            comment="Absolute positioning"
        )
        
        # 9. Execute path movements
        for point in path_points[1:]:
            yield GCodeInstruction(
                code_type="G",
                code_number=1,
                parameters={"X": point[0], "Y": point[1], "F": spray_feedrate},
                comment="Path movement"
            )
        
        # 10. Stop paint flow
        yield GCodeInstruction(
            code_type="M",
            code_number=18,
            parameters={axis: None},
            comment="Stop paint flow"
        )
        
        # 11. Wait for paint tail to clear
        yield GCodeInstruction(
            code_type="G",
            code_number=4,
            parameters={"P": 50},
            comment="Wait for paint tail to clear"
        )
        
        # 12. Stop air
        yield GCodeInstruction(
            code_type="M",
            code_number=106,
            parameters={"P": fan_index, "S": 0.0},
            comment="Air OFF"
        )
        
        # 13. Raise Z to safe height
        yield GCodeInstruction(
            code_type="G",
            code_number=1,
            parameters={"Z": safe_z_height, "F": z_safe_feedrate},
            comment="Raise to safe Z height"
        )
        
        # 14. Remove tool offset if needed
        if tool_index == 1:  # T1 (white)
            # Remove offset
            yield GCodeInstruction(
                code_type="G",
                code_number=1,
                parameters={"X": -100, "Y": 25, "F": travel_feedrate},
                comment="Remove tool offset"
            )
            
            # Re-enable bounds checking
            yield GCodeInstruction(
                code_type="M",
                code_number=121,
                comment="Enable bounds checking"
            ) 