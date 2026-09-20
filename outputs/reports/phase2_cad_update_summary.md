# Phase 2 CAD Update Summary - RADIAL_3_CLEAN

Date: 2026-08-27

Status: `RADIAL_3_CLEAN` active after user design feedback; not approved for fabrication.

## Result

- Applied WS-01-H20: 270 mm collapsed height, 100 mm lift, +/-3 deg pitch/roll, 195/220 mm keyed guide.
- Restored three equal actuators as the dominant 120-degree radial tripod.
- Replaced the visually heavy central yoke/bridge with a compact 120 mm Cardan mount and retained the keyed guide only for X/Y/yaw constraint.
- Removed the 300 x 220 mm upper service opening and restored the continuous upper panel.
- Replaced the two central stop cartridges with identical actuator-axis mechanical stop collars and separate electrical limit envelopes on all three actuators.
- Applied official HRT8E 8/23/11 mm geometry and detailed JNT-BR-01 packages at all six actuator joints. The previous 16 mm gap was superseded by an 18 mm seed after the 14 deg projected eye envelope required about 16.24 mm.
- Added boxed mounting plates, four M8 attachment-hole envelopes, replaceable 12x8.2x8 lug bushings, 3.5 mm misalignment spacers and retained M8 shoulder-pin envelopes.
- Added a filtered radial-tripod verification render while retaining compact-guide detail STEP files.
- Added a six-view review pack: top-off internal view, front/side/top orthographic views, layered exploded view and numbered assembly view.
- Replaced the actuator-axis ring placeholders with the LS-01 twin-rod package: fixed carrier, two moving 12 mm rods, four mechanical collars, two electrical trip cams, two slotted D4N brackets and two switch envelopes per actuator.
- Added `ls01_actuator_limit_package_neutral.step`, a color-keyed lengthwise detail render and a separate end view.

## Verification

- `scripts/run_phase2.ps1`: passed.
- Automated tests: 104 passed.
- CAD outputs: 16 files.
- Render outputs: 21 files.
- Artifact hashes: `outputs/phase2/artifact_manifest.json`.

## Next Engineering Work

1. Replace the current bushing, shoulder-pin, spacer and M8x1.25 actuator-adapter envelopes with exact purchased-part dimensions.
2. Complete V-01 physical HRT8E 14 deg two-plane/diagonal sweep, then freeze or revise the 18 mm stack.
3. Replace LS-01 actuator-housing and moving-crosshead attachment envelopes with vendor-approved datums, then measure collar push-off and D4N overrun in V-03.
4. Re-run interference, stroke, limit hierarchy and load calculations after purchased-part dimensions and measured masses are inserted.
5. Release fabrication drawings only after those checks pass and the user separately accepts the frozen package.
