# Central Yaw Path Summary

Status: preliminary. Not ready for `APPROVE PARAMETERS`.

Current-use note: the active review baseline is now the user-confirmed low-load 10 kg payload / 10 kg cart / +/-3 deg case in `outputs/reports/final_candidate_parameter_pack.md`. The earlier 90 kg yaw case is retained only as archived conservative sensitivity.

## Result

The central yaw-torque path was compared across four Phase 0 concepts.

Preferred direction:

- `YAW-A`: keyed square telescoping guide carries yaw torque.
- The two-axis gimbal should allow pitch/roll but must not interrupt the yaw torque path.

Reserve directions:

- `YAW-D`: dual anti-yaw guides pass load screening, but add width and overconstraint risk.
- `YAW-C`: single 16 mm ball spline passes low-load torque only, but adds package/procurement complexity.
- `YAW-B`: oversized direct-torque U-joint can pass torque/angle, but is large and costly.

## Key Numbers

- Active operating yaw torque screen: about 10.9 Nm.
- Active peak/design yaw torque screen: about 16.4 Nm.
- Archived conservative peak/design yaw torque screen: about 250 Nm.
- YAW-A square tube at active peak/design torque: about 1.24 MPa torsional shear and 0.022 deg twist.
- YAW-A key/contact force at 50 mm couple separation: about 328 N.
- YAW-A preliminary contact pressure with 80 mm overlap and 10 mm contact width: about 0.41 MPa.
- Ruland US32 reference: 485.8 Nm rated torque and 2429.2 Nm peak torque.
- MISUMI No.16 ball spline reference: 51 Nm dynamic torque and 93 Nm static torque; reserve only under the low-load screen.

## Files

- `calculations/central_yaw_path_comparison.py`
- `design_basis/central_yaw_path_comparison.md`

## Gate

```text
CENTRAL YAW PATH COMPARED
YAW-A PREFERRED DIRECTION
CENTRAL GUIDE STILL CRITICAL_OPEN
NOT READY FOR APPROVE PARAMETERS
```
