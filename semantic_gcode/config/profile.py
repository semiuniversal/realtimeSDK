from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class AxisConfig:
    name: str
    limits: List[float] = field(default_factory=lambda: [0.0, 0.0])
    steps_per_mm: Optional[float] = None
    max_speed: Optional[float] = None
    max_acceleration: Optional[float] = None


@dataclass
class ToolConfig:
    number: int
    name: str = ""
    offsets: Dict[str, float] = field(default_factory=dict)


@dataclass
class MachineProfile:
    """Minimal machine profile capturing axes and tools.

    This trimmed version intentionally avoids deeper config dependencies.
    """

    name: str = ""
    axes: Dict[str, AxisConfig] = field(default_factory=dict)
    tools: Dict[int, ToolConfig] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_axis(self, axis: AxisConfig) -> None:
        self.axes[axis.name.upper()] = axis

    def add_tool(self, tool: ToolConfig) -> None:
        self.tools[int(tool.number)] = tool

    def get_axis(self, name: str) -> Optional[AxisConfig]:
        return self.axes.get(name.upper())

    def get_tool(self, number: int) -> Optional[ToolConfig]:
        return self.tools.get(int(number)) 