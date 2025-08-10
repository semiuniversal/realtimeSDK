## M1: Sleep or Conditional stop

### Examples

M1

The effect of M1 depends on the state of the machine.

1.  The firmware finishes any moves left in its buffer.

2.  **Either**: if the axes are homed and if a print is paused (M25), it executes the macro file **cancel.g** if present. **Or**: if M1 is sent at any other time, **sleep.g** is run if present.

3.  All motors and heaters are are turned off.

G and M codes can still be sent, the first of which will wake it up again. See also M112 - emergency stop.

If Marlin is emulated in RepRapFirmware, this does the same as M25 if the code was read from a serial or Telnet connection, else the macro file **sleep.g** is run before all heaters and drives are turned off.

