## M911: Configure auto save on loss of power

Supported in RepRapFirmware 1.19 and later in standalone mode. Supported in SBC mode in DSF v3.4-b2 and later (see \>here).

• RepRapFirmware 1.20 and later, DSF v3.4 and later

• RepRapFirmware 1.19

##### Parameters

- Saaa Auto save threshold in volts. The print will be stopped automatically and resume parameters saved if the voltage falls below this value. Set to around 1V to 2V lower than the voltage that appears at the Duet VIN terminals at full load. A negative or zero value disables auto save.

- Raaa Resume threshold in volts. Must be greater than the auto save voltage. Set to a high value to disable auto resume.

- P"command string" GCode commands to run when the print is stopped.

##### Notes

When the supply voltage falls below the auto save threshold while a print from SD card is in progress, all heaters will be turned off, printing will be stopped immediately (probably in the middle of a move), the position saved, and the specified command string executed. You should typically do the following in the command string:

- If possible, use M913 to reduce the motor current in order to conserve power. For example, on most printers except deltas you can probably set the X and Y motor currents to zero.

- Retract a little filament and raise the head a little. Ideally the retraction should happen first, but depending on the power reserve when low voltage is detected, it may be best to do both simultaneously.

For Duet + SBC, a solid external 5V supply is recommended for the Duet + SBC for this feature to work. When power to the Duet + SBC is cut, the SBC may turn off before the Duet can inform the SBC about the content of resurrect.g, or the SBC may lose power while it's trying to write the content of resurrect.g to the microSD card. An external 5V buck regulator may be sufficient to keep a Duet 3 Mini 5+ and SBC on long enough. For Duet 3 MB6HC, the on-board 5V regulator might not endure long enough for resurrect.g to be written to persistent storage if the Duet powers an SBC as well. Hence we recommend using an external 5V PSU if this feature is configured.

M911 with no parameters displays the current enable/disable state, and the threshold voltages if enabled.

See this page for more details:

##### Parameters

- Saaa:bbb:ccc Shutdown threshold (aaa), pause threshold (bbb) and resume threshold (ccc) all in volts, with aaa \< bbb \< ccc

##### M911 S12.0:19.5:22.0

Notes

Enables auto-pause if the power voltage drops below the pause threshold. The firmware records the current state of the print so that it can be resumed when power is restored and executes the pause procedure to attempt to park the print head using the residual energy in the power supply capacitors. If the supply voltage continues to drop below the shutdown threshold, the firmware disables all heaters and motors and goes into the shutdown state until either the voltage exceeds the resume threshold or the board is reset. In either case, it may be possible to resume the paused print. If the supply voltage does not fall below the shutdown threshold but recovers and exceeds the resume threshold, then the print is resumed automatically.

If any of the three values for the S parameter are zero or negative, or the three values are not in ascending order, then auto-save is disabled.

M911 with no parameters displays the current enable/disable state, and the threshold voltages if enabled.

