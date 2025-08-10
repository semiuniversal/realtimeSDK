## M191: Wait for chamber temperature to reach target temp

### Parameters

- **Snnn** minimum target temperature, waits while heating

- **Rnnn** accurate target temperature, waits while heating and cooling

- **Pnnn** Chamber slot. This defaults to 0 and the maximum is dependent on the board type. (Supported in RepRapFirmware 1.20 and later)

### Examples

M191 S60

Set the temperature of the build chamber to 60C and wait for the temperature to be reached.

