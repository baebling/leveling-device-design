# Joint Detail Summary

Status: preliminary. Not ready for `APPROVE PARAMETERS`.

Current-use note: this summary includes the archived +/-5 deg stretch check and high-yaw-torque sensitivity. The active design direction is now the user-confirmed 10 kg payload / 10 kg cart / +/-3 deg low-load PoC baseline, but the bracket load-path warning still applies.

## What Was Added

The joint work was extended from candidate filtering to first-order packaging and torque screening.

Added:

- `calculations/joint_detail_screen.py`
- `design_basis/joint_detail_screen.md`

## Main Findings

- Actuator joint pin double shear and lug bearing are not the primary bottleneck in the current screen.
- Threaded-stud cantilever bending is the bottleneck if the bracket load line is offset.
- For the archived +/-5 deg stretch screen under the current low-load mass basis, an M8 link-ball style joint with 10 mm unsupported standoff gives about 407 MPa preliminary bending stress and fails the placeholder screen.
- An M12 upsize improves the result to about 119 MPa and passes the placeholder numeric screen, but it remains a reserve rather than a reason to use a threaded shank as a spacer.
- Actuator joint brackets should route force through the ball center and use double-shear/boxed supports.
- The conservative yaw torque screen gives about 125 Nm operating yaw torque and about 250 Nm peak/design torque.
- Small Ruland U-joint examples pass angle but fail the yaw torque screen, so they should not be the sole yaw-torque path.
- The 50 x 3 mm square guide tube looks plausible as a torsion member by first-order thin-wall math, but the Cardan/gimbal connection path remains unresolved.

## Gate

```text
JOINT DETAIL SCREEN COMPLETE
CENTRAL CARDAN/YAW TORQUE PATH STILL CRITICAL_OPEN
NOT READY FOR APPROVE PARAMETERS
```
