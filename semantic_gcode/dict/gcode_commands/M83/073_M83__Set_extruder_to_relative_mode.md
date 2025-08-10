## M83: Set extruder to relative mode

### Examples

M83 ; relative extrusion mode

### Description

Makes the extruder interpret extrusion values as relative positions.

### Notes

- RRF maintains a flag for the extruder absolute/relative positioning state. As such, the following is true:

  - Each input channel (SD card, USB, http, telnet etc) has its own flag for the extruder absolute/relative positioning state.

  - At the end of running config.g at startup, the flag state is copied to all input channels. If no absolute/relative positioning is specified in config.g, the default M82 (absolute) is used.

  - The flag state is saved when a macro starts and is restored when a macro ends. This applies only to macros, not to job files. Changes made during job files persist for the session or until they are changed again.

