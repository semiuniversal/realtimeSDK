## M116: Wait for temperature to be reached

### Parameters

- This command can be used without any additional parameters.

- **Pnnn** Tool number

- **Hnnn** Heater number

- **Cnnn** Chamber number

- **Snn** Tolerance in degC (firmware 2.02/1.23 and later, default 2)

### Examples

M116 M116 P1 M116 H0 S5

The first example waits for all bed, chamber, and tool heaters to arrive at their set values. Note that in v3.5, the scope of tool heaters to wait for is limited to the heaters of the currently selected tool of the selected motion system.

The second shows the optional 'P' parameter that is used to specify a tool number. If this parameter is present, then the system only waits for temperatures associated with that tool to arrive at their set values. This is useful during tool changes, to wait for the new tool to heat up without necessarily waiting for the old one to cool down fully.

The third example waits for the bed to reach its temperature +-5 degC.

See also M109.

Recent versions of RepRapFirmware also allow a list of the heaters to be specified using the 'H' parameter, and if the 'C' parameter is present, this will indicate that the chamber heater should be waited for.

'S' parameter sets the temperature tolerance, default 2 degC.

Note: M116 will not wait for temperatures below 40c because in many cases they may never be reached due to ambient temps. So if you want to wait for a hotend or bed to cool, use 41c or higher.

