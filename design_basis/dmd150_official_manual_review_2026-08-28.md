# DMD-150 Official Manual Review

Date: 2026-08-28

Status: **CONTROL INTERFACE CONFIRMED; ACTUATOR CURRENT AND REGENERATION PROTECTION REMAIN OPEN**

## Source Files

- `references/vendor_downloads/DMD-150_users_manual.pdf`: official Motorbank six-page user manual downloaded from the manufacturer's technical-data page.
- `references/vendor_downloads/arduino_ms-001_dmd-150_example.zip`: official Arduino example downloaded from the manufacturer's technical-data page.

## Confirmed Electrical Ratings

| Item | Official value | Design interpretation |
|---|---:|---|
| Supply range | DC 6.5 to 41 V | Compatible with the selected 12 V bus |
| Continuous current without added cooling | 12 A | Use as the default thermal limit until enclosure testing |
| Continuous current with simple cooling | 15 A | Requires demonstrated airflow and temperature margin |
| Output power at 12 V | 180 W | The distributor's generic 360 W label applies at 24 V, not 12 V |
| Logic high | 2.0 to 5.5 V | Mega2560 5 V logic is compatible |
| Logic low | 0 to 0.8 V | Use a common logic ground and defined startup states |
| PWM range | 0.1 to 100% | Ramp duty rather than making abrupt large changes |
| 5 V auxiliary output | 500 mA | Do not use it as the main Mega/BNO055 supply; retain E005 |
| Driver size | 55 x 55 x 35 mm | Use for enclosure layout |

The 110 A figure in the manual is an instantaneous MOSFET peak rating. It is not an allowable branch current or a basis for breaker, conductor or PSU sizing.

## Confirmed Control Truth Table

| IN1 | IN2 | PWM | Motor state |
|---:|---:|---:|---|
| 0 | 0 | 0 or 1 | Brake |
| 1 | 1 | 0 or 1 | Floating/coast |
| 1 | 0 | 1 or PWM | Forward / forward speed control |
| 0 | 1 | 1 or PWM | Reverse / reverse speed control |

The official Arduino example uses separate `IN1`, `IN2` and `PWM` outputs. Its `brake()` function drives both direction inputs low and PWM to zero; `floating()` drives both direction inputs high and PWM to zero. Mega2560 pins may be reassigned, but this logic must be preserved.

For a full-duty direction reversal, the manual calls for approximately 0.1 s of braking before applying the opposite direction. The control software shall also ramp PWM and prevent direct forward-to-reverse commutation.

## Regeneration And Protection Finding

The manual warns that motor inertia or lowering motion can return energy to the DC bus. A switch-mode power supply may respond by entering overvoltage protection. The manufacturer recommends a bidirectional TVS at the motor output and gives `1.5KE24CA` as an example, while also emphasizing controlled stopping and avoiding abrupt PWM changes.

This creates a real procurement gap:

1. identify a NAVIMRO-orderable bidirectional TVS or manufacturer-approved equivalent;
2. verify its stand-off, clamp voltage and pulse-energy rating against measured actuator regeneration;
3. define terminal placement and lead length in the wiring drawing;
4. confirm that the selected SMPS remains stable during loaded lowering and braking.

Do not treat the example TVS part number, or multiple TVSs in parallel, as an automatically validated final design. Pulse-current sharing and absorbed energy require a bench check.

## Remaining Release Gates

The driver interface itself is no longer an unknown. The remaining driver-system gates are:

- delivered actuator rated, starting and stall current;
- permitted one-, two- and three-axis concurrency;
- loaded-lowering regenerative voltage and energy;
- enclosure airflow and DMD-150 case temperature;
- final Mega2560 pin allocation, startup pull states and point-to-point wiring;
- single-axis current-limited commissioning before all three channels are enabled.

