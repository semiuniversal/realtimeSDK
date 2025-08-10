## G17: Select XY plane for arc moves

Supported from RepRapFirmware 3.3.

**Parameters:** none

### Description

The active plane determines how the tool path of an arc (G2 or G3) is interpreted.

### Notes

- RRF maintains a flag for the selected plane for arc moves (G2 or G3). As such, the following is true:

  - Each input channel (SD card, USB, http, telnet etc) has its own flag for the selected plane.

  - At the end of running config.g at startup, the flag state is copied to all input channels. If no plane is specified in config.g, the default G17 (XY plane) is used.

  - The flag state is saved when a macro starts and is restored when a macro ends.

- G17 is supported in RRF 2.03 to RRF 3.2.2, however as no other plane selection command (G18, G19) is supported, it accepts this command, but takes no action on receiving it.

