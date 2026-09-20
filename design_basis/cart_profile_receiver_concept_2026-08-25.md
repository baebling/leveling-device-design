# Aluminum Profile Cart Receiver Concept

Date: 2026-08-25

Status: user preference recorded. Phase 1 preliminary concept only; not approved for fabrication.

Layout screen: `design_basis/cart_profile_receiver_layout_screen.md`

Hardpoint screen: `design_basis/cart_receiver_hardpoint_screen.md`

## Scope

This note defines only the mechanical receiver/interface zones for coupling the leveling device to a new cart lower frame.

It does not design the cart body, wheels, casters, drive system, navigation system, AMR/AGV base, or payload rack.

## User Decision

The user chose an aluminum profile frame direction for the cart-side receiver/interface.

Interpretation for Phase 1:

- Use bolt-together aluminum T-slot/profile members as the adjustable receiver frame.
- Keep welding to a minimum.
- Keep profile slot adjustment available during mock-up alignment.
- Do not rely on the aluminum profile slot faces themselves as the final locating, wear, or shear surfaces.
- Use local metal insert plates, bushings, rest pads, latch keepers, or dowel plates wherever repeated seating or concentrated contact occurs.

## Recommended Preliminary Architecture

The current preferred receiver structure is:

```text
new cart lower frame
  -> aluminum profile receiver rails / rectangular subframe
  -> bolted local steel or aluminum hard-point plates
  -> rest pads + one master locator + one slotted/diamond secondary locator
  -> mechanical latches with secondary lock and latch-closed sensing
  -> leveling device lower interface
```

Recommended layout principles:

| Item | Preliminary direction | Why |
|---|---|---|
| Receiver structure | Bolt-together aluminum profile rails or shallow subframe | Easy fabrication, adjustment, and rework |
| Profile class | 30 mm or 40 mm class T-slot/profile; exact section TBD | 30 mm helps the 10 kg cart target; 40 mm helps local stiffness and compatibility |
| Local hard points | Separate insert plates for pins, rest pads, latch keepers, and stop blocks | Avoids fretting or wear on raw profile slots |
| Primary locator | One round/tapered master locator | Defines repeatable X/Y seating |
| Secondary locator | One slotted or diamond locator | Adds yaw control while avoiding overconstraint |
| Rest support | Four shim-adjustable rest pads near the receiver corners or load paths | Carries vertical seating load without using latch hooks as supports |
| Latches | 2 minimum, 4 still acceptable as a placeholder for symmetric preload | Latches retain/preload; they do not carry primary horizontal shear |
| Adjustment | Slot adjustment for mock-up, then fixed with dowels, clamp plates, or keyed plates after alignment | Prevents the final interface from depending only on friction |

The current layout candidate carried forward from the first screen is `CR-01`: two 760 mm HFS8-4040 longitudinal receiver rails inside a 760 mm x 560 mm receiver zone. The current hardpoint seed is `CR-01-H1`.

## Candidate Parameter Seeds

These are layout seeds for the next Phase 1 review. They are not manufacturing dimensions.

| Parameter | Candidate seed | Status |
|---|---:|---|
| Device footprint reference | 900 mm L x 800 mm W | Existing target, not image-derived |
| Disconnected device height envelope | 250 to 300 mm | User confirmed |
| Receiver rail direction | Prefer two longitudinal rails along the 900 mm direction | Provisional |
| Receiver rail span | Keep as a parameter inside the 800 mm width envelope | Open |
| Locator span | Maximize practical X/Y separation inside the receiver envelope | Open |
| Rest pad count | 4 | Provisional |
| Latch count | 2 minimum; 4 placeholder for current low-load screen | Open |
| Latch function | Preload/uplift/retention only | Fixed principle |
| Horizontal shear path | Locators, rest geometry, and receiver hard points | Fixed principle |
| Aluminum profile role | Adjustable frame/backbone | User preferred |
| Steel or hard insert role | Local contact, wear, pin bearing, latch keeper, stop face | Provisional hard rule |

## Low-Load Screen Link

The current user-confirmed low-load screen remains the sizing reference:

| Screen item | Current value |
|---|---:|
| Lifted mass baseline | 42 kg |
| Actuator force baseline | about 618 N |
| Active interface vertical design load | about 618 N |
| Active worst interface moment | about 108 Nm |
| Active guide-pin shear design load | about 154 N |
| Active total latch uplift design load | about 124 N |
| Active per-latch uplift with 4 latches | about 31 N |
| YAW-A design yaw torque | about 16 Nm |

These values are low enough that the main receiver risks are not bulk profile strength. The main risks are joint slip, local bearing/wear, backlash, latch geometry, profile connector stiffness, and tolerance stack-up.

## Practical Risks To Carry Forward

- A full 40 x 40 profile cart frame can consume the 10 kg cart mass budget quickly; use 40 mm class members only where they are useful.
- Profile slot friction alone should not be trusted as the final anti-slip or yaw reference after repeated coupling.
- Locating pins should seat into replaceable or well-supported inserts, not directly into soft slot edges.
- Rest pad heights should be shim-adjustable so the cart does not rock on three accidental high points.
- Latch handles and release directions must stay outside the actuator, central guide, and pinch-zone envelope.
- Final profile section, connector type, fastener size, and bracket plate thickness still need source-backed selection before `APPROVE PARAMETERS`.

## Next Work

1. Convert this concept into a parametric receiver-zone sketch using variables, not fabrication drawings.
2. Choose whether the cart-side receiver uses 30 mm class profile generally with 40 mm local rails, or one consistent 40 mm profile family.
3. Recalculate latch/locator loads after choosing locator span and latch positions.
4. Keep the cart mass estimate close to 10 kg by separating the receiver hardware mass from any future cart body mass.

```text
ALUMINUM PROFILE RECEIVER DIRECTION RECORDED
PHASE 1 PRELIMINARY ONLY
NOT APPROVED FOR FABRICATION
```
