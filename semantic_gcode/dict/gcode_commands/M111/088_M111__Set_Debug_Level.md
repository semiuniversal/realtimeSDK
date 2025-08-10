## M111: Set Debug Level

### Parameters

- **Pnn** Debug module number

- **Sn** Debug on (S1), off (S0). S0 is equivalent to D0. S1 is equivalent to D{0xFFFF}.

- **Dnnn** Set/clear individual debug flags for the specified module

- **Bnnnn**

  - RRF 3.6.0 and later: Selects the CAN-connected expansion/tool board

  - RRF 3.5.x: Redirect debug output and allocate buffer memory size

- **Fnnnn** Redirect debug output and allocate buffer memory size (RRF 3.6.0 and later)

#### SBC mode

From v3.6.0, M111 P-1 can be used to set debug logging parameters for DCS in SBC mode. Additional parameters for M111 P-1 include:

- **Snnn** Set debug level (one of trace, debug, info, warning, error, fatal)

- **Onnn** Output log messages as generic messages via DWC (e.g. O1)

### Examples

M111 M111 P4 S1 ; enable all debugging for module 4 M111 P4 D2 ; enable just bit 1 debugging information for module 4 M111 B1024 ; allocate a 1K debug buffer (RRF 3.5.x)

### Description

Enable or disable debugging features for the module number specified by the P parameter. M111 without parameters lists all the modules, their numbers, and whether debugging is enabled for each.

The details of what debugging information is output when debugging is enabled varies from one firmware revision to another, so it is not specified here.

### Notes

- Print quality may be affected when debug output is enabled because of the volume of data sent to USB.

- Debug output is normally sent to the USB port, and any debug output generated from an interrupt service routine is discarded. You can use M111 with the F (RRF 3.6.0 or later) or B (RRF 3.5.x) parameter to allocate a debug buffer; in which case debug output is written to the buffer (even when it comes from an interrupt service routine) and is later extracted and written as a generic message to all active input channels. The F (or B) parameter is the debug buffer size in bytes and must be an exact power of 2. Debug data that can't be written to the buffer because it is full is discarded.

- After the F (RRF 3.6.0 or later) or B (RRF 3.5.x) parameter is used to allocate a debug buffer, if excessive amounts of debug data are generated then HTTP disconnections may occur.

- Debug output should normally be used only for debugging firmware, or when instructed to help with diagnosis of particular issues.

