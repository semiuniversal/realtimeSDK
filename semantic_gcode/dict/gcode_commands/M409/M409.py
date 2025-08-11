"""
M409: Query object model
"""

# Python implementation for M409
# Based on: M409: Query object model

from __future__ import annotations
from typing import Optional, Dict, Any
import json

from semantic_gcode.gcode.base import GCodeInstruction, register_gcode_instruction
from semantic_gcode.gcode.mixins import ExpectsAcknowledgement


@register_gcode_instruction
class M409_QueryObjectModel(GCodeInstruction, ExpectsAcknowledgement):
    """M409: Query object model.

    Minimal support for K"path" queries. Example:
      M409 K"coords.machine"  -> {"coords":{"machine":[x,y,z,...]}}
    """

    code_type = "M"
    code_number = 409
    valid_parameters: list[str] = ["K"]

    @classmethod
    def create(cls, path: str) -> "M409_QueryObjectModel":
        # Ensure path is a string without surrounding quotes; the base class will render
        params = {"K": path}
        return cls(code_type="M", code_number=409, parameters=params, comment="Query object model")

    def parse_json(self, response: str) -> Dict[str, Any]:
        if not response:
            return {}
        txt = response.strip()
        try:
            # Extract JSON substring if the device wraps it with extra text
            if "{" in txt and "}" in txt:
                txt = txt[txt.find("{") : txt.rfind("}") + 1]
            return json.loads(txt)
        except Exception:
            return {}


def m409():
    """
    Implementation for M409: Query object model
    """
    pass

if __name__ == "__main__":
    print("GCode command: M409")
    m409()
