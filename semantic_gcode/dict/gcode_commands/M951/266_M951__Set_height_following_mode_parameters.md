## M951: Set height following mode parameters

Supported in RepRapFirmware 3.x

Height following mode allows the Z position of the tool to be controlled by a PID controller using feedback from a sensor. See also M594.

### Parameters

- **Hnn** Sensor number

- **Pnn.n** Proportional factor, in mm per sensor unit

- **Inn.n** Integral factor, in mm per sensor unit per second

- **Dnn.n** Derivative factor, in mm per rate of change of sensor units (change in sensor unit per second)

- **Fnn.n** (optional) Sample and correction frequency (Hz), default 5Hz

- **Znn.n:nn.n** Minimum and maximum permitted Z values

### Notes

If commanding the motors to increase Z causes the sensor value to increase, then all of P, I and D must be positive. If commanding the motors to increase Z causes the sensor value to decrease, then all of P, I and D must be negative.

