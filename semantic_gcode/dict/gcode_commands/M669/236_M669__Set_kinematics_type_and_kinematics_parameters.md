## M669: Set kinematics type and kinematics parameters

Selects the specified kinematics, then uses the other parameters to configure it. If the K parameter is missing then the other parameters are used to update the configuration data for the current kinematics. If no parameters are given then the current kinematics and configuration parameters will be reported.

RepRapFirmware 2.03 and later can support any kinematics for which the movement of each axis is a linear combination of the movement of the motors. The relationship between axis movement and motor movement is defined by a matrix. So K0, K1, K2, K5, K8 and K11 all select the same kinematics, but with different default matrices.

### Parameters

#### RRF 3.7.0 and later:

- **K"name"** Kinematics type. "name" must be one of: "cartesian", "coreXY", "coreXZ", "linearDelta", "scara", "coreXYU", "hangprinter", "polar", "coreXYUV", "fiveBarScara", "rotaryDelta", "markForged" or a custom kinematics name if using a custom build of RRF with additional kinematics support. Not all standard builds of RRF support all kinematics, in particular Duet 2 builds support a limited number. The K parameter may also be one of the kinematics numbers supported by RRF 3.6 and earlier, however this form of M669 is deprecated and may not be supported in future firmware versions.

#### RRF 3.6.x and earlier:

- **Knnn** Kinematics type: 0 = Cartesian, 1 = CoreXY, 2 = CoreXZ, 3 = linear delta, 4 = serial SCARA, 5 = CoreXYU, 6 = Hangprinter, 7 = polar, 8 = CoreXYUV, 9 = five-bar parallel SCARA, 10 = rotary delta, 11 = Markforged

• Cartesian, CoreXY/XZ/XYU/XYUV, Markforged

• Linear Delta

• Serial SCARA

• Polar

RRF 2.03 and later only

##### Parameters

- **Xnn:nn:nn...** Motor movement coefficients required to move X axis (first row of matrix)

- **Ynn:nn:nn...** Motor movement coefficients required to move Y axis (second row of matrix)

- **Znn:nn:nn...** Motor movement coefficients required to move Z axis (third row of matrix)

- **Unn:nn:nn..., Vnn:nn:nn... etc.** Motor movement coefficients required to move U, V... axes (fourth and subsequent rows of matrix)

- **Snnn** Segments per second (RRF 3.3 and later)

- **Tnnn** Minimum segment length (mm) (RRF 3.3 and later)

##### Notes

- All these parameters are optional. The movement coefficient matrices are initialised to suitable values for the kinematics type you selected in the M667 or M669 command, but you can modify them using these parameters. If you send M669 with no parameters, the existing matrix will be reported.

- When CoreXZ kinematics is selected, the default matrix assumes there is a 3:1 reduction on the Z axis, as in the original CoreXZ design described at on the \>RepRap forums here. If your CoreXZ printer has a different reduction or no reduction then you will need to use the Z parameter to change the Z line of the matrix. For example, if there is no Z reduction then use Z1:0:-1.

- A modified line overrides the default for that axis row, so for example sending M669 K0 X1:0:1 Y0:1:0 Z1:0:-1, produces a CoreXZ matrix, not a cartesian matrix. (The K0 is completely overridden in a 3 axis system). To that end if you are using a modified matrix, it is best to fully specify the matrix to avoid confusion. If you fully override the matrix, the "K" parameter can be any of the linear K parameters.

- In RRF 3, segmentation is not normally used unless the S and/or T parameter is given. Segmenting moves is useful when faster pause response is wanted.

- Unlike some other firmwares, for CoreXY and similar kinematics RRF allows for the fact that the maximum speed and acceleration the machine is capable of varies with the direction of the move. This means that for best performance you should use higher M201 and M203 values in RRF than in those firmwares. See Configuring RepRapFirmware for CoreXY Printer

- For more information on configuring a machine with specific kinematics, see Machine configuration

##### Examples

Response to M669 (no parameters) on simple Cartesian machine:

M669 Kinematics is Cartesian, no segmentation, matrix:: 1.00 0 0 0 1.00 0 0 0 1.00

CoreXY with extra Markforged U axis (see \>this forum post for an example):

