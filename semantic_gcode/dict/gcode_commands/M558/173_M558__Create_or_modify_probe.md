## M558: Create or modify probe

• RepRapFirmware 3.x

• RepRapFirmware 2.x and earlier

##### Parameters

- **Knnn** Sets/selects probe number. If there is no K parameter then 0 is used. You can ignore this parameter if you have only one probe.

- **Pnnn** Probe type

- **C"name"** Specifies the input pin and the optional modulation pin. This parameter is mandatory, except for probe type 0 (manual probing) and 10 (Z motor stall detection).

- **Hnnn** or **Hnnn:nnn** Dive height (mm). The height above the trigger height from which probing starts. The second dive height is supported in RRF 3.5.1 and later, see notes below.

- **Fnnn** or **Fnnn:nnn** or **Fnnn:nnn:nnn** Feed rate (i.e. probing speed, mm/min). Initial fast probe followed by probing at second speed is supported in RRF 3.3 and later. Third speed for scanning Z probe is supported in RRF 3.5.0 and later.

- **Tnnn** Travel speed to and between probe points (mm/min). This is also the Z lift speed after probing. The corresponding axis speed limits set by M203 will be used instead if they are lower.

- **Rnnn** Z probe recovery time before the probing move is started, default zero (seconds). This is to allow the probe to settle after executing a travel move to the coordinates to probe.

- **Annn** Maximum number of times to probe each point, default 1. Maximum, as of RRF 2.03, is 31. Setting M558 A parameter to anything \>31 set it to 0 instead of to 31

- **Snnn** Tolerance when probing multiple times, default 0.03mm

- **Bn** If 1, turn off all heaters while probing, default (B0) leaves heaters on.

M574 Z0 P"nil" ; (RRF 3.0 on Duet 2 ONLY) no Z endstop switch, free up Z endstop input M558 P5 C"zstop" H5 F120 T3000 ; probe connected to Duet 2 Z endstop input ; BL Touch on Duet 3 Mini 5+ M950 S0 C"io3.out" ; servo/gpio 0 is io3.out pin M558 P9 C"io3.in" H5 F500:120 T3000 ; BLTouch connected to io3.in pin ... M280 P0 S10 ; send control signal to BLTouch through servo/gpio 0 ; BLTouch on Duet WiFi M950 S0 C"exp.heater3" ; create servo/gpio 0 on heater 3 pin on expansion connector M558 P9 C"^zprobe.in" H5 F120 T3000 ; BLTouch connected to Z probe IN pin ... M280 P0 S10 ; send control signal to BLTouch through servo/gpio 0 ; For the Duet Smart Effector on Duet 2 M558 P8 C"zprobe.in+zprobe.mod" R0.4 F1200 ; zprobe.mod is the programming pin for M672

##### Notes

A probe may be a switch, an IR proximity sensor, or some other device. The **P** parameter selects which type to use:

- P0 indicates that no probe is present. Whenever Z probing is commanded, you will be prompted to jog the Z axis until the nozzle is just touching the bed and then signal completion.

- P1 specifies an unmodulated or smart IR probe, or any other probe type that emulates one (probe output is an analog signal that rises with decreasing nozzle height above the bed). If there is a control signal to the probe, it is driven high when the probe type is P1.

- P2 specifies a simple modulated IR probe, where the modulation is commanded directly by the main board firmware using the control signal to the probe.

- P3 is similar to P1 but drives the control signal to the probe low. This may be used to switch between different Z probes.

- P5 selects a switch by default (normally closed) for bed probing between the In and Gnd pins of the IO connector (Duet 3) or Z-probe connector (Duet 2).

- P8 is as P5 but is unfiltered, for faster response time.

- P9 is as P5 but for a BLTouch probe that needs to be retracted and redeployed between probe points.

- P10 means use Z motor stall detection as the probe trigger.

- P11 means a scanning Z probe with an analog output (supported from RRF 3.5.0). Such probes must be calibrated before use (see M558.1).

Probe types 4, 6 and 7 (used in RRF 2.x) are not supported in RRF 3.x. Instead, use type 5 (filtered digital) or 8 (unfiltered digital) and use the C parameter to specify the input.

