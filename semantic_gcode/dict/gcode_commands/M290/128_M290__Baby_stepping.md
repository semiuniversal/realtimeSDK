## M290: Baby stepping

Supported in firmware version 1.18 and later.

### Parameters

- **Snnn** Amount to baby step Z in mm. Positive values raise the head or lower the bed, negative values do the opposite.

- **Znnn** Synonym for S (RepRapFirmware 1.21 and later)

- **X,Y,U...** Amount to babystep other axes (RRF 2.03 and later)

- **Rn** (Optional, RepRapFirmware 1.21 and later) R1 = relative (add to any existing babystep amount, the default), R0 = absolute (set babystepping offset to the specified amount)

### Examples

M290 S0.05 ; babystep the head up 0.05mm M290 R0 S0 ; clear babystepping (RepRapFirmware 1.21 and later only)

### Notes

This command tells the printer to apply the specified additional offset to the Z coordinate for all future moves, and to apply the offset to moves that have already been queued if this can be done. Baby stepping is cumulative, for example after M290 S0.1 followed by M290 S-0.02, an offset of 0.08mm is used.

M290 with no parameters reports the accumulated baby stepping offset. Marlin doesn't track accumulated babysteps.

In RepRapFirmware 1.19 and earlier, the babystepping offset is reset to zero when the printer is homed or the bed is probed. In RepRapFirmware 1.21 and later, homing and bed probing don't reset babystepping, but you can reset it explicitly using M290 R0 S0.

