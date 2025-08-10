## M374: Save height map

### Parameters

- **P"filename"** Name of the file to save to

### Usage

- M374

- M374 P"MyAlternateHeightMap.csv"

### Notes

This saves the grid parameters and height map into the specified file, or the default file **heightmap.csv** if no filename was specified. To load the height map automatically at startup, use command G29 S1 or M375 in the config.g file.

The G29 S0 command automatically saves the height map to file, therefore you do not need to use M374 after G29 S0.

