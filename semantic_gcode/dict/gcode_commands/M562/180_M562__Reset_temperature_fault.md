## M562: Reset temperature fault

### Parameters

- **Pnnn** Heater number

### Examples

M562 P2 ; Reset a temperature fault on heater 2

### Notes

If the heater has switched off and locked because it has detected a fault, this will reset the fault condition and allow you to use the heater again. Obviously to be used with caution. If the fault persists it will lock out again after you have issued this command. P0 is heater H0, P1 is heater H1, and so on.

In firmware 1.20 and later, M562 with no parameters will clear a heater fault on all heaters

