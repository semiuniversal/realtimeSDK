## M956: Collect accelerometer data and write to file

Supported in RRF 3.4 and later (limited support in 3.3)

This command causes the specified number of accelerometer samples to be collected and saved to a .csv file.

### Parameters (provisional)

- **Pnn** or **Pbb.nn** Accelerometer to use (required)

- **Snnn** Number of samples to collect (required)

- **X** and/or **Y** and/or **Z** (optional) Machine axes to collect data for. If no axes are specified, or if the accelerometer type is LIS2DW (supported in RRF 3.5.0 and later) then data is collected for all three axes.

- **An** (required) 0 = activate immediately, 1 = activate just before the start of the next move, 2 = activate just before the start of the deceleration segment of the next move

- **F"filename.csv"** Name of the file to save the data in (optional, supported by RRF 3.4 and later). The default folder is 0:/sys/accelerometer . If not specified then the filename will be composed from the current date/time.

### Notes

- The **P** parameter selects which accelerometer to use and is mandatory.

- To use an accelerometer on a CAN-connected expansion board, use the form **P**board-address.device-number for example **P22.0**.

