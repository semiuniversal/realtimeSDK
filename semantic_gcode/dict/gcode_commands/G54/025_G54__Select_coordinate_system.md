## G54: Select coordinate system

Selects coordinate system 1. Supported on the Duet 2 and later Duets only.

G54 selects coordinate system 1, G55 selects coordinate system 2 etc. up to G59 which selects coordinate system 6. G59.1 selects coordinate system 7, G59.2 selects system 8 and G59.3 selects system 9.

Initially, coordinate system 1 is in use, and all coordinate systems have zero offset from the machine coordinates. To set coordinate system offsets, use the G10 command with the L2 parameter.

See the \>NIST GCode Interpreter Version 3 standard for more details.

