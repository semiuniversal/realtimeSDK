## M203: Set maximum feedrate

### Parameters

- **Xnnn** Maximum feedrate for X axis

- **Ynnn** Maximum feedrate for Y axis

- **Znnn** Maximum feedrate for Z axis

- **Unnn** Maximum feedrate for U axis

- **Vnnn** Maximum feedrate for V axis

- **Wnnn** Maximum feedrate for W axis

- **Ennn:nnn...** Maximum feedrates for extruder drives

- **Innn** Minimum overall movement speed (firmware 2.03 and later), default 30mm/min

### Order dependency

If this command refers to any axes other than X, Y and Z then it must be later in config.g than the M584 command that creates those additional axes.

### Examples

M203 X6000 Y6000 Z300 E10000

### Notes

Sets the maximum feedrates that your machine can do in mm/min

RepRapFirmware does not support individual motor settings where an axis has multiple motors connected to different stepper drivers. The first parameter specified will be used for all motors on the axis. You should use identical motors on any axis that has more than one motor to avoid unexpected behaviour.

Example: If you have two motors on your Z axis, physically connected to Z and E0 stepper drivers, configured with M584 Z2:3, set M203 Z300, not M203 Z300,300

