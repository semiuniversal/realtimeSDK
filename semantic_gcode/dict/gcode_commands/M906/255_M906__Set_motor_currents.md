## M906: Set motor currents

Sets the peak currents to send to the stepper motors for each axis. The values are in milliamps.

### Parameters

- **Xnnn** X drive peak motor current

- **Ynnn** Y drive peak motor current

- **Znnn** Z drive peak motor current

- **Ennn** E drive(s) peak motor current(s)

- **Innn** Motor current idle factor (0..100)

- **Tnnn** Idle time-out in seconds (RRF 3.6.0 and later)

### Order dependency

This command must be later in config.g than any M584 command.

### Examples

M906 X300 Y500 Z200 E350:350

### Notes

- RRF uses peak current. Divide by 1.414 for RMS current as used in Marlin implementations for Trinamic drivers

- Current setting on the various Duet boards are as follows:

  - Duet 2 WiF/Ethernet is done in steps of 100mA and is rounded down.

  - Duet Maestro is in steps of 50mA and rounded down.

  - Duet 3 MB6HC and EXP3HC is in steps of 26.2mA.

  - Duet 3 Mini5+ is in steps of 74mA (provisionally), rounded down.

  - Duet 3 1LC toolboard is in steps of 50mA, rounded down.

- The **I** parameter is the percentage of normal that the motor currents should be reduced to when the printer becomes idle but the motors have not been switched off. The default value is 30% and will always be at least 100mA - starting from RRF 2.02 setting it to 0 will disable the steppers after timeout like M18\|M84 do and if an axis is related to the motor, throw out the "homing" of it, since it is likely that the position cannot be precisely determined anymore. Note that the idle current is applied globally for all motors and cannot be set per axis.

- Every driver that is assigned must have its current set using M906. Not setting a current will default a low current (approx 1/32 of the driver max current), however M906 will report 0 until a current is assigned. Disable the driver explicitly if you do not want any current sent to a driver that is assigned.

- As a rule of thumb, the recommendation is to set M906 to use 60-85% of the rated maximum current for the motor. Though you can go above or below as needed, and will have to tune for a balance of motor temperature, motor torque, and noise level. You can also use the EMF calculator (\>reprapfirmware.org and click on EMF calculator) to play with different values to see how it changes behaviour.

- The **T** parameter (RRF 3.6.0 and later) is used to set the idle timeout for all motors (M84 was previously used for this). For example, M906 T10 will idle the stepper motors after 10 seconds of inactivity. Setting M906 T0 does NOT mean "never idle hold" (ie motors stay on all the time, at full current), and T0 is an invalid setting. The correct way to set no idle hold (ie motors are 'always on') is to use M906 I parameter to set the idle hold to the required level, eg M906 I100.

- RepRapFirmware does not support individual motor settings where an axis has multiple motors connected to different stepper drivers. The first parameter specified will be used for all motors on the axis. You should use identical motors on any axis that has more than one motor to avoid unexpected behaviour. Example: If you have two motors on your Z axis, physically connected to Z and E0 stepper drivers, configured with M584 Z2:3, set M906 Z200, not M906 Z200:200

- When using external drivers, the motor current (M906) is not controlled by firmware configuration. It is set by the external stepper driver, usually using jumpers.

