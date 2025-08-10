## M408: Report JSON-style response

**Deprecated in RRF 3.3 and later; planned for removal in RRF 3.7 and later.** Use M409 instead to get response from Object Model, which provides more information.

### Parameters

- **Snnn** Response type (only used when R is zero or not present)

- **Rnnn** Response sequence number (see **seq** and **resp** in list below)

### Examples

M408 S0

### Usage

This reports a JSON-style response by specifying the desired type using the 'S' parameter. The following response types are supported in RRF 3.5 and earlier. Only types 0 and 1 are supported in RRF 3.6.0 and later.

- Type 0 is a short-form response, similar to the response used by older versions of the web interface.

- Type 1 is like type 0 except that static values are also included.

- Type 2 is similar to the response provided by the web server for Duet Web Control.

- Type 3 is an extended version of type 2 which includes some additional parameters that aren't expected to change very frequently.

- Type 4 is an extended version of type 2 which may be used to poll for current printer statistics.

- Type 5 reports the current machine configuration.

Here is an example of a typical type 0 response:

{"status":"I","heaters":\[25.0,29.0,28.3\],"active":\[-273.1,0.0,0.0\],"standby":\[-273.1,0.0,0.0\],"hstat":\[0,2,1\],"pos":\[-11.00,0.00,0.00\],"extr":\[0.0,0.0\],"sfactor":100.00, "efactor":\[100.00,100.00\],"tool":1,"probe":"535","fanPercent":\[75.0,0.0\],"fanRPM":0,"homed":\[0,0,0\],"fraction_printed":0.572}

The response is set as a single line with a newline character at the end. The meaning of the fields is:

**status**: I=idle, P=printing from SD card, S=stopped (i.e. needs a reset), C=running config file (i.e starting up), A=paused, D=pausing, R=resuming from a pause, B=busy (e.g. running a macro), F=performing firmware update **heaters**: current heater temperatures, numbered as per the machine (typically, heater 0 is the bed) **active**: active temperatures of the heaters **standby**: standby temperatures of the heaters **hstat**: status of the heaters, 0=off, 1=standby, 2=active, 3=heater fault. Heater 0 is normally the bed heater, heaters 1, 2.. are the extruder heaters. **pos**: the X, Y and Z (and U, V, W if present) axis positions of the current tool (if a tool is selected), or of the print head reference point if no tool is selected **extr**: the positions of the extruders **sfactor**: the current speed factor (see M220 command) **efactor**: the current extrusion factors (see M221 command), one value per extruder **tool**: the selected tool number. A negative number typically means no tool selected. **probe**: the Z-probe reading **fanPercent**: the speeds of the controllable fans, in percent of maximum **fanRPM**: the print cooling fan RPM **homed**: the homed status of the X, Y and Z axes (and U, V, W if they exist), or towers on a delta. 0=axis has not been homed so position is not reliable, 1=axis has been homed so position is reliable. **fraction_printed**: the fraction of the file currently being printed that has been read and at least partially processed. **message**: the message to be displayed on the screen (only present if there is a message to display) **timesLeft**: an array of the estimated remaining print times (in seconds) calculated by different methods. These are currently based on the proportion of the file read, the proportion of the total filament consumed, and the proportion of the total layers already printed. Only present if a print from SD card is in progress. **seq**: the sequence number of the most recent non-trivial GCode response or error message. Only present if the R parameter was provided and the current sequence number is greater than that. **resp**: the most recent non-trivial GCode response or error message. Only present if the R parameter was provided and the current sequence number is greater.

The type 1 response comprises these fields plus some additional ones that do not generally change and therefore do not need to be fetched as often. The extra fields include:

**myName**: the name of the printer **firmwareName**: the name of the firmware, e.g. "RepRapFirmware" or "Smoothieware" **geometry**: one of "cartesian", "delta", "corexy, "corexz" etc. **axes**: the number of axes **volumes**: the number of SD card slots available **numTools**: the number of available tools numbered contiguously starting from 0

The fields may be in any order in the response. Other implementations may omit fields and/or add additional fields.

### Notes

- In RRF 3.6.0, support for M408 with S parameter other than 0 and 1 has been removed. Note, M408 has been deprecated for a long time. M408 with S=0 and S=1 is still supported in RRF 3.6.0 for the benefit of users with very old PanelDue displays; however it is likely that we will need to remove this support in firmware 3.7.0 to free up flash memory space for other features.

- For a more detailed comparison of type 2 - 5, see \>Status Responses.

- PanelDue currently uses only M408 S0 and M408 S1.

