# Profile-only 3-RPS review guide Rev A

## FABRICATION HOLD — 2026-08-31

Do not assemble or order structure from this package. Vendor-image audit found that the LMB-10 base cannot be mounted as modeled, four oblique lower joints cannot use the 90-degree 4035 connector, the PHS6 stack is 15 mm too short, and the 297 mm profile is not an orderable fixed length. See `verification/vendor_interface_audit_2026-08-31.json` and `web_research/vendor_dimension_interface_audit_2026-08-31.md` in the project.

## Recommended Fusion 360 file

Import `step/MINIMAL_3RPS_profile_only_collapsed_revA.step` with Fusion 360 Upload or File > Open. The assembly contains 91 named positioned components. Use the exploded STEP for order and `ACTUATOR_1_complete_joint_detail_revA.step` for the clevis/PHS6 stack.

## Coordinate system and envelope

- Origin: center of the lower 700 x 700 mm frame at its underside.
- +X: right, +Y: rear/A1 direction, +Z: upward.
- Collapsed envelope: 700 x 700 x 299 mm.
- Raised frame-top height: 345 mm at 50 mm nominal common lift.
- Upper motion: Z 0-50 mm, pitch +/-3 deg, roll +/-3 deg. X, Y and yaw are constrained by the three RPS limbs.
- Required actuator pin-center range: 212.368-298.502 mm.
- LM4075OE theoretical range: 205-305 mm; margins 7.368/6.498 mm.

## Former intended assembly order — review only

1. Build the lower 4040 outer square from two 700 mm sides and two 620 mm cross members. Square diagonals before final torque.
2. Install the three lower tangent rails. A1 is 620 mm at Y=295 mm. A2/A3 are 296.696 mm at -59.999/59.999 deg.
3. Side-mount three LMB-10 brackets at support points (0,250), (-216.5,-125), and (216.5,-125) mm. Their pin axes are tangent to the 250 mm support circle.
4. Insert each LM4075OE lower eye into its LMB-10 and fit the 6 mm retained pin.
5. Build the upper 3030 frame from two 700 mm sides and four 640 mm cross members. The two joint rows are Y=250 and Y=-125 mm in upper local coordinates.
6. Capture one M6 hammer-head/T-bolt in each lower 3030 slot and screw the downward male thread into PHS6 with a jam nut. Fit each actuator upper eye to the single side of PHS6 with an M6x50 partial-thread bolt, two washers and a nyloc nut.
7. Install the three compact M10 two-collar stop rods and lower capture-jaw pairs. Set the collars only after the electrical limits have been tested at low speed.
8. Move one actuator at a time, then perform synchronized Z motion, then pitch/roll. Stop immediately if encoder direction, current, or physical clearance differs from the audit.

## Former fabrication concept — withdrawn

- No full-size structural plate, plywood, acrylic deck, welding, drilling or tapping is used in this Rev A structure.
- The former plan assumed profile square cutting and deburring only. That claim is withdrawn until Rev B connection hardware is verified.
- Small catalog connectors, stop brackets, T-nuts and fasteners remain necessary; "profile-only" means the load-carrying frames contain extrusion rather than sheet.

## Release restrictions

- Yellow actuator bodies are planning envelopes reconstructed from retained LM4075OE 100 mm STEP inspection notes. Replace them with the vendor STEP or measured delivered parts.
- Verify LMB-10, PHS6, profile slot standards, actuator eye width/bore, cable exit and M6 single-side articulation on one physical axis before ordering all structure.
- The stop hardware is a compact preliminary arrangement. Confirm collar contact and bracket stiffness in a supervised low-speed bench test.
- This is a PoC digital mock-up, not a certification or a people-carrying design.
