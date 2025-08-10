## M375: Load height map

Loads the grid matrix file

### Parameters

- **P"filename"**

### Examples

M375 M375 P"MyAlternateHeightMap.csv"

### Notes

Without parameters loads default grid (**sys/heightmap.csv**), and with specified filename attempts to load the specified grid. If not available will not modify the current grid.

In RepRapFirmware this command is equivalent to the G29 S1 command.

