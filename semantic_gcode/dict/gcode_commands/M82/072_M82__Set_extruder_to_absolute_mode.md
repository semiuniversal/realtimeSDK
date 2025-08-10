## M82: Set extruder to absolute mode

### Examples

M82 ; absolute extrusion mode

### Description

Makes the extruder interpret extrusion as absolute positions.

It is strongly recommended to use relative extrusion, not absolute extrusion. This is especially true for multi tool systems.

### Notes

- RRF maintains a flag for the extruder absolute/relative positioning state. As such, the following is true:

  - Each input channel (SD card, USB, http, telnet etc) has its own flag for the extruder absolute/relative positioning state.

  - At the end of running config.g at startup, the flag state is copied to all input channels. If no absolute/relative positioning is specified in config.g, the default M82 (absolute) is used.

  - The flag state is saved when a macro starts and is restored when a macro ends. This applies only to macros, not to job files. Changes made during job files persist for the session or until they are changed again.

- In **absolute extrusion mode only** the virtual extruder counter is incremented when an extruder is commanded to move. This single global counter is visible with the "E" parameter of the M114 response and in the object model at move.virtualEPos. This counter is also set by G92 E"nn" so G92 E0 sets it to 0. This behaviour is there to allow old slicers and other clients which do not understand multiple tool machines to work with absolute extrusion mode. It does not work well with multiple tools, hence why relative extrusion mode is recommended. The virtual E position is reset when a print is started.

#### Example Behaviour

• Single extruder

• Multiple extruders

M82 ; set to absolute mode M114 Response (abridged): .. E:0.000 E0:0.0 .. Note the virtual extruder and Extruder E0 are both at 0 as no movement has been commanded yet. Commanding a move: G1 E10 F300 M114 Response (abridged): .. E:10.000 E0:10.0 .. Both counters show the movement.

Now resetting the Virtual E position to 0, followed by a further move: G92 E0 G1 E11 F300 M114 Response (abridged): .. E:11.000 E0:21.0 .. So the virtual E position has incremented form 0 to 11, but the E0 counter was not reset by G92 E0, so has continued to count up from 10, so is now at 21.

M82 ; set to absolute mode M114 Response (abridged): .. E:0.000 E0:0.0 E1:0.0 E2:0.0 .. Note the virtual extruder and Extruder E0,E1 and E2 are all at 0 as no movement has been commanded yet. Commanding a move with T0 selected G1 E10 F300 M114 Response (abridged): .. E:10.000 E0:10.0 E1:0.0 E2:0.0 .. Both the Virtual extruder and the E0 counters show the movement.

Switching to T2 (no extrusion in the tool change commands in this example), then commanding another movement: G1 E5 F300 M114 Response .. E:5.000 E0:10.0 E1:0.0 E2:-5.0 .. This shows the issue with using absolute extrusion with multiple tools. The virtual extruder was on 10, so in absolute mode the command to move to 5 is a retraction of 5mm. so its updated form 10 to 5, and the selected extruder (E2) moves back from 0 to -5.

It is possible to work around this by resetting the virtual extruder position using G92 E0 before each tool change. Alternatively if its state is needed to be maintained then saving the virtual position into a separate global variable for each tool as part of the tfreeN.g tool change macros and then restoring it in the tpostN.g tool change macros should allow this, however in most cases its better to use M83

