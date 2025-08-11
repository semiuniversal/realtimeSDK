from __future__ import annotations

import os
import threading
import time
from typing import Optional, Dict, Any

from semantic_gcode.transport.base import Transport


_log_init_lock = threading.Lock()
_log_initialized = False


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


class LoggingTransport(Transport):
    """
    Decorator for Transport that logs all TX/RX to a file.
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
        self._log("TX", line.replace("\n", "\\n"))
        try:
            ok = self.inner.send_line(line)
            self._log("TX-OK", str(ok))
            return ok
        except Exception as e:
            self._log("TX-ERR", str(e))
            raise

    def query(self, query_cmd: str) -> Optional[str]:
        # Short-circuit empty queries to avoid logging churn
        if not query_cmd or not str(query_cmd).strip():
            return None
        self._log("Q", (query_cmd if query_cmd else "<empty>").replace("\n", "\\n"))
        try:
            resp = self.inner.query(query_cmd)
            txt = (resp or "").replace("\n", " ").strip()
            self._log("R", txt if txt else "<none>")
            return resp
        except Exception as e:
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