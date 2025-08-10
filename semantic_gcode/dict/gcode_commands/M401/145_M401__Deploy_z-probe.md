## M401: Deploy z-probe

### Parameters

- **P** Probe number (RRF 3.01 and later)

### Examples

M401 M401 P1

This runs macro file **sys/deployprobe#.g** (where \# is the probe number) if it exists, otherwise **sys/deployprobe.g** if it exists.

