## M505: Set configuration file folder

### Parameters

- P"name" ; name of folder, default path is the existing sys path if a relative path is given

### Examples

M505 P"experimental" ; change config file path from /sys/ to /sys/experimental/

### Description

Following this command, files that would normally be fetched from /sys/ (for example, homing files and system macro files in RepRapFirmware) are fetched from the specified folder instead. Any such files that are already being executed will continue to run.

This command can be used to allow multiple configurations to be maintained easily. In RepRapFirmware the file /sys/config.g can contain just these two lines:

M505 P"config1" M98 P"config.g"

The first line changes the config file folder to /sys/config1 and the second one executes file config.g in that folder. To select an alternative configuration, only the first line needs to be edited.

