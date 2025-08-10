## M556: Axis skew compensation

### Parameters

- **Snnn** Height of the measured distances

- **Xnnn** Deviation in X direction, or skew factor when S=1

- **Ynnn** Deviation in Y direction, or skew factor when S=1

- **Znnn** Deviation in Z direction, or skew factor when S=1

- **Pnnn** Apply XY compensation to Y axis instead of X (defaults to 0, requires RRF 3.2-b4 or newer)

### Examples

M556 S100 X0.7 Y-0.2 Z0.6 M556 ; reports the axis compensation in use Axis compensations - XY: 0.00700, YZ: -0.00200, ZX: 0.00600

### Description

This tells software the tangents of the angles between the axes of the machine obtained by printing then measuring a test part. When used without parameters, reports the axis skew compensation factors in use.

### Notes

- The S parameter is the length of a triangle along each axis in mm.

- The X, Y and Z figures are the number of millimeters of the short side of the triangle that represents how out of true a pair of axes is. The X figure is the error between X and Y, the Y figure is the error between Y and Z, and the Z figure is the error between X and Z. Positive values indicate that the angle between the axis pair is obtuse, negative acute.

- If you have calcuated the skew factor by other means, use S1 in M556 and the XYZ parameters are the skew factors.

- Printable parts for calibrating the deviation from orthogonality can be found on the \>RepRapPro Github repository.

- For an explanation of the measuring process and alternative methods, see Orthogonal axis compensation with M556.

