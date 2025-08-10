## M301: Set PID parameters

### Parameters

- **Hnnn** heater number

- **Pnnn** proportional (Kp)

- **Innn** integral (Ki)

- **Dnnn** derivative (Kd)

### Examples

M301 H1 ; Report PID values M301 H1 P20 I0.5 D100 ; Set PID values

### Order dependency

- **RRF 3.x**: The M301 command must come later in config.g than the M950 command that created the heater number it refers to.

### Notes

Sets Proportional (P), Integral (I) and Derivative (D) values for hot end. See also M303

- H: Is the heater number, and is compulsory. H0 is the bed, H1 is the first hot end, H2 the second etc.

- P: Proportional value

- I: Integral value

- D: Derivative value

The P, I and D values must be provided scaled by a factor of 255, for compatibility with older firmwares.

Note: PID parameters are computed automatically when the M307 command is used to define the heater model, or from the default heater model if no M307 command is provided. You can use M301 to override those computed PID parameters, but this is not recommended because it prevents RepRapFirmware from using different PID parameters depending on the heating phase.

