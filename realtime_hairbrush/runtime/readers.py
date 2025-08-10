import threading
import time
from typing import Optional, Callable

from semantic_gcode.dict.gcode_commands.M408.M408 import M408_ReportObjectModel
from .state import MachineState
from ..transport.airbrush_transport import AirbrushTransport
from .events import StateUpdatedEvent, SentEvent, ReceivedEvent
from .object_model import parse_object_model


class StatusPoller:
    def __init__(self, transport: AirbrushTransport, state: MachineState, emit: Optional[Callable] = None, interval: float = 1.0) -> None:
        self.transport = transport
        self.state = state
        self.emit = emit or (lambda e: None)
        self.interval = interval
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._last_diag_ts: float = 0.0
        self._last_endstop_ts: float = 0.0
        # Diagnostics toggles (off by default to reduce log spam)
        self.enable_diagnostics: bool = False
        self.enable_endstops: bool = False
        self.diag_period_s: float = 30.0
        self.endstop_period_s: float = 30.0

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

    def set_diagnostics(self, enabled: bool, period_s: Optional[float] = None) -> None:
        self.enable_diagnostics = bool(enabled)
        if period_s is not None and period_s > 0:
            self.diag_period_s = float(period_s)

    def set_endstops(self, enabled: bool, period_s: Optional[float] = None) -> None:
        self.enable_endstops = bool(enabled)
        if period_s is not None and period_s > 0:
            self.endstop_period_s = float(period_s)

    def _run(self) -> None:
        while not self._stop.is_set():
            now = time.time()
            if self.transport.is_connected():
                # Use M408 S2 each tick for full object model
                try:
                    line = "M408 S2"
                    self.emit(SentEvent(line=line))
                    resp = self.transport.query(line)
                    if resp:
                        self.emit(ReceivedEvent(line=resp))
                        try:
                            import json
                            text = resp.strip()
                            if "{" in text and "}" in text:
                                text = text[text.find("{") : text.rfind("}") + 1]
                            data = json.loads(text)
                        except Exception:
                            data = {}
                        # Merge firmware status, raw JSON, and parsed object model
                        status = data.get("status")
                        observed = {}
                        if status is not None:
                            observed["firmware"] = {"status": status}
                        if isinstance(data, dict) and data:
                            observed["raw_status"] = {"raw": data}
                            # Diagnostics mapping if present in object model (M408 S2)
                            temps = data.get("temps", {})
                            extra = temps.get("extra") if isinstance(temps, dict) else None
                            params = data.get("params", {})
                            diag = {}
                            # VIN
                            atx = params.get("atxPower") if isinstance(params, dict) else None
                            if isinstance(atx, (int, float)) and atx >= 0:
                                diag["vin"] = float(atx)
                            # MCU/driver temps if exposed in extra
                            if isinstance(extra, list) and extra:
                                for item in extra:
                                    if isinstance(item, list) and len(item) >= 2 and isinstance(item[1], (int, float)):
                                        label = str(item[0]).lower()
                                        if "mcu" in label or "cpu" in label:
                                            diag["mcu_temp_c"] = float(item[1])
                                        if "driver" in label or "stepper" in label:
                                            diag["driver_temp_c"] = float(item[1])
                            if diag:
                                snap = self.state.snapshot().get("observed", {})
                                merged = dict(snap)
                                merged.setdefault("diagnostics", {}).update(diag)
                                self.state.update_observed(merged)
                        model = parse_object_model(data) if isinstance(data, dict) else {}
                        if model:
                            observed["object_model"] = model
                        if observed:
                            self.state.update_observed(observed)
                            self.emit(StateUpdatedEvent(state=self.state.snapshot()))
                except Exception:
                    pass
                # Diagnostics (M122) gated and throttled
                if self.enable_diagnostics and (now - self._last_diag_ts > self.diag_period_s):
                    try:
                        try:
                            from semantic_gcode.dict.gcode_commands.M122.M122 import M122_Diagnostics
                            m122 = M122_Diagnostics.create()
                            line = str(m122)
                        except Exception:
                            line = "M122"
                        self.emit(SentEvent(line=line))
                        resp = self.transport.query(line)
                        if resp:
                            self.emit(ReceivedEvent(line=resp))
                            try:
                                diag = m122.parse_diagnostics(resp) if 'm122' in locals() else {}
                            except Exception:
                                diag = {}
                            if diag:
                                snap = self.state.snapshot().get("observed", {})
                                merged = dict(snap)
                                merged.setdefault("diagnostics", {}).update(diag)
                                self.state.update_observed(merged)
                                self.emit(StateUpdatedEvent(state=self.state.snapshot()))
                    except Exception:
                        pass
                    self._last_diag_ts = now
                # Endstops (M119) gated and throttled
                if self.enable_endstops and (now - self._last_endstop_ts > self.endstop_period_s):
                    try:
                        try:
                            from semantic_gcode.dict.gcode_commands.M119.M119 import M119_EndstopStatus
                            m119 = M119_EndstopStatus.create()
                            line = str(m119)
                        except Exception:
                            line = "M119"
                        self.emit(SentEvent(line=line))
                        resp = self.transport.query(line)
                        if resp:
                            self.emit(ReceivedEvent(line=resp))
                            try:
                                ends = m119.parse_endstops(resp) if 'm119' in locals() else {}
                            except Exception:
                                ends = {}
                            if ends:
                                snap = self.state.snapshot().get("observed", {})
                                merged = dict(snap)
                                merged.setdefault("endstops", {}).update(ends)
                                self.state.update_observed(merged)
                                self.emit(StateUpdatedEvent(state=self.state.snapshot()))
                    except Exception:
                        pass
                    self._last_endstop_ts = now
            time.sleep(self.interval)

    def _parse_m122(self, text: str) -> dict:
        # Heuristic parse for VIN, MCU/Driver temps and warnings
        vin = None; mcu_temp = None; driver_temp = None; overtemp = False
        for line in text.splitlines():
            ln = line.strip()
            if "VIN:" in ln:
                try:
                    vin = float(ln.split("VIN:")[-1].split()[0])
                except Exception:
                    pass
            if "MCU temperature" in ln or "MCU temp" in ln:
                try:
                    # e.g., MCU temperature: 49.6 C
                    mcu_temp = float(ln.split(":")[-1].split()[0])
                except Exception:
                    pass
            if "driver" in ln and ("temp" in ln or "overtemp" in ln.lower()):
                if "warning" in ln.lower() or "overtemp" in ln.lower():
                    overtemp = True
                try:
                    # e.g., driver temp: 85.0 C
                    driver_temp = float(ln.split(":")[-1].split()[0])
                except Exception:
                    pass
        out = {}
        if vin is not None:
            out["vin"] = vin
        if mcu_temp is not None:
            out["mcu_temp_c"] = mcu_temp
        if driver_temp is not None:
            out["driver_temp_c"] = driver_temp
        if overtemp:
            out["overtemp_warning"] = True
        return out

    def _parse_m119(self, text: str) -> dict:
        # Heuristic parse: lines like "Endstops - X: not stopped, Y: stopped, Z: not stopped"
        out = {}
        for ln in text.splitlines():
            lower = ln.lower()
            if "x:" in lower or "y:" in lower or "z:" in lower or "u:" in lower or "v:" in lower:
                for axis in ("x","y","z","u","v"):
                    if f"{axis}:" in lower:
                        try:
                            val = lower.split(f"{axis}:")[-1].split(',')[0].strip()
                            out[axis.upper()] = 1 if "stopped" in val else 0
                        except Exception:
                            pass
        return out 