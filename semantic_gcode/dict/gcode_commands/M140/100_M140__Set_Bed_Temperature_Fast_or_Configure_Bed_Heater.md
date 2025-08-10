## M140: Set Bed Temperature (Fast) or Configure Bed Heater

### Parameters

- **Pnnn** (RRF 1.20 and later) Bed heater slot, default 0

- **Hnnn** Heater number

- **Snnn** Active/Target temperature

- **Rnnn** Standby temperature

### Order dependency

In RRF3 a M140 command with H parameter (other than H-1) must come after the M950 command that creates that heater, and before any M143 command that sets a temperature limit for that heater.

### Examples

M140 H0 ; bed heater 0 uses heater 0 M140 P1 H1 ; bed heater 1 uses heater 1 M140 H-1 ; disable bed heater M140 S55 ; set bed temperature to 55C M140 S65 R40 ; set bed temperature to 65C and bed standby temperature to 40C M140 S-273.1 ; switch off bed heater

The first example informs the firmware that bed heater 0 (implied, because no P parameter is provided) uses heater 0. The second example informs the firmware that bed heater 1 (P1) uses heater 1. The third example disables the bed heater. No bed heaters will be shown in DWC. The fourth example sets the temperature of the bed heater to 55oC and returns control to the host immediately (i.e. before that temperature has been reached by the bed). The fifth example sets the bed temperature to 65oC and the bed standby temperature to 40oC. The sixth example sets the active/target bed temperature to absolute negative temperature (-273 or lower). This switches off the bed heater.

### Notes

- If a temperature close to absolute zero is set (strictly less than -273Â°C in RRF 3.3 and earlier, less than or equal to -273Â°C in RRF 3.4.0 and later), the bed heater will be switched off.

- The 'H' parameter sets the heated bed heater number(s). If no heated bed is present, a negative value may be specified to disable it. M140 commands with H parameters would normally be used only in the config.g file.

- On the Duet 3 MB6HC and MB6XD you can configure up to 12 bed heaters; on Duet 3 Mini 5+, 2 bed heaters; on Duet 2 WiFi/Ethernet, 4 bed heaters; on Duet 2 Maestro, 2 bed heaters.

