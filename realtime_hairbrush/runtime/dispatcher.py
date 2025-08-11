import threading
import time
import uuid
from typing import Callable, List, Optional

from semantic_gcode.gcode.base import GCodeInstruction
from semantic_gcode.gcode.mixins import BlocksExecution, ExpectsAcknowledgement

from .events import SentEvent, ReceivedEvent, AckEvent, ErrorEvent
from .queue import InstructionQueue
from ..transport.airbrush_transport import AirbrushTransport
from .state import MachineState


class Dispatcher:
    def __init__(self, transport: AirbrushTransport, state: MachineState) -> None:
        self.transport = transport
        self.state = state
        self.queue = InstructionQueue()
        self._listeners: List[Callable] = []
        self._stop = threading.Event()
        self._worker: Optional[threading.Thread] = None

    def on_event(self, callback: Callable) -> None:
        self._listeners.append(callback)

    def _emit(self, event) -> None:
        for cb in list(self._listeners):
            try:
                cb(event)
            except Exception:
                pass

    def enqueue(self, instruction: GCodeInstruction) -> None:
        self.queue.put(instruction)

    def start(self) -> None:
        if self._worker and self._worker.is_alive():
            return
        self._stop.clear()
        self._worker = threading.Thread(target=self._run_loop, daemon=True)
        self._worker.start()

    def stop(self) -> None:
        self._stop.set()
        if self._worker:
            self._worker.join(timeout=1.0)

    def _run_loop(self) -> None:
        while not self._stop.is_set():
            try:
                instr = self.queue.get(timeout=0.1)
            except Exception:
                continue

            try:
                self.state.apply_predictive(instr)
            except Exception as e:
                self._emit(ErrorEvent(message=f"apply failed: {e}", context={"instruction": str(instr)}))

            line = str(instr)
            self._emit(SentEvent(line=line))

            if not self.transport.is_connected():
                self._emit(ErrorEvent(message="Not connected"))
                continue

            needs_ack = isinstance(instr, ExpectsAcknowledgement) or isinstance(instr, BlocksExecution)
            if needs_ack:
                # Special-case long running M400/G28 with M408 probes
                try:
                    dyn_timeout = float(getattr(self.transport.config, "timeout", 10.0))
                except Exception:
                    dyn_timeout = 10.0
                deadline = time.time() + max(2.0, min(30.0, dyn_timeout))
                upper = line.strip().upper()
                is_http = (getattr(self.transport.config, "transport_type", "").lower() == "http")

                if upper.startswith("M400") or upper.startswith("G28"):
                    # Send the command
                    first = self.transport.query(line)
                    if first:
                        self._emit(ReceivedEvent(line=first))
                    poll_s = 0.5 if is_http else 0.25
                    got_ack = False
                    while time.time() < deadline:
                        try:
                            status_txt = self.transport.query("M408 S0") or self.transport.query("M408 S2")
                        except Exception:
                            status_txt = None
                        if status_txt:
                            self._emit(ReceivedEvent(line=status_txt))
                            txt = status_txt.strip()
                            is_idle = ('"status":"I"' in txt) or ('\"status\":\"I\"' in txt) or ('\"status\":\"idle\"' in txt)
                            if is_idle:
                                self._emit(AckEvent(instruction=line, ok=True, message="Idle"))
                                got_ack = True
                                break
                        time.sleep(poll_s)
                    if not got_ack:
                        self._emit(AckEvent(instruction=line, ok=False, message="Ack timeout"))
                    time.sleep(0.05)
                    continue

                # Token-based ack for all other gated commands
                tag = f"AB#{uuid.uuid4().hex[:8]}"
                try:
                    # Send main command
                    first = self.transport.query(line)
                    if first:
                        self._emit(ReceivedEvent(line=first))
                    # Immediately send token via M118
                    tok_line = f'M118 S"{tag}"'
                    self._emit(SentEvent(line=tok_line))
                    _ = self.transport.query(tok_line)
                except Exception:
                    try:
                        last_err = self.transport.get_last_error()
                    except Exception:
                        last_err = None
                    ctx = {"instruction": line, "tag": tag}
                    if last_err:
                        ctx["last_error"] = last_err
                    self._emit(ErrorEvent(message="Send failed", context=ctx))
                    time.sleep(0.05)
                    continue

                got_ack = False
                base_interval = 0.2 if is_http else 0.05
                interval = base_interval
                while time.time() < deadline:
                    time.sleep(interval)
                    # Read without sending a command when possible (HTTP)
                    resp = None
                    try:
                        if is_http:
                            # type: ignore[attr-defined]
                            resp = getattr(self.transport.transport, "read_reply", None)() if hasattr(self.transport, "transport") else None
                            if resp is None:
                                # Fallback: try rr_reply via underlying http instance
                                from semantic_gcode.transport.http import HttpTransport
                                inner = getattr(self.transport, "transport", None)
                                if isinstance(inner, HttpTransport):
                                    resp = inner.read_reply()
                        if resp is None:
                            resp = self.transport.query("M408 S0")  # light probe to flush message queue
                    except Exception:
                        resp = None
                    if resp:
                        self._emit(ReceivedEvent(line=resp))
                        if tag in resp:
                            self._emit(AckEvent(instruction=line, ok=True, message=tag))
                            got_ack = True
                            break
                        interval = base_interval
                    else:
                        interval = min(0.5, interval * 1.5)

                if not got_ack:
                    self._emit(AckEvent(instruction=line, ok=False, message="Ack timeout"))
            else:
                ok = self.transport.send_line(line)
                if not ok:
                    try:
                        last_err = self.transport.get_last_error()
                    except Exception:
                        last_err = None
                    ctx = {"instruction": line}
                    if last_err:
                        ctx["last_error"] = last_err
                    self._emit(ErrorEvent(message="Send failed", context=ctx))
                    time.sleep(0.05)
                    continue
                resp = self.transport.query("")
                if resp:
                    self._emit(ReceivedEvent(line=resp))

            time.sleep(0.05) 