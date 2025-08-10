"""
M106: Fan On/Off/Speed Control

Controls a fan output. In this project we use specific fan indices to control
air for the airbrush tools (e.g., P2/P3). S is typically 0..1 in RRF.
"""

from typing import Optional, Dict
from semantic_gcode.gcode.base import GCodeInstruction, register_gcode_instruction
from semantic_gcode.gcode.mixins import ExpectsAcknowledgement


@register_gcode_instruction
class M106_FanControl(GCodeInstruction, ExpectsAcknowledgement):
    """
    M106: Fan Control

    Parameters:
    - P: Fan index
    - S: Speed (0.0 .. 1.0)
    """

    code_type = "M"
    code_number = 106

    valid_parameters = ["P", "S"]

    @classmethod
    def create(cls, p: Optional[int] = None, s: Optional[float] = None) -> "M106_FanControl":
        params: Dict[str, object] = {}
        if p is not None:
            params["P"] = int(p)
        if s is not None:
            # Clamp to [0,1]
            try:
                s_val = float(s)
            except Exception:
                s_val = 0.0
            s_val = max(0.0, min(1.0, s_val))
            params["S"] = s_val
        return cls(code_type="M", code_number=106, parameters=params, comment="Fan control")

    def validate_response(self, response: str) -> bool:
        # Accept ok/any non-empty as acknowledgment
        return bool(response and response.strip())


def m106(p: Optional[int] = None, s: Optional[float] = None) -> M106_FanControl:
    return M106_FanControl.create(p=p, s=s)

if __name__ == "__main__":
    print("GCode command: M106")
    instruction = m106(s=0.5)
    print(str(instruction))
    
    # Example with fan number
    instruction = m106(p=1, s=1.0)
    print(str(instruction))
    
    # Example with thermostatic mode
    instruction = m106(p=2, s=0.0)
    print(str(instruction))
