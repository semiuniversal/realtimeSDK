import threading
import time
from typing import Optional, Callable, List

from .state import MachineState
from ..transport.airbrush_transport import AirbrushTransport
from .events import StateUpdatedEvent
from .sequencer import RequestSequencer, Request, Priority, RequestKind
from .sequencer import HttpQuerySpec, SerialQuerySpec


class StatusPoller:
    def __init__(
        self,
        sequencer: RequestSequencer,
        state: MachineState,
        emit: Optional[Callable] = None,
        interval_fast: float = 0.5,
        interval_medium: float = 2.5,
        interval_slow: float = 25.0,
        interval_full: float = 5.0,
    ) -> None:
        self.sequencer = sequencer
        self.state = state
        self.emit = emit or (lambda e: None)
        self.interval_fast = float(interval_fast)
        self.interval_medium = float(interval_medium)
        self.interval_slow = float(interval_slow)
        self.interval_full = float(interval_full)
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._last_fast: float = 0.0
        self._last_medium: float = 0.0
        self._last_slow: float = 0.0
        self._last_full: float = 0.0

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1.0)

    def _submit_query(self, spec, priority: Priority, coalesce_key: str) -> None:
        def on_complete(res):
            if not res or not res.ok or res.data is None:
                return
            try:
                data = res.data
                if isinstance(spec, HttpQuerySpec):
                    key = spec.params.get("key")
                elif isinstance(spec, SerialQuerySpec):
                    cmd = spec.command
                    key = None
                    if 'K"' in cmd or "K'" in cmd:
                        try:
                            # Extract key after K"..." or K'...'
                            if 'K"' in cmd:
                                key = cmd.split('K"', 1)[1].split('"', 1)[0]
                            else:
                                key = cmd.split("K'", 1)[1].split("'", 1)[0]
                        except Exception:
                            key = None
                else:
                    key = None
                import json
                raw = None
                if isinstance(data, str):
                    txt = data.strip()
                    if "{" in txt and "}" in txt:
                        txt = txt[txt.find("{") : txt.rfind("}") + 1]
                    try:
                        raw = json.loads(txt)
                    except Exception:
                        raw = {}
                elif isinstance(data, dict):
                    raw = data
                result = raw.get("result") if isinstance(raw, dict) else None
                patch = {"raw_status": {"raw": {}}}
                if key == "move.axes[].userPosition" and isinstance(result, list):
                    # Store logical/user coordinates and also mirror to coords.machine for UI compatibility
                    patch.setdefault("coords", {})["user_position"] = result
                    patch["raw_status"]["raw"].setdefault("coords", {})["userPosition"] = result
                    # Mirror to legacy keys so UI shows logical coords
                    patch["raw_status"]["raw"].setdefault("coords", {})["machine"] = result
                elif key == "move.axes[].machinePosition" and isinstance(result, list):
                    patch.setdefault("coords", {})["machine_position"] = result
                    patch["raw_status"]["raw"].setdefault("coords", {})["machine"] = result
                elif key == "state.status" and (isinstance(result, str) or result is None):
                    patch.setdefault("firmware", {})["status"] = result
                elif key == "move.axes[].homed" and isinstance(result, list):
                    patch.setdefault("homed", {})["axes"] = result
                    patch["raw_status"]["raw"].setdefault("coords", {})["axesHomed"] = result
                elif key == "state.currentTool" and (isinstance(result, int) or result is None):
                    patch["raw_status"]["raw"]["currentTool"] = result
                elif key == "sensors.endstops[].triggered" and isinstance(result, list):
                    ends = {}
                    for idx, val in enumerate(result):
                        try:
                            axis = ["X","Y","Z","U","V"][idx]
                        except Exception:
                            axis = str(idx)
                        ends[axis] = 1 if val else 0
                    patch.setdefault("endstops", {}).update(ends)
                elif key == "boards[].vIn.current" and (isinstance(result, (int, float, list))):
                    vin = None
                    if isinstance(result, list) and result:
                        vin = result[0]
                    elif isinstance(result, (int, float)):
                        vin = result
                    if vin is not None:
                        patch.setdefault("diagnostics", {})["vin"] = float(vin)
                elif key == "boards[].mcuTemp.current" and (isinstance(result, (int, float, list))):
                    mcu = None
                    if isinstance(result, list) and result:
                        mcu = result[0]
                    elif isinstance(result, (int, float)):
                        mcu = result
                    if mcu is not None:
                        patch.setdefault("diagnostics", {})["mcu_temp_c"] = float(mcu)
                if patch:
                    snap = self.state.snapshot().get("observed", {})
                    merged = dict(snap)
                    def deep_merge(a, b):
                        if not isinstance(a, dict) or not isinstance(b, dict):
                            return b
                        out = dict(a)
                        for k, v in b.items():
                            out[k] = deep_merge(out.get(k, {}), v) if isinstance(v, dict) else v
                        return out
                    merged = deep_merge(merged, patch)
                    self.state.update_observed(merged)
                    self.emit(StateUpdatedEvent(state=self.state.snapshot()))
            except Exception:
                return

        req = Request(kind=RequestKind.QUERY, priority=priority, payload=spec, timeout_s=2.0, on_complete=on_complete)
        req.coalesce_key = coalesce_key
        self.sequencer.submit(req)

    def _run(self) -> None:
        # Build tiered sets of queries
        http_fast = [
            HttpQuerySpec(endpoint="rr_model", params={"key": "move.axes[].userPosition", "flags": "f"}),
            HttpQuerySpec(endpoint="rr_model", params={"key": "state.status", "flags": "f"}),
            HttpQuerySpec(endpoint="rr_model", params={"key": "state.currentTool", "flags": "f"}),
            HttpQuerySpec(endpoint="rr_model", params={"key": "sensors.endstops[].triggered", "flags": "f"}),
        ]
        http_medium = [
            HttpQuerySpec(endpoint="rr_model", params={"key": "move.axes[].homed"}),
            HttpQuerySpec(endpoint="rr_model", params={"key": "boards[].vIn.current", "flags": "f"}),
            HttpQuerySpec(endpoint="rr_model", params={"key": "boards[].mcuTemp.current", "flags": "f"}),
        ]
        # Periodic full refresh (5s) to keep UI accurate while idle
        http_full = [
            HttpQuerySpec(endpoint="rr_model", params={"key": "state.status", "flags": "f"}),
            HttpQuerySpec(endpoint="rr_model", params={"key": "state.currentTool", "flags": "f"}),
            HttpQuerySpec(endpoint="rr_model", params={"key": "move.axes[].userPosition", "flags": "f"}),
            HttpQuerySpec(endpoint="rr_model", params={"key": "move.axes[].homed"}),
            HttpQuerySpec(endpoint="rr_model", params={"key": "sensors.endstops[].triggered", "flags": "f"}),
        ]
        serial_fast = [
            SerialQuerySpec('M409 K"move.axes[].userPosition" F"f"'),
            SerialQuerySpec('M409 K"state.status" F"f"'),
            SerialQuerySpec('M409 K"state.currentTool" F"f"'),
            SerialQuerySpec('M409 K"sensors.endstops[].triggered" F"f"'),
        ]
        serial_medium = [
            SerialQuerySpec('M409 K"move.axes[].homed"'),
            SerialQuerySpec('M409 K"boards[].vIn.current" F"f"'),
            SerialQuerySpec('M409 K"boards[].mcuTemp.current" F"f"'),
        ]
        serial_full = [
            SerialQuerySpec('M409 K"state.status" F"f"'),
            SerialQuerySpec('M409 K"state.currentTool" F"f"'),
            SerialQuerySpec('M409 K"move.axes[].userPosition" F"f"'),
            SerialQuerySpec('M409 K"move.axes[].homed"'),
            SerialQuerySpec('M409 K"sensors.endstops[].triggered" F"f"'),
        ]
        # Detect if HTTP rr_model is available; if not, use serial specs directly
        def http_available() -> bool:
            try:
                inner = getattr(self.sequencer.transport, 'transport', self.sequencer.transport)
                inner2 = getattr(inner, 'transport', inner)
                return callable(getattr(inner2, 'get_model', None))
            except Exception:
                return False
        while not self._stop.is_set():
            now = time.time()
            # Fast tier (250ms)
            if now - self._last_fast >= self.interval_fast:
                specs = http_fast if http_available() else serial_fast
                for spec in specs:
                    # Promote critical keys to MEDIUM priority so they run even during paused low-tier
                    key = spec.params.get("key") if isinstance(spec, HttpQuerySpec) else None
                    critical = {
                        "move.axes[].userPosition",
                        "state.status",
                        "state.currentTool",
                        "sensors.endstops[].triggered",
                    }
                    prio = Priority.MEDIUM if key in critical else Priority.LOW
                    co_key = key if key else "fast"
                    self._submit_query(spec, prio, coalesce_key=f"fast:{co_key}")
                self._last_fast = now
            # Medium tier (2.5s)
            if now - self._last_medium >= self.interval_medium:
                specs = http_medium if http_available() else serial_medium
                for spec in specs:
                    key = spec.params.get("key") if isinstance(spec, HttpQuerySpec) else "medium"
                    self._submit_query(spec, Priority.MEDIUM, coalesce_key=f"medium:{key}")
                self._last_medium = now
            # Full refresh (5s)
            if now - self._last_full >= self.interval_full:
                specs = http_full if http_available() else serial_full
                for spec in specs:
                    key = spec.params.get("key") if isinstance(spec, HttpQuerySpec) else "full"
                    # Ensure these run even if low/background paused
                    self._submit_query(spec, Priority.MEDIUM, coalesce_key=f"full:{key}")
                self._last_full = now
            time.sleep(0.01) 