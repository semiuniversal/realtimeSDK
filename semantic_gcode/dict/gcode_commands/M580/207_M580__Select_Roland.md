## M580: Select Roland

This M-code is not available by default. To enable it change the value of SUPPORT_ROLAND in the Pins\_\*.h file from 0 to 1 and recompile the firmware.

The \>Modela MDX-20 and similar milling machines are very widely available in hackerspaces and maker groups, but annoyingly they don't speak GCodes. As all RepRap firmware includes a GCode interpreter, it is often easy to add functions to convert GCodes to RML.

### Parameters

- **Rnnn** Whether Roland mode should be activated

- **Pnnn** Initial text to send to the Roland controller

### Examples

M580 R1 PVS4;!VZ2;!MC1;

### Description

M580 selects a Roland device for output if the R field is 1, and returns to native mode if the R field is 0.

The optional P string is sent to the Roland if R is 1. It is permissible to call this repeatedly with R set to 1 and different strings in the P field to communicate directly with a Roland.

