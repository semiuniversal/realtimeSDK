## M950: Create heater, fan, spindle, LED strip or GPIO/servo pin

Supported in RepRapFirmware 3.

M950 is used to create heaters, fans, GPIO ports, spindles (3.3 and later) and LED strips (3.5 and later), and to assign pins to them. Each M950 command assigns a pin or pins to a single device. Every M950 command must have **exactly one** of the H, F, J, P, S, D (for Duet 3 MB6HC only) or E (in RRF 3.5 and later) parameters.

If a M950 command has C and/or Q parameters, then the pin allocation and/or frequency will be configured accordingly. Otherwise, the current configuration will be reported.

• RRF 3.5 and later

• RRF 3.4

• RRF 3.3

• RRF 3.0

##### Parameters

- **Hnn** Heater number

- **Fnn** Fan number

- **Jnn** Input pin number

- **Pnn** or **Snn** Output/servo pin number. Each P and/or S number needs to be unique, eg P1, P2, S3 P4, S5 etc. Servo pins are GpOut pins with a different default PWM frequency.

- **Rnn** Spindle number

- **Dn** (Duet 3 MB6HC only) SD slot number. The only value supported is 1.

- **En** LED strip number

- **C"name"** Pin name(s) and optional inversion status, see Pin Names. Pin name "nil" frees up the pin. A leading '!' character inverts the input or output. A leading '^' character enables the pullup resistor1. The '^' and '!' characters may be placed in either order.

- **Qnn** (optional) PWM frequency in Hz. Valid range: 0-65535, default: 500 for GpOut pins, 250 for fans and heaters. Max value for heaters 1000, to avoid overheating the mosfets. For LED strips (supported in RRF 3.5.0 and later only) this is the LED clock frequency.

- **Tn** When creating a heater: temperature sensor number, required (see M308). When creating a LED strip (supported in RRF 3.5.0 and later only): LED type (optional): 0 = DotStar, 1 = RGB Neopixel (default), 2 = RGBW Neopixel. DotStar LEDs can normally be assigned only to an output intended for them. When creating a spindle, type of spindle control (RRF 3.6.0 and later): T0 (default) = enable/direction inputs, T1 = forward/reverse inputs.

- **Lbbb** or **Laaa:bbb** (optional, for spindles only) RPM values that are achieved at zero PWM (optional) and at maximum PWM.

- **Kaaa(:bbb\[:ccc\])** (optional, RRF 3.5 and later) For spindles, these are the PWM values (0..1) for spindle control (max \[aaa\] - or - min, max \[aaa:bbb\] - or - min, max, idle \[aaa:bbb:ccc\]).

- **Knn** (optional, RRF 3.5 and later) For fans, number of pulses output by the tacho per revolution of the fan, default: 2. Valid range: 0.5-20, 0.5-200 in RRF 3.6.0 and later.

- **Kn** (optional, RRF 3.5.3 and later) For LEDs, the colour order for Dotstar LED strips: 0 (BGR), 1 (BRG), 2 (RGB), 3 (RBG), 4 (GBR), 5 (GRB)

- **Unnn** (optional, RRF 3.5.0 and later, for LED strips only) The maximum number of LEDs in the strip. Default 60, larger values use more memory.

1 Check the individual hardware pages, some IO pins have permanent pullups.

##### Parameters

- **Hnn** Heater number

- **Fnn** Fan number

- **Jnn** Input pin number

- **Pnn** or **Snn** Output/servo pin number. Each P and/or S number needs to be unique, eg P1, P2, S3 P4, S5 etc. Servo pins are GpOut pins with a different default PWM frequency.

- **Rnn** Spindle number

- **Dn** (Duet 3 MB6HC only) SD slot number. The only value supported is 1.

- **C"name"** Pin name(s) and optional inversion status, see Pin Names. Pin name "nil" frees up the pin. A leading '!' character inverts the input or output. A leading '^' character enables the pullup resistor1. The '^' and '!' characters may be placed in either order.

- **Qnn** (optional) PWM frequency in Hz. Valid range: 0-65535, default: 500 for GpOut pins, 250 for fans and heaters. Max value for heaters 1000, to avoid overheating the mosfets.

- **Tn** When creating a heater: temperature sensor number, required (see M308).

