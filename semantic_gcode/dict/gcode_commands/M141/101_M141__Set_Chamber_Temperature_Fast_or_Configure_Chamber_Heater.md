## M141: Set Chamber Temperature (Fast) or Configure Chamber Heater

### Parameters

- **Pnnn** (RRF 2.03 and later only) Chamber heater slot, default 0

- **Hnnn** Heater number

- **Snnn** Active/Target temperature

- **Rnnn** Standby temperature

### Order dependency

In RRF3 a M141 command with H parameter (other than H-1) must come after the M950 command that creates that heater, and before any M143 command that sets a temperature limit for that heater.

### Examples

M141 S30 M141 H3 M141 P1 H4

The first example sets the temperature of the chamber to 30oC and return control to the host immediately (i.e. before that temperature has been reached by the chamber). The second example specifies that chamber heater 0 (the default if no P parameter is given) uses heater 3. The third example specifies that chamber heater 1 uses heater 4.

### Notes

- M141 commands with H parameters would normally be used only in the config.g file.

- On the Duet 3 MB6HC and MB6XD you can configure up to 4 chamber heaters; on Duet 3 Mini 5+, 2 chamber heaters; on Duet 2 WiFi/Ethernet, 4 chamber heaters; on Duet 2 Maestro, 2 chamber heaters.

