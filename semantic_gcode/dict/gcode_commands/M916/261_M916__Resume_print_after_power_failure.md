## M916: Resume print after power failure

Supported in firmware 1.20 and later.

If the last print was not completed and resume information has been saved (either because the print was paused or because of a power failure), then the heater temperatures, tool selection, head position, mix ratio, mesh bed compensation height map etc. are restored from the saved values and printing is resumed.

### Parameters

- none

### Examples

M916

### Notes

RepRapFirmware also requires macro file **/sys/resurrect-prologue.g** to be present on the SD card before you can use M916. This file is executed after the heater temperatures have been set, but before waiting for them to reach the assigned temperatures. You should put commands in this file to home the printer as best as you can without disturbing the print on the bed. To wait for the heaters to reach operating temperature first, use command M116 at the start of the file.

See this page for more details: Setting up to resume a print after a power failure or planned power down

Version 1.19 of RepRapFirmware does not support M916 but you can achieve the same effect using command **M98 P"/sys/resurrect.g"**.

