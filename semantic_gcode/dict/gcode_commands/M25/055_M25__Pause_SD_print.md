## M25: Pause SD print

### Examples

M25

The machine pauses printing at the current position within the file. To resume printing, use M226 instead. M226 is intended for use in the GCode file being printed, for example to pause after a particular layer has completed. So it waits until all the moves in the queue have been completed. M25 is intended for use from a different source of GCodes than the current print from SD card (like the web interface console, PanelDue or Macro).

M25 attempts to execute as quickly as possible and follows the following logic:

- When RRF receives M25 it will look for a move in the current queue after which it can stop without violating the configured jerk limits.

- If it finds one it stops after that move without decelerating (because the jerk limits allow that)

- If it can't find one it will plan and execute a deceleration. In this case the pause will occur 1 move + 2 seconds after M25 is sent.

That means the longest it will take to pause is 1 move + 2 seconds. In most situations pause occurs much quicker than that.

After movement is halted as described above but prior to the pause operation completing, the macro file **pause.g** is run. This allows the head to be moved away from the print, filament to be retracted, etc.

Note that if a pause is commanded while a macro is being executed, the pause will be deferred until the macro has completed.

