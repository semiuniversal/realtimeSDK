from __future__ import annotations

import asyncio
import time
from typing import Any, Awaitable, Callable, Dict, Optional

from realtime_hairbrush.transport.airbrush_transport import AirbrushTransport
from realtime_hairbrush.runtime.events import StateUpdatedEvent


class ObjectModelAgent:
    """
    Minimal async agent to centralize object model updates with coalescing.
    - Uses M409 for live coords at a short interval during motion
    - Uses on-demand M408 for snapshots
    - Emits minimal patches via callback
    - Wraps sync transport calls using asyncio.to_thread initially
    """

    def __init__(self) -> None:
        self._transport: Optional[AirbrushTransport] = None
        self._task_loop: Optional[asyncio.Task] = None
        self._running = asyncio.Event()
        self._callbacks: list[Callable[[Dict[str, Any]], None]] = []
        self._motion_active = asyncio.Event()
        self._cooldown_coords_s: float = 0.25
        self._last_emit: Optional[tuple[float, tuple[float, float, float]]] = None
        self._verbose = False
        self._lock = asyncio.Lock()

        # coalescing tokens
        self._want_coords = asyncio.Event()
        self._want_snapshot = asyncio.Event()

    def set_verbose(self, on: bool) -> None:
        self._verbose = on

    def set_transport(self, transport: AirbrushTransport) -> None:
        self._transport = transport

    def on_change(self, cb: Callable[[Dict[str, Any]], None]) -> None:
        self._callbacks.append(cb)

    async def start(self) -> None:
        if self._task_loop and not self._task_loop.done():
            return
        self._running.set()
        self._task_loop = asyncio.create_task(self._run())

    async def stop(self) -> None:
        self._running.clear()
        if self._task_loop:
            try:
                await asyncio.wait_for(self._task_loop, timeout=1.0)
            except Exception:
                self._task_loop.cancel()

    def set_motion_state(self, moving: bool) -> None:
        if moving:
            self._motion_active.set()
        else:
            self._motion_active.clear()

    def request_snapshot_now(self) -> None:
        self._want_snapshot.set()

    def request_coords_now(self) -> None:
        self._want_coords.set()

    async def _run(self) -> None:
        # initial snapshot once running
        self._want_snapshot.set()
        last_coords_at = 0.0
        while self._running.is_set():
            try:
                # prefer explicit requests
                if self._want_snapshot.is_set():
                    self._want_snapshot.clear()
                    await self._do_snapshot()
                    continue
                if self._want_coords.is_set():
                    self._want_coords.clear()
                    await self._do_coords()
                    continue

                # motion-driven coords refresh
                if self._motion_active.is_set():
                    now = time.time()
                    if now - last_coords_at >= self._cooldown_coords_s:
                        last_coords_at = now
                        await self._do_coords()
                        continue

                await asyncio.sleep(0.02)
            except asyncio.CancelledError:
                break
            except Exception:
                # swallow errors; agent should be resilient
                await asyncio.sleep(0.1)

    async def _do_snapshot(self) -> None:
        if not self._transport or not self._transport.is_connected():
            return
        try:
            # Prefer compact M408 S0 to populate homed[] and quick status
            line0 = "M408 S0"
            resp0 = await asyncio.to_thread(self._transport.query, line0)
            data0 = None
            if resp0:
                try:
                    import json
                    t0 = resp0.strip()
                    if "{" in t0 and "}" in t0:
                        t0 = t0[t0.find("{") : t0.rfind("}") + 1]
                    data0 = json.loads(t0) if t0 else None
                except Exception:
                    data0 = None
            # Optionally follow with S2 for fuller object model
            data2 = None
            try:
                line2 = "M408 S2"
                resp2 = await asyncio.to_thread(self._transport.query, line2)
                if resp2:
                    import json
                    t2 = resp2.strip()
                    if "{" in t2 and "}" in t2:
                        t2 = t2[t2.find("{") : t2.rfind("}") + 1]
                    data2 = json.loads(t2)
            except Exception:
                data2 = None
            merged_raw = {}
            if isinstance(data2, dict):
                merged_raw = data2
            if isinstance(data0, dict):
                # data0 may include keys like homed[] and machine[]
                merged_raw = {**merged_raw, **data0}
            if not merged_raw:
                return
            patch = {"raw_status": {"raw": merged_raw}, "firmware": {"status": (data0 or data2 or {}).get("status")}}
            self._emit_patch(patch)
            # Ensure homed[] present using M409 if missing
            try:
                if not isinstance(merged_raw.get("homed"), list):
                    await self._refresh_homed()
            except Exception:
                pass
        except Exception:
            pass

    async def _refresh_homed(self) -> None:
        if not self._transport or not self._transport.is_connected():
            return
        try:
            from semantic_gcode.dict.gcode_commands.M409.M409 import M409_QueryObjectModel
            cmd = M409_QueryObjectModel.create(path='move.axes[].homed', s=2)
            resp = await asyncio.wait_for(asyncio.to_thread(self._transport.query, str(cmd)), timeout=0.8)
            if not resp:
                return
            import json
            txt = resp.strip()
            if "{" in txt and "}" in txt:
                txt = txt[txt.find("{") : txt.rfind("}") + 1]
            data = json.loads(txt)
            result = data.get("result") if isinstance(data, dict) else None
            if isinstance(result, list) and result:
                self._emit_patch({"raw_status": {"raw": {"homed": result}}})
        except Exception:
            pass

    async def _do_coords(self) -> None:
        if not self._transport or not self._transport.is_connected():
            return
        start_ts = time.time()
        try:
            from semantic_gcode.dict.gcode_commands.M409.M409 import M409_QueryObjectModel
            # Prefer coords.machine; returns {"key":"coords.machine","result":{"coords":{"machine":[...]}}}
            cmd = M409_QueryObjectModel.create(path='coords.machine', s=2)
            resp = await asyncio.wait_for(asyncio.to_thread(self._transport.query, str(cmd)), timeout=0.8)
            if not resp:
                return
            if (time.time() - start_ts) > 1.0:
                return  # stale
            data = cmd.parse_json(resp) or {}
            result = data.get("result")
            flat: list[float] = []
            # Handle either nested {"coords":{"machine":[...]}} or direct list
            if isinstance(result, dict):
                maybe = result.get("coords", {}).get("machine") if isinstance(result.get("coords"), dict) else None
                if isinstance(maybe, list):
                    flat = [float(x) for x in maybe if isinstance(x, (int, float))]
            elif isinstance(result, list):
                flat = [float(x) for x in result if isinstance(x, (int, float))]
            if len(flat) >= 3:
                if self._last_emit and all(abs(flat[i] - self._last_emit[1][i]) < 1e-3 for i in range(3)):
                    return
                self._last_emit = (time.time(), (flat[0], flat[1], flat[2]))
                patch = {"coords": {"machine_position": flat}}
                self._emit_patch(patch)
        except Exception:
            pass

    def _emit_patch(self, patch: Dict[str, Any]) -> None:
        for cb in list(self._callbacks):
            try:
                cb(patch)
            except Exception:
                pass 