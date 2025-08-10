"""
Semantic G-code SDK.

A device-independent, real-time control SDK for G-code machines.
"""

__version__ = "0.1.0"

# Import key components for easy access
from .sd_card import SDCard, FileInfo, PrintStatus, FileMetadata
from .config import AliasSystem, ComponentAlias, AliasCompositeFunction as CompositeFunction, MachineProfile
