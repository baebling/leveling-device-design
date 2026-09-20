# CR-01-H4 cart receiver hardware selection screen

Status: Phase 1 preliminary hardware seed. Not approved for fabrication.

## Purpose

CR-01-H3 separated the four cart receiver hard-point roles. CR-01-H4 narrows those rules into a simple, serviceable hardware seed that can be mocked up without pretending that bolt patterns, fits, or supplier part numbers are already approved.

The retained rule is unchanged:

```text
master locator: fixed X/Y
secondary locator: fixed Y and released X
rest pad: Z seating only
latch keeper: preload/uplift only
```

## Recommended seed: CR-01-H4-S1

| Hard point | Preliminary hardware seed | Function and limit |
|---|---|---|
| Master locator | 12 mm removable round locator pin/bushing, 40 x 8 mm replaceable shoulder stop face, two M8-class T-slot clamp fasteners | Fixes X/Y and takes the primary horizontal locating reaction. One 6 mm dowel may be added only after the mock-up alignment is frozen. |
| Secondary locator | 12 mm nominal locator contact in a 20 mm X-slotted or diamond-style receiver seed, two M8-class T-slot clamp fasteners | Fixes Y only and releases X. A second round X/Y pin or X shoulder stop is prohibited. |
| Rest pad | 40 x 30 mm replaceable contact pad, accessible shim pack, two pad-retention screws | Transfers Z seating only. It must not become a side stop or primary horizontal shear path. |
| Latch keeper | 5 mm local steel keeper, separate mechanical secondary lock, separate sensor bracket reserve | Provides preload/uplift retention only. The latch hook and sensors must not be used for horizontal shear or as mechanical stops. |

Keep at least 25 mm tool access for shim, latch, and sensor service. Reserve a 25 x 25 x 35 mm adjustable envelope for each latch-closed and cart-present sensor location.

## First-order screen at local 3x factor

The screen starts from the CR-01-H2 connector demand of about 186 N and applies the existing 3x local uncertainty factor, yielding about 558 N. These are preliminary comparisons against placeholder material allowables, not a release for fabrication.

| Item | Candidate seed | Result | Interpretation |
|---|---|---:|---|
| Master locator bushing bearing | 12 mm pin x 8 mm bushing | about 5.8 MPa | Below the 80 MPa placeholder steel bearing comparison. Keep the contact as a replaceable bushing/insert, not the aluminum profile itself. |
| Replaceable shoulder stop bearing | 40 mm wide x 8 mm contact | about 1.7 MPa | Below the 80 MPa placeholder steel bearing comparison. |
| Replaceable shoulder stop bending | 8 mm local steel stop, 25 mm cantilever seed | about 32.7 MPa | Below the 120 MPa placeholder steel bending comparison. Final screw pattern and edge distance are still open. |
| Optional post-alignment dowel shear | one 6 mm dowel | about 19.7 MPa | Below the 80 MPa placeholder steel shear comparison. Use only after adjustment is no longer required. |
| Rest-pad contact | 40 x 30 mm pad with 3x Z local factor | about 0.8 MPa | Below the 30 MPa placeholder aluminum contact comparison. This is a direct Z seating check only. |

## Backing-plate rule

Start the first mock-up with the two M8-class T-slot fasteners at each critical hard point so the alignment remains adjustable. Add a local 6 mm steel backing bridge, nominal 60 x 40 mm seed, only if the 30-cycle check shows any of the following:

- Hard-point shift greater than 0.2 mm.
- Fastener torque relaxation greater than 20%.
- Profile-wall marking or indentation.
- Latch-preload change after cycling.

This conditional rule avoids adding metal and access difficulty before the low-load PoC proves it is necessary.

## Open before parameter approval

- Exact T-slot nut family, fastener grade, tightening torque, and profile compatibility.
- Final bushing material, fit, retention, and supplier item.
- Final stop-block screw pattern, edge distance, and installation direction.
- Need for the optional dowel after the 30-cycle mock-up.
- Latch model, secondary-lock form, and sensor model/bracket location.

`CR-01-H4-S1` is a Phase 1 hardware selection seed only. It is not an approved fabrication drawing, an assembly instruction, or a purchasing release.
