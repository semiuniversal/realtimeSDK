## M201: Set max acceleration

### Parameters

- **Xnnn** Acceleration for X axis

- **Ynnn** Acceleration for Y axis

- **Znnn** Acceleration for Z axis

- **Unnn** Acceleration for U axis

- **Vnnn** Acceleration for V axis

- **Wnnn** Acceleration for W axis

- **Ennn:nnn...** Acceleration for extruder drives

- **Tn.nn** Acceleration time, only available in experimental firmware bulds that support S-curve acceleration

### Order dependency

If this command refers to any axes other than X, Y and Z then it must be later in config.g than the M584 command that creates those additional axes.

### Examples

M201 X1000 Y1000 Z100 E2000

### Notes

Sets the acceleration that axes can do in mm/second^2 for print moves. For consistency with the rest of GCode movement this should be in mm/(minute^2), but that gives really silly numbers and one can get lost in all the zeros. So for this we use seconds.

To calculate the maximum acceleration values for an axis an online \>Maximum Acceleration Calculator can be used.

RepRapFirmware does not support individual motor settings where an axis has multiple motors connected to different stepper drivers. The first parameter specified will be used for all motors on the axis. You should use identical motors on any axis that has more than one motor to avoid unexpected behaviour. However, each extruder may have a different setting.

Example: If you have two motors on your Z axis, physically connected to Z and E0 stepper drivers, configured with M584 Z2:3, set M201 Z100, not M201 Z100:100.

In experimental 3.6.x firmware builds that support S-curve acceleration, the T parameter (acceleration time) specifies the time in seconds to go from zero to maximum acceleration. The jerk (maximum rate of change of acceleration) for each axis or extruder is then computed as the maximum acceleration for that axis or extruder divided by this acceleration time parameter. If the acceleration time is set to zero (which is the default) then S-curve acceleration is not used. If it is configured nonzero but not all local axes and extruders use phase stepping then S-curve acceleration is not used.

