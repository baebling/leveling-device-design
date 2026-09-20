# Central Guide Mobility Review

Status: Phase 0 mobility review. Preliminary only. Not approved for fabrication CAD.

## 1. Purpose

This file resolves the next engineering question after the feedback review:

Can the central guide constrain X, Y, and yaw while still allowing Z, pitch, and roll?

The answer is conditional:

- Yes, if the central guide is a vertical keyed/torsion-transmitting telescoping member with a real yaw-transmitting two-axis Cardan/gimbal at the upper platform center.
- No, if the inner guide tube is rigidly fixed to the upper platform without a two-axis angular joint.

## 2. Coordinate basis

- X: lateral direction in upper platform plane.
- Y: fore-aft direction in upper platform plane.
- Z: vertical lift direction.
- Pitch: rotation about platform Y axis.
- Roll: rotation about platform X axis.
- Yaw: rotation about vertical Z axis.

Permitted active platform DOF:

```text
Z translation
Pitch
Roll
```

Mechanically constrained DOF:

```text
X translation
Y translation
Yaw
```

## 3. Required central guide architecture

The central guide must be treated as the main non-actuator constraint path:

1. Lower guide housing
   - Fixed to lower interface.
   - Constrains inner guide X/Y translation.
   - Constrains inner guide yaw through square/keyed/splined anti-rotation geometry.
   - Allows inner guide Z translation.

2. Inner telescoping member
   - Slides vertically.
   - Transmits yaw torque between upper Cardan/yoke and lower keyed guide.
   - Does not intentionally tilt with the upper platform.

3. Upper yaw-transmitting Cardan/gimbal
   - Located at the intended platform rotation center.
   - Has two intersecting horizontal rotational axes.
   - Allows platform pitch and roll relative to the vertical inner guide.
   - Constrains relative yaw between platform and inner guide.
   - Must not be a simple loose spherical joint unless a separate yaw anti-rotation path is added.

4. Upper platform
   - Rotates about the Cardan center for pitch/roll.
   - Its center point remains on the guide Z axis.

## 4. Constraint count

The platform has 6 rigid-body DOF before constraints:

```text
tx, ty, tz, rx, ry, rz
```

With a yaw-transmitting two-axis Cardan and keyed telescoping guide, the central guide constrains:

```text
tx = 0
ty = 0
rz = 0
```

Constraint rank = 3, leaving:

```text
tz, rx, ry
```

This is the desired platform mobility.

If the keyed guide is rigidly attached to the upper platform without a Cardan/gimbal, it constrains:

```text
tx = 0
ty = 0
rx = 0
ry = 0
rz = 0
```

Constraint rank = 5, leaving only:

```text
tz
```

That rigid arrangement would bind and is not acceptable.

## 5. Actuator joint requirement

The three actuators should control length only. They should not be relied on to constrain yaw or absorb guide side-load.

Therefore each actuator end must provide enough angular accommodation:

- Lower actuator joint: spherical rod end, true two-axis clevis/gimbal, or equivalent misalignment joint.
- Upper actuator joint: spherical rod end, true two-axis clevis/gimbal, or equivalent misalignment joint mounted to the rotating platform.
- A single-axis clevis pin is not enough unless the entire actuator motion is proven to remain in the clevis plane.
- Firgelli's 8.2 mm clevis hole is a connection interface, not by itself a proof of multi-axis misalignment capacity.

## 6. Numerical screening result

The script `calculations/mobility_analysis.py` was added.

Current results:

| Check | +/-3 deg | +/-5 deg | +/-8 deg |
|---|---:|---:|---:|
| Cardan combined tilt | 4.24 deg | 7.07 deg | 11.30 deg |
| Cardan 8 deg design angle | Pass | Pass | Fail |
| Cardan 10 deg hard stop | Pass | Pass | Fail |
| Max lower actuator joint deviation | 10.94 deg | 13.85 deg | 18.36 deg |
| Max upper actuator joint deviation | 7.08 deg | 7.68 deg | 9.47 deg |
| Actuator length Jacobian rank | 3 | 3 | 3 |
| Max normalized Jacobian condition | 1.45 | 1.50 | 1.63 |

The current geometry is not near a length-control singularity in the checked range. The remaining risk is not the actuator length mapping; it is the physical joint and central guide implementation.

## 7. Guide overlap screen

The current telescoping guide overlap screen gives:

```text
minimum_overlap_mm = 83
required_minimum_overlap_mm = 80
```

This only barely passes the preliminary overlap screen at full lift. It is not enough for fabrication approval because:

- UHMW shim clearance is undefined.
- Side-load and moment capacity are not calculated.
- Stop geometry and assembly tolerance are not allocated.
- The overlap check does not prove smooth sliding under load.

## 8. Current CAD limitation

The current CAD is a visual/parametric placeholder:

- `keyed_guide_inner` stays vertical.
- `cardan_head` is displayed at the platform center.
- The Cardan is not yet a real articulated assembly.
- Actuator joints are drawn as simple spheres, which is a placeholder for angular freedom.

Do not treat the current CAD as proof that the physical mechanism will articulate without binding.

## 9. Required next design decisions

Before parameter approval or detailed CAD, define:

1. Lower actuator joint type.
2. Upper actuator joint type.
3. Central guide lower bearing/slide construction.
4. Central guide upper Cardan/gimbal construction.
5. Whether the Cardan transmits yaw or whether a separate yaw link is required.
6. Cardan axis intersection tolerance.
7. Cardan design angle and hard stop angle.
8. Actuator joint allowable misalignment angle.
9. Guide overlap and side-load capacity.
10. Assembly clearance and shim/preload plan.

## 10. Recommendation

Keep the three-actuator concept direction, but keep `P-GDE-001` as `critical_open`.

The next engineering task should be a small physical or CAD-free bench mock-up of the central guide and Cardan principle before fabrication CAD. A simple test rig can verify whether pitch/roll motion stays smooth while yaw and X/Y remain constrained.
