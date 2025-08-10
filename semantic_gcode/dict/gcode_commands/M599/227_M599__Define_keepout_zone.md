## M599: Define keepout zone

Supported in firmware version 3.5.0 later on Duet 3 main boards

### Parameters

- **Pn** Keepout zone number, default 0

- **Sn** (optional) S1 = activate keepout zone (default if any axes are specified), S0 = deactivate keepout zone

- **X,Y...aaa:bbb** Axis identifier and limits for that axis

### Example

M599 X10:25 Y0:20

### Description

This command establishes a "no entry" zone for the toolhead reference point. If any G0/G1/G2/G3 move attempts to move the toolhead inside the no entry zone, the job will be aborted with an error message.

The X, Y etc. coordinates are machine coordinates, i.e. the area which the tool head reference point is not allowed to enter.

### Notes

- You may specify any number of axes, up to the number that the machine has.

- If no axes are specified and the S parameter is not provided then the parameters and enabled/disabled state of the existing keepout zone will be reported.

- Movement commands (G0, G1, G2 and G3) will normally be checked before starting the move.

- The number of keepout zones supported is implementation dependent. In RRF 3.5.0 only one is supported.

