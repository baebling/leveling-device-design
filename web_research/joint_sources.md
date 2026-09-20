# Joint Source Notes

Access date: 2026-08-24  
Status: preliminary source notes for Phase 0 screening only.

## SRC-JNT-001: MISUMI PHSOSM8

Source: MISUMI/CADENAS CAD catalog page for PHSOSM/PHSOSLM stainless oil-free rod end bearings.

Extracted use:

- PHSOSM8 radial static load: 2.69 kN.
- Allowable angle: 12 deg.
- Mass: 30 g.

Screening result:

- Too tight for the current primary actuator end joint screen.
- May remain useful for low-load auxiliary linkages, not for the current actuator primary joint without redesign.

## SRC-JNT-004: MISUMI RBLD8-Style Link Ball

Source: MISUMI inCAD rotate and transfer mechanism application page.

Extracted use:

- Rod end link ball M8 static load capacity: 12500 N.
- M8 yield strength value in the table: 6570 N.
- Allowable incline angle table lists 40 deg for the smaller listed thread sizes and 30 deg at M16.

Screening result:

- Passes the current preliminary actuator joint angle/load screen for +/-5 deg and +/-8 deg cases.
- Exact purchasable SKU, holder geometry, bracket clearance, stud/pin load path, wear, and supply route remain unresolved.

## SRC-JNT-005: Ruland Universal Joints

Source: Ruland universal joints product family page.

Extracted use:

- Single U-joint family handles up to 45 deg angular misalignment.
- Double U-joint family handles up to 90 deg angular misalignment.
- Metric bore/keyway options are available in the family.

Screening result:

- Useful component-family reference for a yaw-transmitting central Cardan/u-joint.
- Not an approved SKU. Torque, backlash, axial/radial load, keyway/shaft selection, and mounting still need checking.

## SRC-JNT-007: Ruland MUS15-8-8-F

Source: Ruland product page for an 8 mm x 8 mm single Cardan friction-bearing U-joint.

Extracted use:

- Maximum operating angle: 45 deg.
- Rated torque: 15.3 Nm.
- Outside diameter: 15.8 mm.
- Length: 40.0 mm.

Screening result:

- Passes the angle requirement by a large margin.
- Fails the conservative central yaw torque screen.
- Should only be treated as a compact geometry reference, not as the sole yaw-torque member.

## SRC-JNT-008: Ruland MUSSK22-12-12-F

Source: Ruland product page for a keyed 12 mm x 12 mm single Cardan friction-bearing U-joint.

Extracted use:

- Maximum operating angle: 45 deg.
- Rated torque: 39 Nm.
- Peak torque: 197 Nm.
- Outside diameter: 22.1 mm.
- Length: 50.0 mm.

Screening result:

- Passes the angle requirement.
- Fails the conservative central yaw torque screen when used as the sole yaw-torque path.
- May still be useful if yaw torque is carried through a separate guide/key path and the U-joint only handles articulation.

## SRC-JNT-009: Ruland US32-22MM-20MM-F

Source: Ruland product page for a large 22 mm x 20 mm single Cardan friction-bearing U-joint.

Extracted use:

- Maximum operating angle: 45 deg.
- Rated torque: 485.8 Nm.
- Peak torque: 2429.2 Nm.
- Outside diameter: 50.7 mm.
- Length: 139.7 mm.

Screening result:

- Passes the current conservative central yaw torque screen by torque and angle.
- Kept as a reserve direct-torque Cardan concept because the package is large for the central stack.
- Shaft/key/clamp, backlash, side-load, and cost remain unresolved.

## SRC-JNT-010: MISUMI No.000127 Ball Spline Data

Source: MISUMI inCAD workpiece rotate and transfer mechanism page.

Extracted use:

- Ball spline No.16 dynamic torque rating: 51 Nm.
- Ball spline No.16 static torque rating: 93 Nm.
- Smaller No.6 to No.13 sizes are lower.

Screening result:

- A single 16 mm commercial ball spline fails the current central yaw torque screen.
- Ball spline architecture remains mechanically attractive, but would need a larger family, multiple splines, or a lower approved yaw torque requirement.

## SRC-JNT-006: MinebeaMitsumi HRT8E

Source: MinebeaMitsumi official HRT-E standard rod end bearing catalog page.

Extracted use:

- Bore B: 8 mm.
- Body diameter D: 23 mm.
- Eye width W: 11 mm.
- Center height H: 8.25 mm.
- Center-to-end F: 46 mm.
- Male thread: M8x1.25; thread length L: 29 mm.
- HRT8E alpha angle: 14 deg.
- Radial static limit load: 26.77 kN.
- Axial static limit load: 5.29 kN.
- Static ultimate load: 33.44 kN.
- Fatigue load: 5.54 kN.
- Approximate mass: 40 g.

Screening result:

- Passes the current +/-3 deg baseline actuator joint screen.
- Fails the +/-5 deg stretch angular margin screen.
- The 2026-08-27 CAD check conservatively projects the 23 x 11 mm eye at 14 deg. A flat 16 mm yoke gap is too tight; the active preliminary gap is now 18 mm, leaving about 1.76 mm total numerical clearance.
- Packaging must still preserve the full articulation physically; exact spacers, bracket attachment, threaded actuator adapter and shock/fatigue behavior remain unresolved.
