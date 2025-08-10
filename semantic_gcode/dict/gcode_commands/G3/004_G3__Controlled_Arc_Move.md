## G3: Controlled Arc Move

Counter-clockwise arc move. Supported by RRF 1.18 and later in FDM mode, RRF 1.20 and later in CNC mode, and RRF 2.01 and later in Laser mode.

### Usage

- G2 Xnnn Ynnn Znnn Innn Jnnn Ennn Fnnn (Clockwise Arc)

- G3 Xnnn Ynnn Znnn Innn Jnnn Ennn Fnnn (Counter-Clockwise Arc)

### Parameters

- **Xnnn** The position to move to on the X axis.

- **Ynnn** The position to move to on the Y axis.

- **Znnn** The position to move to on the Z axis.

- **Innn** The X coordinate of the arc centre **relative to the current X coordinate** (optional, ignored if R parameter is present).

- **Jnnn** The Y coordinate of the arc centre **relative to the current Y coordinate** (optional, ignored if R parameter is present).

- **Knnn** The Z coordinate of the arc centre **relative to the current Z coordinate** (optional, ignored if R parameter is present). (RRF v3.3 and later)

- **Ennn** The amount to extrude between the starting point and ending point.1

- **Fnnn** The feedrate per minute of the move between the starting point and ending point (optional, defaults to the current feed rate).

- **Rnnn** The radius of the arc (optional, RRF2.03 and later)

- **Snnn** (M452 Laser mode only) Laser power 0-255. See G1 S parameter for usage. Raster clustering not supported. (RRF 2.01 and later)

Either the R parameter must be provided, or at least one of I and J must be provided. To draw a complete circle, define the position of the centre using I and/or J and make X and Y the same as the current X and Y coordinates.

1Where a tool has more than one extruder drive then Ennn:nnn:nnn etc is supported to allow for the individual movement of each to be controlled directly. This overrides the extruder mix ratio set with M567

### Examples

G2 X90.6 Y13.8 I5 J10 E22.4 ; (Move in a Clockwise arc from the current point to point (X=90.6,Y=13.8), with a center point at (X=current_X+5, Y=current_Y+10), extruding 22.4mm of material between starting and stopping) G3 X90.6 Y13.8 I5 J10 E22.4 ; (Move in a Counter-Clockwise arc from the current point to point (X=90.6,Y=13.8), with a center point at (X=current_X+5, Y=current_Y+10), extruding 22.4mm of material between starting and stopping) G2 X100 Y50 R200 ; (draw a clockwise arc with radius 200 from the current position to X=100 Y=50)

### Notes

- If the required parameters are present in a G2/G3 command, RRF does not report errors in arc commands where the parameters describe an arc that is invalid. It will attempt to draw the 'best fit' arc, then complete the move with a linear move to the endpoint. For example, if the generated Gcode is: G1 X50 Y0 G2 X60 Y0 J10 RRF will aim to finish the move +10 along the X axis. The J parameter sets the arc centre to Y10 (J is relative to the current Y position). So it draws the arc, to X60 Y10 (a 3/4 circle going clockwise with G2), then a linear move to X60 Y0. If this last linear move is unwanted, the command should be \`G2 X60 Y10 J10\`. This is inconsistent with the NIST standard, where invalid arcs should result in an error. This is scheduled to be fixed in RRF 3.5.1.

- **RRF 3.3 and later:** Use of I, J and K parameters depends on the plane selected with G17, G18 or G19. Use I and J for the XY plane (G17), I and K for XZ plane (G18), and J and K for YZ plane (G19).

- RRF maintains a flag for feed rate (F parameter). For all G1/2/3 moves (and G0 moves in FDM mode) the following is true:

  - Each input channel (SD card, USB, http, telnet etc) has its own flag for feed rate.

  - At the end of running config.g at startup, the flag state is copied to all input channels. If no feed rate is specified in config.g, the default of 3000mm/min (50mm/s) is used.

  - The feed rate stored by the flag is used if the next G0/1/2/3 command doesn't include an F parameter.

  - The flag state is saved when a macro starts and is restored when a macro ends.

