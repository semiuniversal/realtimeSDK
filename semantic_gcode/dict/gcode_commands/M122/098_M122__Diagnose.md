## M122: Diagnose

### Parameters

- This command can be used without any additional parameters.

- **Pnnn** report specific information (See Notes)

- **Bnnn** Board number (RRF3/Duet 3 only, see Notes)

- **"DSF"** Immediate DSF diagnostics (RRF3/Duet3 only with attached SBC)

### Examples

M122

Sending an M122 causes the RepRap to transmit diagnostic information.

### Notes

The 'P' parameter is used to report specific information. The details vary between releases. As at RepRapFirmware version 3.41 they are:

- P1 print summary test report. Parameters:

  - required parameters: **Taa:bb** = min/max accepted MCU temperature reading, **Vaa:bb** = min/max VIN voltage reading

  - optional parameter: **Waa:bb** = min/max 12V regulator voltage reading if applicable (required if the board monitors the 12V rail)

  - optional parameter: **Faa:bb** = min/max inductive sensor frequency in kHz (required if the board has an inductive sensor chip)

  - NOTE: M122 P1 subfunction is provided for factory testing purposes only, so the details are liable to be changed without notice

- P100 print a summary of recent moves (only if move logging is enabled in the firmware build)

- P101 print the status of an attached DueX expansion board (Duet 2 only)

- P102 print how long it takes to evaluate square roots (the type of square root depends on firmware version)

- P103 print how long it takes to evaluate sine and cosine (not supported on expansion boards)

- P104 print how long it takes to write a file to the SD card (specify the file size in Mbytes in the S parameter, default 10)

- P105 print the sizes of various objects used by RepRapFirmware

- P106 print the addresses of various objects used by RepRapFirmware

- P107 time a CRC-32 operation

- P108 time how long it takes to read the step clock

- P109 generate an under-voltage event to test the pause-on-low-power function

The following 'P' parameters are supported by the **LPC and STM32 Port of RepRapFirmware Only**

- P200 - Lists all of the pins allocated by the firmware and/or board.txt

The following P parameter is supported on boards that use Arm Cortex M4 processors:

- P500 Sn - n=0 disables the processor write buffer; n=1 enables it which is the default at power up. If the S parameter is missing then the current enable/disable state is reported. Disabling the write buffer reduces performance, but can help when debugging if the processor resets and the M122 reset data indicates that the cause was an imprecise exception. Disabling the write buffer will usually make the exception precise in future.

Note: do not use M122 with a P parameter of 1000 or greater. Most of these values are used to test the error reporting facilities and deliberately cause the firmware to crash . As at firmware 3.45 these are:

- P1001 cause a watchdog reset

- P1002 test what happens when a module gets stuck in a spin loop

- P1003 test what happens when we write a blocking message to USB

- P1004 test integer division by zero

- P1005 test the response to an unaligned memory access

- P1006 test the response to accessing an invalid region of memory

- P1007 read/write 32-bit words: A = address, R = number of 32-bit words (optional, default 1), V = value to write (optional)

The 'B' parameter is used in RepRapFirmware 3 on Duet 3 only, to report diagnostic information from connected boards. The B (board number) parameter is the CAN address of the board to be queried, default 0 (i.e. main board). Example:

M122 B1 Diagnostics for board 1: Board EXP3HC firmware 3.0beta1 2019-10-28b1 Never used RAM 163.4Kb, max stack 376b HEAT 1284 CanAsync 1456 CanRecv 1424 TMC 168 AIN 532 MAIN 2220 Driver 0: standstill, reads 26609, writes 11 timeouts 0, SG min/max 0/0 Driver 1: standstill, reads 26611, writes 11 timeouts 0, SG min/max 0/0 Driver 2: standstill, reads 26614, writes 11 timeouts 0, SG min/max 0/0 Move hiccups: 0 VIN: 24.4V, V12: 12.2V MCU temperature: min 43.8C, current 43.9C, max 44.1C

