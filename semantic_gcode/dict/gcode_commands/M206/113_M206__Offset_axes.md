## M206: Offset axes

This command is deprecated. Use G10 L2 P1 instead.

### Parameters

- **Xnnn** X axis offset

- **Ynnn** Y axis offset

- **Znnn** Z axis offset

- **Unnn** U axis offset

- **Vnnn** V axis offset

- **Wnnn** W axis offset

### Order dependency

If this command refers to any axes other than X, Y and Z then it must be later in config.g than the M584 command that creates those additional axes.

### Examples

M206 X10.0 Y10.0 Z-0.4

The values specified will be subtracted from the coordinates given in G0, G1 and related commands. In firmware builds that support workplace coordinates, this command is equivalent to G10 P1 L2 with the X, Y, Z... parameters negated.

