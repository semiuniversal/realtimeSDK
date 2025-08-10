## G30: Single Z-Probe

### Usage

- G30 \[Pnnn\] \[Xnnn\] \[Ynnn\] \[Znnn\] \[Hnnn\] \[Snnn\]

### Parameters

- **Pnnn** Probe point number

- **Xnnn** X coordinate

- **Ynnn** Y coordinate

- **Znnn** Z coordinate

- **Hnnn** Height correction

- **Snnn** Set parameter

- **Kn** (supported in RRF 3.01 and later, default 0) Z probe number

### Examples

G30 ; Probe the bed at the current XY position. When the probe is triggered, set the Z coordinate to the probe trigger height. G30 S-1 ; Probe the bed at the current XY position. When the probe is triggered, do not adjust the Z coordinate, just report the machine height at which the probe was triggered. G30 S-2 ; Probe the bed at the current XY position. When the probe is triggered, adjust the Z offset of the current tool to make the current position Z=0. G30 S-3 ; Probe the bed and set the Z probe trigger height to the height it stopped at (supported in RRF 2.03 and later) G30 P0 X20 Y50 Z-99999 ; Probe the bed at X20 Y50 and save the XY coordinates and the height error as point 0 G30 P3 X180 Y180 Z-99999 S4 ; Probe the bed at X180 Y180, save the XY coordinates and the height error as point 3 and calculate 4-point compensation or calibration G30 P3 X180 Y180 Z-99999 S-1 ; As previous example but just report the height errors

### Description

**Caution:** the XY coordinates are permitted to be outside the normal printable bed area! This is intentional, because some printers (e.g. delta printers) benefit from probing areas not used for printing.

**G30 without a P parameter**

This probes the bed starting at the current height. Depending on the value of the S parameter (0, -1, -2 or -3) it can be used to home the Z axis, to measure the Z probe trigger height, to adjust the Z offset of the current tool, or to adjust the Z probe trigger height.

- G30, G30 S0 or G30 S-4 or lower are just normal probes. When the probe is triggered, sets the Z coordinate to the probe trigger height.

- G30 S-1 probes and reports the Z value when the probe triggers.

- G30 S-2 probes and adjusts the tool Z offset to make the actual stop height match the configured value. A tool must be selected first when using G30 S-2.

- G30 S-3 probes and adjusts the probe trigger height to match the actual stop height.

**G30 with a P parameter**

This is used for operations that are performed after the printer has been homed and that require the height error at more than one probe point to be measured. These operations are typically performed in the bed.g file, with a G30 line for each probe point. With a Z parameter of -9999 or lower, the head moves to the specified XY coordinates and the dive height (set using the H parameter in the M558 command), and probes the bed.

For example, a bed.g for a Cartesian/CoreXY machine probing 3 points might be:

G28 ; home G30 P0 X20 Y190 Z-99999 ; probe point 0 near a leadscrew G30 P1 X180 Y190 Z-99999 ; probe point 1 near a leadscrew G30 P2 X100 Y10 Z-99999 S3 ; probe point 2 near a leadscrew and calibrate 3 motors

The **P parameter** is the probe point number for each G30 command. It should start at P0 and increase sequentially for each additional probe point.

The **S parameter** on the last G30 command in the sequence indicates that a complete set of points has been probed and instructs the firmware what sort of calibration to perform.

- Cartesian/CoreXY kinematics: S-1 will report the Z offset for each probed point, but no calibration is done. S0 specifies that the number of factors to be calibrated is the same as the number of points probed. Otherwise, the value indicates the number of factors to be calibrated, which must be no greater than the number of points probed, eg S3 in the above example with 3 points probed. See also: Bed levelling using multiple independent Z motors

- Linear delta kinematics: S-1 will report the Z offset for each probed point, but no calibration is done. S parameter values of 3, 4, 6, 7, 8 or 9 are for auto calibration. See Calibrating a Delta Printer, setting up the bed.g file for a more detailed explanation.

- Rotary delta kinematics: S-1 will report the Z offset for each probed point, but no calibration is done. S parameter values of 3, 4, 5, or 7 are for auto calibration (experimental).

NOTE: From RepRapFirmware version 1.09 to 3.0, the number of factors may be 3, 4 or 5 when doing old-style auto bed compensation on a Cartesian or CoreXY printer. This form of bed compensation has been removed in RRF 3.01 and later.

If a "normal" **Z parameter** is given instead of -9999 or lower, then the bed is not probed, but instead that value is used as if the Z probe had triggered at that height.

The **H parameter** is an optional height correction for that probe point. It allows for the Z probe having a trigger height that varies with XY position. The nominal trigger height of the Z probe (e.g. at bed centre) is declared in the Z parameter of the G31 command in the config.g file. When you probe using G30 and the probe triggers, the firmware will assume that the nozzle is at the nominal trigger height plus the value you have in the H parameter. For example, when doing delta calibration, it can account for the change in trigger height caused by effector tilt, if the vertical offset caused by the tilt has been measured.

The **K parameter** is applicable to all G30 commands. It is the Z probe number, default 0. It is not remembered between G30 commands, it always defaults to 0.

Using a Scanning Z Probes as a normal Z probe is supported in RRF 3.5.0 and later.

