## M81: ATX Power Off

### Parameters

- **C"port_name"** (RRF 3.4.0 and later) Name of the pin used to control the power supply

- **Sn** n=0 turn power off immediately (default), n=1 turn power off when all thermostatic fans have turned off (RepRapFirmware 1.20 and later only). This parameter optional and ignored if the D parameter is present. The default is to turn off power as soon as the movement queue is empty.

- **Dnnn** Delay powering down for nnn seconds (RRF 3.5 and later only)

### Examples

M81 C"pson" ; allocate the PS_ON pin to power control but leave power off M81 ; turn power off immediately M81 S1 ; turn power off when all thermostatic fans have turned off M81 D30 S1 ; turn power off after 30 seconds or when all thermostatic fans have turned off, whichever happens later (RRF 3.5)

Turns off the ATX power supply. Counterpart to M80. A deferred power down command (M81 S1) that has not yet happened can be cancelled using M80.

In RRF 3.4 and later, M81 will have no effect unless a power control pin has previously been assigned using M80 or M81 with the C parameter. This would normally be done in the config.g file.

