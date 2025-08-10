## M280: Set servo position

• RepRapFirmware 3.x

• RepRapFirmware 2.x

##### Parameters

- **Pnnn** Servo index

- **Snnn** Angle (see notes) or microseconds

##### Parameters

- **Pnnn** Servo index

- **Snnn** Angle (see notes) or microseconds

- **I1** Invert polarity (not supported in RRF3)

##### M280 P1 S50 ; set Heater 1 pin to 50deg servo position M280 P3 I1 S80 ; set Heater 3 pin to 80deg servo position, inverted

RRF 2.x notes

The optional I1 parameter causes the polarity of the servo pulses to be inverted compared to normal for that output pin. The I parameter is not remembered between M280 commands (unlike the I parameter in M106 commands), so if you need inverted polarity then you must include I1 in every M280 command you send.

The servo index is the same as the pin number for the M42 command.

### Notes

S values below 544 are treated as angles, and 544 or greater as the pulse width in microseconds.

The relationship between the S parameter and the pulse width output to the port is the same as in other 3D printer firmwares, so that devices such as BLTouch will perform the same way. However, **there is no standard for servos on the relationship between pulse width and servo angle**. Therefore, **for most servos the value of the S parameter does not equal the servo angle**. Almost all servos accept a pulse width range of at least 1us to 2us, which corresponds to an S parameter range of 44.2 to 141.2 degrees. So for many servos, values in the range 44.2 to 141.2 or alternatively 1000 to 2000 will cover the full operating range of the servo.

See also Using hobby servos and DC motors.

