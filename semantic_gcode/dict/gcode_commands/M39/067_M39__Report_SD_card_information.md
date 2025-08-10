## M39: Report SD card information

Supported in ReprapFirmware 1.21 and later.

This command returns information about the SD card in the specified slot in the requested format.

### Parameters

- **Pn** SD slot number, default 0

- **Sn** Response format. S0 returns a plain text response, S2 returns a response in JSON format.

### Examples

M39 ; report information for SD card 0 in plain text format M39 P1 S2 ; report information for SD card 1 in JSON format ; example output from RRF 3.3 M39 SD card in slot 0: capacity 3.97Gb, free space 3.81Gb, speed 20.00MBytes/sec, cluster size 32kb M39 S2 {"SDinfo":{"slot":0,"present":1,"capacity":3965190144,"free":3807379456,"speed":20000000,"clsize":32768}}

### Notes

In the JSON response, capacity, free space and cluster size are in bytes. and interface speed is in bytes/second.

