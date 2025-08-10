## M957: Raise event

Supported in RepRapFirmware 3.4 and later for raising events

This command is used to raise an event or trigger internally as if the event had actually occurred, and execute any related handler macro for that event or trigger. Its main use is to test event handler and trigger macros.

### Parameters

- **E"type"** Event type name

- **Dnn** Device number to which the event relates

- **Bnn** (optional) CAN address of the board that the event should appear to originate from

- **Pnn** (optional) Additional data about the event (unsigned integer)

- **S"text"** (optional) Short test string to be appended to the event message

### Examples

M957 E"heater_fault" D1 B2

Raise a heater fault from expansion board at CAN address 2 on heater 1

### Notes

- **E** parameter: the event type names are firmware-dependent. In RepRapFirmware they are: heater-fault, driver-error, filament-error, driver-warning. However, in RRF 3.4.0 it is necessary to use underscore "\_" in place of dash "-" when using these event names in M957. Future versions of RRF will allow the dash character to be used instead but will still allow underscore for backwards compatibility.

- **D** parameter: the meaning of the device number depends on the event type. For a driver error it is the driver number. For a heater fault it is the heater number. For a filament error it is the extruder number.

- **P** parameter: (non-negative integer) additional information about the event, e.g. the subtype of a heater fault or a filament error. The meaning of the optional additional parameters also depends on the event type. For example, for a driver error it is the driver status.

- **S** parameter: the full text string describing the fault (the same string that is written to the log file, if the event is logged). This is intended to be suitable to show to the user.

- For more information, see the Events wiki page.

