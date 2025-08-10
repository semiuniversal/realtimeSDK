## M550: Set Name

### Parameters

- **P"nnn"** Machine name

### Examples

M550 P"Godzilla"

### Description

Sets the name of the printer to (in the case of the above example) Godzilla. The name can be any string of printable characters except ';', which still means start comment. The name shows at the top of the DWC page.

The machine name is also used to allow local network discovery using **mDNS local network discovery**. Rather than remembering the ip address of the printer to connect to, or having to find it if assigned by DHCP (mDNS works both with fixed ip address and DHCP), you can use it's name. Using the example name above, in your browser connect to the DWC with http://Godzilla.local.

### Notes

- Quotation marks around the machine name are mandatory in RRF3, but discretionary in earlier firmware versions.

- In SBC mode, this command should be in dsf-config.g, NOT config.g.

- Using the machine name to access the machine on the network relies on mDNS. This needs to be supported on the device trying to connect. See a longer description about mDNS support here.

- The machine name is also used as the NetBIOS name, which can help to identify the Duet on a network. This is only supported on Duet 2 WiFi and legacy Duet 0.6/0.85.

- Both the mDNS and NetBIOS name are limited to 15 characters. If you use a longer name, the mDNS name will be the first 15 characters, eg if the Duet name is "3DPrinterWithVeryLongName", you should still be able to connect to "3DPrinterWithVe.local".

