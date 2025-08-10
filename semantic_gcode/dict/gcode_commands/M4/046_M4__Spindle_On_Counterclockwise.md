## M4: Spindle On, Counterclockwise

Supported in RepRapFirmware version 1.20 and later when the device mode is set to CNC mode (for CNC mode, see M453). Supported in RepRapFirmware version 3.5 and later when the device mode is set to CNC and FFF mode (for FFF mode, see M451).

### Parameters

- **Snnn** Spindle RPM

- **Pnnn** Spindle slot (CNC mode only). Directly address a spindle slot.

### Examples

M4 S4000 ; turn on spindle at speed of 4000 RPM, counterclockwise

### Notes

• M4 in RepRapFirmware 3.5 and later

• M4 in RepRapFirmware 1.20 to 3.4

- **M4** commands are now supported in FFF/FDM mode as well as CNC mode. This will allow mixing of additive and subtractive tools wihtout switching mode.

- **FFF mode:**

  - In FFF mode, M4 will control a predefined spindle, as 'CNC mode' below. Lasers are not supported.

- **CNC mode:**

  - M4 can be called without any parameters and will start the spindle of the current tool turning counterclockwise at the spindle RPM of that tool.

  - Using the S parameter will additionally set the spindle RPM of the current tool.

  - It is an error if there is no tool active or the active tool does not have a spindle assigned and there is no P parameter provided to define which spindle this should be applied to.

&nbsp;

- CNC mode:

  - M4 can be called without any parameters and will start the spindle of the current tool turning counterclockwise at the spindle RPM of that tool.

  - Using the S parameter will additionally set the spindle RPM of the current tool.

  - It is an error if there is no tool active or the active tool does not have a spindle assigned and there is no P parameter provided to define which spindle this should be applied to.

