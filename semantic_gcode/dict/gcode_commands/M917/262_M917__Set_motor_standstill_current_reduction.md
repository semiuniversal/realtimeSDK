## M917: Set motor standstill current reduction

Supported in firmware 3.01 and later for Duet 3.

Motor drivers on Duet 3 allow higher motor currents to be used while the motor is moving. This command sets the percentage of the current set by M906 that is to be used when the motor is stationary but not idle, or moving very slowly.

### Parameters

- **X,Y,Z,E** Percentage of normal current to use when the motor is standing still or moving slowly, default 71

### Order dependency

If this command refers to any axes other than X, Y and Z then it must appear later in config.g than the M584 command that creates those additional axes.

### Examples

M917 X70 Y70 Z80 E70:70

### Notes

Standstill current reduction is not the same as idle current reduction. The standstill current must be high enough to produce accurate motion at low speeds. The idle current needs only to be high enough to hold the motor position well enough so that when the current is restored to normal, the position is the same as it was before the current was reduced to idle.

When M906 is used to set the motor current to 71% or more of the maximum permitted current, RRF will limit the maximum standstill current percentage so that the standstill current is no more than 71% of the maximum permitted motor current. This is to ensure that a single phase of the driver does not pass more than 71% of the maximum current continuously, which would risk overheating the output mosfets of that phase.

Note this is not supported on Duet 2 with TMC2660 or on external drivers.

