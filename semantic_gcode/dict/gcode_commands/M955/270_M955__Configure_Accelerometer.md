## M955: Configure Accelerometer

Supported in RRF 3.4 and later (limited support in 3.3)

This command configures an accelerometer.

### Parameters (provisional)

- **Pnn** or **Pbb.nn** Accelerometer to use (required)

- **Inn** Accelerometer orientation

- **Snnn** Sample rate (Hz)

- **Rnn** Resolution (bits), typically 8, 10 or 12

- **C"aaa+bbb"** Pins to use for CS and INT (in that order) when connecting the accelerometer via SPI

- **Q**nnn (RRF 3.3 and later) SPI clock frequency (optional, default 2000000 i.e. 2MHz)

### Examples

M955 P0 C"spi.cs1+spi.cs0" I10 ; configure accelerometer on mainboard using SPI pins and specify orientation M955 P121.0 I10 ; configure accelerometer on toolboard with CAN address 121 and specify orientation

### Notes

- The **P** parameter selects which accelerometer to use and is mandatory. To use an accelerometer on a CAN-connected expansion board, use the form **P**board-address.device-number for example **P22.0**. Use **P0** for an accelerometer connected locally (i.e. on the mainboard) via SPI.

- If none of the other parameters are provided, the current configuration of the specified accelerometer is reported. Otherwise the configuration of that accelerometer is adjusted according to the I, S, and R parameters. These configuration settings persist until they are changed.

- The **C** parameter is needed only when the accelerometer is connected to a mainboard, and defines the pins used for the CS and INT signals. It is not needed when using a toolboard with integrated accelerometer.

- The **I** (orientation) parameter tells the firmware which of the 24 possible orientations the accelerometer chip is in relative to the printer axes. It is expressed as a 2-digit number. The first digit specifies which machine direction the Z axis of the accelerometer chip (usually the top face of the chip) faces, as follows: 0 = +X, 1 = +Y, 2 = +Z, 4 = -X, 5 = -Y, 6 = -Z. The second digit expresses which direction the X axis of the accelerometer chip faces, using the same code. If the accelerometer chip axes line up with the machine axis, the orientation is 20. This is the default orientation if no orientation has been specified.

- The **S** and **R** parameters control how the accelerometer is programmed. The R parameter is ignored unless the S parameter is also provided. If S is provided but R is missing, a default resolution is used. The sensor resolution will be adjusted to be no greater than the value of the R parameter (or the minimum supported resolution if greater), then the sensor sampling rate will be adjusted to a value supported at that resolution that is close to the S parameter. The actual rate and resolution selected can be found by using M955 with just the P parameter.

- For more information on connecting accelerometers, see the Connecting an accelerometer wiki page.

