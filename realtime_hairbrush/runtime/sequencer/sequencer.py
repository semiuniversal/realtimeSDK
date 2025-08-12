from __future__ import annotations

import queue
import threading
import time
from typing import Callable, Dict, Optional
import uuid

from .request import Request, Result, Priority, RequestKind
from .transport_strategy import HttpQuerySpec, SerialQuerySpec
from ..events import SentEvent, ReceivedEvent, AckEvent, UpdatesPausedEvent, UpdatesResumedEvent
try:
    from ..transport.logging_wrapper import log_note as _log_note
except Exception:
    def _log_note(*args, **kwargs):
        pass


class RequestSequencer:
    def __init__(self, transport, on_event: Optional[Callable[[object], None]] = None) -> None:
        self.transport = transport
        self.on_event = on_event or (lambda e: None)
        self._queues: Dict[Priority, "queue.Queue[Request]"] = {
            Priority.HIGH: queue.Queue(),
            Priority.MEDIUM: queue.Queue(),
            Priority.LOW: queue.Queue(),
            Priority.BACKGROUND: queue.Queue(),
        }
        self._coalesce: Dict[str, Request] = {}
        self._stop = threading.Event()
        self._worker: Optional[threading.Thread] = None
        self._paused_updates: bool = False
        self._pause_depth: int = 0

    def start(self) -> None:
        if self._worker and self._worker.is_alive():
            return
        self._stop.clear()
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._worker.start()

    def stop(self) -> None:
        self._stop.set()
        if self._worker:
            self._worker.join(timeout=1.0)

    def submit(self, req: Request) -> None:
        if req.priority in (Priority.LOW, Priority.BACKGROUND) and req.coalesce_key:
            self._coalesce[req.coalesce_key] = req
            return
        self._queues[req.priority].put(req)

    def pause_updates(self, reason: str = "") -> None:
        self._pause_depth += 1
        if not self._paused_updates:
            self._paused_updates = True
            self._emit(UpdatesPausedEvent(reason=reason))

    def resume_updates(self) -> None:
        if self._pause_depth > 0:
            self._pause_depth -= 1
        if self._pause_depth == 0 and self._paused_updates:
            self._paused_updates = False
            self._emit(UpdatesResumedEvent())

    def _emit(self, e: object) -> None:
        try:
            self.on_event(e)
        except Exception:
            pass

    def _next(self) -> Optional[Request]:
        for prio in (Priority.HIGH, Priority.MEDIUM, Priority.LOW, Priority.BACKGROUND):
            if prio in (Priority.LOW, Priority.BACKGROUND) and self._paused_updates:
                continue
            # drain coalesced first for low/background
            if prio in (Priority.LOW, Priority.BACKGROUND) and self._coalesce:
                _, req = self._coalesce.popitem()
                return req
            q = self._queues[prio]
            try:
                return q.get_nowait()
            except queue.Empty:
                continue
        return None

    def _execute(self, req: Request) -> Result:
        # Determine transport capabilities
        inner = getattr(self.transport, 'transport', self.transport)
        inner2 = getattr(inner, 'transport', inner)
        is_http = callable(getattr(inner2, 'get_model', None))
        is_serial = not is_http
        # Pause background polling for long running commands, and for ANY serial command to avoid interleaving
        if req.kind == RequestKind.COMMAND and (("LongRunning" in (req.side_effects or set())) or is_serial):
            self.pause_updates("Command")
        start = time.time()
        try:
            data = None
            # Emit send arrow for string payload
            if isinstance(req.payload, str):
                self._emit(SentEvent(line=req.payload))
            if req.kind == RequestKind.COMMAND:
                if req.expects_ack and is_serial:
                    # Tagged ack using M118 to disambiguate 'ok'
                    tag = f"AB#{uuid.uuid4().hex[:8]}"
                    deadline = start + max(2.0, min(45.0, req.timeout_s or 10.0))
                    try:
                        # Send main command (logged by transport)
                        _log_note(f"SEND {req.payload}")
                        _ = self.transport.query(req.payload)
                        # Send tag marker
                        tok_line = f'M118 S"{tag}"'
                        _log_note(f"TAG EMIT {tag}")
                        _ = self.transport.query(tok_line)
                    except Exception as e:
                        return Result(ok=False, error=str(e), started_at_s=start, finished_at_s=time.time())
                    # Poll using a light probe until we see the tag
                    interval = 0.08
                    saw_tag = False
                    last_err = None
                    while time.time() < deadline:
                        try:
                            resp = self.transport.query("M408 S0")
                            if isinstance(resp, str) and resp:
                                if tag in resp:
                                    _log_note(f"TAG SEEN {tag}")
                                    saw_tag = True
                                    break
                        except Exception as e:
                            last_err = str(e)
                        time.sleep(interval)
                        interval = min(0.5, interval * 1.5)
                    if not saw_tag:
                        return Result(ok=False, error=last_err or "Ack timeout", started_at_s=start, finished_at_s=time.time())
                    return Result(ok=True, data=None, error=None, started_at_s=start, finished_at_s=time.time())
                elif req.expects_ack:
                    # HTTP or non-serial path: rely on transport query response
                    data = self.transport.query(req.payload)
                else:
                    ok = self.transport.send_line(req.payload)
                    if not ok:
                        return Result(ok=False, error=getattr(self.transport, "_last_error", "send failed"))
                    data = self.transport.query("")
            elif req.kind == RequestKind.QUERY:
                if isinstance(req.payload, HttpQuerySpec):
                    # Prefer HTTP rr_model when available; otherwise fall back to serial M409
                    inner = getattr(self.transport, 'transport', self.transport)
                    inner2 = getattr(inner, 'transport', inner)
                    getter = getattr(inner2, 'get_model', None)
                    used_http = False
                    if callable(getter):
                        try:
                            data = getter(key=req.payload.params.get('key'), flags=req.payload.params.get('flags'))
                            used_http = data is not None
                        except Exception:
                            used_http = False
                    if not used_http:
                        # Fallback to G-code M409 (logged by LoggingTransport Q/R)
                        key = req.payload.params.get('key')
                        flags = req.payload.params.get('flags')
                        cmd = f"M409 K\"{key}\"" if key else "M409"
                        if flags:
                            cmd += f" F\"{flags}\""
                        data = self.transport.query(cmd)
                elif isinstance(req.payload, SerialQuerySpec):
                    # Serial query commands are logged by LoggingTransport Q/R
                    data = self.transport.query(req.payload.command)
                else:
                    data = self.transport.query(req.payload)
            elif req.kind in (RequestKind.UPLOAD, RequestKind.CONTROL):
                data = None
            if isinstance(data, str) and data:
                self._emit(ReceivedEvent(line=data))
            parsed = req.parse_response(data) if req.parse_response else data
            return Result(ok=True, data=parsed, error=None, started_at_s=start, finished_at_s=time.time())
        except Exception as ex:
            return Result(ok=False, error=str(ex), started_at_s=start, finished_at_s=time.time())
        finally:
            if req.kind == RequestKind.COMMAND and (("LongRunning" in (req.side_effects or set())) or is_serial):
                self.resume_updates()

    def _run(self) -> None:
        while not self._stop.is_set():
            req = self._next()
            if not req:
                time.sleep(0.01)
                continue
            res = self._execute(req)
            if req.kind == RequestKind.COMMAND and req.expects_ack:
                self._emit(AckEvent(instruction=str(req.payload), ok=res.ok, message=None if res.ok else res.error))
            if req.on_complete:
                try:
                    req.on_complete(res)
                except Exception:
                    pass
            time.sleep(0.01) 