## M115: Get Firmware Version and Capabilities

### Parameters

- This command can be used without any additional parameters.

- **Bnnn** Board number (RRF v3.x and later, Duet 3 only)

- **Pnnn** Electronics type (support for P parameter removed from RRF 3.5 and later)

### Examples

M115 FIRMWARE_NAME: RepRapFirmware for Duet 2 WiFi/Ethernet FIRMWARE_VERSION: 2.04RC1 ELECTRONICS: Duet WiFi 1.0 or 1.01 FIRMWARE_DATE: 2019-07-14b1 M115 B1 Board EXP3HC firmware 3.0beta1 2019-10-28b1

### Description

Request the Firmware Version and Capabilities of the current microcontroller. See the M408 command for a more comprehensive report on machine capabilities.

### Notes

The **B** parameter is used on Duet 3 only, in RRF v3.x and later. M115 can take an optional B (board number) parameter which is the CAN address of the board to be queried, default 0 (i.e. main board).

The **P** parameter is no longer supported, and has been removed from RRF 3.5 and later, to save memory on Duet 2. It is used tell the firmware about the hardware on which it is running, if RRF can't identify it. Should only be used in config.g, if you're having problems. If the P parameter is present then the integer argument specifies the hardware being used.

- In RRF v2.x to v3.4.x, only Duet 2 hardware could be specified. This was mainly used for internal testing.

- In RRF v1.x, the following are supported on first-generation Duets:

  - M115 P0 - Automatic board type selection if supported, or default if not

  - M115 P1 - Duet 0.6

  - M115 P2 - Duet 0.7

  - M115 P3 - Duet 0.85

