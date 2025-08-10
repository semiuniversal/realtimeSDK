## M953: Set CAN-FD bus fast data rate

Provisional specification - not yet implemented

This command allows the bandwidth of the CAN bus to be optimised, by increasing the data rate during transmission of CAN-FD data packets by means of the BRS (bit rate switch) feature. The maximum speed supported by CAN-FD is 8Mbits/sec but the practical limit depends on the cable length, cable quality, number of devices on the bus and CAN interface hardware used. The rate specified will be rounded down to the nearest achievable rate.

### Parameters

- **Sn.n** Requested bit rate in Mbits/second. Ignored if it is lower than the bit rate for the negotiation phase.

- **T0.n** Fraction of the bit time between the bit start and the sample point (optional)

- **J0.n** Maximum jump time as a fraction of the bit time (optional)

- **Caa:bb** Transceiver delay compensation offset and minimum, in nanoseconds (optional)

### Examples

M953 S4.0 T0.6 J0.2

### Notes

The optional **C** parameter allows fine-tuning of the transmitter delay compensation. The first parameter is the offset added to the measured transmitter delay. The optional second value, which must be greater than the first, is the minimum delay compensation applied.

Glitches seen by the receiver while the transceiver delay is being measured will be ignored if they would result in a transceiver delay compensation lower than this value.

When CAN is implemented on Microchip SAME5x and SAMC21 processors, these values are converted from nanoseconds into time quanta and stored in the TDCO and TDCF fields of the transceiver delay compensation register.

