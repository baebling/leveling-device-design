# Phase 0 Recheck Summary

Status: revised after feedback. Preliminary only. Not ready for `APPROVE PARAMETERS`.

## What changed in this recheck

- The parameter table no longer treats major hardware as frozen selections.
- Firgelli actuator, DESTACO latch, HFS8 frame, BNO085, WT901C, motor drivers, and power supplies are now candidates or unresolved items.
- The central guide is marked `critical_open`.
- Actuator-end and central Cardan joint candidates were screened; joint implementation remains open.
- Joint package and yaw-torque detail screening were added; actuator stud cantilever bending and central yaw torque path are now explicit blockers.
- Central yaw path concepts were compared; YAW-A keyed square guide yaw-torque bypass is now the preferred concept direction.
- YAW-A candidate parameters were defined for gimbal angle, yaw clearance, anti-yaw contact and yoke pins.
- Final candidate parameter pack v1.0 was drafted after the user confirmed 10 kg carried payload, about 10 kg empty cart mass, 250 to 300 mm disconnected device height, +/-3 deg pitch/roll only, and aluminum profile as the cart receiver direction. v1.0 retains CR-01-H4 and adds the JNT-BR-01 HRT8E bracket seed with the corrected axial-capacity basis.
- The 24 V power bus target is no longer approved while the baseline actuator candidate is 12 V.
- The arbitrary 4000 N actuator-upgrade threshold was removed.
- 10 kg is now user-confirmed as the carried material payload target, not total lifted mass.
- Moving structure mass now uses a simpler 15/22 kg PoC sweep for the current baseline.
- A coupled Z-pitch-roll workspace script was added.
- A central guide mobility screen was added; the concept is conditionally feasible only with a yaw-transmitting two-axis Cardan.

## Key files

- `PROJECT_HANDOFF.md`: project-level handoff and gate status.
- `logs/work_history.md`: work history and trial/error record.
- `logs/feedback_recheck_2026-08-24.md`: feedback recheck record.
- `design_basis/design_basis_report.md`: revised design basis report.
- `design_basis/parameter_decision_table.csv`: revised parameter table.
- `design_basis/component_candidate_table.csv`: revised component candidate table.
- `outputs/reports/final_candidate_parameter_pack.md`: consolidated final candidate parameter pack for user judgment.
- `design_basis/cart_profile_receiver_concept_2026-08-25.md`: aluminum-profile cart receiver concept note.
- `design_basis/cart_profile_receiver_layout_screen.md`: CR-01 receiver layout, mass, rest-pad, locator, and latch screen.
- `design_basis/cart_receiver_hardpoint_screen.md`: CR-01-H1 locator insert, rest pad, latch keeper, fastening, and local tab screen.
- `design_basis/cart_receiver_connector_topology_screen.md`: CR-01-H2 slot fastener, backing plate reserve, positive stop and optional dowel screen.
- `design_basis/cart_receiver_connector_detail_screen.md`: CR-01-H3 hardpoint-specific connector stack and service access screen.
- `design_basis/cart_receiver_hardware_selection_screen.md`: CR-01-H4 mock-up hardware selection screen.
- `design_basis/actuator_bracket_package_screen.md`: JNT-BR-01 HRT8E-style centered double-shear bracket screen.
- `outputs/reports/cart_profile_receiver_summary.md`: short CR-01 receiver summary.
- `outputs/reports/cart_receiver_hardpoint_summary.md`: short CR-01-H1 hardpoint summary.
- `outputs/reports/cart_receiver_connector_summary.md`: short CR-01-H2 connector/positive-stop summary.
- `outputs/reports/cart_receiver_connector_detail_summary.md`: short CR-01-H3 connector-stack/access summary.
- `outputs/reports/cart_receiver_hardware_selection_summary.md`: short CR-01-H4 hardware seed summary.
- `outputs/reports/actuator_bracket_package_summary.md`: short JNT-BR-01 bracket-package summary.
- `design_basis/guide_mobility_review.md`: central guide and joint mobility review.
- `design_basis/joint_candidate_screen.md`: actuator-end and central Cardan joint candidate screen.
- `design_basis/joint_detail_screen.md`: actuator joint packaging and central yaw-torque screen.
- `design_basis/central_yaw_path_comparison.md`: central yaw-torque path concept comparison.
- `design_basis/yaw_a_architecture_definition.md`: YAW-A candidate parameter definition.
- `calculations/combined_workspace.py`: coupled workspace screen.
- `calculations/mobility_analysis.py`: central guide, Cardan, actuator joint and Jacobian screen.
- `calculations/joint_candidate_screen.py`: joint candidate angle/load screen.
- `calculations/joint_detail_screen.py`: first-order pin, lug, stud bending and yaw torque screen.
- `calculations/central_yaw_path_comparison.py`: central yaw path concept comparison.
- `calculations/yaw_a_architecture_screen.py`: YAW-A mobility, backlash, contact and yoke pin screen.
- `calculations/user_confirmed_baseline.py`: user-confirmed 10 kg/+/-3 deg low-load PoC screen.
- `calculations/cart_receiver_connector_detail_screen.py`: CR-01-H3 hardpoint-specific connector stack and access screen.
- `calculations/cart_receiver_hardware_selection_screen.py`: CR-01-H4 local hardware and conditional-backing screen.
- `calculations/actuator_bracket_package_screen.py`: JNT-BR-01 HRT8E axial-capacity, articulation, and pin/lug screen.
- `calculations/load_distribution.py`: material/cart/moving-structure force sweep.
- `calculations/interface_moments.py`: interface load/moment screen including CG height.
- `calculations/power_budget.py`: 12 V vs 24 V power architecture screen.

