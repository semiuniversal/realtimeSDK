## M99: Return from Macro/Subprogram

### Examples

M99

Returns from an M98 call, this is not required to return from the end of a macro and the macro naturally returns at the end of file.

RepRapFirmware closes the currently active macro file. If a nested macro is being run, RepRapFirmware goes up one stack level.

