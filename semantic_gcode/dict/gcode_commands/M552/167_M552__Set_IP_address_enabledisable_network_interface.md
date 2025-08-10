## M552: Set IP address, enable/disable network interface

• WiFi interfaces (Duet 2/3 WiFi)

• Ethernet interfaces (Duet 2/3 Ethernet and 06/085)

##### Parameters

- **Innn** (Optional) Number of the network interface to manage (defaults to 0). Only needed if the board supports more than one network interface, such as Duet 3 MB6HC revision 1.02 or later with the optional WiFi interface. On that board, I0 is the Ethernet interface and I1 is the WiFi interface.

- **P"ssid"** (optional, RepRapFirmware 1.20 and later) SSID of network to connect to. The SSID and password must already have been registered using M587. If this parameter is not present, the WiFi will try to connect to the strongest network that is broadcasting its SSID and whose SSID has been registered using M587.

- **Snnn** 0 = disable networking, 1 = enable networking as a client, 2 = enable networking as an access point , -1 = disable WiFi module

Enables networking as a client, and joins the network with the SSID 'MyNetwork', using the parameters (password, IP/gateway address, netmask) configured in M587.

##### Notes

- Also works with the WiFi interface on an attached SBC. See M587 for configuration limitation.

- On Duet boards with WiFi interfaces running firmware 1.19 and later, the IP address is set in the M587 command when you configure the access point details.

- In SBC mode, sending this command makes a persistent change. It does not need to be added to dsf-config.g. It should NOT be included in config.g.

##### Parameters

- **Innn** (Optional) Number of the network interface to manage (defaults to 0).

- **Pnnn** IP address, 0.0.0.0 means acquire an IP address using DHCP

- **Snnn** 0 = disable networking, 1 = enable networking

- **Rnnn** (Optional) HTTP port, default 80 (Deprecated, RepRapFirmware 1.17 and earlier only)

##### Examples

**Duet 2 Ethernet:**

M552 S1 P192.168.1.14

Sets the IP address of the machine to (in this case) 192.168.1.14. If the S parameter is not present then the enable/disable state of the network interface is not changed.

**Duet 3 in SBC mode:**

- M552 I1 S1 P0.0.0.0 ; set the second interface on the SBC to use DHCP and enable it.

The I1 setting here specifies the second network interface on the SBC. This uses the \>DuetPi Management Plugin (installed by default from RRF 3.3 onwards) to set the address on the SBC. To determine which interface is which on the SBC the object model explorer can be used to see the current settings of each interface.

##### Notes

- M552 with no parameters reports the current network state and IP address.

- In firmware 1.18 and later the HTTP port address is set using the M586 command, so the R parameter of this command is no longer supported.

- In SBC mode, sending this command makes a persistent change. It does not need to be added to dsf-config.g. It should NOT be included in config.g.

