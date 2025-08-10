## G21: Set Units to Millimeters

### Examples

G21 ; set units to millimeters

### Description

Units from this command onwards are in millimeters. This is the default.

### Notes

- From RRF 2.03 and later, RRF maintains a flag for the set units (mm or inches, G20 or G21). As such, the following is true:

  - Each input channel (SD card, USB, http, telnet etc) has its own flag for the units setting.

  - At the end of running config.g at startup, the flag state is copied to all input channels. If no units are specified in config.g, the default G21 (mm) is used.

  - The flag state is saved when a macro starts and is restored when a macro ends.

