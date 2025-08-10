## M5: Spindle Off

Supported in RepRapFirmware version 1.20 and later when the device mode is set to CNC mode (for CNC mode, see M453). Supported in RepRapFirmware version 2.01 and later when the device mode is set to CNC and laser mode (for laser mode, see M452). Supported in RepRapFirmware version 3.5 and later when the device mode is set to CNC, laser and FFF mode (for FFF mode, see M451).

### Parameters

- none

### Examples

M5 ; turn off spindle/laser

### Notes

• M5 in RepRapFirmware 3.5 and later

• M5 in RepRapFirmware 3.0 to 3.4

• M5 in RepRapFirmware 2.01 to 2.05.1

• M5 in RepRapFirmware 1.20 to 2.0

- **M5** commands are now supported in FFF/FDM mode as well as CNC and laser mode. This will allow mixing of additive and subtractive tools wihtout switching mode.

- **FFF mode:**

  - In FFF mode, M5 will control a predefined spindle, as 'CNC mode' below. Lasers are not supported.

- **CNC mode:**

  - M5 will stop the spindle of the current tool (if any) or all defined spindles if the current tool has no spindle assigned or there is no active tool.

- **Laser mode:**

  - In 'non-sticky' mode (M452 S0), M5 commands are redundant, as all G1 commands need an S parameter to fire the laser, otherwise it just defaults to S0.

  - In 'sticky' mode (M452 S1), M5 (or M3 S0 or G1 S0) will turn off the laser, and subsequent G1 commands (without an S parameter) will not fire the laser until another M3 S# or G1 S# command is sent.

&nbsp;

- **CNC mode:**

  - M5 will stop the spindle of the current tool (if any) or all defined spindles if the current tool has no spindle assigned or there is no active tool.

- **Laser mode:**

  - In 'non-sticky' mode (M452 S0), M5 commands are redundant, as all G1 commands need an S parameter to fire the laser, otherwise it just defaults to S0.

  - In 'sticky' mode (M452 S1), M5 (or M3 S0 or G1 S0) will turn off the laser, and subsequent G1 commands (without an S parameter) will not fire the laser until another M3 S# or G1 S# command is sent.

&nbsp;

- **CNC mode:**

  - M5 will stop the spindle of the current tool (if any) or all defined spindles if the current tool has no spindle assigned or there is no active tool.

- **Laser mode:**

  - M5 (or M3 S0 or G1 S0) will turn off the laser, and subsequent G1 commands (without an S parameter) will not fire the laser until another M3 S# or G1 S# command is sent.

&nbsp;

- **CNC mode:**

  - M5 will stop the spindle of the current tool (if any) or all defined spindles if the current tool has no spindle assigned or there is no active tool.

