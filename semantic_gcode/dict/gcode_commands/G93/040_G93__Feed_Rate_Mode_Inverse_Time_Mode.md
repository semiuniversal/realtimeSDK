## G93: Feed Rate Mode (Inverse Time Mode)

Supported from firmware version 3.5

### Parameters

- No additional parameters

### Examples

G93

### Description

G93 is Inverse Time Mode. In inverse time feed rate mode, an F word means the move should be completed in (one divided by the F number) minutes. For example, F2.0 means the move should be completed in a half a minute.

### Notes

- When the inverse time feed rate mode is active, an F word must appear on every line which has a G1, G2, or G3 motion.

- An F word on a line that does not have G1, G2, or G3 is ignored.

- Being in inverse time feed rate mode does not affect G0 (rapid move) motions.

- RRF maintains a flag for the feed rate mode selected, which is either Inverse Time Mode or Units per Minute. As such, the following is true:

  - Each input channel (SD card, USB, http, telnet etc) has its own flag for the feed rate mode state.

  - At the end of running config.g at startup, the flag state is copied to all input channels. If no feed rate mode is specified in config.g, the default G94 (Units per Minute) is used.

  - The flag state is saved when a macro starts and is restored when a macro ends. This applies only to macros, not to job files. Changes made during job files persist for the session or until they are changed again.

