## M568: Turn off/on tool mix ratios (deprecated)

**Deprecated:** from firmware 1.19 onwards, this command is no longer required or supported.

### Parameters

- **Pnnn** Tool number

- **Snnn** Whether mix ratios should be activated. 0 (default) mixing is turned off; non-zero it is turned on.

### Examples

M568 P2 S0

Turn on/off automatic mix ratios for tool 2.

### Notes

If a G1 command for the tool provides just one E value, then the mix ratio defined by M567 will always be used.

After turning off command G1 instructions must send as many E values as the tool has drives: G1 X20 E0.2:0.4:0.166:0.3

