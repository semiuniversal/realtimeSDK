## M42: Switch I/O pin

• RepRapFirmware 3.x

• RepRapFirmware 2.x

##### Parameters

- **Pnnn** GPIO port number (set by M950)

- **Snnn** Pin value

##### Notes

- Before you can use M42 you must create a GPIO port using M950. Then in the M42 command, the P parameter is the GPIO port number.

- The F (PWM frequency) and I (invert PWM) parameters are no longer supported in M42. Instead, use the Q (PWM frequency) and C (pin name, with ! to invert) parameters in M950 when you create the GPIO port.

- In RRF 3.4, Duet 3 supports up to 32 outputs and 16 inputs, Duet 2 Wifi/Ethernet support up to 20 GPIO ports, and Duet 2 Maestro supports 10 GPIO ports. No GPIO ports are allocated by default.

##### Parameters

- **Pnnn** Logical pin number

- **Snnn** Pin value

- **Fnnn** PWM frequency (optional)

- **Innn** Invert PWM (optional). I0 (no inversion) is default, I1 inverts.

##### M42 P3 I1 S0.5 F500 ; set Heater 3 pin to 50% PWM at 500Hz, inverted

M42 switches a general purpose I/O pin. Use M42 Px Sy to set pin x to value y. The S field may be in the range 0.0-1.0 or \>1.0-255. 0 is off in both cases.

##### RepRap GCode dictionary M42 entry.

**See also**

M950

