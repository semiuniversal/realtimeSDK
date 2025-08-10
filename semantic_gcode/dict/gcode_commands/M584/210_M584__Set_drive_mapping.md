## M584: Set drive mapping

• RepRapFirmware 3.5 and later

• RepRapFirmware 3.4.x and earlier

##### Parameters

- **Xnnn** Driver number(s) for X motor(s)

- **Ynnn** Driver number(s) for Y motor(s)

- **Znnn** Driver number(s) for Z motor(s)

- **Ennn** Driver number(s) for E motor(s)

- **Unnn, Vnnn, Wnnn, Annn, ...** Additional axes and driver number(s). Available axis names are UVWABCDabcdef, additionally ghijklmnopqrstuvwxyz on Duet 3 MB6HC and MB6XD only.

- **Rn** (optional) 0 = axes created in this command are linear, 1 = axes created are rotational. If not present, RRF assumes UVW are linear and ABCD are rotational.

- **Sn** (optional) 0 = axes created in this command are treated as linear in feedrate calculations, 1 = axes created are treated as rotational in feedrate calculations. See section 2.1.2.5 of the NIST GCode standard for how the feedrate is interpreted. Default is S0 for linear axes and S1 for rotational axes (see the R parameter).

- **Pnnn** Number of visible axes, defaults to the total number of axes configured, excluding extruder drives.

##### Notes (3.5.x and later)

- You can use M584 to create additional axes - for example, to represent additional carriages on a machine with multiple independent X carriages. You can create new axes in any order.

- The maximum number of axes configurable is dependent on the firmware version, see: RepRapFirmware overview, firmware configuration limits

- **VERY IMPORTANT!** X (driver 0), Y (driver 1) and Z (driver 2) are assigned by default.

- There are no default extruder drives; all extruder drives must be declared explicitly using M584.

- Using M584 to map drivers to axes does not affect endstop inputs. Endstops inputs for each axis need to be defined.

##### Parameters

- **Xnnn** Driver number(s) for X motor(s)

- **Ynnn** Driver number(s) for Y motor(s)

- **Znnn** Driver number(s) for Z motor(s)

- **Ennn** Driver number(s) for E motor(s)

- **Unnn, Vnnn, Wnnn, Annn, ...** Additional axes and driver number(s). Available axis names depend on firmware version: UVW available from RepRapFirmware 1.16 UVWABC available from RepRapFirmware 1.19 and 2.x UVWABCD available from RepRapFirmware 3.0 thru 3.2 UVWABCDabcdefghijkl available in RepRapFirmware 3.4

- **Rn** (optional, supported in RRF 3.2 and later) 0 = axes created in this command are linear, 1 = axes created are rotational. If not present, RRF 3.2 and later assume UVW are linear and ABCD are rotational.

- **Sn** (optional, supported in RRF 3.2 and later) 0 = axes created in this command are treated as linear in feedrate calculations, 1 = axes created are treated as rotational in feedrate calculations. See section 2.1.2.5 of the NIST GCode standard for how the feedrate is interpreted. Default is S0 for linear axes and S1 for rotational axes (see the R parameter).

- **Pnnn** Number of visible axes, defaults to the total number of axes configured, excluding extruder drives.

##### Notes (3.4 and earlier)

- You can use M584 to create additional axes - for example, to represent additional carriages on a machine with multiple independent X carriages.

- In 1.20 and later firmware you can create new axes in any order. In earlier firmware versions, additional axes must be created in the order UVWABC.

- The maximum number of axes configurable is dependent on the firmware version, see: RepRapFirmware overview, firmware configuration limits

- **VERY IMPORTANT!** From **RRF 3.3**, X (driver 0), Y (driver 1) and Z (driver 2) are assigned by default. There are no default extruder drives; all extruder drives must be declared explicitly using M584.

- In **RRF 3.2.2 and earlier**, X (driver 0), Y (driver 1), Z (driver 2) and one extruder (driver 3) are assigned by default.

