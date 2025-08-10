## M309: Set or report heater feedforward

Supported in RepRapFirmware v3.4 and later

### Usage

- M309 Pn Saaa:bbb Tddd:eee:fff Aggg

### Parameters

- **Pn** Tool number

- **Saaa:bbb:ccc...** Feedforward PWM coefficients. The number of coefficients provided must equal the number of heaters configured for the tool when it was created (see M563).

- **Tddd:eee:fff...** Feedforward temperature increase coefficients. The number of coefficients provided must equal the number of heaters configured for the tool when it was created (see M563). Supported in RRF 3.6.0 and later.

- **Aggg** Feedforward advance time in milliseconds, maximum 100. RRF will attempt to apply the temperature and PWM adjustment this time in advance of the start of the corresponding move. This advance time may not always be achieved, for example when commencing movement from standstill. Supported in RRF 3.6.0 and later.

### Description

Heater feedforward allows for better regulation of heater temperature, when subjected to changing fan speeds or extrusion rates. RepRapFirmware supports a number of methods of heater feedforward:

- Fan speed to heater power feedforward is calibrated during heater tuning with M303, and stored in the M307 K parameter. This increase heater power, to maintain current temperature, as fan speed increases.

- Extrusion rate to heater power feedforward is configured by M309 S parameter. This increase heater power, to maintain current temperature, as extrusion rate increses.

- In RRF 3.6.0 and later, heater temperature feedforward is configured by M309 T and A parameters. This changes the temperature setpoint as extrusion rate changes, so temperature can be set lower when going slow, and higher when going faster.

Generally, heater feedforward is intended for high flow hot ends or pellet extruders. It's not normally needed on regular hot ends with a 0.4mm or similar size nozzle where the temperature drop caused by extrusion is less than 1C. Heater temperature feedforward is useful when there are big changes in extrusion speed through a job.

### Notes

- If the P parameter is not provided, the current tool is assumed. If the S, T and A parameters are not provided, the existing coefficients are reported.

- The units of S are PWM fraction (on a scale of 0 to 1) per mm/sec of filament forward movement.

- The units of T are degrees Celsius per mm/sec of filament forward movement.

- Feedforward is not applied to nonprinting moves, i.e. extruder moves only, with no other movement parameters. Typically these are retract, reprime, and filament loading moves.

- In RRF 3.6.0 and later, tool heater feedforward based on extrusion rate now works on heaters attached to CAN-connected expansion and tool boards.

- For calibration and examples, see the heater feedforward section of the 'Tuning the heater temperature control' wiki page.

