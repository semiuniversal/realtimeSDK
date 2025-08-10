## M307: Set or report heating process parameters

• RRF 3.4 and later

• RRF 3.3 and 3.2

• RRF 3.1 and 3.0

• RRF 2.x and 1.20 and later 1.x

##### Parameters

- **Hn** Heater number (0 is usually the bed heater)

- **Rnnn** Heating rate in degC/sec at full power when the heater temperature is close to ambient (RRF 3.2 and later)

- **Dnnn** Dead time in seconds

- **Ennn** Exponent of the cooling rate curve, default 1.35. Used in conjunction with the K parameter (RRF 3.4 and later)

- **Knnn** or **Knnn:nnn** Cooling rate in degC/sec when the heater is 100C above ambient. If one value is given then the cooling rate is calculated as K/((Th-Ta)/100)^E where Th is the heater temperature and Ta is the ambient temperature. If two values are given then the cooling rate is calculated as K\[0\]/((Th-Ta)/100)^E + K\[1\]/((Th-Ta)/100)^E\*F where F is the fan PWM in the range 0 to 1. (RRF 3.4 and later)

**Additional parameters to help control the heating process:**

- **Bn** selects Bang-bang control instead of PID if non-zero. Default at power-up is 0 for extruder heaters, 1 for the bed heater.

- **Innn** Invert PWM signal (I0 = not inverted, I1 = invert PWM/bang-bang signal for inverted temperature control \[e.g. with Peltier elements\])

- **Snnn** maximum PWM to be used used with this heater on a scale of 0 to 1. Default 1.0.

- **Vnnn** VIN supply voltage at which the R parameter was calibrated. This allows the PID controller to compensate for changes in supply voltage. A value of zero disables compensation for changes in VIN voltage. Supply voltage compensation is applied to hot end heaters only, not to bed or chamber heaters.

##### M307 H0 ; report the process parameters for heater 0 M307 H1 R2.186 K0.17:0.11 D5.67 S1.00 V24.0 ; set the process parameters for heater 1

Notes (RRF 3.4 and later)

- The K parameter is the rate of cooling in degC/sec when the heater is turned off and the temperature is falling through 100C above ambient temperature. The K parameter is calculated as: K = ( temperature change / time in seconds ) / (( heater temperature - ambient temperature ) / 100 )^E parameter The K parameter can take a second value to allow RRF to calculate the heater cooling rate with the cooling fan on. K\[fan\] = ( temperature change / time in seconds ) / (( heater temperature - ambient temperature ) / 100)^E parameter \* F (fan PWM in the range 0 to 1) The second K value is the additional cooling rate due to the fan running at full PWM.

- The C parameter is deprecated in RRF 3.4.0 and later in favour of the K and E parameters, however existing M307 commands using C and/or A parameters will continue to work.

- See notes on previous RRF 3.x tabs for all changes since RRF 2.x.

##### Parameters

- **Hn** Heater number (0 is usually the bed heater)

- **Rnnn** Heating rate in degC/sec at full power when the heater temperature is close to ambient (RRF 3.2 and later)

- **Cnnn** or **Caaa:bbb** dominant time Constant of the heating process in seconds. If two values are provided (supported in RRF 3.2 and 3.3), the first value is with the fan off and the second is with the fan on at full PWM.

- **Dnnn** Dead time in seconds

**Additional parameters to help control the heating process:**

- **Bn** selects Bang-bang control instead of PID if non-zero. Default at power-up is 0 for extruder heaters, 1 for the bed heater.

