## M569: Set motor driver direction, enable polarity, mode and step pulse timing

### Parameters

- **Pnnn** Motor driver number

- **Snnn** Direction of movement of the motor(s) attached to this driver: 0 = backwards, 1 = forwards (default 1)

- **Rnnn** Driver enable polarity: 0 = active low, 1 = active high, -1 = driver is always disabled and is not monitored (default 0)

- **Tnnn** (firmware 1.14 and later) Minimum driver step pulse width and interval in microseconds

- **Taa:bb:cc:dd** (firmware 1.21 and later) Minimum driver step pulse width, step pulse interval, direction setup time and direction hold time, in microseconds (only applies to external drivers connected to Duet 2, Duet 3 Mini 5+, Duet 3 MB6XD and Duet 3 Expansion 1XD)

- **Dnn** (firmware 2.0 and later, only applies to TMC2660, TMC22xx, TMC2160 and TMC5160 stepper drivers) Driver mode: 0=constant off time, 1=random off time (TMC2660 drivers only), 2=spread cycle, 3=stealthChop (mode 3 for TMC22xx/TMC2160/TMC5160 only), 4=Closed Loop, 5=Assisted open loop (modes 4 and 5 are only for Duet 3 closed loop controllers and motors such as the Motor23CL). The default is spreadCycle for all drivers from RRF 3.4, and stealthChop2 for TMC22xx in RRF 3.3 and earlier. In stealthChop mode the drivers will switch over to spreadCycle automatically at high speeds, see the V parameter.

- **Fnn** (firmware 2.02 and later) Off-time in the chopper control register, 1 to 15

- **Cnnnn** (firmware 2.0 and later, only applies to TMC2660, TMC22xx, TMC2160 and TMC5160 stepper drivers) Lowest 17 bits of the chopper control register value.

- **Bnn** (firmware 2.02 and later) Blanking time (tbl) in the chopper control register, 0 to 3. See the TMC driver datasheet.

- **Hnn** (firmware 2.02 and later) thigh parameter for those stepper driver chips that support it, e.g. TMC5160 and TMC2160. Send M569 P# (where \# is the driver number) with no additional parameters to see how this translates into mm/sec. See also the V parameter.

- **Yaa:bb** or **Yaa:bb:cc** (firmware 2.02 and later) Hysteresis start, end and decrement values in the chopper control register. See the TMC driver datasheet for the meaning.

- **Vnnn** (firmware 2.02 and later) tpwmthrs parameter for those stepper driver chips that support it. This is the interval in clock cycles between 1/256 microsteps below which the drivers will switch from stealthChop to to spreadCycle mode. Only applies when the driver is configured in stealthChop mode. Typical value are from 100 (high speed) to 4000 (low speed). Send M569 P# (where \# is the driver number) with no additional parameters to see how this translates into mm/sec.

- **Unn** (firmware 3.6.0 onwards) for stepper drivers that support globalscaler (TMC5160/2160). This is the maximum value to use for iRun current scaler, 0-31. If not set (and in older firmware versions), this is set to 31 and globalscaler is calculated, otherwise iRun will be set to the value specified. However if the target current can't be reached by reducing globalscaler alone, iRun, and iHold, are also reduced, likewise if the target current is high then iRun and iHold may be increased to achieve it. This means iRun and iHold may be set different than specified to ensure the requested current is applied to the motors, sending M569 Px can be used to verify the iRun value used and the calculated current the driver will actually apply to the motor. Setting iRun directly can allow setting hysteresis start/end values that are more suitable for specific motors, resulting in lower noise. In theory this should only be needed when using low inductance motors, or a high motor supply voltage (e.g. 48V). You can use the excel calculator provided by TMC to help tune iRun and hysteresis values.

### Examples

M569 P0 S0 ; reverse the direction of the motor attached to driver 0 M569 P5 R1 T2.5:2.5:5:0 ; driver 5 requires an active high enable, 2.5us minimum step pulse, 2.5us minimum step interval, 5us DIR setup time and no hold time

### Notes

- If no T parameter is given, then on boards having internal drivers the step pulse width and interval are guaranteed to be suitable for the on-board drivers only, and will generally be too fast for external drivers. On the EXP1XD board the default is T2.7:2.7:2.7:2.7. On the MB6XD board the default is T2.5:2.5:2.5:2.5.

- The T values get rounded up to the next highest value supported by the firmware. So the values reported back may be a little higher than you requested.

- **RepRapFirmware takes the highest T parameters seen in any M569 command, and applies those values to all drivers for which any nonzero T parameter was specified.** So if you want to reduce the T parameters, you will need to do that on all drivers that already have nonzero T parameters. On the MB6XD this means that if you want to reduce the T values below the defaults, you need to do this on all six drivers even if you are not using all of them. Additionally, on all main boards except for the MB6XD, if you reduce the T parameters then you must restart the firmware for the change to take effect. On Duet 3 systems with CAN-connected expansion boards this note applies separately to each board. It does not apply to the EXP1XD because that board has only one driver.

- Some versions of RepRapFirmware prior to 1.14 also provided XYZ and E parameters to allow the mapping from axes and extruders to stepper driver numbers to be changed. From 1.14 onward, this functionality is provided by M584 instead.

