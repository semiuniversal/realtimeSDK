## M24: Start/resume SD print

### Examples

M24

The machine prints from the file selected with the M23 command. If the print was previously paused with M25, printing is resumed from that point. To restart a file from the beginning, use M23 to reset it, then M24.

When this command is used to resume a print that was paused, the macro file **resume.g** is run prior to resuming the print.

