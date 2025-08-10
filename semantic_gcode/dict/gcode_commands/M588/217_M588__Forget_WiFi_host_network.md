## M588: Forget WiFi host network

**This command must not be used in the config.g file**

### Parameters

- **S"ccc"** Network SSID to remove from the remembered list

### Examples

M588 S"Network-ssid-123" M588 S"\*"

### Notes

- The specified SSID will be removed from the remembered list and the associated password cleared out of EEPROM. If the SSID is given as "\*" then all remembered networks will be forgotten.

- Removing the SSID of the access point that the Duet is connected to will not disconnect it from the access point (but future attempts to connect to it will fail unless it is added back).

- The M588 command will fail if the WiFi module has not yet been taken out of reset. So if the WiFi module has not been started, send M552 S0 to put it in idle mode first. M588 does not work from within config.g at startup.

- In SBC mode, sending this command makes a persistent change. It does not need to be added to dsf-config.g. It should NOT be included in config.g.

