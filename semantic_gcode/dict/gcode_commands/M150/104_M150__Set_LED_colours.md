## M150: Set LED colours

• RRF 3.5 and later

• RRF 3.4 and earlier

##### Parameters

- **Rnnn** Red component, 0-255

- **Unnn** Green component, 0-255

- **Bnnn** Blue component, 0-255

- **Wnnn** White component, 0-255 (Only for RGBW NeoPixel)

- **Pnnn** Brightness, 0-255

- **Ynn** Brightness, 0-31 (alternative to P 0-255)

- **Snnn** Number of individual LEDs to set to these colours, default 1

- **Fn** Following command action. F0 (default) means this is the last command for the LED strip, so the next M150 command starts at the beginning of the strip. F1 means further M150 commands for the remainder of the strip follow this one.

- **En** LED strip number, default 0. See M950 for defining the LED strip number, pin and LED type.

M150 E0 R255 P128 S20 F1 ; set first 20 LEDs to red, half brightness, more commands for the strip follow M150 E0 U255 B255 P255 S20 ; set next 20 LEDs to cyan, full brightness, finished programming strip

Ðžn **Fysetc 12864mini display** you can set all three LEDs separately. For display configuration and encoder illumination:

M918 P2 E-4 F2000000 ; Fysetc 12864mini M950 E0 C"io3.out" T1 U3 ; create a RGB Neopixel LED strip with 3 LEDs on the Duet 3 Mini 5+ 12864_EXP1 header M150 E0 R0 U0 B255 P255 S1 F1 ; display led blue M150 E0 R255 U0 B0 P255 S1 F1 ; left encoder led red M150 E0 R0 U255 B0 P255 S1 F0 ; right encoder led green

##### Parameters

- **Rnnn** Red component, 0-255

- **Unnn** Green component, 0-255

- **Bnnn** Blue component, 0-255

- **Wnnn** White component, 0-255 (Only for RGBW NeoPixel, RepRapFirmware 3.3 and later)

- **Pnnn** Brightness, 0-255

- **Ynn** Brightness, 0-31 (alternative to P 0-255)

- **Snnn** Number of individual LEDs to set to these colours, default 1

- **Fn** Following command action. F0 (default) means this is the last command for the LED strip, so the next M150 command starts at the beginning of the strip. F1 means further M150 commands for the remainder of the strip follow this one.

- **Xn** LED type: X0 = DotStar (default prior to RRF 3.2), X1 = RGB NeoPixel (default in RRF 3.2 and later), X2 = bit-banged RGB NeoPixel, X3 = RGBW NeoPixel (from RRF 3.3), X4 = bit-banged RGBW NeoPixel (from RRF3). This parameter is remembered from one call to the next, so it only needs to be given once. Not all boards support all the modes. On the Duet 3 Mini, X1 and X3 select the NeoPixel output on the main board, while X2 and X4 address the RGB LEDs on some 12864 displays.

- **Qnnn** (optional) Use specified SPI frequency (in Hz) instead of the default frequency. This parameter is not normally needed, and is only processed if X parameter also present. When using NeoPixels, only frequencies in the range 2.4 to 4MHz will work.

##### M150 X1 Q3000000 ; set LED type to NeoPixel and set SPI frequency to 3MHz M150 R255 P128 S20 F1 ; set first 20 LEDs to red, half brightness, more commands for the strip follow M150 U255 B255 P255 S20 ; set next 20 LEDs to cyan, full brightness, finished programming strip

Ðžn **Fysetc 12864mini display** you can set all three LEDs separately. For display configuration and encoder illumination:

M918 P2 E-4 F2000000 ; Fysetc 12864mini M150 X2 R255 U0 B0 P255 S1 F1 ; display led M150 X2 R0 U255 B0 P255 S1 F1 ; left encoder led M150 X2 R0 U255 B0 P255 S1 F0 ; right encoder led

### Usage

- LED strips are updated by one or more M150 commands.

- The specified RGB(WPY) values will be sent to the number of LEDs in the LED strip as specified by the S parameter.

- Setting an LED strip to one colour only requires a single M150 command. Make the S parameter equal to or a little longer than the number of LEDs in the strip, with the command containing F0 (or omit as F0 is the default).

- Setting different colours along an LED string requires multiple M150 commands, and the LEDs will be set once the final command is sent. Each previous M150 command should set the F parameter to F1, with the last M150 command setting it to F0 (or omit as F0 is the default). Each M150 command before the final F0 will set the next number of LEDs, defined by the S parameter, to the RGB(WPY) values specified in that M150 command.

- When a new M150 command, or set of M150 commands, are sent, the new RGB(WPY) values overwrite the existing ones, from the beginning of the strip. Only as many LEDs as the M150 commands specify get changed, leaving any LEDs further along the strip with their prior values.

; RRF 3.5 example M150 E0 R255 U0 B0 P255 S10 F1 ; Sets first 10 LEDs to red M150 E0 R0 U255 B0 P255 S10 F1 ; Sets next 10 LEDs to green M150 E0 R0 U0 B255 P255 S10 F0 ; Sets next 10 LEDs to blue, and send to LED strip

### Notes

- Regarding which pins to connect LED strips to:

  - M150 is supported on Duet 3 boards from RRF v3, using the dedicated output connector for DotStar and/or NeoPixel LEDs. It is supported on Duet 2 WiFi/Ethernet mainboards from RRF v3.3, using pin 5 on the CONN_LCD connector.

  - In RRF 3.5 and later, Neopixel LED strips can also be controlled by any pin that can be used as a low voltage digital output, on mainboards or expansion boards; for example an IO_OUT port on a Duet 3 series board.

  - However, when using an output other than the dedicated LED output on Duet 3 boards, in order to meet the precise timing requirement of Neopixel LEDs, RRF waits for all motion to stop and then disables interrupts while sending the LED data. During this time input data from UARTs may be lost, especially if there are a lot of LEDs to update. Therefore you should use the dedicated LED port if available.

  - While LEDs can be connected to Duet 2 mainboards, no pin (including pin 5 on CONN_LCD) can generate the timing in hardware, and motion will stop while the LEDs are updated.

  - In summary, if a Neopixel LED strip is assigned to a pin that cannot generate the WS2812 LED timing in hardware, then motion will be suspended while the LED strip is being written.

- Caution: in early firmware versions, if the S parameter is omitted then as many LEDs as can be set in a single chunk will be addressed which depends on the board (e.g. 60 RGBW neopixels on Duet2). We recommend users always explicitly set the number of LEDs to address with the S parameter, rather than rely on this behaviour as the number of LEDs addressed in a single chunk may change in the future.

- Some Neopixel/WS2812 versions have the colour order as RGB and others are GRB. Check the datasheet for the LEDs you are using if the Red and Green colours are switched. If this is the case then you will have to set the red with the U parameter and green with the R parameter.

See also Connecting 12864 or other displays.

