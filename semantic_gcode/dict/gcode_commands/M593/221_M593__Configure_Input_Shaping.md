## M593: Configure Input Shaping

The purpose of input shaping is to reduce ringing (also called ghosting).

• RepRapFirmware 3.6 and later

• RepRapFirmware 3.3 to 3.5

• RepRapFirmware 3.2 and earlier

##### Parameters

- **P"type"** Type of input shaping to use, not case sensitive. RRF 3.6 supports "none", "zvd", "zvdd", "zvddd", "mzv", "ei2", "ei3" and "custom".

- **Fnnn** Centre frequency of ringing to cancel in Hz

- **Snnn** (optional) Damping factor of ringing to be cancelled, default 0.1.

- **Lnnn** (optional) This parameter is ignored (RRF 3.6.0 and later).

- **Hnn:nn...** Only used with P"custom" parameter. These are the individual amplitudes of each impulse except the last, and the amplitude of the last impulse will be set by RRF to 1.0 minus the sum of the other amplitudes; therefore the amplitudes provided must sum to less than 1.0 (RRF 3.6.0 and later).

- **Tnn:nn...** Only used with P"custom" parameter. These are the cumulative delays of each impulse except the first (the first has zero delay) in seconds, and must be strictly increasing (RRF 3.6.0 and later).

##### Notes

- In RRF 3.6.0, the input shaping algorithm has been changed. The new algorithm has the advantage that it can be (and is) applied to any type of move, including short segmented moves. The disadvantage that it introduces artefacts at direction changes.

- In RRF 3.6.0, the minimum input shaping frequency has been reduced to 4Hz for all boards.

- The L parameter is not used in RRF 3.6.0 and later. The H and T changed compared to earlier

##### Information about the Input Shapers

| **Input Shaper** | **Shaper Duration** | **Band over which vibration reduced by at least 90%** |
|----|----|----|
| ZV | 0.5 / Frequency | Â± 6% Frequency |
| ZVD | 1 / Frequency | Â± 20% Frequency |
| ZVDD | 1.5 / Frequency | Â± 30% Frequency |
| ZVDDD | 2 / Frequency | Â± 38% Frequency |
| MZV | 1 / Frequency | Â± 10% Frequency (also at least 80% reduction from -18% to +108%) |
| EI2 | 1.5 / Frequency | Â± 39% Frequency |
| EI3 | 2 / Frequency | Â± 50% Frequency |

RepRapFirmware no longer supports ZV input shaping because of its poor performance.

##### Parameters

- **P"type"** Type of input shaping to use, not case sensitive. RRF 3.4 supports "none", "zvd", "zvdd", "zvddd", "mzv", "ei2", "ei3" and "custom". RRF 3.3 supports "none" or "daa", and if no P parameter is given but the F parameter is given then "daa" is assumed, for compatibility with previous releases.

- **Fnnn** Centre frequency of ringing to cancel in Hz

- **Snnn** (optional) Damping factor of ringing to be cancelled, default 0.1.

- **Lnnn** (optional) RRF 3.5.x: Minimum fraction of the original acceleration or feed rate to which the acceleration or feed rate may be reduced in order to apply input shaping. The default is 0.25 and the acceptable range is 0.01 to 1.0. RRF 3.4.x and earlier: Minimum acceleration allowed, default 10mm/sec^2. Input shaping will not be applied if it requires the average acceleration to be reduced below this value.

- **Hnn:nn...** Only used with P"custom" parameter. These are the cumulative amplitudes of each impulse except the last, so each is larger than the previous one, and the amplitude of the last will be set by RRF to 1.0.

- **Tnn:nn** Only used with P"custom" parameter. These are the durations of each impulse except the last.

##### Examples

**RRF 3.4 and later**

M593 P"zvd" F40.5 ; use ZVD input shaping to cancel ringing at 40.5Hz M593 P"none" ; disable input shaping M593 P"custom" H0.4:0.7 T0.0135:0.0135 ; use custom input shaping

**RRF 3.3**

M593 P"daa" F40.5 ; use DAA to cancel ringing at 40.5Hz M593 P"none" ; disable DAA

##### Notes