M669 K1 X1:1:0:0 Y1:-1:0:-1 Z0:0:1:0 U0:0:0:1

Note U motor values in X, Y, Z and U parameters come after the Z motor values. M669 reports:

M669 Kinematics is CoreXY, no segmentation, modified matrix: 1.00 1.00 0 0 1.00 -1.00 0 -1.00 0 0 1.00 0 0 0 0 1.00

RRF 2.03 and later only

##### Parameters

- **Xnn:nn:nn...** Extruder offset from nozzle in X

- **Ynn:nn:nn...** Extruder offset from nozzle in X

- **Snnn** Segments per second (RRF 3.3 and later)

- **Tnnn** Minimum segment length (mm) (RRF 3.3 and later)

##### Notes

- This is used when a 4th axis is added to a linear Delta, to carry the extruder and follow in Z. It specifies the XY offsets of the extruder outputs on additional towers, relative to machine centre in the M669 command. See Adding additional towers to carry flying extruders.

- In RRF 3.6.0 and later, delta kinematics now uses segmentation. The default segmentation parameters (max 100 segments/second, minimum segment length 0.2mm) should be suitable for most delta printers. In earlier versions of RRF 3.x, segmentation is not used unless the S and/or T parameter is given. Segmenting moves is useful when faster pause response is wanted.

- For more information on configuring a machine with specific kinematics, see Machine configuration

##### Parameters

- **Pnnn** Proximal arm length (mm)

- **Dnnn** Distal arm length (mm)

- **Annn:nnn** Proximal arm joint movement minimum and maximum angles, in degrees anticlockwise seen from above relative to the X axis

- **Bnnn:nnn** Proximal-to-distal arm joint movement minimum and maximum angles, in degrees anticlockwise seen from above relative to both arms in line

- **Cnnn:nnn:nnn** Crosstalk factors. The first component is the proximal motor steps to equivalent distal steps factor, the second is the proximal motor steps to equivalent Z motor steps factor, and the third component is the distal motor steps to equivalent Z motor steps factor.

- **Rnnn** (optional, RRF 2.03 and later only) Minimum permitted printing radius from the proximal axis. If not specified, it will be calculated to be slightly larger than the distance between nozzle and proximal axis when the distal axis is homed.

- **Snnn** Segments per second (because smooth XY motion is approximated by means of segmentation)

- **Tnnn** Minimum segment length (mm) (because smooth XY motion is approximated by means of segmentation)

- **Xnnn** X offset of bed origin from proximal joint

- **Ynnn** Y offset of bed origin from proximal joint

##### M669 K4 P300 D250 A-90:90 B-135:135 C0:0:0 S100 X300 Y0

Notes

- The minimum and maximum arm angles are also the arm angles assumed by the firmware when the homing switches are triggered. The P, D, A and B parameters are mandatory. The C, X and Y parameters default to zero, and the segmentation parameters default to firmware-dependent values.

- For more information on configuring a machine with specific kinematics, see Machine configuration

##### Parameters

- **Annn** Maximum turntable acceleration in degrees per second^2

- **Fnnn** Maximum turntable speed in degrees per second

- **Hnnn** Radius of the nozzle from the centre of the turntable when the radius arm homing switch is triggered

- **Raaa:bbb** Minimum (aaa) and maximum (bbb) radius on the turntable reachable by the nozzle.

- **Snnn** Segments per second (because smooth XY motion is approximated by means of segmentation)

- **Tnnn** Minimum segment length (mm) (because smooth XY motion is approximated by means of segmentation)

- **Xnnn** X offset of bed origin from turntable centre (not yet implemented)

- **Ynnn** Y offset of bed origin from proximal joint (not yet implemented)

##### Notes

- The **A** and **F** parameters only apply to normal moves not to G1 H2 (individual motor) moves. The intention is that when printing well away from the centre, the normal X and Y limits set by M201 and M203 are sufficient. When printing at a small radius, movement may need to be slowed down to limit the turntable speed and acceleration.

- There is currently no facility for offsetting the radius arm sideways from the centre of rotation of the turntable, or for moving the origin.

- For more information on configuring a machine with specific kinematics, see Machine configuration

