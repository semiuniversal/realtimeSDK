"""
Airbrush-specific instruction class for the Realtime Hairbrush SDK.

This module provides an instruction class tailored for the airbrush plotter,
extending the base GCodeInstruction class with airbrush-specific functionality.
"""

from typing import Dict, Optional, Union, List
import importlib

from semantic_gcode.gcode.base import GCodeInstruction, Numeric

# Import the proper G-code command implementations
try:
    # G-code commands
    from semantic_gcode.dict.gcode_commands.G1.G1 import G1_LinearMove
    from semantic_gcode.dict.gcode_commands.G4.G4 import G4_Dwell
    from semantic_gcode.dict.gcode_commands.G28.G28 import G28_Home
    from semantic_gcode.dict.gcode_commands.G90.G90 import G90_AbsolutePositioning
    from semantic_gcode.dict.gcode_commands.G91.G91 import G91_RelativePositioning
    
    # M-code commands
    from semantic_gcode.dict.gcode_commands.M18.M18 import M18_DisableMotors
    from semantic_gcode.dict.gcode_commands.M106.M106 import M106_FanOn
    
    # T command
    from semantic_gcode.dict.gcode_commands.T.T import T_SelectTool
    
    # Flag to indicate if proper implementations are available
    PROPER_IMPLEMENTATIONS_AVAILABLE = True
except ImportError:
    # Fall back to legacy implementation if proper implementations are not available
    PROPER_IMPLEMENTATIONS_AVAILABLE = False


