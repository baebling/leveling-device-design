# Electrical and control completeness check

Date: 2026-08-28

Status: **STATIONARY BENCH HARDWARE MOSTLY INCLUDED - NOT YET READY FOR FINAL WIRING OR POWER-ON**

## Selected power architecture

This prototype is stationary, indoors and supervised. It therefore uses mains power rather than a traction battery:

`220 VAC -> E008 two-pole breaker -> E004 NES-350-12 -> 12 VDC bus`

The 12 V bus splits into three independent motor branches:

`12 V bus -> E009 DC breaker x3 -> E001 DMD-150 x3 -> LA2000-125150 actuator x3`

The logic branch is:

`12 V bus -> E005 5 V / 3 A DC-DC -> E002 Mega2560 PRO + E003 BNO055`

The actuator delivery specification is DC 12 V, 2000 N, 150 mm stroke and 5 mm/s. The DIHOOL DHLA2000 family page independently supports this force/speed combination, built-in end limits and a 10% duty cycle with a maximum two-minute continuous run. The official A1 page displays `Current: 5 Amp` in its product summary, which is useful as a preliminary operating-current screen. The A2 page omits that field and the manufacturer does not define it as rated, maximum, starting or stall current, so it is not yet a release value for the delivered NAVIMRO variant. Hall feedback is optional at family level, so the page also does not prove that the delivered unit contains Hall feedback.

The official DMD-150 manual closes the controller-interface question: DC 6.5 to 41 V, 12 A continuous without added cooling, 15 A with simple cooling, 180 W at 12 V, 3.3/5 V-compatible TTL thresholds, independent IN1/IN2 direction inputs and PWM. `IN1=IN2=0` is brake and `IN1=IN2=1` is floating/coast. See `design_basis/dmd150_official_manual_review_2026-08-28.md`.

## Included in the NAVIMRO order

| Function | BOM rows | Included hardware |
|---|---|---|
| Motor drive | E001, E009 | Three DMD-150 bidirectional drivers and three DC-rated branch breakers; 12 V use is limited by the manual's 180 W/channel and thermal ratings |
| Supervisory control | E002, E003, E013 | Mega2560 PRO, BNO055 IMU and USB programming/control cable |
| Power conversion | E004, E005 | 12 V / 29 A bench supply and 5 V / 3 A logic converter |
| Mains and grounding | E007, E008, E022 | Grounded AC cord, two-pole disconnect breaker and protective-earth wire |
| Distribution and wiring | E010-E012, E014-E018, E023 | Terminal blocks, power/control wire, ferrules, crimp terminals, heat shrink, glands, ties and insulation tape |
| Enclosure | E006, E019-E021, E024 | Control box, cooling fan/filter, DIN rail and PCB standoffs |

## Intentionally not included

- Battery pack, BMS, battery fuse/disconnect, charger and battery enclosure. They are unnecessary for the approved stationary-bench operating boundary.
- Display, keypad or handheld pendant. Initial operation is planned over USB under direct supervision.
- Dedicated safety-rated emergency-stop switch and motor-power contactor. These were removed with the user's stationary-test scope reduction; E008 is only a reachable bench disconnect and is not a safety-rated E-stop.
- Finished control firmware, final pin map, final wiring schematic and fabricated wire harness.
- Ferrule and insulated-terminal crimping tools, unless the workshop confirms they are already available.

## Open items before final wiring and power-on

1. Confirm whether the three actuators include Hall feedback, pulses per millimetre, limit-feedback conductors, wire colours and connector pinout.
2. Confirm whether the manufacturer-page `5 Amp` value applies to the delivered A2/150 mm/5 mm/s unit and whether it is rated or maximum current. Obtain starting and stall current plus the supplier's allowed three-axis concurrency. Then verify DMD-150, NES-350-12 and the 10 A branch-breaker trip curve.
3. Select a NAVIMRO-orderable bidirectional motor-terminal TVS or manufacturer-approved equivalent, verify pulse-energy suitability, and test SMPS overvoltage behavior during loaded lowering/braking. The DMD-150 manual cites `1.5KE24CA` only as an example; an exact NAVIMRO SKU has not yet been identified.
4. Freeze the Mega2560 pin map and startup states using the confirmed DMD-150 truth table. Add the manual's approximately 0.1 s brake interval before a full-duty direction reversal and ramp PWM changes.
5. Produce and review the point-to-point schematic, terminal numbering, wire sizes, protective-earth bond and enclosure layout.
6. Implement supervised jog, lower-reference homing, per-axis timeout, travel plausibility, mismatch shutdown and lost-pulse detection before auto-level operation. If Hall is not included, use a reduced open-loop commissioning mode and do not claim synchronized leveling performance.
7. Complete continuity, polarity, protective-earth and current-limited single-axis tests before connecting all three actuators. Record DMD-150 temperatures and DC-bus overshoot.

## Battery conversion rule

Do not add an arbitrary 12 V battery to the current BOM. A future battery version requires the measured worst-case current first, followed by a separately selected battery chemistry/capacity, BMS, main fuse, disconnect, charger, connector, enclosure and cable sizing. That is a different electrical release from the present stationary AC-powered bench.

An AC-powered bench remains feasible, but the DMD-150 manual's regeneration warning means the PSU architecture is not released until the loaded-lowering bus-voltage test and suppression selection are complete.
