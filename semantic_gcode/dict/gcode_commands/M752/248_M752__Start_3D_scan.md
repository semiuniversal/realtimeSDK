## M752: Start 3D scan

Instruct the attached 3D scanner to initiate a new 3D scan and to upload it to the board's SD card (i.e. in the "scans" directory).

### Parameters

- Snnn: Length/degrees of the scan

- Rnnn: Resolution (new in RRF 2.0) \[optional, defaults to 100\]

- Nnnn: Scanner mode (new in RRF 2.0) \[optional, 0=Linear (default), 1=Rotary\]

- Pnnn: Filename for the scan

### Examples

M752 S300 Pmyscan

### Notes

Before the SCAN command is sent to the scanner, the macro file "scan_pre.g" is executed and when the scan has finished, the macro file "scan_post.g" is run. Be aware that both files must exist to avoid error messages.

