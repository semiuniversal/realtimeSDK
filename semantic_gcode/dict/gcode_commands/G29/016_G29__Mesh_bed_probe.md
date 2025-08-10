## G29: Mesh bed probe

This command uses a probe to measure the bed height at 4 or more points to determine its tilt and overall flatness. It then enables mesh bed compensation so that the nozzle will remain parallel to the bed. The printer must be homed with G28 before using this command.

### Usage

- G29

- G29 S0

- G29 S1 \[P"filename"\]

- G29 S2

- G29 S3 P"filename"

- G29 S4 P"filename" (only supported in Duet 3 builds of RRF 3.5 and later)

### Parameters

- **S0** Probe the bed, save the height map in a file on the SD card, and activate mesh bed compensation. The height map is stored in file is /sys/heightmap.csv.

- **S1** Load the height map from file and activate mesh bed compensation. The default filename is as for S0 but a different filename can be specified using the P parameter.

- **S2** Disable mesh bed compensation and clear the height map (also clears the map of invalid probe points in builds that support it)

- **S3** Save height map to the specified file (supported in RRF 2.04 and later)

- **S4** (supported in Duet 3 builds of RRF 3.5 and later) Load the grid definition and map of valid probe points from the specified file, default /sys/probePoints.csv

- **P"file.csv"** Optional file name for height map file or probe points file to save with **S3** or load with **S1** or **S4**.

- **Kn** (supported in RRF 3.01 and later only, default 0) Z probe number

##### Mesh.g

- In RRF 3.2 and later, if G29 is commanded with no S parameter, then file **sys/mesh.g** is run if it exists.

- In RRF 3.3 and later any parameters present are passed to mesh.g.

- If sys/mesh.g is not present then the command behaves like G29 S0.

### Examples

G29 S0 ; Probe the bed, save height map to "heightmap.csv" and enable mesh bed compensation G29 S3 P"usual.csv" ; Save the current height map to file "usual.csv" G29 S2 ; Disable mesh bed compensation G29 S1 P"usual.csv" ; Load height map file "usual.csv" and enable mesh bed compensation G29 S4 P"probePoints.csv" ; Load probe points file "probePoints.csv"

### Notes

- To define the probe grid, see M557.

- You can define a height to taper off the compensation using M376

- You can find more detailed information about setting up Mesh Bed Compensation here.

- To see the format of a height map file, generate one and then download it in DWC

- The S4 subfunction supports selective probing, such as probing a grid with holes in it. The probe points file (default /sys/probePoints.csv) needs to be manually created. To use:

  1.  Create a valid probe points file; the default file name is /sys/probePoints.csv. The format of a probe points file is similar to a height map file except for the following:

  - The first line must start with "RepRapFirmware probe points file v2" instead of "RepRapFirmware height map file v2" (the rest of the line is not processed)

  - The fourth and subsequent lines have the value 1 at points that are to be probed if they are reachable and 0 in points that are to be omitted.

  2.  Send an appropriate G29 S4 command, eg G29 S4 P"probePoints.csv".

  3.  When G29 S0 is called subsequently, the grid definition defined in the probe points file is used instead of the grid defined by M557, and reachable points are probed or not as indicated in the file.

