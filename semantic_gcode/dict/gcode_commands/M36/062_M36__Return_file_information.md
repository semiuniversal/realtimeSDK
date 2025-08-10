## M36: Return file information

### Examples

M36 "filename.g" M36

Returns information in JSON format for the specified SD card file (if a filename was provided) or for the file currently being printed. A sample response is:

{"err":0,"size":436831,"fileName":"EscherLizardModified.gcode","lastModified":"2017-09-21T16:58:07","height":5.20,"layerHeight":0.20,"printTime":660,"simulatedTime":1586,"filament":\[1280.7\],"generatedBy":"Simplify3D(R) Version 4.0.0"}

The "err" field is zero if successful, nonzero if the file was not found or an error occurred while processing it. The "size" field should always be present if the operation was successful. The presence or absence of other fields depends on whether the corresponding values could be found by reading the file. The "filament" field is an array of the filament lengths required from each spool. The size is in bytes, the times are in seconds, all other values are in mm. "printTime" is the printing time estimated by the slicer, "simulationTime" is the time measured when the print was simulated by the firmware. The fields may appear in any order, and additional fields may be present. Versions of RepRapFirmware prior to 3.4 do not provide the "fileName" field if information for a specific file was requested.

RepRapFirmware 3.4 and later also return information about thumbnail images embedded in the GCode file via an additional JSON field "thumbnails". A sample value for this field is:

"thumbnails":\[{"width":32,"height":32,"fmt":"qoi","offset":103,"size":2140},{"width":220,"height":220,"fmt":"qoi","offset":2384,"size":25464}\]

The "fmt" field denotes the encoding of the thumbnail and is one of "png", "qoi" or "jpeg". The "thumbnails" field is omitted entirely if there are no thumbnails embedded in the GCode file.

