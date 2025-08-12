"""
Tool Manager for dual-airbrush system with semantic G-code.

Maintains a consistent logical coordinate system while managing
physical tool offsets transparently.
"""

from typing import Optional, Dict, Union
from dataclasses import dataclass
from enum import IntEnum

from realtime_hairbrush.runtime import MachineState, Dispatcher
from semantic_gcode.dict.gcode_commands.G1.G1 import G1_LinearMove
from semantic_gcode.dict.gcode_commands.T.T import T_SelectTool
from semantic_gcode.dict.gcode_commands.M106.M106 import M106_FanControl
from semantic_gcode.dict.gcode_commands.M564.M564 import M564_LimitAxes
from semantic_gcode.dict.gcode_commands.M400.M400 import M400_WaitForMoves
try:
    from realtime_hairbrush.transport.logging_wrapper import log_note as _log_note
except Exception:
    def _log_note(*args, **kwargs):
        pass


class Tool(IntEnum):
    """Tool indices for the dual-airbrush system."""
    BRUSH_A = 0  # Black brush
    BRUSH_B = 1  # White brush
    
    @classmethod
    def from_alias(cls, alias: Union[str, int, 'Tool']) -> 'Tool':
        """
        Resolve a tool from various alias formats.
        
        Args:
            alias: Can be:
                - Tool enum value (Tool.BRUSH_A or Tool.BRUSH_B)
                - Integer (0 or 1)
                - String number ("0" or "1")
                - Letter ("a" or "b", case-insensitive)
                - Color name ("black" or "white", case-insensitive)
        
        Returns:
            Tool: The resolved Tool enum value
            
        Raises:
            ValueError: If the alias cannot be resolved
        """
        # If already a Tool, return it
        if isinstance(alias, cls):
            return alias
            
        # If integer, convert directly
        if isinstance(alias, int):
            if alias == 0:
                return cls.BRUSH_A
            elif alias == 1:
                return cls.BRUSH_B
            else:
                raise ValueError(f"Invalid tool number: {alias}. Must be 0 or 1.")
        
        # If string, try various formats
        if isinstance(alias, str):
            alias_lower = alias.lower().strip()
            
            # Define all possible aliases
            brush_a_aliases = {"0", "a", "black", "brush_a", "tool0"}
            brush_b_aliases = {"1", "b", "white", "brush_b", "tool1"}
            
            if alias_lower in brush_a_aliases:
                return cls.BRUSH_A
            elif alias_lower in brush_b_aliases:
                return cls.BRUSH_B
            else:
                raise ValueError(
                    f"Unknown tool alias: '{alias}'. "
                    f"Valid aliases: 0/a/black for Brush A, 1/b/white for Brush B"
                )
        
        raise TypeError(f"Tool alias must be str, int, or Tool enum, not {type(alias)}")
    
    @property
    def color_name(self) -> str:
        """Get the color name for this tool."""
        return "black" if self == Tool.BRUSH_A else "white"
    
    @property
    def letter(self) -> str:
        """Get the letter designation for this tool."""
        return "A" if self == Tool.BRUSH_A else "B"


@dataclass
class ToolOffset:
    """Physical offset for a tool."""
    x: float
    y: float
    z: float = 0.0


