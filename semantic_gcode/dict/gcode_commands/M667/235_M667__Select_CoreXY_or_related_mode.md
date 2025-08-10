## M667: Select CoreXY or related mode

This command is deprecated from RRF 2.03, and removed from RRF 3.5 and later. Use M669 instead.

### Parameters

- **Snnn** CoreXY mode

- **Xnnn** X axis scale factor (RRF 2.02 and earlier)

- **Ynnn** Y axis scale factor (RRF 2.02 and earlier)

- **Znnn** Z axis scale factor (RRF 2.02 and earlier)

### Order dependency

- M667 must come earlier in config.g than any M671 command.

### Examples

M667 S1

### Notes

- M667 S0 selects Cartesian mode (unless the printer is configured as a delta using the M665 command). Forward motion of the X motor moves the head in the +X direction. Similarly for the Y motor and Y axis, and the Z motor and Z axis. This is the default state of the firmware on power up.

- M667 S1 selects CoreXY mode. Forward movement of the X motor moves the head in the +X and +Y directions. In firmware 1.19 and later, forward movement of the Y motor moves the head in the +X and -Y directions.

- M667 S2 selects CoreXZ mode. Forward movement of the X motor moves the head in the +X and +Z directions. In firmware 1.19 and later, forward movement of the Z motor moves the head in the -X and +Z directions.

- In versions of RRF prior to 2.03, additional parameters X, Y and Z may be given to specify factors to scale the motor movements by for the corresponding axes. For example, to specify a CoreXZ machine in which the Z axis moves 1/3 of the distance of the X axis for the same motor movement, use M667 S2 Z3. The default scaling factor after power up is 1.0 for all axes.

- In RRF 2.03 and later the XYZ parameters are no longer supported. Use the M669 XYZ parameters to alter the movement matrix instead.

- To change the motor directions, see the M569 command.

