## M666: Set delta endstop adjustment

Sets delta endstops adjustments.

### Parameters

- **Xnnn** X axis endstop adjustment

- **Ynnn** Y axis endstop adjustment

- **Znnn** Z axis endstop adjustment

- **Annn** X bed tilt in percent (RRF 1.16 and later)

- **Bnnn** Y bed tilt in percent (RRF 1.16 and later)

### Examples

M666 X-0.1 Y+0.2 Z0

### Notes

Positive endstop adjustments move the head closer to the bed when it is near the corresponding tower. Endstop corrections are expressed in mm.

