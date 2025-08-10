## M594: Enter/Leave Height Following mode

Height following mode allows the Z position of the tool to be controlled by a PID controller using feedback from a sensor. See also M951 for configuration.

### Parameters

- **Pn** P1 = enter height following mode, P0 = leave height following mode

### Notes

If a movement command (e.g. G1) explicitly mentions the Z axis while height following mode is active, existing moves in the pipeline will be allowed to complete and the machine allowed to come to a standstill. Then height following mode will be terminated and the new move executed.

