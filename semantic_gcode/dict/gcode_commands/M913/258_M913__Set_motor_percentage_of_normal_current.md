## M913: Set motor percentage of normal current

This allows motor currents to be set to a specified percentage of their normal values as set by M906. It can be used (for example) to reduce motor current during course homing, to make homing quieter or to reduce the risk of damage to endstops, and to reduce current while loading filament to guard against the possibility of feeding too much filament. Use M913 again with the appropriate parameters set to 100 to restore the normal currents.

### Parameters

- **X, Y, Z, E** Percentage of normal current to use for the specified axis or extruder motor(s)

### Examples

M913 X50 Y50 Z50 ; set X Y Z motors to 50% of their normal current M913 E30:30 ; set extruders 0 and 1 to 30% of their normal current

### Notes

When M913 is executed, it does not wait for all motion to stop first (unlike M906). This is so that it can be used in the M911 power fail script. When using M913 elsewhere, you will typically want to use M400 immediately before M913.

RepRapFirmware does not support individual motor settings where an axis has multiple motors connected to different stepper drivers. The first parameter specified will be used for all motors on the axis. You should use identical motors on any axis that has more than one motor to avoid unexpected behaviour. Example: If you have two motors on your Z axis, physically connected to Z and E0 stepper drivers, configured with M584 Z2:3, set M913 Z50, not M913 Z50:50

