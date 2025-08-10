## M905: Set local date and time

Supported in RepRapFirmware version 1.16 and later.

Updates the machine's local date and time or reports them if no parameters are specified.

### Parameters

- **Pnnn** Current date in the format YYYY-MM-DD

- **Snnn** Current time in the format HH:MM:SS

- **Tnnn** (Supported by DSF v3.3 and later) Timezone to set (e.g Europe/Berlin)

- **Annn** (Supported by DSF v3.5.3 and later) Automatically set date and time via NTP

### Examples

M905 P2016-10-26 S00:23:12 M905 P"2016-10-26" S"00:23:12" T"Europe/Berlin" ; DSF v3.3 and later only M905 A0 P"2024-09-17" S"15:19:54" T"Europe/Berlin" ; DSF v3.5.3 and later only

### Notes

The time should be specified in 24-hours format as in "13:45" instead of 1:45PM.

Timezone setting is only supported by Duets in SBC mode with DSF v3.3 and later.

