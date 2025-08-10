## M17: Enable motors

Available in RepRapFirmware 3.3 and later.

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

M17 M17 X E0

Enables all axis and extruder motors when used without parameters. Motors can also be enabled selectively. For example, M17 X E0:2 will enable the X, extruder 0 and extruder 2 motors. Use this command to energise a motor for stealthChop tuning, followed by a short pause eg G4 P100 to allow the driver to establish the motor parameters.

