## M576: Set SPI comms parameters

Supported in RRF 3.4 and later in SBC mode. This sets the communications parameters of the SPI channel.

### Parameters

- **Snnn** Maximum delay between full SPI transfers (in ms, defaults to 25ms)

- **Fnnn** Maximum delay between full SPI transfers when a file is open (in ms, defaults to 5ms)

- **Pnnn** Number of events required to skip the delay (defaults to 4)

