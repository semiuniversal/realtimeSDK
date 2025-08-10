## M376: Set bed compensation taper

### Parameters

- **Hnnn** Height (mm) over which to taper off the bed compensation

### Examples

M376 H10

### Notes

This command specifies that bed compensation should be tapered linearly over the specified height, so that full bed compensation is applied at Z=0 and no bed compensation is applied when Z is at or above that height. If H is 1.0mm or less then tapering is not applied. So you can use M376 H0 to disable tapering.

RepRapFirmware does not adjust the extrusion factor to account for the layer height varying when tapered bed compensation is used. Therefore it is recommended that the taper height be set to at least 20x the maximum error in the height map, so that the maximum amount of the resulting over- or under- extrusion is limited to 5%.

