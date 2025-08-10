## M665: Set delta configuration

Set the delta calibration variables

### Parameters

- **Lnnn** or **Lnnn:nnn:...** Diagonal rod length

- **Rnnn** Delta radius

- **Bnnn** Safe printing radius

- **Hnnn** Nozzle height above the bed when homed after allowing for endstop corrections

- **Xnnn** X tower position correction

- **Ynnn** Y tower position correction

- **Znnn** Z tower position correction

### Examples

M665 L250 R160 B80 H240 X0 Y0 Z0

### Notes

The **X**, **Y** and **Z** parameters are the X, Y and Z tower angular offsets from the ideal (i.e. equilateral triangle) positions, in degrees, measured anti-clockwise looking down on the printer.

In RRF 2.03 and later, multiple **L** values can be provided, for example:

L260.1:260.2:260.0

The values are the lengths of the rods to the X, Y and Z towers respectively. If more than 3 values are provided, the firmware assumes that there are as many towers as L values up to the maximum supported (currently 6). The XY coordinates of the additional towers must be defined subsequently using the M669 command. If only one L value is provided, the machine is assumed to have 3 towers with all rods having the same length.

