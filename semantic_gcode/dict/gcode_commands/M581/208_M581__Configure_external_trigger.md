## M581: Configure external trigger

• RepRapFirmware 3.01 and later

• RepRapFirmware 3.0

• RepRapFirmware 2.x and earlier

##### Parameters

- **P** Specify one or more input pin numbers that you created using M950 with the J parameter, or -1 to delete the trigger

- **Tnn** Logical trigger number to associate the input(s) with, from zero up to a firmware-specific maximum

- **S** Whether trigger occurs on an inactive-to-active edge of that input (S1, default), active-to-inactive edge (S0), or ignores that input (S-1).

- **R** Condition: whether to trigger at any time (R0, default), only when printing a file from SD card (R1), or only when not printing a file from SD card (R2, supported in RRF 3.2 and later). R-1 temporarily disables the trigger.

- **X**, **Y**, **Z** or any other axis letter: axis or axes whose endstop switches are to cause the trigger

##### M581 T2 P0:3 S1 R1 ; invoke trigger 2 when an inactive-to-active edge is detected on input 0 or input 3 and a file is being printed from SD card M581 T3 X Y S1 ; invoke trigger 3 when the X or Y endstop switch is triggered M581 T2 P-1 ; don't invoke trigger 2 on any input change any more

Notes

- When M581 is executed, if the T parameter is present but the other parameters are omitted, the trigger inputs and edge polarities for that trigger number are reported. Otherwise, the specified inputs and their polarities are added to the conditions that cause that trigger.

- Trigger number 0 causes an emergency stop as if M112 had been received. Trigger number 1 causes the print to be paused as if M25 had been received. Any trigger number \# greater than 1 causes the macro file sys/trigger#.g to be executed. Polling for further trigger conditions is suspended until the trigger macro file has been completed. RepRapFirmware does not wait for all queued moves to be completed before executing the macro, so you may wish to use the M400 command at the start of your macro file. If several triggers are pending, the one with the lowest trigger number takes priority.

- A maximum of 32 triggers can be configured on Duet 3 6HC/6XD, a maximum of 16 on Duet 3 Mini 5+ and Duet 2 WiFi/Ethernet/Maestro.

- **Warning**: if executed during a job, and more than one line long the GCode within the trigger file may be executed between later commands from the job. Bounding the trigger file with M25 and M24 may help, but this will cause warnings if the trigger happens outside of a job. The use of M25/M24 will cause the execution of pause and resume system macros.

For examples, see

##### Parameters

- **P** Specify one or more pin names, see Pin Names

- **Tnn** Logical trigger number to associate the endstop input(s) with, from zero up to a firmware-specific maximum

- **C** Condition: whether to trigger at any time (C0, default) or only when printing a file from SD card (C1)

##### Notes

- Use the P parameter to specify one or more pin names. Use P"nil" to disable that trigger number.

- The pin(s) do not need to be exclusively used by M581; for example, it is permitted to specify the name of a pin that has already been declared as used by an endstop switch in a M574 command.

- The S parameter used in RRF2.x is removed. The command waits for a low-to-high input transition. To wait for a high-to-low transition, invert the pin name using '!'.

- When M581 is executed, if the T parameter is present but the other parameters are omitted, the trigger inputs and edge polarities for that trigger number are reported. Otherwise, the specified inputs and their polarities are added to the conditions that cause that trigger.

- Trigger number 0 causes an emergency stop as if M112 had been received. Trigger number 1 causes the print to be paused as if M25 had been received. Any trigger number \# greater than 1 causes the macro file sys/trigger#.g to be executed. Polling for further trigger conditions is suspended until the trigger macro file has been completed. RepRapFirmware does not wait for all queued moves to be completed before executing the macro, so you may wish to use the M400 command at the start of your macro file. If several triggers are pending, the one with the lowest trigger number takes priority.

- **Warning**: if executed during a build process, and more than one line long the GCode within the trigger file may be executed between later commands from the build file. Bounding the trigger file with M25 and M24 may help, but this will cause error warnings if the trigger happens outside of a build process. The use of M25/M24 will cause the execution of pause and resume system macros.

##### Parameters

- **Tnn** Logical trigger number to associate the endstop input(s) with, from zero up to a firmware-specific maximum (e.g. 9 for RepRapFirmware)

- **X, Y, Z, E** Selects endstop input(s) to monitor

- **P** Reserved, may be used in future to allow general I/O pins to cause triggers

- **S** Whether trigger occurs on a rising edge of that input (S1, default), falling edge (S0), or ignores that input (S-1). By default, all triggers ignore all inputs.

- **C** Condition: whether to trigger at any time (C0, default) or only when printing a file from SD card (C1)

##### M581 E1:2 S1 T2 C1 ; invoke trigger 2 when a rising edge is detected on the E1 or E2 endstop input and a file is being printed from SD card

Notes

- When M581 is executed, if the T parameter is present but the other parameters are omitted, the trigger inputs and edge polarities for that trigger number are reported. Otherwise, the specified inputs and their polarities are added to the conditions that cause that trigger. Using S-1 with no X Y Z or E parameters sets the trigger back to ignoring all inputs.

- Trigger number 0 causes an emergency stop as if M112 had been received. Trigger number 1 causes the print to be paused as if M25 had been received. Any trigger number \# greater than 1 causes the macro file sys/trigger#.g to be executed. Polling for further trigger conditions is suspended until the trigger macro file has been completed. RepRapFirmware does not wait for all queued moves to be completed before executing the macro, so you may wish to use the M400 command at the start of your macro file. If several triggers are pending, the one with the lowest trigger number takes priority.

- A maximum of 16 triggers can be configured on Duet 2.

- **Warning**: if executed during a build process, and more than one line long the GCode within the trigger file may be executed between later commands from the build file. Bounding the trigger file with M25 and M24 may help, but this will cause error warnings if the trigger happens outside of a build process. The use of M25/M24 will cause the execution of pause and resume system macros.

