from __future__ import annotations

from typing import Optional
import threading
import time
import os

from textual import events
from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Input, Footer, RichLog
from rich.markup import escape

from realtime_hairbrush.runtime import Dispatcher, MachineState, ObjectModelAgent
from realtime_hairbrush.runtime.events import (
    SentEvent,
    ReceivedEvent,
    AckEvent,
    ErrorEvent,
    StateUpdatedEvent,
)
from realtime_hairbrush.runtime.readers import StatusPoller
from realtime_hairbrush.transport.airbrush_transport import AirbrushTransport
from realtime_hairbrush.transport.config import ConnectionConfig
from realtime_hairbrush.config.settings import load_settings, clear_settings, update_last_connection
from realtime_hairbrush.runtime.object_model import parse_object_model
from realtime_hairbrush.runtime.sequencer import Request, RequestKind, Priority
from realtime_hairbrush.runtime.sequencer import HttpQuerySpec
from realtime_hairbrush.execution.tool_manager import ToolManager
from semantic_gcode.dict.gcode_commands.G4.G4 import G4_Dwell


class AirbrushTextualApp(App):
    CSS = """
    #status {
        background: #2ecc71; /* light green */
        color: black;
        padding: 0 1;
        text-style: bold;
    }
    """

    def __init__(
        self,
        transport: Optional[AirbrushTransport],
        dispatcher: Optional[Dispatcher],
        state: MachineState,
    ) -> None:
        super().__init__()
        self.transport = transport
        self.dispatcher = dispatcher
        self.state = state
        self.poller: Optional[StatusPoller] = None
        self._listener_attached = False
        # Verbosity (OFF by default to suppress polling spam)
        self._verbose: bool = False
        # Track whether last sent line was an M408 (to suppress its 'ok' when verbose OFF)
        self._last_sent_was_m408: bool = False
        # One-shot wait for IP query (fulfilled by ReceivedEvent)
        self._ip_wait_active: bool = False
        self._ip_wait_event: threading.Event = threading.Event()
        self._ip_wait_result: Optional[str] = None
        # Track last time we saw a status update to detect stale connection
        self._last_status_ts: float = 0.0
        # Temporary motion refresh timer (Textual timer) to boost status during moves (legacy path)
        self._motion_refresh_timer = None
        self._motion_refresh_inflight: bool = False
        self._last_machine_pos = None
        self._move_timeout_prev: Optional[float] = None
        # Command history
        self._history: list[str] = []
        self._hist_pos: Optional[int] = None
        self._commands = [
            "help","connect","disconnect","home","move","tool",
            "air","paint","dot","draw","ip","gcode","status","verbose","exit","quit"
        ]

        # Widgets
        self.status_widget: Optional[Static] = None
        self.high_log: Optional[RichLog] = None
        self.gcode_log: Optional[RichLog] = None
        self.input_widget: Optional[Input] = None

        # Async ObjectModelAgent (optional)
        # Enable async agent by default in this branch; allow opt-out via AIRBRUSH_ASYNC=0
        self._use_async_agent = os.getenv("AIRBRUSH_ASYNC", "1") not in ("0", "false", "False")
        self._agent: Optional[ObjectModelAgent] = ObjectModelAgent() if self._use_async_agent else None
        # Tool manager middleware
        self.tool_manager: Optional[ToolManager] = None

    def compose(self) -> ComposeResult:
        self.status_widget = Static(self._status_block_text(), id="status")
        self.high_log = RichLog(id="high", wrap=False)
        self.high_log.write("[High-level messages]\nType 'help' for commands.\n")
        self.high_log.write("Verbose: OFF\n")
        self.gcode_log = RichLog(id="gcode", wrap=False)
        self.gcode_log.write("[Raw G-code stream]\n")
        self.input_widget = Input(placeholder="> type commands here", id="input")
        yield Vertical(
            self.status_widget,
            Horizontal(self.high_log, self.gcode_log),
            self.input_widget,
            Footer(),
        )

    def on_mount(self) -> None:
        if self.input_widget:
            self.input_widget.focus()
        if self.dispatcher and not self._listener_attached:
            self.dispatcher.on_event(lambda ev: self.call_from_thread(self._handle_event, ev))
            self._listener_attached = True
        # Disable legacy StatusPoller if async agent is used
        if self._agent:
            self.poller = None
        # Start async ObjectModelAgent if enabled
        if self._agent and self.transport:
            try:
                self._agent.set_transport(self.transport)
                self._agent.set_verbose(self._verbose)
                self._agent.on_change(lambda patch: self.call_from_thread(self._merge_observed_patch, patch))
                import asyncio
                asyncio.get_event_loop().create_task(self._agent.start())
            except Exception:
                pass
        # force an immediate status render tick while first poll is in-flight
        self._update_status()
        # On startup, if connected, schedule a one-shot deferred snapshot to avoid blocking render
        if self._agent and self.transport and self.transport.is_connected():
            try:
                import asyncio
                self.call_later(lambda: asyncio.get_event_loop().call_later(0.05, lambda: self._agent.request_snapshot_now()))
            except Exception:
                pass
        self.set_interval(0.5, self._update_status)

    def on_unmount(self) -> None:
        if self.poller:
            try:
                self.poller.stop()
            except Exception:
                pass
        if self._agent:
            try:
                import asyncio
                asyncio.get_event_loop().create_task(self._agent.stop())
            except Exception:
                pass

    def on_key(self, event: events.Key) -> None:
        if not self.input_widget or not self.input_widget.has_focus:
            return
        if event.key == "up":
            if not self._history:
                return
            if self._hist_pos is None:
                self._hist_pos = len(self._history) - 1
            else:
                self._hist_pos = max(0, self._hist_pos - 1)
            self.input_widget.value = self._history[self._hist_pos]
            event.stop()
        elif event.key == "down":
            if self._hist_pos is None:
                return
            if self._hist_pos < len(self._history) - 1:
                self._hist_pos += 1
                self.input_widget.value = self._history[self._hist_pos]
            else:
                self._hist_pos = None
                self.input_widget.value = ""
            event.stop()
        elif event.key == "tab":
            text = (self.input_widget.value or "").lstrip()
            if not text:
                return
            head = text.split()[0]
            matches = [c for c in self._commands if c.startswith(head)]
            if not matches:
                return
            def common_prefix(strs: list[str]) -> str:
                if not strs:
                    return ""
                s1 = min(strs)
                s2 = max(strs)
                i = 0
                while i < len(s1) and i < len(s2) and s1[i] == s2[i]:
                    i += 1
                return s1[:i]
            completion = matches[0] if len(matches) == 1 else common_prefix(matches)
            if completion and completion != head:
                rest = text[len(head):]
                self.input_widget.value = completion + (" " if not rest or rest.startswith(" ") is False else "")
                event.stop()

    def _emit_event_safe(self, ev) -> None:
        self.call_from_thread(self._handle_event, ev)

    def _force_status_refresh(self) -> None:
        if not self.dispatcher:
            return
        seq = getattr(self.dispatcher, "sequencer", None)
        if not seq:
            return
        specs = [
            ("move.axes[].machinePosition", "f"),
            ("move.axes[].homed", "f"),
            ("state.status", "f"),
            ("state.currentTool", "f"),
        ]
        def make_cb(key: str):
            def on_complete(res):
                if not res or not res.ok or res.data is None:
                    return
                data = res.data
                raw = data if isinstance(data, dict) else {}
                result = raw.get("result") if isinstance(raw, dict) else None
                patch = {}
                if key == "move.axes[].machinePosition" and isinstance(result, list):
                    patch = {"coords": {"machine_position": result}, "raw_status": {"raw": {"coords": {"machine": result}}}}
                elif key == "move.axes[].homed" and isinstance(result, list):
                    patch = {"homed": {"axes": result}, "raw_status": {"raw": {"coords": {"axesHomed": result}}}}
                elif key == "state.status":
                    patch = {"firmware": {"status": result}}
                elif key == "state.currentTool":
                    patch = {"raw_status": {"raw": {"currentTool": result}}}
                if patch:
                    self._merge_observed_patch(patch)
            return on_complete
        for key, flags in specs:
            spec = HttpQuerySpec(endpoint="rr_model", params={"key": key, "flags": flags})
            req = Request(kind=RequestKind.QUERY, priority=Priority.MEDIUM, payload=spec, timeout_s=2.0, on_complete=make_cb(key))
            req.coalesce_key = f"ui:{key}"
            seq.submit(req)

    def _update_status(self) -> None:
        if self.status_widget:
            self.status_widget.update(self._status_block_text())

    def _refresh_status_once(self) -> None:
        if not self.transport or not self.transport.is_connected():
            return
        # If async agent is active, delegate to it and avoid direct M408 here
        if self._agent:
            try:
                self._agent.request_snapshot_now()
            except Exception:
                pass
            return
        try:
            from semantic_gcode.dict.gcode_commands.M408.M408 import M408_ReportObjectModel
            cmd = M408_ReportObjectModel.create(selector=0)
            resp = self.transport.query(str(cmd))
            if resp:
                parsed = cmd.parse_status(resp)
                observed = {"firmware": {"status": parsed.get("status")}, "raw_status": parsed}
                self.state.update_observed(observed)
                self._update_status()
                self._last_status_ts = time.time()
        except Exception:
            pass

    def _merge_observed_patch(self, patch: dict) -> None:
        def deep_merge(a, b):
            if not isinstance(a, dict) or not isinstance(b, dict):
                return b
            out = dict(a)
            for key, val in b.items():
                if isinstance(val, dict):
                    out[key] = deep_merge(out.get(key, {}), val)
                else:
                    out[key] = val
            return out
        snap = self.state.snapshot().get("observed", {})
        merged = deep_merge(snap, patch or {})
        self.state.update_observed(merged)
        self._update_status()

    def _get_current_tool_index(self) -> int:
        obs_tool = self.state.snapshot().get("observed", {}).get("raw_status", {}).get("raw", {}).get("currentTool")
        return 0 if obs_tool is None else int(obs_tool)

    def _get_paint_flow(self) -> Optional[float]:
        predictive = self.state.snapshot().get("predictive", {})
        pos = predictive.get("position", {})
        tool_index = self._get_current_tool_index()
        axis = 'u' if tool_index == 0 else 'v'
        val = pos.get(axis)
        try:
            return float(val) if val is not None else None
        except Exception:
            return None

    def _flow_to_mm(self, flow: float) -> float:
        try:
            f = max(0.0, min(1.0, float(flow)))
        except Exception:
            f = 0.0
        return 4.0 * (0.2 + 0.8 * f)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        text = (event.value or "").strip()
        if not text:
            return
        if not self._history or self._history[-1] != text:
            self._history.append(text)
        self._hist_pos = None
        if self.input_widget:
            self.input_widget.value = ""
        threading.Thread(target=self._handle_command_sync, args=(text,), daemon=True).start()

    def _status_block_text(self) -> str:
        mode = None
        host = "-"
        connected = False
        if self.transport and self.transport.is_connected():
            connected = True
            mode = self.transport.config.transport_type
            if mode == "serial":
                host = self.transport.config.serial_port or "-"
            elif mode == "http":
                host = self.transport.config.http_host or "-"
        obs = self.state.snapshot().get("observed", {})
        fw_status = obs.get("firmware", {}).get("status")
        label_map = {
            "I": "Idle", "i": "Idle", "idle": "Idle",
            "B": "Busy", "busy": "Busy",
            "P": "Printing", "printing": "Printing",
            "H": "Homing", "homing": "Homing",
            "S": "Stopped", "stopped": "Stopped",
        }
        label = label_map.get(str(fw_status).strip() if fw_status is not None else None, None)
        # Keep last known label if unknown or None
        if not hasattr(self, "_last_status_label"):
            self._last_status_label = "Idle" if (self.transport and self.transport.is_connected()) else "?"
        if not label:
            if connected:
                label = "Idle"
                self._last_status_label = label
            else:
                label = getattr(self, "_last_status_label", "?")
        else:
            self._last_status_label = label
        # Use live machine position for in-flight updates; xyz is the commanded/target position
        pos = (
            obs.get("coords", {}).get("machine_position")
            or obs.get("raw_status", {}).get("raw", {}).get("coords", {}).get("machine")
            or obs.get("raw_status", {}).get("raw", {}).get("coords", {}).get("xyz")
            or obs.get("raw_status", {}).get("raw", {}).get("position")
        )
        # Homing info can be provided as coords.axesHomed (M408 S2) or homed (M408 S0)
        homed_list = (
            obs.get("homed", {}).get("axes")
            or obs.get("raw_status", {}).get("raw", {}).get("coords", {}).get("axesHomed")
            or obs.get("raw_status", {}).get("raw", {}).get("homed")
            or []
        )
        def is_homed_xyz() -> bool:
            try:
                return bool(int(homed_list[0])) and bool(int(homed_list[1])) and bool(int(homed_list[2]))
            except Exception:
                return False
        homed_flag = is_homed_xyz()
        def fmt(v):
            try:
                return f"{float(v):.3f}"
            except Exception:
                return "-"
        if isinstance(pos, (list, tuple)) and len(pos) >= 3:
            x = fmt(pos[0]) if homed_flag else "?"
            y = fmt(pos[1]) if homed_flag else "?"
            z = fmt(pos[2]) if homed_flag else "?"
        else:
            x = y = z = "?" if homed_flag is False else "-"
        tool = obs.get("raw_status", {}).get("raw", {}).get("currentTool")
        tool_str = str(tool) if tool is not None else "-"
        fan_percent = obs.get("raw_status", {}).get("raw", {}).get("params", {}).get("fanPercent") or []
        air_on = None
        try:
            # Fans 2/3 used for air; OFF if 0 or not present
            chan2 = fan_percent[2] if len(fan_percent) > 2 else 0
            chan3 = fan_percent[3] if len(fan_percent) > 3 else 0
            air_on = (chan2 > 0) or (chan3 > 0)
        except Exception:
            air_on = None
        air_str = "ON" if air_on is True else ("OFF" if air_on is False else "-")
        paint_flow = self._get_paint_flow()
        paint_str = (f"{paint_flow:.2f}" if paint_flow is not None else "-")
        homed = homed_list
        def flag(i):
            try:
                return "1" if int(homed[i]) else "0"
            except Exception:
                return "-"
        limits = f"[X:{flag(0)}] [Y:{flag(1)}] [Z:{flag(2)}] [U:{flag(3)}] [V:{flag(4)}]"
        diag = obs.get("diagnostics", {})
        vin = diag.get("vin")
        if vin is None:
            vin = obs.get("raw_status", {}).get("raw", {}).get("params", {}).get("atxPower")
        vin = "-" if vin is None else vin
        mcu_temp = diag.get("mcu_temp_c", "-")
        driver_temp = diag.get("driver_temp_c", "-")
        overtemp = diag.get("overtemp_warning", False)
        driver_label = f"Driver temp: {'WARNING' if overtemp else driver_temp}"
        ends = obs.get("endstops", {})
        ends_list = " ".join([f"{k}:{'1' if v else '0'}" for k, v in ends.items()]) if ends else ""
        if not connected:
            conn_label = "Not Connected"
        else:
            conn_label = f"Serial:{host}" if (mode == "serial") else (f"HTTP:{host}" if mode == "http" else "-:-")
        homed_text = "Yes" if homed_flag else "No"
        line1 = f"Status:{label} | ToolPos[X:{x}] [Y:{y}] [Z:{z}] | Homed:{homed_text}"
        line2 = f"Tool:{tool_str} | Air:{air_str} | Paint:{paint_str} | Endstops: {ends_list}"
        # Place Not Connected at the start of System line before Vin
        line3 = f"System: [{conn_label}] [Vin {vin} V] [MCU Temp: {mcu_temp} C] [{driver_label}]"
        return "\n".join([line1, line2, line3])

    def _handle_command_sync(self, text: str) -> None:
        parts = text.split()
        if not parts:
            return
        # Echo command to high-level log for history
        if self.high_log:
            self.high_log.write(f"> {text}")
        cmd = parts[0].lower()
        rest = parts[1:]
        try:
            if cmd == "help":
                if self.high_log:
                    # Detailed help from commands.yaml when a topic is given
                    try:
                        from realtime_hairbrush.cli.utils.command_parser import parse_commands_yaml
                        import os
                        yaml_path = os.path.join(os.path.dirname(__file__), '..', 'commands.yaml')
                        yaml_path = os.path.abspath(yaml_path)
                        commands = parse_commands_yaml(yaml_path)
                    except Exception:
                        commands = {}
                    topic = (rest[0].lower() if rest else None)
                    if topic and topic in commands:
                        cdef = commands[topic] or {}
                        self.high_log.write(f"{topic}: {cdef.get('purpose','')}")
                        params = cdef.get('params', {})
                        if isinstance(params, list):
                            # flatten list to dict
                            p = {}
                            for itm in params:
                                if isinstance(itm, dict):
                                    p.update(itm)
                                else:
                                    p[itm] = {}
                            params = p
                        if isinstance(params, dict) and params:
                            self.high_log.write("Parameters:")
                            for pname, pdef in params.items():
                                if not isinstance(pdef, dict):
                                    pdef = {}
                                opt = pdef.get('optional', True)
                                acc = pdef.get('accepts', []) or []
                                self.high_log.write(f"  {pname}{' (optional)' if opt else ''}: {pdef.get('purpose','')}")
                                if acc:
                                    self.high_log.write(f"    accepts: {', '.join(str(a) for a in acc)}")
                        examples = cdef.get('usage-examples', []) or []
                        if examples:
                            self.high_log.write("Examples:")
                            for ex in examples:
                                self.high_log.write(f"  {ex}")
                        return
                    # Fallback: list commands
                    self.high_log.write("Commands:")
                    for name, cdef in sorted((commands or {}).items()):
                        self.high_log.write(f"  {name}: {cdef.get('purpose','')}")
                return
            if cmd == "verbose":
                val = (rest[0].lower() if rest else "").strip()
                if val in ("on", "1", "true", "yes"):
                    self._verbose = True
                elif val in ("off", "0", "false", "no"):
                    self._verbose = False
                else:
                    # Toggle if no/invalid arg
                    self._verbose = not self._verbose
                if self.high_log:
                    self.high_log.write(f"Verbose: {'ON' if self._verbose else 'OFF'}")
                return
            if cmd == "settings":
                # settings [show|clear]
                sub = (rest[0].lower() if rest else "show")
                if sub == "show":
                    data = load_settings()
                    if self.high_log:
                        self.high_log.write("Settings:")
                        self.high_log.write(str(data or {}))
                    return
                if sub == "clear":
                    clear_settings()
                    if self.high_log:
                        self.high_log.write("Settings cleared.")
                    return
                if self.high_log:
                    self.high_log.write(f"[error] Unknown settings subcommand: {sub}")
                return
            if cmd in ("exit", "quit"):
                self.exit()
                return
            # Connection guard for commands that require an active transport
            requires_connection = cmd in {
                "home","move","tool","air","paint","dot","draw","gcode","status","estop"
            }
            if requires_connection and (not self.transport or not self.transport.is_connected()):
                if self.high_log:
                    self.high_log.write("[error] Not connected")
                return
            if cmd == "connect":
                if len(rest) < 1:
                    if self.high_log:
                        self.high_log.write("[error] connect serial <port> [baud] | connect http <ip> | connect serial auto | connect last")
                    return
                mode = rest[0].lower()
                settings = load_settings()
                last = settings.get("last", {})
                transport_type = None
                cfg = None
                if mode == "last":
                    transport_type = last.get("transport")
                    if transport_type == "serial":
                        port = last.get("serial_port")
                        baud = last.get("baud", 115200)
                        if not port:
                            if self.high_log: self.high_log.write("[error] No last serial port stored")
                            return
                        cfg = ConnectionConfig(transport_type="serial", serial_port=port, serial_baudrate=int(baud), timeout=5.0)
                    elif transport_type == "http":
                        ip = last.get("ip")
                        if not ip:
                            if self.high_log: self.high_log.write("[error] No last IP stored")
                            return
                        cfg = ConnectionConfig(transport_type="http", http_host=ip, timeout=10.0)
                    else:
                        if self.high_log: self.high_log.write("[error] No last connection stored")
                        return
                elif mode == "serial" and len(rest) >= 2 and rest[1].lower() == "last":
                    port = last.get("serial_port")
                    baud = last.get("baud", 115200)
                    if not port:
                        if self.high_log: self.high_log.write("[error] No last serial port stored")
                        return
                    cfg = ConnectionConfig(transport_type="serial", serial_port=port, serial_baudrate=int(baud), timeout=5.0)
                elif mode == "http" and len(rest) >= 2 and rest[1].lower() == "last":
                    ip = last.get("ip")
                    if not ip:
                        if self.high_log: self.high_log.write("[error] No last IP stored")
                        return
                    cfg = ConnectionConfig(transport_type="http", http_host=ip, timeout=10.0)
                elif mode == "serial":
                    if len(rest) >= 2 and rest[1].lower() == "auto":
                        from realtime_hairbrush.cli.utils.port_selection import select_port_for_device
                        port = select_port_for_device("duet")
                        if not port:
                            if self.high_log: self.high_log.write("[error] No Duet device found")
                            return
                        baud = 115200
                    else:
                        if len(rest) < 2:
                            if self.high_log: self.high_log.write("[error] connect serial <port> [baud]")
                            return
                        port = rest[1]
                        baud = int(rest[2]) if len(rest) > 2 else 115200
                    cfg = ConnectionConfig(transport_type="serial", serial_port=port, serial_baudrate=baud, timeout=5.0)
                elif mode == "http":
                    if len(rest) < 2:
                        if self.high_log: self.high_log.write("[error] connect http <ip>")
                        return
                    ip = rest[1]
                    cfg = ConnectionConfig(transport_type="http", http_host=ip, timeout=10.0)
                else:
                    if self.high_log: self.high_log.write("[error] connect serial|http ...")
                    return
                # Teardown any prior runtime
                if self.poller:
                    try:
                        self.poller.stop()
                    except Exception:
                        pass
                    self.poller = None
                self._listener_attached = False
                if self.dispatcher:
                    try:
                        # Best-effort stop if implemented
                        stop = getattr(self.dispatcher, "stop", None)
                        if callable(stop):
                            stop()
                    except Exception:
                        pass
                    self.dispatcher = None
                # Create new transport and connect
                self.transport = AirbrushTransport(cfg)
                if not self.transport.connect():
                    if self.high_log:
                        self.high_log.write(f"[error] connect failed: {self.transport.get_last_error()}")
                    return
                # Create fresh dispatcher (no periodic poller; status is on-demand)
                self.dispatcher = Dispatcher(self.transport, self.state)
                self.dispatcher.on_event(lambda ev: self.call_from_thread(self._handle_event, ev))
                self.dispatcher.start()
                self._listener_attached = True
                # Wire transport into async ObjectModelAgent if enabled
                if self._agent:
                    try:
                        self._agent.set_transport(self.transport)
                    except Exception:
                        pass
                # Initialize ToolManager
                try:
                    self.tool_manager = ToolManager(self.dispatcher, self.state)
                except Exception:
                    self.tool_manager = None
                # Start sequencer-backed status poller to guarantee status population
                try:
                    from realtime_hairbrush.runtime.readers import StatusPoller
                    self.poller = StatusPoller(self.dispatcher.sequencer, self.state, emit=self._emit_event_safe, interval_fast=0.25, interval_medium=2.5, interval_slow=25.0)
                    self.poller.start()
                except Exception:
                    self.poller = None
                # Immediately fetch full status once on connect
                try:
                    if self._agent:
                        self._agent.request_snapshot_now()
                    else:
                        self._refresh_status_once()
                    # Also force a targeted refresh via sequencer to populate homed and coords immediately
                    self._force_status_refresh()
                finally:
                    # update UI immediately regardless of fetch outcome
                    self.call_from_thread(self._update_status)
                # Save last successful connection with fingerprint
                fingerprint = {}
                try:
                    from semantic_gcode.dict.gcode_commands.M115.M115 import M115_GetFirmwareInfo
                    m115 = M115_GetFirmwareInfo.create()
                    resp = self.transport.query(str(m115))
                    if resp:
                        fingerprint = m115.parse_info(resp)
                except Exception:
                    fingerprint = {}
                ttype = self.transport.config.transport_type
                serial_port = self.transport.config.serial_port if ttype == "serial" else None
                baud = self.transport.config.serial_baudrate if ttype == "serial" else None
                ip = self.transport.config.http_host if ttype == "http" else None
                update_last_connection(ttype, serial_port=serial_port, baud=baud, ip=ip, fingerprint=fingerprint)
                if self.high_log:
                    used = f"serial ({serial_port}@{baud})" if ttype == "serial" else f"http ({ip})"
                    self.high_log.write(f"Connected via {used}")
                self.call_from_thread(self._update_status)
                return
            if cmd == "disconnect":
                # Stop poller
                if self.poller:
                    try:
                        self.poller.stop()
                    except Exception:
                        pass
                    self.poller = None
                # Stop dispatcher
                if self.dispatcher:
                    try:
                        stop = getattr(self.dispatcher, "stop", None)
                        if callable(stop):
                            stop()
                    except Exception:
                        pass
                    self.dispatcher = None
                self._listener_attached = False
                # Disconnect transport
                if self.transport and self.transport.is_connected():
                    try:
                        self.transport.disconnect()
                    except Exception:
                        pass
                self.transport = None
                # Reset status timestamps to mark as not connected
                self._last_status_ts = 0.0
                if self.high_log:
                    self.high_log.write("Disconnected")
                self.call_from_thread(self._update_status)
                return
            if cmd == "home":
                from semantic_gcode.dict.gcode_commands.G28.G28 import G28_Home
                g28 = G28_Home.create(axes=None)
                if self.dispatcher:
                    self.dispatcher.enqueue(g28)
                else:
                    self.transport.send_line(str(g28))
                return
            if cmd == "move":
                # move x.. y.. [z..] [f..]
                # Block if not homed
                try:
                    obs = self.state.snapshot().get("observed", {})
                    homed = (
                        obs.get("homed", {}).get("axes")
                        or obs.get("raw_status", {}).get("raw", {}).get("coords", {}).get("axesHomed")
                        or obs.get("raw_status", {}).get("raw", {}).get("homed")
                        or []
                    )
                    ok = False
                    if isinstance(homed, (list, tuple)) and len(homed) >= 3:
                        try:
                            ok = bool(int(homed[0])) and bool(int(homed[1])) and bool(int(homed[2]))
                        except Exception:
                            ok = False
                    if not ok:
                        if self.high_log:
                            self.high_log.write("[error] Machine is not homed. Please home first.")
                        return
                except Exception:
                    if self.high_log:
                        self.high_log.write("[error] Machine is not homed. Please home first.")
                    return
                kv = {p[0].lower(): p[1:] for p in rest if len(p) >= 2 and p[0].lower() in ("x","y","z","f") and p[1:].replace('.', '', 1).replace('-', '', 1).isdigit()}
                x = float(kv['x']) if 'x' in kv else None
                y = float(kv['y']) if 'y' in kv else None
                z = float(kv['z']) if 'z' in kv else None
                f = float(kv['f']) if 'f' in kv else None
                if x is None and y is None and z is None:
                    if self.high_log:
                        self.high_log.write("[error] move requires at least one of x, y, z")
                    return
                # Fill Z from observed if omitted
                if z is None:
                    try:
                        snap = self.state.snapshot().get("observed", {}).get("raw_status", {}).get("raw", {})
                        pos = (
                            snap.get("coords", {}).get("machine")
                            or snap.get("coords", {}).get("xyz")
                            or snap.get("position")
                        )
                        if isinstance(pos, (list, tuple)) and len(pos) >= 3:
                            z = float(pos[2])
                    except Exception:
                        z = z
                if self.tool_manager:
                    self.tool_manager.move_to(x if x is not None else self.tool_manager.get_logical_position()['x'],
                                              y if y is not None else self.tool_manager.get_logical_position()['y'],
                                              z=z,
                                              feedrate=f if f is not None else 3000,
                                              wait=True)
                else:
                    from semantic_gcode.dict.gcode_commands.G1.G1 import G1_LinearMove
                    from semantic_gcode.dict.gcode_commands.M400.M400 import M400_WaitForMoves
                    params = {}
                    if x is not None: params['x'] = x
                    if y is not None: params['y'] = y
                    if z is not None: params['z'] = z
                    if f is not None: params['feedrate'] = f
                    g1 = G1_LinearMove.create(**params)
                    m400 = M400_WaitForMoves.create()
                    if self.dispatcher:
                        self.dispatcher.enqueue(g1); self.dispatcher.enqueue(m400)
                    else:
                        self.transport.send_line(str(g1)); self.transport.query(str(m400))
                # Notify async agent that motion is active; it will poll coords faster during motion
                if self._agent:
                    try:
                        self._agent.set_motion_state(True)
                    except Exception:
                        pass
                # Do not immediately set predictive final pos in status bar; rely on observed polling
                return
            if cmd == "tool":
                if not rest:
                    if self.high_log:
                        self.high_log.write("[error] tool requires index")
                    return
                raw = rest[0]
                resolved_idx = None
                if self.tool_manager:
                    try:
                        # Let ToolManager resolve aliases and perform the switch
                        self.tool_manager.switch_tool(raw, wait=True)
                        # Best-effort derive numeric index from alias for local observed patch
                        rl = str(raw).lower()
                        if rl.isdigit():
                            resolved_idx = int(rl)
                        elif rl in ("1","b","white"): resolved_idx = 1
                        elif rl in ("0","a","black"): resolved_idx = 0
                    except Exception as e:
                        if self.high_log:
                            self.high_log.write(f"[error] tool: {e}")
                        return
                else:
                    # Fallback: attempt to resolve alias locally
                    rl = str(raw).lower()
                    if rl.isdigit():
                        resolved_idx = int(rl)
                    elif rl in ("1","b","white"):
                        resolved_idx = 1
                    elif rl in ("0","a","black"):
                        resolved_idx = 0
                    else:
                        if self.high_log:
                            self.high_log.write("[error] tool: expected 0/a/black or 1/b/white")
                        return
                    from semantic_gcode.dict.gcode_commands.T.T import T_SelectTool
                    from semantic_gcode.dict.gcode_commands.M400.M400 import M400_WaitForMoves
                    tsel = T_SelectTool.create(tool_number=resolved_idx)
                    m400 = M400_WaitForMoves.create()
                    if self.dispatcher:
                        self.dispatcher.enqueue(tsel); self.dispatcher.enqueue(m400)
                    else:
                        self.transport.send_line(str(tsel)); self.transport.query(str(m400))
                # Local update of tool index in observed state (status polling will confirm)
                if resolved_idx is not None:
                    self._merge_observed_patch({"raw_status": {"raw": {"currentTool": resolved_idx}}})
                return
            if cmd == "air":
                # air [on|off] [tool]
                state = None
                tool_arg = None
                for token in rest:
                    t = token.lower()
                    if t in ("on","1","true","yes","off","0","false","no"):
                        state = t
                    elif t in ("0","a","black","1","b","white"):
                        tool_arg = t
                is_on = (state is None) or (state in ("on","1","true","yes"))
                is_off = (state in ("off","0","false","no"))
                target = tool_arg
                if self.tool_manager:
                    if is_on:
                        self.tool_manager.set_air(True, tool=target)
                    elif is_off:
                        self.tool_manager.set_air(False, tool=target)
                    else:
                        if self.high_log:
                            self.high_log.write("[error] air: unknown state; use on/off")
                        return
                else:
                    # Fallback (previous behavior)
                    from semantic_gcode.dict.gcode_commands.M106.M106 import M106_FanControl
                    obs_tool = self.state.snapshot().get("observed", {}).get("raw_status", {}).get("raw", {}).get("tool")
                    tool_index = 0 if obs_tool is None else int(obs_tool)
                    if tool_arg in ("1","b","white"):
                        tool_index = 1
                    fan_on = 2 if tool_index == 0 else 3
                    fan_other = 3 if tool_index == 0 else 2
                    seq = []
                    if is_on:
                        seq.append(M106_FanControl.create(p=fan_other, s=0.0))
                        seq.append(M106_FanControl.create(p=fan_on, s=1.0))
                    elif is_off:
                        if tool_arg is None:
                            seq.append(M106_FanControl.create(p=2, s=0.0))
                            seq.append(M106_FanControl.create(p=3, s=0.0))
                        else:
                            seq.append(M106_FanControl.create(p=fan_on, s=0.0))
                    else:
                        if self.high_log:
                            self.high_log.write("[error] air: unknown state; use on/off")
                        return
                    if self.dispatcher:
                        for instr in seq:
                            self.dispatcher.enqueue(instr)
                    else:
                        for instr in seq:
                            self.transport.send_line(str(instr))
                # After enqueuing, update local observed fanPercent immediately
                # Determine indexes again (simple re-eval)
                tool_index = self._get_current_tool_index()
                if any(tok.lower() in ("1","b","white") for tok in rest):
                    tool_index = 1
                fan_on = 2 if tool_index == 0 else 3
                fan_other = 3 if tool_index == 0 else 2
                state_tok = next((t.lower() for t in rest if t.lower() in ("on","1","true","yes","off","0","false","no")), None)
                is_on = (state_tok is None) or (state_tok in ("on","1","true","yes"))
                is_off = state_tok in ("off","0","false","no")
                fanPercent = [0.0] * 13
                if is_on:
                    # other off, selected on
                    if fan_on < len(fanPercent):
                        fanPercent[fan_on] = 1.0
                    if fan_other < len(fanPercent):
                        fanPercent[fan_other] = 0.0
                elif is_off:
                    if any(tok.lower() in ("0","a","black","1","b","white") for tok in rest):
                        if fan_on < len(fanPercent):
                            fanPercent[fan_on] = 0.0
                    else:
                        # all off
                        pass
                self._merge_observed_patch({"raw_status": {"raw": {"fanPercent": fanPercent}}})
                return
            if cmd == "paint":
                # paint <flow 0..1>
                # Block if not homed
                try:
                    obs = self.state.snapshot().get("observed", {}).get("raw_status", {}).get("raw", {}).get("coords", {}).get("axesHomed") or []
                    if not (bool(int(homed[0])) and bool(int(homed[1])) and bool(int(homed[2]))):
                        if self.high_log:
                            self.high_log.write("[error] Machine is not homed. Please home first.")
                        return
                except Exception:
                    if self.high_log:
                        self.high_log.write("[error] Machine is not homed. Please home first.")
                    return
                if not rest:
                    if self.high_log:
                        self.high_log.write("[error] paint requires <flow 0..1>")
                    return
                try:
                    flow = float(rest[0])
                except Exception:
                    if self.high_log:
                        self.high_log.write("[error] flow must be a number 0..1")
                    return
                flow = max(0.0, min(1.0, flow))
                if self.tool_manager:
                    self.tool_manager.set_paint_flow(flow, tool=None, wait=True)
                else:
                    # Fallback to legacy per-axis move
                    obs_tool = self.state.snapshot().get("observed", {}).get("raw_status", {}).get("raw", {}).get("tool")
                    tool_index = 0 if obs_tool is None else int(obs_tool)
                    axis = 'u' if tool_index == 0 else 'v'
                    from semantic_gcode.dict.gcode_commands.G1.G1 import G1_LinearMove
                    from semantic_gcode.dict.gcode_commands.M400.M400 import M400_WaitForMoves
                    params = {axis: flow}
                    g1 = G1_LinearMove.create(**params)
                    m400 = M400_WaitForMoves.create()
                    if self.dispatcher:
                        self.dispatcher.enqueue(g1); self.dispatcher.enqueue(m400)
                    else:
                        self.transport.send_line(str(g1)); self.transport.query(str(m400))
                # After issuing G1 U/V, update predictive position immediately
                tool_index = self._get_current_tool_index()
                axis = 'u' if tool_index == 0 else 'v'
                try:
                    flow = float(rest[0])
                    flow = max(0.0, min(1.0, flow))
                except Exception:
                    flow = None
                if flow is not None:
                    # Snapshot predictive, update position
                    snap_pred = self.state.snapshot().get("predictive", {})
                    pos = dict(snap_pred.get("position", {}))
                    pos[axis] = flow
                    # Merge via observed as we don't have direct setter for predictive; rely on G1.apply for future
                    # For immediate UI, just refresh status text; paint uses predictive accessor
                    self._update_status()
                return
            if cmd == "dot":
                # dot tool? p <0..1> x <num> y <num> z <num> ms <int>
                # Block if not homed
                try:
                    homed = self.state.snapshot().get("observed", {}).get("raw_status", {}).get("raw", {}).get("coords", {}).get("axesHomed") or []
                    if not (bool(int(homed[0])) and bool(int(homed[1])) and bool(int(homed[2]))):
                        if self.high_log:
                            self.high_log.write("[error] Machine is not homed. Please home first.")
                        return
                except Exception:
                    if self.high_log:
                        self.high_log.write("[error] Machine is not homed. Please home first.")
                    return
                # Flexible token parsing: accept pairs (k v) and compact forms like x100, y100, z60, ms100
                tokens = {}
                keys = ("tool","p","x","y","z","ms")
                i = 0
                while i < len(rest):
                    t = rest[i].strip()
                    tl = t.lower()
                    if tl in keys and i + 1 < len(rest):
                        tokens[tl] = rest[i+1]
                        i += 2
                        continue
                    # compact form detection
                    matched = False
                    for name in keys:
                        if tl.startswith(name) and len(tl) > len(name):
                            tokens[name] = t[len(name):]
                            matched = True
                            break
                    i += 1 if matched else 1
                tool_tok = tokens.get("tool")
                try:
                    flow = float(tokens.get("p",""))
                    x = float(tokens.get("x",""))
                    y = float(tokens.get("y",""))
                    z = float(tokens.get("z",""))
                    ms = int(tokens.get("ms",""))
                except Exception:
                    if self.high_log:
                        self.high_log.write("[error] dot requires: p <0..1> x <num> y <num> z <num> ms <int>")
                    return
                flow = max(0.0, min(1.0, flow))
                # Tool-managed sequence
                if self.tool_manager:
                    if tool_tok is not None:
                        self.tool_manager.switch_tool(tool_tok, wait=True)
                    self.tool_manager.set_air(True)
                    self.tool_manager.move_to(x, y, z=z, feedrate=24000, wait=True)
                    self.tool_manager.set_paint_flow(max(0.0, min(1.0, flow)), wait=True)
                    self.dispatcher.enqueue(G4_Dwell.create(p=ms))
                    self.tool_manager.stop_paint_flow(wait=True)
                    self.tool_manager.set_air(False)
                else:
                    # Fallback legacy path
                    from semantic_gcode.dict.gcode_commands.T.T import T_SelectTool
                    from semantic_gcode.dict.gcode_commands.M106.M106 import M106_FanControl
                    from semantic_gcode.dict.gcode_commands.G1.G1 import G1_LinearMove
                    from semantic_gcode.dict.gcode_commands.M400.M400 import M400_WaitForMoves
                    tool_index = 1 if (tool_tok or "0").lower() in ("1","b","white") else 0
                    fan_on = 2 if tool_index == 0 else 3
                    fan_other = 3 if tool_index == 0 else 2
                    axis = 'u' if tool_index == 0 else 'v'
                    seq = [
                        T_SelectTool.create(tool_number=tool_index),
                        M106_FanControl.create(p=fan_other, s=0.0),
                        M106_FanControl.create(p=fan_on, s=1.0),
                        G1_LinearMove.create(x=x, y=y, z=z),
                        G1_LinearMove.create(**{axis: flow}),
                        G4_Dwell.create(p=ms),
                        G1_LinearMove.create(**{axis: 0.0}),
                        M106_FanControl.create(p=fan_on, s=0.0),
                        M400_WaitForMoves.create(),
                    ]
                    for instr in seq:
                        self.dispatcher.enqueue(instr)
                return
            if cmd == "draw":
                # draw [params per commands.yaml]
                # Parse key/value pairs, allow bare tokens like 'tool' then value
                tokens = {}
                keys = ("tool","p","f","xs","ys","zs","xe","ye","ze","ps")
                i = 0
                while i < len(rest):
                    t = rest[i].strip()
                    tl = t.lower()
                    if tl in keys and i + 1 < len(rest):
                        tokens[tl] = rest[i+1]
                        i += 2
                        continue
                    # compact forms like f1000, xs0, ys0, z50 (maps to zs), xe200, ye0, ze10, ps.2
                    matched = False
                    # Special-case single 'z' to mean starting Z (zs)
                    if tl.startswith('z') and not tl.startswith('ze') and not tl.startswith('zs') and len(tl) > 1:
                        tokens['zs'] = t[1:]
                        matched = True
                    else:
                        for name in ("xs","ys","zs","xe","ye","ze","ps","f","p","tool"):
                            if tl.startswith(name) and len(tl) > len(name):
                                tokens[name] = t[len(name):]
                                matched = True
                                break
                    i += 1 if matched else 1
                # Defaults
                tool_tok = tokens.get("tool")
                try:
                    p = float(tokens.get("p", ""))
                except Exception:
                    if self.high_log:
                        self.high_log.write("[error] draw requires p <0..1> and xe/ye")
                    return
                ps = tokens.get("ps")
                ps_val = None
                if ps is not None:
                    try:
                        ps_val = float(ps)
                    except Exception:
                        ps_val = None
                xs = tokens.get("xs"); ys = tokens.get("ys"); zs = tokens.get("zs")
                xe = tokens.get("xe"); ye = tokens.get("ye"); ze = tokens.get("ze")
                f = tokens.get("f")
                if xe is None or ye is None:
                    if self.high_log:
                        self.high_log.write("[error] draw requires xe and ye")
                    return
                try:
                    xe_f = float(xe); ye_f = float(ye)
                    xs_f = float(xs) if xs is not None else None
                    ys_f = float(ys) if ys is not None else None
                    zs_f = float(zs) if zs is not None else None
                    ze_f = float(ze) if ze is not None else None
                    f_f = float(f) if f is not None else None
                except Exception:
                    if self.high_log:
                        self.high_log.write("[error] invalid numeric value in draw")
                    return
                if self.tool_manager:
                    if tool_tok is not None:
                        self.tool_manager.switch_tool(tool_tok, wait=True)
                    # Optional move to start
                    if xs_f is not None or ys_f is not None or zs_f is not None:
                        self.tool_manager.move_to(xs_f if xs_f is not None else self.tool_manager.get_logical_position()['x'],
                                                  ys_f if ys_f is not None else self.tool_manager.get_logical_position()['y'],
                                                  z=zs_f, feedrate=24000, wait=True)
                    # Air on, set initial flow
                    self.tool_manager.set_air(True)
                    self.tool_manager.set_paint_flow(max(0.0, min(1.0, p)), wait=True)
                    # Move to end
                    self.tool_manager.move_to(xe_f, ye_f, z=ze_f, feedrate=(f_f if f_f is not None else 3000), wait=True)
                    # Optional ending paint flow
                    if ps_val is not None:
                        self.tool_manager.set_paint_flow(max(0.0, min(1.0, ps_val)), wait=True)
                    # Stop paint and air off
                    self.tool_manager.stop_paint_flow(wait=True)
                    self.tool_manager.set_air(False)
                else:
                    # Fallback legacy behavior
                    from semantic_gcode.dict.gcode_commands.T.T import T_SelectTool
                    from semantic_gcode.dict.gcode_commands.M106.M106 import M106_FanControl
                    from semantic_gcode.dict.gcode_commands.G1.G1 import G1_LinearMove
                    from semantic_gcode.dict.gcode_commands.M400.M400 import M400_WaitForMoves
                    tool_index = 1 if (tool_tok or "0").lower() in ("1","b","white") else 0
                    fan_on = 2 if tool_index == 0 else 3
                    fan_other = 3 if tool_index == 0 else 2
                    axis = 'u' if tool_index == 0 else 'v'
                    seq = []
                    seq.append(T_SelectTool.create(tool_number=tool_index))
                    if xs_f is not None or ys_f is not None or zs_f is not None:
                        seq.append(G1_LinearMove.create(x=xs_f, y=ys_f, z=zs_f))
                    seq.append(M106_FanControl.create(p=fan_other, s=0.0))
                    seq.append(M106_FanControl.create(p=fan_on, s=1.0))
                    seq.append(G1_LinearMove.create(**{axis: max(0.0, min(1.0, p))}))
                    params = {"x": xe_f, "y": ye_f}
                    if ze_f is not None:
                        params["z"] = ze_f
                    if f_f is not None:
                        params["feedrate"] = f_f
                    seq.append(G1_LinearMove.create(**params))
                    if ps_val is not None:
                        seq.append(G1_LinearMove.create(**{axis: max(0.0, min(1.0, ps_val))}))
                    seq.append(G1_LinearMove.create(**{axis: 0.0}))
                    seq.append(M106_FanControl.create(p=fan_on, s=0.0))
                    seq.append(M400_WaitForMoves.create())
                    for instr in seq:
                        self.dispatcher.enqueue(instr)
                return
            if cmd == "ip":
                # Auto-connect to serial and query IP (M552)
                try:
                    # If not connected, attempt serial auto
                    if not self.transport or not self.transport.is_connected():
                        from realtime_hairbrush.cli.utils.port_selection import select_port_for_device
                        port = select_port_for_device("duet")
                        if not port:
                            if self.high_log:
                                self.high_log.write("[error] No Duet device found for IP query")
                            return
                        cfg = ConnectionConfig(transport_type="serial", serial_port=port, serial_baudrate=115200, timeout=5.0)
                        self.transport = AirbrushTransport(cfg)
                        if not self.transport.connect():
                            if self.high_log:
                                self.high_log.write(f"[error] connect failed: {self.transport.get_last_error()}")
                            return
                    # Try to read IP from current object model first
                    ip = None
                    try:
                        snap = self.state.snapshot().get("observed", {}).get("raw_status", {}).get("raw", {})
                        # Heuristic: find any IPv4-like value under 'network'
                        import re
                        def find_ipv4(obj):
                            if isinstance(obj, dict):
                                for v in obj.values():
                                    r = find_ipv4(v)
                                    if r:
                                        return r
                            elif isinstance(obj, list):
                                for v in obj:
                                    r = find_ipv4(v)
                                    if r:
                                        return r
                            elif isinstance(obj, str):
                                m = re.search(r"(\d{1,3}\.){3}\d{1,3}", obj)
                                if m:
                                    return m.group(0)
                            return None
                        ip = find_ipv4(snap.get("network"))
                    except Exception:
                        ip = None
                    # If not found, force one-shot status and try again
                    if not ip:
                        self._refresh_status_once()
                        try:
                            snap = self.state.snapshot().get("observed", {}).get("raw_status", {}).get("raw", {})
                            import re
                            def find_ipv4(obj):
                                if isinstance(obj, dict):
                                    for v in obj.values():
                                        r = find_ipv4(v)
                                        if r:
                                            return r
                                elif isinstance(obj, list):
                                    for v in obj:
                                        r = find_ipv4(v)
                                        if r:
                                            return r
                                elif isinstance(obj, str):
                                    m = re.search(r"(\d{1,3}\.){3}\d{1,3}", obj)
                                    if m:
                                        return m.group(0)
                                return None
                            ip = find_ipv4(snap.get("network"))
                        except Exception:
                            ip = None
                    # Query IP via M552 if still unknown
                    if not ip:
                        try:
                            from semantic_gcode.dict.gcode_commands.M552.M552 import M552_NetworkControl
                            m552 = M552_NetworkControl.create()
                            line = str(m552)
                        except Exception:
                            line = "M552"
                        if self.gcode_log:
                            self.gcode_log.write(escape(f"→ {line}"))
                        # Send and try to extract IP directly from immediate response
                        resp = self.transport.query(line)
                        if resp and self.gcode_log:
                            self.gcode_log.write(escape(f"← {resp.strip()}"))
                        # Direct regex extraction
                        import re as _re
                        m = _re.search(r"IP address\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)", resp or "")
                        if m:
                            ip = m.group(1)
                        # If not found, begin wait for an asynchronous IPv4 line via ReceivedEvent
                        if not ip:
                            self._ip_wait_active = True
                            self._ip_wait_result = None
                            try:
                                self._ip_wait_event.clear()
                            except Exception:
                                pass
                            try:
                                self._ip_wait_event.wait(8.0)
                            except Exception:
                                pass
                            if self._ip_wait_result:
                                ip = self._ip_wait_result
                            self._ip_wait_active = False
                            self._ip_wait_result = None
                    if self.high_log:
                        self.high_log.write(f"IP: {ip or 'unknown'}")
                except Exception as e:
                    if self.high_log:
                        self.high_log.write(f"[error] ip: {e}")
                return
            if cmd == "gcode":
                if not rest:
                    if self.high_log:
                        self.high_log.write("[error] gcode requires raw command text")
                    return
                raw = " ".join(rest)
                # Send raw line(s) split by ';' or comma
                lines = [seg.strip() for seg in raw.replace(',', ';').split(';') if seg.strip()]
                for line in lines:
                    if self.gcode_log:
                        self.gcode_log.write(escape(f"→ {line}"))
                    if self.dispatcher:
                        # Minimal: send via transport; dispatcher still logs
                        self.transport.send_line(line)
                    else:
                        self.transport.send_line(line)
                return
            if cmd == "status":
                # If async agent is enabled, request snapshot via agent and return
                if self._agent:
                    if not self.transport or not self.transport.is_connected():
                        if self.high_log:
                            self.high_log.write("[error] Not connected")
                        return
                    try:
                        self._agent.request_snapshot_now()
                        if self.high_log:
                            self.high_log.write("Requested status snapshot (agent)")
                    except Exception:
                        pass
                    return
                # Legacy direct M408 S2
                if not self.transport or not self.transport.is_connected():
                    if self.high_log:
                        self.high_log.write("[error] Not connected")
                    return
                line = "M408 S2"
                if self.gcode_log:
                    self.gcode_log.write(escape(f"→ {line}"))
                resp = self.transport.query(line)
                if resp:
                    if self.gcode_log:
                        self.gcode_log.write(escape(f"← {resp.strip()}"))
                    try:
                        import json
                        text_json = resp.strip()
                        if "{" in text_json and "}" in text_json:
                            text_json = text_json[text_json.find("{") : text_json.rfind("}") + 1]
                        data = json.loads(text_json)
                    except Exception:
                        data = {}
                    model = parse_object_model(data) if isinstance(data, dict) else {}
                    observed = {"firmware": {"status": data.get("status")},}
                    if model:
                        observed["object_model"] = model
                    self.state.update_observed(observed)
                    self._update_status()
                return
            if cmd == "estop":
                # Emergency stop/reset (M999). Warn that connection may reset.
                try:
                    from semantic_gcode.dict.gcode_commands.M999.M999 import M999_EmergencyStop
                    estop = M999_EmergencyStop.create()
                    line = str(estop)
                except Exception:
                    line = "M999"
                if self.gcode_log:
                    self.gcode_log.write(escape(f"→ {line}"))
                try:
                    # Use send_line instead of query; firmware may reset immediately
                    self.transport.send_line(line)
                except Exception as e:
                    if self.high_log:
                        self.high_log.write(f"[error] estop: {e}")
                # Immediately disconnect to prevent further commands hitting a rebooting board
                try:
                    if self.poller:
                        try:
                            self.poller.stop()
                        except Exception:
                            pass
                        self.poller = None
                    if self.dispatcher:
                        try:
                            stop = getattr(self.dispatcher, "stop", None)
                            if callable(stop):
                                stop()
                        except Exception:
                            pass
                        self.dispatcher = None
                    self._listener_attached = False
                    if self.transport and self.transport.is_connected():
                        try:
                            self.transport.disconnect()
                        except Exception:
                            pass
                    self.transport = None
                    self._last_status_ts = 0.0
                    if self.high_log:
                        self.high_log.write("E-Stop sent (M999). Disconnected immediately. Reconnect when ready.")
                    self.call_from_thread(self._update_status)
                finally:
                    return
            if self.high_log:
                self.high_log.write(f"[error] Unknown command: {cmd}")
        except Exception as e:
            if self.high_log:
                self.high_log.write(f"[error] {e}")

    def _handle_event(self, ev) -> None:
        # Always show raw G-code stream arrows, except suppress poller spam when verbose OFF
        try:
            from realtime_hairbrush.runtime.events import SentEvent, ReceivedEvent, AckEvent, ErrorEvent, StateUpdatedEvent
        except Exception:
            return
        if isinstance(ev, SentEvent):
            if self.gcode_log:
                line = (ev.line or "")
                self._last_sent_was_m408 = line.strip().startswith("M408")
                if (not self._verbose) and self._last_sent_was_m408:
                    return
                self.gcode_log.write(escape(f"→ {line}"))
            # If a motion or home command is sent, start a temporary fast refresh
            try:
                ln = (ev.line or "").strip()
                if ln.startswith("G1") or ln.startswith("G28"):
                    # Start/replace a 0.5s interval to refresh status while in motion (legacy)
                    if self._agent:
                        try:
                            self._agent.set_motion_state(True)
                        except Exception:
                            pass
                    else:
                        if self._motion_refresh_timer is not None:
                            try:
                                self._motion_refresh_timer.cancel()
                            except Exception:
                                pass
                        self._motion_refresh_timer = self.set_interval(0.25, self._refresh_coords_machine)
            except Exception:
                pass
            return
        if isinstance(ev, ReceivedEvent):
            if self.gcode_log:
                txt = (ev.line or "").strip()
                if not txt:
                    return
                # Fulfill one-shot IP wait if an IPv4 appears in a subsequent line
                if self._ip_wait_active:
                    try:
                        import re
                        m = re.search(r"(\d{1,3}\.){3}\d{1,3}", txt)
                        if m:
                            self._ip_wait_result = m.group(0)
                            try:
                                self._ip_wait_event.set()
                            except Exception:
                                pass
                    except Exception:
                        pass
                # Route firmware warnings/errors to the high-level pane, keep file logging separate
                low = txt.lower()
                if low.startswith("warning") or low.startswith("error"):
                    if self.high_log:
                        self.high_log.write(txt)
                    return
                # Suppress floody noise when verbose is OFF
                if (not self._verbose):
                    # Hide large JSON/object-model dumps
                    if (txt.startswith("{") or '"status"' in txt):
                        return
                    # Hide generic ok and legacy acc chatter
                    if low == 'ok' or low.startswith('ok ') or low.startswith('acc'):
                        return
                # Suppress 'ok' only for M408 when verbose is OFF
                if (not self._verbose) and self._last_sent_was_m408 and txt.lower() == 'ok':
                    return
                # If JSON substring exists, compress to one line
                if "{" in txt and "}" in txt:
                    try:
                        import json
                        js = txt[txt.find("{") : txt.rfind("}") + 1]
                        obj = json.loads(js)
                        compact = json.dumps(obj, separators=(",", ":"))
                        self.gcode_log.write(escape(f"← {compact}"))
                        return
                    except Exception:
                        pass
                self.gcode_log.write(escape(f"← {txt}"))
            return
        if isinstance(ev, AckEvent):
            instr = (ev.instruction or "").strip()
            if instr.startswith("M408"):
                self._update_status()
                self._last_status_ts = time.time()
                return
            # On M400 (end of motion), force a one-shot immediate status refresh and stop motion timer
            if instr.startswith("M400"):
                try:
                    if self._motion_refresh_timer is not None:
                        self._motion_refresh_timer.cancel()
                        self._motion_refresh_timer = None
                except Exception:
                    pass
                # Signal agent that motion ended
                if self._agent:
                    try:
                        self._agent.set_motion_state(False)
                    except Exception:
                        pass
                self._refresh_status_once()
                # Force an immediate update of homed and coords via rr_model
                self._force_status_refresh()
                self._last_status_ts = time.time()
                # Restore prior transport timeout after gated motion completes
                try:
                    if self._move_timeout_prev is not None:
                        self.transport.config.timeout = self._move_timeout_prev
                        self._move_timeout_prev = None
                except Exception:
                    pass
                # Do not return; fall through to log ack as usual
            # For all other acks (non-status commands), refresh only if agent is not active
            if (not self._agent) and instr and (not instr.startswith("M409")) and (not instr.startswith("M400")):
                try:
                    self._refresh_status_once()
                    self._last_status_ts = time.time()
                except Exception:
                    pass
            msg = "OK" if ev.ok else (ev.message or "Timeout")
            if self.high_log:
                self.high_log.write(f"Ack: {msg}")
            self._update_status()
            return
        if isinstance(ev, ErrorEvent):
            if self.high_log:
                self.high_log.write(f"[error] {ev.message}")
            return
        if isinstance(ev, StateUpdatedEvent):
            self._update_status()
            self._last_status_ts = time.time()
            return 

    def _refresh_coords_machine(self) -> None:
        # Latest-only, non-overlapping M409 K"coords.machine" refresh for live positions during motion
        if self._motion_refresh_inflight:
            return
        if not self.transport or not self.transport.is_connected():
            return
        self._motion_refresh_inflight = True
        try:
            start_ts = time.time()
            # Short per-request timeout (best-effort) to avoid late, bursty updates
            old_timeout = None
            try:
                old_timeout = getattr(self.transport.config, 'timeout', None)
                if old_timeout is not None and old_timeout > 0.8:
                    self.transport.config.timeout = 0.8
            except Exception:
                pass
            try:
                from semantic_gcode.dict.gcode_commands.M409.M409 import M409_QueryObjectModel
                cmd = M409_QueryObjectModel.create(path='move.axes[].machinePosition', s=2)
                resp = self.transport.query(str(cmd))
            except Exception:
                resp = self.transport.query('M409 K"move.axes[].machinePosition"')
            finally:
                # Restore timeout
                try:
                    if old_timeout is not None:
                        self.transport.config.timeout = old_timeout
                except Exception:
                    pass
            if not resp:
                return
            # Drop stale responses (arrived too late)
            if (time.time() - start_ts) > 1.0:
                return
            # Parse JSON and update only the coords.machine part of observed
            try:
                import json
                txt = resp.strip()
                if "{" in txt and "}" in txt:
                    txt = txt[txt.find("{") : txt.rfind("}") + 1]
                obj = json.loads(txt)
            except Exception:
                obj = {}
            result = obj.get('result') if isinstance(obj, dict) else None
            machine = result if isinstance(result, (list, tuple)) else None
            if isinstance(machine, (list, tuple)):
                # Debounce unchanged values (within a small epsilon)
                try:
                    if isinstance(self._last_machine_pos, (list, tuple)) and len(self._last_machine_pos) >= 3 and len(machine) >= 3:
                        eps = 1e-3
                        if (abs(float(machine[0]) - float(self._last_machine_pos[0])) < eps and
                            abs(float(machine[1]) - float(self._last_machine_pos[1])) < eps and
                            abs(float(machine[2]) - float(self._last_machine_pos[2])) < eps):
                            return
                except Exception:
                    pass
                # Merge minimally to the raw_status branch used by status bar
                self._merge_observed_patch({
                    'raw_status': {'raw': {'coords': {'machine': machine}}}
                })
                self._last_machine_pos = list(machine)
                self._last_status_ts = time.time()
        finally:
            self._motion_refresh_inflight = False 