## M670: Set IO port bit mapping

### Parameters

- **Pnn:nn:nn...** - List of up to 16 port numbers that bits 0, 1, 2... control. In RRF2.x and earlier these are logical port numbers. In RRF 3.6.0 and later these are GpOut port numbers that have previously been assiged using M950. RRF 3.x versions before 3.6.0 do not use this parameter.

- **Cnnn** - Up to 16 pin name(s) to be controlled. Used only in RRF3.x versions before 3.6.0. See Pin Names)

- **Tnnn** - Port switching time advance in milliseconds

### Examples

M670 T5 P220:221:222 ; RRF 2.x M670 T5 C"sx1509b.0+sx1509b.1+sx1509b.2" ; RRF 3.x prior to 3.6.0 M670 T5 P2:3:8 ; RRF 3.6.0 or later

### Notes

- RepRapFirmware 1.19 and later provides an optional P parameter on the G1 command to allow I/O ports to be set to specified states for the duration of the move. The argument to the P parameter is a bitmap giving the required state of each port. The M670 command specifies the mapping between the bits of that argument and logical port numbers. Optionally, the T parameter can be used to advance the I/O port switching a short time before the corresponding move begins.

- In RRF3 pror to version 3.6.0 the P parameter is removed. Use the C parameter to specify the pin names to be used.

- In all versions of RRF3 the ports or pins specified must be on the main board, not on a CAN-connected expansion board. On Duet 2 some or all of the ports may be on a DueX or additional SX1509B chip.

