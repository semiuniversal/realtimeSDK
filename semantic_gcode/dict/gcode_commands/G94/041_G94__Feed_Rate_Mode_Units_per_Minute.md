## G94: Feed Rate Mode (Units per Minute)

Supported from firmware version 3.5

### Parameters

- No additional parameters

### Examples

G94

### Description

G94 is Units per Minute Mode. In units per minute feed mode, an F word is interpreted to mean the controlled point should move at a certain number of inches per minute, millimeters per minute, or degrees per minute, depending upon what length units are being used and which axis or axes are moving.

### Notes

- RRF maintains a flag for the feed rate mode selected, which is either Inverse Time Mode or Units per Minute. As such, the following is true:

  - Each input channel (SD card, USB, http, telnet etc) has its own flag for the feed rate mode state.

  - At the end of running config.g at startup, the flag state is copied to all input channels. If no feed rate mode is specified in config.g, the default G94 (Units per Minute) is used.

  - The flag state is saved when a macro starts and is restored when a macro ends. This applies only to macros, not to job files. Changes made during job files persist for the session or until they are changed again.

# M-commands

