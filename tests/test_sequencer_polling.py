import time
import threading

from realtime_hairbrush.runtime import MachineState
from realtime_hairbrush.runtime.sequencer import RequestSequencer
from realtime_hairbrush.runtime.readers import StatusPoller


class FakeTransport:
    def __init__(self):
        self._connected = True

    def is_connected(self):
        return True

    def send_line(self, line: str) -> bool:
        return True

    def query(self, cmd: str) -> str:
        # Minimal M409 fallback if ever used
        return '{"result": null}'

    # rr_model HTTP emulation
    def get_model(self, key=None, flags=None):
        # Return minimal object model pieces per key, wrapped as rr_model JSON
        mapping = {
            "move.axes[].machinePosition": {"result": [10.0, 20.0, 5.0]},
            "state.status": {"result": "I"},
            "move.axes[].homed": {"result": [1, 1, 1, 1, 1]},
            "state.currentTool": {"result": 0},
            "sensors.endstops[].triggered": {"result": [0, 0, 0, 0, 0]},
            "boards[].vIn.current": {"result": 24.1},
            "boards[].mcuTemp.current": {"result": 42.5},
        }
        return mapping.get(key, {"result": None})


def test_status_poller_populates_observed():
    fake = FakeTransport()
    state = MachineState()
    seq = RequestSequencer(transport=fake)
    seq.start()
    try:
        poller = StatusPoller(seq, state, emit=None, interval_fast=0.05, interval_medium=0.05, interval_slow=10.0)
        poller.start()
        # Allow a few cycles to run
        time.sleep(0.5)
        poller.stop()
        # Allow sequencer to deliver any pending callbacks
        time.sleep(0.1)
        snap = state.snapshot()
        observed = snap.get("observed", {})
        # Firmware status
        assert observed.get("firmware", {}).get("status") == "I"
        # Positions
        machine = (((observed.get("raw_status", {}) or {}).get("raw", {}) or {}).get("coords", {}) or {}).get("machine")
        assert isinstance(machine, list) and len(machine) >= 3
        # Homed list
        homed = (((observed.get("raw_status", {}) or {}).get("raw", {}) or {}).get("coords", {}) or {}).get("axesHomed")
        assert isinstance(homed, list) and len(homed) >= 3 and int(homed[0]) == 1
        # Tool
        tool = (((observed.get("raw_status", {}) or {}).get("raw", {}) or {}).get("currentTool"))
        assert tool == 0
        # Endstops
        ends = observed.get("endstops", {})
        assert isinstance(ends, dict) and "X" in ends
        # Diagnostics
        diag = observed.get("diagnostics", {})
        assert "vin" in diag and "mcu_temp_c" in diag
    finally:
        try:
            poller.stop()
        except Exception:
            pass
        seq.stop() 