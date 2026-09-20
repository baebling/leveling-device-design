# Guide Mobility Summary

Status: next-step Phase 0 analysis complete. Preliminary only.

## Result

The central guide concept is conditionally feasible, but not solved for fabrication.

The required mechanism is:

```text
keyed vertical telescoping guide
+ yaw-transmitting two-axis Cardan/gimbal at platform center
+ multi-axis actuator end joints
```

A rigid keyed slide bolted directly to the upper platform would bind because it allows only Z translation.

## Key numerical results

From `calculations/mobility_analysis.py`:

- With a yaw-transmitting two-axis Cardan, central guide constraint rank is 3, leaving Z, pitch, and roll.
- A rigid keyed slide without Cardan has constraint rank 5, leaving only Z.
- Actuator length Jacobian rank is 3 in the checked +/-3, +/-5, and +/-8 deg cases.
- Max normalized Jacobian condition number is about 1.63 in the checked range, so the length mapping is not the dominant risk.
- Cardan combined tilt:
  - +/-3 deg pitch/roll: 4.24 deg.
  - +/-5 deg pitch/roll: 7.07 deg.
  - +/-8 deg pitch/roll: 11.30 deg.
- Current `cardan_design_angle_deg = 8` and `cardan_hard_stop_angle_deg = 10`, so +/-8 deg fails the Cardan screen.
- Max lower actuator joint deviation:
  - +/-3 deg case: 10.94 deg.
  - +/-5 deg case: 13.85 deg.
  - +/-8 deg case: 18.36 deg.
- Minimum guide overlap is 83 mm against an 80 mm preliminary requirement, which is too close for approval.

## Engineering interpretation

The current issue is not whether three actuator lengths can mathematically define Z/Pitch/Roll. They can in the screened range.

The issue is whether the physical guide and joints can realize that motion without side-load or binding:

- The central Cardan must transmit yaw while allowing pitch/roll.
- The actuator ends must not be simple single-axis clevises unless their motion plane is proven.
- The guide must not be asked to absorb actuator side-load from misalignment.
- The 83 mm guide overlap margin needs a real side-load and clearance check.

## Status update

`P-GDE-001` should remain:

```text
UNRESOLVED / critical_open
```

Next recommended work:

1. Define the central Cardan/yaw-torque path.
2. Select actuator joint family and allowable misalignment angle.
3. Allocate Cardan hard stop below joint limits.
4. Re-run combined workspace using the chosen joint and stop limits.
5. Build a small bench mock-up before fabrication CAD.
