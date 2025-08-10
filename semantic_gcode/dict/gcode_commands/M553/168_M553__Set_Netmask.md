## M553: Set Netmask

### Parameters

- **Innn** (Optional) Number of the network interface to manage (defaults to 0)

- **Pnnn** Net mask

### Examples

M553 P255.255.255.0

Sets the network mask of the RepRap machine to (in this case) 255.255.255.0.

### Notes

- In SBC mode, sending this command makes a persistent change. It does not need to be added to dsf-config.g. It should NOT be included in config.g.

- A restart may be required before the new network mask is used.

- If no 'P' field is specified, this echoes the existing network mask configured.

- DuetWifiFirmware versions 1.18 and earlier do not support setting the network mask manually.

