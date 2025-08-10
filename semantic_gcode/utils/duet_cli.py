"""
Command-line interface for Duet board configuration.

This module provides a command-line tool for configuring Duet boards,
particularly focused on network setup and board detection.
"""
import argparse
import sys
import time
import json
from typing import List, Dict, Any, Optional

from ..transport.serial import SerialTransport
from ..session.config_session import ConfigSession
from .duet_config import scan_for_duet_boards


def scan_command(args: argparse.Namespace) -> None:
    """
    Scan for Duet boards connected via serial.
    
    Args:
        args: Command-line arguments
    """
    print("Scanning for Duet boards...")
    boards = scan_for_duet_boards()
    
    if not boards:
        print("No Duet boards found")
        return
    
    print(f"Found {len(boards)} Duet board(s):")
    for i, (port, info) in enumerate(boards):
        print(f"{i+1}. {port}")
        if info:
            print(f"   Firmware: {info.get('firmware_name', 'unknown')} {info.get('firmware_version', 'unknown')}")
            print(f"   Board: {info.get('board_type', 'unknown')}")


def info_command(args: argparse.Namespace) -> None:
    """
    Get information about a Duet board.
    
    Args:
        args: Command-line arguments
    """
    port = args.port
    
    print(f"Connecting to {port}...")
    transport = SerialTransport(port, debug=args.debug)
    session = ConfigSession(transport, debug=args.debug)
    
    if not session.connect():
        print(f"Failed to connect to {port}")
        return
    
    if not session.is_duet_board():
        print(f"The device on {port} is not a Duet board")
        return
    
    print(f"Connected to Duet board on {port}")
    
    # Get board info
    board_info = session.get_board_info()
    print(f"Firmware: {board_info.get('firmware_name', 'unknown')} {board_info.get('firmware_version', 'unknown')}")
    print(f"Board: {board_info.get('board_type', 'unknown')}")
    
    # Get network status
    try:
        network_status = session.get_network_status()
        print("\nNetwork Status:")
        print(f"State: {network_status.get('state', 'unknown')}")
        if network_status.get('ip'):
            print(f"IP Address: {network_status.get('ip')}")
        if network_status.get('mac'):
            print(f"MAC Address: {network_status.get('mac')}")
    except Exception as e:
        print(f"Error getting network status: {e}")
    
    # Get diagnostics if requested
    if args.diagnostics:
        try:
            print("\nDiagnostics:")
            diagnostics = session.get_diagnostics()
            if "details" in diagnostics:
                print(diagnostics["details"])
        except Exception as e:
            print(f"Error getting diagnostics: {e}")
    
    # Disconnect
    session.disconnect()


def wifi_scan_command(args: argparse.Namespace) -> None:
    """
    Scan for available WiFi networks.
    
    Args:
        args: Command-line arguments
    """
    port = args.port
    
    print(f"Connecting to {port}...")
    transport = SerialTransport(port, debug=args.debug)
    session = ConfigSession(transport, debug=args.debug)
    
    if not session.connect():
        print(f"Failed to connect to {port}")
        return
    
    if not session.is_duet_board():
        print(f"The device on {port} is not a Duet board")
        session.disconnect()
        return
    
    print(f"Connected to Duet board on {port}")
    print("Scanning for WiFi networks...")
    
    try:
        networks = session.scan_wifi_networks(timeout=args.timeout)
        
        if not networks:
            print("No WiFi networks found")
        else:
            print(f"Found {len(networks)} WiFi network(s):")
            # Sort by signal strength (RSSI)
            networks.sort(key=lambda x: x.get('rssi', -100), reverse=True)
            
            for i, network in enumerate(networks):
                print(f"{i+1}. {network.get('ssid', 'unknown')} "
                      f"(Signal: {network.get('rssi', 'unknown')}dBm, "
                      f"Channel: {network.get('channel', 'unknown')}, "
                      f"Encryption: {network.get('encryption', 'unknown')})")
    except Exception as e:
        print(f"Error scanning for WiFi networks: {e}")
    
    # Disconnect
    session.disconnect()


