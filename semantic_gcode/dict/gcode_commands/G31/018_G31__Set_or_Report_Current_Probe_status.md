## G31: Set or Report Current Probe status

### Usage

- G31 Knn Pnnn Znnn \[Xnnn Ynnn ...\] \[Snnn Hnnn Tnnn:nnn\] ; RRF v3.3 and later

- G31 Kn Pnnn Znnn \[Xnnn Ynnn ...\] \[Snnn Hnnn Tnnn\] ; RRF v3.0 to v3.2

- G31 Pnnn Znnn \[Xnnn Ynnn ...\] \[Snnn Tnnn\] ; RRF v2.x and earlier

### Parameters

• RepRapFirmware v3.3 and later

• RepRapFirmware v3.0 to v3.2

• RepRapFirmware v2.x and earlier

- **Kn** Selects the Z probe number. If there is no K parameter then Z probe 0 is used.

- **Pnnn** Trigger value

- **Znnn** Trigger Z height in mm (default 0.7)

- **X,Y,U,V,W,A,B,C...nnn** Probe Offsets for all axes except Z1

- **Snnn** Calibration temperature2

- **Tnnn or Tnnn:nnn** Temperature coefficient3

- **Hnnn** Selects the sensor number (defined by M308) to use for temperature compensation when the S and T parameters are used.2

##### Notes

1 X,Y,U,V,W,A,B,C...nnn offsets of the Z probe relative to the print head reference point can be specified. This allows you to calculate your probe coordinates based on the geometry of the bed, without having to correct them for Z probe X,Y,U,V,W,A,B,C...nnn offset.

2 Optional parameter 'S' specifies the temperature in Â°C at which the specified Z parameter is correct. The default is current temperature. In RRF3 you must specify which temperature sensor to use in the 'H' parameter.

3 Optional parameter 'T' specifies one, or two, temperature coefficients of the Z parameter, default zero. This is useful for probes that are affected by temperature.

- If one parameter is specified, it is the variation in Z parameter height with the change in sensor temperature in mm/Â°C. The parameter is applied to the difference between current measured temperature and calibration temperature 'S'. For example, G31 Z1.2 T0.02 S20 H2 when sensor 2 measures 26C would calculate trigger height as 1.2 + 0.02x6 = 1.32mm

- If two parameters are specified, the first is the variation in Z parameter height with the change in sensor temperature in mm/Â°C, and the second is variation in Z parameter height with the square of temperature. The parameters are applied to the difference between current measured temperature and calibration temperature 'S'. For example, G31 Z1.2 T0.03:0.02 S20 H2 when sensor 2 measures 26C would calculate trigger height as 1.2 + 0.03x6 + 0.02x6x6 = 2.1mm

&nbsp;

- **Kn** Selects the Z probe number. If there is no K parameter then Z probe 0 is used.

- **Pnnn** Trigger value

- **Znnn** Trigger Z height

- **Xnnn** Probe X offset1

- **Ynnn** Probe Y offset1

- **Snnn** Calibration temperature2

- **Cnnn or Cnnn:nnn** Temperature coefficient3

- **Hnnn** Selects the sensor number (defined by M308) to use for temperature compensation when the C and S parameters are used.2

##### Notes

1 X and Y offsets of the Z probe relative to the print head reference point can be specified. This allows you to calculate your probe coordinates based on the geometry of the bed, without having to correct them for Z probe X and Y offset.

2 Optional parameter 'S' specifies the temperature in Â°C at which the specified Z parameter is correct. The default is current temperature. In RRF3 you must specify which temperature sensor to use in the 'H' parameter.

3 Optional parameter 'C' specifies one, or two (RRF v3.2), temperature coefficients of the Z parameter, default zero. This is useful for probes that are affected by temperature.

- If one parameter is specified, it is the variation in Z parameter height with the change in sensor temperature in mm/Â°C. The parameter is applied to the difference between current measured temperature and calibration temperature 'S'. For example, G31 Z1.2 C0.02 S20 H2 when sensor 2 measures 26C would calculate trigger height as 1.2 + 0.02x6 = 1.32mm

- If two parameters are specified (RRF v3.2), the first is the variation in Z parameter height with the change in sensor temperature in mm/Â°C, and the second is variation in Z parameter height with the square of temperature. The parameters are applied to the difference between current measured temperature and calibration temperature 'S'. For example, G31 Z1.2 C0.03:0.02 S20 H2 when sensor 2 measures 26C would calculate trigger height as 1.2 + 0.03x6 + 0.02x6x6 = 2.1mm

&nbsp;

- **Pnnn** Trigger value

- **Znnn** Trigger Z height

- **Xnnn** Probe X offset1

- **Ynnn** Probe Y offset1

- **Snnn** Calibration temperature2

- **Cnnn** Temperature coefficient3

- **Tnnn** (RRF 1.17 and later) Z probe type to which the S and C parameters apply, defaults to the current Z probe type as defined by M558 P parameter.4

##### M558 command to select the probe type before sending the G31 command, or use the T parameter.

### Examples

G31 P500 Z2.6 G31 X16.0 Y1.5 ; RRF 3.3 and later example of probe with thermistor and temperature compensation M558 P8 C"io2.in" H1 F1000 T6000 A3 ; Prusa PindaV2 Endstop M308 S2 P"temp2" A"Pinda V2" Y"thermistor" T100000 B3950 ; Prusa PindaV2 Thermistor G31 P500 X23 Y5 Z1.1 S21 H2 T0.02 ; Nozzle offset - Smooth Sheet

### Order dependency

A G31 command to set Z probe parameters must come after the M558 command that defines the Z probe. It must also come after M584 if it references any axes beyond X and Y (RRF \>=3.3).

### Notes

- When used on its own this reports whether the Z probe is triggered, or gives the Z probe value in some units if the probe generates height values. If combined with a Z and P field (example: G31 P312 Z0.7) this will set the Z height to 0.7mm when the Z-probe value reaches 312 when a G28 Z0 (zero Z axis) command is sent. The machine will then move a further -0.7mm in Z to place itself at Z = 0. This allows non-contact measuring probes to approach but not touch the bed, and for the gap left to be allowed for. If the probe is a touch probe and generates a simple 0/1 off/on signal, then G31 Z0.7 will tell the RepRap machine that it is at a height of 0.7mm (as configured by Z0.7 in this example) when the probe is triggered.

- If you are using the nozzle as a probe (for example with a peizo or switch that the hotend has a travel distance to trigger) then remember the Z offset may need to be negative (ie the probe triggers under Z0)

- Separate G31 parameters may be defined for different probe types (i.e. 0+4 for switches, 1+2 for IR probes and 3 for alternative sensors). To specify which probe you are setting parameters for, send a M558 command to select the probe type before sending the G31 command, or use the T parameter.