- **Lbbb** or **Laaa:bbb** (optional, for spindles only) RPM values that are achieved at zero PWM (optional) and at maximum PWM.

1 Check the individual hardware pages, some IO pins have permanent pullups.

##### Parameters

- **Hnn** Heater number

- **Fnn** Fan number

- **Jnn** Input pin number

- **Pnn** or **Snn** Output/servo pin number. Each P and/or S number needs to be unique, eg P1, P2, S3 P4, S5 etc. Servo pins are GpOut pins with a different default PWM frequency.

- **Rnn** Spindle number

- **C"name"** Pin name(s) and optional inversion status, see Pin Names. Pin name "nil" frees up the pin. A leading '!' character inverts the input or output. A leading '^' character enables the pullup resistor1. The '^' and '!' characters may be placed in either order.

- **Qnn** (optional) PWM frequency in Hz. Valid range: 0-65535, default: 500 for GpOut pins, 250 for fans and heaters. Max value for heaters 1000, to avoid overheating the mosfets.

- **Tn** When creating a heater: temperature sensor number, required (see M308).

- **Lbbb** or **Laaa:bbb** (optional, for spindles only) RPM values that are achieved at zero PWM (optional) and at maximum PWM.

1 Check the individual hardware pages, some IO pins have permanent pullups.

##### Parameters

- **Hnn** Heater number

- **Fnn** Fan number

- **Jnn** Input pin number (RRF 3.01 and later only)

- **Pnn** or **Snn** Output/servo pin number. Each P and/or S number needs to be unique, eg P1, P2, S3 P4, S5 etc. Servo pins are GpOut pins with a different default PWM frequency.

- **C"name"** Pin name(s) and optional inversion status, see Pin Names. Pin name "nil" frees up the pin. A leading '!' character inverts the input or output. A leading '^' character enables the pullup resistor1. The '^' and '!' characters may be placed in either order.

- **Qnn** (optional) PWM frequency in Hz. Valid range: 0-65535, default: 500 for GpOut pins, 250 for fans and heaters. Max value for heaters 1000, to avoid overheating the mosfets.

- **Tn** When creating a heater: temperature sensor number, required (see M308).

1 Check the individual hardware pages, some IO pins have permanent pullups.

### Order dependency

- When M950 is used to create a heater, the M950 command must come later in config.g than the M308 command that creates the sensor referred to in the T parameter

- M950 must come before any commands that refer to the device being created. For example, when M950 is used to create a heater, it must be earlier than the M307 command used to set the heater parameters, and earlier than any M563 commands that create tools that use that heater. When M950 is used to create a fan, it must come earlier than any M106 commands relating to that fan. When M950 is used to create an LED strip, it must come earlier than any M150 commands that use that strip.

### Configuration examples and notes

• Heaters

• Fans

• Inputs

• Outputs and servos

• Spindles

• SD card slot

• LED strips

M950 H1 C"out1" Q100 T1 ; create heater 1 M950 H2 C"nil" ; disable heater 2 and free up the associated pin M950 H1 C"3.out0+out2" Q100 T1 ; create heater 1 using ports OUT0 and OUT2 on CAN board 3 (RRF 3.4 or later)

- **Hnn** Heater number

- **C"name"** Pin name(s) and optional inversion status. Pin name "nil" frees up the pin.

- **Qnn** (optional) PWM frequency in Hz. Valid range: 0-65535, default: 250 for heaters. Max value for heaters 1000, to avoid overheating the mosfets.

- **Tn** When creating a heater, temperature sensor number, required (see M308).

&nbsp;

- **Fnn** Fan number

- **C"name"** Pin name(s) and optional inversion status. Pin name "nil" frees up the pin. A leading '!' character inverts the input or output. A leading '^' character enables the pullup resistor1. The '^' and '!' characters may be placed in either order.

- **Qnn** (optional) PWM frequency in Hz. Valid range: 0-65535, default: 250 for fans.

- **Knn** (optional, RRF 3.5 and later) For fans, number of pulses output by the tacho per revolution of the fan, default: 2. Valid range: 0.5-20, 0.5-200 in RRF 3.6.0 and later.

&nbsp;

- **Jnn** Input pin number

- **C"name"** Pin name(s) and optional inversion status. Pin name "nil" frees up the pin. A leading '!' character inverts the input or output. A leading '^' character enables the pullup resistor1. The '^' and '!' characters may be placed in either order.

