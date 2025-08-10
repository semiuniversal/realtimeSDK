## M595: Set movement queue length

Supported in RRF 3.2 and later.

Different features of motion control firmware may have competing demands on microcontroller RAM. In particular, operations that use many short segments (e.g. laser rastering) need longer movement queues than typical 3D printing, but have fewer motors to control. This command allows the movement queue parameters to be adjusted so that the queue can be lengthened if necessary, or kept short if a long movement queue is not needed and there are other demands on RAM.

### Parameters

- **Pnn** Maximum number of moves held in the movement queue. RepRapFirmware uses this value to determine how many DDA objects to allocate.

- **Snn** (optional) Number of pre-allocated per-motor movement objects. If the number of pre-allocated objects is insufficient, RepRapFirmware will attempt to allocate additional ones dynamically when they are needed.

- **Rnnn** Grace period in milliseconds (supported in RRF 3.3 and later). When filling the movement queue from empty, the system waits for this amount of time after the last movement command was received before starting movement. This is to allow the movement queue to fill more before movement is started when commands are received from USB, Telnet or another serial channel. It should not be needed when processing a GCode file from the SD card.

- **Qn** (optional, RRF3.3 and later) Movement queue number, default 0. Some builds of RRF have a secondary movement queue. You can configure the length of that queue by specifying Q1.

### Notes

M595 without any parameters reports the length of the movement queue and the number of per-motor movement objects allocated.

