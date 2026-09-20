# Sensor, Control, Power, And Safety Sources

Access date: 2026-08-24

## IMU / Tilt Sensing

| Source ID | Candidate | Key official values | Decision |
|---|---|---|---|
| SRC-SEN-001 | Adafruit BNO085 breakout | BNO085 sensor fusion breakout; 29.50 USD product guide price | Baseline PoC IMU candidate |
| SRC-SEN-002 | Bosch BNO055 | Integrated 9-axis orientation sensor; not recommended for new designs | Avoid as new design unless already stocked |
| SRC-SEN-003 | TDK ICM-20948 | 9-axis DMP IMU; EOL status | Avoid final selection |
| SRC-SEN-004 | WitMotion WT901C | Pitch/roll accuracy 0.2 deg, up to 200 Hz output | Strong tilt-sensor candidate for faster integration |

## Motor Drivers

| Source ID | Candidate | Key official values | Decision |
|---|---|---|---|
| SRC-DRV-001 | Cytron MD13S | 13 A continuous, 30 A peak 10 s, 6-30 V, overcurrent/undervoltage | Baseline if actuator current stays <=13 A |
| SRC-DRV-002 | Cytron MD20A | 20 A continuous, 60 A peak, 6-30 V, thermal/overcurrent protection | Preferred if using 12 V Firgelli with 5.5 A/axis and margin |
| SRC-DRV-003 | Pololu G2 24v13 | 13 A continuous, 6.5-40 V, current sense/limit, reverse protection | Good compact alternative, no overtemp shutoff |

## Power Supplies

| Source ID | Candidate | Key official values | Decision |
|---|---|---|---|
| SRC-PWR-001 | Mean Well LRS-350-24 | 24 V, 14.6 A, 350.4 W, -25 to 70 C | Low-cost 24 V bench/enclosure candidate |
| SRC-PWR-002 | Omron S8VK-G48024 | 24 V, 20 A, 480 W, DIN rail, -40 to 70 C | Preferred industrial DIN candidate if budget allows |
| SRC-PWR-003 | TDK-Lambda DRF240-24-1 | 24 V, 10 A, 240 W, 15 A peak | Likely insufficient for simultaneous 3-axis motion |

## Safety Devices

| Source ID | Candidate | Key official values | Decision |
|---|---|---|---|
| SRC-SAF-001 | Omron A22E-M-03 E-stop | 3NC, IP65, push-lock/turn-reset | Baseline E-stop candidate |
| SRC-SAF-002 | Omron D4N limit switch | IP67, direct opening, 15M mechanical operations | Baseline limit/interlock switch candidate |
| SRC-SAF-003 | Schneider Harmony XB4/ZB4 | Up to IP66/67/69/69K, -40 to 70 C | Alternative E-stop/control family |

## Control Variable Guidance

- Do not set target leveling error from IMU accuracy alone.
- Proposed Phase 0 target: level display/control deadband 0.3 deg, expected achieved leveling error 0.5 deg after backlash/structure/play. This is ASSUMED/PROVISIONAL and must be tested.
- Control mode should stay slow demonstration only: manual, lift, auto-level. High-speed dynamic leveling remains excluded.
