## M755: Set alignment mode for 3D scanner

Sends the ALIGN ON/OFF command the attached 3D scanner.

### Parameters

- Pnnn Whether to turn on (\> 0) or off (\<= 0) the alignment feature

### Examples

M755 P1 M755 P0

### Notes

Some devices turn on a laser when this command is received. If the 'P' parameter is missing, equal to, or less than 0, the alignment feature is turned off. Depending on whether the alignment is turned on or off, either align_on.g or align_off.g is executed before the ALIGN command is sent to the scanner.

