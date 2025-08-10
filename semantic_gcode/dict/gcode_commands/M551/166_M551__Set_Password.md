## M551: Set Password

### Parameters

- **P"nnn"** Password

### Examples

M551 P"my-very-secret-word"

### Description

The code 'P' is not part of the password. Note that as this is sent in clear it does not (nor is it intended to) offer a security. But on machines that are (say) on a network, it might prevent idle messing about. The password can contain any printable characters except ';', which still means start comment.

### Notes

If the specified password differs from the default one (i.e. reprap), the user will be asked to enter it when a connection is established.

Quotation marks around the password are mandatory in RRF3, but discretionary in earlier firmware versions.

