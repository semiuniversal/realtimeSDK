## M570: Configure heater fault detection

• RRF 3.5 and later

• RRF 3.4.0 to 3.4.3

• RRF 3.3 and earlier

- **Hnnn** Heater number

- **Pnnn** Time in seconds for which a temperature anomaly must persist on this heater before raising a heater fault (default 5 seconds)

- **Tnnn** Permitted temperature excursion from the setpoint for this heater (default 15C)

- **Rn** (RRF 3.5 and later only) Maximum number of consecutive temperature reading failures before a heater fault is raised. The default is 3 which guarantees that a fault will be raised within one second of a sensor becoming disconnected or shorted. Using R0 will result in a heater fault being raised immediately when a sensor fails to deliver a sensible reading, but will make the system more likely to report spurious failures if the sensor or its wiring is subjected to electrical interference or ESD.

The actions taken on a heater fault, after the heater is shutdown, are now handled by the

- **Hnnn** Heater number

- **Pnnn** Time in seconds for which a temperature anomaly must persist on this heater before raising a heater fault (default 5 seconds)

- **Tnnn** Permitted temperature excursion from the setpoint for this heater (default 15C)

The actions taken on a heater fault, after the heater is shutdown, are now handled by the

**Parameters for RepRapFirmware 1.15e to 3.3**

- **Hnnn** Heater number

- **Pnnn** Time in seconds for which a temperature anomaly must persist on this heater before raising a heater fault (default 5 seconds)

- **Tnnn** Permitted temperature excursion from the setpoint for this heater (default 15C)

- **Snnn** (RRF versions between 1.20 and 3.3 inclusive only) Integer timeout in minutes (can be set to 0) for print to be cancelled after heater fault. If the S parameter timeout occurs (which only happens if a SD print is in progress), RRF will also try to turn off power via the PS_ON pin.

**Parameters for RepRapFirmware 1.14 and earlier**

- **Snnn** Heater timeout (in seconds)

### Order dependency

When using RepRapFirmware 3 the M570 command must come later in config,g than the M950 command that creates the heater specified in the H parameter.

### Examples

M570 H1 P4 T15 ; An anomaly on heater 1 must persist for 4 seconds, and must be greater or less than 15C from the setpoint, to raise a heater fault.

### Notes

**Warning!** Heating fault detection is provided to reduce the risk of starting a fire if a dangerous fault occurs, for example if the heater cartridge or thermistor falls out of the heater block. You should carefully consider sensible values for the detection time or permitted temperature excursion, setting them incorrectly will reduce the protection. Also note that this protection should not be relied upon exclusively. Protection against fire should be provided external to the operation of the firmware as well (fuses, fire detection, do not print unattended etc)

For further details about heater fault handling see Heater faults and how to avoid them

