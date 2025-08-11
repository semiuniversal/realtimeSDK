"""
M999: Restart
"""

# Python implementation for M999
# Based on: M999: Restart

# Can you add that to @commands.yaml   and update the @README.md
# ?from typing import Dict
from semantic_gcode.gcode.base import GCodeInstruction, register_gcode_instruction
from semantic_gcode.gcode.mixins import ExpectsAcknowledgement


@register_gcode_instruction
class M999_EmergencyStop(GCodeInstruction, ExpectsAcknowledgement):
    """M999: Emergency stop / reset.

    Sends an immediate firmware reset/estop. Behavior depends on firmware.
    For RepRapFirmware, this resets the machine; connection may drop.
    """

    code_type = "M"
    code_number = 999
    valid_parameters: list[str] = []

    @classmethod
    def create(cls) -> "M999_EmergencyStop":
        return cls(code_type="M", code_number=999, parameters={}, comment="Emergency stop / reset")

    def validate_response(self, response: str) -> bool:
        # Any response is acceptable; many firmwares reset and may not reply
        return True
