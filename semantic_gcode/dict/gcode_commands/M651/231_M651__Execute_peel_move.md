## M651: Execute peel move

This command is sent by nanoDLP to execute a peel move after exposing a layer. RepRapFirmware 2.02 executes macro /sys/peel-move.g in response to this command. To use RepRapFirmware 2.03 or later with nanoDLP, create a macro file M651.g in the /sys folder of the SD card and populate it with the commands needed to execute the peel move.

