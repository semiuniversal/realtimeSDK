## M500: Store parameters

Implemented in RepRapFirmware 1.17 and later.

### Parameters

- **Pnn** or **Pnn:nn** Stores additional parameters. P31 stores G31 Probe status parameters; P10 stores G10/M568 tool offsets.

### Examples

M500 M500 P31 M500 P10 M500 P10:31

### Description

Save current parameters to the sys/config-override.g on the SD card, similar to other firmware's storing to EEPROM. The parameters stored are:

- M307 auto tune results

- PID parameters, if you used M301 to override the auto tune PID settings

- Delta printer M665 and M666 settings

- Any M208 axis limits that were determined using a G1 H3 (or S3 in RRF 2.x and earlier) move

- If the P31 parameter is used, the G31 trigger height, trigger value and X and Y offsets for each possible Z probe type (in older firmware versions the G31 parameters are stored even if the P31 parameter is not present)

- If the P10 parameter is present, the G10 tool offsets

Ensure that M501 is at the end of config.g in order for the values in config-override.g to be loaded on startup.

