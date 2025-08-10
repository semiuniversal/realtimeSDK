## M912: Set electronics temperature monitor adjustment

### Parameters

- **Pnnn** Temperature monitor channel, default 0

- **Snnn** Value to be added to the temperature reading in degC

### Examples

M912 P0 S10.5

### Notes

Many microcontrollers used to control 3D printers have built-in temperature monitors, but they normally need to be calibrated for temperature reading offset. The S parameter specifies the value that should be added to the raw temperature reading to provide a more accurate result.

(Currently only for the CPU on-chip temperature sensor P0. Other P parameter could in the future be added for boards with multiple on-chip sensors)

