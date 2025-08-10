## M577: Wait until endstop is triggered

Wait for an endstop switch to be triggered or an input to become active.

• RepRapFirmware 3.01 and later

• RepRapFirmware 3.0

• RepRapFirmware 2.x and earlier

##### Parameters

- **Sn** Desired endstop or input level: 1 = triggered/active (default), 0 =not triggered/inactive

- **X, Y, Z, U, V, W, A, B, C, D** Axis endstop to wait for

- **Pnnn** Input pin number to wait for (see M950 with J parameter)

##### M577 X S0 ; wait until X endstop is not triggered M950 J2 P"!e0stop" ; define input pin number 2 M577 P2 ; wait until tE0 endstop input is low

##### Parameters

- **P"nnn"** Specifies one or more pin names, see Pin Names

##### Parameters

- **Snnn** Desired endstop level

- **Xnnn** Select X axis endstop

- **Ynnn** Select Y axis endstop

- **Znnn** Select Z axis endstop

- **Ennn** Select extruder drive endstop

##### M577 E0 S1

Wait for an endstop switch to be pressed. The example above will wait until the first extruder endstop is triggered.

The following trigger types may be used using the 'S' parameter:

0: Endstop not hit 1: Low endstop hit 2: High endstop hit 3: Near endstop (only Z probe)

