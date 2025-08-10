## M471: Rename File/Directory on SD-Card

Supported in RRF \>= 2.03.

### Usage

- M471 S"source/name" T"dest/name" D1

### Parameters

- **S"name"** Name of existing file/directory

- **T"name"** New name of file/directory

- **Dnnn** Setting this to 1 will delete any existing file that matches the T parameter value

### Examples

M471 S"/sys/config-override.g" T"/sys/config-override.g.bak"

### Notes

Rename or move a file or directory. Using the D parameter will delete any existing file with the target name. Renaming or moving across directories is possible though not from one SD-Card to another.

