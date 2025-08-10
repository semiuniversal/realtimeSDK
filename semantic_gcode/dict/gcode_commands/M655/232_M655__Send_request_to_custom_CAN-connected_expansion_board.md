## M655: Send request to custom CAN-connected expansion board

Supported from firmware version 3.6.0

### Parameters

- **Bnn** CAN address of target board

- **C"nn.string"** Reduced string parameter, for example CAN address and port name

- **A"string"** Normal string parameter

- **Pnnn** Unsigned integer parameter, maximum 65535

- **R** and/or **S** Signed integer parameters

- **E** and/or **F** Floating point parameters

### Examples

M655 B10 C"hello world" P1 R-4 E0.123 M655 C"10:pump" P0 S22 F42.1

### Description

This command allows standard main board firmware builds to control features on custom CAN-connected expansion boards in situations where standard commands such as M950 and M42 are not suitable, for example because they do not provide sufficient parameters. The main board firmware expects to receive a standard reply to it.

### Notes

- All parameters are optional, except that exactly one of B or C must be present.

- The C parameter if present must start with the CAN address of the target board followed by a period. It will be "reduced" by removing this prefix and any underscores or hyphens and converting all characters to lowercase before sending the request to the target board.

- The total number of bytes occupied by the parameters provided, excluding the B parameter and after reducing the C parameter, must not exceed 60. The number of bytes in a string parameter is the number of bytes in the UTF8-encoded string plus 1. The P parameter occupies 2 bytes and the signed integer and float parameters occupy 4 bytes each.

