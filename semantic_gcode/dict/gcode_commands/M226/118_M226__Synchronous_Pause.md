## M226: Synchronous Pause

### Examples

M226

### Description

Initiates a pause in the same way as if the pause button is pressed, except that execution of all prior GCode commands in the same input stream is completed first. Then the SD card input stream is paused and file sys/pause.g is run.

### Notes

- Use M226 when a pause is required in the GCode file being printed, for example to pause after a particular layer has completed. It waits until all the moves in the queue have been completed.

- Use M600 when a pause is required to change filament in the GCode file being printed.

- Use M25 when a pause is required from a different source of GCodes (such as the web interface console, PanelDue or a Macro).

