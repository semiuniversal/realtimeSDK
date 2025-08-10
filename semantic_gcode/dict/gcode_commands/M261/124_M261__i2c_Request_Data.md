## M261: i2c Request Data

Deprecated in RRF 2.02 and later. Use M260 instead.

### Parameters

- **Ann** I2C address

- **Bnn** How many bytes to request

- **V"name"** (optional, from RRF 3.6.0) name of a new variable to receive data into. If this parameter is not present then the data read is output to the console.

### Examples

M261 A99 B5 ; Request 5 bytes from Address 99

