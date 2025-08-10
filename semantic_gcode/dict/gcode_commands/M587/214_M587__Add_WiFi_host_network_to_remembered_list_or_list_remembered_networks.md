## M587: Add WiFi host network to remembered list, or list remembered networks

**This command must not be used in the config.g file.**

### Parameters

- **S"ccc"** Network SSID (case sensitive)

- **P"ccc"** Network password (case sensitive)

- **Inn.nn.nn.nn** (optional) IP address to use when connected to this network. If zero or not specified then an IP address will be acquired via DHCP.

- **Jnn.nn.nn.nn** (optional) Gateway IP address to use when connected to this network.

- **Knn.nn.nn.nn** (optional) Netmask to use when connected to this network

- **Lnn.nn.nn.nn** (optional, supported only by DuetPi + DSF v3.3 or newer) DNS server to use

- **Cnnn** (supported only by DuetPi + DSF v3.3 or newer) Country code for the WiFi adapter, only required if not set before

- **Fn** (optional) Format of the response when M587 is used to report the remembered list: 0=plain text (default), 1=JSON

- **Xn** (optional, RRF 3.5 and later only, standalone mode only) Authentication mode, default 0 (WPA2-PSK)

The SSID and password must always be enclosed in double quotation marks.

RepRapFirmware 3.5 and later with WiFiServer 2.1 and later support WiFi Enterprise Authentication experimentally. The modes supported are:

- EAP-TLS (only on ESP32-C3) - certificates-based authentication; needs a client certificate, private key and an optional private key password

- EAP-TTLS-MSCHAPv2 - username and password authentication

- EAP-PEAP-MSCHAPv2 - username and password authentication

All three protocols have an option to specify an anonymous identity and CA validation certificate.

When using one of these modes there are additional parameters and the meaning of the P parameter may be changed, as follows:

- **Xn** Authentication mode: 0=WPA2-PSK, 1=EAP-TLS (supported on ESP32-S3 WiFi modules only), 1=EAP-PEAP-MSCHAPv2, 3=EAP-TTLS-MSCHAPv2

- **E"eee"** Filename of CA validation certificate in /sys directory of SD card

- **A"aaa"** Anonymous identity

### Protocol-specific parameters:

**EAP-TLS**

- **U"uuu"** Filename of client/user certficate in /sys directory

- **P"ppp"** Filename of private key file in /sys directory

- **Q"qqq"** Private key password

**EAP-TTLS-MSCHAPv2 and EAP-PEAP-MSCHAPv2**

- **U"uuu"** Username

- **P"ppp"** Password

### Examples

M587 S"Network-ssid-123" P"Password123" I192.128.1.200 ; connect to access point "Network-ssid-123" using WPA2-PSK authentication M587 X2 E"ca.pem" S"test-ap" U"bob" P"hello" ; Connect to AP "test-ap" with EAP-PEAP-MSCHAPv2, username "bob" and password "hello". Perform CA validation with certificate sys/ca.pem

### Notes

- In SBC mode (v3.3 and later) it is not possible to configure different IP addresses per SSID.

- In SBC mode, sending this command makes a persistent change. It does not need to be added to dsf-config.g. It should NOT be included in config.g.

- Many programs used to send GCodes convert all characters to uppercase. In firmware 1.19.2 and later, within any quoted string you can use a single-quote character to indicate that the following character should be changed to lowercase. For example, M587 S"ABC" P"P'A'S'SW'O'R'D" would specify that the password is "PassWord". Use two single quote characters to represent one actual single quote character in the password or in the SSID. For example, if your SSID is "Pete's network" then enter "Pete''s network".

- The use of special characters in the SSID cannot be guaranteed to work. In general it's best to avoid most special characters. Spaces, periods, dashes, underscores, and other punctuation is likely ok, but special characters on the number keys likely are not safe. (@#\$%^&\*). If you are having troubles adding your SSID, try a simplified version with only letters and numbers.

- M587 with no parameters lists all the remembered SSIDs, but not the remembered passwords.

- The M587 command will fail if the WiFi module has not yet been taken out of reset. So if the WiFi module has not been started, send M552 S0 to put it in idle mode first.

- When connecting to an open network with no password, M587 still requires a password in the P parameter. However, it doesn't matter what password you provide as long as it meets the minimum length requirement for M587.

**Important!** Do not use M587 within config.g. As well as being a security hazard, writing the access point parameters to WiFi chip every time you start the Duet may eventually wear out the flash memory. Also, the wifi module does not get enabled until the end of running config.g (see \>this forum thread for explanation). It is better to use a macro to send M587.