## Revised conclusions

| Topic | Revised conclusion |
|---|---|
| Three-actuator concept | Retain as concept direction |
| 10 kg payload | User-confirmed carried material payload target |
| 10 kg empty cart | User-confirmed primary cart basis; 20/30 kg retained only as sensitivity |
| Cart receiver fabrication | CR-01 two-rail aluminum profile receiver kit, CR-01-H1 hardpoint seed, CR-01-H2-B connector topology, CR-01-H3 connector-stack rules, and CR-01-H4-S1 mock-up hardware seed carried forward; exact slot nut/backing plate/fit/fastener/latch/sensor details open |
| 20 kg payload | Archived sensitivity, not a current design target |
| 100 mm lift | Target, not full-workspace guarantee |
| +/-3 deg pitch/roll | User-confirmed baseline, but needs workspace and guide proof |
| +/-5 deg | Future stretch only, not required |
| +/-8 deg | Archived sensitivity only |
| Firgelli F-SD-H-450 12 V | Leading low-load PoC candidate |
| PHSOSM8 actuator joint | Screened out for primary actuator joint |
| HRT8E actuator joint | Leading +/-3 actuator joint candidate |
| High-angle link-ball joint | Reserve if HRT8E packaging loses angular margin |
| JNT-BR-01 bracket seed | Official HRT8E 8/23/11 mm envelope; centered 8 mm double-shear pin/lug; 18 mm detailed span; 14 deg physical no-contact check required |
| Actuator joint bracket load path | Critical open: avoid threaded-stud cantilever bending |
| Small central U-joint | Screened out as sole yaw-torque path |
| Central yaw path | YAW-A keyed square guide torque-bypass concept preferred |
| YAW-A gimbal angle | 8 deg design, 10 deg hard stop candidate |
| YAW-A yaw clearance | <=0.2 mm preferred, <=0.3 mm max candidate |
| YAW-A contact/yoke | >=10 mm contact width, >=80 mm overlap, >=10 mm yoke pins |
| Single 16 mm ball spline | Low-load reserve only; not preferred over simple YAW-A |
| Oversized US32 U-joint | Archived oversized reserve |
| DESTACO 323-R | Candidate latch only |
| HFS8-4040 | Candidate profile only |
| Central guide | Critical open mechanical risk |
| Power bus | 12 V PoC baseline if Firgelli is kept; 24 V only after actuator reselection |
| Motor drivers | Three independent channels required |
| E-stop | Must remove motor power through relay/contactor path, not MCU input only |

## Coupled workspace screen

The previous table checked actuator stroke too optimistically. `calculations/combined_workspace.py` now checks lift and pitch/roll together.

Current CAD geometry result:

- With 5 mm actuator end margin, the whole 0-100 mm lift range supports at least about +/-5.75 deg symmetric pitch/roll.
- With 15 mm actuator end margin, the whole 0-100 mm lift range supports only about +/-3.5 deg symmetric pitch/roll.
- At minimum lift and +/-3 deg with 15 mm margin, effective end margin is only about 2.5 mm.
- At minimum lift and +/-5 deg with 15 mm margin, the screen fails.

