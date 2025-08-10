"""
AirControlMixin for controlling air solenoids.

This module provides a mixin for controlling the air solenoids via fan outputs.
"""

from typing import Dict, Any, Optional, Union, List, Generator
import time

from semantic_gcode.gcode.base import GCodeInstruction, Numeric


class AirControlMixin:
    """
    Mixin for controlling airbrush air solenoids.
    """
    
    def start_air(self, tool_index: int, fan_index: Optional[int] = None) -> Generator[GCodeInstruction, None, None]:
        """
        Start air flow (solenoid open) for the specified tool.
        
        Args:
            tool_index: 0 for black, 1 for white
            fan_index: Fan index override (defaults to 2 for tool 0, 3 for tool 1)
            
        Yields:
            GCodeInstruction: G-code instruction for starting air flow
        """
        if fan_index is None:
            fan_index = 2 if tool_index == 0 else 3
            
        # M106 P<fan_index> S1.0: Fan ON
        yield GCodeInstruction(
            code_type="M",
            code_number=106,
            parameters={"P": fan_index, "S": 1.0}
        )
    
    def stop_air(self, tool_index: int, fan_index: Optional[int] = None) -> Generator[GCodeInstruction, None, None]:
        """
        Stop air flow (solenoid closed) for the specified tool.
        
        Args:
            tool_index: 0 for black, 1 for white
            fan_index: Fan index override (defaults to 2 for tool 0, 3 for tool 1)
            
        Yields:
            GCodeInstruction: G-code instruction for stopping air flow
        """
        if fan_index is None:
            fan_index = 2 if tool_index == 0 else 3
            
        # M106 P<fan_index> S0: Fan OFF
        yield GCodeInstruction(
            code_type="M",
            code_number=106,
            parameters={"P": fan_index, "S": 0.0}
        )
    
    def wait_for_air_stabilization(self, milliseconds: int = 50) -> Generator[GCodeInstruction, None, None]:
        """
        Wait for air to stabilize after turning it on.
        
        Args:
            milliseconds: Wait time in milliseconds
            
        Yields:
            GCodeInstruction: G-code instruction for waiting
        """
        # G4 P<milliseconds>: Dwell
        yield GCodeInstruction(
            code_type="G",
            code_number=4,
            parameters={"P": milliseconds}
        ) 