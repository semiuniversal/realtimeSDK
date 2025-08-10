## M20: List SD card

### Parameters

- This command can be used without any additional parameters.

- **Snnn** Output style: 0 = text (default), 2 = JSON, 3 = Verbose JSON

- **P"path"** Folder to list, defaults to the standard folder for GCode files (0:/gcodes in RepRapFirmware)

- **Rnnn** Number of files to skip, default 0, S2 and S3 only

- **Cnnn** Maximum number of items to return, S2 and S3 only (only RRF 3.6.0 and newer)

### Examples

M20 ; lists all files in the default folder of the internal SD card (0:/gcodes) M20 S2 P"/gcodes/subdir" ; lists all files in the gcodes/subdir folder of the internal SD card, using JSON format M20 P"1:/" ; lists all files on the secondary (PanelDue) SD card's root

If Marlin compatibility is enabled, a file list response is encapsulated:

Begin file list: Traffic cone.g frog.gcode calibration piece.g End file list ok

If RepRapFirmware emulates no firmware compatibility, a typical response looks like:

GCode files: "Traffic cone.g","frog.gcode","calibration piece.g"

RepRapFirmware always returns long filenames in the case in which they are stored.

If the S2 parameter is used then the file list is returned in JSON format as a single array called "files" with each name that corresponds to a subdirectory preceded by an asterisk, and the directory is returned in variable "dir". Example:

M20 S2 P"/gcodes" {"dir":"/gcodes","first":0,"next":0,"files":\["4-piece-1-2-3-4.gcode","Hinged_Box.gcode","Hollow_Dodecahedron_190.gcode","\*Calibration pieces"\]}

Returned value "first" is the number of files that were skipped (as specified in the R parameter), and "next" is the number to skip next time to retrieve the next block of filenames. If "next" is zero then there are no more filenames.

The S3 parameter is similar to S2 but includes "type", "name", "size", "date", e.g.

M20 S3 R23 { "dir": "0:/gcodes/", "first": 23, "files": \[ { "type": "f", "name": "Hinged_Box.gcode", "size": 179638, "date": "2022-11-09T18:56:02" }, { "type": "f", "name": "frog.gcode.gcode", "size": 612786, "date": "2022-11-09T14:06:32" } \], "next": 0 }

