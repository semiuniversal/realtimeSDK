## M84: Stop idle hold

Deprecated in RRF 3.6.0 and later. Use M18 to disable motors, and M906 T# to set idle timeout

### Parameters

- This command can be used without any additional parameters.

- **Snnn** Idle Time-out

- X,Y, E0:1.. etc

### Examples

M84 ; Disable all motors M84 S10 ; Set idle time out to 10 seconds M84 E0:1:2:3:4 ; Disable specific motors

### Description

Stops the idle hold on all axis and extruder, effectively disabling the specified motor, or all motors, the same as M18. Be aware that by disabling idle hold during printing, you will get quality issues. Also used to set the idle timeout for all motors. For example, M84 S10 will idle the stepper motors after 10 seconds of inactivity. The idle current is set by the M906 I parameter.

### Notes

- For example, M84 S10 will idle the stepper motors after 10 seconds of inactivity.

- You can disable individual motors with the standard X, Y, Z etc switches.

- Setting M84 S0 does NOT mean "never idle hold" (ie motors stay on all the time, at full current), and S0 is an invalid setting. The correct way to set no idle hold (ie motors are 'always on') is to use M906 I parameter to set the idle hold to the required level, eg M906 I100.

