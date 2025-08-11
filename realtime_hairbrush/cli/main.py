"""
Main CLI entry point for the Realtime Hairbrush SDK.

This module provides the main CLI entry point and command groups.
"""

import click
import sys
import os

from realtime_hairbrush.transport.airbrush_transport import AirbrushTransport
from realtime_hairbrush.transport.config import ConnectionConfig
from realtime_hairbrush.config.manager import ConfigManager
from realtime_hairbrush.runtime import Dispatcher, MachineState
from realtime_hairbrush.runtime.events import SentEvent, ReceivedEvent, AckEvent, ErrorEvent, StateUpdatedEvent
from realtime_hairbrush.runtime.readers import StatusPoller

from realtime_hairbrush import __version__


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="airbrush")
@click.option('--config', '-c', help='Path to configuration file')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, config, verbose):
    """
    Realtime Hairbrush SDK - default launches the TUI.

    Subcommands are still available for advanced use.
    """
    # Initialize the context object
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['config_file'] = config
    ctx.obj['config_manager'] = ConfigManager(config_file=config)

    if verbose:
        click.echo(f"Realtime Hairbrush SDK v{__version__}")
        click.echo(f"Using configuration file: {config or 'default'}")

    # If no subcommand provided, launch the Textual TUI by default
    if ctx.invoked_subcommand is None:
        from realtime_hairbrush.ui.textual_app import AirbrushTextualApp
        transport: AirbrushTransport = ctx.obj.get('transport')
        dispatcher = ctx.obj.get('dispatcher')
        state = MachineState()
        if transport and not dispatcher:
            dispatcher = Dispatcher(transport, state)
            dispatcher.start()
        AirbrushTextualApp(transport, dispatcher, state).run()


# Import command groups
from realtime_hairbrush.cli.commands.connect import connect, get_ip_serial
from realtime_hairbrush.cli.commands.config import config_cmd
from realtime_hairbrush.cli.commands.manual import manual
from realtime_hairbrush.cli.commands.sequence import sequence
from realtime_hairbrush.cli.commands.stroke import stroke

# Add command groups
cli.add_command(connect)
cli.add_command(get_ip_serial)
cli.add_command(config_cmd)
cli.add_command(manual)
cli.add_command(sequence)
cli.add_command(stroke)


@cli.command()
@click.pass_context
def interactive(ctx):
    """
    Start interactive mode.
    """
    # Use the standalone interactive runner which wires connect handlers
    # and the runtime Dispatcher/StatusPoller.
    run_standalone_interactive()


@cli.command()
@click.pass_context
def tui(ctx):
    """Launch the full-screen TUI.

    Layout:
      - Top: 3-line status (Status/ToolPos/Coord; Tool/Air/Paint/Limits; System connection & temps)
      - Middle: High-level messages (abstracted confirmations)
      - Third: Raw G-code stream (→/←)
      - Bottom: Input line
    """
    from realtime_hairbrush.ui.app import AirbrushTUI
    transport: AirbrushTransport = ctx.obj.get('transport')
    dispatcher = ctx.obj.get('dispatcher')
    state = MachineState()
    if transport and not dispatcher:
        dispatcher = Dispatcher(transport, state)
        dispatcher.start()
    app = AirbrushTUI(transport, dispatcher, state)
    app.run()


@cli.command(name="tui-prompt")
@click.pass_context
def tui_prompt(ctx):
    """Launch the prompt-session TUI (more reliable on Windows/WSL)."""
    from realtime_hairbrush.ui.prompt_app import AirbrushPromptUI
    transport: AirbrushTransport = ctx.obj.get('transport')
    dispatcher = ctx.obj.get('dispatcher')
    state = MachineState()
    if transport and not dispatcher:
        dispatcher = Dispatcher(transport, state)
        dispatcher.start()
    AirbrushPromptUI(transport, dispatcher, state).run()


@cli.command(name="tui-textual")
@click.pass_context
def tui_textual(ctx):
    """Launch the Textual-based TUI (cross-platform, Rich-powered)."""
    from realtime_hairbrush.ui.textual_app import AirbrushTextualApp
    transport: AirbrushTransport = ctx.obj.get('transport')
    dispatcher = ctx.obj.get('dispatcher')
    state = MachineState()
    if transport and not dispatcher:
        dispatcher = Dispatcher(transport, state)
        dispatcher.start()
    AirbrushTextualApp(transport, dispatcher, state).run()


