# Joint Candidate Summary

Status: preliminary. Not ready for `APPROVE PARAMETERS`.

Current-use note: after the 2026-08-25 user clarification, +/-5 deg is no longer a current requirement. HRT8E-style rod ends are the leading simple +/-3 deg candidate; high-angle link balls are reserve.

## Result

The next Phase 0 step screened actuator-end and central Cardan joint candidates.

- Lower actuator joint articulation is the critical joint motion.
- Required actuator joint angle with a 2 deg margin is about 13 deg for the +/-3 deg baseline and about 16 deg for the +/-5 deg stretch case.
- A single-axis clevis is rejected as the primary actuator end joint unless a future planar linkage proof is added.
- MISUMI PHSOSM8 is too tight for the primary actuator joint in the current screen.
- MinebeaMitsumi HRT8E passes the current +/-3 deg baseline screen but fails the +/-5 deg angular margin screen.
- MISUMI RBLD8-style high-angle link ball remains the leading candidate family for a +/-5 deg stretch study, pending exact SKU and packaging checks.
- Central guide still needs a yaw-transmitting Cardan/u-joint or equivalent gimbal. Ruland-style U-joints are a reference component family by angle only, not an approved SKU.

## Files Added Or Updated

- `calculations/joint_candidate_screen.py`
- `design_basis/joint_candidate_screen.md`
- `design_basis/parameter_decision_table.csv`
- `design_basis/component_candidate_table.csv`
- `web_research/source_register.csv`

## Gate

```text
JOINT IMPLEMENTATION SCREENED
CENTRAL CARDAN STILL CRITICAL_OPEN
NOT READY FOR APPROVE PARAMETERS
```
