# Phase 2 Detailed CAD Baseline - 2026-08-26 (Superseded Visual Variant)

> Superseded by `radial_3_clean_baseline_2026-08-26.md` after user feedback that the large central gimbal and stop-cartridge design was visually unacceptable. Retained only as an archived engineering attempt.

## Status

The user entered the exact approval phrase `APPROVE CONCEPT` on 2026-08-26. This authorizes Phase 2 detailed parametric CAD. It does not authorize fabrication, certify safety, or close the physical evidence plan.

## Implemented Baseline

- Workspace: WS-01-H20, 270 mm disconnected/collapsed device height, 100 mm Z lift, +/-3 deg pitch and roll.
- Actuator geometry: 185 mm collapsed vertical joint separation, 308.666 mm preserved radial horizontal offset, 359.873 mm level/collapsed actuator length.
- Central guide: 50 x 50 x 3 mm outer square tube, 195 mm outer length, 42 x 42 x 3 mm inner tube, 220 mm inner length, replaceable UHMW yaw shims.
- Gimbal order: lower fixed +Y pitch axis, intermediate pitch-moving ring, upper local +X roll axis, `R = Ry(pitch) Rx(roll)`.
- Angular stops: independent +/-7 deg pitch and roll stop seats; diagonal total tilt remains about 9.89 deg inside the 10 deg total envelope.
- Lift stops: two passive telescopic captured-shoulder cartridges outside the central guide bore. Electrical switch envelopes are separate parts.
- Actuator joints: JNT-BR-01 seed with 8 mm pin, 8 mm lugs, 16 mm maximum inner support gap, and HRT8E-style eye envelopes.
- Upper interface: 300 x 220 mm central service opening and a 360 x 70 x 8 mm gimbal bridge tied into the inner HFS8 rails.

## CAD Motion Bodies

1. `keyed_guide_outer` and `gimbal_lower_pitch_yoke` are fixed in X/Y/yaw and translate only with the lower structure reference.
2. `keyed_guide_inner`, `guide_moving_stop_bar`, and the lower yoke translate in Z without pitch/roll.
3. `gimbal_intermediate_ring` follows pitch only.
4. `gimbal_upper_roll_yoke` and the upper platform follow pitch and roll.
5. No third azimuth joint is modeled.

## Generated Evidence

- Full assembly STEP states: collapsed, neutral, raised, max pitch, max roll, max pitch+roll, and cart disengaged.
- Central detail STEP states: `guide_gimbal_neutral.step` and `guide_gimbal_max_pitch_roll.step`.
- Full assembly and filtered central-detail renders, including neutral and +3/+3 deg limit views.
- GLB, preliminary DXF/STL outputs, calculation reports, BOM, and SHA-256 artifact manifest.
- Full automated test result: 94 tests passed.

## Rejected CAD Attempts and Corrections

- The old solid blocks at the ends of the square guide obstructed the sliding bore. They were removed.
- The first external-stop concept used fixed vertical posts. In the collapsed pose they pierced the upper deck and protruded into the payload surface. Render and pairwise intersection checks exposed the problem, so the posts were replaced with below-deck passive telescopic stop cartridges.
- The first detail render included the complete platform and hid the gimbal. Rendering now supports a component filter for central-mechanism verification views.
- After making 270 mm the global CAD baseline, the workspace comparison script added another 20 mm to WS-01-H20. Candidate offsets were corrected to absolute 250/270 mm references.
- CadQuery's XZ workplane extrudes along negative Y. The pitch pin was initially translated in the wrong direction and intersected an upper cross rail; its centering translation was corrected.

## Remaining Limits

- HRT8E eye width, washer stack, body envelope, load direction, and 14 deg no-contact motion are not verified from an actual purchased drawing/mock-up.
- Gimbal stop tabs are parametric seat envelopes, not tolerance-complete adjustable stop hardware.
- Passive stop cartridges are a packaging seed; exact shoulder geometry, rated stop load, end cushioning, and purchased/fabricated implementation remain open.
- UHMW shim thickness, fit, wear, contamination, and measured yaw freeplay remain open.
- Exact bolt holes, bushings, pin retention, weld/bolt joining, edge distances, and fastener torque are not frozen.
- CAD mass properties are not yet reconciled with a measured 10 kg cart and the moving/fixed mass split.
- Electrical limit switch cams, overrun, homing, power isolation, channel protection, and latch/cart interlocks remain open.

All geometry remains `PRELIMINARY - NOT APPROVED FOR FABRICATION`.