Therefore do not claim `100 mm lift + +/-3 deg full-angle leveling at all heights` until mechanical stops, control overshoot, tolerance, guide mobility, and joint articulation are allocated.

## Central guide mobility screen

`calculations/mobility_analysis.py` now checks the guide concept, Cardan tilt, actuator joint deviation, guide overlap, and actuator-length Jacobian rank.

Key result:

- With a yaw-transmitting two-axis Cardan, the central guide constraint rank is 3 and leaves Z, pitch, and roll.
- A rigid keyed slide without Cardan has constraint rank 5 and leaves only Z, so pitch/roll would bind.
- Actuator-length Jacobian rank is 3 in +/-3, +/-5, and +/-8 deg screens.
- Cardan tilt is 4.24 deg at +/-3 deg, 7.07 deg at +/-5 deg, and 11.30 deg at +/-8 deg.
- The current 8 deg design angle / 10 deg hard stop passes +/-3; +/-5 is hard-stop sensitivity only and is no longer required.
- Max lower actuator joint deviation is 10.94 deg at +/-3 and 13.85 deg at +/-5, so single-axis clevis joints are not acceptable without additional proof.
- Minimum guide overlap is 83 mm against an 80 mm preliminary requirement, which is too close for approval.

## Joint candidate screen

`calculations/joint_candidate_screen.py` applies a preliminary 2 deg angular margin and 2x static load capacity screen to actuator-end joint candidates.

Key result:

- Required actuator joint angular allowance is about 13 deg for the user-confirmed +/-3 deg baseline.
- PHSOSM8 fails the current primary actuator joint screen because both angle and static load margin are too tight.
- HRT8E passes the current +/-3 deg baseline screen and becomes the leading simple joint candidate if packaging preserves articulation.
- A high-angle RBLD8-style link ball remains a reserve if HRT8E-style packaging loses angular margin.
- JNT-BR-01 corrects the HRT8E actuator-axis capacity basis to 5.29 kN axial static, rather than 26.77 kN radial static. At active +/-3 deg/DF 2.0/100 mm eccentricity, the approximately 972 N maximum actuator force produces about 2.72x axial margin against the existing 2x static screen.
- JNT-BR-01 uses the official HRT8E 8/23/11 mm envelope, a centered 8 mm double-shear pin/lug and an 18 mm detailed support span. The regenerated screen gives about 8.7 MPa pin shear, 78.5 MPa pin bending, 13.7 MPa lug bearing and 38.5 MPa lug-root bending. Required articulation is about 12.94 deg versus 14 deg catalog, so actual 14 deg no-contact proof is mandatory.
- The central guide still needs a yaw-transmitting Cardan/u-joint or equivalent gimbal; Ruland-style U-joints are a component-family reference by angle only.

## Joint detail screen

`calculations/joint_detail_screen.py` checks first-order packaging details after the joint candidate filter.

Key result:

- Pin double shear and lug bearing are not the primary bottleneck in the current actuator joint screen.
- Threaded-stud cantilever bending is the bottleneck if the joint is mounted with an offset load line.
- At the archived +/-5 deg stretch screen under the current low-load mass basis, an M8 high-angle link-ball style joint with 10 mm unsupported standoff gives about 407 MPa preliminary bending stress.
- An M12 upsize reduces the same screen to about 119 MPa and passes the placeholder numeric screen, but it remains a reserve rather than a reason to use a threaded shank as a spacer.
- Therefore actuator force must pass through the ball center or a boxed/double-shear bracket must be used.
- The old conservative central yaw torque screen was about 125 Nm operating and about 250 Nm peak/design; this is no longer the primary user-confirmed PoC target.
- The user-confirmed YAW-A PoC design yaw torque is about 16 Nm with the 10 kg cart basis; the earlier 24 Nm value remains only as a 30 kg cart sensitivity.
- The 50 x 3 mm square guide tube looks plausible as a torsion member by first-order math; the unresolved issue is the Cardan/gimbal/key/fastener/backlash connection path.

## Central yaw path comparison

`calculations/central_yaw_path_comparison.py` compares four ways to carry yaw torque.

Key result:

