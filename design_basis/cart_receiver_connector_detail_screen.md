# CR-01-H3 cart receiver connector detail / access screen

Status: Phase 1 preliminary screen. Not approved for fabrication.

## Purpose

CR-01-H2 selected the preferred connector topology: slot fasteners for adjustment and clamp, plus a shoulder/key/positive stop for final locating. CR-01-H3 maps that topology to each hard point so the next designer does not accidentally overconstrain the cart receiver.

This is still not a fabrication drawing. It is a connector-stack and bench-check rule set.

## Hardpoint-specific stack

| Code | Hard point | Role | Constrain | Release | Preliminary stack |
|---|---|---|---|---|---|
| CR-01-H3-L1 | Master locator | Repeatable X/Y location and horizontal shear | X, Y | - | Two M8-class T-slot fasteners plus shoulder/key positive stop; optional dowel after alignment |
| CR-01-H3-L2 | Slotted secondary locator | Yaw reference through separated Y reaction | Y | X | Two M8-class T-slot fasteners plus one-direction shoulder/key stop; do not pin both axes |
| CR-01-H3-RP | Rest pad | Z seating and height trimming | Z | X, Y | T-slot clamp plus accessible shim stack and lock feature |
| CR-01-H3-LK | Latch keeper | Preload/uplift retention and latch-closed sensing | Z uplift retention | primary horizontal shear | T-slot clamp plus local steel keeper; secondary lock and sensor reserve |

## Local bearing and access screen

| Screen | Result | Interpretation |
|---|---:|---|
| Profile wall / stop backing bearing with 3x local load factor | about 1.74 MPa | Low versus the placeholder 30 MPa aluminum bearing screen, but exact profile lip geometry is unresolved |
| Slot nut local clamp pressure with assumed 18 x 12 mm contact | about 18.5 MPa | Passes placeholder screen, but exact slot nut contact and torque are still not approved |
| Minimum tool access clearance seed | 25 mm | Keep shim, latch, and sensor hardware serviceable |
| Sensor envelope reserve seed | 25 x 25 x 35 mm | Placeholder for cart-present and latch-closed sensing only |

## Mock-up acceptance rules

Run at least 30 latch/unlatch/seating cycles before freezing the receiver connector stack.

Add a backing plate or stiffer local stack if any of these occur:

- Hard-point shift exceeds 0.2 mm.
- Fastener torque relaxation exceeds 20%.
- Profile wall marking or indentation appears.
- Latch preload visibly changes after cycling.

Add a dowel only after alignment is finalized and repeatability is more important than slot adjustability.

Reject any detail that:

- Makes the slotted secondary locator block both X and Y.
- Lets the latch hook carry primary horizontal shear.
- Uses an electrical sensor as a mechanical stop.

## Current carry-forward decision

```text
CR-01-H3
master locator fixed in X/Y
secondary locator constrains Y only and releases X
rest pads carry Z seating only
latch keepers carry preload/uplift only
backing plates are conditional after mock-up evidence
```

Before `APPROVE PARAMETERS`, the exact slot nut family, backing plate geometry, stop block shape, dowel position, latch/sensor access, and profile wall bearing detail remain open.
