## M540: Set MAC address

### Parameters

- **Pnnn** The MAC address

### Examples

M540 PDE:AD:BE:EF:CA:FE

### Description

Sets the \>MAC address of the printer. This should be done before any other network commands. The MAC address is six one-byte hexadecimal numbers separated by colons. Only works on Ethernet-equipped Duet mainboards, in standalone mode (i.e. not Duets with WiFi or Duet boards with SBC).

### Notes

- On WiFi-equipped Duet boards (Duet 3 Mini 5+ WiFi and Duet 2 WiFi) the MAC address is unique and set on the WiFi Module so this command has no effect.

- The default MAC address on a Ethernet-equipped Duet boards is generated from the unique processor ID so there is normally no need to change it.

- All devices running on the same network should have different MAC addresses. For your printers, changing the last digit is sufficient.

- In SBC mode, this command should be in dsf-config.g, NOT config.g.

