## M591: Configure filament sensing

This command configures a given pin to read a filament sensor and configures filament monitoring for its corresponding extruder. The filament sensor may be a simple switch that detects the presence of filament, or a sensor that measures filament motion (e.g. laser, magnetic or pulsed filament monitor), or both.

In **RRF 3.4 and later** the action on a filament error is to raise a filament-error event. See Events.

In **RRF 3.3 and 3.2** the action on a filament error is to.

- pause the print

- run filament-error#.g if available, where \# is the extruder number

- failing that run filament-error.g if available

- failing that show a message on all available targets with the type of filament error and invoke system macro pause.g. The job is paused and will need manual intervention to resume the print.

**RRF 1.19 to 3.1.1** does not support filament-error macros. The action on a filament error is to enter the Pausing state, show a message on all available targets with the type of filament error, and invoke system macro pause.g. The job is paused and will need manual intervention to resume the print. Note that filament monitoring in RRF is only active when printing from SD card.

• M591 - RepRapFirmware 3.x

• M591 - RepRapFirmware 1.21 to 2.x

• M591 - RepRapFirmware 1.20 and earlier

##### Parameters

- **Dnn** Extruder drive number (0, 1, 2...)

- **Pnn** Type of sensor:

  - 0 = none

  - 1 = simple sensor (high signal when filament present)

  - 2 = simple sensor (low signal when filament present)

  - 3 = Duet3D rotating magnet sensor

  - 4 = Duet3D rotating magnet sensor with microswitch

  - 5 = Duet3D laser sensor

  - 6 = Duet3D laser sensor with microswitch

  - 7 = pulse-generating sensor

- **C"name"** Pin name the filament sensor is connected to (RRF3 only), see Pin Names. DueX2/5 users, see Notes below.

- **Sn** 0 = disable filament monitoring (default), 1 = enable filament monitoring when printing from SD card, 2 = enable filament monitoring all the time (S2 is supported RRF 3.5.0 and later ). Filament monitors accumulate calibration data (where applicable) even when filament monitoring is disabled.

**Additional parameters for Duet3D rotating magnet filament monitor**

- **Raa:bb** Allow the filament movement reported by the sensor to be between aa% and bb% of the commanded values; if it is outside these values and filament monitoring is enabled, the print will be paused

- **Enn** minimum extrusion length before a commanded/measured comparison is done, default 3mm

- **An** 1 = check All extruder motion, 0 (default) = only check extruder motion of printing moves (moves with both movement and forward extrusion)

- **Lnn** Filament movement per complete rotation of the sense wheel, in mm

**Additional parameters for Duet3D laser filament monitor**

- **Lnn** (firmware 3.2 and later) Calibration factor, default 1.0. The filament movement reported by the laser sensor is multiplied by this value before being compared with the commanded extrusion. Intended for use with sensors that use the laser to read movement of a wheel that is turned by the filament.

- **R, E, A** As for Duet3D magnetic filament monitor

**Additional parameters for a pulse generating filament monitor**

- **Lnn** Filament movement per pulse in mm

- **R, E** As for Duet3D laser filament monitor

##### Parameters

As RRF3, except 'C' parameter is the endstop number.

- **Cnn** Which input the filament sensor is connected to. On Duet electronics: 0=X endstop input, 1=Y endstop input, 2=Z endstop input, 3=E0 endstop input etc. DueX2/5 users, see Notes below.

##### M591 D0 P3 C3 S1 R70:130 L24.8 E3.0 ; Duet3D rotating magnet sensor for extruder drive 0 is connected to E0 endstop input, enabled, sensitivity 24.8mm.rev, 70% to 130% tolerance, 3mm detection length M591 D0 ; display filament sensor parameters for extruder drive 0

##### Parameters

- **Dnn** Extruder drive number (0, 1, 2...)

- **Pnn** Type of sensor, where:

  - 0 = none

  - 1 = simple sensor (high signal when filament present)

  - 2 = simple sensor (low signal when filament present)

  - 3 = Duet3D rotating magnet sensor

  - 4 = Duet3D rotating magnet sensor with microswitch

- **Cn** Which input the filament sensor is connected to. On Duet electronics: 0 = X endstop input, 1 = Y endstop input, 2 = Z endstop input, 3 = E0 endstop input etc. DueX2/5 users, see Notes below.

**Additional parameters for Duet3D rotating magnet filament monitor**

- **Snn** Sensitivity, in mm of filament movement per complete rotation of the sense wheel.

- **Rnn** Tolerance as a percentage of the commanded extrusion amount. A negative value puts the firmware in calibration mode.

- **Enn** minimum extrusion length before a commanded/measured comparison is done, default 3mm

##### M591 D0 P5 C3 R70:140 E3.0 S1 ; Duet3D rotating magnet sensor for extruder drive 0 is connected to E0 endstop input, sensitivity 1.05, tolerance 70% to 140%, 3mm detection length M591 D1 ; display filament sensor parameters for extruder drive 1

### Notes

- DueX2/5: Endstop inputs on the DueX expansion board (duex.e\[2-6\]stop in RRF 3.x, C5 thru C9 in RRF 2.x) can only be used for simple filament presence sensors (e.g. microswitch), not for sensors that detect motion (e.g. rotation or laser sensor). However, the endstop inputs on the Duet 2 WiFi/Ethernet CONN_LCD connector (connlcd.4 and connlcd.3 in RRF3.x, C10 and C11 in RRF 2.x) support any filament sensor.

- To free a filament sensor's GPIO pin, run M591 D# P0, where \# is the corresponding extruder.

### Documentation

- Duet3d Rotating Magnet Filament Monitor

- Duet3d Laser Filament Monitor

- Connecting and configuring filament-out sensors

