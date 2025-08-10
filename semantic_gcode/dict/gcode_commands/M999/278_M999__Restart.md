## M999: Restart

Restarts the firmware using a software reset.

### Parameters

- This command can be used without any additional parameters.

- **Bnnn** Optional CAN address of the board to restart (defaults to 0)

- **Pnnn** Reset flags

### Examples

M999

### Notes

- The **P** parameter can also put the board into firmware upload mode (as if the Erase button had been pressed) if parameter P"ERASE" is present.

- In SBC mode, from DSF v3.3 the **B** parameter may be set to -1 to reboot the attached SBC (DuetPi + SBC). DSF v3.5 also supports P"OFF" to shut down the SBC. Requires the DuetPi Management Plugin to be enabled. See SBC Setup - Useful commands.

