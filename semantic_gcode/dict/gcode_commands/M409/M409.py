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

    Minimal support for K"path" queries with optional S level. Example:
      M409 K"coords.machine" S2  -> {"key":"coords.machine","result":{"coords":{"machine":[...]}}}
      M409 K"move.axes[].machinePosition" S2 -> {"key":"...","result":[...]} (positions list)
    """

    code_type = "M"
    code_number = 409
    valid_parameters: list[str] = ["K", "S"]

    @classmethod
    def create(cls, path: str, s: Optional[int] = 2) -> "M409_QueryObjectModel":
        # Quote the K path explicitly; include S level if provided
        quoted = f'"{path}"'
        params: Dict[str, object] = {"K": quoted}
        if s is not None:
            params["S"] = int(s)
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
