## M3: Spindle On, Clockwise

Supported in RepRapFirmware version 1.20 and later when the device mode is set to CNC mode (for CNC mode, see M453). Supported in RepRapFirmware version 2.01 and later when the device mode is set to CNC and laser mode (for laser mode, see M452). Supported in RepRapFirmware version 3.5 and later when the device mode is set to CNC, laser and FFF mode (for FFF mode, see M451).

### Parameters

- **Snnn** Spindle RPM (CNC/FFF mode), laser power 0-255 (laser mode).

- **Pnnn** Spindle slot (CNC/FFF mode). Directly address a spindle slot.

### Examples

M3 S4000 ; CNC mode, turn on spindle at speed of 4000 RPM, clockwise M3 S255 ; laser mode, set laser power to full on

### Notes

• M3 in RepRapFirmware 3.5 and later

• M3 in RepRapFirmware 3.0 and 3.4

• M3 in RepRapFirmware 2.01 to 2.05.1

• M3 in RepRapFirmware 1.20 to 2.0

- **M3** commands are now supported in FFF/FDM mode as well as CNC and laser mode. This will allow mixing of additive and subtractive tools wihtout switching mode.

- **FFF mode:**

  - In FFF mode, M3 will control a predefined spindle, as 'CNC mode' below. Lasers are not supported.

- **CNC mode:**

  - M3 can be called without any parameters and will start the spindle of the current tool turning clockwise at the spindle RPM of that tool.

  - Using the S parameter will additionally set the spindle RPM of the current tool.

  - It is an error if there is no tool active or the active tool does not have a spindle assigned and there is no P parameter provided to define which spindle this should be applied to.

- **Laser mode:**

  - In 'non-sticky' mode (M452 S0), M3 commands are redundant, as all G1 commands need an S parameter to fire the laser, otherwise it just defaults to S0.

  - In 'sticky' mode (M452 S1), you can set the laser with, for example, M3 S255, then subsequent G1 moves will use that setting without needing an S parameter. Alternatively set the laser power with the first G1 S command, and subsequent G1 commands will use that setting, until either an M3 S0, G1 S0 or M5 is sent.

  - M3 can't be used to fire the laser on its own; the laser will only fire with a G1 movement command.

  - All M3 commands must have an S parameter. Sending M3 on its own generates an error.

  - The relationship between the S parameter and laser power depends on the R parameter that was specified in the M452 command.

  - Note there can be issues using this mode as the M-command queue is only 8 commands long, while the G-command queue is 20 commands long. You may get stuttering, particularly when raster engraving. Better to use G1 with S parameter, and the 'raster clustering' format for even better performance (see G1 entry, S parameter section).

&nbsp;

- CNC mode:

  - M3 can be called without any parameters and will start the spindle of the current tool turning clockwise at the spindle RPM of that tool.

  - Using the S parameter will additionally set the spindle RPM of the current tool.

  - It is an error if there is no tool active or the active tool does not have a spindle assigned and there is no P parameter provided to define which spindle this should be applied to.

- Laser mode:

  - In 'non-sticky' mode (M452 S0), M3 commands are redundant, as all G1 commands need an S parameter to fire the laser, otherwise it just defaults to S0.

  - In 'sticky' mode (M452 S1), you can set the laser with, for example, M3 S255, then subsequent G1 moves will use that setting without needing an S parameter. Alternatively set the laser power with the first G1 S command, and subsequent G1 commands will use that setting, until either an M3 S0 or M5 is sent.

  - M3 can't be used to fire the laser on its own; the laser will only fire with a G1 movement command.

  - All M3 commands must have an S parameter. Sending M3 on its own generates an error.

  - The relationship between the S parameter and laser power depends on the R parameter that was specified in the M452 command.

  - Note there can be issues using this mode as the M-command queue is only 8 commands long, while the G-command queue is 20 commands long. You may get stuttering, particularly when raster engraving. Better to use G1 with S parameter.

&nbsp;

- CNC mode:

  - M3 can be called without any parameters and will start the spindle of the current tool turning clockwise at the spindle RPM of that tool.

  - Using the S parameter will additionally set the spindle RPM of the current tool.

  - It is an error if there is no tool active or the active tool does not have a spindle assigned and there is no P parameter provided to define which spindle this should be applied to.

- Laser mode:

  - M3 turns the laser on, with the S parameter setting the laser power (0 to 255), before a series corresponding G1 move.

  - The relationship between the S parameter and laser power depends on the R parameter that was specified in the M452 command.

  - Note there can be issues using this mode as the M-command queue is only 8 commands long, while the G-command queue is 20 commands long. You may get stuttering, particularly when raster engraving. Better to use G1 with S parameter.

&nbsp;

- CNC mode:

  - M3 can be called without any parameters and will start the spindle of the current tool turning clockwise at the spindle RPM of that tool.

  - Using the S parameter will additionally set the spindle RPM of the current tool.

  - It is an error if there is no tool active or the active tool does not have a spindle assigned and there is no P parameter provided to define which spindle this should be applied to.

