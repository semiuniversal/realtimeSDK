## T: Select Tool

### Parameters

- **nnn**: Tool number to select. A negative number deselects all tools.

- **R1**: Select the tool that was active when the print was last paused (firmware 1.20 and later)

- **Pnnn**: Bitmap of all the macros to be run (dc42 build 1.19 or later and ch fork 1.17b or later)

- **Tnn**: (RRF 3.4 and later) Alternative way to specify the tool number, which allows use of an expression to calculate the tool number

### Examples

T0 ; select tool 0 T1 P0 ; select tool 1 but don't run any tool change macro files T-1 P0 ; deselect all tools but don't run any tool change macro files T R1 ; select the tool that was active last time the print was paused T ; report the current tool number T T{state.currentTool + 1} ; select the tool whose number is one higher than the current tool

### Description

If Tn is used to select tool n but that tool is already active, the command does nothing. Otherwise, the sequence followed is:

**Note:** Prior to RRF 3.3, when changing tools, tool change macro files are not run unless all axes have been homed. In RRF 3.3 and later, tool change macro files are run **regardless of whether axes have been homed or not**. You can use conditional GCode to choose which commands are executed if axes have been homed/not homed.

1.  If the new tool number is not the same as the old tool number, including if either old or new tool number is -1 (i.e. no tool), the current coordinates are saved to memory slot 2 automatically (see G60).

2.  Run macro tfree#.g where \# is the number of the old tool.

3.  If a tool is already selected, deselect it and set its heaters to their standby temperatures (as defined by the R parameter in the most recent G10/M568 command for that tool)

4.  Run macro tpre#.g where \# is the number of the new tool

5.  Set the new tool to its operating temperatures specified by the S parameter in the most recent G10/M568 command for that tool

6.  Run macro tpost#.g where \# is the number of the new tool. Typically this file would contain at least a M116 command to wait for its temperatures to stabilise.

7.  Apply any X, Y, Z offset for the new tool specified by G10

8.  Use the new tool.

### Notes

- Selecting a non-existent tool (49, say) just does Steps 1-2 above, and also removes any X/Y/Z offset applied for the old tool. That is to say it leaves the previous tool in its standby state. You can, of course, use the G10/M568 command beforehand to set that standby temperature to anything you like.

- After a reset tools will not start heating until they are selected. You can either put them all at their standby temperature by selecting them in turn, or leave them off so they only come on if/when you first use them. The M0, M1 and M112 commands turn them all off. You can, of course, turn them all off with the M1 command, then turn some back on again. Don't forget also to turn on the heated bed (if any) if you use that trick.

- Tool numbering starts at 0 by default however M563 allows the user to specify tool numbers, so with them you can have tools 17, 29 and 48 if you want. Negative numbers are not allowed. The highest Tool number that can be defined from RRF3 onwards is 49.

- From RRF 3.3 both selecting as well as deselecting with a configured spindle will stop the spindle assigned to these tools. This is in accordance to NIST GCode standard that says "after a tool change is complete the spindle is stopped".

- Under special circumstances, the execution of tool macro files may not be desired. RepRapFirmware 1.19 or later supports an optional **P** parameter to specify which macros shall be run. If it is absent then all of the macros above will be run, else you can pass a bitmap of all the macros to be executed. The bitmap of this value consists of tfree=1, tpre=2 and tpost=4.

- You may wish to include a move to a parking position within the tfreeN.g GCode macro in order to allow the new extruder to reach temperature while not in contact with the print.

- Tool offsets are applied whenever there is a current tool. So they are applied in tfree.g (for the outgoing tool) and in tpost.g (for the incoming tool), but not in tpre.g (because no tool is current at that point).

For more information and example usage of tool change macros, see: Multiple tools and tool change macros
