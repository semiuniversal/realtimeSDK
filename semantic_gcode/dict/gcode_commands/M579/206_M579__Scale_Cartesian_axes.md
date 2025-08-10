## M579: Scale Cartesian axes

On a Cartesian RepRap you can get prints exactly the right size by tweaking the axis steps/mm using the M92 GCode. But this does not work so easily for Delta and other RepRaps for which there is cross-talk between the axes. This command allows you to adjust the X, Y, and Z axis scales directly. So, if you print a part for which the Y length should be 100mm and measure it and find that it is 100.3mm long then you set Y0.997 (= 100/100.3).

### Parameters

- **Xnnn** Scale factor for X axis

- **Ynnn** Scale factor for Y axis

- **Znnn** Scale factor for Z axis

- **U, V, W, A, B, C** Scale factors for additional axes

### Examples

M579 X1.0127 Y0.998

### Notes

On a suitable-configured IDEX printer, a scaling factor of -1 for the U axis can be used to turn a ditto print into a mirror image print.

