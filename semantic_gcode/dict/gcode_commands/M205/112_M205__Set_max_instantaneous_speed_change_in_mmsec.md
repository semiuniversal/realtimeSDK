## M205: Set max instantaneous speed change in mm/sec

- **Xnnn** X axis max instantaneous speed change in mm/sec

- **Ynnn** Y axis max instantaneous speed change in mm/sec

- **Znnn** Z axis max instantaneous speed change in mm/sec

- **Unnn, Vnnn, Wnnn etc.** U, V, W axis max instantaneous speed change in mm/sec

### Order dependency

If this command refers to any axes other than X, Y and Z then it must be later in config.g than the M584 command that creates those additional axes.

### Notes

- This command is provided as an alternative to M566 for compatibility with Marlin. In M566 the units are mm/min as with all other speeds. In M205 they are in mm/sec.

- In RRF 3.6.0 and later, jerk limits set using M566 (or the default jerk limits if M566 has never been used) can no longer be exceeded by a subsequent M205 command. In config.g you should use M566 to set the maximum jerk values that the machine can use reliably. You may also set default values using M205 if you want these to be lower. In previous firmware versions, M566 and M205 both adjusted a single set of jerk limits. In this release, RRF maintains separate machine jerk limits and jerk limits for the current job. M566 sets both jerk limits, whereas M205 sets only the jerk limits for the current job. The current job jerk limits are constrained to be no higher than the machine jerk limits. This allows slicers to use M205 to change the allowed jerk without exceeding machine limits.

- In RRF 3.6.0 and later, M205 jerk settings are now included in the resurrect.g file.

