# LS-01M static-bench actuator-axis mechanical-stop CAD seed

Status: `PHASE_2_PRELIMINARY_NOT_FOR_FABRICATION`

## Purpose

LS-01M is the reduced stationary-bench version of the earlier LS-01 stop/limit cassette. It preserves the active `RADIAL_3_CLEAN` arrangement while removing the external D4N switch, trip-cam and slotted-bracket hardware from the active CAD and BOM.

Each actuator receives:

- one MB21-derived fixed carrier located on the official body-bracket datum,
- two 12 mm moving rods on 104 mm centers,
- one keyed capture crosshead connected to the front-clevis adapter without clamping the chrome rod,
- two mechanical collars per travel direction,
- two replaceable guide bushings.

The electrical travel boundary is the actuator's built-in non-adjustable end-limit path. The external D4N/cam package remains archived research, not an active build item.

## Coordinate conversion

Let `L` be actuator lower-pin to upper-pin length, `s_f = 220 mm` the fixed carrier station from the lower pin, and `o_c = 0 mm` the moving datum at the front-clevis pin centre. A collar or cam at distance `d` behind the crosshead reaches the fixed carrier when:

```text
d = L_contact - o_c - s_f
```

| Event | Actuator length | Offset behind crosshead |
|---|---:|---:|
| Lower mechanical stop | 324 mm | 104 mm |
| Lower commanded boundary | 334 mm | control value only |
| Upper commanded boundary | 508 mm | control value only |
| Upper mechanical stop | 518 mm | 298 mm |

The command boundaries remain inside the mechanical contacts. The actuator's built-in end limits are not adjustable and their actual trip positions must be measured on all three purchased units.

## Geometry seed

| Parameter | Value |
|---|---:|
| Moving rods | 2 x 12 mm diameter x 320 mm |
| Rod center spacing | 104 mm |
| Fixed carrier station | 220 mm from lower pin |
| Moving datum | upper/front clevis pin centre |
| Capture bridge setback | 32 mm behind front pin |
| MB21 official STEP envelope | 50 x 82.854 x 100 mm |
| Guide bushings | 16 mm OD x 12.4 mm bore x 14 mm |
| Mechanical collar envelope | 12 mm bore x 28 mm OD x 11 mm width |

The rod spacing was initially 86 mm. CAD intersection checks found that the 28 mm stop collars and then-active 20 mm trip cams entered the simplified motor-box envelope. Increasing the centers to 104 mm and the carrier width to 132 mm removed those intersections. The D4N/cam hardware was later removed for the stationary-bench variant, but the wider twin-rod layout is retained for collar and carrier clearance.

The earlier 42 mm moving-crosshead station was discarded after separating the official actuator STEP into fixed-body, moving-rod/clevis, and moving-shoulder solids. It did not provide a defensible clevis attachment datum. Moving the datum to the front pin changed the four offsets to 104/109/293/298 mm and required 320 mm rods. A first annular capture entered the upper yoke by 49.57 mm3, so it was removed in favor of two keyed capture straps and a relieved bridge. A 28 mm bridge setback still left 0.99 mm3 at combined pitch/roll; 32 mm clears all named poses in the current preliminary envelopes.

The MB21 bracket spans 170 to 270 mm from the rear pin when centered at 220 mm. The source STEP fixed-body zone is approximately 45.17 to 288.73 mm from the rear pin, leaving about 18.73 mm at the tighter end. These are STEP-derived layout measurements, not toleranced dimensions or proof that MB21 may carry impact stop reaction.

## Static reference

The retained stop reference is 42 kg lifted mass with a 2.0 static factor:

```text
F_package = 42 kg x 9.80665 m/s^2 x 2.0 = 823.8 N
F_equal-share per rod = 411.9 N
12 mm rod axial stress = 3.64 MPa
collar-face average contact pressure = 0.82 MPa
```

For procurement screening, each collar must have verified axial holding or measured push-off of at least 823.8 N, twice the equal-share rod reaction. This target does not approve impact capacity. One-rod load concentration, crosshead bending, carrier attachment, actuator-housing load acceptance, fatigue, contamination, and a falling load remain unresolved.

## Purchased-part reference

- [Ruland MSP-12-FZ official page](https://www.ruland.com/msp-12-fz.html): 12 mm bore, 28 mm OD, 11 mm width, two-piece steel collar, two M4 x 12 screws and 4.6 Nm seating torque. Project-specific push-off and impact acceptance are not published on the referenced page.

The former Omron D4N-4D32 research is retained in the source register only. It is not procured for `LS-01M_STATIC_BENCH_MINIMAL`.

## Required physical validation

1. Ask Firgelli whether MB21 and the actuator housing may carry the calculated external stop reaction and impact. If not, replace it with a lower-yoke-mounted fixed frame.
2. Build and sweep one JNT-CG-01 factory-eye cradle and keyed crosshead; confirm it never clamps or side-loads the chrome rod.
3. Measure actual pin-to-pin endpoints and internal-limit positions for all three purchased actuators.
4. Apply a controlled static push-off test to each collar above 823.8 N, then perform low-speed end tests with no person under or on the platform.
5. Replicate the cassette only after one complete actuator module passes the fit and motion check.

No part of this package is approved for fabrication, certification, or carrying people.

See `design_basis/firgelli_mount_datum_review_2026-08-27.md` for the archived STEP hashes and datum decision.