class AirbrushInstruction(GCodeInstruction):
    """
    Airbrush-specific instruction class.
    
    This class extends the base GCodeInstruction class with airbrush-specific
    attributes and factory methods for creating common airbrush-related G-code
    instructions.
    """
    
    def __init__(
        self,
        code_type: str,
        code_number: int,
        parameters: Dict[str, Numeric] = None,
        comment: Optional[str] = None,
        tool_index: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize an airbrush instruction.
        
        Args:
            code_type: The G-code type (G, M, T)
            code_number: The G-code number
            parameters: Parameters for the instruction
            comment: Optional comment
            tool_index: Optional tool index (0 or 1)
            **kwargs: Additional metadata
        """
        super().__init__(
            code_type=code_type,
            code_number=code_number,
            parameters=parameters or {},
            comment=comment,
            **kwargs
        )
        self.tool_index = tool_index
    
    @classmethod
    def create_tool_select(cls, tool_index: int) -> 'AirbrushInstruction':
        """
        Create a tool selection instruction.
        
        Args:
            tool_index: Tool index (0 or 1)
            
        Returns:
            AirbrushInstruction: Tool selection instruction
        """
        if PROPER_IMPLEMENTATIONS_AVAILABLE:
            # Use the proper implementation
            instruction = T_SelectTool.create(tool_number=tool_index)
            
            # Convert to AirbrushInstruction for backward compatibility
            return cls(
                code_type=instruction.code_type,
                code_number=instruction.code_number,
                parameters=instruction.parameters,
                comment=instruction.comment,
                tool_index=tool_index
            )
        else:
            # Fall back to legacy implementation
            return cls(
                code_type='T',
                code_number=tool_index,
                comment=f"Select Tool {tool_index}",
                tool_index=tool_index
            )
    
    @classmethod
    def create_air_control(
        cls, 
        tool_index: int, 
        on: bool = True,
        fan_index: Optional[int] = None
    ) -> 'AirbrushInstruction':
        """
        Create an air control instruction.
        
        Args:
            tool_index: Tool index (0 or 1)
            on: True to turn on, False to turn off
            fan_index: Fan index for the solenoid (default: 2 for tool 0, 3 for tool 1)
            
        Returns:
            AirbrushInstruction: Air control instruction
        """
        # Determine fan index if not specified
        if fan_index is None:
            fan_index = 2 if tool_index == 0 else 3
            
        if PROPER_IMPLEMENTATIONS_AVAILABLE:
            # Use the proper implementation
            instruction = M106_FanOn.create(
                fan_number=fan_index,
                speed=1.0 if on else 0.0
            )
            
            # Convert to AirbrushInstruction for backward compatibility
            return cls(
                code_type=instruction.code_type,
                code_number=instruction.code_number,
                parameters=instruction.parameters,
                comment=f"Air {'on' if on else 'off'} for Tool {tool_index}",
                tool_index=tool_index
            )
        else:
            # Fall back to legacy implementation
            value = 1.0 if on else 0.0
            action = "on" if on else "off"
            return cls(
                code_type='M',
                code_number=106,
                parameters={
                    'P': fan_index,
                    'S': value
                },
                comment=f"Air {action} for Tool {tool_index}",
                tool_index=tool_index
            )
    
    @classmethod
    def create_paint_flow_start(
        cls, 
        tool_index: int,
        width: float = 1.0,
        opacity: float = 1.0,
        axis: Optional[str] = None
    ) -> List['AirbrushInstruction']:
        """
        Create a sequence of instructions to start paint flow.
        
        This generates multiple G-code instructions:
        1. G91 - Set relative positioning
        2. G1 U/V - Set flow value
        3. G90 - Set absolute positioning
        
        Args:
            tool_index: Tool index (0 or 1)
            width: Line width (0.0-1.0)
            opacity: Paint opacity (0.0-1.0)
            axis: Axis for paint flow control (U or V, default based on tool_index)
            
        Returns:
            List[AirbrushInstruction]: List of instructions
        """
        # Determine axis if not specified
        if axis is None:
            axis = "U" if tool_index == 0 else "V"
            
        # Calculate flow value based on width and opacity
        flow_value = width * opacity
        
        if PROPER_IMPLEMENTATIONS_AVAILABLE:
            # Use the proper implementations
            instructions = []
            
            # 1. Set relative positioning
            g91_instruction = G91_RelativePositioning.create()
            instructions.append(cls(
                code_type=g91_instruction.code_type,
                code_number=g91_instruction.code_number,
                parameters=g91_instruction.parameters,
                comment=g91_instruction.comment,
                tool_index=tool_index
            ))
            
            # 2. Set flow value
            g1_instruction = G1_LinearMove.create(**{axis.lower(): flow_value})
            instructions.append(cls(
                code_type=g1_instruction.code_type,
                code_number=g1_instruction.code_number,
                parameters={axis: flow_value},  # Ensure axis is uppercase
                comment=f"Start paint flow (width={width}, opacity={opacity})",
                tool_index=tool_index
            ))
            
            # 3. Set absolute positioning
            g90_instruction = G90_AbsolutePositioning.create()
            instructions.append(cls(
                code_type=g90_instruction.code_type,
                code_number=g90_instruction.code_number,
                parameters=g90_instruction.parameters,
                comment=g90_instruction.comment,
                tool_index=tool_index
            ))
            
            return instructions
        else:
            # Fall back to legacy implementation
            return [
                # Set relative positioning
                cls(
                    code_type='G',
                    code_number=91,
                    comment="Set relative positioning",
                    tool_index=tool_index
                ),
                
                # Set flow value
                cls(
                    code_type='G',
                    code_number=1,
                    parameters={
                        axis: flow_value
                    },
                    comment=f"Start paint flow (width={width}, opacity={opacity})",
                    tool_index=tool_index
                ),
                
                # Set absolute positioning
                cls(
                    code_type='G',
                    code_number=90,
                    comment="Set absolute positioning",
                    tool_index=tool_index
                )
            ]
    
    @classmethod
    def create_paint_flow_stop(
        cls, 
        tool_index: int,
        axis: Optional[str] = None
    ) -> 'AirbrushInstruction':
        """
        Create an instruction to stop paint flow.
        
        Args:
            tool_index: Tool index (0 or 1)
            axis: Axis for paint flow control (U or V, default based on tool_index)
            
        Returns:
            AirbrushInstruction: Paint flow stop instruction
        """
        # Determine axis if not specified
        if axis is None:
            axis = "U" if tool_index == 0 else "V"
            
        if PROPER_IMPLEMENTATIONS_AVAILABLE:
            # Use the proper implementation
            instruction = M18_DisableMotors.create(axes=[axis])
            
            # Convert to AirbrushInstruction for backward compatibility
            return cls(
                code_type=instruction.code_type,
                code_number=instruction.code_number,
                parameters={axis: 0},  # Ensure axis is uppercase
                comment=f"Stop paint flow for Tool {tool_index}",
                tool_index=tool_index
            )
        else:
            # Fall back to legacy implementation
            return cls(
                code_type='M',
                code_number=18,
                parameters={
                    axis: 0
                },
                comment=f"Stop paint flow for Tool {tool_index}",
                tool_index=tool_index
            )
    
    @classmethod
    def create_move(
        cls,
        x: Optional[float] = None,
        y: Optional[float] = None,
        z: Optional[float] = None,
        feedrate: Optional[float] = None
    ) -> 'AirbrushInstruction':
        """
        Create a move instruction.
        
        Args:
            x: X position
            y: Y position
            z: Z position
            feedrate: Movement speed
            
        Returns:
            AirbrushInstruction: Move instruction
        """
        if PROPER_IMPLEMENTATIONS_AVAILABLE:
            # Use the proper implementation
            instruction = G1_LinearMove.create(x=x, y=y, z=z, feedrate=feedrate)
            
            # Convert to AirbrushInstruction for backward compatibility
            return cls(
                code_type=instruction.code_type,
                code_number=instruction.code_number,
                parameters=instruction.parameters,
                comment=instruction.comment
            )
        else:
            # Fall back to legacy implementation
            parameters = {}
            if x is not None:
                parameters['X'] = x
            if y is not None:
                parameters['Y'] = y
            if z is not None:
                parameters['Z'] = z
            if feedrate is not None:
                parameters['F'] = feedrate
            
            return cls(
                code_type='G',
                code_number=1,
                parameters=parameters,
                comment="Move"
            )
    
    @classmethod
    def create_safe_z_move(cls, z: float = 10.0, feedrate: Optional[float] = None) -> 'AirbrushInstruction':
        """
        Create a safe Z move instruction.
        
        Args:
            z: Z position
            feedrate: Movement speed
            
        Returns:
            AirbrushInstruction: Z move instruction
        """
        if PROPER_IMPLEMENTATIONS_AVAILABLE:
            # Use the proper implementation
            instruction = G1_LinearMove.create(z=z, feedrate=feedrate)
            
            # Convert to AirbrushInstruction for backward compatibility
            return cls(
                code_type=instruction.code_type,
                code_number=instruction.code_number,
                parameters=instruction.parameters,
                comment=f"Move Z to safe height {z}mm"
            )
        else:
            # Fall back to legacy implementation
            parameters = {'Z': z}
            if feedrate is not None:
                parameters['F'] = feedrate
            
            return cls(
                code_type='G',
                code_number=1,
                parameters=parameters,
                comment=f"Move Z to safe height {z}mm"
            )
    
    @classmethod
    def create_spray_z_move(cls, z: float = 1.5, feedrate: Optional[float] = None) -> 'AirbrushInstruction':
        """
        Create a spray Z move instruction.
        
        Args:
            z: Z position
            feedrate: Movement speed
            
        Returns:
            AirbrushInstruction: Z move instruction
        """
        if PROPER_IMPLEMENTATIONS_AVAILABLE:
            # Use the proper implementation
            instruction = G1_LinearMove.create(z=z, feedrate=feedrate)
            
            # Convert to AirbrushInstruction for backward compatibility
            return cls(
                code_type=instruction.code_type,
                code_number=instruction.code_number,
                parameters=instruction.parameters,
                comment=f"Move Z to spray height {z}mm"
            )
        else:
            # Fall back to legacy implementation
            parameters = {'Z': z}
            if feedrate is not None:
                parameters['F'] = feedrate
            
            return cls(
                code_type='G',
                code_number=1,
                parameters=parameters,
                comment=f"Move Z to spray height {z}mm"
            )
    
    @classmethod
    def create_dwell(cls, milliseconds: int) -> 'AirbrushInstruction':
        """
        Create a dwell instruction.
        
        Args:
            milliseconds: Dwell time in milliseconds
            
        Returns:
            AirbrushInstruction: Dwell instruction
        """
        if PROPER_IMPLEMENTATIONS_AVAILABLE:
            # Use the proper implementation
            instruction = G4_Dwell.create(milliseconds=milliseconds)
            
            # Convert to AirbrushInstruction for backward compatibility
            return cls(
                code_type=instruction.code_type,
                code_number=instruction.code_number,
                parameters=instruction.parameters,
                comment=instruction.comment
            )
        else:
            # Fall back to legacy implementation
            return cls(
                code_type='G',
                code_number=4,
                parameters={
                    'P': milliseconds
                },
                comment=f"Dwell for {milliseconds}ms"
            )
    
    @classmethod
    def create_home(
        cls, 
        axes: Optional[List[str]] = None
    ) -> 'AirbrushInstruction':
        """
        Create a homing instruction.
        
        Args:
            axes: List of axes to home (e.g., ["X", "Y"]), or None to home all axes
            
        Returns:
            AirbrushInstruction: Homing instruction
        """
        if PROPER_IMPLEMENTATIONS_AVAILABLE:
            # Use the proper implementation
            instruction = G28_Home.create(axes=axes)
            
            # Convert to AirbrushInstruction for backward compatibility
            return cls(
                code_type=instruction.code_type,
                code_number=instruction.code_number,
                parameters=instruction.parameters,
                comment=instruction.comment
            )
        else:
            # Fall back to legacy implementation
            parameters = {}
            if axes:
                for axis in axes:
                    parameters[axis] = 0
                comment = f"Home {', '.join(axes)} axes"
            else:
                comment = "Home all axes"
            
            return cls(
                code_type='G',
                code_number=28,
                parameters=parameters,
                comment=comment
            ) 