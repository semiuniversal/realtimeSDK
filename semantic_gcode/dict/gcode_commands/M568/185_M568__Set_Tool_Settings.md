## M568: Set Tool Settings

Available in RepRapFirmware 3.3 and later. The R and S parameters are alternatives to the temperature-setting functions of G10, which may be deprecated in the future.

### Usage

- M568 Pnnn Rnnn Snnn Fnnn An

### Parameters

- **Pnnn** Tool number. If this parameter is not provided, the current tool is used.

- **Rnnn** Standby temperature(s)

- **Snnn** Active temperature(s)

- **Fnnn** Spindle RPM

- **An** Required heater state: 0 = off, 1 = standby temperature(s), 2 = active temperature(s). Supported in RRF 3.3 and later. If there is a current tool and the P parameter specifies a different tool, then any heaters used by the current tool are not affected.

### Examples

M568 P1 R140 S205 ; set standby and active temperatures for tool 1 M568 P0 F5200 ; set spindle RPM for tool 0 M568 P2 A1 ; set tool 2 heaters to their standby temperatures

### Description

The **R** value is the standby temperature in Â°C that will be used for the tool, and the **S** value is its operating temperature. If you don't want the tool to be at a different temperature when not in use, set both values the same.

The **F** value will be used to set the configured spindle RPM for this tool's spindle. This value is direction-independent and needs to be given as a positive number. If the spindle is already running it will apply the new speed to the current direction (selected by M3/M4) immediately.

### Notes

Remember that any parameter that you don't specify will automatically be set to the last value for that parameter.

RepRapFirmware will report the tool parameters if only the tool number is specified.

Temperatures set with M568 do not wait for the heaters to reach temp before proceeding. In order to wait for the temp use a M116 command after the M568 to wait for temps to be reached.

See the T code (select tool) below. In tools with multiple heaters the temperatures for them all are specified thus: R100.0:90.0:20.0 S185.0:200.0:150.0 .

See also M585.