- **Innn** Invert PWM signal (I0 = not inverted, I1 = invert PWM/bang-bang signal for inverted temperature control \[e.g. with Peltier elements\]

- **Snnn** maximum PWM to be used used with this heater on a scale of 0 to 1. Default 1.0.

- **Vnnn** VIN supply voltage at which the R parameter was calibrated (RepRapFirmware 1.20 and later). This allows the PID controller to compensate for changes in supply voltage. A value of zero disables compensation for changes in VIN voltage. Supply voltage compensation is applied to hot end heaters only, not to bed or chamber heaters.

##### M307 H0 ; report the process parameters for heater 0 M307 H1 R2.186 C202.1:155.0 D5.67 S1.00 V24.0 ; set the process parameters for heater 1

Notes (RRF 3.2 and 3.3)

- The A parameter is deprecated in RRF 3.2 and later in favour of the R parameter, however existing M307 commands using the A parameter will continue to work.

- See notes on previous RRF 3.x tabs for all changes since RRF 2.x.

##### Parameters

- **Hn** Heater number (0 is usually the bed heater)

- **Annn** gAin, expressed as ultimate temperature rise obtained in degC divided by the PWM fraction. For example, if G=180 then at 50% PWM the ultimate temperature rise would be 90C.

- **Cnnn** dominant time Constant of the heating process in seconds.

- **Dnnn** Dead time in seconds

**Additional parameters to help control the heating process:**

- **Bn** selects Bang-bang control instead of PID if non-zero. Default at power-up is 0 for extruder heaters, 1 for the bed heater.

- **Innn** Invert PWM signal (I0 = not inverted, I1 = invert PWM/bang-bang signal for inverted temperature control \[e.g. with Peltier elements\])

- **Snnn** maximum PWM to be used used with this heater on a scale of 0 to 1. Default 1.0.

- **Vnnn** VIN supply voltage at which the A parameter was calibrated (RepRapFirmware 1.20 and later). This allows the PID controller to compensate for changes in supply voltage. A value of zero disables compensation for changes in VIN voltage. Supply voltage compensation is applied to hot end heaters only, not to bed or chamber heaters.

##### M307 H0 ; report the process parameters for heater 0 M307 H1 A346.2 C140 D5.3 B0 S0.8 V23.8; set process parameters for heater 1, use PID, and limit heater 1 PWM to 80%

Notes

- The F parameter is no longer supported. Use M950 to set the frequency in the M950 command that you use to define the heater.

- The I2 parameter is no longer supported, and I3 does the same as I1. You can use M950 to invert the output.

- You can no longer disable a heater using M307 A-1 C-1 D-1. To use the pin for something else, don't create a heater on that pin.

Example:

;RRF 2.x code M307 H0 F100 ; change heater 0 PWM frequency to 100Hz M307 H2 A-1 C-1 D-1 ; disable heater 2 so we can use its pin to drive a fan ;RRF 3.x code M950 H0 C"bed_heat" Q100 T0 ; heater 0 uses the bed_heat pin, sensor 0, PWM frequency 100Hz ; No need to disable heater 2 because we didn't define it in the first place

##### Parameters

- **Hn** Heater number (0 is usually the bed heater)

- **Annn** gAin, expressed as ultimate temperature rise obtained in degC divided by the PWM fraction. For example, if G=180 then at 50% PWM the ultimate temperature rise would be 90C.

- **Cnnn** dominant time Constant of the heating process in seconds.

- **Dnnn** Dead time in seconds

**Additional parameters to help control the heating process:**

- **Bn** selects Bang-bang control instead of PID if non-zero. Default at power-up is 0 for extruder heaters, 1 for the bed heater.

- **Innn** Invert PWM signal (I0 = not inverted, I1 = invert PWM/bang-bang signal for inverted temperature control \[e.g. with Peltier elements\], I2 = full PWM signal inversion, I3 = both I1 and I2)

- **Snnn** maximum PWM to be used used with this heater on a scale of 0 to 1. Default 1.0.

- **Vnnn** VIN supply voltage at which the A parameter was calibrated (RepRapFirmware 1.20 and later). This allows the PID controller to compensate for changes in supply voltage. A value of zero disables compensation for changes in VIN voltage. Supply voltage compensation is applied to hot end heaters only, not to bed or chamber heaters.

- **Fnnn** PWM frequency to use

##### Notes (RRF 2.x and 1.20 and later 1.x)

- RepRapFirmware 1.16 and later allow the PID controller for a heater to be disabled by setting the A, C and D parameters to -1. This frees up the corresponding heater control pin for use as a general purpose I/O pin to use with the M42 or M280 command. Example: M307 H2 A-1 C-1 D-1.

### Order dependency

- **RRF 3.x**: The M307 command must come later in config.g than the M950 command that created the heater number it refers to.

### Notes

Each heater and its corresponding load may be approximated as a first order process with dead time, which is characterised by the gain, time constant and dead time parameters. The model can used to calculate optimum PID parameters (including using different values for the heating or cooling phase and the steady state phase), to better detect heater faults, and to calculate feed-forward terms to better respond to changes in the load. Normally these model parameters are found by auto tuning - see Tuning heater temperature control.

For those platforms that provide power voltage monitoring, the calibration voltage setting allows the heating controller to adjust the power automatically in response to changes in the power supply voltage. For example, if a bed or chamber heater is turned on or off, this may cause the power supply voltage to change a little, which if not corrected for would change the extruder heater power.