- `YAW-A`, a keyed square telescoping guide carrying yaw torque with a two-axis gimbal for pitch/roll, is the preferred Phase 0 direction.
- Under the user-confirmed primary PoC yaw screen, YAW-A contact force is about 328 N and contact pressure is about 0.41 MPa with 80 mm overlap and 10 mm contact width.
- `YAW-B`, an oversized Ruland US32-class direct-torque U-joint, passes torque and angle but is large for the central stack.
- `YAW-C`, a single 16 mm ball spline, is no longer torque-blocked under the low-load screen but remains a reserve because it adds procurement/package complexity and still needs pitch/roll isolation.
- `YAW-D`, dual anti-yaw guides, passes load-only screening but has package and overconstraint risks.

## YAW-A candidate parameters

`calculations/yaw_a_architecture_screen.py` converts YAW-A into candidate values:

- Constraint rank is 3, leaving Z, pitch and roll.
- A rigid keyed slide without gimbal is rejected because pitch/roll bind.
- A loose spherical joint is rejected because yaw is unconstrained.
- Candidate gimbal angle is 8 deg design and 10 deg hard stop.
- Preferred total yaw clearance is <=0.2 mm, with <=0.3 mm as the current maximum candidate.
- Estimated yaw freeplay is about 0.23 deg at 0.2 mm clearance and about 0.34 deg at 0.3 mm clearance.
- Anti-yaw contact target is >=10 mm contact width and >=80 mm overlap, with >=100 mm preferred overlap.
- Candidate gimbal/yoke yaw couple is >=50 mm arm, >=10 mm pin diameter and >=8 mm lug thickness.

## Force and mass screen

The lifted mass is now treated as:

```text
moving_structure_mass + empty_cart_mass + material_payload_mass
```

The user-confirmed low-load PoC screen now uses 10 kg material payload, 10 kg primary cart mass, 20/30 kg cart mass as archive/check sensitivity, and 15/22 kg moving structure sweep:

- 10 kg material payload + 10 kg cart + 22 kg moving structure = 42 kg primary lifted mass.
- At +/-3 deg, DF 1.5, and 50 mm eccentricity, the primary screened actuator axial force is about 618 N.
- This gives about 3.24x margin against the 450 lbf / 2002 N Firgelli reference rating.
- DF 2.0 / 50 mm gives about 824 N and DF 1.5 / 100 mm gives about 729 N; both pass the Firgelli reference rating.
- The previous 30 kg cart sensitivity gives about 912 N and is retained only as an archive/check case.

## Cart profile receiver screen

`calculations/cart_profile_receiver_screen.py` checks the aluminum profile cart receiver direction.

Key result:

- The preferred `CR-01` layout uses two 760 mm HFS8-4040 longitudinal receiver rails in a 760 mm x 560 mm receiver zone.
- The screened receiver kit mass is about 4.50 kg including placeholder local hard points.
- A self-contained HFS8 rectangular receiver is about 6.43 kg and is therefore a heavier reserve.
- A GFS8 two-rail reserve is about 5.16 kg and should be used only if stiffness demands it.
- Four rest pads at 620 mm x 520 mm span remain compressive in the active worst interface screen, with about 331 N maximum pad load and about 81 N minimum pad load.
- Locator shear is about 154 N if the master locator carries all horizontal shear, and yaw couple force at 520 mm locator span is only about 32 N.
- Latches remain retention/preload items only; they are not the primary shear path.

## Cart receiver hardpoint screen

`calculations/cart_receiver_hardpoint_screen.py` checks the CR-01-H1 hardpoint seed.

Key result:

- Locator insert seed: 12 mm locator interface in an 8 mm local steel insert or hardened bushing.
- Combined locator screen load is about 186 N and locator insert bearing stress is about 1.94 MPa.
- Rest pad seed: 40 mm x 30 mm contact on an 8 mm local pad with shims; contact pressure is about 0.28 MPa.
- Latch keeper seed: 5 mm local steel keeper; bearing is about 0.25 MPa with four latches and about 0.49 MPa with two latches.
- Insert-to-profile fastening placeholder: two M8-class fasteners per critical hard point, assumed 4000 N clamp each and 0.15 friction, giving about 6.45x slip margin.
- This slip screen does not approve friction as the final locator. Add dowel, keyed plate, shoulder block, or positive stop after mock-up alignment.

## Cart receiver connector topology screen

