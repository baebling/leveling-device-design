# Joint Candidate Screen

Status: preliminary Phase 0 screen. Not approved for fabrication.

Current-use note: after the 2026-08-25 user clarification, +/-5 deg is no longer a current requirement. Use HRT8E-style rod ends as the leading +/-3 deg candidate and keep high-angle link balls as reserve.

## Purpose

This note narrows the joint implementation risk identified in `design_basis/guide_mobility_review.md`.

The current concept requires:

- Upper platform commanded DOF: Z, pitch, roll.
- Mechanically constrained DOF: X, Y, yaw.
- Actuator end joints that tolerate spatial articulation.
- A central guide joint that transmits yaw constraint while allowing pitch and roll.

## Screening Criteria

The screen in `calculations/joint_candidate_screen.py` applies:

- Angular margin: 2 deg beyond calculated maximum joint deviation.
- Static load screen: candidate static capacity >= 2 x calculated maximum actuator axial force.
- Force case: `load_distribution.worst_case(angle, design_factor=2.0, max_eccentricity_mm=100)`.

This is a preliminary filter only. It is not a certification safety factor and does not replace bracket, pin, thread, bending, wear, or fatigue calculations.

## Required Actuator Joint Articulation

`calculations/mobility_analysis.py` shows that the lower actuator joint is the critical actuator-end joint.

| Pitch/roll case | Max lower joint deviation | Max upper joint deviation | Required actuator joint angle with 2 deg margin |
|---:|---:|---:|---:|
| +/-3 deg | 10.94 deg | 7.08 deg | 12.94 deg |
| +/-5 deg | 13.85 deg | 7.68 deg | 15.85 deg |
| +/-8 deg | 18.36 deg | 9.47 deg | 20.36 deg |

Implication:

- A single-axis clevis is rejected as the primary actuator end joint unless a future linkage proves the motion is planar.
- For a +/-3 deg baseline, require at least about 13 deg actuator joint articulation after packaging.
- For a +/-5 deg stretch case, require at least about 16 deg actuator joint articulation after packaging.

## Actuator Joint Candidate Result

| Candidate | Source | Screen result | Reason |
|---|---|---|---|
| Single-axis clevis | concept screen | Fail | Spatial joint motion is required. |
| MISUMI PHSOSM8 | SRC-JNT-001 | Fail | 12 deg angle and 2.69 kN static capacity are too tight under current screening. |
| MinebeaMitsumi HRT8E | SRC-JNT-006 | Pass for +/-3, fail for +/-5 | Its 5.29 kN axial static limit still passes the current +/-3 screen, but 14 deg angle does not meet the +/-5 case with 2 deg margin. |
| MISUMI RBLD8-style link ball | SRC-JNT-004 | Pass in current screen | High angular allowance and adequate static capacity in the preliminary M8 table. Exact purchasable SKU/package remains open. |

Current recommendation:

- Do not use PHSOSM8 as the primary actuator end joint in the approval package.
- Carry HRT8E only if the baseline remains +/-3 deg, JNT-BR-01 preserves the full 14 deg articulation, and the actuator-axis screen continues to use the 5.29 kN axial catalog limit rather than the higher radial value.
- Carry a high-angle link-ball style joint as the leading candidate if +/-5 deg remains a serious target.

## Central Cardan Candidate Result

`calculations/mobility_analysis.py` shows required central Cardan tilt:

| Pitch/roll case | Max Cardan tilt | Required Cardan angle with 2 deg margin |
|---:|---:|---:|
| +/-3 deg | 4.24 deg | 6.24 deg |
| +/-5 deg | 7.07 deg | 9.07 deg |
| +/-8 deg | 11.30 deg | 13.30 deg |

The current CAD placeholder values are:

- Design angle: 8 deg.
- Hard stop angle: 10 deg.

Result:

- The 8 deg design value passes +/-3 only after margin.
- The 10 deg hard-stop planning value barely passes +/-5 after margin, but this is not an independent purchased joint rating.
- Both current placeholder values fail the +/-8 sensitivity case after margin.

Ruland-style single universal joints are useful as a component-family reference because they provide a yaw-transmitting Cardan/u-joint class with much larger catalog angular capacity. This does not approve a specific SKU. Torque capacity, backlash, axial/radial load, keyway/shaft interface, and mounting stiffness remain unresolved.

## Open Items Before Parameter Approval

1. Select exact actuator end joint package and confirm retained articulation in the bracketed assembly.
2. Check pin/stud bending, thread engagement, joint axial load component, and bracket bearing stress.
3. Select exact central yaw-transmitting Cardan/gimbal implementation.
4. Prove the central guide side-load path and backlash do not defeat X/Y/yaw constraint.
5. Repeat the screen after moving/fixed mass split and final usable workspace are updated.

```text
JOINT IMPLEMENTATION SCREENED
HRT8E ACCEPTABLE ONLY FOR +/-3 BASELINE SCREEN
HIGH-ANGLE LINK BALL PREFERRED FOR +/-5 STRETCH STUDY
CENTRAL CARDAN STILL CRITICAL_OPEN
NOT READY FOR APPROVE PARAMETERS
```
