## M425: Configure backlash compensation

Support in RRF 3.5 and later.

### Parameters

- **X,Y,Z,A,B...** Backlash in mm for the specified axis motor

- **Snn** (optional) Distance multiplier, default 10

This command tells RRF to insert additional steps when the specified motors reverse direction, to compensate for backlash. The additional steps are inserted over a distance of at least the distance multiplier times the amount of backlash. For example, a multiplier of 10 and a backlash of 0.5mm would mean that the backlash steps would be inserted over as many moves as needed to make up at least 5mm of movement. If the multipler is set too low then missed steps could result.

The X,Y,Z... parameters refer to individual motors or sets of motors, not Cartesian axes. For example, on a CoreXY machine the X parameter defines the backlash compensation applied to the X motor, and the Y parameter defines the backlash compensation applied to the Y motor.

M425 with no parameters reports the current backlash compensation settings. The settings can also be read from the object model in move.axes\[\].backlash and move.backlashFactor.

### Examples

M425 X0.15 Y0.23 S5

### Limitations

- Backlash compensation isn't applied when Delta kinematics are used.

- If M584 is used to configure multiple drivers for an axis, the same backlash compensation is applied to all of them.

- Backlash compensation isn't applied to moves that level the bed after running G32

- Backlash compensation isn't a substitute for good mechanics. In particular, if the machine is a 3D printer then extrusion will continue while the backlash is taken up, which may result in a seam where the direction is changed.

