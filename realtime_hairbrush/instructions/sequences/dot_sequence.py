"""
dot_sequence.py - Dot stroke sequence for the airbrush plotter
"""
from semantic_gcode.gcode.base import GCodeInstruction
from typing import Generator

def execute_dot(tool_index: int, x: float, y: float, width: float = 1.0, opacity: float = 1.0, duration: float = 1.0) -> Generator[GCodeInstruction, None, None]:
    """
    Execute a dot stroke at (x, y) with specified width, opacity, and duration.
    Yields:
        GCodeInstruction: G-code instructions for the dot stroke
    """
    spray_z_height = 1.5 + (width * 0.5)
    fan_index = 2 if tool_index == 0 else 3
    axis = "U" if tool_index == 0 else "V"
    # 1. Select tool
    yield GCodeInstruction(code_type='T', code_number=tool_index, comment=f"Select tool {tool_index}")
    # 2. Move to safe Z height
    yield GCodeInstruction(code_type='G', code_number=1, parameters={'Z': 10.0, 'F': 1000}, comment="Move to safe Z height")
    # 3. Move to position
    yield GCodeInstruction(code_type='G', code_number=0, parameters={'X': x, 'Y': y, 'F': 3000}, comment="Move to dot position")
    # 4. Lower to spray height
    yield GCodeInstruction(code_type='G', code_number=1, parameters={'Z': spray_z_height, 'F': 500}, comment="Lower to spray height")
    # 5. Start air
    yield GCodeInstruction(code_type='M', code_number=106, parameters={'P': fan_index, 'S': 1.0}, comment="Air ON")
    # 6. Wait for air to stabilize
    yield GCodeInstruction(code_type='G', code_number=4, parameters={'P': 50}, comment="Wait for air to stabilize")
    # 7. Start paint flow
    yield GCodeInstruction(code_type='G', code_number=91, comment="Relative positioning")
    flow_value = width * opacity * 4.0
    yield GCodeInstruction(code_type='G', code_number=1, parameters={axis: flow_value, 'F': 300}, comment=f"Start paint flow: width={width}, opacity={opacity}")
    yield GCodeInstruction(code_type='G', code_number=90, comment="Absolute positioning")
    # 8. Dwell for the specified duration
    dwell_ms = int(duration * 1000)
    yield GCodeInstruction(code_type='G', code_number=4, parameters={'P': dwell_ms}, comment=f"Dwell for {dwell_ms} ms")
    # 9. Stop paint flow
    yield GCodeInstruction(code_type='M', code_number=18, parameters={axis: None}, comment="Stop paint flow")
    # 10. Wait for paint tail to clear
    yield GCodeInstruction(code_type='G', code_number=4, parameters={'P': 50}, comment="Wait for paint tail to clear")
    # 11. Stop air
    yield GCodeInstruction(code_type='M', code_number=106, parameters={'P': fan_index, 'S': 0.0}, comment="Air OFF")
    # 12. Raise to safe Z height
    yield GCodeInstruction(code_type='G', code_number=1, parameters={'Z': 10.0, 'F': 1000}, comment="Raise to safe Z height") 