def wifi_setup_command(args: argparse.Namespace) -> None:
    """
    Set up WiFi on a Duet board.
    
    Args:
        args: Command-line arguments
    """
    port = args.port
    ssid = args.ssid
    password = args.password
    
    if not ssid:
        print("SSID is required")
        return
    
    print(f"Connecting to {port}...")
    transport = SerialTransport(port, debug=args.debug)
    session = ConfigSession(transport, debug=args.debug)
    
    if not session.connect():
        print(f"Failed to connect to {port}")
        return
    
    if not session.is_duet_board():
        print(f"The device on {port} is not a Duet board")
        session.disconnect()
        return
    
    print(f"Connected to Duet board on {port}")
    print(f"Setting up WiFi for network '{ssid}'...")
    
    try:
        result = session.setup_wifi(ssid, password or "", wait_for_connection=True, timeout=args.timeout)
        
        if result["success"]:
            print(f"WiFi setup successful: {result['message']}")
            if result.get("ip_address"):
                print(f"IP Address: {result['ip_address']}")
                
                # Save IP address to file if requested
                if args.save_ip:
                    with open(args.save_ip, "w") as f:
                        f.write(result["ip_address"])
                    print(f"IP address saved to {args.save_ip}")
        else:
            print(f"WiFi setup failed: {result['message']}")
    except Exception as e:
        print(f"Error setting up WiFi: {e}")
    
    # Disconnect
    session.disconnect()


def ap_setup_command(args: argparse.Namespace) -> None:
    """
    Set up a Duet board as a WiFi access point.
    
    Args:
        args: Command-line arguments
    """
    port = args.port
    ssid = args.ssid
    password = args.password
    channel = args.channel
    
    if not ssid:
        print("SSID is required")
        return
    
    print(f"Connecting to {port}...")
    transport = SerialTransport(port, debug=args.debug)
    session = ConfigSession(transport, debug=args.debug)
    
    if not session.connect():
        print(f"Failed to connect to {port}")
        return
    
    if not session.is_duet_board():
        print(f"The device on {port} is not a Duet board")
        session.disconnect()
        return
    
    print(f"Connected to Duet board on {port}")
    print(f"Setting up access point with SSID '{ssid}'...")
    
    try:
        result = session.configure_access_point(ssid, password, channel)
        
        if result:
            print("Access point setup successful")
            print("The board will now restart in access point mode")
            print(f"Connect to the '{ssid}' WiFi network to access the board")
        else:
            print("Access point setup failed")
    except Exception as e:
        print(f"Error setting up access point: {e}")
    
    # Disconnect
    session.disconnect()


def protocol_command(args: argparse.Namespace) -> None:
    """
    Configure network protocols on a Duet board.
    
    Args:
        args: Command-line arguments
    """
    port = args.port
    protocol = args.protocol
    enable = args.enable
    
    protocol_names = {
        0: "HTTP",
        1: "FTP",
        2: "Telnet",
        3: "MQTT"
    }
    
    protocol_name = protocol_names.get(protocol, f"Protocol {protocol}")
    
    print(f"Connecting to {port}...")
    transport = SerialTransport(port, debug=args.debug)
    session = ConfigSession(transport, debug=args.debug)
    
    if not session.connect():
        print(f"Failed to connect to {port}")
        return
    
    if not session.is_duet_board():
        print(f"The device on {port} is not a Duet board")
        session.disconnect()
        return
    
    print(f"Connected to Duet board on {port}")
    print(f"{'Enabling' if enable else 'Disabling'} {protocol_name} protocol...")
    
    try:
        result = session.enable_network_protocol(protocol, enable)
        
        if result:
            print(f"{protocol_name} protocol {'enabled' if enable else 'disabled'} successfully")
        else:
            print(f"Failed to {'enable' if enable else 'disable'} {protocol_name} protocol")
    except Exception as e:
        print(f"Error configuring protocol: {e}")
    
    # Disconnect
    session.disconnect()


