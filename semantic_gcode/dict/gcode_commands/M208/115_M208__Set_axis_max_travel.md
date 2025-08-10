## M208: Set axis max travel

### Parameters

- **Snnn** 0 = set axis maximum (default), 1 = set axis minimum

- **Xnnn** X axis limit

- **Ynnn** Y axis limit

- **Znnn** Z axis limit

Alternative (from RepRapFirmware 2.02/1.23)

- **Xaaa:bbb** X axis minimum and maximum limit

- **Yaaa:bbb** Y axis minimum and maximum limit

- **Zaaa:bbb** Z axis minimum and maximum limit

### Order dependency

If this command refers to any axes other than X, Y and Z then it must be later in config.g than the M584 command that creates those additional axes.

### Examples

M208 X200 Y200 Z90 ; set axis maxima M208 X-5 Y0 Z0 S1 ; set axis minima M208 X-5:200 Y0:200 Z0:90 ; set axis minima and maxima

### Notes

The values specified set the software limits for axis travel in the specified direction. The axis limits you set are also the positions assumed when an endstop is triggered.

The min/max axis positions are +/- (2^31 - 1) microsteps. Position accuracy will start to suffer when the positions are outside approx. +/- 2^24 microsteps, because it is held and calculated as a 32-bit float. See also this note on maximum length of moves in the G1 Gcode entry.

The M208 minimum Z value applies to deltas. The M208 XY min/max and Z max values don't.

