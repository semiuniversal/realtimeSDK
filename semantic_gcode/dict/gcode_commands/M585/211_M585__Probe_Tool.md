## M585: Probe Tool

Supported in RRF 1.20 and later.

In machines with at least one tool probe this code allows to update the current tool's offset by driving it into a given endstop. This code works similarly to G1 .. H1 (machine homing; G1 .. S1 is RRF 2.02 and earlier) except that it sets the offset of the current tool instead of the machine position, and that a custom endstop number (RRF 2.x) or custom Z probe (RRF 3.x) can be used.

• RepRapFirmware 3.x

• RepRapFirmware 2.x and earlier

##### Parameters

- **Xnnn** - Probe tool in X direction where nnn specifies the expected distance between the trigger point of your endstop switch and the starting point

- **Ynnn** - Probe tool in Y direction where nnn specifies the expected distance between the trigger point of your endstop switch and the starting point

- **Znnn** - Probe tool in Z direction where nnn specifies the expected distance between the trigger point of your endstop switch and the starting point

- **U,V,W,A,B,Cnnn** - As for X,Y,Z above

- **Pn** - Z probe number to use (optional)

- **Fnnn** - Requested feedrate of the probing move. If this parameter is omitted, the last set feedrate is used

- **Snnn** - Direction of the probing move. S=0 (default) means travel forwards (towards the axis maximum), S=1 means go backwards (towards the axis minimum)

- **Rnnn** - Probing radius, i.e. the relative movement amount from the current position (optional, if used the S parameter is ignored)

##### Notes

- You can only specify one axis per M585 call and that XYZ are not the only possible axes for this code (UVWABC would be valid as well).

- The values of the XYZ parameters are the absolute distances between the position at which the endstop is actually triggered and your own start position. It is mandatory to measure this distance once before M585 can be used reliably. An example: Say you wish to probe the tool offset on the X axis. If the trigger position of your endstop is at X=210 and you want to drive your tool from X=190 into the endstop switch, you need to specify -20 as your X parameter because you expect to travel 20mm towards the endstop switch and need to correct this factor. If you drive the tool backwards (e.g. from X=210 to X=190), the correction factor should be 20.

- You can use M585 to probe until a regular axis endstop is triggered.

- If you want to probe until a custom input is triggered, use M558 to configure an additional probe that uses that pin, then refer to that probe in your M585 command. See example above.

- In principle the following workflow should be performed for each axis using a macro file. You may wish to enhance this workflow depending on your own requirements and endstop configuration.

  - Reset the axis tool offset (G10 Pxx X0 Y0 Z0)

  - Select your tool (Txx)

  - Move the tool to your starting position (G1 X?? Y?? Z?? F3000)

  - Drive the tool into the endstop or custom input, stop there and apply the new tool offset with the given correction factor (M585 XYZ?? F1000 P??)

  - Call G10 Pxx with your tool number to get the corrected tool offset or call M500 (supported in RRF 1.20 and later) to store the probed tool offsets on the SD card

##### Parameters

- **Xnnn** - Probe tool in X direction where nnn specifies the expected distance between the trigger point of your endstop switch and the starting point

- **Ynnn** - Probe tool in Y direction where nnn specifies the expected distance between the trigger point of your endstop switch and the starting point

- **Znnn** - Probe tool in Z direction where nnn specifies the expected distance between the trigger point of your endstop switch and the starting point

- **U,V,W,A,B,Cnnn** - As for X,Y,Z above

- **Ennn** - Custom endstop number to use (optional). This must be the drive number of the according endstop (i.e. X=0, Y=1, Z=2, E0=3 etc.)

- **Lnnn** - Trigger level of the custom endstop (optional, 0 = active-low, 1 = active-high). This requires the 'E' parameter to be present \[RRF 2.04 and later\]

- **Fnnn** - Requested feedrate of the probing move. If this parameter is omitted, the last set feedrate is used

- **Snnn** - Direction of the probing move. S=0 (default) means travel forwards (towards the axis maximum), S=1 means go backwards (towards the axis minimum)

- **Rnnn** - Probing radius, i.e. the relative movement amount from the current position (optional, if used the S parameter is ignored) \[requires RRF 1.20 or later\]

##### M585 X100 F600 E3 L0 S0 ; probe X until E0 endstop goes low

Notes

- You can only specify one axis per M585 call and that XYZ are not the only possible axes for this code (UVWABC would be valid as well).

- The values of the XYZ parameters are the absolute distances between the position at which the endstop is actually triggered and your own start position. It is mandatory to measure this distance once before M585 can be used reliably. An example: Say you wish to probe the tool offset on the X axis. If the trigger position of your endstop is at X=210 and you want to drive your tool from X=190 into the endstop switch, you need to specify -20 as your X parameter because you expect to travel 20mm towards the endstop switch and need to correct this factor. If you drive the tool backwards (e.g. from X=210 to X=190), the correction factor should be 20.

- In case you are using different switches for tool probing, RepRapFirmware allows you to use a custom endstop. If a different endstop than the axis endstop is used, the drive number of the matching endstop can be specified via the optional E parameter (e.g. E4 for the E1 endstop).

- In principle the following workflow should be performed for each axis using a macro file. You may wish to enhance this workflow depending on your own requirements and endstop configuration.

- Reset the axis tool offset (G10/M568 Pxx X0 Y0 Z0)

  - Select your tool (Txx)

  - Move the tool to your starting position (G1 X?? Y?? Z?? F3000)

  - Drive the tool into the endstop, stop there and apply the new tool offset with the given correction factor (M585 XYZ?? F1000 E??)

  - Call G10 Pxx with your tool number to get the corrected tool offset or call M500 (supported in RRF 1.20 and later) to store the probed tool offsets on the SD card

