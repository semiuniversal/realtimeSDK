## M997: Perform in-application firmware update

This command triggers a firmware update if the necessary files are present on the SD card.

### Parameters

- **Snnn** Firmware module number(s), default 0

- **Bnnn** CAN address of the board to be updated (RRF 3.0 and later, Duet 3 only)

- **P"filename"** Filename of firmware binary to use (RRF 3.3 and later)

- **F\[feed\]** Set package feed for DSF packages (RRF 3.5 and later, SBC only)

- **V\[version\]** Install a specific DSF/RRF combination (RRF 3.5 and later, SBC only)

### Examples

M997 ; update firmware on mainboard (S0 is the default) M997 B121 ; update firmware on CAN-connected expansion/tool board at CAN address 121 M997 S1 ; update firmware on WiFi module (standalone only) M997 S1 P"0:/sys/DuetWiFiServer.bin" ; update firmware on WiFi module with specific file (standalone only) M997 S0:1 ; update firmware modules 0 and 1 (mainboard and WiFi module, standalone only) M997 S2 ; update DSF (SBC mode only) M997 S2 F"unstable" ; Set package feed for DSF packages (SBC mode only) M997 S2 F"stable-3.5" ; Set package feed and version for DSF packages (SBC mode only) M997 S2 V"3.5.0-rc.2" ; Install a specific DSF/RRF combination (SBC mode only) M997 S3 B121 ; update bootloader on CAN-connected expansion/tool board at CAN address 121 M997 S4 ; update firmware on connected PanelDue

### Notes

- **S** parameter: in RepRapFirmware on the Duet series, the S parameter selects the firmware module numbers are as follows:

  - **0** - main firmware, specific for Duet board. Needs the appropriate IAP (In-App Programmer, specific to the Duet board) binary present on the SD card to be able to install the firmware. See Installing and Updating Firmware for full details.

  - **1** - WiFi module firmware, filename DuetWiFiServer.bin or DuetWiFiModule-32S3.bin depending on the board (WiFi-equipped Duets only)

  - **2** - update DSF packages in SBC mode (RRF 3.5 or later)

  - **3** - update the bootloader on the CAN-connected Duet 3 expansion board specified by the B parameter (see Updating the bootloader on Duet 3 expansion and tool boards)

  - **4** - update PanelDue firmware (RRF 3.2 and later; see PanelDue firmware update instructions).

- **B** parameter: On Duet 3 only this command take an optional B (board number) parameter which is the CAN address of the board to be updated, default 0 (i.e. main board).

- **P** parameter: The optional P parameter can be used to provide the filename of the file to be used for updating a module. This can either only be a filename in which case it will prepend directories.firmware to it (0:/firmware) or can be an absolute path to the file to be used. It is not allowed to use P parameter and multiple modules, e.g. S1:4. (RRF 3.3 and later).

- **F** and **V** parameters: In SBC mode from RRF 3.5 and later, M997 S2 can be used to install the latest DSF and security-related packages on DuetPi (via apt update/unattended-upgrade). It also supports two optional arguments:

  - F"\[feed\]" - Set package feed for DSF packages where \<feed\> can be stable (default), unstable, stable-x.y, or unstable-x.y where x.y corresponds to a version. e.g. 3.4 or 3.5.

  - V"\[version\]" - Install a specific DSF/RRF combination (must not be used together with M997 F). Example: M997 S2 V"3.5.0-rc.2"

- With all firmware versions up to RRF v3.2.2, all firmware update files are stored in the '0:/sys/' directory. From RRF v3.3, to avoid too many files in this folder, all firmware update files are stored in '0:/firmware/' directory.

- When using firmware v1.18 or older, M997 S2 updates the web server file system (DuetWebControl.bin).

- In older Duet 2 firmware versions, M997 S3 was used to put the WiFi module into bootloader mode, so that firmware can be uploaded directly via its serial port.

### See also

- Installing and Updating Firmware

- PanelDue firmware update instructions

- Updating the bootloader on Duet 3 expansion and tool boards

