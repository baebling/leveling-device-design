# Cart receiver connector detail summary

Status: Phase 1 preliminary. Not approved for fabrication.

CR-01-H3 maps the preferred CR-01-H2-B connector topology onto each cart receiver hard point.

## Current conclusion

Carry forward:

```text
CR-01-H3
master locator: fixed X/Y
secondary locator: Y only, X released
rest pads: Z seating only
latch keepers: preload/uplift only
```

The important practical rule is that the secondary locator must stay slotted/diamond-like. If it is pinned round in both X and Y, the receiver becomes overconstrained and will be harder to assemble repeatably.

## Screened values

| Item | Result |
|---|---:|
| Profile wall / stop bearing with 3x local factor | about 1.74 MPa |
| Slot nut clamp contact pressure, assumed 18 x 12 mm contact | about 18.5 MPa |
| Mock-up cycle count before freezing connector stack | 30 cycles |
| Maximum hard-point shift before adding backing/stiffer stack | 0.2 mm |
| Maximum fastener torque relaxation before adding backing/stiffer stack | 20% |
| Minimum tool access seed | 25 mm |
| Sensor envelope reserve seed | 25 x 25 x 35 mm |

## Remaining blockers

- Exact slot nut family and contact geometry.
- Profile wall bearing, indentation, and torque retention after physical cycling.
- Backing plate shape if cycling fails.
- Replaceable stop block shape and access.
- Dowel position after mock-up alignment.
- Latch-closed and cart-present sensor bracket placement.

This remains:

```text
PHASE_1_PRELIMINARY_NOT_FOR_FABRICATION
```