- Changing an existing drive (i.e. X, Y, Z or E) to a different driver with an **existing** assignment will result in two axes using the same driver, e.g. M584 X1 results in 'Driver assignments: X1 Y1 Z2'. Changing a drive to an unassigned driver results in the drive moving to the new driver, e.g. M584 Z3 results in 'Driver assignments: X1 Y1 Z3'. This may result in unexpected behaviour. It is best practice to define all drives explicitly as in the above example, if you are not using the default drive/driver assignments.

- Using M584 to map drivers to axes does not affect endstop inputs.

  - In RRF 3, endstops inputs for each axis need to be defined.

  - In RRF 2, endstop inputs XYZ are pre-allocated, after that they are allocated in the order in which axes are created. So if you create just one extra axes (e.g. U), it will use the E0 endstop input. If more than one axis is created in a single M584 command, endstop inputs are allocated to the new axes in axis creation order (see previous item). For example, M584 C5 U6 would allocate endstop input E0 to the U axis and E1 to the C axis.

### Order dependency

- M584 must come earlier in config.g than any M350 and M906 commands. If it creates new axes, it must also be earlier than any M92, M201, M203, M208, M350, M566, M574, M667 and M669 commands.

### Examples

M584 X0 Y1 Z2:3 E4:5:6 ; Driver 0 controls the X motor, 1 controls Y, 2 and 3 control Z motors, 4 5 and 6 control E motors

### Notes (all versions)

- Every driver that is assigned must have its current set using M906. Not setting a current will default a low current (approx 1/32 of the driver max current), however M906 will report 0 until a current is assigned. Disable the driver explicitly if you do not want any current sent to a driver that is assigned.

- Because GCode is normally case insensitive, axes that are represented by lowercase letters must be prefixed with a single quote character in GCode commands. For example, M584 'A1.2 would assign axis 'a' to driver 1.2, and G1 'A10 would move the 'a' axis to the 10mm or 10 degree position (or by 10mm or 10 degrees if in relative mode).

- **P** paramter: You can hide axes, starting with the last axis created, using the P parameter. Hidden axes have no homing buttons or jog controls in the user interface.

- If you create more than one axis in a M584 command, the axes are created in the order UVWABCDabcdefghijkl regardless of the order of the parameters in the M584 command. This affects which axes will be hidden if you use the M584 P parameter to hide axes. For example, M584 C5 U6 creates axes U and C in that order, so M584 P4 would hide the C axis, not the U axis. If you want to create the axes in the order C then U (so that M584 P4 hides the U axis), use two M584 commands: M584 C5 followed by M584 U6.

- RepRapFirmware does not support individual motor settings where an axis has multiple motors connected to different stepper drivers. The first parameter specified will be used for all motors on the axis. You should use identical motors on any axis that has more than one motor to avoid unexpected behaviour. Example: If you have two motors on your Z axis, physically connected to Z and E0 stepper drivers, configured with M584 Z2:3, set M92 Z80, not M92 Z80:80

- On the Duet 2 WiFi and Duet 2 Ethernet, if you configure multiple drivers for an axis, either all of them must be TMC2660 drivers on the Duet or a Duet expansion board, or none of them must be. This is to facilitate dynamic microstepping and other features of the TMC2660.

- On Duet 3 mainboards and expansion boards, the drivers are assigned with \<board CAN address\>.\<driver number\>. The mainboard is always CAN address 0, and is implied if omitted. Example:

> M584 X0 Y1 Z2 E3:4:1.0:1.1 The "0" index for the main board is implicit, this is equivalent to the previous example: M584 X0.0 Y0.1 Z0.2 E0.3:0.4:1.0:1.1

- If you assign an axis or extruder to one or more drivers, and later you want to reassign it to a different driver, then to ensure correct operation you must disable those axes/extruders using M18 before using M584 to reassign them. After using M584, you must set the motor current using M906 and the microstepping using M350. Example:

> ; Here axis B and extruder E0 have already been assigned and possibly moved, but we now want to reassign them M18 B E0 ; disable the axes/extruder that we are going to reassign M584 B3 E4 ; reassign them M906 B1000 E1000 ; set the motor currents M350 B16 E16 I1 ; set the microstepping

