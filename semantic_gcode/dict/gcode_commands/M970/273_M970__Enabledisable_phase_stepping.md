## M970: Enable/disable phase stepping

Support in RepRapFirmware 3.6 and later

Motor drivers on Duet 3 6HC allow for direct control of the motor phases. This command allows setting the motion controller to use phase stepping instead of step and direction.

### Parameters

- **X,Y,Z,E** 0 or 1 to disable/enable phase stepping for that axis.

### Order dependency

This command must appear after any M584 command that refers to the same axis.

### Examples

M970 X1 Y0 Z0 E1:0

Enable phase stepping for X and E0, enable step direction for Y, Z, and E1.

### Notes

- Phase stepping can be enabled/disabled for each axis/extruder individually.

- In phase stepping, the motor current is scaled based on the current speed and acceleration. The current will not exceed the value set by M906.

- The standstill current factor set by M917 is also used to scale the motor current. The scaled current will be a minimum of the current \* standstill current factor.

- Stall detect is not supported while phase stepping is enabled.