- The L parameter changed in RRF 3.5.0 compared to previous versions; it is the minimum fraction of the original acceleration or feed rate to which the acceleration or feed rate may be reduced in order to apply input shaping. For example, if the commanded feedrate is F1000, L0.25 would allow the feedrate to reduce to F250, while L0.75 would only allow it to reduce to F750. So the **least** amount of reduction of acceleration or feed rate is from the **highest** L value.

##### Information about the Input Shapers

| **Input Shaper** | **Shaper Duration** | **Band over which vibration reduced by at least 90%** |
|----|----|----|
| ZV | 0.5 / Frequency | Â± 6% Frequency |
| ZVD | 1 / Frequency | Â± 20% Frequency |
| ZVDD | 1.5 / Frequency | Â± 30% Frequency |
| ZVDDD | 2 / Frequency | Â± 38% Frequency |
| MZV | 1 / Frequency | Â± 10% Frequency (also at least 80% reduction from -18% to +108%) |
| EI2 | 1.5 / Frequency | Â± 39% Frequency |
| EI3 | 2 / Frequency | Â± 50% Frequency |

RepRapFirmware no longer supports ZV input shaping because of its poor performance.

##### Parameters

- **Fnnn** Centre frequency of ringing to cancel by DAA, in Hz. Zero or negative values disable DAA.

- **Lnnn** Minimum acceleration allowed, default 10mm/sec^2. DAA will not be applied if it requires the average acceleration to be reduced below this value.

**Example (RRF 3.2 and earlier)**

M593 F40.5 ; use DAA to cancel ringing at 40.5Hz

Note: In firmware 2.02 up to 3.3 the only form of input shaping supported is Dynamic Acceleration Adjustment (DAA). By default, DAA is disabled. If it is enabled, then acceleration and deceleration rates will be adjusted per-move to reduce ringing at the specified frequency. Acceleration limits set by M201 and M204 will still be honoured when DAA is enabled, so DAA will only ever reduce acceleration. Therefore your M201 and M204 limits must be high enough so that DAA can reduce the acceleration to the optimum value. Where possible DAA reduces the acceleration or deceleration so that the time for that phase is the period of the ringing. If that is not possible because of the acceleration limits, it tries for 2 times the period of the ringing.

### Notes

- Input shaping not working for your printer? Check this:

  - High X and Y jerk values are an issue for all types of Input Shaping because the theory behind IS assumes no jerk. Therefore you should set the X and Y jerk limits only as high as necessary to allow curves to be printed smoothly. Users report jerk values of 5mm/s (300mm/min) seem to allow for IS to work, and curves to print smoothly, though test it works for you.

  - Another cause of IS not working is mesh compensation with a fine mesh and low acceleration. This splits the acceleration and deceleration parts of a move across multiple segments, which makes it difficult for RRF to apply IS.

  - A third cause is short accelerate/decelerate moves. This is being addressed in RRF 3.5.0.

- Input shaping is most useful to avoid exciting low-frequency ringing, for which S-curve acceleration is ineffective and may make the ringing worse. High-frequency ringing would be better countered by using S-curve acceleration; however, low-frequency ringing is more of a problem in most 3D printers.

- The ringing frequencies are best measured using an accelerometer, for which support is provided in RRF 3.3 and later.

- If you don't have an accelerometer, take a print that exhibits ringing on the perimeters (for example a cube), preferably printed single-wall or external-perimeters-first. Divide the speed at which the outer perimeter was printed (in mm/sec) by the distance between adjacent ringing peaks (in mm). When measuring the distance between peaks, ignore peaks close to the corner where the ringing started (these peaks will be spaced more closely because the print head will have been accelerating in that area).

- Cartesian and CoreXY printers will typically have different frequencies of ringing for the X and Y axes. In this case it is is usually best to aim to cancel the lower ringing frequency. If the frequencies are not much different, in a moving-bed Cartesian printer you can reduce the higher ringing frequency by adding mass to that axis or reducing belt tension on that axis. Note that X axis ringing causes artefacts predominantly on the Y face of the test cube, and vice versa.

- Keep in mind that you have to retune Pressure Advance after you have configured Input Shaping. The Pressure Advance will differ from shaper to shaper and from frequency to frequency.

- See also: Input shaping