class ToolManager:
    """
    Manages tool offsets and coordinate transformations for dual-airbrush system.
    
    This class maintains a consistent logical coordinate system for the user
    while handling physical tool offsets transparently.
    """
    
    def __init__(self, dispatcher: Dispatcher, state: MachineState):
        """
        Initialize the tool manager.
        
        Args:
            dispatcher: Dispatcher for sending G-code commands
            state: Machine state tracker
        """
        self.dispatcher = dispatcher
        self.state = state
        
        # Define tool offsets (physical positions relative to Tool 0)
        self.tool_offsets = {
            Tool.BRUSH_A: ToolOffset(0, 0, 0),      # Reference position
            Tool.BRUSH_B: ToolOffset(100, -25, 0),  # 100mm right, 25mm forward
        }
        
        # Air control fan indices
        self.tool_fans = {
            Tool.BRUSH_A: 2,  # Fan P2 for Brush A
            Tool.BRUSH_B: 3,  # Fan P3 for Brush B
        }
        
        # Paint flow axes
        self.tool_flow_axes = {
            Tool.BRUSH_A: 'U',  # U axis for Brush A
            Tool.BRUSH_B: 'V',  # V axis for Brush B
        }
        
        # Flow control parameters (from YAML config)
        self.flow_config = {
            'U': {'min': 0.0, 'max': 4.0, 'dead_zone': 0.8, 'feedrate': 200},
            'V': {'min': 0.0, 'max': 4.0, 'dead_zone': 0.8, 'feedrate': 200},
        }
        
        # State tracking
        self.current_tool: Optional[Tool] = Tool.BRUSH_A
        self.logical_position = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.soft_limits_disabled = False
        self._synced_from_observed_once: bool = False
        
    def switch_tool(self, tool: Union[Tool, str, int], wait: bool = True) -> None:
        """
        Switch to a different tool while maintaining logical position.
        
        This method handles the tool change and moves the carriage so that
        the new tool ends up at the same logical position where the old tool was.
        
        Args:
            tool: Tool to switch to (can be Tool enum, int, or string alias)
            wait: Whether to wait for moves to complete
        """
        _log_note(f"TOOL switch requested: {tool}")
        tool = Tool.from_alias(tool)
        _log_note(f"TOOL resolved to index={int(tool)} (current={int(self.current_tool) if self.current_tool is not None else None})")

        # Synchronize logical position from observed state before computing moves
        if not self._synced_from_observed_once:
            try:
                snap = self.state.snapshot().get("observed", {})
                raw = (snap.get("raw_status", {}) or {}).get("raw", {})
                # Determine current tool from observed if available
                obs_tool = raw.get("currentTool")
                if obs_tool is None:
                    obs_tool = int(self.current_tool) if self.current_tool is not None else 0
                # Prefer userPosition when available
                coords = (raw.get("coords", {}) or {})
                pos = coords.get("userPosition") or coords.get("machine") or coords.get("xyz") or raw.get("position")
                if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                    cur_offset = self.tool_offsets[Tool.BRUSH_A if int(obs_tool) == 0 else Tool.BRUSH_B]
                    # logical = user - current_offset
                    self.logical_position['x'] = float(pos[0]) - cur_offset.x
                    self.logical_position['y'] = float(pos[1]) - cur_offset.y
                    _log_note(f"TOOL one-time sync logical from observed: user=({pos[0]},{pos[1]}) cur_offset=({cur_offset.x},{cur_offset.y}) -> logical=({self.logical_position['x']},{self.logical_position['y']})")
            except Exception:
                # Best-effort; ignore sync errors
                pass
            finally:
                self._synced_from_observed_once = True
            
        if tool == self.current_tool:
            _log_note("TOOL early return: requested equals current tool")
            return
            
        # Calculate where to move BEFORE tool change so that after T the logical stays the same
        # With RRF userPosition = machinePosition + offset(tool), the required pre-move is:
        # C = L0 + (current_offset - target_offset)
        old_offset = self.tool_offsets[self.current_tool]
        new_offset = self.tool_offsets[tool]
        pre_move_x = self.logical_position['x'] + (old_offset.x - new_offset.x)
        pre_move_y = self.logical_position['y'] + (old_offset.y - new_offset.y)
        _log_note(f"TOOL pre-move compute: L0=({self.logical_position['x']},{self.logical_position['y']}) old_off=({old_offset.x},{old_offset.y}) new_off=({new_offset.x},{new_offset.y}) -> command C=({pre_move_x},{pre_move_y})")

        # Handle soft limits around pre-move if switching to Tool B (extended range)
        if tool == Tool.BRUSH_B and not self.soft_limits_disabled:
            m564 = M564_LimitAxes.create(limit_within_bounds=False, require_homing_before_move=False)
            self.dispatcher.enqueue(m564)
            _log_note("TOOL enqueue: M564 S0 H0 (disable limits)")
            self.soft_limits_disabled = True
        
        # Pre-move under current tool so that after T we are aligned
        g1_cmd = G1_LinearMove.create(x=pre_move_x, y=pre_move_y, feedrate=24000)
        self.dispatcher.enqueue(g1_cmd)
        _log_note(f"TOOL enqueue: G1 X{pre_move_x} Y{pre_move_y} F24000 (pre-move)")
        if wait:
            m400 = M400_WaitForMoves.create()
            self.dispatcher.enqueue(m400)
            _log_note("TOOL enqueue: M400 (after pre-move)")

        # Now select the new tool; after this firmware applies the new offset
        t_cmd = T_SelectTool.create(tool_number=int(tool))
        self.dispatcher.enqueue(t_cmd)
        _log_note(f"TOOL enqueue: T{int(tool)}")
        # Optional small dwell to stabilize object model after T
        try:
            from semantic_gcode.dict.gcode_commands.G4.G4 import G4_Dwell
            self.dispatcher.enqueue(G4_Dwell.create(milliseconds=200))
            _log_note("TOOL enqueue: G4 P200 (post-T dwell)")
        except Exception:
            pass
        # Normalize user coordinate frame so userPosition reflects logical L0 after T
        try:
            from semantic_gcode.dict.gcode_commands.G92.G92 import G92_SetPosition
            g92 = G92_SetPosition.create(x=self.logical_position['x'], y=self.logical_position['y'])
            self.dispatcher.enqueue(g92)
            _log_note(f"TOOL enqueue: G92 X{self.logical_position['x']} Y{self.logical_position['y']} (normalize user coords)")
        except Exception:
            _log_note("TOOL note: G92 not available; skipping user coord normalization")

        # If switching back to Tool A, re-enable limits after T
        if tool == Tool.BRUSH_A and self.soft_limits_disabled:
            m564 = M564_LimitAxes.create(limit_within_bounds=True, require_homing_before_move=True)
            self.dispatcher.enqueue(m564)
            _log_note("TOOL enqueue: M564 S1 H1 (enable limits)")
            self.soft_limits_disabled = False
        
        # Update tracking
        self.current_tool = tool
        _log_note(f"TOOL current set to {int(tool)}")
        
    def move_to(self, x: float, y: float, z: Optional[float] = None, 
                feedrate: float = 3000, wait: bool = False) -> None:
        """
        Move to logical coordinates, automatically applying tool offset.
        
        Args:
            x: Logical X coordinate
            y: Logical Y coordinate
            z: Logical Z coordinate (optional)
            feedrate: Movement speed in mm/min
            wait: Whether to wait for move to complete
        """
        # Update logical position
        self.logical_position['x'] = x
        self.logical_position['y'] = y
        if z is not None:
            self.logical_position['z'] = z
            
        # Calculate physical position with tool offset
        offset = self.tool_offsets[self.current_tool]
        physical_x = x + offset.x
        physical_y = y + offset.y
        physical_z = self.logical_position['z'] + offset.z if z is not None else None
        
        # Build and send G1 command
        g1_cmd = G1_LinearMove.create(
            x=physical_x,
            y=physical_y,
            z=physical_z,
            feedrate=feedrate
        )
        self.dispatcher.enqueue(g1_cmd)
        
        if wait:
            m400 = M400_WaitForMoves.create()
            self.dispatcher.enqueue(m400)
            
    def set_paint_flow(self, flow_value: float, tool: Optional[Union[Tool, str, int]] = None, 
                       wait: bool = False) -> None:
        """
        Set paint flow for a specific tool using U/V axis.
        
        Args:
            flow_value: Flow value (0.0 to 1.0)
            tool: Tool to set flow for (None uses current tool)
            wait: Whether to wait for move to complete
        """
        # Determine which tool to control
        if tool is not None:
            target_tool = Tool.from_alias(tool)
        else:
            target_tool = self.current_tool
            
        # Get the appropriate axis for the target tool
        axis = self.tool_flow_axes[target_tool]
        config = self.flow_config[axis]
        
        # Map flow value (0-1) to stepper position
        if flow_value <= 0.0:
            position = config['min']
        else:
            # Map from 0-1 to dead_zone-max range
            position = config['dead_zone'] + (flow_value * (config['max'] - config['dead_zone']))
            position = min(max(position, config['min']), config['max'])
        
        # Create G1 command with appropriate axis
        kwargs = {axis.lower(): position, 'feedrate': config['feedrate']}
        g1_cmd = G1_LinearMove.create(**kwargs)
        self.dispatcher.enqueue(g1_cmd)
        
        if wait:
            m400 = M400_WaitForMoves.create()
            self.dispatcher.enqueue(m400)
            
    def set_air(self, on: bool, tool: Optional[Union[Tool, str, int]] = None) -> None:
        """
        Control air for a specific tool.
        
        Args:
            on: True to turn on, False to turn off
            tool: Tool to control air for (None uses current tool)
        """
        # Determine which tool to control
        if tool is not None:
            target_tool = Tool.from_alias(tool)
        else:
            target_tool = self.current_tool
            
        fan_index = self.tool_fans[target_tool]
        m106_cmd = M106_FanControl.create(
            p=fan_index,
            s=1.0 if on else 0.0
        )
        self.dispatcher.enqueue(m106_cmd)
        
    def air_on(self, tool: Optional[Union[Tool, str, int]] = None) -> None:
        """
        Turn air on for a specific tool.
        
        Args:
            tool: Tool to turn air on for (None uses current tool)
        """
        self.set_air(True, tool)
        
    def air_off(self, tool: Optional[Union[Tool, str, int]] = None) -> None:
        """
        Turn air off for a specific tool.
        
        Args:
            tool: Tool to turn air off for (None uses current tool)
        """
        self.set_air(False, tool)
        
    def stop_paint_flow(self, tool: Optional[Union[Tool, str, int]] = None, wait: bool = False) -> None:
        """
        Stop paint flow (set to 0) for a specific tool.
        
        Args:
            tool: Tool to stop flow for (None uses current tool)
            wait: Whether to wait for move to complete
        """
        self.set_paint_flow(0.0, tool, wait)
        
    def get_logical_position(self) -> Dict[str, float]:
        """Get the current logical position (user coordinates)."""
        return self.logical_position.copy()
        
    def get_physical_position(self) -> Dict[str, float]:
        """Get the actual physical position of the carriage."""
        offset = self.tool_offsets[self.current_tool]
        return {
            'x': self.logical_position['x'] + offset.x,
            'y': self.logical_position['y'] + offset.y,
            'z': self.logical_position['z'] + offset.z,
        }
    
    def get_current_tool(self) -> Tool:
        """Get the currently selected tool."""
        return self.current_tool
    
    def get_current_tool_info(self) -> Dict[str, Union[int, str]]:
        """Get information about the currently selected tool."""
        return {
            'index': int(self.current_tool),
            'letter': self.current_tool.letter,
            'color': self.current_tool.color_name,
            'fan': self.tool_fans[self.current_tool],
            'flow_axis': self.tool_flow_axes[self.current_tool],
        }
    
    def set_logical_position(self, x: Optional[float] = None, 
                            y: Optional[float] = None, 
                            z: Optional[float] = None) -> None:
        """
        Update the logical position without moving the machine.
        Useful for synchronizing after manual moves or homing.
        
        Args:
            x: New logical X coordinate (None keeps current value)
            y: New logical Y coordinate (None keeps current value)
            z: New logical Z coordinate (None keeps current value)
        """
        if x is not None:
            self.logical_position['x'] = x
        if y is not None:
            self.logical_position['y'] = y
        if z is not None:
            self.logical_position['z'] = z


