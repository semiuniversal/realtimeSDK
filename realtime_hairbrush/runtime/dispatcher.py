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

# New imports for sequencer integration
from .sequencer import RequestSequencer
from .sequencer import Request, Result, Priority, RequestKind


class Dispatcher:
    def __init__(self, transport: AirbrushTransport, state: MachineState) -> None:
        self.transport = transport
        self.state = state
        self.queue = InstructionQueue()
        self._listeners: List[Callable] = []
        self._stop = threading.Event()
        self._worker: Optional[threading.Thread] = None
        # Single-threaded request sequencer; it is the sole I/O owner
        self.sequencer = RequestSequencer(transport=self.transport, on_event=self._emit)

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
        self.sequencer.start()
        self._worker = threading.Thread(target=self._run_loop, daemon=True)
        self._worker.start()

    def stop(self) -> None:
        self._stop.set()
        try:
            self.sequencer.stop()
        except Exception:
            pass
        if self._worker:
            self._worker.join(timeout=1.0)

    def _to_request(self, instr: GCodeInstruction) -> Request:
        line = str(instr)
        # Infer behavior
        needs_ack = isinstance(instr, ExpectsAcknowledgement) or isinstance(instr, BlocksExecution)
        side_effects = set()
        upper = line.strip().upper()
        if upper.startswith("G28") or upper.startswith("T") or upper.startswith("M98"):
            side_effects.add("LongRunning")
        # Priority: ensure motion and tool-select are not reordered behind M400
        if upper.startswith("G0") or upper.startswith("G1") or upper.startswith("T"):
            priority = Priority.HIGH
        else:
            priority = Priority.HIGH if needs_ack else Priority.MEDIUM
        # Timeout heuristics
        timeout_s = 30.0 if ("LongRunning" in side_effects) else max(5.0, float(getattr(self.transport.config, "timeout", 10.0)))

        def on_complete(res: Result) -> None:
            if needs_ack:
                self._emit(AckEvent(instruction=line, ok=res.ok, message=None if res.ok else res.error))

        return Request(
            kind=RequestKind.COMMAND,
            priority=priority,
            payload=line,
            timeout_s=timeout_s,
            expects_ack=needs_ack,
            side_effects=side_effects,
            on_complete=on_complete,
        )

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

            # Create a Request and submit to the sequencer
            req = self._to_request(instr)
            self.sequencer.submit(req)
            time.sleep(0.01) 