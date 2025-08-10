## M929: Start/stop event logging to SD card

When event logging is enabled, important events such as power up, start/finish printing and (if possible) power down will be logged to the SD card. Each log entry is a single line of text, starting with the date and time if available, or the elapsed time since power up if not. If the log file already exists, new log entries will be appended to the existing file.

### Parameters

- **P"filename"** The name of the file to log to. Only used if the S1 parameter is present. A default filename will be used if this parameter is missing.

- **Sn** S1 = start logging, S0 = stop logging (RRF \<= 3.2.0)

- **Sn** S0 = stop logging, S1 = log level WARN, S2 = log level INFO, S3 = log level DEBUG (RRF \>= 3.2.0)

### Examples

M929 P"eventlog.txt" S1 ; start logging warnings to file eventlog.txt M929 S0 ; stop logging

### Notes

From RepRapFirmware 3.2.0 and later, more granular logging is available. There are three log levels, and no logging. When logging is enabled, each line in the log will have the log level of that message added after the timestamp.

- WARN: All log messages from previous versions will fall into this log level

- INFO: G10, M117, M291 and M292 invocations will fall into this log level

- DEBUG: all output not listed above will be logged within this log level

**Caution**: do not rename or delete the current log file while logging is enabled!

Also see M118.