`calculations/cart_receiver_connector_topology_screen.py` checks the CR-01-H2 connector and anti-slip topology.

Key result:

- The connector design demand inherited from CR-01-H1 is about 186 N.
- Slot-friction-only fastening has about 6.45x placeholder slip margin, but is rejected for final locating.
- The preferred `CR-01-H2-B` topology uses two M8-class T-slot fasteners per critical hard point for clamp/adjustment, then a shoulder/key/positive stop for final shear and yaw locating.
- A 40 x 8 mm positive-stop contact gives about 0.58 MPa bearing pressure.
- A 6 mm stop tab with 25 mm cantilever gives about 19 MPa bending stress.
- An optional 6 mm dowel gives about 6.6 MPa shear and about 3.9 MPa bearing in an 8 mm plate.
- Backing clamp plates and through-bolted cart members remain reserves, not the current preferred topology.

## Cart receiver connector detail / access screen

`calculations/cart_receiver_connector_detail_screen.py` maps CR-01-H2-B to each hard point.

Key result:

- Master locator stack fixes X and Y.
- Slotted secondary locator stack fixes Y only and releases X so the receiver does not become overconstrained.
- Rest pads are Z seating and shim-adjustment points, not hidden horizontal stops.
- Latch keepers carry preload/uplift only and must not pull the cart sideways as a primary shear path.
- Profile wall / stop backing bearing with a 3x local factor is about 1.74 MPa.
- Slot nut local clamp screen is about 18.5 MPa using a placeholder 18 x 12 mm contact area.
- Before freezing the connector stack, run at least 30 coupling cycles; add backing/stiffer stack if hard-point shift exceeds 0.2 mm or fastener torque relaxation exceeds 20%.
- Reserve at least 25 mm tool access and a 25 x 25 x 35 mm placeholder envelope for latch-closed/cart-present sensing.

## Cart receiver hardware-selection screen

`calculations/cart_receiver_hardware_selection_screen.py` narrows those rules into the CR-01-H4-S1 mock-up hardware seed: removable 12 mm master bushing plus replaceable stop, X-releasing secondary slot/diamond locator, 40 x 30 mm shim pad, and a 5 mm keeper with separate mechanical secondary lock.

At the existing 3x local screen load, it returns about 5.8 MPa bushing bearing, 1.7 MPa stop bearing, 32.7 MPa stop bending, 19.7 MPa optional 6 mm dowel shear, and 0.8 MPa rest-pad contact. The 60 x 40 x 6 mm steel backing bridge remains conditional on the existing 30-cycle mock-up trigger.

## Power/control screen

For the 12 V Firgelli candidate:

- 3 actuators x 5.5 A = 16.5 A motor current before controller current and derating.
- Current screen recommends about 12 V 23 A / 273 W before final derating.
- 24 V supply candidates should not be approved unless the actuator is changed to a 24 V version/family or a large DC-DC path is deliberately selected.
- Three independent actuator drive channels are required for pitch/roll, not one common synchronized up/down command.
- Homing and lost-pulse detection are required because Hall feedback is incremental.

## Approval gate

Do not create detailed CAD updates, fabrication drawings, manufacturing exports, or embedded control code yet.

Before parameter approval:

1. Confirm JNT-BR-01 against the actual HRT8E drawing and a 14 deg no-contact gauge/mock-up.
2. Resolve central guide mobility and joint definitions.
3. Finalize combined workspace and end-stroke margin.
4. Split fixed/moving masses and update load cases.
5. Plan the CR-01-H4-S1 30-cycle mock-up, then select exact purchased hardware only after fit, torque retention, wear, latch, and sensor evidence are available.
6. Resolve 12 V vs 24 V power architecture.
7. Define homing, mismatch detection, motor power isolation, fuses, and latch interlocks.
8. Re-issue the parameter approval package.

```text
PHASE 0 DIRECTION REVIEWED
PARAMETER TABLE REVISED AFTER FEEDBACK
USER-CONFIRMED LOW-LOAD +/-3 DEG BASELINE
CR-01-H2 CONNECTOR TOPOLOGY SCREENED
CR-01-H3 CONNECTOR STACK RULES SCREENED
CR-01-H4 HARDWARE SEED SCREENED
JNT-BR-01 HRT8E BRACKET SEED SCREENED
NOT READY FOR APPROVE PARAMETERS
```
