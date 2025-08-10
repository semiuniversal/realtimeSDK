## M118: Send Message to Specific Target

Supported in RepRapFirmware 1.21 and later.

### Parameters

- **Pnnn** Message type (0 = Generic \[default\], 1 = USB, 2 = PanelDue/UART, 3 = HTTP, 4 = Telnet, 5 = second UART, 6 = MQTT Client \[RRF 3.5 and later on WiFi-equipped Duet 3 boards only\]) (optional)

- **S"msg"** Message to send , limit of 100 characters

- **Lnnn** Log level of this message (0 = do not log this line, 1 = log as WARN, 2 = log as INFO, 3 = log as DEBUG (default)) (RRF 3.2 and later)

- **T"topic"** The topic to publish the message under (only valid on MQTT Client message).

- **Qnn** The QOS level of the message to publish, from 0 to 2 (only valid for MQTT Client message, optional). Defaults to 0 if not specified.

- **Rn** Set publish retain flag, 1 or 0 (only valid for MQTT Client message, optional). Defaults to 0 if not specified.

- **Dn** Set publish duplicate flag, 1 or 0 (only valid for MQTT Client message, optional). Defaults to 0 if not specified.

### Examples

M118 S"Hello Duet" M118 S"Hello Logfile" L1 M118 P0 S"Hello Logfile and DWC" L1 M118 S"Don't log me" L0 M118 S"My MQTT Message" T"My-MQTT-Topic"

This code may be used to send messages to a specific target. Basically it is a simple wrapper for RepRapFirmware's Platform::Message method.

Note that the implementation in RepRapFirmware always requires the S-parameter to be passed. If it is omitted, an error will be reported.

The second example shows how to send a message to the log file in log level WARN instead of the default log level DEBUG.

The third example shows how to prevent a message from being logged.

Note that a message only having the **Lnnn** parameter but no **Pnnn** parameter will only go to the log file (if the log level matches the current log level of the system) and will not be sent to other outputs. If you want it to show on DWC as well then send:

M118 P0 S"message" L1

**Note**: messages that exceed **100 characters** will be truncated.

