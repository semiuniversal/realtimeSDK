## M21: Initialize SD card

• Standalone mode

• SBC mode

The specified SD card is initialized.

##### Parameters

- This command can be used without any additional parameters.

- **Pnnn** SD card number (default 0)

##### M21 M21 P1

Notes

- If an SD card is loaded when the machine is switched on, this will happen by default.

- SD cards must be initialized for the other SD functions to work.

In SBC mode and RRF v3.4 or newer this code may be used to mount block devices or remote endpoints using the mount command.

##### Parameters

- **Pnnn** Device node or remote endpoint

- **Snnn** Local directory to mount to (e.g. 0:/gcodes/remote, optional if the device node is already present in /etc/fstab)

- **Tnnn** Mount type (-t flag, e.g. nfs)

- **Onnn** Mount options (-o flag)

##### Notes

- This requires the DuetPiManagementPlugin to be running.

- In SBC mode, this command should be in dsf-config.g NOT config.g.

