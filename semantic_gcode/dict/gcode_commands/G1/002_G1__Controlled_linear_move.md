## G1: Controlled linear move

### Usage

- RRF2.02 and later, RRF3

  - G0 Xnnn Ynnn Znnn Ennn Fnnn Snnn Hnnn

  - G1 Xnnn Ynnn Znnn Ennn Fnnn Snnn Hnnn

- RRF2.01 and earlier

  - G0 Xnnn Ynnn Znnn Ennn Fnnn Snnn

  - G1 Xnnn Ynnn Znnn Ennn Fnnn Snnn

### Parameters

- Not all parameters need to be used, but at least one of XYZEF must be used

- **Xnnn** The position to move to on the X axis

- **Ynnn** The position to move to on the Y axis

- **Znnn** The position to move to on the Z axis

- **Ennn** The amount to extrude between the starting point and ending point 1

- **Fnnn** The feed rate per minute of the move between the starting point and ending point (if supplied)

- **Hnnn** Move type (RRF2.02 and later, RRF3)

- **Snnn**

  - In **RRF3**, the S parameter is used to set laser power, when switched into Laser mode (see M452); its use for defining move type is deprecated, use 'H' parameter instead.

  - In **RRF 3.5.0** and later, in the form **Snnn:nnn:...**, it is additionally used for laser raster clustering, see S parameter description below.

  - In **RRF2.02** and later, when switched into Laser mode (see M452), this parameter sets the laser power. When not switched into Laser mode, and always in firmware 2.01 and earlier, it defines the move type (see the description of the H parameter).

- **Rn** Return to the coordinates stored in restore point \#n (see G60). Any X, Y, Z and other axis parameters in the command are used as offsets from the stored position. Axes not mentioned are not moved, so use offset 0 for axes you want to restore to the stored value. For example, G1 R2 X0 Y0 Z2 will move to 2mm above the position stored in restore point 2 (i.e. after a toolchange).

- **Pnnnn** (supported only in some builds of RepRapFirmware) IOBITS parameter. Defines the states of output pins while this command is executed. See the M670 command.

1Where a tool has more than one extruder drive then Ennn:nnn:nnn etc is supported to allow for the individual movement of each to be controlled directly. This overrides the extruder mix ratio set with M567

**Very important!** If you use M452 to put your machine into Laser mode, when upgrading firmware from 2.01 or earlier to 2.02 or later you must replace all S parameters in G0/G1 commands in homing files etc. by H parameters. This is because S is now used to control laser power, for compatibility with programs that generate GCode files for laser cutters.

### Examples

G0 X12 ; (move to 12mm on the X axis) G0 F1500 ; (Set the feedrate to 1500mm/minute) G1 X90.6 Y13.8 E22.4 ; (Move to 90.6mm on the X axis and 13.8mm on the Y axis while extruding 22.4mm of material) G1 E10:10:5:0:0 F300 ; with a tool that has 5 extruder drives, extrude 10mm on drive 0, 10mm on drive 1, 5mm on drive 2 and 0mm on drive 3 and 4.

### Notes

RepRapFirmware treats G0 and G1 in the same way **except** as follows:

- On SCARA and similar architectures that normally require linear motion to be approximated by short segments, a single continuous non-segmented movement will be used if this can be done without the print head dropping below the current Z height.

- In Laser and CNC mode, G0 moves are executed at the maximum feed rate available, to comply with the NIST GCode standard, This feed rate is set by the M203 command.

- RRF maintains a flag for feed rate (F parameter). For all G1/2/3 moves (and G0 moves in FDM mode) the following is true:

  - Each input channel (SD card, USB, http, telnet etc) has its own flag for feed rate.

  - At the end of running config.g at startup, the flag state is copied to all input channels. If no feed rate is specified in config.g, the default of 3000mm/min (50mm/s) is used.

  - The feed rate stored by the flag is used if the next G0/1/2/3 command doesn't include an F parameter.

  - The flag state is saved when a macro starts and is restored when a macro ends.

#### G0/G1 H and S parameter

The meaning of the H parameter is as follows:

- **H0** no special action (default)

