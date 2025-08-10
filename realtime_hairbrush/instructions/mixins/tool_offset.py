"""
ToolOffsetMixin for managing tool offsets.

This module provides a mixin for managing tool offsets for the dual-airbrush system.
"""

from typing import Dict, Any, Optional, Union, List, Generator
import time

from semantic_gcode.gcode.base import GCodeInstruction, Numeric


class ToolOffsetMixin:
    """
    Mixin for managing tool offsets for the dual-airbrush system.
    """
    
    def apply_tool_offset(self, tool_index: int, x_offset: float = 100, y_offset: float = -25, z_offset: float = 0) -> Generator[GCodeInstruction, None, None]:
        """
        Apply the appropriate offset for the selected tool.
        For T1 (white), apply offset relative to T0 (black).
        
        Args:
            tool_index: 0 for black (no offset), 1 for white (needs offset)
            x_offset: X offset value
            y_offset: Y offset value
            z_offset: Z offset value
            
        Yields:
            GCodeInstruction: G-code instructions for applying tool offset
        """
        if tool_index == 1:  # Only T1 needs offset
            # First disable bounds checking
            yield GCodeInstruction(
                code_type="M",
                code_number=120,
                comment="Disable bounds checking"
            )
            
            # Apply offset with a move
            yield GCodeInstruction(
                code_type="G",
                code_number=1,
                parameters={"X": x_offset, "Y": y_offset, "Z": z_offset, "F": 3000},
                comment="Apply tool offset"
            )
    
    def remove_tool_offset(self, tool_index: int, x_offset: float = 100, y_offset: float = -25, z_offset: float = 0) -> Generator[GCodeInstruction, None, None]:
        """
        Remove the tool offset (only needed for T1).
        
        Args:
            tool_index: 0 for black (no offset), 1 for white (needs offset removal)
            x_offset: X offset value to reverse
            y_offset: Y offset value to reverse
            z_offset: Z offset value to reverse
            
        Yields:
            GCodeInstruction: G-code instructions for removing tool offset
        """
        if tool_index == 1:
            # Move back by the negative offset amount
            yield GCodeInstruction(
                code_type="G",
                code_number=1,
                parameters={"X": -x_offset, "Y": -y_offset, "Z": -z_offset, "F": 3000},
                comment="Remove tool offset"
            )
            
            # Re-enable bounds checking
            yield GCodeInstruction(
                code_type="M",
                code_number=121,
                comment="Enable bounds checking"
            )
    
    def set_tool_offset(self, tool_index: int, x: float, y: float, z: float = 0) -> Generator[GCodeInstruction, None, None]:
        """
        Set the offset for the specified tool using G10.
        
        Args:
            tool_index: Tool index (0 or 1)
            x: X offset
            y: Y offset
            z: Z offset
            
        Yields:
            GCodeInstruction: G-code instruction for setting tool offset
        """
        yield GCodeInstruction(
            code_type="G",
            code_number=10,
            parameters={"P": tool_index, "X": x, "Y": y, "Z": z},
            comment=f"Set tool {tool_index} offset"
        )
    
    def get_tool_offsets(self) -> Generator[GCodeInstruction, None, None]:
        """
        Get the current tool offsets.
        
        Yields:
            GCodeInstruction: G-code instruction for getting tool offsets
        """
        yield GCodeInstruction(
            code_type="M",
            code_number=500,
            comment="Report tool offsets"
        ) 