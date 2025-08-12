from __future__ import annotations

import os
import threading
import time
from typing import Optional, Dict, Any

from semantic_gcode.transport.base import Transport


_log_init_lock = threading.Lock()
_log_initialized = False


STATUS_LOG_ENABLED = os.getenv("AIRBRUSH_STATUS_LOG", "0") in ("1", "true", "True")
FULL_GCODE_TRACE = os.getenv("AIRBRUSH_GCODE_TRACE", "0") in ("1", "true", "True")


def _repo_root_log_path() -> str:
    # Compute repo root as two levels up from this file: realtimeSDK/
    here = os.path.dirname(__file__)
    repo_root = os.path.abspath(os.path.join(here, "..", ".."))
    log_dir = os.path.join(repo_root, "log")
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception:
        pass
    return os.path.join(log_dir, "airbrush.log")


def _get_log_path() -> str:
    path = os.getenv("AIRBRUSH_LOG_PATH")
    if path:
        # Ensure parent directory exists
        try:
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        except Exception:
            pass
        return path
    # Default to <repo_root>/log/airbrush.log
    return _repo_root_log_path()


def _write_header(fh) -> None:
    fh.write(f"# Airbrush session log started at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")


def reset_session_log() -> None:
    """Truncate the session log immediately (e.g., at app launch)."""
    global _log_initialized
    with _log_init_lock:
        try:
            log_path = _get_log_path()
            with open(log_path, "w", encoding="utf-8") as f:
                _write_header(f)
            _log_initialized = True
        except Exception:
            # Do not crash if path unwritable
            pass


def _ensure_log_fresh() -> str:
    global _log_initialized
    with _log_init_lock:
        log_path = _get_log_path()
        if not _log_initialized:
            try:
                with open(log_path, "w", encoding="utf-8") as f:
                    _write_header(f)
            except Exception:
                pass
            _log_initialized = True
        return log_path


_log_write_lock = threading.Lock()

def log_note(text: str) -> None:
    """Append a diagnostic NOTE line to the session log."""
    try:
        path = _ensure_log_fresh()
        ts = time.strftime('%Y-%m-%d %H:%M:%S')
        line = f"[{ts}.{int((time.time()%1)*1000):03d}] NOTE {text}\n"
        with _log_write_lock:
            with open(path, "a", encoding="utf-8") as f:
                f.write(line)
    except Exception:
        pass


def _is_status_query(cmd: Optional[str]) -> bool:
    if not cmd:
        return True
    t = str(cmd).strip().lower()
    if not t:
        return True
    return (
        t.startswith("m409") or t.startswith("m408") or t.startswith("m114") or t.startswith("m105") or t.startswith("rr_reply") or t.startswith("rr_model")
    )


def _is_mutation(cmd: Optional[str]) -> bool:
    if not cmd:
        return False
    t = str(cmd).strip().upper()
    if not t:
        return False
    # Movement and machine state changing commands
    return (
        t.startswith("G0") or t.startswith("G1") or t.startswith("G2") or t.startswith("G3") or
        t.startswith("G28") or t.startswith("G92") or t.startswith("M400") or t.startswith("M98") or
        t.startswith("M106") or t.startswith("M107") or t.startswith("M104") or t.startswith("M109") or
        t.startswith("M140") or t.startswith("M190") or t.startswith("T ") or t == "T" or t.startswith("M999") or
        t.startswith("M552")
    )


