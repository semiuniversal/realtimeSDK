## M308: Set or report sensor parameters

M308 is supported in RepRapFirmware 3. If running RRF2.x or earlier, use M305.

### Parameters

- **Sn** Sensor number

- **P"pin_name"** The name of the control board pin that this sensor uses. For thermistors it is the thermistor input pin name, see Pin Names. For sensors connected to the SPI bus it is the name of the output pin used as the chip select.

- **Y"sensor_type"** The sensor and interface type. See tabs below. (Also "current-loop-pyro")

- **A"name"** Sensor name (optional), displayed in the web interface

- **Uu, Vv** (RRF 3.5 and later, optional, default zero) Temperature reading offset and slope adjustment parameters. The temperature in Â°C read from the sensor is adjusted as follows: adjustedReading = (rawReading \* (1.0 + v)) + u

• Thermistor

• PT1000

• PT100

• Thermocouple

• Temperature/Humidity/Pressure

• MCU/motor driver temperature

• Linear analog

• Duet 3 ADC daughterboard

##### Additional parameters for thermistors

- **Y"sensor_type"** The sensor and interface type: "thermistor"

- **Tnnn** (for thermistor sensors) Thermistor resistance at 25Â°C

- **Bnnn** Beta value, or the reciprocal of the Steinhart-Hart thermistor model B coefficient

- **Cnnn** Steinhart-Hart C coefficient, default 0

- **Rnnn** Series resistor value. Leave blank to use the default for your board.

- **Lnnn** ADC low offset correction, default 0

- **Hnnn** ADC high offset correction, default 0

##### Thermistor notes

- See also Connecting thermistors and PT1000 temperature sensors

##### Additional parameters for PT1000 sensors

- **Y"sensor_type"** The sensor and interface type: "pt1000"

- **Rnnn** Series resistor value. Leave blank to use the default for your board.

- **Lnnn** ADC low offset correction, default 0

- **Hnnn** ADC high offset correction, default 0

##### PT1000 notes

- See also Connecting thermistors and PT1000 temperature sensors

##### Additional parameters for MAX31865-based PT100 sensors

- **Y"sensor_type"** The sensor and interface type: "pt100"

- **Rnnn** Reference resistor value. Leave blank to use the default for your SPI daughterboard.

- **Wnnn** Number of wires used to connect the PT100 sensor (2, 3, or 4).

- **Fnn** (where nn is 50 or 60) The local mains frequency. Readings will be timed to optimise rejection of interference at this frequency.

##### PT100 notes

- See also Connecting PT100 temperature sensors

##### Additional parameters for MAX31856-based thermocouple sensors

- **Y"sensor_type"** The sensor and interface type: "thermocouple-max31855" or "thermocouple-max31856"

- **K"c"** The thermocouple type letter, default K

- **Fnn** (where nn is 50 or 60) The local mains frequency. Readings will be timed to optimise rejection of interference at this frequency.

##### Thermocouple notes

- See also Connecting thermocouples

##### Additional parameters for Temperature/Humidity/Pressure sensors

- **Y"sensor_type"** The sensor and interface type: "dht21", "dht22", "dht-humidity" - for DHT sensors "bme280", "bme-pressure", "bme-humidity" - BME280 sensors

- **P"nnn"** parameter for "dht-humidity", "bme-pressure" and "bme-humidity"

##### Temperature/Humidity/Pressure notes

- "dht11" is supported in firmware up to RRF 3.3, but removed from RRF 3.4 onward. DHT11 sensors are no longer recommened for new designs so replace them with a BME280 sensor instead.

- "bme280" is only supported in RRF 3.5 and later, and only on Duet 3 boards.

- DHT sensors provide a primary temperature output and an additional output providing humidity. To access the humidity output of a DHT sensor you must first configure the primary sensor of type "dht21" or "dht22". Then you can configure "dht-humidity" to be attached to the DHT sensor's secondary output, by specifying port P"Snnn.1" where **nnn** is the sensor number of the primary sensor.

- Similarly, BME280 sensors provide a primary temperature output and two additional outputs providing pressure and humidity. To access the additional output of a BME280 sensor you must first configure the primary sensor of type "bme280". Then you can configure sensor "bme-pressure" to be attached to the BME280 sensor's secondary output, by specifying port P"Snnn.1" where nnn is the sensor number of the primary sensor; and you can configure sensor "bme-humidity" to be attached to the BME280 sensor's secondary output by specifying port P"Snnn.2". If the BME280 is connected to a CAN-connected expansion board then you must also prefix the port name with the CAN address of that board, e.g. P"10.S20.1".

- See also Connecting digital humidity and temperature sensors.

&nbsp;

- **Y"sensor_type"** The sensor and interface type: "drivers" "mcu-temp" (see note below regarding "mcu-temp" support on Duet 3 Mini 5+) "drivers-duex" (only supported by Duet WiFi/Ethernet with an attached DueX2 or DueX5).

