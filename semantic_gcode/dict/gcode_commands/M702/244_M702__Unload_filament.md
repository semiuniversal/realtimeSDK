## M702: Unload filament

Supported in RepRapFirmware 2.02 and newer.

This code is intended to unload the previously loaded filament from the selected tool.

### Parameters

- This command can be used without any additional parameters.

- **Pnn** P0 sets loaded filament to null without running the filament unload script; P1 (default) sets loaded filament to null and runs the unload script (RRF3.6.0 and later)

### Examples

M702

### Notes

RepRapFirmware will do the following when called:

- Run the macro file "unload.g" in the subdirectory of the given material (e.g. /filaments/PLA/unload.g)

- Change the filament name of the current tool, so it can be reported back to Duet Web Control

