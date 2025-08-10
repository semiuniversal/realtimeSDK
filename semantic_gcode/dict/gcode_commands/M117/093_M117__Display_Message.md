## M117: Display Message

### Examples

M117 Hello World M117 "Hello world"

This causes the given message to be shown in the status line on an attached LCD or if no LCD is attached, this message will be reported on the web interface. Quotation marks around the string to be displayed are recommended but not mandatory.

RRF \>= 3.2.0: All messages sent via M117 will be logged with log level INFO if logging is enabled at least at log level INFO.

Note: Due to the way M117 messages are communicated, messages sent in quick succession may not all display. Use M118 for those cases.