To read mcu and driver temperatures on an expansion board connected to a Duet 3 mainboard, put the CAN address at the start of a dummy P parameter. For example, a board at CAN address 1 would use:

M308 S12 Y"mcu-temp" P"1.dummy" A"3HC MCU" M308 S13 Y"drivertemp" P"1.dummy" A"3HC Steppers"

##### MCU/motor driver temperature notes

- The Trinamic drivers used on Duets do not report temperature, rather they report one of: temperature OK, temperature overheat warning, and temperature overheat error. RRF translates these three states into readings of 0C, 100C and 150C.

- mcu-temp on Duet 3 Mini 5+: The SAME54P20A chip used in the Duet 3 Mini 5+ does not have a functioning temperature sensor. In theory it does have an on-chip temperature sensor, but the errata document for the chip says it doesn't work. However, experimental support for the Duet 3 Mini 5+ on-chip MCU temperature sensor has been added in RepRapFirmware 3.3. As the chip manufacturer advises that it is not supported and should not be used, we can't promise that it will give useful readings on all boards. It will be removed if it causes significant support issues. Please report any issues in the \>Duet3D support forum.

- From RRF 3.4.0 "drivertemp" is changed to "drivers" to match the main board.

##### Additional parameters for linear analog sensors

- **Y"sensor_type"** The sensor and interface type: "linear-analog"

- **Fn** F0 = unfiltered (fast response), F1 = filtered (slower response, but noise reduced and ADC oversampling used to increase resolution). F1 is only available when using a port intended for thermistors, not when using a general input port.

- **Bnnn** The temperature or other value when the ADC output is zero

- **Cnnn** The temperature or other value when the ADC output is full scale

**Additional parameters for Duet 3 ADC daughterboard**

- **Y"sensor_type"** The sensor and interface type: "ads131.chan0.u" or "ads131.chan0.b" depending on whether unipolar or bipolar operation is required

- **P"pin_name"** **Channel 0**: "spi.cs0" if using a 6HC main board, "spi.cs1" for other main boards; except that if this daughter board is fitted on top of another Duet3D daughter board then add 2 to the cs number. **Channel 1**: "Sxx.1" where xx is the sensor number of the first channel (note you need to prepend the expansion board CAN address if the sensor is on an expansion board)

- **Bnnn** the reading required when the ADC reading is at minimum (typically with 0V output from the sensor). Defaults to 0 if not provided.

- **Cnnn** the reading required when the ADC reading is at maximum (typically with 10V output from the sensor). Defaults to 100 if not provided.

##### Duet 3 ADC daughterboard notes

- Duet3 ADC daughterboard sensors: "ads131.\*\*\*" are only supported in RRF 3.6 and later, and only on Duet 3 boards.

- See also Duet 3 ADC daughterboard.

### Notes

- This code replaces M305 in RepRapFirmware 3. In earlier versions of RepRapFirmware, sensors only existed in combination with heaters, which necessitated the concept of a "virtual heater" to represent a sensor with no associated heater (e.g. MCU temperature sensor). RepRapFirmware 3 allows sensors to be defined independently of heaters. The association between heaters and sensors is defined using M950.

- M308 can be used in the following ways:

  - **M308 Snn Y"type" \[other parameters\]**: delete sensor nn if it exists, create a new one with default settings, and configure it using the other parameters. At least the pin name must also be provided, unless the sensor doesn't use a pin (e.g. MCU temperature sensor).

  - **M308 Snn**: report the settings of sensor nn, this will also report the last error on that sensor if applicable

  - **M308 A"name"**: report the settings of the first sensor named "name"

  - **M308 Snn \[any other parameters except Y\]**: amend the settings of sensor nn

- Sensor type names obey the same rules as Pin Names, i.e. case is not significant, neither are hyphen and underscore characters.

- All Duets have some degree of auto-calibration to measure and cancel gain and offset errors in the analog-to-digital converters (ADC). The L and H parameters override auto-calibration. For more information on tuning Duet ADCs, see Connecting thermistors and PT1000 temperature sensors - When to calibrate.

- When converting from older versions of RRF to RRF3 you must replace each M305 command by a similar M308 command, which must be earlier in config.g than any M950 command that uses it. You must also use M950 to define each heater that you use, because there are no default heaters. Example - old code:M305 P0 T100000 B3950 ; bed heater uses a B3950 thermistor M305 P1 T100000 B4725 C7.06e-8 ; E0 heater uses E3D thermistor New code:M308 S0 P"bed_temp" Y"thermistor" T100000 B3950 ; define bed temperature sensor M308 S1 P"e0temp" Y"thermistor" T100000 B4725 C7.06e-8 ; define E0 temperature sensor M950 H0 C"bed_heat" T0 ; heater 0 uses the bed_heat pin, sensor 0 M950 H1 C"e0heat" T1 ; heater 1 uses the e0heat pin and sensor 1

