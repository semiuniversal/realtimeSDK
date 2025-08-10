## M350: Set microstepping mode

### Usage

- M350 Xnn Ynn Znn Enn Inn

### Parameters

- Not all parameters need to be used, but at least **one** should be used. As with other commands, RepRapFirmware reports the current settings if no parameters are used.

- **Xnn** Set stepping mode for the X axis

- **Ynn** Set stepping mode for the Y axis

- **Znn** Set stepping mode for the Z axis

- **Enn** Set stepping mode for Extruder 0 (use Enn:nn:nn etc. for multiple extruders)

- **Inn** Enable (nn=1) or disable (nn=0) microstep interpolation mode for the specified drivers, if they support it. All Duet 3 boards, and Duet 2 Maestro supports interpolation at all microstep settings. Duet 2 WiFi/Ethernet support interpolation (to x256 microstepping) only when configured for x16 microstepping.

**Modes (nn)**

- 1 = full step

- 2 = half step

- 4 = quarter step

- 8 = 1/8 step

- 16 = 1/16 step

- 32 = 1/32 step

- 64 = 1/64 step

- 128 = 1/128 step

- 256 = 1/256 step

### Order dependency

This command must be later in config.g than any M584 command.

### Examples

M350 Z1 ;set the Z-axis' driver to use full steps M350 E4:4:4 ;set extruders 0-2 to use quarter steps)

When M350 is processed, the steps/mm will be adjusted automatically to allow for any changes in microstepping. Therefore you can either:

a\) Set Steps/mm correctly for the default 1/16 microstepping, then set the microstepping to the desired amount using M350:

M92 X80 Y80 Z400 ; set axis steps/mm M92 E420:430 ; set extruder 0 and 1 steps/mm M350 X128 Y128 Z128 E128:128 ; set microstepping

or

b\) Set the microstepping using M350 and then set the correct steps/mm for that microstepping amount:

M350 X128 Y128 Z128 E128:128 ; set microstepping M92 X640 Y640 Z3200 ; set axis steps/mm @128 microstepping M92 E3360:3440 ; set extruder 0 and 1 steps/mm

Assuming that in the first example the microstepping was initially at the default x16, both the above examples result in the same steps/mm settings.

### Notes

- RepRapFirmware does not support individual motor settings where an axis has multiple motors connected to different stepper drivers. The first parameter specified will be used for all motors on the axis. You should use identical motors on any axis that has more than one motor to avoid unexpected behaviour. Example: If you have two motors on your Z axis, physically connected to Z and E0 stepper drivers, configured with M584 Z2:3, set M350 Z16, not M350 Z16,16

- Microstep interpolation at all microstep settings is supported on all Duet 3 boards with onboard drivers (TMC5160, TMC2160 or TMC2209), and on Duet 2 Maestro (TMC2224 drivers). The TMC2660 drivers used on the Duet 2 WiFi and Duet 2 Ethernet support microstep interpolation, but only when microstepping is set to 16. In other configurations, specifying I1 has no effect.

- When using external drivers, the microstepping mode (M350) is not controlled by firmware configuration. It is set by the external stepper driver, usually using jumpers to set the 'pulses per rotation'.

