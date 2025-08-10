## G20: Set Units to Inches

### Examples

G20 ; set units to inches

### Description

Units from this command onwards are in inches. Note that this is only intended to affect G0, G1 and other commands commonly found in GCode files that represent objects to print. Specifically G20 only affects: G0 to G3, G10 and G92. So you should use metric values in config.g when configuring the printer and then change to inches with G20 at the end of it if the GCodes you want to send to move the machine are expressed in inches by default.

### Notes

- From RRF 2.03 and later, RRF maintains a flag for the set units (mm or inches, G20 or G21). As such, the following is true:

  - Each input channel (SD card, USB, http, telnet etc) has its own flag for the units setting.

  - At the end of running config.g at startup, the flag state is copied to all input channels. If no units are specified in config.g, the default G21 (mm) is used.

  - The flag state is saved when a macro starts and is restored when a macro ends.

