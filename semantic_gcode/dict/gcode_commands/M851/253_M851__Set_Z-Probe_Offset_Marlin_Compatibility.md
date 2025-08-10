## M851: Set Z-Probe Offset (Marlin Compatibility)

RepRapFirmware 2.02 and later

### Parameters

- **Znnn** Trigger Z height

### Examples

M851 Z-2.3

### Notes

M851 is implemented for backwards compatibility with other firmware. It sets the Z probe trigger in the same way as M500 command is used.

G31 should be used in preference to M851.

