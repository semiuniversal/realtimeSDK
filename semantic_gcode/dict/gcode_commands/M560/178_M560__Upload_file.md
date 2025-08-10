## M560: Upload file

### Parameters

- **P"filename"** File name to upload to.

- **Snnn** File size for binary transfer. If not present, the transfer is terminated by a special string, described below.

- **Cnnn** CRC-32 of the file (optional)

### Examples

M560 P"index.html"

### Notes

In RRF 3.1 and earlier, the default filename is reprap.htm and the default path is /www.

After sending M560 the file should be sent, terminated by the string \<!-- \*\*EoF\*\* --\>. Clearly that string cannot exist in the body of the file, but can be put on the end to facilitate this process.

