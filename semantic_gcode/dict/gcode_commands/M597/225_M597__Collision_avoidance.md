## M597: Collision avoidance

Supported from firmware version 3.5 on Duet 3 main boards

### Parameters

- X,Y...aaa First axis identifier and value

- U,V...bbb Second axis identifier and value

### Description

This configuration command is intended for use in systems having multiple tool heads that can be moved independently and asynchronously. The axis letters must be different from each other, so must the values of aaa and bbb. Normally, aaa will be zero and bbb will be positive. The command specifies that the machine position of the axis with the higher value must always be at least the difference in values greater than the position of the other axis. If this is not the case, the job will be aborted prior to starting the first move that would cause the conflict.

### Example

M597 V0 Y23.5

In the above example, the position of the Y axis must always be at least 23.5mm greater than the position of the V axis.

When Y and V are driven by independent motion systems and executing moves independently, in any block of GCode between synchronisation points, using this example the minimum of all Y coordinates inside the block (including the initial Y coordinate) must be at least 23.5mm greater than the maximum of the all V coordinates inside the block. If this is not the case, the job will be aborted prior to starting the first move that would cause the conflict.

