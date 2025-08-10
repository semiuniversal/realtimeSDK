## M450: Report Printer Mode

Supported by RRF 1.20 and later.

### Parameters

- none

### Examples

M450

### Notes

Printers can be used for different task by exchanging the toolhead. Depending on the tool, a different behavior of some commands can be expected. This command reports the current working mode. Possible responses are:

PrinterMode:FFF

PrinterMode:Laser

PrinterMode:CNC

The default at power up is FFF.

