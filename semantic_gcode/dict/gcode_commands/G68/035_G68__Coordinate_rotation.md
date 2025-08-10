## G68: Coordinate rotation

### Usage

- G68 Xnnn Ynnn Rnnnn

- G68 Annn Bnnn Rnnnn

### Parameters

- **Xnnn, Ynnn...** Centre coordinates to rotate about

- **Annn** first centre coordinate in the selected plane (e.g. equivalent to Xnnn if the selected plane is XY)

- **Bnnn** second centre coordinate in the selected plane (e.g. equivalent to Ynnn if the selected plane is XY)

- **Rnnn** angle to rotate in degrees. Positive angles rotate anticlockwise when viewing the selected plane from above.

Rotates the coordinate system in the current plane as selected by G19. You may either specify the coordinates of the two axes of the selected plan (e.g. X and Y if using the default XY plane or after G17) or you may specify A and B coordinates.

RepRapFirmware implements G68 for the XY plane only. Coordinate rotation is not applied if any of the following is true:

- The move is a G1 Hn or G0 Hn move with n != 0;

- The selected plane is not XY;

- G53 is in effect;

- A system macro (i.e. one that is invoked automatically, such as homing or tool change) is being run.

Note: if G68 coordinate rotaton is in effect and you use one of G54 thru G59.3 to switch to a different workplace coordinate system, the rotation origin will move in line with the origin of the workplace coordinate system.

