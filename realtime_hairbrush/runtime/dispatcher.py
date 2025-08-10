import threading
import time
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

            # Predictive apply before send
            try:
                self.state.apply_predictive(instr)
            except Exception as e:
                self._emit(ErrorEvent(message=f"apply failed: {e}", context={"instruction": str(instr)}))

            line = str(instr)
            self._emit(SentEvent(line=line))

            # Ensure connection
            if not self.transport.is_connected():
                self._emit(ErrorEvent(message="Not connected"))
                continue

            # If the instruction expects acknowledgement, send via query to obtain initial response
            needs_ack = isinstance(instr, ExpectsAcknowledgement) or isinstance(instr, BlocksExecution)
            if needs_ack:
                response_accum = ""
                try:
                    first_resp = self.transport.query(line)
                    if first_resp:
                        self._emit(ReceivedEvent(line=first_resp))
                        response_accum += first_resp
                except Exception:
                    # Surface last error and continue
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

                deadline = time.time() + 30.0
                while time.time() < deadline:
                    resp = self.transport.query("")
                    if resp:
                        self._emit(ReceivedEvent(line=resp))
                        response_accum += resp
                        if isinstance(instr, ExpectsAcknowledgement):
                            try:
                                if instr.validate_response(response_accum):
                                    # Include the last non-empty line as message
                                    last_line = "".join([r for r in response_accum.splitlines() if r]).strip()
                                    self._emit(AckEvent(instruction=line, ok=True, message=last_line or None))
                                    break
                            except Exception:
                                pass
                    time.sleep(0.05)
                else:
                    self._emit(AckEvent(instruction=line, ok=False, message="Ack timeout"))

            # Non-ack commands: optionally read any immediate response
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

            # Small pacing between commands to avoid overruns on some serial stacks
            time.sleep(0.05) 