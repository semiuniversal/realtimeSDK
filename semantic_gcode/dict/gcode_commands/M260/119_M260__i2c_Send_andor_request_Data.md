## M260: i2c Send and/or request Data

Send and/or receive data over the i2c bus. Supported in RepRapFirmware 1.21 and later.

### Parameters

- **Ann** I2C address

- **Rnn** Number of bytes to receive (optional) - firmware 2.02 and later only

- **Bnn:nn:nn...** Bytes to send (optional in firmware 2.02 and later)

- **S"ascii data"** data to send (alternative to B parameter). Each character is converted to the corresponding ASCII value. Ignored if **B** parameter is present.

- **V"name"** (optional, from RRF 3.6.0) name of a new variable to receive data into. If this parameter is not present then the data read is output to the console.

### Examples

M260 A5 B65 ; send 'A' to address 5 now M260 A"x7F" B65 ; send 'A' to address 7F (hex) M260 A0 B82:101:112:82:97:112 ; send 'RepRap' to address 0 M260 A"x71" B19 R2 ; send 19 to address 71 (hex) and read 2 bytes back M260 A5 R2 ; read 2 bytes of data from address 5 M260 A5 S"Hello world" ; send "Hello world" to address 5

Hex addresses are only supported in firmware 2.02 and later.

