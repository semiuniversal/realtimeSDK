"""
Fan-related G-code instructions.

These instructions control fans and cooling systems.
"""
from typing import Optional, ClassVar, List, Dict, Any
import re

from ..base import GInstruction, register_instruction


@register_instruction
class SetFanSpeed(GInstruction):
    """M106: Set fan speed."""
    code: ClassVar[str] = "M106"
    accepted_args: ClassVar[List[str]] = ["S", "P"]


@register_instruction
class FanOff(GInstruction):
    """M107: Turn fan off."""
    code: ClassVar[str] = "M107"
    accepted_args: ClassVar[List[str]] = ["P"]
