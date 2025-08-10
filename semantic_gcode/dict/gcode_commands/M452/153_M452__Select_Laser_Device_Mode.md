## M452: Select Laser Device Mode

Support in RRF 2.01 and later.

• RepRapFirmware 3.x

• RepRapFirmware 2.x

##### Parameters

- **C"name"** Pin name(s) and optional inversion status, see Pin Names. A leading '!' character inverts the input or output.

- **Rnnn** The value of the S parameter in G1 commands that corresponds to full laser power, default 255

- **Sn** 0 (default) = laser is off when executing G1 commands that have no S parameter (non-sticky mode), 1= laser power is sticky across G1 commands (sticky mode)

- **Fnnn** The PWM frequency used to drive the laser - default is 500Hz

##### ; Duet 3 MB6HC M452 C"out9" R255 F200 ; Enable Laser mode, on out9, with max intensity being 255, and a PWM frequency of 200 ; Duet 3 Mini 5+ M452 C"out6" R255 F200 ; Enable Laser mode, on out6, with max intensity being 255, and a PWM frequency of 200 ; Duet 2 example: M452 C"!exp.heater3" F100 ; laser uses heater3 pin inverted, PWM frequency 100Hz

Notes

- Switches to laser mode. This mode enables handling of a laser pin and makes sure that the laser is only activated during G1 moves if laser was enabled (using G1 Snn moves) or E is increasing (using M571). G0 moves should never enable the laser.

- **Very important!** If you use M452 to put your machine into Laser mode and are upgrading from RepRapFirmware **v2.01 or earlier**, you must replace all S parameters in G0/G1 commands in homing files etc. with H parameters. This is because S is now used to control laser power.

- In laser mode, it is valid in a Gcode file to send G0 or G1 on one line, and then just send co-ordinates on the following lines.

- In 'non-sticky' mode (M452 S0), M3 commands are redundant, as all G1 commands need an S parameter to fire the laser, otherwise it defaults to S0.

- In 'sticky' mode (M452 S1)

  - M3 Snnn, eg M3 S255, sets laser power and M5 turns off laser power (sets it to zero), but do not activate the laser.

  - G1 moves subsequent to an M3 Snnn command will use that setting without needing an S parameter.

  - Alternatively set the laser power with the first G1 Snnn command, and subsequent G1 commands will use that setting, until either an M3 S0, G1 S0 or M5 is sent.

- RRF 3.x includes laser power velocity ramping. RRF 2.x does not.

- See also Configuring RepRapFirmware for a laser engraver/cutter.

##### Parameters

- **Pnnn** Logical pin number used to control the laser

- **In** Invert (I1) or don't invert (I0, default) the output polarity

- **Rnnn** The value of the S parameter in G1 and/or M3 commands that corresponds to full laser power, default 255

- **Sn** 0 (default) = laser is off when executing G1 commands that have no S parameter (non-sticky mode), 1= laser power is sticky across G1 commands (sticky mode)

- **Fnnn** The PWM frequency used to drive the laser - default is 500Hz

##### M452 P3 I1 F100 ; laser uses heater3 pin inverted, PWM frequency 100Hz M452 P2 R255 F200 ; switch to laser mode using the heater 2 (E1 heater) output pins to control the laser

Notes

- Switches to laser mode. This mode enables handling of a laser pin and makes sure that the laser is only activated during G1 moves if laser was enabled (using M3 Snn or G1 Snn moves) or E is increasing (using M571). G0 moves should never enable the laser.

- **Very important!** If you use M452 to put your machine into Laser mode and are upgrading from RepRapFirmware **v2.01 or earlier**, you must replace all S parameters in G0/G1 commands in homing files etc. with H parameters. This is because S is now used to control laser power.

- In RRF 2.05 and later, M3 Snnn no longer turns on the laser immediately. 'Non-sticky' is the default mode.

- In RRF 2.01 to 2.04, M3/M5 immediately enables/disables the laser. 'Sticky' is the default mode.

- Logical pin numbers for the P parameter are as defined for the M42 and M208 commands. If a heater or fan output is used to control the laser, you must disable the corresponding heater (see M307) or fan (see M106) first.

- RRF 2.x does not support laser power velocity ramping.

- See also Configuring RepRapFirmware for a laser engraver/cutter.