- **H1** terminate the move when the endstop switch is triggered and set the axis position to the axis limit defined by M208. On delta printers, H1 also selects individual motor mode as for H2. Normally used with relative motor coordinates (see G91).

- **H2** Individual motor mode. X refers to the X motor or motors, Y refers to the Y motor or motors, and so on. Normally used with relative motor coordinates (see G91).

- **H3** terminate the move when the endstop switch is triggered and set the axis limit to the current position, overriding the value that was set by M208.

- **H4** terminate the move when the endstop switch is triggered and update the current position (supported in RRF 3.2 or later)

The meaning of the S parameter has changed over successive versions of RepRapFirmware. It currently sets the laser power when M452 Laser mode is set, but was also used for homing behaviour. See below.

• RRF 3

• RRF 2.02 to 2.05.1

• RRF 2.01 and earlier

In **RRF 3.x**:

- **H** parameter controls movement type

- **S** parameter sets laser power with range of 0-255 when M452 Laser mode set, otherwise ignored. M452 R\[0-255\] parameter sets the maximum laser power, the G1 S parameter sets a proportion of this.

| **RRF 3, G0/G1 H parameter BEFORE and AFTER M452 Laser Mode.** |  |
|----|----|
| **Parameter** | **Meaning** |
| G1 Xnnn Ynnn Znnn H0 (default) | Ignore endstops while moving but apply axis limits. Don't allow movement if the axis has not previously been homed unless M564 has been used to allow it. |
| G1 Xnnn Ynnn Znnn H1 | Sense endstops while moving (ignoring the axis limits) and stop when the endstop is hit. On Delta, Scara and Polar machines, axis letters refer to individual motors. |
| G1 Xnnn Ynnn Znnn H2 | Ignore endstops and axis limits while moving. Also ignore if axis has not been homed. On Delta, Scara, Polar and Core XY machines axis letters refer to individual towers (delta) or individual joint motors (scara) or A/B motors (CoreXY). |
| G1 Xnnn Ynnn Znnn H3 | Sense endstops while measuring axis length, setting the appropriate M208 limit to the measured position at which the endstop switch triggers. |
| G1 Xnnn Ynnn Znnn H4 | Sense endstops while moving, update the current position at which the endstop switch triggers (supported in RRF 3.2 and later). |

| **RRF 3, G0/G1 S parameter BEFORE M452 Laser Mode.** |
|------------------------------------------------------|
| S parameter is ignored                               |

| **RRF 3, G0/G1 S parameter AFTER M452 Laser Mode.** |
|-----------------------------------------------------|
| S parameter sets laser power with range of 0-255.   |

In **RRF 3.5.0 and later**:

- **Snnn:nnn:...** parameter is additionally used for 'Raster clustering' mode. Up to 8 S parameters are supported.

To increase the speed of raster engraving, raster clustering mode has been implemented. A single G1 move is split up into equal portions by multiple values in the S parameter, eg G1 X50 S100:50:25:50:100 would move 50mm and change the laser power every 10mm. This allows more commands to fit in the command buffer, to keep speed up. Laser cutter software such as Lightburn supports raster clustering.

In **RRF 2.02 to 2.05.1**:

- **H** parameter controls movement type.

- **S** parameter controls movement type BEFORE M452 Laser Mode is set. S parameter sets laser power with range of 0-255 AFTER M452 Laser mode set. M452 R\[0-255\] parameter sets the maximum laser power, the G1 S parameter sets a proportion of this.

| **RRF 2.02 to 2.05.1, G0/G1 H parameter BEFORE and AFTER M452 Laser Mode.** |  |
|----|----|
| **Parameter** | **Meaning** |
| G1 Xnnn Ynnn Znnn H0 | Ignore endstops while moving. |
| G1 Xnnn Ynnn Znnn H1 | Sense endstops while moving (ignoring the axis limits). On Delta (only), axis letters refer to individual towers. |
| G1 Xnnn Ynnn Znnn H2 | Ignore endstops while moving. Also ignore if axis has not been homed. On Delta and Core XY, axis letters refer to individual towers. |
| G1 Xnnn Ynnn Znnn H3 | Sense endstops while measuring axis length, setting the appropriate M208 limit to the measured position at which the endstop switch triggers. |

