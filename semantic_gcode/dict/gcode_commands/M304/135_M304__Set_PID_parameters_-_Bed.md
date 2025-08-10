## M304: Set PID parameters - Bed

### Parameters

- This command can be used without any additional parameters.

- **Pnnn** proportional (Kp)

- **Innn** integral (Ki)

- **Dnnn** derivative (Kd)

### Examples

M304 P1 I2 D3 M304 ; Report parameters

### Notes

Sets Proportional, Integral and Derivative values for bed. This command is identical to M301 except that the H parameter (heater number) defaults to zero.

