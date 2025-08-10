"""
PlotterMotionMixin for specialized motion control.

This module provides a mixin for specialized motion control for the airbrush plotter.
"""

from typing import Dict, Any, Optional, Union, List, Generator, Tuple
import time

from semantic_gcode.gcode.base import GCodeInstruction, Numeric


class PlotterMotionMixin:
    """
    Mixin for specialized plotter motion control.
    """
    
    def safe_move_to(self, x: float, y: float, feedrate: float = 3000) -> Generator[GCodeInstruction, None, None]:
        """
        Move to a position safely by first raising Z to safe height.
        
        Args:
            x: X position
            y: Y position
            feedrate: Movement speed
            
        Yields:
            GCodeInstruction: G-code instructions for safe movement
        """
        # First raise Z to safe height if not already there
        yield GCodeInstruction(
            code_type="G",
            code_number=1,
            parameters={"Z": 5.0, "F": 1000}  # Z5: Safe height
        )
        
        # Then move to XY position
        yield GCodeInstruction(
            code_type="G",
            code_number=0,  # G0: Rapid move
            parameters={"X": x, "Y": y, "F": feedrate}
        )
    
    def lower_to_spray_height(self, feedrate: float = 500) -> Generator[GCodeInstruction, None, None]:
        """
        Lower Z to spray height.
        
        Args:
            feedrate: Movement speed
            
        Yields:
            GCodeInstruction: G-code instruction for lowering Z
        """
        yield GCodeInstruction(
            code_type="G",
            code_number=1,
            parameters={"Z": 1.5, "F": feedrate}  # Z1.5: Spray height
        )
    
    def raise_to_safe_height(self, feedrate: float = 1000) -> Generator[GCodeInstruction, None, None]:
        """
        Raise Z to safe travel height.
        
        Args:
            feedrate: Movement speed
            
        Yields:
            GCodeInstruction: G-code instruction for raising Z
        """
        yield GCodeInstruction(
            code_type="G",
            code_number=1,
            parameters={"Z": 5.0, "F": feedrate}  # Z5: Safe height
        )
    
    def move_along_path(self, path_points: List[Tuple[float, float]], feedrate: float = 1500) -> Generator[GCodeInstruction, None, None]:
        """
        Move along a path of points.
        
        Args:
            path_points: List of (x, y) coordinates
            feedrate: Movement speed
            
        Yields:
            GCodeInstruction: G-code instructions for path movement
        """
        for x, y in path_points:
            yield GCodeInstruction(
                code_type="G",
                code_number=1,  # G1: Controlled move
                parameters={"X": x, "Y": y, "F": feedrate}
            )
    
    def home_axes(self, axes: Optional[List[str]] = None) -> Generator[GCodeInstruction, None, None]:
        """
        Home the specified axes or all axes if none specified.
        
        Args:
            axes: List of axes to home (e.g., ["X", "Y"])
            
        Yields:
            GCodeInstruction: G-code instruction for homing
        """
        params = {}
        if axes:
            for axis in axes:
                params[axis] = None
        
        yield GCodeInstruction(
            code_type="G",
            code_number=28,
            parameters=params
        )
    
    def set_absolute_positioning(self) -> Generator[GCodeInstruction, None, None]:
        """
        Set absolute positioning mode.
        
        Yields:
            GCodeInstruction: G-code instruction for absolute positioning
        """
        yield GCodeInstruction(
            code_type="G",
            code_number=90
        )
    
    def set_relative_positioning(self) -> Generator[GCodeInstruction, None, None]:
        """
        Set relative positioning mode.
        
        Yields:
            GCodeInstruction: G-code instruction for relative positioning
        """
        yield GCodeInstruction(
            code_type="G",
            code_number=91
        )
    
    def disable_bounds_checking(self) -> Generator[GCodeInstruction, None, None]:
        """
        Disable machine bounds checking.
        
        Yields:
            GCodeInstruction: G-code instruction for disabling bounds checking
        """
        yield GCodeInstruction(
            code_type="M",
            code_number=120
        )
    
    def enable_bounds_checking(self) -> Generator[GCodeInstruction, None, None]:
        """
        Enable machine bounds checking.
        
        Yields:
            GCodeInstruction: G-code instruction for enabling bounds checking
        """
        yield GCodeInstruction(
            code_type="M",
            code_number=121
        ) 