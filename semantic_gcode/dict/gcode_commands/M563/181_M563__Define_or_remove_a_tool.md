## M563: Define or remove a tool

### Parameters

- **Pnnn** Tool number (0 to 49 in RRF 3.x)

- **S"name"** Tool name (optional)

- **Dnnn** Extruder drive(s)

- **Hnnn** Heater(s)

- **Fnnn** Fan number(s) to use as print cooling fans for this tool (RepRapFirmware 1.16 and later)

- **Xnnn** Axis or axes to map X movement to (RepRapFirmware 1.16 and later)

- **Ynnn** Axis or axes to map Y movement to (RepRapFirmware 1.19 and later)

- **Znnn** Axis or axes to map Z movement to (RepRapFirmware 3.5 and later)

- **Lnnn** Drive to use for filament mapping. By default RRF will use the first and only extruder drive if this parameter is not specified (supported by RRF \>= 2.02)

- **Rnn** Spindle number (RRF \>= 3.3)

### Examples

M563 P0 D0:2:3 H1:3 ; create a tool using extruder drives 0, 2 and 3 and heaters 1 and 3 M563 P1 D1 H2 X3 ; create a tool using extruder drive 1 and heater 2 with X movement mapped to the U axis M563 P2 D0:1 H1:2 X0:3 F0:2 ; create a tool using extruder drives 0 and 1, heaters 1 and 2, with X movement mapped to both X and U axes and fan 0 mapped to fans 0 and 2 M563 P3 D0 H1 S"Chocolate extruder" ; create a named tool using extruder drive 0 and heater 1 M563 P1 D-1 H-1 ; Delete tool 1

### Description

Tools are usually (though not necessarily) extruders. Normally an M563 command to define a tool is immediately followed by a G10 command to set the tool's offsets and temperatures (temperatures can also be set with M568).

**P** The 'P' field specifies the tool number. In RRF3, tool numbers may be between 0 and 49. In RRF2 they may be between 0 and 65535. If you use the M563 command with a P value for a tool that has already been defined, and you provide any other parameters, that tool is redefined using the new values you provide.

**D** The 'D' field specifies the drive(s) used by the tool - in the first example drives 0, 2 and 3. The 'D' field number corresponds to the 'E' parameter defined in the M584 command. '0' means first 'E' driver in M584 and so on. Drive 0 is the first drive in the machine after the movement drives (usually X, Y and Z). If there is no 'D' field the tool has no drives. Tools are driven using multiple values in the 'E' field of G1 commands, each controlling the corresponding drive in the 'D' field above, as follows:

G1 X90.6 Y13.8 E2.24:2.24:15.89 G1 X70.6 E0:0:42.4

The first line moves straight to the point (90.6, 13.8) extruding a total of 2.24mm of filament from both drives 0 and 2 and 15.98mm of filament from drive 3. The second line moves back 20mm in X extruding 42.4mm of filament from drive 3.

Alternatively, if the slicer does not support generating G1 commands with multiple values for the extrusion amount, the M567 command can be used to define a tool mix ratio.

**H** The 'H' field specifies the tool's heaters - in the first example heaters 1 and 3. Heater 0 is usually the hot bed (if any) so the first extruder heater is usually 1. If there is no H field the tool has no heaters. It is permissible for different tools to share some (or all) of their drives and heaters. So, for example, you can define two tools with identical hardware, but that just operate at different temperatures.

**F** The print cooling fan number(s) of the tool, default 0. Use this parameter if you are not using fan 0 as the print cooling fan for the tool you are defining. **You do not need to, and must not, list the fan numbers of thermostatic hot end fans here**. To use more than one print cooling fan for the tool, the definition would typically look like this:

M563 P0 D0 H1 F0:1 ; tool 0 uses extruder drive 0 and heater 1. Fan 0 and Fan 1 are use by tool 0 as print cooling fans.

**R** The spindle number mapped to this tool. (RRF \>= 3.3)

M563 P0 R0 ; assign spindle 0 to tool 0

**X, Y, Z** The X, Y and Z mapping options are used to create tools on machines with multiple independent X, Y and/or Z carriages. The additional carriages are set up as axes U, V etc. (see M584) and the X/Y/Z mapping option in M563 defines which carriage or carriages are used. Axes are mapped in the order XYZUVWABC, where X=0, Y=1, Z=2, U=3 etc, not by driver number.

**S** As shown in the example above the S parameter can be used to give a tool a name. RepRapFirmware supports an additional form of the M563 command. The command:

M563 S1

means add 1 (the value of the S parameter) to all tool numbers found in the remainder of the current input stream (e.g. the current file if the command is read from a file on the SD card), or until a new M563 command of this form is executed. The purpose of this is to provide compatibility between systems in which tool numbers start at 1, and programs such as slic3r that assume tools are numbered from zero.

RepRapFirmware maps the loaded filament on a per-extruder basis so if you have a mixing tool (one with more than one extruder), the **L** parameter tells the web interface which filament to display. If there is more than one extruder and the L parameter is omitted, no filament is displayed at all.

### Notes

In **RepRapFirmware 3.x**, in order to avoid the serialised object model getting very large, the P parameter (tool number) may not exceed 49.

M563 with just a P parameter just reports the existing configuration of the tool. Therefore, if you want to create a tool with no heaters and no extruders, you must provide at least one other parameter. For example, you can use the S parameter to name the tool.

RepRapFirmware allows the deletion of existing tools if M563 is called in this way:

M563 P1 D-1 H-1

