## M672: Program Z probe

This command is for sending configuration data to programmable Z probes such as the Duet3D delta effector, for example to set the sensitivity. The specified command bytes are sent to the probe. The Duet3D probe stores the configuration data in non-volatile memory, so there is no need to send this command every time the probe is used.

### Parameters

- **Snn:nn:nn...** Sequence of 8-bit unsigned values to send to the currently-selected Z probe

- **Knn** (optional) Z probe number, default 0 (supported in RRF 3.01 and later)

### Examples

M672 S105:50:205

### Notes

For the Duet3d smart effector:

- The programming pin has to be defined in the M558 command

- To program the sensitivity threshold, send command M672 S105:aaa:bbb replacing aaa by the desired threshold and bbb by 255 - aaa. The green LED will flash 4 times if the command is accepted. When you subsequently power up the effector, the green LED will flash three times instead of twice to indicate that a custom sensitivity is being used. Higher values make the sensor less sensitive. The default threshold for the Duet3D Smart Effector is 50.

- To revert to factory sensitivity, send command M672 S131:131. The green LED will flash 5 times if the command is accepted. When you subsequently power up the effector, the green LED will flash twice to indicate that default settings are being used.

See the Smart effector and carriage adapters for delta printer documentation for more details.

