# CR-01 Cart Receiver Hardpoint Screen

Date: 2026-08-25

Status: Phase 1 preliminary hardpoint screen only. Not approved for fabrication.

Related layout: `design_basis/cart_profile_receiver_layout_screen.md`

Calculation: `calculations/cart_receiver_hardpoint_screen.py`

## Purpose

This screen narrows the CR-01 aluminum-profile receiver hard points:

- locator insert
- rest pad insert
- latch keeper
- insert-to-profile fastening
- local stop/keeper tab

The values below are candidate seeds. They are not hole coordinates, cut lengths, fabrication drawings, or purchase-ready specifications.

## Recommended Hardpoint Set

| Hardpoint | Candidate seed | Role |
|---|---|---|
| Locator insert | 12 mm locator interface in 8 mm local steel insert or hardened bushing | Repeatable X/Y seating and shear transfer |
| Secondary locator | Slotted/diamond receiver around the second locator | Yaw control without overconstraint |
| Rest pad insert | 40 x 30 mm contact seed on 8 mm local pad with shim stack | Vertical seating and height adjustment |
| Latch keeper | 5 mm local steel keeper seed | Retention/preload/uplift only |
| Profile fastening | Two M8-class T-slot fasteners per critical hard point as starting topology | Adjustable mock-up fastening |
| Anti-slip feature | Dowel, key, or positive stop after alignment | Final shear/yaw reference, not slot friction |

## Locator Insert Screen

| Item | Value |
|---|---:|
| Pin/interface diameter seed | 12 mm |
| Local insert thickness seed | 8 mm |
| Master locator shear load | about 154 N |
| Yaw couple force at 520 mm span | about 32 N |
| Combined screen load | about 186 N |
| Bearing stress | about 1.94 MPa |

Interpretation:

- Bulk bearing stress is low in the active PoC load screen.
- Use steel or a hardened bushing at repeated locator contact.
- The unresolved risks are seating wear, lead-in geometry, debris tolerance, and final locator hardware selection.

## Rest Pad Insert Screen

| Item | Value |
|---|---:|
| Pad contact seed | 40 x 30 mm |
| Local insert thickness seed | 8 mm |
| Maximum active screened pad load | about 331 N |
| Contact pressure | about 0.28 MPa |

Interpretation:

- Bulk contact pressure is low.
- Four pads should be shim-adjustable because profile assembly tolerance can otherwise leave one pad unloaded.
- Final design should set a practical shim range and locking method before approval.

## Latch Keeper Screen

| Item | 4-latch placeholder | 2-latch minimum check |
|---|---:|---:|
| Per-latch uplift | about 31 N | about 62 N |
| Keeper seed | 25 mm width x 5 mm thickness | 25 mm width x 5 mm thickness |
| Bearing stress | about 0.25 MPa | about 0.49 MPa |

Interpretation:

- Latch keeper bulk bearing is not the active blocker.
- Latches remain preload/uplift/retention items only.
- Secondary lock and latch-closed sensing remain required.

## Profile Fastener Slip Screen

Candidate placeholder:

| Item | Value |
|---|---:|
| Critical fasteners per hard point | 2 |
| Assumed clamp per fastener | 4000 N |
| Assumed friction coefficient | 0.15 |
| Slip demand | about 186 N |
| Slip capacity | about 1200 N |
| Slip margin | about 6.45x |

Interpretation:

- Even a modest clamp assumption screens above the current active load.
- This does not approve friction as the final locating method.
- After alignment, add dowel, keyed plate, shoulder block, or a positive stop so repeatability does not depend on slot friction.

## Local Keeper/Stop Tab Bending Screen

| Item | Value |
|---|---:|
| Load seed | about 154 N |
| Cantilever seed | 25 mm |
| Plate strip seed | 40 mm wide x 6 mm thick |
| Bending stress | about 16 MPa |

Interpretation:

- Local tab bending is not the likely bulk-strength blocker at this load level.
- Geometry, weld-free/bolt-only mounting, edge distance, and fastener placement still need detail review.

## Current Recommendation

Carry forward `CR-01-H1`:

```text
CR-01-H1:
two 760 mm HFS8-4040 receiver rails,
12 mm master locator interface in 8 mm local steel insert,
slotted/diamond secondary locator,
four 40 x 30 mm shim-adjustable rest pad contacts,
5 mm local steel latch keepers,
two M8-class fasteners per critical hard point for mock-up adjustment,
dowel/key/positive stop after alignment.
```

## Open Items Before Parameter Approval

- Exact slot nut and connector type.
- Whether critical hard points use two bolts, four bolts, or a backing/clamp plate.
- Locator hardware family, lead-in angle, and bushing replaceability.
- Rest pad screw/thread size, shim material, and lock method.
- Latch keeper shape, latch approach direction, handle clearance, secondary lock, and latch-closed sensor.
- Edge distances and whether final inserts need dowel pins after alignment.
- Whether the 8 mm insert / 5 mm keeper / 6 mm tab seeds remain practical with local fabrication tools.

```text
CR-01-H1 HARDPOINT CANDIDATE DEFINED
PHASE 1 PRELIMINARY ONLY
NOT APPROVED FOR FABRICATION
```
