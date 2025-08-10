"""
Device controller for G-code machines.

This module provides the Device class, which is the main entry point for controlling
G-code compatible machines.
"""
from typing import Dict, Any, Optional, Union, List, Type

from ..gcode import GInstruction, GCodeRegistry
from ..transport import Transport
from ..utils.exceptions import ConnectionError, StateError


class Device:
    """
    High-level controller for G-code compatible machines.
    
    This class provides a unified interface for sending commands to a G-code machine
    and monitoring its state, regardless of the underlying transport mechanism.
    """
    
    def __init__(self, transport: Transport):
        """
        Initialize a device controller.
        
        Args:
            transport: The transport to use for communication
        """
        self.transport = transport
        self._connected = False
        self._state = {
            "positioning_mode": "absolute",  # "absolute" or "relative"
            "units": "mm",  # "mm" or "inch"
            "position": {"X": 0.0, "Y": 0.0, "Z": 0.0},
            "selected_tool": 0
        }
    
    def connect(self) -> bool:
        """
        Connect to the device.
        
        Returns:
            bool: True if connection was successful, False otherwise
        
        Raises:
            ConnectionError: If connection fails
        """
        result = self.transport.connect()
        if result:
            self._connected = True
            self._update_state_from_device()
        return result
    
    def disconnect(self) -> None:
        """
        Disconnect from the device.
        """
        self.transport.disconnect()
        self._connected = False
    
    def is_connected(self) -> bool:
        """
        Check if the device is connected.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self._connected and self.transport.is_connected()
    
    def send(self, instruction: GInstruction) -> bool:
        """
        Send a G-code instruction to the device.
        
        Args:
            instruction: The instruction to send
            
        Returns:
            bool: True if the instruction was sent successfully, False otherwise
            
        Raises:
            ConnectionError: If not connected
            StateError: If the instruction would cause an invalid state transition
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to device")
        
        # Update local state based on the instruction
        self._update_state_for_instruction(instruction)
        
        # Convert instruction to G-code and send
        gcode = instruction.to_gcode()
        return self.transport.send_line(gcode)
    
    def query(self, instruction: GInstruction) -> Optional[str]:
        """
        Send a query instruction and get the response.
        
        Args:
            instruction: The query instruction to send
            
        Returns:
            Optional[str]: The response from the device, or None if no response
            
        Raises:
            ConnectionError: If not connected
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to device")
        
        # Convert instruction to G-code and send query
        gcode = instruction.to_gcode()
        return self.transport.query(gcode)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the device.
        
        Returns:
            Dict[str, Any]: A dictionary containing the device status
            
        Raises:
            ConnectionError: If not connected
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to device")
        
        # Get status from transport and update local state
        status = self.transport.get_status()
        self._update_state_from_status(status)
        
        # Return a merged status with both transport and local state
        return {
            **status,
            "state": self._state
        }
    
    def send_raw(self, gcode: str) -> bool:
        """
        Send a raw G-code string to the device.
        
        Args:
            gcode: The G-code string to send
            
        Returns:
            bool: True if the command was sent successfully, False otherwise
            
        Raises:
            ConnectionError: If not connected
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to device")
        
        # Try to parse the G-code to update local state
        instruction = GCodeRegistry.parse(gcode)
        if instruction:
            self._update_state_for_instruction(instruction)
        
        # Send the raw G-code
        return self.transport.send_line(gcode)
    
    def query_raw(self, gcode: str) -> Optional[str]:
        """
        Send a raw G-code query and get the response.
        
        Args:
            gcode: The G-code query to send
            
        Returns:
            Optional[str]: The response from the device, or None if no response
            
        Raises:
            ConnectionError: If not connected
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to device")
        
        # Send the raw query
        return self.transport.query(gcode)
    
    def _update_state_from_device(self) -> None:
        """
        Update the local state from the device status.
        """
        try:
            # Get current position
            position_response = self.transport.query("M114")
            if position_response:
                self._parse_position(position_response)
            
            # Get current status
            status = self.transport.get_status()
            self._update_state_from_status(status)
        except Exception:
            # Ignore errors during state update
            pass
    
    def _update_state_from_status(self, status: Dict[str, Any]) -> None:
        """
        Update the local state from a status dictionary.
        
        Args:
            status: The status dictionary from the transport
        """
        # Update position if available
        if "position" in status:
            self._state["position"].update(status["position"])
    
    def _update_state_for_instruction(self, instruction: GInstruction) -> None:
        """
        Update the local state based on an instruction.
        
        Args:
            instruction: The instruction that will be sent
            
        Raises:
            StateError: If the instruction would cause an invalid state transition
        """
        # Update state based on instruction type
        class_name = instruction.__class__.__name__
        
        # Update positioning mode
        if class_name == "SetAbsolutePositioning":
            self._state["positioning_mode"] = "absolute"
        elif class_name == "SetRelativePositioning":
            self._state["positioning_mode"] = "relative"
        
        # Update units
        elif class_name == "SetUnitsMM":
            self._state["units"] = "mm"
        elif class_name == "SetUnitsInch":
            self._state["units"] = "inch"
        
        # Update position origin
        elif class_name == "SetPositionOrigin":
            # G92 sets the current position to the specified coordinates
            for axis, value in instruction.args.items():
                if axis in self._state["position"]:
                    self._state["position"][axis] = value
        
        # Update position for movement commands
        elif class_name in ["MoveTo", "RapidMove", "ArcMove"]:
            self._update_position(instruction)
        
        # Update selected tool
        elif class_name == "SelectTool":
            self._state["selected_tool"] = instruction.args["P"]
    
    def _update_position(self, instruction: GInstruction) -> None:
        """
        Update the position state based on a movement instruction.
        
        Args:
            instruction: The movement instruction
        """
        # Only update axes that are specified in the instruction
        for axis in ["X", "Y", "Z"]:
            if axis in instruction.args:
                if self._state["positioning_mode"] == "absolute":
                    # Absolute positioning: set position directly
                    self._state["position"][axis] = instruction.args[axis]
                else:
                    # Relative positioning: add to current position
                    self._state["position"][axis] += instruction.args[axis]
    
    def _parse_position(self, position_response: str) -> None:
        """
        Parse a position response from the device.
        
        Args:
            position_response: The position response string (e.g., "X:10.0 Y:20.0 Z:0.0")
        """
        # Parse position response (format: "X:10.0 Y:20.0 Z:0.0")
        parts = position_response.split()
        for part in parts:
            if ":" in part:
                axis, value_str = part.split(":", 1)
                try:
                    value = float(value_str)
                    if axis in self._state["position"]:
                        self._state["position"][axis] = value
                except ValueError:
                    pass
