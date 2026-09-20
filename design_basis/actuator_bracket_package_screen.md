# JNT-BR-01 HRT8E actuator bracket package

Status: Phase 2 detailed CAD seed updated 2026-08-27. Not approved for fabrication.

## Purpose

The HRT8E-style M8 rod end remains the leading simple actuator-end candidate for the user-confirmed +/-3 degree PoC. JNT-BR-01 keeps the actuator force and pin axis intersecting at the spherical-bearing center, so the threaded shank is not used as a bending spacer.

The package is now represented by preliminary detailed CAD with boxed double-shear lugs, replaceable bushings, misalignment-spacer envelopes and retained shoulder-pin hardware. It is not a fabrication drawing or purchased-bracket release.

## Official HRT8E inputs

MinebeaMitsumi data was rechecked on 2026-08-27: 8 mm bore, 23 mm body diameter, 11 mm eye width, 8.25 mm center height, 46 mm center-to-end, M8x1.25 thread, 29 mm thread length and 14 deg articulation. The actuator-axis screen continues to use the lower 5.29 kN axial static value instead of the 26.77 kN radial value.

## Coordinate system and load path

Set the spherical-bearing center as `J`.

```text
+X: neutral actuator force line toward the actuator
+Y: through-pin axis
+Z: completes the right-hand frame
```

The actuator resultant and pin axis must intersect at `J`. The M8 threaded shank provides thread engagement to the actuator-side adapter only.

## Active detailed seed

| Item | Preliminary seed | Rule |
|---|---|---|
| Bracket form | Two symmetric 8 mm steel lugs tied into a boxed base yoke | Do not use a single thin lug as the primary pin support. |
| Pin | 8 mm shoulder-pin envelope in double shear | Exact pin grade, shoulder length and positive retention remain open. |
| Loaded pin support span | 18 mm between lug inner faces | Revised from 16 mm after applying the official eye envelope. Recalculate if the real stack is wider. |
| Lug section | 8 mm thickness, at least 32 mm load width, no more than 30 mm free root-length seed | Final edge distance, outline and joining detail remain open. |
| Lug bushings | 12 mm OD x 8.2 mm ID x 8 mm replaceable envelopes | Final fit, material and retention remain open. |
| Misalignment spacers | 3.5 mm per side, 10.8 mm OD envelope | Exact purchased or turned detail remains open. |
| Bracket attachment | Four M8 clearance-hole envelopes per boxed yoke | Final backing plate, joint method, torque and edge distances remain open. |
| Articulation | No contact through the full 14 deg catalogue envelope | Numerical projection is not a substitute for V-01. |
| Fallback | RBLD8-style high-angle link-ball package | Use only if the physical HRT8E package fails. |

## Clearance revision

The earlier 16 mm gap was too tight once the official body dimensions were used. A conservative flat-lug projection gives:

```text
projected width = 11*cos(14 deg) + 23*sin(14 deg)
                = about 16.24 mm
```

The active 18 mm gap leaves about 1.76 mm total numerical clearance, or about 0.88 mm per side. Chamfers, real spherical insert geometry, spacer shape and tolerances are not fully represented, so physical proof remains mandatory.

## Active low-load screen

| Check | Candidate result | Interpretation |
|---|---:|---|
| Required articulation | about 12.94 deg | About 1.06 deg remains against the 14 deg catalogue value. |
| Pin double shear | about 8.7 MPa | Below the 100 MPa placeholder comparison. |
| Pin bending | about 78.5 MPa | 8 mm pin with 18 mm support span; below the 150 MPa placeholder comparison. |
| Lug bearing | about 13.7 MPa | Below the 100 MPa placeholder comparison. |
| Lug-root bending | about 38.5 MPa | Below the 150 MPa placeholder comparison. |
| 14 deg projected eye clearance | about 1.76 mm total | Numerical envelope only. |

These comparisons do not establish material grade, weld capacity, fatigue life, shock resistance, thread engagement, fits or final pin retention.

## Rejected load paths

- Single-shear primary lug.
- Any threaded-shank standoff that puts a bending moment into the M8 root.
- A bracket that contacts the rod-end body before full required articulation.
- A pin support span wider than 18 mm without a new calculation.

## V-01 physical acceptance

1. Confirm official dimensions against the physical HRT8E.
2. Record the real spacer, shoulder-pin, retainer and actuator-thread adapter stack.
3. Make a low-cost gauge from the detailed CAD seed.
4. Sweep 14 deg in both principal planes and the diagonal combination with no contact.
5. Measure the support span and recalculate if it exceeds 18 mm.
6. Confirm retention hardware cannot rub the moving rod end.

Open items are the actuator-thread adapter, exact spacer and pin hardware, bushing fit, lug material and joining, bracket attachment, edge distances, fatigue/shock validation and the physical V-01 sweep.
