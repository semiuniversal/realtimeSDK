"""
G-code instruction classes for semantic representation of G-code commands.

This package provides classes for representing G-code commands as semantic Python objects,
with bidirectional conversion between the semantic representation and raw G-code.
"""
from .base import GInstruction, GCodeRegistry, register_instruction

# Import instructions from the instructions package
from .instructions.motion import RapidMove, MoveTo, ArcMove, Dwell
from .instructions.state import (
    SetAbsolutePositioning,
    SetRelativePositioning,
    SetUnitsMM,
    SetUnitsInch,
    SetPositionOrigin,
    SetAbsoluteExtruderMode,
    SetRelativeExtruderMode
)
from .instructions.tool import SelectTool, DefineTool
from .instructions.temperature import (
    SetExtruderTemp,
    SetExtruderTempAndWait,
    SetBedTemp,
    SetBedTempAndWait,
    GetTemperatures
)
from .instructions.fan import SetFanSpeed, FanOff
from .instructions.system import EmergencyStop, GetFirmwareVersion, DisplayMessage, SendMessage

__all__ = [
    # Base classes
    'GInstruction',
    'GCodeRegistry',
    'register_instruction',
    
    # Motion instructions
    'RapidMove',
    'MoveTo',
    'ArcMove',
    'Dwell',
    
    # State instructions
    'SetAbsolutePositioning',
    'SetRelativePositioning',
    'SetUnitsMM',
    'SetUnitsInch',
    'SetPositionOrigin',
    'SetAbsoluteExtruderMode',
    'SetRelativeExtruderMode',
    
    # Tool instructions
    'SelectTool',
    'DefineTool',
    
    # Temperature instructions
    'SetExtruderTemp',
    'SetExtruderTempAndWait',
    'SetBedTemp',
    'SetBedTempAndWait',
    'GetTemperatures',
    
    # Fan instructions
    'SetFanSpeed',
    'FanOff',
    
    # System instructions
    'EmergencyStop',
    'GetFirmwareVersion',
    'DisplayMessage',
    'SendMessage'
]
