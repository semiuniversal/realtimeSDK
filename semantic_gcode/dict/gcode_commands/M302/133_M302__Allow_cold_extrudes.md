## M302: Allow cold extrudes

### Parameters

- This command can be used without any additional parameters.

- **Pnnn** Cold extrude allow state

- **Snnn** Minimum extrusion temperature (RepRapFirmware 2.02 and later)

- **Rnnn** Minimum retraction temperature (RepRapFirmware 2.02 and later)

### Examples

M302 ; Report current state M302 P1 ; Allow cold extrusion M302 S120 R110 ; Allow extrusion starting from 120Â°C and retractions already from 110Â°C

### Notes

This tells the printer to only allow movement of the extruder motor above a certain temperature, or if disabled, to allow extruder movement when the hotend is below a safe printing temperature.

The minimum temperatures for extrusion can be set using the Snnn parameter with a default value of 160Â°C if unset. A minimum retraction temperature can be set with the Rnnn parameter. The default for this is 90Â°C.

M302 with no parameters it will report the current cold extrusion state.

One limitation of M302 is that it requires a thermistor to be present for the temperature to be monitored. If your system does not have a thermistor or heater to be monitored, you can define your tool in M563 without a heater to disable cold extrusion protection on that tool. Example:

M563 P0 S"Pump" D0 F0

Note the lack of H parameter.

