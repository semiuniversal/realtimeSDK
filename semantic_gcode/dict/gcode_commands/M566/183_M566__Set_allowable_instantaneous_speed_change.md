## M566: Set allowable instantaneous speed change

### Parameters

- **Xnnn** Maximum instantaneous speed change of the X axis (mm/min)

- **Ynnn** Maximum instantaneous speed change of the Y axis

- **Znnn** Maximum instantaneous speed change of the Z axis

- **Ennn** Maximum instantaneous speed change of the extruder drives

- **Pn** Jerk policy (RepRapFirmware 2.03 and later)

### Examples

M566 X600 Y600 Z50 E600

### Description

Sets the maximum allowable speed change (sometimes called 'jerk speed') of each motor when changing direction.

The model files and GCode files used by repraps generally render circles and other curves shapes as a sequence of straight line segments. If the motors were not allowed any instantaneous speed change, they would have to come to a stop at the junction between each pair of line segments. By allowing a certain amount of instantaneous speed change, printing speed can be maintained when the angle between the two line segments is small enough.

**X** and **Y** parameter: If you set the X and Y values too low, then the printer will be slow at printing curves. If they are too high then the printer may be noisy when cornering and you may suffer ringing and other print artefacts, or even missed steps.

**Z** parameter: When mesh bed compensation is used, movement may be jerky if the allowed Z jerk is too low, because the Z speed needs to change abruptly as the head moves between squares in the mesh.

**E** parameter: Generally, extruder jerk can be set high, between 3000 and 6000 mm/min, otherwise it will limit the acceleration of other axes.

**P** parameter: The default jerk policy is 0, which replicates the behaviour of earlier versions of RRF (jerk is only applied between two printing moves, or between two travel moves, and only if they both involve XY movement or neither does). Changing the jerk policy to 1 allows jerk to be applied between any pair of moves.

### Notes

- In RRF 3.6.0 and later, jerk limits set using M566 (or the default jerk limits if M566 has never been used) can no longer be exceeded by a subsequent M205 command. In config.g you should use M566 to set the maximum jerk values that the machine can use reliably. You may also set default values using M205 if you want these to be lower. In previous firmware versions, M566 and M205 both adjusted a single set of jerk limits. In this release, RRF maintains separate machine jerk limits and jerk limits for the current job. M566 sets both jerk limits, whereas M205 sets only the jerk limits for the current job. The current job jerk limits are constrained to be no higher than the machine jerk limits. This allows slicers to use M205 to change the allowed jerk without exceeding machine limits.

- The minimum jerk speed supported in as at firmware version 2.02 is 0.1mm/sec.

- RepRapFirmware does not support individual motor settings where an axis has multiple motors connected to different stepper drivers. The first parameter specified will be used for all motors on the axis. You should use identical motors on any axis that has more than one motor to avoid unexpected behaviour.

- Example: If you have two motors on your Z axis, physically connected to Z and E0 stepper drivers, configured with M584 Z2:3, set M566 Z50, not M566 Z50:50

