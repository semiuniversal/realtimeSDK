# Realtime Hairbrush SDK

A device-independent, real-time control SDK and Textual UI for G-code machines (focused on an airbrush plotter using RepRapFirmware). This guide explains how it works, how to install and run it, how to use the TUI, and how to integrate the SDK into a larger application.

---

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
  - [Setup](#setup)
  - [Launch the TUI](#launch-the-tui)
  - [Connect to Your Device](#connect-to-your-device)
- [Theory of Operation](#theory-of-operation)
  - [Architecture](#architecture)
  - [Event Flow](#event-flow)
  - [Status Polling (M408 S2)](#status-polling-m408-s2)
- [G-code Paradigm](#g-code-paradigm)
  - [Semantic Command Classes](#semantic-command-classes)
  - [Mixins (Behavior-by-Composition)](#mixins-behavior-by-composition)
  - [Dispatcher and Acknowledgements](#dispatcher-and-acknowledgements)
- [Using the Textual UI](#using-the-textual-ui)
  - [Layout](#layout)
  - [Built-in Commands](#built-in-commands)
  - [Status Details](#status-details)
- [Duet Web Control (DWC): Configuration and Macros](#duet-web-control-dwc-configuration-and-macros)
- [Integrating into a Larger Application](#integrating-into-a-larger-application)
  - [Embedding the Library (Recommended)](#embedding-the-library-recommended)
  - [Creating Your Own Application (Scaffold)](#creating-your-own-application-scaffold)
  - [Concurrency and Threading](#concurrency-and-threading)
  - [Optional REST Control Plane (Advanced)](#optional-rest-control-plane-advanced)
- [Hairbrush-Specific Notes](#hairbrush-specific-notes)
  - [Tool Offsets and T1 Behavior](#tool-offsets-and-t1-behavior)
  - [U/V Axis Dead Zone Mapping](#uv-axis-dead-zone-mapping)
- [Troubleshooting](#troubleshooting)
- [Project Layout](#project-layout)
- [License](#license)

---

## Overview

This SDK provides a robust, cross-platform Textual (Rich) TUI and a structured semantic G-code layer for building reliable, real-time control applications for G-code machines. It is geared toward an airbrush plotter running RepRapFirmware (Duet), but the abstractions generalize.

Key features:
- Cross-platform Textual UI with real-time status and TX/RX logs
- Clean separation of transport (serial/HTTP), dispatcher, and status polling
- Semantic G-code command classes (typed factories, mixins, parsing helpers)
- Straightforward integration into desktop/web/creative apps

---

## Quick Start

### Setup

Preferred (activation-free) workflow using uv:

- macOS/Linux:
  ```bash
  bash setup.sh
  uv run airbrush tui-textual
  ```
- Windows (PowerShell):
  ```powershell
  ./setup.ps1
  uv run airbrush tui-textual
  ```

The setup scripts use `uv sync` to create `.venv` and install dependencies. From then on, use `uv run` to execute commands without activating the virtual environment.

Alternative (manual):
- Standard venv + pip
  ```bash
  python -m venv .venv
  source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
  pip install -e .
  ```
- Manual uv steps
  ```bash
  uv venv
  # optional activation; you can skip and just use `uv run`
  source .venv/bin/activate
  uv pip install -e .
  ```

### Launch the TUI

```bash
uv run airbrush tui-textual
```

### Connect to Your Device

If you wish to use HTTP, first attach a USB cable for a serial connection. The serial link lets the app discover the machine’s IP address.

- Auto-detect serial (Windows/Duet): `connect serial auto`
- Specific serial port (examples): `connect serial COM9` (Windows) or `connect serial /dev/ttyACM0` (Linux)
- Get the IP address: `ip`
  - After your first successful HTTP connection, the SDK saves the IP in its settings so you can reuse it without a serial cable next time.
- Strong recommendation: Create a DHCP reservation for your device in your router. This prevents IP changes and eliminates serial lookups in daily use.
- Connect over HTTP (Duet Web Control): `connect http 192.168.x.x`

Try a few commands:
- `home`
- `move x100 y0`
- `tool 0`

Type `help` to list available commands.

---

## Theory of Operation

### Architecture

- Transport (`realtime_hairbrush/transport`): serial/HTTP connection and configuration
- Runtime (`realtime_hairbrush/runtime`):
  - Dispatcher: enqueues semantic commands, manages acknowledgements, emits events
  - StatusPoller: periodically issues `M408 S2`, updates `MachineState` on change
  - MachineState: deep-merges observed state so fields don’t reset on partial updates
- UI (`realtime_hairbrush/ui/textual_app.py`):
  - Top: multi-line status
  - Left: high-level messages (Home/Move OK)
  - Right: raw TX/RX stream with minified M408 JSON
  - Bottom: input line

### Event Flow

1) UI parses input → builds semantic commands → enqueues via Dispatcher
2) Dispatcher sends G-code over Transport and waits for ack (e.g., `M400` for motion)
3) StatusPoller issues `M408 S2` on a fixed interval (0.5–1.0s), parses object model, updates MachineState
4) UI listens to Dispatcher and Poller events and updates panes

### Status Polling (M408 S2)

- Uses `coords.machine` for live positions (target `coords.xyz` does not move)
- M408 JSON is displayed as a single, compact line in the right log

---

## G-code Paradigm

### Semantic Command Classes

- Located under `semantic_gcode/dict/gcode_commands/<CODE>/<CODE>.py`
- Decorated with `@register_gcode_instruction`
- Declare `code_type`, `code_number`, `valid_parameters`
- Provide `create(...)` factories and optional response parsers

### Mixins (Behavior-by-Composition)

- Add mixins (see `semantic_gcode/gcode/mixins.py`) for behaviors such as `ExpectsAcknowledgement`
- Mixins let commands advertise runtime expectations without hardcoding the dispatcher

### Dispatcher and Acknowledgements

- The dispatcher serializes operations
- Motion sequences typically enqueue `M400` to gate completion
- UI shows concise, high-level acks (e.g., “Move: OK”)

---

## Using the Textual UI

### Layout

- Top: 3-line status (Status, ToolPos, System)
- Middle left: high-level messages (Home/Move OK, errors)
- Middle right: raw TX/RX stream with minified M408 JSON
- Bottom: command input with history/completion

### Built-in Commands

- `help`
- `connect serial auto` | `connect serial <port> [baud]` | `connect http <ip>` | `disconnect`
- `home`
- `move x<mm> y<mm> [z<mm>] [f<mm/min>]`
- `tool <index>`
- `ip` (discover IP via serial)
- `status` (one-shot M408 S2)

### Status Details

- Live positions come from `coords.machine`
- Tool index from `currentTool`
- Air/paint indicators map to object model fields when available
- VIN/MCU/driver temps are available when diagnostics are enabled

---

## Duet Web Control (DWC): Configuration and Macros

DWC is the browser UI for RepRapFirmware. It allows you to inspect the machine, send G-code, edit startup files (e.g., `sys/config.g`), and manage macros.

Important:
- IP discovery: Use the serial path in this app to retrieve the IP (`ip`), then open DWC at `http://<ip>`
- Strongly recommended: Reserve a static IP (DHCP reservation) for your Duet in your router. This prevents IP changes and eliminates serial lookups in daily use.
- Safety/caution: The provided configuration and macros are pre-tuned. Changing limits, steps/mm, homing, tool offsets, or safety macros can cause dangerous motion. Backup first; validate with clearances.

References (Duet3D):
- Duet Web Control: https://docs.duet3d.com/User_manual/RepRapFirmware/Duet_Web_Control
- G-code dictionary: https://docs.duet3d.com/User_manual/RepRapFirmware/GCode
- Configuration: https://docs.duet3d.com/User_manual/RepRapFirmware/Configuration

---

## Integrating into a Larger Application

You may wish to embed this  SDK into a broader app (desktop UI, web app, or a creative coding tool). Below are recommended integration patterns.

### Embedding the Library (Recommended)

Initialize transport/dispatcher/state once, start the poller, and expose a tiny domain API:

```python
# app/driver.py
from realtime_hairbrush.transport.config import ConnectionConfig
from realtime_hairbrush.transport.airbrush_transport import AirbrushTransport
from realtime_hairbrush.runtime import Dispatcher, MachineState
from realtime_hairbrush.runtime.readers import StatusPoller
from realtime_hairbrush.runtime.events import StateUpdatedEvent
from semantic_gcode.dict.gcode_commands.G1.G1 import G1_LinearMove
from semantic_gcode.dict.gcode_commands.G28.G28 import G28_Home
from semantic_gcode.dict.gcode_commands.M400.M400 import M400_WaitForMoves

class HairbrushDriver:
    def __init__(self):
        self.transport = None
        self.dispatcher = None
        self.state = MachineState()
        self.poller = None

    def connect_serial(self, port, baud=115200):
        cfg = ConnectionConfig(transport_type="serial", serial_port=port, serial_baudrate=baud, timeout=5.0)
        self.transport = AirbrushTransport(cfg)
        if not self.transport.connect():
            raise RuntimeError(self.transport.get_last_error())
        self.dispatcher = Dispatcher(self.transport, self.state)
        self.dispatcher.start()
        self.poller = StatusPoller(self.transport, self.state, emit=self._on_event, interval=0.5)
        self.poller.start()

    def _on_event(self, ev):
        if isinstance(ev, StateUpdatedEvent):
            # forward to your app’s event bus or observers
            pass

    def home(self):
        self.dispatcher.enqueue(G28_Home.create(axes=None))
        self.dispatcher.enqueue(M400_WaitForMoves.create())

    def move_xy(self, x, y, feedrate=None):
        params = {"x": x, "y": y}
        if feedrate is not None:
            params["feedrate"] = feedrate
        self.dispatcher.enqueue(G1_LinearMove.create(**params))
        self.dispatcher.enqueue(M400_WaitForMoves.create())

    def disconnect(self):
        if self.poller:
            self.poller.stop()
        if self.transport and self.transport.is_connected():
            self.transport.disconnect()
```

### Creating Your Own Application (Scaffold)

A minimal script that connects, homes, and moves:

```python
from realtime_hairbrush.transport.config import ConnectionConfig
from realtime_hairbrush.transport.airbrush_transport import AirbrushTransport
from realtime_hairbrush.runtime import Dispatcher, MachineState
from realtime_hairbrush.runtime.readers import StatusPoller
from semantic_gcode.dict.gcode_commands.G28.G28 import G28_Home
from semantic_gcode.dict.gcode_commands.G1.G1 import G1_LinearMove
from semantic_gcode.dict.gcode_commands.M400.M400 import M400_WaitForMoves

state = MachineState()
cfg = ConnectionConfig(transport_type="serial", serial_port="COM9", serial_baudrate=115200, timeout=5.0)
transport = AirbrushTransport(cfg)
assert transport.connect(), transport.get_last_error()

dispatcher = Dispatcher(transport, state)
dispatcher.start()
poller = StatusPoller(transport, state, emit=lambda ev: None, interval=0.5)
poller.start()

dispatcher.enqueue(G28_Home.create(axes=None))
dispatcher.enqueue(M400_WaitForMoves.create())
dispatcher.enqueue(G1_LinearMove.create(x=100.0, y=0.0, feedrate=1200.0))
dispatcher.enqueue(M400_WaitForMoves.create())
```

### Concurrency and Threading

- Dispatcher and Poller run in background threads; enqueue safely from UI thread
- For asyncio apps, wrap blocking calls with `asyncio.to_thread` and post events back to the loop

### Optional REST Control Plane (Advanced)

For multi-process or cross-language control, a small REST server can help. For a single application, embedding the driver directly is simpler and avoids extra dependencies.

Pros:
- Decouples UI/client from the motion driver (multi-language, networkable)
- Simple automation over HTTP

Cons:
- Extra dependencies and process management
- Security hardening if exposed beyond localhost

Minimal example (FastAPI):

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from app.driver import HairbrushDriver

app = FastAPI()
driver = HairbrushDriver()

class ConnectSerial(BaseModel):
    port: str
    baud: int = 115200

class MoveXY(BaseModel):
    x: float
    y: float
    feedrate: float | None = None

@app.post("/connect/serial")
def connect_serial(body: ConnectSerial):
    try:
        driver.connect_serial(body.port, body.baud)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/home")
def home():
    driver.home()
    return {"enqueued": True}

@app.post("/move")
def move(body: MoveXY):
    driver.move_xy(body.x, body.y, body.feedrate)
    return {"enqueued": True}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

Security notes:
- Bind to localhost unless you implement auth
- Add a token header if exposing on LAN
- Clamp motion ranges, rate-limit requests, require homing before motion

---

## Hairbrush-Specific Notes

### Tool Offsets and T1 Behavior

- `T0` = Brush A (primary), `T1` = Brush B (secondary)
- `T1` typically relies on firmware `G10` tool offsets; some workflows temporarily disable soft limits (`M564 H0 S0`) for the first offset-applying move and then restore (`M564 H1 S1`). If you automate this, make it explicit and visible in logs.

### U/V Axis Dead Zone Mapping

- U/V range ~0–4 mm; bottom 20% (~0–0.8 mm) is a dead zone (off)
- To map normalized flow `f ∈ [0,1]` to mm: `mm = 4.0 * (0.2 + 0.8 * f)`

---

## Troubleshooting

- UI starts but Enter does nothing: ensure you’re using `tui-textual`
- No status updates: connect first; try `status` to force an M408 S2
- Excessive logs: keep diagnostics (M122/M119) disabled or run at long intervals
- Serial bandwidth: 0.5–1.0s polling is realistic; HTTP often tolerates faster polling
- Defaults flashing: state updates deep-merge; if issues persist, verify M408 parsing

---

## Project Layout

- `realtime_hairbrush/`
  - `cli/` command entrypoints (Textual UI launched via `tui-textual`)
  - `ui/` Textual app (`textual_app.py`)
  - `runtime/` dispatcher, status poller, machine state, events
  - `transport/` connection and config
  - `config/` settings manager and defaults
  - Optional: `instructions/`, `execution/` foundations for higher-level ops
- `semantic_gcode/`
  - `gcode/` base classes and mixins
  - `dict/gcode_commands/` semantic command classes (G1, G28, M400, M408, etc.)
  - `transport/`, `utils/`, `state/`, `controller/` supporting modules

---

## License

MIT License (see `pyproject.toml`). Use at your own risk. Validate motions in a safe test mode before running live operations.
