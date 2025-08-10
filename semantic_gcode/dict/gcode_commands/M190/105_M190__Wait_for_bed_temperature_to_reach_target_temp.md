## M190: Wait for bed temperature to reach target temp

### Parameters

- **Snnn** minimum target temperature, waits while heating

- **Pnnn** Bed heater slot (supported in RepRapFirmware 1.20 and later)

- **Rnnn** accurate target temperature, waits while heating and cooling

### Examples

M190 S60

Set the temperature of the bed to 60C and wait for the temperature to be reached.

Note: M190 will not wait for temperatures below 40c because in many cases they may never be reached due to ambient temps. So if you want to wait for a bed to cool, use 41c or higher.