class LoggingTransport(Transport):
    """
    Decorator for Transport that logs all TX/R to a file.
    The log file is truncated once per process session on first use.
    """

    def __init__(self, inner: Transport) -> None:
        self.inner = inner
        self._log_path = _ensure_log_fresh()
        self._lock = threading.Lock()

    # Utilities
    def _log(self, direction: str, text: str) -> None:
        try:
            ts = time.strftime('%Y-%m-%d %H:%M:%S')
            line = f"[{ts}.{int((time.time()%1)*1000):03d}] {direction} {text}\n"
            with self._lock:
                with open(self._log_path, "a", encoding="utf-8") as f:
                    f.write(line)
        except Exception:
            pass

    # Transport interface
    def connect(self) -> bool:
        self._log("CONNECT", f"type={type(self.inner).__name__}")
        ok = False
        try:
            ok = self.inner.connect()
            self._log("CONNECT", f"ok={ok}")
            return ok
        except Exception as e:
            self._log("CONNECT-ERR", str(e))
            raise

    def disconnect(self) -> None:
        self._log("DISCONNECT", "")
        try:
            self.inner.disconnect()
        except Exception as e:
            self._log("DISCONNECT-ERR", str(e))
            raise

    def is_connected(self) -> bool:
        try:
            ok = self.inner.is_connected()
            return ok
        except Exception as e:
            self._log("IS_CONNECTED-ERR", str(e))
            raise

    def send_line(self, line: str) -> bool:
        # Log only mutating commands unless FULL_GCODE_TRACE
        if FULL_GCODE_TRACE or _is_mutation(line):
            tag = "ACTUAL-TX" if FULL_GCODE_TRACE else "TX"
            self._log(tag, line.replace("\n", "\\n"))
        try:
            ok = self.inner.send_line(line)
            if FULL_GCODE_TRACE or _is_mutation(line):
                tag = "TX-OK"
                self._log(tag, str(ok))
            return ok
        except Exception as e:
            if FULL_GCODE_TRACE or _is_mutation(line):
                self._log("TX-ERR", str(e))
            raise

    def query(self, query_cmd: str) -> Optional[str]:
        # Status queries suppressed unless explicitly enabled (never trace rr_model here)
        if _is_status_query(query_cmd) and not _is_mutation(query_cmd) and not STATUS_LOG_ENABLED:
            return self.inner.query(query_cmd)
        # Log G-code Q when FULL_GCODE_TRACE or if mutation; suppress rr_model
        if not _is_status_query(query_cmd) and (FULL_GCODE_TRACE or _is_mutation(query_cmd) or STATUS_LOG_ENABLED):
            self._log("Q", (query_cmd if query_cmd else "<empty>").replace("\n", "\\n"))
        try:
            resp = self.inner.query(query_cmd)
            # Log replies for G-code only (exclude rr_model/rr_reply unless STATUS_LOG_ENABLED)
            should_log_rx = not _is_status_query(query_cmd)
            if should_log_rx and (FULL_GCODE_TRACE or _is_mutation(query_cmd) or STATUS_LOG_ENABLED):
                txt = (resp or "").replace("\n", " ").strip()
                tag = "ACTUAL-RX" if FULL_GCODE_TRACE else "R"
                self._log(tag, txt if txt else "<none>")
            return resp
        except Exception as e:
            if not _is_status_query(query_cmd) and (FULL_GCODE_TRACE or _is_mutation(query_cmd) or STATUS_LOG_ENABLED):
                self._log("Q-ERR", str(e))
            raise

    def get_status(self) -> Dict[str, Any]:
        try:
            st = self.inner.get_status()
            self._log("STATUS", str(st))
            return st
        except Exception as e:
            self._log("STATUS-ERR", str(e))
            raise

    # HTTP rr_model/rr_reply forwarding for HttpTransport (status suppressed by default)
    def get_model(self, key: Optional[str] = None, flags: Optional[str] = None):
        if STATUS_LOG_ENABLED:
            self._log("RR_MODEL", f"key={key} flags={flags}")
        getter = getattr(self.inner, "get_model", None)
        if callable(getter):
            data = getter(key=key, flags=flags)
            if STATUS_LOG_ENABLED:
                self._log("RR_MODEL_R", str(data)[:300])
            return data
        return None

    def read_reply(self) -> Optional[str]:
        reader = getattr(self.inner, "read_reply", None)
        if callable(reader):
            data = reader()
            if STATUS_LOG_ENABLED:
                self._log("RR_REPLY", str(data)[:300])
            return data
        return None 