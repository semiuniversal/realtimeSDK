## M207: Set retract length

### Parameters

- **Pn** Tool number (optional, supported in RRF 3.01 and later only)

- **Snnn** positive length to retract and un-retract, in mm

- **Rnnn** positive or negative additional length to un-retract, in mm, default zero

- **Fnnn** retraction feedrate, in mm/min

- **Tnnn** feedrate for un-retraction if different from retraction, mm/min (RepRapFirmware 1.16 and later only)

- **Znnn** additional zlift/hop

### Order dependency

The M207 command must come later in config.g than the M563 command that creates the tool to which it relates.

### Examples

M207 S4.0 F2400 Z0.075

Sets the retract length used by the G10 and G11 firmware retraction and reprime commands. In RRF 3.01 and later, if a P parameter is provided then only the retraction parameters for the specified tool will be set. In other cases, the new retraction parameters will apply to all tools.

