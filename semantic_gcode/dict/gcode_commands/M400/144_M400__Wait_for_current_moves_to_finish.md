## M400: Wait for current moves to finish

### Parameters

- **Sn** (RRF 3.5.0 and later only, optional, default 0) 0 = release all axes and extruders owned by the current motion system except for axes/extruders needed by the current tool, 1 = do not release axes or extruders

### Examples

M400 ; wait until motion stops, in RRF 3.5.0 and later with multiple motion systems release owned axes and extruders M400 S1 ; wait until motion stops, do not release any axes or extruders

### Notes

Finishes all current moves and and thus clears the buffer. That's identical to G4 P0 except that G4 P0 does not release any axes or extruders.

