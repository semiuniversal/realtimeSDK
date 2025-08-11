from __future__ import annotations

from typing import Optional
import threading

from textual import events
from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Input, Footer, RichLog
from rich.markup import escape

from realtime_hairbrush.runtime import Dispatcher, MachineState
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


class AirbrushTextualApp(App):
    CSS = """
    #status {
        background: #1f3b7a; /* deep blue */
        color: white;
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
        # Command history
        self._history: list[str] = []
        self._hist_pos: Optional[int] = None
        self._commands = [
            "help","connect","disconnect","home","move","tool",
            "air","paint","dot","draw","ip","gcode","settings","status","verbose","exit","quit"
        ]

        # Widgets
        self.status_widget: Optional[Static] = None
        self.high_log: Optional[RichLog] = None
        self.gcode_log: Optional[RichLog] = None
        self.input_widget: Optional[Input] = None

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
        if self.transport and self.transport.is_connected() and not self.poller:
            # Global poll interval: slower (2.0s) to reduce contention on all transports
            poll_interval = 2.0
            self.poller = StatusPoller(self.transport, self.state, emit=self._emit_event_safe, interval=poll_interval)
            self.poller.start()
        # force an immediate status render tick while first poll is in-flight
        self._update_status()
        self.set_interval(0.5, self._update_status)

    def on_unmount(self) -> None:
        if self.poller:
            try:
                self.poller.stop()
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

    def _update_status(self) -> None:
        if self.status_widget:
            self.status_widget.update(self._status_block_text())

    def _refresh_status_once(self) -> None:
        if not self.transport or not self.transport.is_connected():
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
        except Exception:
            pass

    def _merge_observed_patch(self, patch: dict) -> None:
        snap = self.state.snapshot().get("observed", {})
        merged = dict(snap)
        # shallow merge top-level only; patch should reflect minimal raw_status keys
        for k, v in patch.items():
            if isinstance(v, dict) and isinstance(merged.get(k), dict):
                merged[k] = {**merged.get(k, {}), **v}
            else:
                merged[k] = v
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
        if self.transport:
            mode = self.transport.config.transport_type
            if mode == "serial":
                host = self.transport.config.serial_port or "-"
            elif mode == "http":
                host = self.transport.config.http_host or "-"
        obs = self.state.snapshot().get("observed", {})
        fw_status = obs.get("firmware", {}).get("status")
        label = {
            "I": "Idle",
            "B": "Busy",
            "P": "Printing",
            "H": "Homing",
            "S": "Stopped",
            "i": "Idle",
            "busy": "Busy",
            "idle": "Idle",
        }.get(fw_status, fw_status or "?")
        # Use live machine position for in-flight updates; xyz is the commanded/target position
        pos = (
            obs.get("raw_status", {}).get("raw", {}).get("coords", {}).get("machine")
            or obs.get("raw_status", {}).get("raw", {}).get("coords", {}).get("xyz")
            or obs.get("raw_status", {}).get("raw", {}).get("position")
        )
        def fmt(v):
            try:
                return f"{float(v):.3f}"
            except Exception:
                return "-"
        x = fmt(pos[0]) if isinstance(pos, (list, tuple)) and len(pos) >= 1 else "-"
        y = fmt(pos[1]) if isinstance(pos, (list, tuple)) and len(pos) >= 2 else "-"
        z = fmt(pos[2]) if isinstance(pos, (list, tuple)) and len(pos) >= 3 else "-"
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
        homed = obs.get("raw_status", {}).get("raw", {}).get("coords", {}).get("axesHomed") or []
        def flag(i):
            try:
                return "1" if int(homed[i]) else "0"
            except Exception:
                return "-"
        limits = f"[X:{flag(0)}] [Y:{flag(1)}] [Z:{flag(2)}] [U:{flag(3)}] [V:{flag(4)}]"
        diag = obs.get("diagnostics", {})
        # Try diagnostics; fall back to params.atxPower for VIN if present
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
        conn_label = f"Serial:{host}" if (mode == "serial") else (f"HTTP:{host}" if mode == "http" else "-:-")
        line1 = f"Status:{label} | ToolPos[X:{x}] [Y:{y}] [Z:{z}] | Coord:Absolute"
        line2 = f"Tool:{tool_str} | Air:{air_str} | Paint:{paint_str} | Limits:{limits}"
        line3 = f"System: [{conn_label}] [Vin {vin} V] [MCU Temp: {mcu_temp} C] [{driver_label}]"
        if ends_list:
            line3 += f" [Endstops: {ends_list}]"
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
                    self.high_log.write("Commands:")
                    for line in [
                        "  help",
                        "  connect serial <port> [baud]",
                        "  connect http <ip>",
                        "  disconnect",
                        "  home",
                        "  move x.. y.. [z..] [f..]",
                        "  tool N",
                        "  air [on|off] [tool]",
                        "  paint flow <0..1>",
                        "  dot ...",
                        "  draw ...",
                        "  ip",
                        "  gcode <raw>",
                        "  status",
                        "  verbose on|off",
                        "  exit | quit",
                    ]:
                        self.high_log.write(line)
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
                self.transport = AirbrushTransport(cfg)
                if not self.transport.connect():
                    if self.high_log:
                        self.high_log.write(f"[error] connect failed: {self.transport.get_last_error()}")
                    return
                # Create dispatcher/poller if needed
                if not self.dispatcher:
                    self.dispatcher = Dispatcher(self.transport, self.state)
                    self.dispatcher.on_event(lambda ev: self.call_from_thread(self._handle_event, ev))
                    self.dispatcher.start()
                if not self.poller:
                    self.poller = StatusPoller(self.transport, self.state, emit=self._emit_event_safe, interval=0.5)
                    self.poller.start()
                # Immediately fetch full status once on connect
                try:
                    self._refresh_status_once()
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
                if self.poller:
                    try:
                        self.poller.stop()
                    except Exception:
                        pass
                    self.poller = None
                if self.transport and self.transport.is_connected():
                    self.transport.disconnect()
                if self.high_log:
                    self.high_log.write("Disconnected")
                self.call_from_thread(self._update_status)
                return
            if not self.transport or not self.transport.is_connected():
                if self.high_log:
                    self.high_log.write("[error] Not connected")
                return
            if cmd == "home":
                from semantic_gcode.dict.gcode_commands.G28.G28 import G28_Home
                from semantic_gcode.dict.gcode_commands.M400.M400 import M400_WaitForMoves
                g28 = G28_Home.create(axes=None)
                m400 = M400_WaitForMoves.create()
                if self.dispatcher:
                    self.dispatcher.enqueue(g28)
                    self.dispatcher.enqueue(m400)
                else:
                    self.transport.send_line(str(g28))
                    self.transport.query(str(m400))
                return
            if cmd == "move":
                kv = {p[0].lower(): p[1:] for p in rest if len(p) >= 2 and p[0].lower() in ("x","y","z","f") and p[1:].replace('.', '', 1).replace('-', '', 1).isdigit()}
                x = float(kv['x']) if 'x' in kv else None
                y = float(kv['y']) if 'y' in kv else None
                z = float(kv['z']) if 'z' in kv else None
                f = float(kv['f']) if 'f' in kv else None
                if x is None and y is None and z is None:
                    if self.high_log:
                        self.high_log.write("[error] move requires at least one of x, y, z")
                    return
                from semantic_gcode.dict.gcode_commands.G1.G1 import G1_LinearMove
                params = {}
                if x is not None: params['x'] = x
                if y is not None: params['y'] = y
                if z is not None: params['z'] = z
                if f is not None: params['feedrate'] = f
                g1 = G1_LinearMove.create(**params)
                if self.dispatcher:
                    self.dispatcher.enqueue(g1)
                else:
                    self.transport.send_line(str(g1))
                # Do not immediately set predictive final pos in status bar; rely on observed polling
                return
            if cmd == "tool":
                if not rest:
                    if self.high_log:
                        self.high_log.write("[error] tool requires index")
                    return
                idx = int(rest[0])
                from semantic_gcode.dict.gcode_commands.T.T import T_SelectTool
                from semantic_gcode.dict.gcode_commands.M400.M400 import M400_WaitForMoves
                tsel = T_SelectTool.create(tool_number=idx)
                m400 = M400_WaitForMoves.create()
                if self.dispatcher:
                    self.dispatcher.enqueue(tsel); self.dispatcher.enqueue(m400)
                else:
                    self.transport.send_line(str(tsel)); self.transport.query(str(m400))
                # Immediate local update of tool index in observed state
                self._merge_observed_patch({"raw_status": {"raw": {"currentTool": idx}}})
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
                # default tool selection from observed state
                obs_tool = self.state.snapshot().get("observed", {}).get("raw_status", {}).get("raw", {}).get("tool")
                tool_index = 0 if obs_tool is None else int(obs_tool)
                if tool_arg in ("1","b","white"):
                    tool_index = 1
                fan_on = 2 if tool_index == 0 else 3
                fan_other = 3 if tool_index == 0 else 2
                from semantic_gcode.dict.gcode_commands.M106.M106 import M106_FanControl
                from semantic_gcode.dict.gcode_commands.M400.M400 import M400_WaitForMoves
                seq = []
                # Normalize state
                is_on = (state is None) or (state in ("on","1","true","yes"))
                is_off = (state in ("off","0","false","no"))
                if is_on:
                    # Enforce exclusivity: turn the other fan off, then this one on
                    seq.append(M106_FanControl.create(p=fan_other, s=0.0))
                    seq.append(M106_FanControl.create(p=fan_on, s=1.0))
                elif is_off:
                    # If no tool specified, turn off all air; else turn off selected only
                    if tool_arg is None:
                        seq.append(M106_FanControl.create(p=2, s=0.0))
                        seq.append(M106_FanControl.create(p=3, s=0.0))
                    else:
                        seq.append(M106_FanControl.create(p=fan_on, s=0.0))
                else:
                    if self.high_log:
                        self.high_log.write("[error] air: unknown state; use on/off")
                    return
                seq.append(M400_WaitForMoves.create())
                if self.dispatcher:
                    for instr in seq:
                        self.dispatcher.enqueue(instr)
                else:
                    for instr in seq:
                        s = str(instr)
                        if s.startswith("M400"):
                            self.transport.query(s)
                        else:
                            self.transport.send_line(s)
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
                # Determine tool -> axis
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
                tokens = {rest[i].lower(): rest[i+1] for i in range(0, len(rest)-1, 2) if rest[i].lower() in ("tool","p","x","y","z","ms")}
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
                # Determine tool and mapping
                tool_index = None
                if tool_tok is not None:
                    tool_index = 1 if tool_tok.lower() in ("1","b","white") else 0
                else:
                    obs_tool = self.state.snapshot().get("observed", {}).get("raw_status", {}).get("raw", {}).get("tool")
                    tool_index = 0 if obs_tool is None else int(obs_tool)
                fan_on = 2 if tool_index == 0 else 3
                fan_other = 3 if tool_index == 0 else 2
                axis = 'u' if tool_index == 0 else 'v'
                from semantic_gcode.dict.gcode_commands.T.T import T_SelectTool
                from semantic_gcode.dict.gcode_commands.M106.M106 import M106_FanControl
                from semantic_gcode.dict.gcode_commands.G1.G1 import G1_LinearMove
                from semantic_gcode.dict.gcode_commands.G4.G4 import G4_Dwell
                from semantic_gcode.dict.gcode_commands.M400.M400 import M400_WaitForMoves
                seq = []
                # Optional tool select
                seq.append(T_SelectTool.create(tool_number=tool_index))
                # Enforce exclusivity: turn off other, then turn on selected
                seq.append(M106_FanControl.create(p=fan_other, s=0.0))
                seq.append(M106_FanControl.create(p=fan_on, s=1.0))
                # Move to position
                seq.append(G1_LinearMove.create(x=x, y=y, z=z))
                # Set paint flow
                seq.append(G1_LinearMove.create(**{axis: flow}))
                # Dwell
                seq.append(G4_Dwell.create(p=ms))
                # Paint off
                seq.append(G1_LinearMove.create(**{axis: 0.0}))
                # Air off
                seq.append(M106_FanControl.create(p=fan_on, s=0.0))
                # Gate with M400 at end
                seq.append(M400_WaitForMoves.create())
                if self.dispatcher:
                    for instr in seq:
                        self.dispatcher.enqueue(instr)
                else:
                    for instr in seq:
                        s = str(instr)
                        if s.startswith("M400"):
                            self.transport.query(s)
                        else:
                            self.transport.send_line(s)
                return
            if cmd == "draw":
                # draw [params per commands.yaml]
                # Parse key/value pairs, allow bare tokens like 'tool' then value
                tokens = {}
                i = 0
                while i < len(rest) - 1:
                    key = rest[i].lower()
                    val = rest[i+1]
                    tokens[key] = val
                    i += 2
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
                # Determine tool and mapping
                if tool_tok is not None:
                    tool_index = 1 if tool_tok.lower() in ("1","b","white") else 0
                else:
                    obs_tool = self.state.snapshot().get("observed", {}).get("raw_status", {}).get("raw", {}).get("tool")
                    tool_index = 0 if obs_tool is None else int(obs_tool)
                fan_on = 2 if tool_index == 0 else 3
                fan_other = 3 if tool_index == 0 else 2
                axis = 'u' if tool_index == 0 else 'v'
                from semantic_gcode.dict.gcode_commands.T.T import T_SelectTool
                from semantic_gcode.dict.gcode_commands.M106.M106 import M106_FanControl
                from semantic_gcode.dict.gcode_commands.G1.G1 import G1_LinearMove
                from semantic_gcode.dict.gcode_commands.M400.M400 import M400_WaitForMoves
                seq = []
                # Tool select if needed
                seq.append(T_SelectTool.create(tool_number=tool_index))
                # Optional move to start
                if xs_f is not None or ys_f is not None or zs_f is not None:
                    seq.append(G1_LinearMove.create(x=xs_f, y=ys_f, z=zs_f))
                # Enforce exclusivity: other off, selected on
                seq.append(M106_FanControl.create(p=fan_other, s=0.0))
                seq.append(M106_FanControl.create(p=fan_on, s=1.0))
                # Set initial paint flow
                seq.append(G1_LinearMove.create(**{axis: max(0.0, min(1.0, p))}))
                # Move to end with optional feedrate
                params = {"x": xe_f, "y": ye_f}
                if ze_f is not None:
                    params["z"] = ze_f
                if f_f is not None:
                    params["feedrate"] = f_f
                seq.append(G1_LinearMove.create(**params))
                # Optional ending paint flow
                if ps_val is not None:
                    seq.append(G1_LinearMove.create(**{axis: max(0.0, min(1.0, ps_val))}))
                # Paint off and air off
                seq.append(G1_LinearMove.create(**{axis: 0.0}))
                seq.append(M106_FanControl.create(p=fan_on, s=0.0))
                # Gate
                seq.append(M400_WaitForMoves.create())
                if self.dispatcher:
                    for instr in seq:
                        self.dispatcher.enqueue(instr)
                else:
                    for instr in seq:
                        s = str(instr)
                        if s.startswith("M400"):
                            self.transport.query(s)
                        else:
                            self.transport.send_line(s)
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
                        # Send and wait for OK, then wait for the subsequent IPv4 line via ReceivedEvent
                        resp = self.transport.query(line)
                        if resp and self.gcode_log:
                            self.gcode_log.write(escape(f"← {resp.strip()}"))
                        # Begin wait for the asynchronous IPv4 line
                        self._ip_wait_active = True
                        self._ip_wait_result = None
                        try:
                            self._ip_wait_event.clear()
                        except Exception:
                            pass
                        # Wait up to 8 seconds for the IP line to appear
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
                # Send M408 S2, log arrows, parse and update
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
                # Suppress object-model JSON when verbose is OFF
                if (not self._verbose) and (txt.startswith("{") or '"status"' in txt):
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
                return
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
            return 