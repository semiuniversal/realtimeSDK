## M143: Maximum heater temperature

• M143 in RRF 3.01 and later

• M143 in RRF 3.0 and earlier

##### Parameters

- **H** Heater number to monitor (default 1 which is normally the first hot end)

- **S** Maximum permitted temperature

- **P** Heater monitor number, default 0

- **T** Sensor number used to monitor the heater. It defaults to the sensor that controls the heater (as was specified in the M308 command when the heater was created).

- **A** Action to trigger (0: Generate heater fault \[default\] 1: Switch off permanently 2: Switch off temporarily 3: Shut down the printer)1

- **C** Condition for temperature event (0: Temperature too high \[default\] 1: Temperature too low, -1: Monitor is disabled)

Each heater supports a certain number (3 in most builds of RRF) of monitors for that heater. The P parameter allows you to choose which monitor to configure.

By default, monitor 0 is set up to generate a heater fault if a temperature limit is exceeded according to the sensor that controls the heater, and monitors 1 and 2 are disabled.

##### M143 H1 P0 S275 A2 ; switch off heater 1 temporarily if it exceeds 275Â°C M143 H1 P1 S285 A0 ; raise a heater fault if it exceeds 285C

##### Parameters

- **H** Heater number to turn off if an anomaly is detected (default 1 which is normally the first hot end). This must be a real heater.

- **S** Maximum permitted temperature

- **P** Heater protection instance (defaults to H parameter if omitted)1

- **X** Heater number whose temperature sensor is used to monitor the heater specified in the H parameter. This can be a virtual heater. It default to the value of the H parameter.1

- **A** Action to trigger (0: Generate heater fault \[default\] 1: Switch off permanently 2: Switch off temporarily)1

- **C** Condition for temperature event (0: Temperature too high \[default\] 1: Temperature too low)1

##### M143 S275 ; set the maximum temperature of the hot-end to 275Â°C M143 H0 S125 ; set the maximum bed temperature to 125C M143 H1 S275 X103 ; use virtual heater 103 to monitor heater 1

You have heater 3 mapped to a chamber heater which is supposed to be temporarily turned off when the temperature in it exceeds 65C. The thermistor for the chamber is set up as a virtual heater on channel 104 and can be viewed on the "Extra" panel on DWC (refer to M305 for further details on how to set this up). To achieve this you can configure an extra heater protection with the following GCode:

M143 P100 H3 X104 A2 C0 S65

##### Order dependency

If the heater is a bed or chamber heater then the M143 command must come after the M140 or M141 command that declares the heater as a bed or chamber heater.

### Notes

1 Supported in RepRapFirmware 1.20 and later. Starting from this version RepRapFirmware allows more granular control over the heater subsystem. By default each heater has one heater protection instance assigned to it, which is by default configured to generate a heater fault if the maximum heater temperature is exceeded.

The default maximum temperature for all heaters was 300Â°C prior to RepRapFirmware version 1.13, and 262Â°C from 1.13. At RepRapFirmware 1.17 the default maximum temperatures were 262C for extruders and 125C for the bed. In more recent versions the default maximum heater temperature is 290C, to allow the hot end to be tightened at 285C as per the E3D recommendation. When the temperature of the heater exceeds this value a heater error will be triggered.

With A0 set on RepRapFirmware 1.26.1, PS_ON is triggered after the fault has exisited for the duration defined by the S parameter set in M570.

