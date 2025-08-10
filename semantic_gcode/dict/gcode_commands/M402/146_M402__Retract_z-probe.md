## M402: Retract z-probe

### Parameters

- **P** Probe number (RRF 3.01 and later)

### Examples

M402 M402 P1

### Notes

This runs macro file **sys/retractprobe#.g** (where \# is the probe number) if it exists, otherwise **sys/retractprobe.g** if it exists.

