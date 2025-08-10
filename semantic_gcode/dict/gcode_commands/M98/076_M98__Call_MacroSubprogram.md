## M98: Call Macro/Subprogram

### Parameters

- **P"nnn"** Macro filename. If no path is specified, the default folder is /sys.

- **Rn** When M98 is used inside a macro and no P parameter is provided, indicates whether the macro can be paused from this point onwards and subsequently restarted from the beginning. (RRF 3.4 and later, see Notes for usage).

### Examples

M98 P"mymacro.g" ; Runs the macro in the file /sys/mymacro.g M98 P"macro.g" S100 Y"string" ; Runs /sys/macro.g, passes the values for parameters S and Y to the macro ; within macros M98 R1 ; macro can be paused from this point onwards

### Notes

- Macro calls can be nested (i.e. a macro can call another macro). From RRF v3.4.0, the maximum stack depth is 10. This is the maximum number of macro calls and M120 commands that may be nested. However, there is also a limit on the number of open files, which is 20 on Duet 3 and 10 on Duet 2. For example, on Duet 2 if you have a print running from SD card and logging enabled, you will be limited to a macro nesting depth of 8.

- **P** parameter:

  - In RRF 3.x and later, quotation marks around the filename are mandatory. In RRF2.x and earlier, the filename can be enclosed in quotes if required. See Quoted Strings for details.

  - The filename may include a path to a subdirectory. For relative paths, the default folder is /sys. Absolute file paths are also supported starting with "0:/" for the internal SD card or "1:/" for the external SD card if fitted.

  - If the P parameter is provided then any additional parameters will be passed to the macro. In RRF 3.3 and later M98 supports additional parameters used to pass information to the macro being called. See the GCode Meta Commands, Macro parameters documentation for the details.

- **R** parameter: this is used within a macro file to indicate whether the macro can be paused from this point on.

  - 0 = (default) remainder of current macro cannot be paused. By default, a macro cannot be paused except in the case of power failure.

  - 1 = remainder of current macro can be paused **and the macro restarted from the beginning after resuming**,

  - **Do not use R1 in system macros** such as tool change macros, homing macros, pause.g or resume.g.

