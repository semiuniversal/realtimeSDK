## M105: Get Extruder Temperature

### Parameters

- This command can be used without any additional parameters.

- **Rnnn** Response sequence number1

- **Snnn** Response type1

### Examples

M105 M105 S2

Request the temperature of the current extruder and the build base in degrees Celsius. Reports the current and target temperatures of all active heaters.

### Notes

1 Returns a JSON-formatted response if parameter S2 or S3 is specified. Additionally, parameter Rnn may be provided, where nn is the sequence number of the most recent GCode response that the client has already received. M105 S2 is equivalent to M408 S0, and M105 S3 is equivalent to M408 S2. Usage of these forms of M105 is deprecated, please use M408 instead.