Probes connected to Duet 3 expansion or tool boards are limited to types 8 and 9. Firmware 3.5 and later also support type 11.

Only one Type 2 probe can be configured, and if using Duet 3 then it must be connected to the Duet 3 main board, not to a CAN-connected expansion or tool board.

M558 with P parameter deletes the existing probe with that K number (if any) and creates a new probe. This resets the G31 values for that probe to default values.

**In RRF 3.0 on Duet 2 boards only** (not in RRF 3.01 and later, and not in RRF 3.0 on Duet 3), if your probe is connected to the Z endstop input, that input is by default pre-assigned to be used by the Z endstop, so you must free it up first with M574 Z0 P"nil".

The **C** parameter specifies the input pin and the optional modulation pin. See Pin names for a list of available pins and their names to use. Invert the input by prefixing the input pin with ! character, when using an NPN output inductive or capacitive sensor or using an NO switch (not recommended, use a NC switch instead). The pullup resistor on the Z probe input is disabled by default. Enable it by prefixing the input pin (C parameter) with the ^ character. Enable pullup resistor with ^ if using Duet 2, running RRF3, using the Z probe input pin, and the probe type is a switch or BLTouch.

The **H** parameter:

- Defines the dive height when Z probing, which is the height above the trigger height from which probing starts.

- The default is 3mm or 5mm depending on firmware version. You may wish to increase it during initial calibration.

- When using mesh bed compensation or running G30 commands with specified XY coordinates (for example from the bed.g file), the firmware moves the Z probe to this height above where it expects the bed to be before commencing probing. The maximum depth of probing from this position is twice the dive height.

- A large dive height will tolerate a very uneven bed or poor calibration. A small dive height will make probing faster, because the Z probe has less distance to travel before reaching the bed.

- From RRF 3.5.1, the H parameter supports two dive heights. When probing multiple times at the same point, the second and subsequent probes use the second dive height and it is calculated relative to the height at which the probe last triggered. The idea is to speed up probing if you make the second dive height smaller than the first.

The **F** parameter:

- With a single value for the **F** parameter, this defines the probing feed rate (i.e. probing speed), in mm/min.

- From RRF 3.3 you can provide two **F** parameters instead of one, where the second is lower than the first, for example F1000:500. When doing a plain G30 command, an additional probe will be done using the first speed to establish the approximate bed position, before one or more additional probes are done using the second speed. The first speed will not be used when probing at a defined point or when mesh bed probing.

- From RRF 3.5.0 the **F** parameter can take up to three values. The third value is the scanning speed for scanning Z probes, and is only used by them, and only reports by M558 for scanning Z probes. If a scanning Z probe is used as an ordinary Z probe with G30 (which is be supported in 3.5.0) then the first two speeds given in the F parameter will be used, as usual.

The **A** and **S** parameters control multiple probing. Probing is repeated until two consecutive probe attempts produce results that differ by no more than the S parameter; then the average of those two results is used. For example, S-1 would force averaging. However, if the number of attempts specified by the A parameter is reached without getting two consecutive results within tolerance of each other, no further probe attempts are made and the average result of all the attempts is used.

Related commands:

##### Parameters

- **Pnnn** Z probe type

- **Fnnn** Feed rate (i.e. probing speed, mm/min)

- **Hnnn** Dive height (mm). When using mesh bed compensation or running G30 commands with specified XY coordinates (for example from the bed.g file), the firmware moves the Z probe to this height above where it expects the bed to be before commencing probing. The maximum depth of probing from this position is twice the dive height. A large dive height will tolerate a very uneven bed or poor calibration. A small dive height will make probing faster, because the Z probe has less distance to travel before reaching the bed. Default value if omitted is 5mm.

- **Innn** Invert (I1) or do not invert (I0, default) the Z probe reading (RepRapFirmware 1.16 and later)

- **Rnnn** Z probe recovery time before the probing move is started, default zero (seconds) (RepRapFirmware 1.17 and later). This is to allow the probe to settle after executing a travel move to the coordinates to probe.

- **Tnnn** Travel speed to and between probe points (mm/min). This is also the Z lift speed after probing. The corresponding axis speed limits set by M203 will be used instead if they are lower.

