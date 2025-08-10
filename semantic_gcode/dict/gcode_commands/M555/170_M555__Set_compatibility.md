## M555: Set compatibility

### Parameters

- **Pnnn** Emulation type

### Examples

M555 P1

### Description

Set the firmware to a mode where its input and (especially) output behaves similar to other established firmware. The value of the 'P' argument is:

| **value** | **Firmware**                 |
|-----------|------------------------------|
| 0         | RepRap_Firmware              |
| 1         | RepRap_Firmware              |
| 2         | Marlin                       |
| 3         | not used                     |
| 4         | not used                     |
| 5         | not used                     |
| 6         | nanoDLP (RRF 2.02 and later) |

