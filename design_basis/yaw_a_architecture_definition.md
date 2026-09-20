# YAW-A Architecture Definition

Status: preliminary Phase 0 candidate parameter definition. Not approved for fabrication.

Update: revised after the 2026-08-25 user clarification that 10 kg carried payload, about 10 kg empty cart mass, 250 to 300 mm disconnected device height, and +/-3 deg pitch/roll are sufficient, and simple fabrication/assembly is preferred.

## Purpose

This note turns the preferred central yaw path concept into candidate parameters for user review.

YAW-A means:

- The keyed square telescoping guide carries yaw torque.
- The upper two-axis gimbal/yoke allows pitch and roll.
- The gimbal/yoke must not create a free yaw joint.
- The actuators control platform plane height/tilt and should not be relied on as yaw constraints.

The calculation backing this note is `calculations/yaw_a_architecture_screen.py`.

## Required Mobility

Platform twist variables:

```text
tx, ty, tz, rx, ry, rz
```

YAW-A should constrain:

```text
tx = 0
ty = 0
rz = 0
```

And allow:

```text
tz, rx, ry
```

Screen result:

| Architecture | Constraint rank | Passive DOF | Result |
|---|---:|---:|---|
| YAW-A keyed slide + yaw-locking two-axis gimbal | 3 | 3 | Pass |
| Rigid keyed slide without gimbal | 5 | 1 | Reject: pitch/roll bind |
| Loose spherical joint without yaw lock | 2 | 4 | Reject: yaw unconstrained |

## Candidate Gimbal Parameters

The earlier 12 deg design / 14 deg hard-stop candidate was sized around a possible +/-5 deg stretch path. The user has now clarified that only +/-3 deg pitch/roll is required. Therefore the simpler 8 deg design / 10 deg hard-stop candidate is carried forward.

Candidate YAW-A values:

| Parameter | Candidate value | Reason |
|---|---:|---|
| Normal gimbal design angle | 8 deg | Passes +/-3 deg pitch/roll plus 2 deg margin |
| Independent gimbal hard stop | 10 deg | Covers +/-5 deg as a non-required sensitivity |
| Required angle at +/-3 deg | 6.24 deg | Pass |
| Required angle at +/-5 deg | 9.07 deg | Hard-stop pass only; not a requirement |
| Required angle at +/-8 deg | 13.30 deg | Reject as current baseline/sensitivity |

Interpretation:

- +/-5 deg is now an archived future stretch case, not a current requirement.
- The hard stop should prevent geometric crash/bind before joint damage.
- Electrical limits and mechanical stops must remain independent.

## Candidate Anti-Yaw Contact Parameters

The current user-confirmed PoC yaw torque screen uses:

- Material payload: 10 kg.
- Empty cart mass: about 10 kg primary.
- Total lifted mass in the current primary baseline: 42 kg.
- Baseline design yaw torque: about 16 Nm.
- 30 kg cart sensitivity design yaw torque: about 24 Nm.
- Guide couple separation: 50 mm.

Candidate values:

| Parameter | Candidate value |
|---|---:|
| Anti-yaw contact width per active face | >= 10 mm |
| Minimum engaged overlap | >= 80 mm |
| Preferred engaged overlap | >= 100 mm |
| Design couple force at 50 mm separation | about 328 N |
| Contact pressure at 80 mm overlap and 10 mm width | about 0.41 MPa |
| Contact pressure at 100 mm overlap and 10 mm width | about 0.33 MPa |

The 80 mm overlap is a minimum screen value. The project should prefer 100 mm or more after geometry update if packaging allows.

## Candidate Backlash Parameters

Yaw backlash estimate:

```text
yaw_freeplay = atan(total_clearance / couple_separation)
```

Using 50 mm couple separation:

| Total clearance | Estimated yaw freeplay | Status |
|---:|---:|---|
| 0.1 mm | 0.11 deg | Preferred |
| 0.2 mm | 0.23 deg | Preferred target |
| 0.3 mm | 0.34 deg | Acceptable maximum candidate |
| 0.5 mm | 0.57 deg | Reject for current screen |

Candidate values:

- Preferred total yaw clearance: <= 0.2 mm.
- Maximum total yaw clearance before rework: <= 0.3 mm.
- Preferred yaw freeplay target: <= 0.25 deg.
- Maximum yaw freeplay limit: <= 0.5 deg.

This is not yet a tolerance drawing. It is a parameter target for shim/wear-pad/preload design.

## Candidate Gimbal/Yoke Pin Parameters

For yaw torque transmission through the gimbal/yoke, a first-order pin screen uses:

- User-confirmed PoC design yaw torque: about 16 Nm.
- Candidate yaw couple arm: 50 mm.
- Candidate pin diameter: 10 mm.
- Candidate lug thickness: 8 mm.

Result:

- Pin force: about 328 N.
- Pin double-shear stress: about 2.1 MPa.
- Lug bearing stress: about 4.1 MPa.

Candidate values:

- Yaw torque couple arm: >= 50 mm.
- Gimbal/yoke pin diameter: >= 10 mm.
- Lug thickness: >= 8 mm.
- Use double-shear yokes wherever possible.

This does not approve bearing life, fatigue, fastener sizing, or manufacturing details.

## Carried Forward Candidate Parameters

| Parameter | Candidate value |
|---|---:|
| `yaw_a_gimbal_design_angle_deg` | 8 |
| `yaw_a_gimbal_hard_stop_deg` | 10 |
| `yaw_a_total_clearance_target_mm` | <= 0.2 |
| `yaw_a_total_clearance_max_mm` | <= 0.3 |
| `yaw_a_yaw_freeplay_target_deg` | <= 0.25 |
| `yaw_a_yaw_freeplay_max_deg` | <= 0.5 |
| `yaw_a_contact_width_mm` | >= 10 |
| `yaw_a_min_overlap_mm` | >= 80 |
| `yaw_a_preferred_overlap_mm` | >= 100 |
| `yaw_a_yoke_couple_arm_mm` | >= 50 |
| `yaw_a_yoke_pin_diameter_mm` | >= 10 |
| `yaw_a_yoke_lug_thickness_mm` | >= 8 |

## Open Items

Before parameter approval:

1. Define the actual gimbal/yoke axis order and pin stack.
2. Prove yaw torque transfer through upper platform, yoke, intermediate block, inner guide, guide contact faces, and lower housing.
3. Select shim/wear pad material and contamination protection.
4. Check side load and friction under off-center load.
5. Check backlash after wear and assembly tolerance.
6. Build a small non-fabrication mock-up before metal CAD.

```text
YAW-A CANDIDATE PARAMETERS DEFINED
NOT APPROVED FOR FABRICATION
NOT READY FOR APPROVE PARAMETERS
```
