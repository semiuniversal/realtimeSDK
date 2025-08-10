## M503: Print settings

### Examples

M503

### Description

This command asks the firmware to reply with the current print settings stored in sys/config.g. The reply output includes the GCode commands to produce each setting. For example, the Steps Per Unit values are displayed as an M92 command.

### Notes

The output may be truncated if it is too long. M503 does **not** include values stored in config-override.g.

