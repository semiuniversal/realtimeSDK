## M404: Filament diameter

### Parameters

- **Nnnn** Filament diameter (in mm)

- **Dnnn** Nozzle diameter (in mm) (deprecated in 3.4-b1)

### Examples

M404 N1.75 M404 N3.0 D1.0 ; See note below about D parameter

### Notes

Enter the nominal filament width (3mm, 1.75mm) or will display nominal filament width without parameters.

The 'D' parameter is used to properly detect the first layer height when files are parsed or a new print is being started. From RRF 3.4-b1 the D parameter is deprecated and no longer used in detecting the first layer height.

The values of this command are currently only used by the print monitor and only when the slicer reports the filament usage by volume instead of by length.

