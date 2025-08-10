## M26: Set SD position

### Parameters

- Snnn File position from start of file in bytes

- Pnnn (Optional) Proportion of the first move to be skipped, default 0.0, must be less than 1.0

- Xnnn, Ynnn, Znnn (Optional) If the command at the specified file position is a G2 or G3 command and the P parameter is nonzero then these are the coordinates of the centre of the arc for that command.

### Examples

M26 S49315

Set the file offset in bytes from the start of the SD card file selected by M23. The offset must correspond to the start of a GCode command. This command is used when restarting a job that was interrupted, for example by a power failure.

