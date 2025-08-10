## M564: Limit axes

### Parameters

- **Hnnn** H1 = forbid movement of axes that have not been homed, H0 = allow movement of axes that have not been homed (firmware 1.21 and later)

- **Snnn** S1 = limit movement within axis boundaries, S0 = allow movement outside boundaries

### Examples

M564 S0 H0

### Description

Allow moves outside the print volume and before homing, or not. If the S parameter is 0, then you can send G codes to drive the RepRap outside its normal working volume, and it will attempt to do so. Likewise if the H parameter is zero you can move the head or bed along axes that have not been homed. The default behaviour is S1 H1. On some types of printer (e.g. Delta and SCARA), movement before homing may be prohibited regardless of the H parameter.

