"""
M119: Get Endstop Status

Queries the current state of configured endstops/switches. Output is typically
textual, listing each axis and whether it is stopped or not.
"""

from typing import Dict
from semantic_gcode.gcode.base import GCodeInstruction, register_gcode_instruction
from semantic_gcode.gcode.mixins import ExpectsAcknowledgement


@register_gcode_instruction
class M119_EndstopStatus(GCodeInstruction, ExpectsAcknowledgement):
    """
    M119: Get Endstop Status

    Behavior:
    - Expects a textual response listing axes and their stop states.
    - Provides a helper to parse a map like {"X": 0/1, "Y": 0/1, ...}.
    """

    code_type = "M"
    code_number = 119

    valid_parameters: list[str] = []

    @classmethod
    def create(cls) -> "M119_EndstopStatus":
        return cls(code_type="M", code_number=119, parameters={}, comment="Get endstop status")

    def validate_response(self, response: str) -> bool:
        return bool(response and response.strip())

    def parse_endstops(self, response: str) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for ln in response.splitlines():
            lower = ln.lower()
            if any(axis in lower for axis in ("x:", "y:", "z:", "u:", "v:")):
                for axis in ("x", "y", "z", "u", "v"):
                    if f"{axis}:" in lower:
                        try:
                            val = lower.split(f"{axis}:")[-1].split(',')[0].strip()
                            out[axis.upper()] = 1 if "stopped" in val else 0
                        except Exception:
                            pass
        return out


def m119() -> M119_EndstopStatus:
    """Convenience function for M119."""
    return M119_EndstopStatus.create()
