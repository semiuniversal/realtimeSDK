## M671: Define positions of Z pivot points or bed levelling screws

Informs the firmware of the positions of the pivot points, where the bed or gantry connect to the Z axis.

### Parameters

- **Xnn:nn:nn...** List of between 2 and 4 X coordinates of the pivot points

- **Ynn:nn:nn...** List of between 2 and 4 Y coordinates of the pivot points

- **Snn** Maximum correction allowed for each pivot point in mm (optional, default 1.0)

- **Pnnn** Pitch of the bed levelling screws (not used when bed levelling using multiple independently-driven Z motors). Defaults to 0.5mm which is correct for M3 bed levelling screws.

- **Fnn** Fudge factor, default 1.0

### Order dependency

M671 must come later in config.g than any command that changes the kinematics, e.g. M669.

### Examples

M671 X-15.0:100.0:215.0 Y220.0:-20.0:220.0 ; Z pivot points are at (-15,220), (100,-20) and (215,220)

### Notes

- M671 is used to define the **pivot points** of the bed or gantry where it connects to the Z axis. These pivot points are often at each leadscrew, but may also be offset from the leadscrews, if the bed/gantry rests on a carriage extending out from the leadscrew, for example on a kinematic mount.

- When this command is used to define the pivot point positions, the numbers of X and Y coordinates must both be equal to the number of drivers used for the Z axis (see the G32 command.

- The X and Y coordinates in M671 are measured from the origin X0,Y0 set by M208.

- The order of the X and Y coordinates is important; they relate to the order the motor drivers are defined in the M584 command. The first defined motor in M584 should be the first defined coordinates for X and Y in M671, and so on. For example, if you have M584 Z3:4:5 and M671 X\[a\]:\[b\]:\[c\] Y\[a\]:\[b\]:\[c\], the positions of X and Y for the motor on Z3 are defined by X\[a\],Y\[a\], Z4 by X\[b\],Y\[b\], and Z5 by X\[c\],Y\[c\].

- The firmware algorithm assumes perfect gimbal joints at the pivot point, so that the bed is completely free to adopt the plane (or the twisted plane if there are 4 points) defined by the pivot points. In real printers this is rarely the case and the corrections are insufficient to level the bed, so multiple G32 commands need to be sent if the bed is a long way off level. The F parameter allows for the corrections calculated by the firmware to be multiplied by a factor so as to achieve faster convergence in this situation.

- For machines without multiple independently-driven Z axes, this command can also be used to define the positions of the bed levelling screws instead. Then bed probing can be used to calculate and display the adjustment required to each screw to level the bed. The thread pitch (P parameter) is used to translate the height adjustment needed to the number of turns of the levelling screws. See Manual Bed Levelling Assistant.

- For printers that print directly onto a desktop and have levelling feet, this command can be used to define the coordinates of the levelling feet, so that bed probing can be used to calculate and display the adjustments needed to the feet. In this case the displayed corrections must be reversed. For example, "0.2 turn down" means the bed needs to be lowered or the printer raised by 0.2 turn lower at that screw position. See Manual Bed Levelling Assistant.

