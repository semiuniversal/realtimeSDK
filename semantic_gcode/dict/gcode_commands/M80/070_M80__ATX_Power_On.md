## M80: ATX Power On

### Parameters

- **C"port_name"** (RRF 3.4.0 and later) Name of the pin used to control the power supply

### Examples

M80 ; sets pin in the power on state M80 C"pson" ; allocates the pin and sets the pin in the power on state. M80 C"!pson" ; inverts the PS_ON output for Meanwell power supplies

Turns on the ATX power supply from standby mode to fully operational mode using the power supply control pin on the External 5V header. If a deferred power down command was set up using M81 S1 then it is cancelled.

In RRF 3.4.0 and later, M80 will do nothing unless you have previously allocated a pin to control power using either M80 or M81 with C parameter. This would normally be done in the config.g file.

