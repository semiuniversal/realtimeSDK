## M114: Get Current Position

### Examples

M114

This reports the X, Y, Z (,U, V, W, A, B, C if configured) and E coordinates to the host. The coordinates reported are those at the end of the last completed move.

For example, the machine returns a string such as:

C: X:10.000 Y:20.000 Z:5.000 E:51.000 E0:51.0 E1:0.0 Count 800 1600 2000 Machine 10.00 20.00 5.00 Bed comp 0.00

The first E value (without an extruder number) is the current virtual extruder position, and is included for the benefit of GCode senders that don't understand multiple extruders. Note that the virtual extruder position is only incremented in absolute extrusion mode (M82), it can also be accessed in the object model at move.virtualEPos. M92 E"nn" sets the virtual extruder position to the number specified as "nn". The virtual E position is reset when a print is started, as are the individual E0, E1, etc counters. See the M82 section of this page for more information on absolute extrusion, the virtual extruder concept, and why it is generally better to use relative extrusion.

The E0, E1 etc. values are for each individual extruder.

The Count values are the microstep positions of each individual motor or motor group. The Machine values are the machine axis coordinates, which are calculated from the user coordinates by accounting for workplace coordinate offsets, bed compensation, axis skew compensation, babystepping and Z lift.

Note: there is no agreed definition of what the response to M114 should be. We try to keep the M114 response compatible with other firmwares as far as we can, but this is not always possible. Users writing applications which need to fetch current positions from RepRapFirmware 3 are recommended to use object model queries instead.

