## G53: Use machine coordinates

Supported on the Duet 2 and later Duets only.

### Examples

G53 G1 X50 Y50 Z20 ; these moves are in machine coordinates G1 X100 Y100 Z20 ; these moves, on the line after G53, are in the currently selected coordinate system

G53 causes all coordinates in movement commands on the remainder of the current line of GCode to be interpreted as machine coordinates, ignoring any coordinate offset of the workplace coordinate system currently in use, and also ignoring any tool offsets. G53 is not modal and must be programmed on each line on which it is intended to be active. On the following line without G53, the coordinate system reverts to the currently selected coordinate system.

See the \>NIST GCode Interpreter Version 3 standard for more details.

