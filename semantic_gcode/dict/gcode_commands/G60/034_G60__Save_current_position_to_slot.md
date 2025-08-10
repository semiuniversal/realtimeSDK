## G60: Save current position to slot

Supported in firmware 1.21 and later.

### Usage

- **G60 Snn**

### Parameters

- **Snn** specifies memory slot number (0-based) to save into (default 0)

RepRapFirmware for Duets generally provides slots 0 thru 5. When a print is paused the coordinates are saved to slot 1 automatically, and at the start of a tool change the coordinates are saved to slot 2 automatically. The remaining slots are free to use for any purpose. Use G0 or G1 with the appropriate R parameter to move the current tool to a saved position.

**Note:** Do not use G60 in pause.g . It is not needed as the co-ordinates are saved in slot 1 automatically. Using it in pause.g can lead to issues with restoring the primary and secondary motion system correctly in RRF 3.5.1

