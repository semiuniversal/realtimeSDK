## M291: Display message and optionally wait for response

Supported in firmware version 1.19 and later.

### Parameters

- **P"message"** The message to display, which must be enclosed in double quotation marks. If the message itself contains a double quotation mark, use two double quotation marks to represent it. Maximum length \<250 chars. Limited by total gcode length limit of 256 characters.

- **R"message"** Optional title for the message box. Must be enclosed in double quotation marks too. Maximum length 60 chars

- **Sn** Message box mode (see below), default 1

- **Tn** Timeout in seconds, only used for types 0, 1, and those with a cancel button (type 3 or higher with J1 or J2 parameter; the message box is cancelled upon timeout). The message will be cancelled after this amount of time if the user does not cancel it before then. A zero or negative value means that the message does not time out (it may still be cancelled by the user if it has a Cancel button). For modes 0 and 1 there is a default timeout of 10 seconds if no T parameter is provided. For other modes the default is no timeout.

- **X, Y, Z,,,** 0 = no special action (default), 1 = display jog buttons alongside the message to allow the user to adjust the head position on the specified axis. Only valid in with message box modes S2 and S3.

- **Jn** (RRF 3.5 and later only, optional) If message box mode \>= 4: 0 = no Cancel button (default), 1 = display a Cancel button (job/macro is cancelled immediately when pressed or when it times out); 2 (RRF 3.6.0 and later) = display a Cancel button (result variable is set to -1 when pressed or when timeout is reached).

- **K{"choice1","choice1",...}** (RRF 3.5 and later only) List of choices, required (and only used) when S=4.

- **Lnnn** (RRF 3.5 and later only, optional) Minimum accepted value (S=5 or S=6), or minimum number of characters (S=7).

- **Hnnn** (RRF 3.5 and later only, optional) Maximum accepted value (S=5 or S=6), or maximum number of characters (S=7).

- **Fnnn** or **F"text"** (RRF 3.5 and later only, optional) default choice number (counting from 0) when S=4, or default value when S\>=5.

### Description

This command provides a more flexible alternative to M117, in particular messages that time out, messages that suspend execution until the user acknowledges them, and messages that allow the user to adjust the height of the print head before acknowledging them.

Messages can be non-blocking, i.e. are for information and/or don't need interaction from the user, or blocking, i.e. require input from the user. Message box mode (S parameter) 0 and 1 are non-blocking, all others are blocking. Allowed message box modes are:

S0: No buttons are displayed (non-blocking) S1: Only "Close" is displayed (non-blocking) S2: Only "OK" is displayed (blocking, send M292 to resume the execution) S3: "OK" and "Cancel" are displayed (blocking, send M292 to resume the execution or M292 P1 to cancel the operation in progress) S4: Display a number of choices. The names of the choices are given by the K parameter as an array of strings. The choice selected by the user, as the array index, is available to be used in the "input" constant (blocking, RRF 3.5 and later only) S5: Prompt for an integer value. L is the minimum accepted value (default 0), H is the maximum accepted value (default unlimited), and F is the default value. The integer is available to be used in the "input" constant (blocking, RRF 3.5 and later only) S6: Prompt for a floating point value. L is the minimum accepted value (default 0.0), H is the maximum accepted value, and F is the default value. The floating point value is available to be used in the "input" constant (blocking, RRF 3.5 and later only) S7: Prompt for a string value. L is the minimum number of characters (default 1), H is the maximum number of characters (default 10), and F is the default value. The string is available to be used in the "input" constant (blocking, RRF 3.5 and later only)

### Notes

- The combination S0 T0 is not permitted, because that would generate a message box with no close button and that never times out, which would lock up the user interface.

- Duet Web Control 2.03 and later support HTML messages but those may not be displayed correctly on an attached PanelDue.

- When using Duet 3 with attached SBC, DSF versions before v3.1.1 support only non-blocking calls are supported in DuetSoftwareFramework. M291 is fully supported in DSF v3.1.1 and later.

- The limit in RRF 3.4 and later is 256 characters in the entire GCode command. Before 3.4 is was 200 characters, in RRF2 it's 160 characters.

- For message box modes 4 and higher The J parameter specifies whether a Cancel button is provided and what action is taken when that button is pressed or the timeout (see T parameter) expires. J1 causes execution of the entire file stack from which the M291 command was executed to be terminated. J2 (supported in RRF 3.6.0 and later) causes the message box to be cancelled but execution to continue as normal with **result** set to -1 and the value of **input** undefined. Therefore when J2 is used the value of **result** must be tested in the line that follows the M291 command.

### Examples

M291 R"Title" P"Message" K{"Yes","No"} S4 if (input == 1) echo "No chosen" M291 R"Title" P"Request for string" S7 L5 H40 F"default string" echo {input^" entered by user"}

