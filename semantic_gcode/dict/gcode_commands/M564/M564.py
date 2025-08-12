from __future__ import annotations

"""
M564: Limit axes

- Hnnn: H1 = forbid movement of axes that have not been homed, H0 = allow
- Snnn: S1 = limit movement within axis boundaries, S0 = allow outside boundaries

Reference: 182_M564__Limit_axes.md
"""

from typing import Optional, Dict

from semantic_gcode.gcode.base import GCodeInstruction, register_gcode_instruction


@register_gcode_instruction
class M564_LimitAxes(GCodeInstruction):
    """M564: Limit axes and homing constraints.

    Examples:
      - M564 S0 H0  (allow moves outside volume and before homing)
      - M564 S1 H1  (default: enforce limits and require homing)
    """

    code_type = "M"
    code_number = 564
    valid_parameters: list[str] = ["S", "H"]

    @classmethod
    def create(
        cls,
        limit_within_bounds: Optional[bool] = None,
        require_homing_before_move: Optional[bool] = None,
    ) -> "M564_LimitAxes":
        """Factory to create M564 with boolean-friendly parameters.

        Args:
          limit_within_bounds: If True -> S1, False -> S0, None -> omit S
          require_homing_before_move: If True -> H1, False -> H0, None -> omit H
        """
        params: Dict[str, int] = {}
        if limit_within_bounds is not None:
            params["S"] = 1 if bool(limit_within_bounds) else 0
        if require_homing_before_move is not None:
            params["H"] = 1 if bool(require_homing_before_move) else 0
        return cls(code_type="M", code_number=564, parameters=params, comment="Limit axes")

    def describe(self) -> str:
        s = self.parameters.get("S")
        h = self.parameters.get("H")
        parts = []
        if s is not None:
            parts.append(f"S{int(s)}")
        if h is not None:
            parts.append(f"H{int(h)}")
        args = " ".join(parts) if parts else "<defaults>"
        return f"M564 {args} (limit axes / homing constraints)"
