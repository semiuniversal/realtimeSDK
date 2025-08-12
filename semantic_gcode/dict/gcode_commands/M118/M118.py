from __future__ import annotations

"""
M118: Send Message to Specific Target

RepRapFirmware: M118 P<channel> S"message"
- P is optional (selects output channel; if omitted, sends to default/active)
- S is the message string (quoted)

This implementation focuses on building a safe S parameter for tagging acks.
"""

from typing import Optional, Dict, Any, List

from semantic_gcode.gcode.base import GCodeInstruction, register_gcode_instruction
from semantic_gcode.gcode.mixins import ExpectsAcknowledgement


@register_gcode_instruction
class M118_SendMessage(GCodeInstruction, ExpectsAcknowledgement):
    """M118: Send message to host/log targets.

    Typical usage for tagged-ack mechanism:
      M118 S"AB#1234ABCD"
    """

    code_type = "M"
    code_number = 118
    valid_parameters: list[str] = ["P", "S"]

    @classmethod
    def create(cls, message: str, p: Optional[int] = None) -> "M118_SendMessage":
        params: Dict[str, object] = {}
        if p is not None:
            params["P"] = int(p)
        # Quote and escape the message
        safe = message.replace("\\", "\\\\").replace("\"", "\\\"")
        params["S"] = f'"{safe}"'
        return cls(code_type="M", code_number=118, parameters=params, comment="Send message")

    def validate_response(self, response: str) -> bool:
        """Basic validator used when a plain ack is acceptable.
        For tagged-ack use cases, the dispatcher should look for the echoed message, not rely on this.
        """
        if not response:
            return False
        lower = response.lower()
        if "ok" in lower:
            return True
        # Echo match: message text present in response
        msg = self.parameters.get("S") if hasattr(self, "parameters") else None
        if isinstance(msg, str):
            # msg is quoted; search without quotes too
            token = msg.strip('"')
            if token and token in response:
                return True
        return False

    @staticmethod
    def extract_echoes(response: str) -> List[str]:
        """Extract non-ok echo lines from a reply blob."""
        out: List[str] = []
        for ln in (response or "").splitlines():
            s = ln.strip()
            if not s:
                continue
            if s.lower() == "ok":
                continue
            out.append(s)
        return out
