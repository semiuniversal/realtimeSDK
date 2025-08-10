## M701: Load filament

RepRapFirmware 1.19 and later implements a filament management mechanism to load and unload different materials. This code may be used to load a material for the active tool.

### Parameters

- This command can be used without any additional parameters.

- **Snn** Filament to load

- **Pnn** P0 sets loaded filament without running the filament load script; P1 (default) sets loaded filament and runs the load script (RRF3.6.0 and later)

### Examples

M701 S"PLA"

### Notes

This code will work only for tools that have exactly one extruder assigned.

When called the firmware does the following:

- Run the macro file "load.g" in the subdirectory of the given material (e.g. /filaments/PLA/load.g)

- Change the filament name of the associated tool, so it can be reported back to Duet Web Control

If this code is called without any parameters, RepRapFirmware will report the name of the loaded filament (if any).

