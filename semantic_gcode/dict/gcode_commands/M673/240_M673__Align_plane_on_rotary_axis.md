## M673: Align plane on rotary axis

Supported in RepRapFirmware 2.02 and later.

This code is intended to align a plane that is mounted on a rotary axis.

### Parameters

- **U,V,W,A,B,C** Rotary axis name on which the plane is mounted

- **Pnnn** Factor to multiply the correction amount with (defaults to 1)

### Examples

M673 A

### Notes

To make use of this code it is required to take two probe points via G30 P first.

