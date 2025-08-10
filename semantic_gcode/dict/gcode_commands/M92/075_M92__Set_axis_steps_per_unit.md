## M92: Set axis steps per unit

### Parameters

- This command can be used without any additional parameters.

- **Xnnn** Steps per mm for the X drive

- **Ynnn** Steps per mm for the Y drive

- **Znnn** Steps per mm for the Z drive

- **Unnn** Steps per mm for the U drive

- **Vnnn** Steps per mm for the V drive

- **Wnnn** Steps per mm for the W drive

- **Ennn** Steps per mm for the extruder drive(s)

- **Snnn** Defines in which microstepping the above steps per unit are given. If omitted it will use the microstepping currently set by M350. This parameter is supported in RRF \>=2.03.

### Order dependency

If this command refers to any axes other than X, Y and Z then it must be later in config.g than the M584 command that creates those additional axes.

### Examples

M92 X80 Y80 Z80 M92 E420:500

### Notes

- Allows programming of steps per mm for motor drives. These values are reset to those set in config.g on power on, unless saved with M500. It will report the current steps/mm if you send M92 without any parameters.

- RepRapFirmware does not support individual motor settings where an axis has multiple motors connected to different stepper drivers. The first parameter specified will be used for all motors on the axis. You should use identical motors on any axis that has more than one motor to avoid unexpected behaviour. Example: If you have two motors on your Z axis, physically connected to Z and E0 stepper drivers, configured with M584 Z2:3, set M92 Z80, not M92 Z80:80

- RepRapFirmware uses floating point maths so it is possible to use floating point numbers for steps/mm.

