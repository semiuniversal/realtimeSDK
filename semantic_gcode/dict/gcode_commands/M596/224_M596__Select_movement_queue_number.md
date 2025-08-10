## M596: Select movement queue number

Supported from firmware version 3.5 on Duet 3 main boards

### Parameters

- **Pnn** Movement queue number. Queues are numbered 0 (the default queue), 1, ...

### Description

This command is supported in RepRapFirmware 3.5 and later builds that can execute moves on different axis systems asynchronously, for example for concurrent processing of two or more actions. It specifies that subsequent GCode commands from this input channel should be routed to the specified movement queue and the tool associated with that queue.

### Notes

- The number of available queues is firmware-dependent but will typically be 2. Before using a movement queue other than queue 0 it may be necessary to use M595 to increase the length of that queue, because the default length of movement queues other than the primary one may be quite short.

- At the start of a file print, queue 0 is selected automatically.

- M596 without the P parameter reports the current movement queue number for the input channel that the command was received on.

- See Multiple Motion Systems for more information.

