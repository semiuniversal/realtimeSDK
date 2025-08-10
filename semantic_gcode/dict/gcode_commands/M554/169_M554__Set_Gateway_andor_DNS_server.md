## M554: Set Gateway and/or DNS server

### Parameters

- **Innn** (Optional) Number of the network interface to manage (defaults to 0)

- **Pnnn** Gateway

- **Snnn** (Optional) DNS server (only supported by DSF 3.3 with DuetPi system config plugin)

### Examples

M554 P192.168.1.1

Sets the Gateway IP address of the RepRap machine to (in this case) 192.168.1.1.

### Notes

- In SBC mode, sending this command makes a persistent change. It does not need to be added to dsf-config.g. It should NOT be included in config.g. Also make sure to set a static IP address before trying to set a static gateway or DNS server.

- A restart may be required before the new gateway IP address is used.

- If no 'P' field is specified, this echoes the existing Gateway IP address configured.

- DuetWifiFirmware versions 1.18 and earlier do not support setting the gateway address.

