"""
gradient_sequence.py - Gradient stroke sequence for the airbrush plotter
"""
from semantic_gcode.gcode.base import GCodeInstruction
from typing import Generator

def execute_gradient(tool_index: int, x1: float, y1: float, x2: float, y2: float, segments: int, width: float = 1.0, opacity: float = 1.0) -> Generator[GCodeInstruction, None, None]:
    """
    Execute a gradient stroke from (x1, y1) to (x2, y2) with specified segments, width, and opacity.
    Yields:
        GCodeInstruction: G-code instructions for the gradient stroke
    """
    # Linear interpolation for width/opacity along the path
    for i in range(segments):
        t0 = i / segments
        t1 = (i + 1) / segments
        px0 = x1 + (x2 - x1) * t0
        py0 = y1 + (y2 - y1) * t0
        px1 = x1 + (x2 - x1) * t1
        py1 = y1 + (y2 - y1) * t1
        seg_width = width * (1 - t0) + width * t1  # Simple linear, can be improved
        seg_opacity = opacity * (1 - t0) + opacity * t1
        from .stroke_sequence import execute_stroke
        for instr in execute_stroke(tool_index, [(px0, py0), (px1, py1)], seg_width, seg_opacity):
            yield instr 