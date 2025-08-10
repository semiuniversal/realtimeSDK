"""
Temperature-related G-code instructions.

These instructions control heaters, temperature monitoring, etc.
"""
from typing import Optional, ClassVar, List, Dict, Any
import re

from ..base import GInstruction, register_instruction


@register_instruction
class SetExtruderTemp(GInstruction):
    """M104: Set extruder temperature without waiting."""
    code: ClassVar[str] = "M104"
    accepted_args: ClassVar[List[str]] = ["S", "T"]


@register_instruction
class SetExtruderTempAndWait(GInstruction):
    """M109: Set extruder temperature and wait."""
    code: ClassVar[str] = "M109"
    accepted_args: ClassVar[List[str]] = ["S", "T", "R"]


@register_instruction
class SetBedTemp(GInstruction):
    """M140: Set bed temperature without waiting."""
    code: ClassVar[str] = "M140"
    accepted_args: ClassVar[List[str]] = ["S"]


@register_instruction
class SetBedTempAndWait(GInstruction):
    """M190: Set bed temperature and wait."""
    code: ClassVar[str] = "M190"
    accepted_args: ClassVar[List[str]] = ["S", "R"]


@register_instruction
class GetTemperatures(GInstruction):
    """M105: Get temperature readings."""
    code: ClassVar[str] = "M105"
    accepted_args: ClassVar[List[str]] = []
