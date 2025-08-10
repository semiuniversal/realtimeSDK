## M915: Configure motor stall detection

This sets the stall detection parameters and optionally the low-load current reduction parameters for TMC2660, TMC2130 or similar driver chips. Use either the P parameter to specify which driver number(s) you want to configure, or the axis names of the axes that those motors drive (the parameters will then be applied to all the drivers associated with any of those axes).

• RRF 3.4 and later

• RRF 3.3 and earlier

##### Parameters

- **Pnnn:nnn:...** Drive number(s) to configure

- **X,Y,Z,U,V,W,A,B,C** Axes to configure (alternative to using the P parameter)

- **Snnn** Stall detection threshold (see notes below)

- **Fn** Stall detection filter mode, 1 = filtered (one reading per 4 full steps), 0 = unfiltered (default, 1 reading per full step)

- **Hnnn** (optional) Minimum motor full steps per second for stall detection to be considered reliable, default 200

- **Tnnn** (optional) Coolstep control register, 16-bit unsigned integer

- **Rn** Action to take on detecting a stall from any of these drivers: 0 = no action (default), 1 = just log it, 2 or 3 = create an event (see notes).

##### Notes

- In RRF 3.6.0, a homing move that uses stall detect endstops will be cancelled and an error message generated if the movement speed is too low for stall detection to be definitely feasible (also if it is too high when using TMC2209 or TMC2240 drivers). There are small speed ranges that will be rejected by this release but may in practice have worked on some boards using previous firmware versions, so please test stall homing after upgrading.

- In RRF 3.4.0 thru 3.4.5, motor stalls don't generate events when not printing from SD card. RRF 3.4.6 and later do generate events when not printing from SD card.

- In RRF v3.4 and later, R2 and R3 both cause an event to be created when the driver stalls.

- To handle the event, RRF calls driver-stall.g passing the stalled local driver number in param.D and the CAN address of the board concerned in param.B.

- If file driver-stall.g is not found then the default action is to report it to the console and carry on.

- File rehome.g is no longer used.

- See the events page for more detail.

##### Parameters

- **Pnnn:nnn:...** Drive number(s) to configure

- **X,Y,Z,U,V,W,A,B,C** Axes to configure (alternative to using the P parameter)

- **Snnn** Stall detection threshold (see notes below)

- **Fn** Stall detection filter mode, 1 = filtered (one reading per 4 full steps), 0 = unfiltered (default, 1 reading per full step)

- **Hnnn** (optional) Minimum motor full steps per second for stall detection to be considered reliable, default 200

- **Tnnn** (optional) Coolstep control register, 16-bit unsigned integer

- **Rn** Action to take on detecting a stall from any of these drivers: 0 = no action (default), 1 = just log it, 2 = pause print, 3 = pause print, execute /sys/rehome.g, and resume print.

### Order dependency

If this command refers to any axes other than X, Y and Z then it must appear later in config.g than the M584 command that creates those additional axes.

### Examples

M915 P0:2:3 S10 F1 R0 M915 X Y S5 R2

### Notes

- **S parameter** For most drivers, values range from -64 to +63. For TMC2209 drivers (Duet 3 Mini 5+, Duet 3 Toolboard 1LC) values range from -128 to +127. Lower values make stall detection more sensitive. Values below -10 are not recommended. S3 is a good starting point for many motors.

- **T parameter**

  - For all versions of RRF before 3.5.0, on TMC2160/5160/2240, the T parameter is not processed correctly, and might affect whether stalls are recognised instead of setting the coolstep parameters. This is fixed in RRF 3.5.0 and later.

  - Setting incorrect coolstep parameters could result in motor current being reduced too much, which could result in layer shifts. Users should only use the T parameter if they have read the driver datasheet and know what they are doing.

- If any of the S, F, T and R parameters are absent, the previous values for those parameters associated with the specified drivers will continue to be used.

- If all the parameters are absent, the existing settings for the specified drive(s) will be reported.

- See the Trinamic TMC2660 and TMC2130 datasheets for more information about the operation and limitations of motor stall detection.

- See here for more detailed information on Stall Detection and Sensorless Homing.

- In RRF 3.6.0 and later, when stall detect endstops are configured, G1 H1/H3/H4 moves are vetted to ensure that stall detection has been configured and suitable parameters and movement speed have been selected to make stall detection possible; otherwise the move is abandoned and an error message generated.

