## M453: Select CNC Device Mode

Supported by RRF 1.20 and later.

• M453 in RepRapFirmware 3.3 and later

• M453 in RepRapFirmware 3.2

• M453 in RepRapFirmware 3.0 and 3.1.x

• M453 in RepRapFirmware 1.x and 2.x

Switches to CNC mode. All other parameters have been removed and moved into M950.

##### ; Old code M453 S0 T1 C"!exp.heater3" R12000 ; Assign tool 1 to spindle index 0, with PWM pin on heater 3 and 12000 RPM achieved at full PWM ; New code M950 R0 C"!exp.heater3" L12000 ; Create spindle index 0, with PWM pin on heater 3 and 12000 RPM achieved at full PWM M563 P1 S"Spindle 1" R0 ; Create tool 1 with spindle 0 and call it "Spindle 1" M453 ; Old code M453 S0 T1 C"exp.heater3+exp.heater4+exp.heater5" Q100 ; spindle PWM on heater 3 pin, on/off on heater 4, reverse/forward on heater 5, PWM frequency 100Hz ; New code M950 R0 C"exp.heater3+exp.heater4+exp.heater5" Q100 M563 P1 S"Spindle 1" R0 ; Create tool 1 with spindle 0 and call it "Spindle 1" M453

##### Parameters

- **Snnn** (optional) Spindle index, defaults to 0. Duet 2 supports 4 spindles max

- **C"aaa+bbb+ccc"** Names of the ports used to drive the spindle motor. "aaa" is the PWM port used to control the speed. "bbb" (optional) is the digital port used to turn the spindle motor on. "ccc" (optional) is the name of the port used to command reverse instead of forward spindle rotation.

- **Rbbb** or **Raaa:bbb** (optional) RPM values that are achieved at zero PWM and at maximum RPM. Used to convert the S parameter in M3 and M4 commands to a PWM value.

- **Qnnn** (optional) The PWM frequency to use

- **Tnnn** (optional) Assign spindle to a tool allowing better control in DWC

##### Parameters

- **Snnn** (optional) Spindle index, defaults to 0. Duet 2 supports 4 spindles max

- **C"fff+rrr"** Names of the ports used to drive the spindle motor in clockwise and counterclockwise directions. Omit the "+rrr" part if the spindle turns clockwise only.

- **Rnnn** Spindle RPM that is achieved at full PWM. Used to convert the S parameter in M3 and M4 commands to a PWM value.

- **Fnnn** (optional) The PWM frequency to use

- **Tnnn** (optional) Assign spindle to a tool allowing better control in DWC

##### Parameters

- **Snnn** (optional) Spindle index, defaults to 0. Duet 2 supports 4 spindles max

- **Pfff:rrr** Logical pin numbers used to drive the spindle motor in clockwise and counterclockwise directions. Omit the ":rrr" part if the spindle turns clockwise only. (Not supported in RRF3, see notes)

- **In** Invert (I1) or don't invert (I0, default) the output polarity. (Not supported in RRF3, see notes)

- **Rnnn** Spindle RPM that is achieved at full PWM. Used to convert the S parameter in M3 and M4 commands to a PWM value.

- **Fnnn** (optional) The PWM frequency to use

- **Tnnn** (optional) Assign spindle to a tool allowing better control in DWC

##### M453 P2 R5000 ; switch to CNC mode using heater 2 (E1 heater) pins to control the spindle motor

Logical pin numbers for the P parameters are as defined for the M42 and M208 commands. If you wish to assign a heater or fan output to control the spindle motor as in the above example, you must first disable the corresponding heater (see M307) or fan (see M106).

### Notes

- Switches to CNC mode. In this mode M3/M4/M5 control the pins defined for the milling device. By default, no output is assigned to a spindle motor, so it must be configured.

- In CNC mode, it is valid in a Gcode file to send G0 or G1 on one line, and then just send co-ordinates on the following lines.

- In CNC mode, comments can be enclosed in a **single** pair of parentheses, e.g. (comment). Comments cannot include double or nested parentheses, e.g. (comment (a bit more comment)), and they must start and end on the same line. This complies with NIST Gcode interpreter guidelines. e.g. G28 (here come the axes to be homed) X Y

- When using Gcode meta commands, sub-expressions may be enclosed in { } or in ( ). However, standard CNC GCode uses ( ) to enclose comments (see note above). So in CNC mode, RepRapFirmware treats ( ) as enclosing subexpressions when they appear inside { } and as enclosing comments when they do not. Therefore, when RepRapFirmware is running in CNC mode, any use of ( ) to enclose a subexpression or function parameter list must be within an expression enclosed in { }.

- See also Configuring RepRapFirmware for a CNC machine.