def main():
    """
    Entry point function for the CLI.
    This function is referenced in pyproject.toml as the entry point.
    """
    # Debug output to stderr
    print(f"DEBUG: main() entry point called with args: {sys.argv}", file=sys.stderr)
    sys.stderr.flush()

    # When running as a script, use the basename of the script as argv[0]
    # to avoid the "found in sys.modules" warning
    if sys.argv[0].endswith('.py'):
        sys.argv[0] = os.path.basename(sys.argv[0])

    try:
        return cli(auto_envvar_prefix='AIRBRUSH')
    except Exception as e:
        print(f"ERROR: Exception in main(): {e}", file=sys.stderr)
        sys.stderr.flush()
        raise


def run_standalone_interactive():
    """
    Run the interactive shell as a standalone application.
    This provides a persistent environment for controlling the airbrush plotter.
    """
    # Create a context object
    ctx = click.Context(cli)
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = True
    ctx.obj['config_file'] = None
    ctx.obj['config_manager'] = ConfigManager()

    # Start the interactive shell
    shell = AirbrushShell(ctx)
    # Runtime state holders
    runtime_state = MachineState()
    runtime_dispatcher = None
    runtime_poller = None

    # Load commands.yaml to check which commands to register
    import os
    from realtime_hairbrush.cli.utils.command_parser import parse_commands_yaml
    yaml_path = os.path.join(os.path.dirname(__file__), '..', 'commands.yaml')
    yaml_commands = parse_commands_yaml(yaml_path)
    yaml_command_names = set(yaml_commands.keys())

    # Define a consolidated connect handler that can handle both serial and HTTP
    def do_connect(arg):
        """
        Connect to the Duet board via serial or HTTP.
        Usage: connect [transport] [port/ip] [baud]
        """
        args = arg.split()

        # Default values
        transport_type = "http"  # Default to HTTP if nothing specified
        port = "auto"
        baudrate = "auto"
        ip_address = "last"

        # Get last used settings from config
        last_transport = None
        last_port = None
        last_baudrate = None
        last_ip = None

        if shell.config_manager:
            connection_config = shell.config_manager.get_connection_config()
            if connection_config:
                # Access attributes directly instead of using get method
                last_transport = connection_config.transport_type
                last_port = connection_config.serial_port
                last_baudrate = connection_config.serial_baudrate
                last_ip = connection_config.http_host

        # Parse arguments based on the YAML definition
        if len(args) == 0:
            # No args, use defaults
            pass
        elif len(args) == 1:
            # One arg could be: transport type, IP address, port name, or "last"
            arg0 = args[0].lower()
            if arg0 in ["serial", "http"]:
                transport_type = arg0
            elif arg0 == "last":
                if last_transport:
                    transport_type = last_transport
                    port = "last"
                    baudrate = "last"
                    ip_address = "last"
                else:
                    click.echo("No last connection settings found.")
                    return
            elif arg0.startswith(("com", "/dev/tty", "/dev/cu")):
                # Looks like a port name
                transport_type = "serial"
                port = arg0
            else:
                # Assume it's an IP address
                transport_type = "http"
                ip_address = arg0
        elif len(args) >= 2:
            # Two or more args
            arg0 = args[0].lower()
            arg1 = args[1].lower()

            if arg0 in ["serial", "http"]:
                transport_type = arg0
                if transport_type == "serial":
                    port = arg1
                    if len(args) > 2:
                        baudrate = args[2]
                else:  # HTTP
                    ip_address = arg1
            else:
                # First arg is not a transport type, assume serial port + baud
                transport_type = "serial"
                port = arg0
                baudrate = arg1

        # Handle 'last' and 'auto' values
        if transport_type == "serial":
            if port == "last" and last_port:
                port = last_port
            if baudrate == "last" and last_baudrate:
                baudrate = last_baudrate
            elif baudrate == "auto":
                baudrate = 115200  # Default to highest common baud rate

            # Handle auto port selection
            if port == "auto":
                from realtime_hairbrush.cli.utils.port_selection import select_port_for_device
                click.echo("Scanning for Duet devices...")
                auto_port = select_port_for_device("duet")
                if auto_port:
                    port = auto_port
                    click.echo(f"Found Duet device at {port}")
                else:
                    click.echo("No Duet devices found. Please specify a port manually.")
                    return
        else:  # HTTP
            if ip_address == "last" and last_ip:
                ip_address = last_ip

        # Create connection config
        if transport_type == "serial":
            try:
                if isinstance(baudrate, str) and baudrate != "auto":
                    baudrate = int(baudrate)
            except ValueError:
                click.echo(f"Invalid baud rate: {baudrate}, using default: 115200")
                baudrate = 115200

            config = ConnectionConfig(
                transport_type="serial",
                serial_port=port,
                serial_baudrate=baudrate,
                timeout=5.0
            )
            click.echo(f"Connecting to serial port {port} at {baudrate} baud...")
        else:
            config = ConnectionConfig(
                transport_type="http",
                http_host=ip_address,
                timeout=10.0
            )
            click.echo(f"Connecting to Duet Web Control at {ip_address}...")

        # Create transport and connect
        transport = AirbrushTransport(config)
        if transport.connect():
            click.echo("Connected successfully")
            shell.transport = transport
            ctx.obj['transport'] = transport
            # Bootstrap runtime dispatcher and poller if not started
            nonlocal runtime_dispatcher, runtime_poller
            if runtime_dispatcher is None:
                runtime_dispatcher = Dispatcher(transport, runtime_state)

                def _print_event(ev):
                    if isinstance(ev, SentEvent):
                        click.echo(f"→ {ev.line}")
                    elif isinstance(ev, ReceivedEvent):
                        # Collapse newlines and filter noisy JSON/object-model dumps
                        txt = ev.line.strip()
                        if not txt:
                            return
                        # Skip large JSON payloads from HTTP/object model
                        if txt.startswith('{') or txt.startswith('[') or '"status"' in txt:
                            return
                        # Show warnings/errors and short responses
                        if txt.lower().startswith('warning') or txt.lower().startswith('error') or len(txt) <= 120:
                            click.echo(f"← {txt}")
                    elif isinstance(ev, AckEvent):
                        status = "ok" if ev.ok else "timeout"
                        click.echo(f"[ack] {status}: {ev.instruction}")
                    elif isinstance(ev, ErrorEvent):
                        click.echo(f"[error] {ev.message}")
                    elif isinstance(ev, StateUpdatedEvent):
                        # Very compact status indicator
                        st = ev.state.get("observed", {}).get("firmware", {}).get("status")
                        if st:
                            label = {
                                "I": "Idle",
                                "B": "Busy",
                                "P": "Printing",
                                "H": "Homing",
                                "S": "Stopped",
                                # fallbacks for lowercase or words
                                "i": "Idle",
                                "busy": "Busy",
                                "idle": "Idle",
                            }.get(st, str(st))
                            click.echo(f"[status] {label}")

                runtime_dispatcher.on_event(_print_event)
                runtime_dispatcher.start()
                # Make available to shell
                ctx.obj['dispatcher'] = runtime_dispatcher
                # Attach to current shell instance so commands use it
                try:
                    shell.dispatcher = runtime_dispatcher
                except Exception:
                    pass

            if runtime_poller is None:
                runtime_poller = StatusPoller(transport, runtime_state, emit=runtime_dispatcher._emit, interval=0.5)
                runtime_poller.start()

            # Save connection settings for 'last' option
            if shell.config_manager:
                connection_settings = {
                    'transport_type': transport_type,
                    'serial_port': port if transport_type == "serial" else None,
                    'serial_baudrate': baudrate if transport_type == "serial" else None,
                    'http_host': ip_address if transport_type == "http" else None
                }
                shell.config_manager.save_connection_config(connection_settings)
        else:
            click.echo(f"Connection failed: {transport.get_last_error()}")

    def do_status(arg):
        """Show connection status and get IP address."""
        if not shell.transport:
            click.echo("Not connected")
            return

        if shell.transport.is_connected():
            status = shell.transport.get_status()
            click.echo("Connected")
            click.echo(f"Transport type: {shell.transport.config.transport_type}")
            if shell.transport.config.transport_type == "serial":
                click.echo(f"Serial port: {shell.transport.config.serial_port}")
                click.echo(f"Baud rate: {shell.transport.config.serial_baudrate}")

                # If this is the 'ip' command, query the IP address
                if arg == 'ip':
                    click.echo("Querying IP address via serial (M552)...")
                    response = shell.transport.query("M552")
                    if not response:
                        click.echo("No response from board. Make sure the board is powered and connected via serial.")
                        return
                    import re
                    match = re.search(r'IP address ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', response)
                    if match:
                        ip = match.group(1)
                        click.echo(f"Board IP address: {ip}")
                    else:
                        click.echo(f"Response: {response.strip()}")
            else:
                click.echo(f"Host: {shell.transport.config.http_host}")

            # Display additional status information
            if ctx.obj.get('verbose'):
                click.echo("Status details:")
                for key, value in status.items():
                    click.echo(f"  {key}: {value}")

            # Display current tool
            click.echo(f"Current tool: {shell.current_tool}")
        else:
            click.echo("Not connected")

    def do_ip(arg):
        """Automatically connect to serial and query the board's IP address."""
        from realtime_hairbrush.cli.utils.port_selection import select_port_for_device

        # If already connected via serial, just query the IP
        if shell.transport and shell.transport.is_connected() and shell.transport.config.transport_type == 'serial':
            # Already connected, just query the IP
            pass
        else:
            # Not connected via serial, try to connect silently
            try:
                # Try to find a Duet board without printing detection messages
                port = select_port_for_device("duet")
                if not port:
                    click.echo("No Duet device found. Please connect manually using 'connect serial <port>'.")
                    return

                # Use the selected port to connect
                baudrate = 115200  # Default baud rate

                config = ConnectionConfig(
                    transport_type="serial",
                    serial_port=port,
                    serial_baudrate=baudrate,
                    timeout=5.0
                )

                transport = AirbrushTransport(config)

                if not transport.connect():
                    click.echo(f"Connection failed: {transport.get_last_error()}")
                    return

                # Store the transport for future use
                shell.transport = transport
                ctx.obj['transport'] = transport
            except Exception as e:
                click.echo(f"Error connecting: {e}")
                return

        # Now we should be connected via serial, issue M552
        try:
            # Try to import and use the proper M552 implementation
            from semantic_gcode.dict.gcode_commands.M552.M552 import M552_NetworkControl

            # Create and execute the M552 command
            m552_cmd = M552_NetworkControl.create()

            # Send the command and get the response
            response = shell.transport.query(str(m552_cmd))

            if not response:
                click.echo("No response from board. Make sure the board is powered and connected.")
                return

            # Use the command's extract_ip_address method to get the IP
            ip_address = m552_cmd.extract_ip_address(response)

            if ip_address:
                click.echo(f"Board IP address: {ip_address}")
            else:
                click.echo(f"Could not find IP address in response: {response.strip()}")

        except ImportError:
            # Fall back to manual regex extraction if M552 implementation is not available
            response = shell.transport.query("M552")

            if not response:
                click.echo("No response from board. Make sure the board is powered and connected.")
                return

            import re
            match = re.search(r'IP address ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', response)
            if match:
                ip = match.group(1)
                click.echo(f"Board IP address: {ip}")
            else:
                click.echo(f"Could not find IP address in response: {response.strip()}")
        except Exception as e:
            click.echo(f"Error querying IP address: {e}")
            return

    def do_disconnect(arg):
        """
        Disconnect from the current connection.
        """
        if not shell.transport or not shell.transport.is_connected():
            click.echo("Not connected")
            return

        transport_type = shell.transport.config.transport_type
        if transport_type == "serial":
            click.echo(f"Disconnecting from serial port {shell.transport.config.serial_port}...")
        else:
            click.echo(f"Disconnecting from {shell.transport.config.http_host}...")

        if shell.transport.disconnect():
            click.echo("Disconnected successfully")
            shell.transport = None
            ctx.obj['transport'] = None
            # Stop runtime threads if running
            nonlocal runtime_dispatcher, runtime_poller
            try:
                if runtime_poller:
                    runtime_poller.stop()
                    runtime_poller = None
                if runtime_dispatcher:
                    runtime_dispatcher.stop()
                    runtime_dispatcher = None
                    # Detach from shell
                    try:
                        shell.dispatcher = None
                    except Exception:
                        pass
            except Exception:
                pass
        else:
            click.echo(f"Disconnection failed: {shell.transport.get_last_error()}")

    # Define command handlers
    connection_handlers = {
        'connect': do_connect,
        'ip': do_ip,
        'disconnect': do_disconnect
    }

    # Register only commands that are in the YAML file
    for cmd_name, handler in connection_handlers.items():
        if cmd_name in yaml_command_names:
            purpose = yaml_commands.get(cmd_name, {}).get('purpose', handler.__doc__)
            shell.register_command(cmd_name, handler, purpose)

    # Display welcome message
    click.echo(f"Realtime Hairbrush SDK v{__version__} - Interactive Control")
    click.echo("Type 'help' or '?' to list commands.")

    # Show hints for important commands that are in the YAML file
    if 'connect' in yaml_command_names:
        click.echo("Use 'connect serial' to connect to a serial port")
        click.echo("Use 'connect 192.168.1.x' to connect via HTTP")
    if 'ip' in yaml_command_names:
        click.echo("Use 'ip' to get the board's IP address via serial")

    # Start the shell
    shell.cmdloop()

# When run as a module (python -m realtime_hairbrush.cli.main)
if __name__ == "__main__" or __name__ == "realtime_hairbrush.cli.main":
    # Check if the first argument is 'interactive-shell'
    if len(sys.argv) > 1 and sys.argv[1] == 'interactive-shell':
        # Remove the 'interactive-shell' argument
        sys.argv.pop(1)
        # Run the standalone interactive shell
        run_standalone_interactive()
    else:
        # Fix for the runpy warning when running as a module
        module_name = os.path.basename(sys.argv[0])
        if module_name.endswith('.py'):
            module_name = module_name[:-3]
        sys.argv[0] = module_name

        sys.exit(main()) 