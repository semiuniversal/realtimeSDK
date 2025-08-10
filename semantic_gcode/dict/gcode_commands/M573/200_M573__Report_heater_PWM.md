## M573: Report heater PWM

Not supported in RRF 3.4 and later.

### Parameters

- **Pnnn** Heater number

### Examples

M573 P1

### Description

This gives a running average (usually taken over about five seconds) of the PWM to the heater specified by the P field. If you know the voltage of the supply and the resistance of the heater this allows you to work out the power going to the heater. Scale: 0 to 1.

In RRF 3.4 and later, if you need to find the average heater PWM, you can query the object model instead. The recommended replacement for M573 P1 is: echo heat.heaters\[1\].avgPwm

