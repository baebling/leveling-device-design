# Rev E Mega2560 controller

This firmware is for the stationary, supervised Rev E proof-of-concept only. It is not a safety controller and it must not be used for a person-carrying or moving platform.

## Fixed interfaces

| Function | Mega2560 pins |
|---|---|
| Encoder A | D2, D3, D18 |
| Encoder B | D22, D23, D24 |
| MDD10A PWM | D5, D6, D7 |
| MDD10A direction | D30, D31, D32 |
| Unused fourth MDD10A channel | PWM D8 held at 0, direction D33 low |
| MPU6050 | SDA D20, SCL D21 |

Motor power does not pass through the Mega. The Mega, MPU6050, and encoder logic use the regulated 5 V branch. All logic grounds and the MDD10A signal grounds meet at the 5 V/24 V DC common terminal; protective earth does not carry logic current.

## Commands

Send newline-terminated commands at 115200 baud.

```text
STATUS
HOME
JOG <axis 1..3> <signed_mm>
LIFT <absolute_mm 0..50>
LEVEL
STOP
ZERO_IMU
SAVE_CAL <c1> <c2> <c3> <dL1/dP> <dL2/dP> <dL3/dP> <dL1/dR> <dL2/dR> <dL3/dR>
```

`counts/mm` must be measured on the exact actuator revision. The nominal CAD sensitivity seed at Z=25 mm is:

```text
dL/dPitch = -0.194842, 3.006702, -2.811860 mm/deg
dL/dRoll  =  3.359349,-1.510936, -1.848413 mm/deg
```

Do not use the seed as proof of real calibration. `SAVE_CAL` stores measured counts/mm and the reviewed sensitivity matrix in EEPROM. Automatic motion remains blocked until valid positive counts/mm values exist.

## Commissioning order

1. Keep motor power disconnected and verify that all PWM outputs remain at zero after reset.
2. Connect one actuator and one driver channel only.
3. Confirm motor polarity and encoder sign with short, unloaded JOG trials.
4. Run supervised HOME. Internal actuator limits are assumed; no-pulse during HOME is only an endpoint indication, not independent safety protection.
5. Measure counts/mm over at least 50 mm in both directions and record backlash.
6. Save calibration, then repeat for the remaining axes.
7. Test `LIFT 25`, `LIFT 50`, and `LEVEL` unloaded before adding the 10 kg test load.

The firmware implements PWM ramping, 100 ms reversal dead time, motion timeout, encoder no-pulse and wrong-direction faults, IMU stale detection, a 5 degree tilt fault, 0-100 mm actuator travel limits, and sequential 0.25 mm leveling corrections. The physical mechanical stops and actuator internal limits remain mandatory and independent.
