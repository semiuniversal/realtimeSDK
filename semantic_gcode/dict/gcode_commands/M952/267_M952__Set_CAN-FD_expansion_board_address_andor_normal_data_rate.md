## M952: Set CAN-FD expansion board address and/or normal data rate

Some CAN-connected expansion boards are too small to carry address selection switches. Such boards default to a standard address, which can be changed using this command.

### Parameters

- **Bn** Existing CAN address of expansion board to be changed, 1 to 125.

- **An** New CAN address of that expansion board, 1 to 125.

- **Sn.n** Requested bit rate in Kbits/second (1K = 1000) (optional, default 1000)

- **T0.n** Fraction of the bit time between the bit start and the sample point (optional)

- **J0.n** Maximum jump time as a fraction of the bit time (optional)

### Examples

M952 B121 A20 ; change the CAN address of expansion board 121 to 20 M952 B20 S500 ; change the CAN bit rate or expansion board 20 to 500kbps

### Notes

The change of CAN address will not take place until the expansion board is restarted.

This command can also be used to change the normal data rate, for example if the printer has CAN bus cables that are too long to support the standard data rate (1Mbits/sec in RepRapFirmware). All boards in the system on the same CAN bus must use the same CAN data rate. The procedure for changing the data rate is:

- Use M952 to change the data rate on all the expansion boards, one at a time. After changing the data rate on each expansion board, you will no longer be able to communicate with it, and you may need to power it down or disconnect it from the CAN bus to prevent it interfering with subsequent CAN communications.

- Change the data rate of the main board last. Then the main board should be able to communicate with all the expansion boards again.

