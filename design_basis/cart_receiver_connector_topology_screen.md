# CR-01-H2 cart receiver connector / positive-stop topology screen

Status: Phase 1 preliminary screen. Not approved for fabrication.

## Purpose

CR-01 and CR-01-H1 define the aluminum-profile receiver rails and local hard points. CR-01-H2 adds the next missing layer: how those hard points should be connected to the profile so that mock-up adjustment is easy, but final locating does not rely on profile-slot friction.

The controlling rule is:

```text
T-slot fasteners may clamp and adjust the hard point.
The final repeatable X/Y/yaw locating path needs a mechanical shoulder, key, dowel, or positive stop.
```

## Basis

- Active low-load baseline: 10 kg payload, about 10 kg empty cart, 22 kg moving structure.
- Receiver demand inherited from CR-01-H1: locator shear plus low-load yaw couple force.
- Calculated connector demand: about 186 N.
- Friction-only slip margin with the placeholder clamp assumption: about 6.45x.

This means bulk strength is not the current blocker. Repeatability, slot creep/slip, assembly adjustment, and avoiding a hidden final friction-only load path are the blockers.

## Candidate topology screen

| Code | Topology | Decision | Reason |
|---|---|---|---|
| CR-01-H2-A | Slot friction only | Reject for final locating | Numeric slip margin passes the placeholder check, but the final locator/yaw path must not be slot friction. |
| CR-01-H2-B | Slot fasteners plus shoulder/key positive stop | Preferred | Keeps easy slot-nut adjustment during mock-up, then gives the aligned hard point a mechanical load path. |
| CR-01-H2-C | Slot fasteners plus backing clamp plate | Reserve | Useful if profile wall stiffness or service adjustment is poor, but heavier and less compact. |
| CR-01-H2-D | Through-bolted crossmember or cart member | Conditional reserve | Robust only if the later cart frame deliberately provides access. Do not infer cart holes or members from images. |

## Preferred CR-01-H2-B seed

| Item | Preliminary value |
|---|---:|
| Critical hard-point clamp | Two M8-class T-slot fasteners per hard point |
| Final shear/yaw path | Replaceable shoulder/key/positive stop face |
| Optional repeatability feature | One 6 mm or larger dowel after mock-up alignment |
| Positive stop contact seed | 40 mm width x 8 mm height |
| Positive stop tab seed | 6 mm thick, 25 mm cantilever screen |
| Backing plate | Reserve only |

Screen result:

- Positive stop bearing: about 0.58 MPa.
- Positive stop local tab bending: about 19 MPa.
- Optional 6 mm dowel shear: about 6.6 MPa.
- Optional 6 mm dowel bearing in 8 mm plate: about 3.9 MPa.

These values are low in the current low-load screen. They do not approve geometry, material, bolt grade, slot nut type, torque, washer stack, profile wall bearing, fatigue, wear, or production tolerance.

## Implementation notes for later CAD

- Use slot nuts first to set locator/rest/latch-keeper positions during bench mock-up.
- After alignment, add a shoulder block, keyed plate edge, dowel, or replaceable stop insert so the slot nuts are not the final locating feature.
- Put the positive stop in the direction of expected shear/yaw reaction, and avoid overconstraining the slotted/diamond secondary locator.
- Keep rest pad shims accessible from above or the side.
- Keep latch keepers as preload/uplift retention only. Locators and rest pads carry shear and seating.
- Keep electrical latch/position sensors separate from the mechanical stop/lock path.

## Approval gate

CR-01-H2 is a topology seed only:

```text
PHASE_1_PRELIMINARY_NOT_FOR_FABRICATION
```

Before `APPROVE PARAMETERS`, the exact profile connector family, slot nut/backing plate stack, shoulder/key/dowel geometry, profile wall bearing, service adjustment method, and cart-side access must be reviewed.
