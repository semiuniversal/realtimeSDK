## M606: Fork input file reader

### Parameters

- **S\[mode\]**\> Mode, must be 1 (other values are reserved for future use).

### Example

M606 S1 ; Fork input reader

### Description

If the S1 parameter is present and the command occurs within a job from SD card or other storage media, or within a macro file invoked by such a job, it causes the input stream to be forked. From that point on, each motion system can read and execute commands from the job file and any macro files invoked by it independently of other motion systems. In consequence, when the movement queue of one motion system becomes full, or one motion system is waiting for a tool change or other action to complete, the other motion system(s) can still read and execute commands.

### Notes

- This command is only supported on firmware configurations that support two or more motion systems that execute asynchronously with respect to each other.

- When the input stream is forked, all local variables belonging to the un-forked input stream are copied to the fork(s). If the command occurs in a macro then the return stack is also copied to the forks, so that each fork will execute the remainder of all the macro files in the stack.

- In the event that this command with the S1 parameter is executed from a job file when the input stream has already been forked, it is ignored.

- If the S1 parameter is present and the command is used from an input channel other than a file stream then a warning is issued but it is otherwise ignored.

- If this command is run without the S parameter then the firmware just reports whether the input stream that runs stored jobs has been forked.

- See also the M598 command which is used to synchronise forked input streams at particular point in the file.

- See Multiple Motion Systems for more information.