# Example usage
if __name__ == "__main__":
    # This is just example code showing how to use the ToolManager
    print("ToolManager for dual-airbrush system")
    print("=====================================")
    print()
    print("Example usage:")
    print()
    print("from realtime_hairbrush.transport.config import ConnectionConfig")
    print("from realtime_hairbrush.transport.airbrush_transport import AirbrushTransport")
    print("from realtime_hairbrush.runtime import MachineState, Dispatcher")
    print("from ToolManager import ToolManager")
    print()
    print("# Initialize connection")
    print('cfg = ConnectionConfig(transport_type="http", http_host="192.168.86.27", timeout=10.0)')
    print("transport = AirbrushTransport(cfg)")
    print("assert transport.connect()")
    print()
    print("# Initialize runtime")
    print("state = MachineState()")
    print("dispatcher = Dispatcher(transport, state)")
    print("dispatcher.start()")
    print()
    print("# Create tool manager")
    print("tool_manager = ToolManager(dispatcher, state)")
    print()
    print("# === REAL-TIME CONTROL EXAMPLES ===")
    print()
    print("# Switch to tool B (white)")
    print('tool_manager.switch_tool("white")')
    print()
    print("# Move to a position (uses logical coordinates)")
    print("tool_manager.move_to(100, 100, z=10)")
    print()
    print("# Turn on air for current tool")
    print("tool_manager.air_on()")
    print()
    print("# Set paint flow to 50%")
    print("tool_manager.set_paint_flow(0.5)")
    print()
    print("# Move while painting")
    print("tool_manager.move_to(200, 100, feedrate=1500)")
    print()
    print("# Stop paint flow")
    print("tool_manager.stop_paint_flow()")
    print()
    print("# Turn off air")
    print("tool_manager.air_off()")
    print()
    print("# Control specific tools without switching")
    print('tool_manager.set_paint_flow(0.3, tool="a")  # Set flow for tool A')
    print('tool_manager.air_on(tool="black")  # Turn on air for black brush')
    print()
    print("# Get position information")
    print("logical = tool_manager.get_logical_position()")
    print("physical = tool_manager.get_physical_position()")
    print("print(f'Logical: {logical}, Physical: {physical}')")