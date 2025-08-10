## M22: Release SD card

• Standalone mode

• SBC mode

The specified SD card is released, so further (accidental) attempts to read from it are guaranteed to fail.

##### Parameters

- This command can be used without any additional parameters.

- **Pnnn** SD card number (default 0)

##### M22 M22 P1

Notes

- This command is helpful, but not mandatory before removing the card physically.

In SBC mode and v3.4 or newer this code may be used to unmount block devices or remote endpoints using the mount command.

##### Parameters

- **Pnnn** Device node or remote endpoint

##### Notes

- This requires the DuetPiManagementPlugin to be running.

- In SBC mode, this command should be in dsf-config.g NOT config.g.

