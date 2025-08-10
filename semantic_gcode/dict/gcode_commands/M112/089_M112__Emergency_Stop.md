## M112: Emergency Stop

### Examples

M112

Any moves in progress are immediately terminated, then Duet shuts down. All motors and heaters are turned off. PSU power (if controlled by the Duet via the PS_ON pin) is NOT turned off, to allow any always-on fans to continue to run. The Duet can be started again by pressing the reset button or power cycling the board. See also User manual: Connecting an emergency stop.

