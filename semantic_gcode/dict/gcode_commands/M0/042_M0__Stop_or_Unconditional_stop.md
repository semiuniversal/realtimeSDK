## M0: Stop or Unconditional stop

### Parameters

- This command can be used without any additional parameters.

### Examples

M0

The effect of M0 depends on the state of the machine.

1.  The firmware finishes any moves left in its buffer.

2.  **Either**: if the axes are homed and if a print is paused (M25), it executes the macro file **cancel.g** if present. **Or**: if M0 is sent at any other time, **stop.g** is run if present.

3.  All motors are put into idle mode.

4.  If there is no stop.g or cancel.g file (as appropriate) then all heaters are turned off too. In RRF versions prior to 3.4 you can prevent heaters being turned off using parameter H1.

Note: From RRF 3.5b1, When a print file completes normally then file stop.g is run automatically even if the print file did not end with a M0 command.

See also M112 - emergency stop.

