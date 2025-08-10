"""
Connect commands for the Realtime Hairbrush CLI.

This module provides commands for connecting to the airbrush plotter.
"""

import click
from typing import Optional
import sys
import serial.tools.list_ports

from realtime_hairbrush.transport.airbrush_transport import AirbrushTransport
from realtime_hairbrush.transport.config import ConnectionConfig


@click.group()
def connect():
    """
    Connect to the airbrush plotter.
    """
    pass


@connect.command()
@click.option('--port', '-p', required=True, help='Serial port')
@click.option('--baudrate', '-b', default=115200, help='Baud rate')
@click.option('--timeout', '-t', default=5.0, help='Timeout in seconds')
@click.pass_context
def serial(ctx, port, baudrate, timeout):
    """
    Connect via serial port.
    """
    config = ConnectionConfig(
        transport_type="serial",
        serial_port=port,
        serial_baudrate=baudrate,
        timeout=timeout
    )
    
    transport = AirbrushTransport(config)
    
    click.echo(f"Connecting to serial port {port} at {baudrate} baud...")
    
    if transport.connect():
        click.echo("Connected successfully")
        # Save connection state for persistence
        AirbrushTransport.save_connection_state()
    else:
        click.echo(f"Connection failed: {transport.get_last_error()}")


@connect.command()
@click.option('--host', '-h', required=True, help='Duet Web Control host')
@click.option('--password', '-p', default=None, help='Password')
@click.option('--timeout', '-t', default=10.0, help='Timeout in seconds')
@click.pass_context
def http(ctx, host, password, timeout):
    """
    Connect via HTTP (Duet Web Control).
    """
    config = ConnectionConfig(
        transport_type="http",
        http_host=host,
        http_password=password,
        timeout=timeout
    )
    
    transport = AirbrushTransport(config)
    
    click.echo(f"Connecting to Duet Web Control at {host}...")
    
    if transport.connect():
        click.echo("Connected successfully")
        # Save connection state for persistence
        AirbrushTransport.save_connection_state()
    else:
        click.echo(f"Connection failed: {transport.get_last_error()}")


@connect.command()
@click.pass_context
def status(ctx):
    """
    Check connection status.
    """
    # Create a transport with empty config to check the global connection
    transport = AirbrushTransport(ConnectionConfig())
    
    if transport.is_connected():
        status = transport.get_status()
        click.echo("Connected")
        click.echo(f"Status: {status}")
    else:
        click.echo("Not connected")


@connect.command()
@click.pass_context
def disconnect(ctx):
    """
    Disconnect from the airbrush plotter.
    """
    # Create a transport with empty config to disconnect the global connection
    transport = AirbrushTransport(ConnectionConfig())
    
    if transport.is_connected():
        transport.disconnect()
        click.echo("Disconnected")
        # Remove connection state file
        AirbrushTransport.save_connection_state()
    else:
        click.echo("Not connected") 


@click.command()
@click.argument('device_type', required=False, default='duet')
@click.pass_context
def auto_connect(ctx, device_type):
    """
    Auto-connect to a device: auto_connect [duet|arduino]
    Scans all serial ports and baud rates for a Duet/RepRapFirmware board.
    """
    device_type = device_type.lower() if device_type else 'duet'
    click.echo(f"Scanning for {device_type} devices on available serial ports...")

    # Platform-specific port patterns
    if sys.platform.startswith('win'):
        port_patterns = ['COM%s' % i for i in range(1, 21)]
    elif sys.platform.startswith('darwin'):
        port_patterns = [
            '/dev/tty.usb*', '/dev/tty.SLAB_USBtoUART*', '/dev/tty.wchusbserial*', '/dev/tty.Bluetooth*', '/dev/tty.*'
        ]
    else:
        port_patterns = ['/dev/ttyACM*', '/dev/ttyUSB*', '/dev/ttyS*']

    # List all ports
    all_ports = set()
    for portinfo in serial.tools.list_ports.comports():
        all_ports.add(portinfo.device)
    # Add globbed ports for macOS/Linux
    import glob
    for pattern in port_patterns:
        for port in glob.glob(pattern):
            all_ports.add(port)
    all_ports = sorted(all_ports)

    if not all_ports:
        click.echo("No serial ports found.")
        return

    # Baud rates to try (highest to lowest)
    baud_rates = [250000, 230400, 115200, 57600, 38400, 19200, 9600]

    found = False
    for port in all_ports:
        for baud in baud_rates:
            click.echo(f"Trying {port} @ {baud}...")
            try:
                ser = serial.Serial(port, baudrate=baud, timeout=2)
                ser.reset_input_buffer()
                import time
                # Try both line endings and both commands
                responses = []
                for cmd in [b'M115\n', b'M115\r\n', b'M552\n', b'M552\r\n']:
                    ser.write(cmd)
                    ser.flush()
                    time.sleep(0.3)  # Give the board a moment to respond
                    # Read up to 3 lines
                    for _ in range(3):
                        line = ser.readline().decode(errors='ignore').strip()
                        if line:
                            responses.append(line)
                ser.close()
                # Print all responses for debugging
                for resp in responses:
                    click.echo(f"  Response: {resp}")
                # Flexible detection: look for key substrings in any response
                detected = False
                for resp in responses:
                    if any(s in resp.lower() for s in ["reprapfirmware", "duet", "firmware_name"]):
                        detected = True
                        break
                if detected:
                    click.echo(f"Duet/RepRapFirmware board detected on {port} @ {baud}!")
                    from realtime_hairbrush.transport.config import ConnectionConfig
                    from realtime_hairbrush.transport.airbrush_transport import AirbrushTransport
                    config = ConnectionConfig(
                        transport_type="serial",
                        serial_port=port,
                        serial_baudrate=baud,
                        timeout=5.0
                    )
                    transport = AirbrushTransport(config)
                    if transport.connect():
                        click.echo(f"Connected to Duet on {port} @ {baud}.")
                        ctx.obj['transport'] = transport
                        found = True
                        return
                    else:
                        click.echo(f"Failed to connect to {port} @ {baud} after detection.")
            except Exception as e:
                click.echo(f"  Exception: {e}")
                pass
    if not found:
        click.echo("No Duet/RepRapFirmware device found on any port/baud rate.")
        click.echo(f"Ports tried: {', '.join(all_ports)}")


@click.command()
@click.pass_context
def get_ip_serial(ctx):
    """
    Query the board's IP address via serial (M552).
    """
    transport = ctx.obj.get('transport')
    if not transport or transport.config.transport_type != 'serial' or not transport.is_connected():
        click.echo("Error: You must be connected to the board via serial to use this command.")
        click.echo("Use 'connect_serial <port> [baudrate]' to connect first.")
        return
    click.echo("Querying IP address via serial (M552)...")
    response = transport.query("M552")
    if not response:
        click.echo("No response from board. Make sure the board is powered and connected via serial.")
        return
    # Try to extract the IP address from the response
    import re
    match = re.search(r'IP address ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', response)
    if match:
        ip = match.group(1)
        click.echo(f"Board IP address: {ip}")
    else:
        click.echo(f"Response: {response.strip()}")

__all__ = ["connect", "get_ip_serial", "auto_connect"] 