| **RRF 2.02 to 2.05.1, G0/G1 S parameter BEFORE M452 Laser Mode.** |  |
|----|----|
| **Parameter** | **Meaning** |
| G1 Xnnn Ynnn Znnn S0 | Ignore endstops while moving. |
| G1 Xnnn Ynnn Znnn S1 | Sense endstops while moving. On Delta (only), axis letters refer to individual towers. |
| G1 Xnnn Ynnn Znnn S2 | Ignore endstops while moving. Also ignore if axis has not been homed. On Delta and CoreXY, axis letters refer to individual towers. |
| G1 Xnnn Ynnn Znnn S3 | Sense endstops while measuring axis length, and set the appropriate M208 limit to the measured position at which the endstop switch triggers. |

| **RRF 2.02 to 2.05.1, G0/G1 S parameter AFTER M452 Laser Mode.** |
|------------------------------------------------------------------|
| S parameter sets laser power with range of 0 to 255.             |

In **RRF 2.01 and earlier**:

- **S** parameter controls the movement type. There is no H parameter or M452 Laser Mode.

| **RRF_2.01 and earlier, G0/G1 S parameter** |  |
|----|----|
| **Parameter** | **Meaning** |
| G1 Xnnn Ynnn Znnn S0 | Ignore endstops while moving. |
| G1 Xnnn Ynnn Znnn S1 | Sense endstops while moving. On Delta (only), axis letters refer to individual towers. |
| G1 Xnnn Ynnn Znnn S2 | Ignore endstops while moving. Also ignore if axis has not been homed. On Delta and CoreXY, axis letters refer to individual motors. |
| G1 Xnnn Ynnn Znnn S3 | Sense endstops while measuring axis length, and set the appropriate M208 limit to the measured position at which the endstop switch triggers. |

#### Feedrate

G1 F1500 G1 X50 Y25.3 E22.4

In the above example, we set the feedrate to 1500mm/minute on line 1, then move to 50mm on the X axis and 25.3mm on the Y axis while extruding 22.4mm of filament between the two points.

G1 F1500 G1 X50 Y25.3 E22.4 F3000

However, in the above example, we set a feedrate of 1500mm/minute on line 1, then do the move described above accelerating to a feedrate of 3000 mm/minute as it does so. The extrusion will accelerate along with the X and Y movement, so everything stays synchronized.

Feedrate is treated as simply another variable (like X, Y, Z, and E) to be linearly interpolated. This gives complete control over the acceleration and deceleration of the printer head in such a way that ensures that everything moves smoothly together, and the right volume of material is extruded at all points. The feedrate specified may not be reached due to a lower feedrate limit being configured, or the move being too short for the axis to accelerate and decelerate in time.

**For CNC users especially: RRF has a default minimum movement speed of 0.5mm/sec.** In firmware 2.03 and later this can be changed using the I ('i') parameter of the M203 command.

#### Maximum Length of Moves

##### Microstep counter limit

The firmware keeps track of the exact number of microsteps sent to each movement axis using a 32-bit signed integer microstep counter, this limits the maximum absolute move and axis length to (2^31 - 1) microsteps. This does not apply to extruder drives. The firmware multiplies the requested axis position (after adding any offsets) by the steps/mm to get the required microstep position and the microstep counter accumulates across multiple moves, as the axis position increases it increments, as it decreases it decrements. The maximum size of the microstep counter is only an issue for situations where an axis needs to accommodate one or more moves or an overall axis length that would overflow the counter (i.e. an extremely long axis, or an extremely high resolution axis). In typical uses this is not a concern, for example on a standard linear axis using 160 microsteps/mm an axis of over 13km is supported. In cases where the microstep counter is not sufficient (e.g. a very high resolution rotary axis moving for a very long time) G92 can be used to set the origin to a new point on the axis and thus reset the counter.

In a similar manner, if the requested axis position gets very large then accuracy will suffer, because it is held and calculated as a 32-bit float.

##### Move time limit

The maximum duration of a single move that RRF can handle is about 47 minutes on Duet 3 (which is 2^31 cycles of the 750kHz clock) and 38 minutes on Duet 2. If very long running moves are required (e.g. a long running rotary axis) then split the move into several commands each taking no more than about 30 minutes.

