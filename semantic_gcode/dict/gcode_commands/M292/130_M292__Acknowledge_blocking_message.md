## M292: Acknowledge blocking message

**Caution**: this command is intended to be used by user interfaces only.

### Parameters

- **Pnnn** Whether the current operation shall be cancelled (P=1) or continued (P=0)

- **R{expression}** (RRF 3.5 and later, only present if P=0 and the message box mode was 4 or greater) The returned value. For message box mode 4 this is an integer representing the choice that was selected, counting from 0. For message box modes 5/6/7 this is the integer/float/string value that was entered.

- **Snnn** (RRF 3.5 and later) The sequence number of the message being acknowledged

This command is sent by the user interface when the user acknowledges a message that was displayed because of a M291 command with parameter S=2 or S=3. DWC and PanelDue 3.5 and later also use thie command to acknowledge a non-blocking message (M291 command with parameter S=0 or S=1) but in that case the S parameter must match the sequence number of the message being acknowledged. The P parameter is ignored unless M291 was called with S=3, and always ignored by RRF 3.5 and later if the R parameter is present.

In RRF versions prior to 3.5, M292 may only be used to acknowledge blocking message boxes. RRF 3.5 and later allow M292 to be used to cancel non-blocking message boxes too, provided that the correct sequence number is specified.

Supported in firmware version 1.19 and later.

