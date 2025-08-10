## M589: Configure access point parameters

**This command must not be used in the config,g file**

### Parameters

- **S"ccc"** The SSID that the WiFi interface should use when it is commanded to run as an access point

- **P"ccc"** The WiFi password (must be at least 8 characters long)

- **Inn.nn.nn.nn** The IP address to use

- **Cnn** The WiFi channel to use (optional)

### Examples

M589 S"DuetSSID" P"password" I192.168.0.1 C1

### Usage

**To use AP mode:**

- Send a M589 command once from the console, or via macro to set the access point name, IP address etc. These parameters will be saved within the WiFi module.

- The password must be at least 8 characters long. See notes of M587 for valid characters.

- The M589 command will fail if the WiFi module has not yet been taken out of reset. So if the WiFi module has not been started, send M552 S0 to put it in idle mode first.

- M589 does not work from within config.g at startup.

- Use M552 S2 in config.g to start the wifi module.

- WPA2 security will be used by default.

- Look for the wireless network name you specified on your device and connect to it using the password you set.

### Notes

- In SBC mode, sending this command makes a persistent change. It does not need to be added to dsf-config.g. It should NOT be included in config.g.