M950 P0 C"exp.heater3" ; create output/servo port 0 attached to heater 3 pin on expansion connector

- **Pnn** or **Snn** Output/servo pin number. Each P and/or S number needs to be unique, eg P1, P2, S3 P4, S5 etc. Servo pins are GpOut pins with a different default PWM frequency.

- **C"name"** Pin name(s) and optional inversion status, see Pin Names. Pin name "nil" frees up the pin. A leading '!' character inverts the input or output. A leading '^' character enables the pullup resistor1. The '^' and '!' characters may be placed in either order.

- **Qnn** (optional) PWM frequency in Hz. Valid range: 0-65535, default: 500 for GpOut pins.

Supported in RRF 3.3 and later.

M950 R0 C"!exp.heater3" L12000 ; Spindle 0 uses exp.heater3 as RPM pin and has a max RPM of 12000

- **Rnn** Spindle number

- **C"name"** Pin name(s) and optional inversion status. Pin name "nil" frees up the pin. A leading '!' character inverts the input or output. A leading '^' character enables the pullup resistor1. The '^' and '!' characters may be placed in either order.

- **Qnn** (optional) PWM frequency in Hz. Valid range: 0-65535.

- **Lbbb** or **Laaa:bbb** (optional) RPM values that are achieved at zero PWM (optional) and at maximum PWM.

- **Kaaa(:bbb\[:ccc\])** (optional, RRF 3.5 and later) PWM values (0..1) for spindle control (max \[aaa\] - or - min, max \[aaa:bbb\] - or - min, max, idle \[aaa:bbb:ccc\])

- **Tn** (RRF 3.6.0 and later) Specifies type of spindle control: T0 (default) = enable/direction inputs, T1 = forward/reverse inputs.

##### Notes

- When using M950 to create a spindle (with default T0 in RRF 3.6.0 and later), use the following format:M950 R0 C"pwm_pin + on/off_pin + forward/reverse_pin" Qfff Laa:bb

- When using M950 to create a spindle, with T1 in RRF 3.6.0 and later, use the following format:M950 R0 C"pwm_pin + forward_pin + reverse_pin" T1 Qfff Laa:bb

- C can have 1, 2 or 3 pins.

  - The first pin defines a pwm-capable pin to set the spindle speed.

  - If a second pin is defined it is used as spindle on/off.

  - If a third pin is defined it is used as spindle forward/reverse.

- **Qfff** is the PWM frequency as usual

- **Laa:bb** sets the RPM range as "aa" to "bb". "Lbb" just sets the max RPM to "bb". Default RPM values are 60 min 10000 max

- In RRF 3.6.0 and later, sending M950 R# were R# is the spindle number, reports on that spindle.

M950 D1 C"spi.cs0+spi.cs2" ; on Duet 3 MB6HC support external SD card using pins spi.cs0 and spi.cs2 for the CS and Card Detect pins respectively (RRF 3.4 and later)

- **En** LED strip number

- **C"name"** Pin name

- **Qnn** (optional) LED clock frequency, default 3000000Hz.

- **Tn** (optional) LED type: 0 = DotStar, 1 = RGB Neopixel (default), 2 = RGBW Neopixel. DotStar LEDs can normally be assigned only to an output intended for them.

- **Unnn** (optional) The maximum number of LEDs in the strip. Default 60, larger values use more memory.

##### Notes

- The **Qnn** parameter sets the LED clock frequency. This is 4x the bit rate. Most datasheets for LEDs (at least SK6812 and WS2812B based LEDs) suggest a maximum data rate of 800Kbps, so 800000 \* 4 = 3200000. The default of 3000000 appears to work well with most LEDs.

- The **Unn** parameter defines the maximum number of LEDs in a strip, and the default is 60. It can be increased using the M950 U parameter, subject to (a) available RAM and (b) on the 6HC and 6XD there is an additional limit because the DMA buffer has to be in non-cached memory. For 6HC and 6XD the max LEDs for a strip connected to the dedicated LED port is currently 240 Neopixel RGBW or 320 RGB. It might reduce in future.

- When configuring a LED strip on a tool board or 1XD (which have very little free RAM), or configuring multiple LED strips, using a lower U parameter (ie set U to the number of LEDs) is advised to save RAM.

