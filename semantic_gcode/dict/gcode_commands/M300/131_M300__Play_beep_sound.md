## M300: Play beep sound

### Parameters

- **Snnn** frequency in Hz

- **Pnnn** duration in milliseconds

- **Cnnn** custom buzzer port (only in RRF 3.6 or later, must be PWM-capable)

### Examples

M300 S300 P1000

### Notes

Play beep sound, use to notify events like the end of printing. If an LCD device is attached to RepRapFirmware, a sound is played via the add-on touch screen control panel. Else the web interface will play a beep sound.

If you intend to play multiple notes in a row, you will need to insert a G4 delay command between them at least equal to the length of the tone.

Example:

M300 S2000 P200 G4 P200 M300 S2500 P300 G4 P300

or

M300 C"io5.out"

See also Macros, sounds section

