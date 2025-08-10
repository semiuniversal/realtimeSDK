from __future__ import annotations

import os
from typing import Any, Dict, Optional
import yaml

# Store settings in project tree under realtime_hairbrush/
SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "..", "settings.yaml")
SETTINGS_PATH = os.path.abspath(SETTINGS_PATH)


def load_settings() -> Dict[str, Any]:
    try:
        if not os.path.exists(SETTINGS_PATH):
            return {}
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {}


def save_settings(data: Dict[str, Any]) -> None:
    try:
        os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, sort_keys=True)
    except Exception:
        # Silent failure; caller can ignore
        pass


def clear_settings() -> None:
    try:
        if os.path.exists(SETTINGS_PATH):
            os.remove(SETTINGS_PATH)
    except Exception:
        pass


def update_last_connection(
    transport: str,
    serial_port: Optional[str] = None,
    baud: Optional[int] = None,
    ip: Optional[str] = None,
    fingerprint: Optional[Dict[str, str]] = None,
) -> None:
    data = load_settings()
    data.setdefault("last", {})
    last = data["last"]
    last["transport"] = transport
    if serial_port is not None:
        last["serial_port"] = serial_port
    if baud is not None:
        last["baud"] = int(baud)
    if ip is not None:
        last["ip"] = ip
    if fingerprint:
        last["fingerprint"] = fingerprint
    save_settings(data) 