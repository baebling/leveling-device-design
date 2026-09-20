# Mechanism Comparison After Web-Based Parameter Review

Status: Phase 0 concept comparison, revised after feedback. Preliminary only. Not approved for parameter freeze or fabrication.

Current-use note: after the 2026-08-25 user clarification, the active review baseline is 10 kg carried payload and +/-3 deg pitch/roll with simple fabrication/assembly priority. See `design_basis/user_confirmed_scope_2026-08-25.md`.

## Scope

This comparison is limited to the leveling/lifting upper module, universal lower mounting interface, and mechanical cart coupling interface. It does not define the AMR/AGV, wheel unit, drive unit, navigation system, robot arm, or cart body.

## Coordinate and DOF basis

- X: lateral direction in the upper platform plane.
- Y: fore-aft direction in the upper platform plane.
- Z: vertical lift direction.
- Permitted active upper-platform DOF: Z translation, pitch, roll.
- Mechanically constrained DOF: X translation, Y translation, yaw.

## Alternatives

| Alternative | Description | Benefits | Main risks | Phase 0 result |
|---|---|---|---|---|
| A | Three inclined actuators determine the upper plane; central guide concept must constrain X/Y/yaw while allowing pitch/roll | Avoids four-point overconstraint, low part count, good lift/pitch/roll authority, cart interface space remains open | Actuator axial load grows with shallow geometry and eccentric load; central guide mobility is critical-open | Retain as concept direction only |
| B | Four corner actuators support the platform | Familiar layout and corner support | Overconstraint, synchronization sensitivity, higher cost and controller burden | Rejected for PoC baseline |
| C | Separated Z lift stage plus pitch/roll gimbal or nested axes | Clear DOF separation | Taller stack, more bearings, more interface conflicts, higher fabrication complexity | Rejected for current budget/scope |

## Why Alternative A remains the concept direction

The web-based component review and later feedback do not invalidate the earlier Phase 1 decision matrix. They do change the approval status:

- The current 450 lbf class actuator is a candidate only, not a frozen purchase item.
- Pitch/roll +/-3 deg remains a reasonable target, but not yet an approved full-workspace claim.
- +/-5 deg can be kept as a stretch target if actuator force margin, joint angle, and stop geometry are reviewed.
- +/-8 deg should stay a sensitivity case, not a selected target for the current hardware.
- The cart latch must not carry primary shear. Locating pins, rest pads, and side constraints should carry X/Y/yaw and shear; latches provide seating preload and uplift restraint.
- The central guide must be reworked as a critical-open item. A simple keyed telescoping guide may overconstrain pitch/roll and bind.

## Phase gate

No additional detailed CAD, fabrication drawings, or manufacturing exports should be created from these values. Before a future `APPROVE PARAMETERS` gate, resolve central guide mobility, coupled workspace, moving/fixed mass split, power architecture, and control/safety interlocks.
