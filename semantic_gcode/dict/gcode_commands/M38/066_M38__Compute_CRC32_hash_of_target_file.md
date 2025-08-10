## M38: Compute CRC32 hash of target file

From 3.6 onwards

Used to compute a hash of a file on the SD card and returns a hexadecimal string which is the CRC32 of the file.

### Examples

M38 gcodes/myfile.g

### Notes

If the file cannot be found, then the string "Cannot find file" is returned instead.

This used to compute the SHA1 hash but that deprecated and removed from ReprapFirmware 3.5.2 and later.

