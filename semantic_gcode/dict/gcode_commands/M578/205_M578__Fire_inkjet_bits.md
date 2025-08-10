## M578: Fire inkjet bits

This command is not enabled unless the SUPPORT_INKJET feature is enabled when the firmware is built.

### Parameters

- **Pnnn** Inkjet head number

- **Snnn** Bit pattern

### Examples

M578 P3 S5

This fires inkjet head 3 (the P field) using the bit pattern specified by the S field, in the example shown would fire bits 101.

### Notes

If the P parameter is ommitted inkjet 0 is assumed.

This is a version of the M700 command used by \>Inkshield.

An alternative way of controlling inkjets would be to use the P parameter on the M670 command.

