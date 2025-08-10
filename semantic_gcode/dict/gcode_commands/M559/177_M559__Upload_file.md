## M559: Upload file

### Parameters

- **P"filename"** File name to upload to.

- **Snnn** File size for binary transfer. If not present, the transfer is terminated by a M29 command

- **Cnnn** CRC-32 of the file (optional)

### Examples

M559 P"config.g"

### Notes

In RRF 3.1 and earlier, the default filename is config.g and the default path is /sys. In RRF 3.2 and later there is no default filename.

Quotation marks around the filename are mandatory in RRF 3.2 and later.

Was used by the original web interface to upload a configuration file. Can now be used to upload any file.

