## M954: Configure as CAN expansion board

Supported in RRF 3.4 and later on Duet 3 boards

This command is used to reconfigure the board it is executed on as a CAN-connected expansion board. It would typically be the only command in the config.g file. When it is executed, the board changes its CAN address to the one specified in the A parameter, stops sending CAN time sync messages, and responds to requests received via CAN just like a regular expansion board.

### Parameters

- **Ann** CAN address to use (required)

### Notes

After this command is executed, for diagnostic purposes a few GCode commands can still be sent to the USB port for local execution, for example M122.

