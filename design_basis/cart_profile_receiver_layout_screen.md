# Cart Profile Receiver Layout Screen

Date: 2026-08-25

Status: Phase 1 preliminary layout screen only. Not approved for fabrication.

Related concept note: `design_basis/cart_profile_receiver_concept_2026-08-25.md`

Calculation: `calculations/cart_profile_receiver_screen.py`

Hardpoint follow-up: `design_basis/cart_receiver_hardpoint_screen.md`

## Coordinate Basis

Use the same project coordinate convention:

| Axis | Meaning |
|---|---|
| X | device length direction, nominal 900 mm envelope |
| Y | device width direction, nominal 800 mm envelope |
| Z | vertical |

Origin is the nominal device center. No cart dimension is inferred from images.

## Preferred Preliminary Receiver Zone

The current preferred cart-side receiver zone is a light two-rail kit, not a full cart frame:

| Item | Candidate seed |
|---|---:|
| Receiver outer length | 760 mm |
| Receiver outer width | 560 mm |
| Longitudinal rail count | 2 |
| Longitudinal rail length | 760 mm each |
| Rail centerline Y positions | +/-260 mm |
| Rest pad X span | 620 mm |
| Rest pad Y span | 520 mm |
| Locator X span | 520 mm |
| Master locator seed | X -260 mm, Y 0 mm |
| Slotted/diamond secondary locator seed | X +260 mm, Y 0 mm |
| Latch placeholder count | 4 |
| Latch seed positions | +/-330 mm X, +/-260 mm Y |

Interpretation:

- Two longitudinal aluminum-profile receiver rails are the preferred backbone.
- Cross support belongs to the new cart lower frame and is not designed here.
- Local hard points are bolted to the rails or adjacent cart-frame members.
- The positions above are receiver-zone seeds, not hole coordinates.

## Mass Screen

The hard-point allowance is a placeholder containing rest blocks, locator plates, latch keepers, stop tabs, and fasteners. It is not a BOM.

| Layout | Profile basis | Profile length | Profile mass | Hard-point allowance | Total receiver mass | Status |
|---|---|---:|---:|---:|---:|---|
| Two-rail receiver kit | HFS8-4040 | 1.52 m | 2.63 kg | 1.87 kg | 4.50 kg | Preferred |
| Self-contained rectangular receiver | HFS8-4040 | 2.64 m | 4.57 kg | 1.87 kg | 6.43 kg | Heavier reserve |
| Two-rail stiff reserve | GFS8-4040 | 1.52 m | 3.30 kg | 1.87 kg | 5.16 kg | Stiffness reserve |
| Self-contained stiff rectangular reserve | GFS8-4040 | 2.64 m | 5.73 kg | 1.87 kg | 7.60 kg | Reject for 10 kg cart target unless mass target changes |

Current reading:

- The two-rail HFS8-4040 receiver kit uses about 45% of the 10 kg empty-cart basis.
- A self-contained rectangular subframe can work structurally, but it consumes too much of the 10 kg cart mass budget for a simple PoC.
- If 40 mm profile feels too heavy after the full cart frame is sketched, a 30 mm profile family may be studied, but it needs its own source-backed mass/stiffness data before parameter approval.

## Rest Pad Screen

Using the active low-load worst interface moment from `calculations/interface_moments.py`:

| Item | Value |
|---|---:|
| Vertical design load | about 824 N |
| Worst roll moment in active screen | about 108 Nm |
| Rest pad X span | 620 mm |
| Rest pad Y span | 520 mm |
| Base load per pad | about 206 N |
| Maximum screened pad load | about 331 N |
| Minimum screened pad load | about 81 N |

All four pads remain in compression in this simplified active screen. Shim adjustment is still required because profile assembly tolerances can otherwise leave one pad unloaded.

## Locator And Latch Screen

Using the current low-load latch and yaw screens:

| Item | Value |
|---|---:|
| Guide/locator shear design load | about 154 N |
| Master locator single-point shear if it carries all horizontal shear | about 154 N |
| Shared shear if two locators share load | about 77 N each |
| YAW-A design yaw torque reference | about 16 Nm |
| Yaw couple force at 520 mm locator span | about 32 N |
| Total latch uplift design load | about 124 N |
| Per-latch uplift with 4 latches | about 31 N |

The latch remains a retention and preload item only. The receiver geometry, locators, rest pads, and local stop faces should carry horizontal shear and repeatable alignment.

## Current Recommendation

Carry forward the following candidate:

```text
CR-01: two longitudinal HFS8-4040 receiver rails,
760 mm long, 560 mm receiver-zone width,
master locator + slotted/diamond secondary locator,
four shim-adjustable rest pads,
two minimum / four placeholder mechanical latches,
local metal hard points for all concentrated contact.
```

Carry as reserves:

- `CR-02`: self-contained HFS8 rectangular subframe if the cart frame cannot provide cross support.
- `CR-03`: GFS8 two-rail reserve if the HFS8 rail connector stiffness fails.
- `CR-04`: 30 mm-class profile study if the final cart mass exceeds the 10 kg target. This requires new source-backed profile data.

## Open Items Before Parameter Approval

- Exact profile family and local procurement code.
- Connector style, slot nut type, and CR-01-H1 dowel/keyed plate/positive stop details after alignment.
- Insert plate material and thickness.
- Locator hardware size and seating geometry.
- Rest pad thread, shim, or eccentric adjustment method.
- Latch keeper geometry, release clearance, secondary lock, and latch-closed sensing.
- Confirmation that the full cart including receiver stays near the 10 kg empty-cart target.

```text
CR-01 RECEIVER LAYOUT CANDIDATE DEFINED
PHASE 1 PRELIMINARY ONLY
NOT APPROVED FOR FABRICATION
```
