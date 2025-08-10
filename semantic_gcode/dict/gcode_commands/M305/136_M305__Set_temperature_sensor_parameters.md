## M305: Set temperature sensor parameters

RepRapFirmware 3: Use M308 instead (see Notes).

### Parameters

- **Pnnn** Heater number (0, 1, 2...) or virtual heater number (100, 101, 102...)

- **S"name"** Heater name (optional). Named virtual heaters are shown in Duet Web Control; anonymous virtual heaters are not.

- **Xnnn** Heater ADC channel, or thermocouple or PT100 adapter channel; defaults to the same value as the P parameter

- **Tnnn** (for thermistor sensors) The thermistor resistance at 25oC

- **T"c"** (for MAX31856-based thermocouple sensor daughter boards) The thermocouple type letter, default K

- **Bnnn** If the sensor is a thermistor, this is the Beta value. For the Steinhart-Hart thermistor model, this is the reciprocal of the B coefficient

- **Cnnn** If the sensor is a thermistor, this is the Steinhart-Hart C coefficient, default 0

- **Rnnn** If the sensor is a thermistor or PT1000 sensor, this is the Series resistor value, see here for more information: M305 R parameter.

- **Lnnn** If the sensor is a thermistor, this is the ADC low offset. If it is a current loop sensor, this is the temperature when the current is 4mA.

- **Hnnn** If the sensor is a thermistor, this is the ADC high offset. If it is a current loop sensor, this is the temperature when the current is 20mA.

- **Fnn** (where nn is 50 or 60) If the sensor interface uses a MAX31856 thermocouple chip or MAX31865 PT100 chip, this is the local mains frequency. Readings will be timed to optimise rejection of interference at this frequency.

- **Wn** Configure number of wires used to connect PT100 sensor. Should be \[2..4\].

### Examples

M305 P1 T100000 R1000 B4200

### Description

Sets the parameters for temperature measurement. The example above tells the firmware that for heater 1 (P parameter: 0 = heated bed, 1 = first extruder) the thermistor 25C resistance (T parameter) is 100Kohms, the thermistor series resistance (R parameter) is 1Kohms, the thermistor beta (B parameter) is 4200. All parameters other than P are optional. If only the P parameter is given, the existing values are displayed. DuetWebControl 1.19.2 and newer support optional units to be set by the S parameter in the form of "Heater name \[Unit\]".

### Notes

**Notes - RepRapFirmware 3**

Prior to RRF3, every temperature sensor belongs to a heater. For sensors with no controllable heater (e.g. the MCU temperature sensor) you have to create a "virtual heater" in order to be able to use the sensor. In RRF3, sensors are created and configured independently from heaters, using the M308 command. When creating a heater using M950, you tell it which sensor to use. You must create the sensor before you refer to it in a M950 command. M305 is not used.

**Notes - RepRapFirmware 2.x and earlier**

RepRapFirmware also supports ADC gain and offset correction and a thermistor selection facility. Example:

M305 P1 T100000 R1000 B4200 H14 L-11 X2

The H correction affects the reading at high ADC input voltages, so it has the greatest effect at low temperatures. The L correction affects the reading at low input voltages, which correspond to high temperatures. The ADC on the Duet 2 WiFi and Duet 2 Ethernet is self-calibrating, so you should not need to provide any corrections when using these controllers.

The X parameter tells the firmware which temperature sensor channel to use channel, as follows:

- Channels 0, 1... are the thermistor inputs for heaters 0, 1 etc.

- Channels 100, 101... are MAX31855 thermocouple channels using chip selects CS1, CS2... on the SPI bus, see Connecting thermocouples.

- Channels 150, 151... are MAX31856 thermocouple channels using chip selects CS1, CS2... on the SPI bus

- Channels 200, 201... are MAX31865 PT100 channels using chip selects CS1, CS2... on the SPI bus, see Connecting PT100 temperature sensors.

- Channels 300, 301... are current loop channels using chip selects CS1, CS2... on the SPI bus

- Channels 400, 401... are DHTxx temperature channels. The DATA line of the DHTxx must be connected to one of pins CS1, CS2... on the SPI bus. Specify the sensor type (11 for DHT11, 21 for DHT21 or 22 for DHT22) via the T-parameter. e.g. M305 P102 X401 T22 S"DHT temperature"

- Channels 450, 451... are as 400, 401... but specify the corresponding humidity sensor of the DHTxx

- Channels 500, 501... are the thermistor inputs, but configured for PT1000 sensors rather than thermistors. Only the R, H and L parameters are significant, see example below.

- Channel 1000 is the on-chip microcontroller temperature sensor

- Channel 1001 represents the temperature warning and overheat flags on the TMC2660, TMC2224 or other smart drivers on the Duet main board. It reads 0C when there is no warning, 100C if any driver reports over-temperature warning , and 150C if any driver reports over temperature shutdown.

- Channel 1002 is as channel 1001 but for drivers on the Duex 2 or Duex 5 expansion board.

If the M305 command for a real heater does not specify a sensor channel and the heater has not been configured yet, then it defaults to using the thermistor associated with that heater.

PT1000 Example:

M305 P1 X501 R2200 ; heater 1 uses a PT1000 connected to thermistor channel 1 which has a 2.2K series resistor (i.e a Duet 2 Maestro)

Note: PT1000 sensors connected to thermistor inputs have lower resolution than PT100 sensors connected via the PT100 daughter board. The accuracy of PT1000 sensors should be very good on the Duet 2 Maestro and generally good on the Duet 2 Wifi and Duet 2 Ethernet. See the PT1000 documentation for more details.

Virtual heaters 100, 101 and 102 are preconfigured to use temperature sensor channels 1000, 1001 and 1002 respectively. We suggest you use virtual heaters 103 upwards if you want to create additional virtual heaters.

If you send the following command:

M305 P101

you should get the response "Heater 101 uses TMC2660 temperature warnings sensor channel 1001". But as this virtual heater has no name, it doesn't show up in DWC. You can fix that by sending:

M305 P101 S"Drivers"

After that, if you go to the "Extra" tab in DWC (where is says Tools/Heaters/Extra), you will see "Drivers" as an entry.

