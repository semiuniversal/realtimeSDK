## G10: Set workplace coordinate offset or tool offset

This form of the G10 command is recognised by having either or both of the L and P parameters. Supported on the Duet 2 series and later Duets.

### Parameters

- **Ln** (Default L1) Mode (see below)

- **Pnn** Tool number (default: current tool) if L=1, coordinate system number (default: current coordinate system) if L=2 or L=20

- **Xnnn** X offset

- **Ynnn** Y offset

- **U,V,W,A,B,C,D,...nnn** other axis offsets1

- **Znnn** Z offset2

**Modes**

- L1: this sets the tool offset, as if the L parameter was not present

- L2: this sets the origin of the coordinate system number specified by the P parameter (1 to 9) to the specified X, Y, Z... values

- L20: this is similar to L2 except that the origin is specified relative to the current position of the tool.

### Notes

1Tool offsets are applied after any X axis mapping has been performed. Therefore if for example you map X to U in your M563 command to create the tool, you should specify a U offset not an X offset. If you map X to both X and U, you can specify both offsets.

2It's usually a bad idea to put a non-zero Z value in as well unless the tools are loaded and unloaded by some sort of tool changer or are on independent carriages. When all the tools are in the machine at once they should all be positioned at the same Z height to avoid a lower tool colliding with the object while a higher tool is printing.

Tool offsets are given as the offset of the nozzle relative to the print head reference point, so the signs are opposite to what you might expect because tool offsets are subtracted from the required printing locations during printing.

Any parameter that you don't specify will automatically be set to the last value for that parameter. That usually means that you want explicitly to set Z0.0. RepRapFirmware will report the tool parameters if only the tool number is specified.

See also M585.

**Tool Offset Examples**

G10 P2 X17.8 Y-19.3 Z0.0 ; sets the offset for tool 2 to the X, Y, and Z values specified G10 L1 P2 X17.8 Y-19.3 Z0.0 ; sets the offset for tool 2 to the X, Y, and Z values specified

**Coordinate Offset Example**

Suppose the current machine coordinates are X110 Y110 Z20 and you want to make this the origin (i.e. X0 Y0 Z0) of the second coordinate system (accessible via G55) then there are two options:

1.  G10 L2 P2 X110 Y110 Z20

2.  G10 L20 P2 X0 Y0 Z0

The first example will set offsets to be subtracted from the current machine coordinates.

The second example will set the coordinates of the current position in the specified coordinate system directly.

### Order dependency

If this command refers to any axes other than X, Y and Z then it must appear later in config.g than the M584 command that creates those additional axes.

