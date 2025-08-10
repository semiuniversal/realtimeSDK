from typing import Dict, Any, Optional
import threading


class MachineState:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._predictive: Dict[str, Any] = {}
        self._observed: Dict[str, Any] = {}

    def apply_predictive(self, instruction: Any) -> None:
        if not hasattr(instruction, "apply"):
            return
        with self._lock:
            self._predictive = instruction.apply(dict(self._predictive))

    def _deep_merge(self, base: Dict[str, Any], patch: Dict[str, Any]) -> Dict[str, Any]:
        out = dict(base)
        for k, v in (patch or {}).items():
            if isinstance(v, dict) and isinstance(out.get(k), dict):
                out[k] = self._deep_merge(out.get(k, {}), v)
            else:
                out[k] = v
        return out

    def update_observed(self, observed: Dict[str, Any]) -> None:
        with self._lock:
            # Merge incrementally so previously known values persist
            self._observed = self._deep_merge(self._observed, observed or {})

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            snap = {
                "predictive": dict(self._predictive),
                "observed": dict(self._observed),
            }
            return snap 