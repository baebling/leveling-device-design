# Fusion 360 import and rejected-assembly review guide - Rev B

## Current release state

**REJECTED - DO NOT FABRICATE OR PURCHASE FROM THIS PACKAGE.** A later assembly-axis audit found that both 4035/DCB connector fasteners were modeled vertically, the one-sided PHS6 offset produces a 3.549 degree actuator/pin-axis error at zero tilt, and the support azimuth gaps are 90/90/180 degrees instead of the requested 120/120/120 degrees. STEP files are retained only to reproduce and inspect the failure.

## Recommended Fusion 360 file

For failure review only, import `step/MINIMAL_3RPS_profile_only_collapsed_revB.step`. It contains 80 named positioned components. Do not treat the exploded STEP as a valid assembly sequence.

## Coordinate system and envelope

- Origin: lower 700 x 700 mm frame center at its underside.
- +X: right, +Y: A1/rear direction, +Z: upward.
- Collapsed envelope: 700 x 700 x 296 mm.
- Upper motion: common Z lift 0-50 mm, pitch +/-3 deg, roll +/-3 deg.
- Actuator pin-center demand: 225.002-280.344 mm.
- LM4075OE nominal range: 205-305 mm; margins 20.002/24.656 mm.

## Rejected assembly sequence

1. Build the lower orthogonal 4040 grid: two 700 mm sides, three 620 mm cross members at Y=330/-330/-10, and the 300 mm A1 rail from Y=10 to 310. Use eight 4035 brackets and two M8 fasteners per bracket.
2. Top-mount each LMB-10. Put its pin center at A1=(0,65), A2=(-75,-10), A3=(75,-10) mm and its second base feature 36 mm inward. Both M8 fasteners share one profile slot.
3. Place each actuator lower eye in the 20 mm LMB opening. Fit the included 6 mm pin only after checking that the delivered eye width is at most 20 mm and the retainer is included.
4. Build the upper 3030 grid: two 700 mm sides and four 640 mm cross members at local Y=335/-335/240/-10. Use eight DCB3025 brackets and two M6 fasteners per bracket.
5. Capture one TB306 M6x20 head in each lower 3030 slot. Use a 5 mm jam nut and screw PHS6 onto the remaining 12.5 mm nominal thread engagement. Lock the jam nut with medium-strength threadlocker.
6. Put the PHS6 ring on one side of the actuator upper eye. Fit the M6x50 half-thread bolt, two flat washers and measured shims so the 32 mm plain shank spans both bearing surfaces. Use a prevailing-torque nut without clamping the PHS6 inner ring against its outer body.
7. Install three mechanically independent stop rods/catches only after the selected catalog arrangement reproduces the CAD clear opening. Electrical limit switches do not replace these stops.
8. With no payload, move one actuator at a time at low speed. Then test common Z, pitch and roll while checking current, encoder direction, cable clearance, pin retention and stop contact.

## Fabrication operations

- No full-size plate, plywood, acrylic structural deck, welding, drilling or tapping is required by the Rev B profile frame.
- Profiles are fixed-length NAVIMRO cuts. Only square cutting and deburring are required at the supplier.
- The stop capture remains a catalog-combination placeholder and cannot be ordered from this package yet.

## Open receipt checks

- LM4075OE eye axial width, bore, cable-exit envelope and actual 205/305 mm pin-center lengths.
- LMB-10 included pin diameter, usable grip length and positive retainer.
- M6x50 upper pivot washer/shim stack and prevailing-torque nut SKU.
- Final M10 stop rod, collars, catch brackets and profile fasteners.

This is a rejected fixed indoor low-speed 10 kg PoC digital mockup, not a fabrication release, certification, or people-carrying design.
