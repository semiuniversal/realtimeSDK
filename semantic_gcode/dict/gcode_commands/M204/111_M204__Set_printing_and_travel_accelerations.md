## M204: Set printing and travel accelerations

### Parameters

- **Pnnn** Acceleration for printing moves

- **Tnnn** Acceleration for travel moves

### Examples

M204 P500 T2000

### Notes

- M204 sets travel and printing acceleration limits for the current job only.

- Use M201 to set per-axis accelerations and extruder accelerations. RepRapFirmware applies the M204 accelerations to the move as a whole, and also applies the limits set by M201 to each axis and extruder.

- RepRapFirmware applies M204 accelerations to the X and Y axes of the current tool. This includes active tools that map X/Y to additional axis (eg U/V). If additional axes are directly commanded (eg G1 commands to U/V axes) when the tool that maps these to X/Y is not selected, or the selected tool does not map X/Y to the other axes, then M204 limits will not be applied.

- Values are in mm/sÂ².

- This command is supported by firmware version 1.18 and later.

