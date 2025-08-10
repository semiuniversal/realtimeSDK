## G10: Tool Temperature Setting

Note that this use of G10 may be deprecated in a future version of RRF, although it will remain available for a substantial time. It will be replaced with M568 which can already be used for temperature setting in firmware 3.3 and later.

This form of the G10 command is recognised by having a P combined with at least an R or S parameter.

### Usage

- G10 Pnnn Rnnn Snnn

### Parameters

- **Pnnn** Tool number

- **Rnnn** Standby temperature(s)

- **Snnn** Active temperature(s)

### Order dependency

The tool must be created with M563 before it is referenced with this command.

### Examples

G10 P1 R140 S205 ; set standby and active temperatures for tool 1

Remember that any parameter that you don't specify will automatically be set to the last value for that parameter.

The R value is the standby temperature in oC that will be used for the tool, and the S value is its operating temperature. If you don't want the tool to be at a different temperature when not in use, set both values the same.

Temperatures set with G10 do not wait for the heaters to reach temp before proceeding. In order to wait for the temp use a M116 command after the G10 to wait for temps to be reached.

See the T code (select tool) below. In tools with multiple heaters the temperatures for them all are specified thus: R100.0:90.0:20.0 S185.0:200.0:150.0 .

