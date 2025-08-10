## M586: Configure network protocols

### Parameters

- **Inn** Interface number (RRF 3 and later, defaults to 0, only supported in standalone mode)

- **Pnn** Protocol: 0 = HTTP or HTTPS, 1 = FTP or SFTP, 2 = Telnet or SSH (which of the two choices depends on the T parameter), 3 = multicast discovery (OEM-specific), 4 = MQTT (see M586.4 below)

- **Snn** 0 = disable this protocol, 1 = enable this protocol

- **Hnn** Remote server IP address (only applicable for MQTT, see also M586.4)

- **Rnn** TCP port number to use for the specified protocol. Ignored unless S = 1. If this parameter is not provided then the default port for that protocol and TLS setting is used. When S=0 the default port numbers are 80, 21 and 23 respectively.

- **Tnn** 0 = don't use TLS, 1 = use TLS. Ignored unless S = 1. If this parameter is not provided, then TLS will be used if the firmware supports it and a security certificate has been configured. If T1 is given but the firmware does not support TLS or no certificate is available, then the protocol will not be enabled and an error message will be returned.

- **C"\<site\>"** (RRF 3.2 and later only) Set or reset allowed site for Cross-Origin Resource Sharing (CORS) HTTP requests

**Note**: TLS has not yet been implemented in RepRapFirmware, therefore T1 will not work.

### Examples

; standalone mode M586 P0 S1 ; enable HTTP M586 P1 S0 ; disable FTP M586 P2 S1 ; enable Telnet ; SBC mode ; NOTE: In SBC mode sending these makes a persistant change, do not add to config.g M586 P0 T1 S1 ; enable HTTPS M586 P1 T1 S1 ; disable SFTP M586 P2 T1 S1 ; enable SSH

### Notes

- Standalone mode does not support any secure protocols (M586 ... T1), ie HTTP, FTP and Telnet only. SBC mode can support HTTPS, SFTP and SSH.

- In SBC mode, sending this command makes a persistent change. It does not need to be added to dsf-config.g. It should NOT be included in config.g.

- In SBC mode, M586 I is not supported. Configure ufw or another firewall to restrict protocol access per adapter if required.

- M586 with no S parameter reports the current support for the available protocols.

- RepRapFirmware 1.18 and later enable only HTTP (or HTTPS if supported) protocol by default. If you wish to enable FTP and/or Telnet, enable them using this command once or twice in config.g.

- To connect via FTP, use an FTP client such as FileZilla. In FileZilla, create a 'New site', give it a name, then set the 'Host' to the Duet's IP address or .local hostname. Set 'Logon Type' to 'Anonymous', and in 'Transfer Settings' check 'Limit number of simultaneous connections' and set 'Maximum number of connections' to 1. Then connect.

