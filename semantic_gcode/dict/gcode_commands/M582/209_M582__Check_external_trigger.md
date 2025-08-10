## M582: Check external trigger

### Parameters

- **Tnn** Trigger number to poll

- **Sn** (optional, RRF 3.5 and later only) 0 = only trigger if the input states are at the correct level (default), 1 = trigger unconditionally

### Examples

M582 T2 ; check levels of inputs that give rise to trigger \#2 M582 T3 S1 ; set trigger \#3 pending unconditionally

### Notes

Triggers set up by the M581 command are normally activated only when the specified inputs change state. This command provides a way of causing the trigger to be executed if the input is at a certain level. For each of the inputs associated with the trigger, the trigger condition will be checked as if the input had just changed from the opposite state to the current state. If the S1 parameter is used then the trigger will be activated unconditionally (RRF 3.5 and later only).

For example, if you use M581 to support an out-of-filament sensor, then M582 allows you to check for out-of-filament just before starting a print.

