"""
System-related G-code instructions.

These instructions control machine-level operations like emergency stop,
firmware information, etc.
"""
from typing import Optional, ClassVar, List, Dict, Any
import re

from ..base import GInstruction, register_instruction


@register_instruction
class EmergencyStop(GInstruction):
    """M112: Emergency stop."""
    code: ClassVar[str] = "M112"
    accepted_args: ClassVar[List[str]] = []


@register_instruction
class GetFirmwareVersion(GInstruction):
    """M115: Get firmware version and capabilities."""
    code: ClassVar[str] = "M115"
    accepted_args: ClassVar[List[str]] = []


@register_instruction
class DisplayMessage(GInstruction):
    """M117: Display message on LCD."""
    code: ClassVar[str] = "M117"
    accepted_args: ClassVar[List[str]] = []


@register_instruction
class SendMessage(GInstruction):
    """M118: Send message to host."""
    code: ClassVar[str] = "M118"
    accepted_args: ClassVar[List[str]] = ["P"]
