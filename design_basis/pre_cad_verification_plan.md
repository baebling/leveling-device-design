# Pre-CAD Verification Plan

Status: `APPROVE CONCEPT` received 2026-08-26. This evidence plan now gates design freeze and fabrication release, not detailed CAD entry.

## Purpose

The calculations now select a preliminary low-load concept package, but three interfaces still depend on real geometry, contact, and repeatability. This plan defines the minimum evidence required to decide whether those candidate parameters are retained, revised, or rejected. It is a PoC planning document only; it is not a safety certification or field-test procedure.

## Candidate Set Under Test

| Area | Current candidate | Quantitative basis |
|---|---|---|
| Operating workspace | `WS-01-H20`: 270 mm disconnected/collapsed device height, 100 mm lift, +/-3 deg pitch/roll | 11.13 mm minimum actuator soft reserve; 88 mm minimum guide overlap in the selected grid |
| Central yaw path | `YAW-A`: keyed square guide plus lower-+Y/upper-+X two-axis yoke | No independent yaw in `R = Ry(pitch) Rx(roll)`; four +/-7 deg pin stops remain below 10 deg total diagonal tilt |
| Actuator bracket | `JNT-BR-01-HRT8E`: centered double shear 8 mm pin/lug, 18 mm detailed CAD span | Official 23 x 11 mm eye envelope; 5.29 kN axial-static basis; about 12.94 deg required articulation against 14 deg catalogue value |
| Cart receiver | `CR-01-H4-S1`: master 12 mm bushing/stop, X-releasing secondary, Z-only rest pad, latch preload/secondary lock | 30-cycle evidence decides whether backing bridge or dowel is needed |
| Travel protection | 334-508 mm command; 329/513 mm electrical target; 324/518 mm mechanical-stop guarded values | Planning hierarchy only; final dimensions require real actuator and stop geometry |

## Verification Matrix

| ID | Fixture / input | Minimum action | Pass condition | Failure action |
|---|---|---|---|---|
| V-01 | Purchased HRT8E plus two-lug detailed gauge | Confirm official 8/23/11 mm dimensions, real spacer/pin stack and actuator-thread adapter; sweep 14 deg in both planes and diagonal | No contact through full 14 deg; measured stack <=18 mm or newly recalculated; no threaded-shank bending spacer | Recalculate pin/lug, relieve or redesign JNT-BR-01, or change to RBLD8 reserve |
| V-02 | Non-load-bearing YAW-A yoke/guide gauge | Sweep all nine +/-3 deg pitch/roll points while guide translates; then reach all +/-7 deg axis stops and diagonal corners | No bind/contact; no third azimuth joint; stops contact before unintended interference; yaw freeplay <=0.5 deg | Revise yoke axes, stop geometry, guide fit/wear pads, or retain a reserve yaw path |
| V-03 | One real actuator, planned switch target and external stop sample | Measure endpoint dimensions; slowly approach both directions for 10 repetitions | Electrical switch opens before physical stop; measured overrun fits the allocated gap; no reliance on actuator internal limit | Increase gap, reduce speed, change switch/actuator geometry, or revise operating window |
| V-04 | CR-01-H4-S1 receiver mock-up | Couple/uncouple 30 times; log hard-point shift, torque relaxation, marking and latch preload | Shift <=0.2 mm, torque loss <=20%, no profile-wall marking, no preload drift; master/secondary roles remain separated | Add 60 x 40 x 6 mm backing bridge, revise stop/insert, then repeat; do not add a second fixed X/Y locator |
| V-05 | Mass scale and parts list | Weigh cart receiver and moving upper assembly separately | Cart concept remains near 10 kg basis; actual moving mass replaces 15/22 kg sweep | Re-run actuator, yaw, interface and stop screens with measured masses |
| V-06 | Bench electrical architecture review | Confirm 12 V actuator compatibility, three independent channels, E-stop power isolation, latch/cart interlock concept | No 24 V supply is paired directly with the 12 V actuator; control cannot command motion with cart/latch state open | Reselect actuator/bus/driver or revise architecture before powered work |

## Data Record Requirements

For every verification row, store the fixture version, actual part number, photographs, measurement tool, measured values, pass/fail result, and any deviation in `logs/`. A drawing or a visual judgment without a measured clearance/freeplay value does not close an item.

## Decision Rule

All V-01 through V-04 must pass, or their residual risk and replacement candidate must be explicitly accepted by the user. V-05 and V-06 must update the relevant calculations before any detailed CAD is treated as more than a preliminary visualization. When the evidence package is complete, present the candidate pack to the user. Only the exact user message `APPROVE CONCEPT` opens the detailed CAD phase.

```text
PRE-CAD EVIDENCE PLAN COMPLETE
BENCH EVIDENCE PENDING
NO DETAILED CAD OR FABRICATION RELEASE
```