def transition_command(args: argparse.Namespace) -> None:
    """
    Transition from serial to WiFi connectivity.
    
    Args:
        args: Command-line arguments
    """
    port = args.port
    ssid = args.ssid
    password = args.password
    
    if not ssid:
        print("SSID is required")
        return
    
    print(f"Connecting to {port}...")
    transport = SerialTransport(port, debug=args.debug)
    session = ConfigSession(transport, debug=args.debug)
    
    if not session.connect():
        print(f"Failed to connect to {port}")
        return
    
    if not session.is_duet_board():
        print(f"The device on {port} is not a Duet board")
        session.disconnect()
        return
    
    print(f"Connected to Duet board on {port}")
    print(f"Setting up WiFi for network '{ssid}'...")
    print("Transitioning from serial to WiFi connectivity...")
    
    try:
        http_transport = session.transition_to_wifi(ssid, password or "", timeout=args.timeout)
        
        if http_transport:
            ip_address = http_transport.base_url.replace("http://", "")
            print(f"Transition successful! Board is now accessible at http://{ip_address}")
            
            # Save IP address to file if requested
            if args.save_ip:
                with open(args.save_ip, "w") as f:
                    f.write(ip_address)
                print(f"IP address saved to {args.save_ip}")
            
            # Get status via HTTP if requested
            if args.test:
                print("\nTesting HTTP connection...")
                try:
                    status = http_transport.get_status()
                    print("Connection successful!")
                    print(f"Firmware: {status.get('firmware', {}).get('name', 'unknown')} "
                          f"{status.get('firmware', {}).get('version', 'unknown')}")
                except Exception as e:
                    print(f"Error testing HTTP connection: {e}")
                
                # Disconnect HTTP transport
                http_transport.disconnect()
        else:
            print("Transition failed. The board may not be connected to WiFi.")
    except Exception as e:
        print(f"Error during transition: {e}")
    
    # Disconnect serial transport
    session.disconnect()


def main() -> None:
    """
    Main entry point for the CLI tool.
    """
    parser = argparse.ArgumentParser(description="Duet board configuration tool")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan for Duet boards")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Get information about a Duet board")
    info_parser.add_argument("--port", "-p", required=True, help="Serial port")
    info_parser.add_argument("--diagnostics", "-d", action="store_true", help="Get detailed diagnostics")
    
    # WiFi scan command
    wifi_scan_parser = subparsers.add_parser("wifi-scan", help="Scan for available WiFi networks")
    wifi_scan_parser.add_argument("--port", "-p", required=True, help="Serial port")
    wifi_scan_parser.add_argument("--timeout", "-t", type=int, default=10, help="Scan timeout in seconds")
    
    # WiFi setup command
    wifi_setup_parser = subparsers.add_parser("wifi-setup", help="Set up WiFi on a Duet board")
    wifi_setup_parser.add_argument("--port", "-p", required=True, help="Serial port")
    wifi_setup_parser.add_argument("--ssid", "-s", required=True, help="WiFi SSID")
    wifi_setup_parser.add_argument("--password", "-w", help="WiFi password")
    wifi_setup_parser.add_argument("--timeout", "-t", type=int, default=30, help="Connection timeout in seconds")
    wifi_setup_parser.add_argument("--save-ip", help="Save IP address to file")
    
    # Access point setup command
    ap_setup_parser = subparsers.add_parser("ap-setup", help="Set up a Duet board as a WiFi access point")
    ap_setup_parser.add_argument("--port", "-p", required=True, help="Serial port")
    ap_setup_parser.add_argument("--ssid", "-s", required=True, help="Access point SSID")
    ap_setup_parser.add_argument("--password", "-w", help="Access point password")
    ap_setup_parser.add_argument("--channel", "-c", type=int, help="WiFi channel")
    
    # Protocol command
    protocol_parser = subparsers.add_parser("protocol", help="Configure network protocols")
    protocol_parser.add_argument("--port", "-p", required=True, help="Serial port")
    protocol_parser.add_argument("--protocol", "-r", type=int, required=True, 
                                help="Protocol number (0=HTTP, 1=FTP, 2=Telnet, 3=MQTT)")
    protocol_parser.add_argument("--enable", "-e", action="store_true", help="Enable protocol (default: disable)")
    
    # Transition command
    transition_parser = subparsers.add_parser("transition", help="Transition from serial to WiFi connectivity")
    transition_parser.add_argument("--port", "-p", required=True, help="Serial port")
    transition_parser.add_argument("--ssid", "-s", required=True, help="WiFi SSID")
    transition_parser.add_argument("--password", "-w", help="WiFi password")
    transition_parser.add_argument("--timeout", "-t", type=int, default=30, help="Connection timeout in seconds")
    transition_parser.add_argument("--save-ip", help="Save IP address to file")
    transition_parser.add_argument("--test", action="store_true", help="Test HTTP connection after transition")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute the appropriate command
    if args.command == "scan":
        scan_command(args)
    elif args.command == "info":
        info_command(args)
    elif args.command == "wifi-scan":
        wifi_scan_command(args)
    elif args.command == "wifi-setup":
        wifi_setup_command(args)
    elif args.command == "ap-setup":
        ap_setup_command(args)
    elif args.command == "protocol":
        protocol_command(args)
    elif args.command == "transition":
        transition_command(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 