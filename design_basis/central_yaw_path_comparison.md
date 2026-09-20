# Central Yaw Path Comparison

Status: preliminary Phase 0 concept comparison. Not approved for fabrication.

Current-use note: after the 2026-08-25 user clarification, the active review baseline is the low-load 10 kg payload / 10 kg cart / +/-3 deg case in `design_basis/user_confirmed_scope_2026-08-25.md` and `outputs/reports/final_candidate_parameter_pack.md`. The earlier 90 kg yaw case is retained only as an archived conservative sensitivity.

## Purpose

Previous checks showed that small universal joints can provide enough articulation angle but cannot serve as the sole yaw-torque path. This note compares alternative central yaw-torque paths while preserving the required platform DOF:

- Allowed: Z translation, pitch, roll.
- Constrained: X translation, Y translation, yaw.

The comparison is implemented in `calculations/central_yaw_path_comparison.py`.

## Required Case

The active screen uses the current user-confirmed low-load case:

| Item | Value |
|---|---:|
| Total lifted mass | 42 kg |
| Horizontal acceleration | 0.25 g |
| Design factor | 1.5 |
| CG offset | 50 mm X, 50 mm Y |
| Operating yaw torque | 10.9 Nm |
| Peak/design yaw torque | 16.4 Nm |
| Required Cardan/gimbal articulation with margin at +/-3 deg pitch/roll | 6.2 deg |

This is still a screening case, not a certified load case.

Archived conservative sensitivity:

| Item | Value |
|---|---:|
| Total lifted mass | 90 kg |
| Horizontal acceleration | 0.5 g |
| Design factor | 2.0 |
| CG offset | 100 mm X, 100 mm Y |
| Operating yaw torque | 124.8 Nm |
| Peak/design yaw torque | 249.6 Nm |

## Compared Concepts

| ID | Concept | Screen result | Phase 0 rank |
|---|---|---|---:|
| YAW-A | Keyed square slide with two-axis gimbal torque bypass | Pass preliminary load screen | 1 |
| YAW-D | Dual parallel anti-yaw guides with top compliance | Pass load only; reserve | 2 |
| YAW-C | Single 16 mm commercial ball spline | Passes low-load torque only; reserve | 3 |
| YAW-B | Oversized direct-torque universal joint | Pass torque/angle screen; oversized reserve | 4 |

## YAW-A: Keyed Square Slide With Gimbal Torque Bypass

Direction:

- The central square telescoping guide carries yaw torque.
- The upper two-axis gimbal allows pitch/roll but does not interrupt yaw torque transmission.
- Yaw torque passes through the keyed/anti-rotation tube and its fastened yokes, not through a small U-joint.

Screen result:

- At 16.4 Nm peak/design torque, the 50 x 3 mm square-tube estimate gives about 1.24 MPa torsional shear and 0.022 deg twist over 190 mm.
- With a 50 mm torque-couple separation, the key/facing couple force is about 328 N.
- With 80 mm overlap and a 10 mm contact width, preliminary contact pressure is about 0.41 MPa.

Interpretation:

- This is the preferred Phase 0 direction.
- The concept remains open because backlash, wear, side-load, sliding clearance, contamination, gimbal-axis implementation, and connection fasteners are not solved.
- A physical mock-up is required before fabrication CAD.

## YAW-B: Oversized Direct-Torque Universal Joint

Reference source:

- Ruland US32-22MM-20MM-F, rated torque 485.8 Nm, peak torque 2429.2 Nm, max operating angle 45 deg.

Screen result:

- Rated torque margin against the 10.9 Nm operating torque is very large.
- Peak torque margin against the 16.4 Nm peak/design torque is very large.
- Angle margin at the +/-3 deg pitch/roll screen is large.

Interpretation:

- This is the reserve torque-capable Cardan direction.
- It is probably large for the current central stack: 50.7 mm OD and 139.7 mm length.
- Shaft/key/clamp details, backlash, side load, cost, and package height remain unresolved.

## YAW-C: Single 16 mm Commercial Ball Spline

Reference source:

- MISUMI No.000127 ball spline table lists the No.16 static torque rating as 93 Nm and dynamic torque rating as 51 Nm.

Screen result:

- Dynamic torque margin against 10.9 Nm: about 4.7.
- Static torque margin against 16.4 Nm: about 5.7.

Interpretation:

- Keep a single 16 mm ball spline as a reserve, not the preferred central yaw path.
- It is no longer torque-blocked under the low-load screen, but it would change cost, package, and overconstraint risk.
- Pitch/roll still requires a separate gimbal isolation scheme.

## YAW-D: Dual Parallel Anti-Yaw Guides

Reference source:

- HIWIN MGN15H block rating already in the source register: dynamic 6370 N, static 9110 N.

Screen result:

- With 400 mm guide separation, operating couple force is about 27 N.
- Peak/design couple force is about 41 N.
- These are small compared with the reference guide load ratings.

Interpretation:

- Load capacity is not the issue.
- This is a reserve concept only because it widens the mechanism, adds alignment sensitivity, and can overconstrain pitch/roll unless top compliance/gimbals are explicit.

## Current Decision

Carry forward YAW-A as the preferred central yaw path:

```text
Preferred: keyed square telescoping guide carries yaw torque
Required: two-axis gimbal permits pitch/roll without interrupting yaw path
Rejected: small U-joint as sole yaw-torque path
Reserve: oversized direct-torque Cardan or dual anti-yaw guides
Reserve for now: single 16 mm ball spline
```

## Open Items

Before parameter approval:

1. Define the gimbal/yoke topology that lets pitch/roll move while preserving yaw torque transfer.
2. Define anti-yaw key/contact faces, overlap, wear pads, preload/clearance, and contamination protection.
3. Check backlash and allowable yaw compliance.
4. Check side load from off-axis actuator and payload cases.
5. Build a low-risk physical mock-up before detailed metal fabrication CAD.

```text
CENTRAL YAW PATH COMPARED
YAW-A PREFERRED DIRECTION
CENTRAL GUIDE STILL CRITICAL_OPEN
NOT READY FOR APPROVE PARAMETERS
```
