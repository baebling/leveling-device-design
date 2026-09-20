# RADIAL_3_CLEAN Active CAD Baseline

Date: 2026-08-26

Status: Active Phase 2 preliminary CAD. Not approved for fabrication.

## User Decision

The first post-approval CAD made the central gimbal, bridge, and stop cartridges too visually dominant. The user requested a return to the existing three-actuator radial design. `RADIAL_3_CLEAN` is now the active variant.

## Active Layout

- Three identical linear actuators are placed at 120-degree intervals.
- The upper joints remain on a 400 mm radius and the lower joints on the concentric approximately 91.33 mm radius.
- The three actuator lengths directly generate Z, pitch, and roll.
- The center retains only a compact 50/42 mm keyed telescopic guide and a Cardan mount no larger than 120 x 120 mm.
- The central part constrains X, Y, and yaw; it is not a fourth lifting leg or a visual frame feature.
- The upper 900 x 800 panel is continuous again, without the rejected 300 x 220 mm service opening.
- Mechanical stop collars and separate electrical-limit envelopes are duplicated symmetrically on all three actuator axes.

## Preserved Engineering Values

- WS-01-H20: 270 mm collapsed device height and 100 mm lift.
- Pitch/Roll requirement: +/-3 degrees.
- Gimbal stop seed: +/-7 degrees per axis, below the 10-degree diagonal total envelope.
- Guide lengths: 195 mm outer and 220 mm inner with at least 88 mm overlap in the screened raised corner.
- JNT-BR-01: official HRT8E 8/23/11 mm envelope, 8 mm pin/lug, revised 18 mm inner support gap, replaceable lug bushings and retained pin hardware envelopes. The revision is detailed in `design_basis/actuator_joint_detail_cad_2026-08-27.md`.

## Archived Variant

The large three-body YAW-A bridge and two central passive stop cartridges are retained at:

- `cad/variants/yaw_a_detailed_2026_08_26.py`
- `cad/variants/upper_interface_yaw_a_detailed_2026_08_26.py`
- `outputs/archive/yaw_a_detailed_2026-08-26/`

They are `archived_not_preferred` and must not become active again without explicit user direction.

## Remaining Work

- Replace limit-envelope rings with selected switch brackets and real mating stop shoulders.
- Confirm that actuator-axis collars can carry the required static stop reference and expected overrun without loading the rod improperly.
- Add exact Cardan bushings, shoulder bolts, retention, and frame attachment.
- Recheck full-pose interference after actual actuator and rod-end drawings are inserted.
- Keep all drawings preliminary until V-01 through V-06 evidence is complete.
