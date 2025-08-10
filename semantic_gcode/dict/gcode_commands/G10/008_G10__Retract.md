## G10: Retract

This form of the G10 command is recognised by having no parameters.

### Parameters

- (no parameters in the RepRapFirmware implementation)

### Examples

G10

### Notes

- Retracts filament then performs any zlift/hop according to settings of M207.

- RepRapFirmware recognizes G10 as a command to set tool offsets and/or temperatures if the P parameter is present, and as a retraction command if it is absent.

- G10 will retract all extruders associated with a tool as defined by M563, regardless of the mixing ratio set in M567

