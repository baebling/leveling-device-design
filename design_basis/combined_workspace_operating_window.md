# Combined Workspace Operating Window

Status: Phase 1 preliminary parameter screen. Not approved for fabrication.

## Purpose And Coordinate System

This screen selects a geometry candidate that can perform the user-confirmed full operating grid before detailed CAD:

- Material payload: 10 kg user-confirmed PoC basis. The workspace result is geometric; it does not increase any load claim.
- Vertical lift: 0, 50, 75, and 100 mm from the selected disconnected/collapsed pose.
- Pitch and roll: every nine combination of `-3, 0, +3 deg`.
- Coordinate origin: lower-platform center; `+X` is the 900 mm length direction, `+Y` the 800 mm width direction, and `+Z` vertical. Pitch is about `+Y`; roll is about `+X`.

For upper joint `u_i`, lower joint `b_i`, and platform height `z`, the calculation is:

```text
Li = || Ry(pitch) Rx(roll) ui + [0, 0, z] - bi ||
```

The preliminary actuator operating keep-out is `15 mm` from each catalogue end: `334 to 508 mm` for the 319 to 523 mm candidate actuator. This is a planning reserve for catalogue-end uncertainty, position-feedback/deceleration allowance, and assembly tolerance. It is neither the final mechanical-stop location nor an approval of the catalogue dimensions.

## Comparison Result

| Candidate | Collapsed device height | Guide outer / inner | Worst actuator soft reserve | Minimum guide overlap | Result |
|---|---:|---:|---:|---:|---|
| WS-01-H0 existing comparison | 250 mm | 190 / 200 mm | about 2.54 mm | 83 mm | Geometrically passes, but too tight for CAD baseline |
| WS-01-H20 recommended | 270 mm | 195 / 220 mm | about 11.13 mm | 88 mm | Recommended for pre-CAD parameter review |

The selected `270 mm` value stays inside the user-confirmed 250 to 300 mm disconnected-height envelope and is mechanically simpler than consuming the actuator retraction margin. The guide length change is needed because raising the collapsed pose without changing the guide would reduce the 100 mm-lift overlap below the existing 80 mm requirement.

## Recommended Candidate: WS-01-H20

| Parameter | Preliminary candidate | Reason |
|---|---:|---|
| Disconnected/collapsed device height | 270 mm | Retains practical lower-end reserve while staying in the approved envelope |
| Platform-joint height increase from older 250 mm layout | 20 mm | Raises the limiting retracted actuator length |
| Required lift from this new collapsed pose | 100 mm | Full user target remains checked |
| Outer keyed guide length | 195 mm | Restores overlap margin without a large package change |
| Inner keyed guide length | 220 mm | Keeps an 88 mm minimum overlap in the full grid |
| Actuator soft operating window | 334 to 508 mm | 15 mm candidate keep-out from 319/523 mm catalogue endpoints |
| Worst retraction-side soft reserve | about 11.13 mm | Occurs at 0 mm lift and a combined +/-3 degree corner |
| Worst extension-side soft reserve | about 73.80 mm | Occurs near 100 mm lift; not the limiting condition |
| Minimum guide-overlap reserve | 8 mm above the 80 mm rule | Occurs at 100 mm lift |

The guide calculations use overlap only. They do not establish guide side-load capacity, friction, wear-pad life, tube buckling, or stop impact capacity.

## Stop And Limit Requirements Carried Into CAD

1. The lower and upper lift hard stops must be separate physical parts. They cannot be the actuator's internal limit or an electrical switch.
2. Electrical upper/lower limit switches must open before the corresponding mechanical stop contact and must not be used as normal positioning feedback alone.
3. CAD must check every permitted pitch/roll and lift-stop contact permutation so that no actuator reaches the actual manufacturer end condition. The 15 mm soft window is a control target, not a claimed hard-stop clearance.
4. The current placeholder guide model puts generic stop blocks inside the guide assembly. It must be replaced by external shoulders/collars or equivalent geometry that cannot obstruct the sliding inner tube.
5. The YAW-A pitch/roll stops are four separate adjustable contacts at +/-7 degrees per yoke axis, as defined in `design_basis/yaw_a_gimbal_kinematic_definition.md`.

## Open Evidence Before Concept Approval

- Confirm the purchased actuator's actual pin-to-pin end dimensions, internal limit behavior, backlash, and deceleration/overshoot.
- Perform the yoke clearance/backlash gauge and the HRT8E 14 degree bracket gauge.
- Establish the lift-stop contact surfaces, their impact/load capacity, and their relationship to actuator endpoints in CAD.
- Recalculate moving/fixed mass split and actuator force after the 270 mm geometry is represented in CAD.

```text
WS-01-H20 SELECTED AS PRE-CAD PARAMETER CANDIDATE
NOT A FABRICATION GEOMETRY OR CONCEPT APPROVAL
```
