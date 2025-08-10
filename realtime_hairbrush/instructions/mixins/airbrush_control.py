"""
AirbrushControlMixin for controlling paint flow.

This module provides a mixin for controlling the paint flow via the U/V axes.
"""

from typing import Dict, Any, Optional, Union, List, Generator
import time

from semantic_gcode.gcode.base import GCodeInstruction, Numeric


class AirbrushControlMixin:
    """
    Mixin for controlling airbrush paint flow via U/V axes.
    """
    
    def start_paint_flow(self, tool_index: int, width: float, opacity: float) -> Generator[GCodeInstruction, None, None]:
        """
        Start paint flow for the specified tool with given width and opacity.
        
        Args:
            tool_index: 0 for black (U axis), 1 for white (V axis)
            width: Controls the paint flow width
            opacity: Controls the paint density/opacity
            
        Yields:
            GCodeInstruction: G-code instructions for starting paint flow
        """
        axis = "U" if tool_index == 0 else "V"
        # Calculate flow value based on width and opacity
        flow_value = self._calculate_flow(width, opacity)
        
        # Switch to relative mode, set flow, return to absolute mode
        yield GCodeInstruction(code_type="G", code_number=91)  # G91: Relative positioning
        yield GCodeInstruction(code_type="G", code_number=1, parameters={axis: flow_value, "F": 300})  # Flow command
        yield GCodeInstruction(code_type="G", code_number=90)  # G90: Absolute positioning
    
    def stop_paint_flow(self, tool_index: int) -> Generator[GCodeInstruction, None, None]:
        """
        Stop paint flow for the specified tool.
        
        Args:
            tool_index: 0 for black (U axis), 1 for white (V axis)
            
        Yields:
            GCodeInstruction: G-code instruction for stopping paint flow
        """
        axis = "U" if tool_index == 0 else "V"
        yield GCodeInstruction(code_type="M", code_number=18, parameters={axis: None})  # M18 U/V: Disable stepper
    
    def _calculate_flow(self, width: float, opacity: float) -> float:
        """
        Calculate the flow value based on width and opacity parameters.
        
        Args:
            width: Width parameter (0.0-1.0)
            opacity: Opacity parameter (0.0-1.0)
            
        Returns:
            float: Flow value
        """
        # Clamp inputs to 0.0-1.0 range
        width = max(0.0, min(1.0, width))
        opacity = max(0.0, min(1.0, opacity))
        
        # Scale to the 0-4mm range (machine limit)
        base_flow = width * 4.0
        
        # Apply opacity scaling
        return base_flow * opacity 