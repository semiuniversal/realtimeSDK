"""
homing_sequence.py - Homing sequence for the airbrush plotter
"""
from semantic_gcode.gcode.base import GCodeInstruction
from typing import Generator

def execute_homing_sequence() -> Generator[GCodeInstruction, None, None]:
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