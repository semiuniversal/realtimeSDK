## M472: Delete File/Directory on SD-Card

Supported in RRF \>= 3.5.

### Usage

- M472 P"filename"

### Parameters

- **P"name"** Name of file/directory

- **Rnnn** Delete directory recursively (defaults to 0)

### Examples

M472 P"/sys/foobar" R1

