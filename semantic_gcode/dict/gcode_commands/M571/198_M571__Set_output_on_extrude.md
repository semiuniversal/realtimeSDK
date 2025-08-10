## M571: Set output on extrude

### Parameters

- **Snnn** Output value

- **Fnnn** Output PWM frequency (RepRapFirmware 1.17 and later; deprecated in 3.2 and later; not available in 3.5.0 and later)

- **Qnnn** Output PWM frequency (RepRapFirmware 3.2 and later; not used in 3.6.0 and later)

- **Pnnn** (RepRapFirmware 3.6.0 and later) GpOut port number to use

- **P"pin-name"** (RepRapFirmware 3.0 to 3.5.x) Name of the pin to use

- **Pnnn** (RepRapFirmware 1 and 2) Logical pin number (RepRapFirmware 1.17), defaults to the FAN0 output in firmware 1.19 and earlier until M571 with a P parameter has been seen

### Examples

M571 P3 S0.5 ; turn on GpOut port 3 at 50% PWM while extrusion is commanded (RRF 3.6.0 and later) M571 P"heater3" S0.5 ; turn on heater 3 output at 50% PWM while extrusion is commanded (RRF 3 up to 3.5.x) M571 P3 F200 S1 ; turn on logical pin 3 while extrusion is commanded (RRF 2)

### Description

This turns the controlled pin output on whenever extrusion is being done, and turns it off when the extrusion is finished. The output could control a fan or a stirrer or anything else that needs to work just when extrusion is happening. It also can be used to control a laser beam. The S parameter sets the value of the PWM to the output. 0.0 is off; 1.0 is fully on.

### Notes

- In RepRapFirmware 3.6.0 and later you specify the GpOut port number using the P parameter. The port must previously have been created using the M950 command and must be on the main board.

- In RepRapFirmware 3.0 to 3.5.x you specify the pin name using the P parameter.

- For RepRapFirmware 1.x and 2.x, pin numbers are the same as in the M42 and M280 commands. The pin you specify must not be in use for anything else, so if it is normally used as a heater you must disable the heater first using M307, or if it is used for a fan you must disable the fan using M106 with the I-1 parameter.

- RepRapFirmware 1.20 and later do not default to using the FAN0 output, so you must send M571 with a P parameter at least once to define the pin that you wish to use.

- In RepRapFirmware 1.17 and later you can use the P parameter to change the pin used and set the PWM frequency. Defaults to using the FAN0 output.

