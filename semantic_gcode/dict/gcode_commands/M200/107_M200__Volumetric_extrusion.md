## M200: Volumetric extrusion

Supported in RRF 1.19 and later

### Parameters

- **Daaa:bbb:ccc...** Sets filament diameter to aaa for extruder 0, bbb for extruder 1 and so on. If any of aaa, bbb etc. are zero then volumetric extrusion is disabled for that extruder.

- **Daaa** Sets filament diameter (or disables volumetric extrusion) for all extruders

- **S\[bool\]** Enable or disable volumetric extrusion for this input channel (RepRapFirmware 3.5 and later)

### Examples

M200 D0 ; disable volumetric extrusion on all extruders M200 S0 ; disable volumetric extrusion for this input channel (RRF 3.5 and later) M200 D1.75 ; set all extruder filament diameters to 1.75mm M200 D1.75:3.0:1.75 ; set extruder 0 to 1.75mm, extruder 1 to 3.0mm and all remaining extruders to 1.75mm

### Description

Volumetric extrusion is an option you can set in some slicers whereby all extrusion amounts are specified in mm3 (cubic millimetres) of filament instead of mm of filament. This makes the GCode independent of the filament diameter, potentially allowing the same GCode to run on different printers. The purpose of the M200 command is to inform the firmware that the GCode input files have been sliced for volumetric extrusion, and to provide the filament diameter so that the firmware can adjust the requested extrusion amount accordingly.

### Notes

- Sending M200 without parameters reports the current volumetric extrusion state and (where appropriate) filament diameter for each extruder.

- To set filament diameter without enabling volumetric extrusion, use M404.

- Note that if you use slicer-commanded retraction, the retraction amounts must be specified in mm3 too. If instead you use firmware retraction, then the firmware retraction amounts specified using the M207 command are still interpreted as mm.

- RRF maintains a flag for the volumetric extrusion state. As such, the following is true:

  - Each input channel (SD card, USB, http, telnet etc) has its own flag for the volumetric extrusion state.

  - At the end of running config.g at startup, the flag state is copied to all input channels. If no volumetric extrusion is specified in config.g, the default (disabled) is used.

  - The flag state is saved when a macro starts and is restored when a macro ends.

