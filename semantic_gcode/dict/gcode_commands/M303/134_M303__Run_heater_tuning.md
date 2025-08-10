## M303: Run heater tuning

### Parameters

- **Hnnn** heater number (in RRF 3.2 and later, this parameter is optional if the T parameter is given)

- **Pnnn** PWM to use, 0 to 1 (you should normally use 1 i.e. full power), default 1

- **Snnn** target temperature

- **Tnnn** (RRF 3.2 and later, optional) Tool whose primary heater is to be tuned

- **Annn** (RRF 3.2 and later, optional) ambient temperature - use this parameter if you want to tune a heater that has been on and has not cooled down to ambient temperature yet

- **Ynn** (RRF 3.3 and later, optional) Tuning cycle hysteresis, default 5C. When tuning bed heaters that are slow to cool down, tuning will be faster if you use a lower value, provided that there is no noise in the temperature readings.

- **F**nn (RRF 3.3 and later) Fan PWM to use when the print cooling fan is turned on (ignored if the T parameter is not present), default 0.7 in RRF 3.4.0. Use a lower value if your printer uses a powerful print cooling fan that you do not normally run at full PWM.

- **Qn** (RRF 3.5 and later) Q0 (default) = display M307 parameters and suggestion to edit config.g or run M500 when tuning completes, Q1 = Quiet mode (do not display those messages). Use Q1 if you run M303 as part of a macro that saves the tuning result.

### Examples

M303 H1 P1 S240 ; tune heater 1 using 100% PWM, target temperature 240C M303 T0 S205 ; tune the primary heater of tool 0 (RRF 3.2 and later)

### Notes

PID Tuning refers to a control algorithm used to tune heating behaviour for hot ends and heated beds. This command computes the process model parameters (see Tuning heater temperature control.

Tuning is performed asynchronously. Run M303 with no parameters while a tuning is underway to see the current tuning state, or the last tuning result if the tuning process has already completed.

