## M703: Configure filament

After assigning a filament to a tool, this command may be used to run /filaments/\<filament name\>/config.g to set parameters like temperatures, extrusion factor, retract distance. If no filament is loaded, the code completes without a warning.

### Parameters

- This command can be used without any additional parameters.

### Examples

M703

### Notes

If the filaments feature is used, it is recommended to put this code into tpost\*.g to ensure the right filament parameters are set.

