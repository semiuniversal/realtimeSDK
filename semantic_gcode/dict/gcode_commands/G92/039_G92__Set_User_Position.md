## G92: Set User Position

### Parameters

- This command can be used without any additional parameters.

- **Xnnn** new X axis position

- **Ynnn** new Y axis position

- **Znnn** new Z axis position

- **Ennn** new extruder position

### Examples

G92 X10 E90

Allows manual specification of the axis positions by setting the current user position to the values given. The machine position is updated as necessary taking into account tool offsets and workplace coordinate offsets. The example above would set the machine's X user coordinate to 10, and the extruder coordinate to 90. No physical motion will occur. In RepRapFirmware, a G92 without coordinates does nothing.

