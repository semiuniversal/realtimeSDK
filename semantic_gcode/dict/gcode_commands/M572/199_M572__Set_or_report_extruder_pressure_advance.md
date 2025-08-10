## M572: Set or report extruder pressure advance

### Parameters

- **Dnnn** Extruder number(s)

- **Snnn** Pressure advance amount (in seconds) to use for that extruder or extruders

### Examples

M572 D0 S0.1 ; set extruder 0 pressure advance to 0.1 seconds M572 D0:1:2 S0.2 ; set extruder 0, 1 and 2 pressure advance to 0.2 seconds (RepRapFirmware 1.20 and later)

### Description

This sets the pressure advance coefficient (S parameter) for the specified extruder (D parameter). Only one S value is allowed. If you wish to set different pressure advance for different extruders, use multiple M572 commands.

Pressure advance causes the extruder drive position to be advanced or retarded during printing moves by an additional amount proportional to the rate of extrusion. At the end of a move when the extrusion rate is decreasing, this may result in the extruder drive moving backwards (i.e. retracting). Therefore, if you enable this feature, you may need to reduce the amount of retraction you use in your slicing program to avoid over-retraction.

### Notes

- If you configure Input Shaping, you will need to retune your Pressure Advance. It is recommend to first tune Input Shaping, then Pressure Advance, then Retraction.

- When upgrading to RRF 3.6.0, when input shaping is used, pressure advance may need to be reduced compared to 3.5.x firmware.

- When enabling and configuring pressure advance, the extruder acceleration (M205 reports jerk in mm/s. For example, if a machine used extruder jerk of 50mm/s (3,000mm/min) at a PA of 0.02s, maximum extruder acceleration would be 50 / 0.02 = 2,500mm/s^2.

- For more details such as tuning the value see Pressure advance.

