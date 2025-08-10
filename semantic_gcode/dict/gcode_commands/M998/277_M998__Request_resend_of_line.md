## M998: Request resend of line

### Parameters

- **Pnnn** Line number

### Examples

M998 P34

Request a resend of line 34.

### Notes

In some implementations the input-handling code overwrites the incoming G Code with this when it detects, for example, a checksum error. Then it leaves it up to the GCode interpreter to request the resend.

