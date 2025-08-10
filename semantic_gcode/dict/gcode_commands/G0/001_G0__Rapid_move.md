## G0: Rapid move

Same as G1 except as follows:

- When in Laser or CNC mode, the move is executed at the maximum feedrate available. The F parameter (if present) is ignored.

- In some architectures such as Scara and Polar the move will not necessarily be in a straight line.

See 'G1: Controlled linear' move for usage.

