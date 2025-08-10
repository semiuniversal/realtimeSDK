## G32: Run bed.g macro

### Parameters

In RRF 3.3 and later any parameters will be passed to macro file bed.g.

### Examples

G32 ; execute macro bed.g

The firmware executes macro file **bed.g**. This macro normally uses G30 commands to probe the bed and then perform auto calibration of a delta printer (see Calibrating a delta printer), or perform bed levelling by moving the Z leadscrews independently, or display the manual corrections needed to the bed levelling screws.

For more detail on using G32 for automatic Delta calibration see: Calibrating a delta printer

For more detail on using G32 for automatic leveling of a cartesian or CoreXY see: Bed levelling using multiple independent Z motors

For more detail on using G32 for manual bed leveling assistant see: Using the manual bed levelling assistant

