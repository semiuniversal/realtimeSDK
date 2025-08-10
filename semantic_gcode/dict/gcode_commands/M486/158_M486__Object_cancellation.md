## M486: Object cancellation

Supported in RRF 3.1 and later.

### Parameters

- **Tnn** Tell the firmware how many objects there are

- **S\[index\]** Inserted in GCode to indicate which object is being printed

- **Ann** Used in conjunction with S parameter, names an object

- **Pnn** Cancel object nn. First object is 0.

- **Unn** Uncancel object nn. First object is 0.

- **C** Cancel current object

### Examples

M486 T12 ; Total of 12 objects (otherwise the firmware must count) M486 S3 ; Indicate that the 4th object is starting now M486 S3 A"cube copy 3" ; Indicate that the 4th object is starting now and name it M486 S-1 ; Indicate a non-object, purge tower, or other global feature M486 P10 ; Cancel object with index 10 (the 11th object) M486 U2 ; Un-cancel object with index 2 (the 3rd object) M486 C ; Cancel the current object (use with care!) M486 ; List the objects on the build plate

### Descripton

This provides an interface to identify objects on the print bed and cancel them. Basic usage: Use **M486 Tnn** to tell the firmware how many objects there are, so it can provide an LCD interface. (Otherwise the firmware counts them up in the first layer.) In every layer of your GCode, preface each object's layer slice with **M486 S\[index\]** to indicate which object is being printed. The index should be zero-based. To cancel the first object, use **M486 P0**; to cancel the 5th object use **M486 P4**; and so on. The "current" object is canceled with **M486 C**.

GCodes associated with the canceled objects are no longer printed. Firmware supports this feature by ignoring G0-G3/G5 moves in XYZ while updating F and keeping the E coordinate up-to-date without extruding.

Slicers should number purge towers and other global features with a negative index (or other flag) to distinguish them from regular print objects, since it is important to preserve color changes, purge towers, and brims.

In RepRapFirmware, if the GCode file being printed contains object label comments (e.g. using the "Label objects" option in PrusaSlicer) then it is not necessary to use M486 S commands to indicate which object is being printed. Objects on the build plate will be numbered from 0 in the order in which their labels first appear in the file.

If you do use M486 S commands in the GCode file instead of object label comments, then RepRapFirmware provides an optional A parameter to the M486 S command to allow objects to be named. The name of each object need only be specified once.

For the benefit of Duet Web Control and other user interfaces, the list of objects on the build plate known to RRF may also be retrieved from the object model using M409, including their names (if available) and approximate locations.

