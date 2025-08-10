## M557: Set Z probe point or define probing grid

• Define G29 probe grid

• Define G32 probe points

##### Parameters

- **Xaaa:bbb** Minimum and maximum X coordinates to probe

- **Yaaa:bbb** Minimum and maximum Y coordinates to probe

- **X,Y,U,V,W,A,B,C...aaa:bbb** Minimum and maximum coordinates of an arbitrary axis (except Z) to probe (RRF \>=3.3)

- **Raaa** Radius to probe

- **Saaa** Probe point spacing (RepRapFirmware 1.19 and later also support **Saaa:bbb**)

- **Pnn** or **Pxx:yy** (RRF 2.02 and later) Number of points to probe in the X and Y axis directions (alternative to specifying the probe point spacing)

All values in mm.

##### M557 X0:200 Y0:220 S20 M557 X0:100 Y0:120 S50:60 M557 R150 S15

Notes

- In RRF 3.3 and later, it is possible to use an arbitrary axes pair for probing, e.g. X-A or U-C. When using **Raaa** to define a radius this will default to X-Y.

- For Cartesian printers, specify minimum and maximum X and Y values to probe and the probing interval. For Delta printers, specify the probing radius. If you define both, the probing area will be the intersection of the rectangular area and the circle.

- There is a firmware-dependent maximum number of probe points supported: RRF 3.5 - 961 (6HC/XD only, 31x31 grid) or 441 (Duet 3 Mini 5+ and Duet 2, 21x21 grid); RRF 3.4 - 441; RRF 1.x - 121 on the Duet 06/085 (enough for a 11x11 grid).

##### Parameters

Deprecated and not supported in firmware 1.18 and later. Cartesian/CoreXY printers only,

- **Pnnn** Probe point number

- **Xnnn** X coordinate

- **Ynnn** Y coordinate

##### M557 P1 X30 Y40.5

G32. Defining the probe points in this way is deprecated in RepRapFirmware, you should define them in a bed.g file instead.

