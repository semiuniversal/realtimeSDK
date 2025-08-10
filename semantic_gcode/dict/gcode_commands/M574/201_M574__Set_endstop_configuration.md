## M574: Set endstop configuration

• M574 - RepRapFirmware 3

• M574 - RepRapFirmware 2.x and earlier

##### Parameters

- **Xnnn** Position of X endstop: 0 = none, 1 = low end, 2 = high end.

- **Ynnn** Position of Y endstop: 0 = none, 1 = low end, 2 = high end.

- **Znnn** Position of Z endstop: 0 = none, 1 = low end, 2 = high end.

- **P"pin_name"** Defines the pin name(s) that the endstop(s) for the specified axis are connected to, see Pin Names. Needed when S=1. May need ! before pin name to invert signal, or ^ to enable the pullup resistor, for example on the Duet 2 expansion header if using the pins directly without a duex5.

- **Snnn** 1 = switch-type (eg microswitch) endstop input, 2 = Z probe (when used to home an axis other than Z), 3 = single motor load detection, 4 = multiple motor load detection (see Notes).

- **Knnn** Optional Z probe number (3.5 or later, only for S2, defaults to 0)

To use two Z motors using independent homing switches, declare two Z motors in M584, then declare two pins for Z endstops in a single M574 command. Example

M584 X0 Y1 Z2:3 E4 M574 Z1 S1 P"io2.in+io3.in" ; Z axis with two motors, individual min endstops, active high

The order of endstop switch pin names in M574 must match the order of Z motor driver numbers in M584. When homing Z, RRF3 homes the motors of the axis at the same time, independently to their defined endstops. See Axis levelling using endstops.

##### Notes

- In RRF3, the M574 command allows for more flexibility than in RRF2. This includes supporting axes defined with multiple motors and multiple endstops (one per motor), use of non-default endstop inputs, and re-assigning endstop inputs.

- Use a separate M574 command for each axis. For historical reasons, RRF currently allows multiple endstops to be declared using M574 in some situations, but this facility may be withdrawn in future versions.

- For endstop types other than stall detecton, parameter **P** gives the pin name(s) for the endstop(s) for the specified axis. If the number of pins matches the number of motors assigned to that axis, motors will be stopped individually when their endstop switches trigger.

- For active low endstops, use type S1 and invert the input by prefixing the pin name with '!', for example M574 X1 S1 P"!xstop". Invert the input when using an NPN output normally-open inductive or capacitive sensor, or using a normally-open switch (not recommended, use a normally-closed switch instead).

- The S2 option of M574 is intended for use only when axes other than Z are using the Z probe for homing. The only printers known to do this are the RepRapPro Ormerod, Huxley Duo, and Mendel Tricolour machines. When using the Z probe to home Z, M574 Z has no bearing on the probe setup or usage.

- A Z probe and a Z endstop (e.g. a switch) can both be configured at the same time. G30 commands will use the probe setup with M558, and G1 H1 Z moves use the endstop configured with M574 Z.

- Endstop type S4 means use motor stall detection (like S3) but if there are multiple motors dedicated to a single axis, stop each one individually as it stalls. S3 means use motor stall detection but if there are multiple motors dedicated to a single axis, stop all those motors when the first one stalls.

- Pull up resistors on Duet 2/Duex5 inputs should be configured for connecting a digital inputs (like a switch, BLtouch, etc) only on inputs not labelled "n"Stop (xstop, ystop etc).

- To un-configure an endstop and free up any associated input pins, set the endstop position of that axis to 'none'. For example, M574 X0 will delete the X endstop and free up any inputs that it was using.

##### Parameters

- **Xnnn** Position of X endstop: 0 = none, 1 = low end, 2 = high end.

- **Ynnn** Position of Y endstop: 0 = none, 1 = low end, 2 = high end.

- **Znnn** Position of Z endstop: 0 = none, 1 = low end, 2 = high end.

- **E** Select extruder endstops to define active high or low (RepRapFirmware 1.16 and earlier only)

- **Snnn** Endstop type: 0 = active low endstop input, 1 = active high endstop input, 2 = Z probe, 3 = motor load detection

##### M574 X1 Y2 Z0 S1 ; X endstop at low end, Y endstop at high end, no Z endstop, all active high

Axis levelling using endstops.

In RepRapFirmware 1.16 and earlier, the M574 command with E parameter was used to specify whether a Z probe connected to the E0 endstop input produces an active high (S1) or active low (S0) output. In RepRapFirmware 1.17 and later, use the I parameter of the M558 command instead.

