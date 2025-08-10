## M650: Set peel move parameters

This command is sent by nanoDLP to set the parameters for the peel move used after curing a layer. RepRapFirmware 2.02 ignores this command. If you use RepRapFirmware 2.03 with nanoDLP, create an empty M650.g file in the /sys folder of the SD card so that RRF will ignore it without emitting an error message.

