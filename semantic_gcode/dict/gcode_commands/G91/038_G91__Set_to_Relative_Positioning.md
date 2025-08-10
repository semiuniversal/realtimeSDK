## G91: Set to Relative Positioning

### Parameters

- No additional parameters

### Usage

- G91

### Description

All coordinates from now on are relative to the last position.

### Notes

- RepRapFirmware uses M83 to set the extruder to relative mode: extrusion is NOT set to relative using G91

- RRF maintains a flag for the absolute/relative positioning state. As such, the following is true:

  - Each input channel (SD card, USB, http, telnet etc) has its own flag for the absolute/relative positioning state.

  - At the end of running config.g at startup, the flag state is copied to all input channels. If no absolute/relative positioning is specified in config.g, the default G90 (absolute) is used.

  - The flag state is saved when a macro starts and is restored when a macro ends. This applies only to macros, not to job files. Changes made during job files persist for the session or until they are changed again.

