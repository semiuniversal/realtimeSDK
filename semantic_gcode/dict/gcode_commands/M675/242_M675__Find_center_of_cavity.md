## M675: Find center of cavity

This code is intended to find the center of a cavity that can be measured using the configured axis endstop. It probes towards the minimum end of the specified axis to find one side of the cavity, backs off a little, and then probes towards the maximum end of the same axis to find the other side.

### Parameters

- **X,Y,Z** Axis to probe on

- **Fnnnn** Probing feedrate

- **Rnnn** Distance to back off after finding the minimum before probing for the maximum, sufficient to ensure that the probe or endstop stops registering contact

- **Pnnn** Use probe with the given number instead of endstop (RRF3.x and later)

### Examples

M675 X R2 F1200

### Notes

If using a Z probe for this purpose, make sure the endstop type for the corresponding axis is updated before this code is run.

How it works:

- Once this code starts, RepRapFirmware will move to the lower end looking for an endstop to be triggered.

- Once it is triggered, the lower position is saved and the axis maximum is probed.

- As soon as both triggers have been hit, the center point is calculated and the machine moves to the calculated point.

