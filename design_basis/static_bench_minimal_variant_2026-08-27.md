# Static-bench minimal prototype variant

Status: `STATIC_BENCH_LOW_SPEED - NOT APPROVED FOR GENERAL USE`

## User-approved scope reduction

The user confirmed that the prototype will only be powered for test operation and will not travel. The active build is therefore reduced from the earlier industrial-style protection package to `LS-01M_STATIC_BENCH_MINIMAL`.

## Operating boundary

- Module mechanically fixed to a stationary test frame.
- Indoor, dry, supervised test only.
- No cart travel, no unattended cycles and no people on or under the platform.
- 10 kg payload target and +/-3 degree pitch/roll only.
- Low-speed jog and short validation cycles.

## Removed from the active CAD and BOM

- Six Omron D4N external limit switches.
- Six electrical trip cams and their slotted brackets.
- Dedicated industrial emergency-stop switch SKU.
- Safety interlock, mobile-operation sensors and guarding package.

These parts remain archived research candidates and must be reconsidered if the device becomes mobile, unattended, higher-speed or used outside a controlled bench test.

## Retained minimum mechanism protection

- Selected LA2000-125150 built-in electrical end limits, pending supplier wiring confirmation.
- Independent LS-01M external mechanical stop collars.
- A reachable bench-supply power disconnect operated by the test supervisor.
- Current limiting/fusing sized for the wiring and actuator branch.

The external mechanical collars are retained because the actuator internal limits may not be the only travel boundary under `HC-005`. They are not a certified safety function.

## Fabrication status

This scope reduction removes unnecessary purchased safety hardware but does not by itself release fabrication. The following measured inputs remain mandatory:

1. Exact K92931811/LA2000-125150 end interfaces, pin-centre limits, Hall/limit wiring, current and matching STEP.
2. JFT-8R received dimensions, Rev D yoke articulation and shoulder-bolt engagement.
3. Mechanical-collar push-off and stop-contact test.
4. Apply the confirmed DMD-150 IN1/IN2/PWM truth table, approximately 0.1 s reversal brake interval and PWM ramping; complete single-axis current-limited commissioning, thermal measurement and regeneration/SMPS overshoot testing.
5. Actual actuator endpoints and three-actuator Hall-count repeatability if Hall feedback is supplied.

The first build should be one joint and one actuator cassette, not six joints and three full cassettes at once.
