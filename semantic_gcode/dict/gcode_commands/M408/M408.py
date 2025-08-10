"""
M408: Report JSON-style response (RepRapFirmware object model)

This command reports machine status in JSON-like format.
Common usage: M408 S0 to report overall status including state code.
"""

from typing import Optional, Dict, Any
import json
import re
from semantic_gcode.gcode.base import GCodeInstruction, register_gcode_instruction
from semantic_gcode.gcode.mixins import ExpectsAcknowledgement, PositionProvider, TemperatureProvider


@register_gcode_instruction
class M408_ReportObjectModel(GCodeInstruction, ExpectsAcknowledgement, PositionProvider, TemperatureProvider):
    """
    M408: Report JSON-style response

    Parameters:
    - S: report selector (0 is common overall status)
    - F: format selector
    """
    code_type = "M"
    code_number = 408

    valid_parameters = ["S", "F"]

    @classmethod
    def create(cls, selector: Optional[int] = 0) -> "M408_ReportObjectModel":
        params: Dict[str, Any] = {}
        if selector is not None:
            params["S"] = selector
        return cls(code_type="M", code_number=408, parameters=params, comment="Report object model")

    def parse_status(self, response: str) -> Dict[str, Any]:
        """
        Parse a subset of the object model from response.
        Accepts either JSON or key:value style lines. Returns {'status': code or None, 'raw'|'raw_text': ...}
        """
        if not response:
            return {"status": None, "raw_text": response}
        # Try to locate a JSON object on the last line first
        lines = [ln.strip() for ln in response.splitlines() if ln.strip()]
        json_line = None
        for ln in reversed(lines):
            if ln.startswith("{") and ln.endswith("}"):
                json_line = ln
                break
        try:
            data = json.loads(json_line if json_line else response)
            status = data.get("status") or data.get("state") or data.get("machineState")
            return {"status": status, "raw": data}
        except Exception:
            pass
        # Regex fallback for status code
        compact = response.replace(" ", "")
        m = re.search(r'"status"\s*:\s*"([A-Za-z])"', compact)
        if m:
            return {"status": m.group(1), "raw_text": response}
        return {"status": None, "raw_text": response}

    def execute(self, device) -> Optional[str]:
        response = device.send(str(self))
        return response