- **Annn** Maximum number of times to probe each point, default 1. Maximum, as of 2.03, is 31. Setting M558 A parameter to anything \>31 set it to 0 instead of to 31

- **Snnn** Tolerance when probing multiple times, default 0.03mm

- **Bn** If 1, turn off all heaters while probing, default (B0) leaves heaters on. (RepRapFirmware 1.21 and later)

- **Cn** Endstop input number when the probe type is P4, default 3 (RepRapFirmware 2.02/1.23 and later)

**Obsolete parameters**

- **Xnnn** If nonzero, use probe for homing X axis (RRF 1.19 and earlier)

- **Ynnn** If nonzero, use probe for homing Y axis (RRF 1.19 and earlier)

- **Znnn** If nonzero, use probe for homing Z axis (RRF 1.19 and earlier)

##### M558 P1 X1 Y0 Z1 F500 T5000 H3 ; probe is used for homing X and Z axes (RRF 1.19 and earlier) M558 P4 H5 F120 T3000 ; probe connected to E0 endstop input M558 P7 H5 F120 T3000 ; probe connected to Z endstop input ; BLTouch on Duet Maestro M558 P9 H5 F120 T3000 ; BLTouch connected to Z probe IN pin ... M280 P64 S10 ; send control signal to BLTouch through Z probe MOD pin ; BLTouch on Duet WiFi M558 P9 H5 F120 T3000 ; BLTouch connected to Z probe IN pin M307 H3 A-1 C-1 D-1 ; free up heater 3 to use as BLTouch servo pin ... M280 P3 S10 I1 ; send control signal to BLTouch through heater 3 pin

Notes

A probe may be a switch, an IR proximity sensor, or some other device. The **P** selects which to use:

- P0 indicates that no probe is present. Whenever Z probing is commanded, you will be prompted to jog the Z axis until the nozzle is just touching the bed and then signal completion.

- P1 specifies an unmodulated or smart IR probe, or any other probe type that emulates one (probe output is an analog signal that rises with decreasing nozzle height above the bed). If there is a control signal to the probe, it is driven high when the probe type is P1.

- P2 specifies a simple modulated IR probe, where the modulation is commanded directly by the main board firmware using the control signal to the probe.

- P3 is similar to P1 but drives the control signal to the probe low. This may be used to switch between different Z probes.

- P4 selects a switch for bed probing. In recent firmware versions the C parameter specifies the endstop input number, default 3 (on the Duets this is the E0 endstop input).

- P5 (from RepRapFirmware 1.14) selects a switch by default (normally closed) for bed probing between the In and Gnd pins of the Z-probe connector (Duet 0.8.5 and Duet 2 WiFi).

- P6 is as P4 but the switch is connected to an alternative connector (on the Duet series, the E1 endstop connector). Deprecated in recent firmware versions, use P4 C4 instead.

- P7 (from RepRapFirmware 1.20) selects a switch (by default normally closed) connected to the Z endstop input. Deprecated in recent firmware versions, use P4 C2 instead.

- P8 (from RepRapFirmware 1.20) is as P5 but is unfiltered, for faster response time.

- P9 (from RepRapFirmware 1.21) is as P5 but for a BLTouch probe that needs to be retracted and redeployed between probe points.

- P10 means use Z motor stall detection as the Z probe trigger.

The **H** parameter defines the Z probe dive height, which is the height above the trigger height from which probing starts. The default is 3mm or 5mm depending on firmware version. You may wish to increase it during initial calibration.

The **A** and **S** parameters control multiple probing. Probing is repeated until two consecutive probe attempts produce results that differ by no more than the S parameter; then the average of those two results is used. For example, S-1 would force averaging. However, if the number of attempts specified by the A parameter is reached without getting two consecutive results within tolerance of each other, no further probe attempts are made and the average result of all the attempts is used.

In RepRapFirmware versions 1.19 and earlier, the **X**, **Y** and **Z** parameters specify whether each axis uses the Z probe as a substitute homing switch or not. If the parameter is nonzero, the Z probe is used for homing that axis. If the parameter is zero, the endstop switch for that axis is used for homing instead. In firmware 1.20 and later, use the S parameter in the Connecting a Z probe

