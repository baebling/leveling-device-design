# User-Confirmed Simplified PoC Scope

Date: 2026-08-25

Status: design-scope clarification from user. Preliminary only; not approved for fabrication.

## Confirmed Direction

The user clarified that the design does not need high load capacity or high tilt range.

Current Phase 0 baseline should therefore be:

| Item | Confirmed baseline |
| --- | --- |
| Carried material payload | 10 kg |
| Empty cart mass | about 10 kg expected |
| Cart design basis | Cart can be designed around the leveling device |
| Pitch implementation target | +/-3 deg |
| Roll implementation target | +/-3 deg |
| Disconnected leveling-device height envelope | 250 to 300 mm |
| Higher load cases | Not required for the primary PoC |
| +/-5 deg pitch/roll | Future stretch only, not a current requirement |
| +/-8 deg pitch/roll | Sensitivity/archive only |
| Cart receiver fabrication preference | Bolt-together aluminum profile |
| Design priority | Easy machining, fabrication, assembly, and adjustment |

Important interpretation:

```text
10 kg is the carried material payload.
The current primary cart mass basis is also about 10 kg.
Actuator force still includes the empty cart mass and moving upper-module mass.
```

## Updated Load Screen

`calculations/user_confirmed_baseline.py` adds a reproducible low-load PoC screen.

Baseline assumptions until the real cart is measured:

| Item | Value |
| --- | --- |
| Material payload | 10 kg |
| Primary empty cart mass | 10 kg |
| Heavy-cart sensitivity | 20, 30 kg archive/check cases |
| Moving structure sweep | 15, 22 kg |
| Pitch/roll | +/-3 deg |
| Baseline design factor | 1.5 |
| Baseline X/Y eccentricity | 50 mm |
| Sensitivity design factor | 2.0 |
| Sensitivity X/Y eccentricity | 100 mm |

Current baseline result:

| Result | Value |
| --- | --- |
| Primary screened total lifted mass | 42 kg |
| Primary baseline actuator axial force | about 618 N |
| Firgelli reference actuator rating | about 2002 N |
| Baseline force margin | about 3.24x |
| DF 2.0 / 50 mm eccentricity sensitivity force | about 824 N |
| DF 1.5 / 100 mm eccentricity sensitivity force | about 729 N |
| Heavy-cart 30 kg sensitivity force | about 912 N |

This means the current Firgelli 450 lbf actuator candidate can remain the leading low-load PoC actuator candidate, pending packaging, stroke margin, current, duty, and bracket checks.

Current interface/latch screen:

| Result | Value |
| --- | --- |
| Active interface case vertical design load | about 618 N |
| Active interface case pitch/roll moment | about 31 Nm |
| Active low-load worst interface moment | about 108 Nm |
| Active guide-pin shear design load | about 154 N |
| Active total latch uplift design load | about 124 N |
| Active per-latch uplift with 4 latches | about 31 N |

The latch remains a preload/uplift and retention item. Horizontal shear and repeatable alignment should still be carried by locating pins, rest pads, and receiver geometry.

## Updated YAW-A Screen

The earlier YAW-A 12 deg / 14 deg gimbal candidate was sized to keep the +/-5 deg stretch case healthy.

For the user-confirmed +/-3 deg PoC baseline, a simpler YAW-A candidate is now:

| Item | Candidate |
| --- | --- |
| YAW-A gimbal design angle | 8 deg |
| YAW-A gimbal hard stop angle | 10 deg |
| Total yaw clearance | <=0.2 mm preferred, <=0.3 mm max |
| Anti-yaw contact face | >=10 mm width, >=80 mm overlap |
| Yoke yaw couple arm | >=50 mm |
| Yoke pin | >=10 mm |
| Yoke lug thickness | >=8 mm |

Baseline YAW-A yaw load:

| Result | Value |
| --- | --- |
| Baseline design yaw torque | about 16 Nm |
| Heavy-cart 30 kg sensitivity design yaw torque | about 24 Nm |
| Anti-yaw contact couple force | about 328 N |
| Contact pressure at 10 mm x 80 mm | about 0.41 MPa |
| 10 mm pin double-shear stress | about 2.1 MPa |
| 8 mm lug bearing stress | about 4.1 MPa |

## Fabrication Implications

The simplified direction favors:

- Keeping the three-actuator tripod concept.
- Keeping the already modeled 12 V Firgelli actuator candidate unless packaging or tests fail.
- Using HRT8E-style M8 rod ends as the leading actuator joint candidate for +/-3 deg.
- Keeping high-angle link-ball joints as reserve, not the default.
- Avoiding oversized industrial actuators, large Cardan joints, and complex multi-guide yaw paths unless the simple YAW-A mock-up fails.
- Designing brackets so actuator load lines pass through the joint centers.
- Keeping the cart coupling mechanical: locating/rest pads for shear and latch/secondary lock for preload/uplift.
- Treating the cart receiver as a designable part, so its frame spacing and latch points can be chosen around the leveling-device envelope instead of being reverse engineered from images.
- Using aluminum profile as the cart-side receiver backbone, while keeping locating pins, rest pads, latch keepers, and stop faces on local metal inserts or plates rather than on raw profile slots.

## Information Still Needed

The project can proceed with assumptions, but these inputs would remove most remaining uncertainty:

1. Target cart lower-frame outside length and width that the new cart should be designed to provide.
2. Exact aluminum profile family/section, connector style, and whether 30 mm or 40 mm class members best fit the 10 kg cart mass goal.
3. Intended locating-pin, rest-pad, insert-plate, and latch receiver zones on the new profile frame.
4. Whether 12 V power is acceptable for the PoC, or whether an existing 24 V supply must be used.
5. Approximate carried-material shape and whether the 10 kg load may be strongly off-center.

Until those are known, do not infer dimensions or mass from images.

```text
PHASE 0 DIRECTION REVIEWED
USER-CONFIRMED LOW-LOAD +/-3 DEG BASELINE
NOT READY FOR APPROVE PARAMETERS
NOT APPROVED FOR FABRICATION
```
