from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class HttpQuerySpec:
    endpoint: str
    params: Dict[str, str]


@dataclass
class SerialQuerySpec:
    command: str


class TransportStrategy:
    @staticmethod
    def http_fast() -> List[HttpQuerySpec]:
        return [
            HttpQuerySpec(endpoint="rr_model", params={"key": "move.axes[].machinePosition", "flags": "f"}),
            HttpQuerySpec(endpoint="rr_model", params={"key": "state.status", "flags": "f"}),
            HttpQuerySpec(endpoint="rr_model", params={"key": "heat.heaters[].current", "flags": "f"}),
        ]

    @staticmethod
    def http_medium() -> List[HttpQuerySpec]:
        return [
            HttpQuerySpec(endpoint="rr_model", params={"key": "tools"}),
            HttpQuerySpec(endpoint="rr_model", params={"key": "move.axes[].homed"}),
            HttpQuerySpec(endpoint="rr_model", params={"key": "job.progress"}),
            HttpQuerySpec(endpoint="rr_model", params={"key": "boards[].vIn.current", "flags": "f"}),
            HttpQuerySpec(endpoint="rr_model", params={"key": "boards[].mcuTemp.current", "flags": "f"}),
        ]

    @staticmethod
    def http_endstops() -> HttpQuerySpec:
        return HttpQuerySpec(endpoint="rr_model", params={"key": "sensors.endstops[].triggered", "flags": "f"})

    @staticmethod
    def serial_fast() -> List[SerialQuerySpec]:
        return [
            SerialQuerySpec('M409 K"move.axes[].machinePosition" F"f"'),
            SerialQuerySpec('M409 K"state.status" F"f"'),
            SerialQuerySpec('M409 K"heat.heaters[].current" F"f"'),
        ]

    @staticmethod
    def serial_medium() -> List[SerialQuerySpec]:
        return [
            SerialQuerySpec('M409 K"tools"'),
            SerialQuerySpec('M409 K"move.axes[].homed"'),
            SerialQuerySpec('M409 K"job.progress"'),
            SerialQuerySpec('M409 K"boards[].vIn.current" F"f"'),
            SerialQuerySpec('M409 K"boards[].mcuTemp.current" F"f"'),
        ]

    @staticmethod
    def serial_endstops() -> SerialQuerySpec:
        return SerialQuerySpec('M409 K"sensors.endstops[].triggered" F"f"') 