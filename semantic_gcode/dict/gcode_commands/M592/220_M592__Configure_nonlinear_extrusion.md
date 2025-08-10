## M592: Configure nonlinear extrusion

### Parameters

- **Dnn** Extruder drive number (0, 1, 2...)

- **A**nnn A coefficient in the extrusion formula, default zero

- **B**nnn B coefficient in the extrusion formula, default zero

- **L**nnn Upper limit of the nonlinear extrusion compensation, default 0.2

- **T** nnn Reserved for future use, for the temperature at which these values are valid

### Examples

M592 D0 A0.01 B0.0005 ; set parameters for extruder drive 0 M592 D0 ; report parameters for drive 0

### Description

Most extruder drives use toothed shafts to grip the filament and drive it through the hot end. As the extrusion speed increases, so does the back pressure from the hot end, and the increased back pressure causes the amount of filament extruded per step taken by the extruder stepper motor to reduce. This may be because at high back pressures, each tooth compresses and skates over the surface of the filament for longer before it manages to bite. See \>graph here for an example.

### Notes

- Nonlinear extrusion is an experimental feature in RepRapFirmware to compensate for this effect. The amount of extrusion requested is multiplied by (1 + min(L, Av + Bv^2)) where v is the requested extrusion speed (calculated from the actual speed at which the move will take place) in mm/sec.

- Nonlinear extrusion is not applied to extruder-only movements such as retractions and filament loading.

