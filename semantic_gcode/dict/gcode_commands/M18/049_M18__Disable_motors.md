## M18: Disable motors

### Parameters

- This command can be used without any additional parameters.

- **X** X axis

- **Y** Y axis

- **Z** Z axis

- **U** U axis

- **V** V axis

- **W** W axis

- ... or any other defined axis

- **E\[n\]** Extruder drive(s)

### Examples

M18 ; Disable all axis and extruder motors M18 X E0:2 ; Disable X, extruder 0 and extruder 2 motors.

### Notes

- Stops the idle hold on all axis and extruder, effectively disabling the specified motor, or all motors. Disables motors and allows axes to move 'freely.'

- When used without parameters, all axis and extruder motors are disabled.

- Individual motors can be disabled with the X, Y, Z etc axis switches.

- Be aware that by disabling idle hold during printing, you will get quality issues.

