## M575: Set serial comms parameters

This sets the communications parameters of the serial comms channel specified by the P parameter.

### Parameters

- **Pnnn** Serial channel number

- **Bnnn** Baud rate, default 57600 (same as the default PanelDue baud rate)

- **C"port_name"** Port name for Transmit/Receive control of the RS485 transceiver when the mode is Device and you are using it for Modbus RTU (S7). Not required when running on Duet hardware with a built-in RS485 transceiver. Not required if the transceiver module does automatic transmit/receive switching (note that such transceivers may not work with some Modbus devices).

- **Snnn** Mode: 0 = PanelDue; 1 (default) = PanelDue mode, checksum or CRC required; 2 = raw mode; 3 = raw mode with checksum or CRC required; 4 = PanelDue mode, CRC required; 5 = disabled; 6 = raw mode, CRC required; 7 = Device, eg Modbus or UART (if supported).

### Examples

M575 P1 B57600 S1

### Description

P0 specifies the main serial interface (typically a USB port), while P1 specifies an auxiliary serial port (for example, the port used to connect a PanelDue) and P2 specifies a second auxiliary port if there is one. The B parameter is the required baud rate (this parameter is ignored if the port is a true USB port).

Modes 2 and 3 are supported in RRF 3.01 and later. Modes 4 and 6 are supported in RRF 3.4 and later. Mode 5 is supported in RRF 3.6 and later. Mode 7 is supported by RRF 3.6 and later on some boards.

### Notes

- In RRF 3.1 and later for Duet 3, the auxiliary serial port remains disabled until a M575 P1 command is received. This is to allow the IO_0 port to be used for other purposes. In RRF 3.2 and later on all boards, the auxilliary serial port(s) remain disabled until enabled using M575.

- In RRF 3.6.0 and later, the USB port can now be switched into PanelDue mode using M575.

