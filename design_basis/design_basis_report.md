# Phase 0 Web-Based Design Basis Report

Status: concept approved for Phase 2 detailed CAD on 2026-08-26. Preliminary; not approved for fabrication.

## 1. Current conclusion

The Phase 0 source structure and traceability are useful, but the previous wording was too close to a parameter approval package. The correct current state is:

```text
PHASE 0 DIRECTION REVIEWED
PARAMETER TABLE REVISED AFTER FEEDBACK
USER-CONFIRMED LOW-LOAD +/-3 DEG BASELINE
ALUMINUM PROFILE CART RECEIVER DIRECTION RECORDED
CR-01-H3 CONNECTOR STACK RULES SCREENED
CR-01-H4 HARDWARE SEED SCREENED
JNT-BR-01 HRT8E BRACKET SEED SCREENED
APPROVE CONCEPT RECEIVED 2026-08-26
PHASE 2 DETAILED CAD BASELINE GENERATED
BENCH EVIDENCE PENDING BEFORE DESIGN FREEZE
NOT APPROVED FOR FABRICATION
```

The concept direction can remain:

- Three-actuator upper platform concept.
- User-confirmed carried material payload target: 10 kg.
- User-confirmed expected empty cart mass: about 10 kg, with the cart designable around the module.
- User-confirmed disconnected leveling-device height envelope: 250 to 300 mm.
- User-confirmed Pitch/Roll target: +/-3 deg.
- User-preferred cart receiver fabrication direction: CR-01 two-rail aluminum profile receiver kit with CR-01-H1 local metal hard points, CR-01-H2-B connector / positive-stop topology, CR-01-H3 hardpoint-specific stack rules, and CR-01-H4-S1 mock-up hardware seed.
- +/-5 deg as future stretch only, not a current requirement.
- +/-8 deg as sensitivity only, not a baseline target.
- Mechanical locating and latching for cart coupling.
- Independent electrical limits and mechanical stops.

But component names and geometry values are still candidates or assumptions, not frozen selections.

## 2. Feedback findings accepted

The external feedback identified five material issues, all accepted:

1. The central guide mechanism is not solved. It is now marked `critical_open`.
2. Lift and pitch/roll use the same actuator stroke budget. A coupled workspace screen was added.
3. The 12 V Firgelli actuator candidate conflicts with a blanket 24 V bus target. Power architecture is now unresolved.
4. The 10 kg payload must mean additional material payload, not total lifted mass.
5. Component candidates were marked as selected too early. The parameter table now uses `CANDIDATE`, `UNRESOLVED`, `ASSUMED`, and `SELECTED_CONCEPT` more carefully.

## 3. Governing constraints

- Scope is limited to the leveling/lifting upper module, universal lower mounting interface, and mechanical cart coupling.
- Active upper-platform DOF are Z, pitch, and roll only.
- X, Y, and yaw must be mechanically constrained.
- Cart engagement must use mechanical locating and latching. Electromagnets cannot be the primary lock.
- Electrical limit switches and mechanical stops must be independent.
- Cart dimensions, materials, mass, and hole locations may not be inferred from images.
- The module is not for carrying people, and no certification claim is made.

## 4. Revised calculation basis

### 4.1 Lifted mass

The material payload is not the lifted mass. Actuator loads must use:

```text
total_lifted_mass =
moving_structure_mass
+ empty_cart_mass
+ material_payload_mass
```

Current user-confirmed PoC analysis sweeps:

- Material payload: 5 and 10 kg primary; 20 kg archived sensitivity only.
- Empty cart mass: 10 kg primary; 20 and 30 kg archive/check sensitivity.
- Moving structure mass: 15 and 22 kg.
- Design factor: 1.5 baseline; 2.0 sensitivity.
- Payload/CG offset: 0 and 50 mm baseline; 100 mm sensitivity.

`calculations/user_confirmed_baseline.py` now records the 2026-08-25 user clarification.

### 4.2 Actuator force

The load distribution screen remains:

```text
W_design = total_lifted_mass * g * design_factor

[ 1   1   1  ] [R1]   [W_design]
[x1  x2  x3 ] [R2] = [W_design * x_cg]
[y1  y2  y3 ] [R3]   [W_design * y_cg]

F_actuator_i = R_i / cos(theta_i)
```

This is a screening equation only. It does not replace pin, bracket, bolt, buckling, fatigue, shock, side-load, backlash, or finite-element checks.

### 4.3 Coupled workspace

The previous simple length sweep has been supplemented by `calculations/combined_workspace.py`.

With the current CAD geometry:

- At 5 mm actuator end margin, the minimum supported symmetric pitch/roll angle across 0-100 mm lift is about 5.75 deg.
- At 15 mm actuator end margin, the minimum supported symmetric pitch/roll angle across 0-100 mm lift drops to about 3.5 deg.
- At minimum lift and +/-3 deg, the 15 mm-margin screen leaves only about 2.5 mm effective margin.
- At minimum lift and +/-5 deg, the 15 mm-margin screen fails.
- +/-8 deg remains sensitivity only.

The current 250 mm comparison geometry therefore could not claim `100 mm lift + +/-3 deg pitch/roll at all heights` without more end-stroke, mechanical-stop, control-overshoot, tolerance, guide-mobility, and joint-angle evidence.

### 4.4 Selected pre-CAD operating-window candidate

`calculations/workspace_operating_window_screen.py` compares the old 250 mm layout to the approved higher collapsed pose. `WS-01-H20` is the selected Phase 2 CAD baseline:

- 270 mm disconnected/collapsed device height, within the user-confirmed 250 to 300 mm envelope.
- 0 to 100 mm lift and every nine `-3/0/+3 deg` pitch/roll combination.
- 195 mm outer and 220 mm inner keyed-guide candidate, producing 88 mm minimum overlap against the 80 mm target.
- 334 to 508 mm actuator soft operating window, with 11.13 mm minimum remaining reserve at the lower combined corner.

`calculations/travel_limit_hierarchy_screen.py` separates the planned command window from electrical and mechanical protection: command 334/508 mm, electrical targets 329/513 mm, and guarded mechanical-stop boundaries 324/518 mm. These are actuator-length planning values. CAD must create external physical shoulders/collars and real switches, then prove their contact order and measured overrun. They are not fabrication dimensions.

## 5. Revised parameter envelope

| Area | Revised status |
|---|---|
| Three-actuator architecture | Concept direction retained |
| Firgelli F-SD-H-450-12V-8in Hall | Leading low-load PoC candidate |
| DESTACO 323-R latch | Candidate only |
| HFS8-4040 frame | Candidate profile, exact procurement code open |
| Aluminum profile cart receiver | CR-01 two-rail HFS8 receiver kit candidate; CR-01-H1 hardpoint seed, CR-01-H2-B connector topology, CR-01-H3 connector stack rules, and CR-01-H4-S1 hardware seed added |
| BNO085 | Candidate PoC IMU |
| WT901C | Candidate packaged tilt sensor; exact variant to confirm |
| 10 kg payload | User-confirmed carried material payload target |
| 10 kg empty cart | User-confirmed primary cart basis; 20/30 kg retained only as sensitivity |
| 22 kg moving structure | Current upper PoC moving-structure sweep value |
| Disconnected device height 250-300 mm | User-confirmed envelope before cart coupling |
| Neutral/collapsed height | WS-01-H20 270 mm Phase 2 CAD baseline, inside 250-300 mm user envelope |
| 100 mm lift | Selected grid passes with +/-3 deg; physical actuator/guide/stop evidence still required |
| +/-3 deg pitch/roll | User-confirmed baseline; YAW-A axis order and workspace screened, physical mock-up still required |
| Actuator end joint | HRT8E-style rod end for +/-3 baseline with JNT-BR-01 centered double-shear bracket seed; high-angle link ball reserve |
| 24 V bus | Not required unless actuator is reselected |
| 4000 N upgrade threshold | Removed; upgrade criterion is derived from force/package/speed/duty/control checks |

## 6. Critical open item: central guide

The current phrase `central keyed telescoping guide plus Cardan accommodation` is a concept, not a solved mechanism.

The next-step mobility screen in `calculations/mobility_analysis.py` refines this:

- A keyed vertical telescoping guide with a yaw-transmitting two-axis Cardan has constraint rank 3, leaving Z, pitch, and roll.
- A rigid keyed slide without Cardan has constraint rank 5, leaving only Z and therefore binding pitch/roll.
- The actuator-length Jacobian rank is 3 in the screened +/-3, +/-5, and +/-8 deg ranges, so the length mapping is not the dominant risk.
- The physical risk remains Cardan/yaw torque transmission, actuator joint misalignment, side-load, guide overlap, and stop/clearance allocation.

Before parameter approval, the project must define:

- Actuator upper and lower joint types.
- Central guide lower joint type.
- Central guide upper joint type.
- Cardan axis directions.
- Which component constrains yaw.
- Whether pitch/roll induce guide side-load.
- Joint maximum articulation over all poses.
- Whether the constraint set is overconstrained or underconstrained.
- A full-pose mobility check, ideally using a Jacobian/rank or equivalent constraint analysis.
- A physical mock-up or low-risk bench test before metal fabrication.

This is the largest mechanical risk. If it is not resolved, the real mechanism can bind even if all actuator force calculations pass.

Current numerical flags:

- Cardan combined tilt is 4.24 deg at +/-3 deg, 7.07 deg at +/-5 deg, and 11.30 deg at +/-8 deg.
- The current 8 deg design angle / 10 deg hard stop passes the user-confirmed +/-3 deg baseline and treats +/-5 deg as hard-stop sensitivity only.
- Lower actuator joint deviation reaches 10.94 deg at +/-3 deg and 13.85 deg at +/-5 deg.
- Current guide overlap minimum is 83 mm against an 80 mm preliminary target, which is too close for approval.

### 6.1 Joint candidate follow-up

`calculations/joint_candidate_screen.py` adds a preliminary candidate filter:

- Angular margin: 2 deg beyond calculated joint deviation.
- Static load screen: candidate static capacity >= 2 x calculated maximum actuator axial force.

Screen result:

- Single-axis clevis is rejected as the primary actuator end joint because the current motion is spatial.
- MISUMI PHSOSM8 is screened out for the primary actuator joint.
- MinebeaMitsumi HRT8E passes the current +/-3 deg baseline screen and is now the leading simple actuator joint candidate if packaging preserves articulation.
- MISUMI RBLD8-style high-angle link ball remains a reserve if the HRT8E-style package loses angular margin.
- Ruland-style universal joints are useful as a yaw-transmitting central Cardan component-family reference by angle only. Exact torque, backlash, axial/radial load, and mounting are still open.

### 6.2 Joint detail follow-up

`calculations/joint_detail_screen.py` adds first-order packaging checks for the joint load path.

Actuator joint result:

- Pin double-shear and lug bearing stresses are not the obvious bottleneck in the current screen.
- Threaded-stud cantilever bending is the bottleneck if the bracket force line is offset.
- At the archived +/-5 deg stretch screen under the current low-load mass basis, an M8 link-ball style joint with a 10 mm unsupported standoff gives about 407 MPa preliminary bending stress.
- An M12 upsize reduces that to about 119 MPa and passes the placeholder 150 MPa numeric screen, but remains a packaging reserve rather than a reason to use a threaded shank as a spacer.
- The actuator bracket must route force through the ball center or use a boxed/double-shear arrangement that avoids using the threaded shank as a cantilever spacer.
- JNT-BR-01 corrects the HRT8E actuator-axis screen to the 5.29 kN axial static value, not the 26.77 kN radial catalog value. The active +/-3 deg/DF 2.0/100 mm eccentricity screen is about 972 N; the existing 2x static comparison leaves about 2.72x axial margin.
- JNT-BR-01 now uses the official HRT8E 8/23/11 mm envelope, two 8 mm steel lugs, one 8 mm double-shear pin and an 18 mm loaded inner-lug support span. The regenerated placeholder comparison gives about 8.7 MPa pin shear, 78.5 MPa pin bending, 13.7 MPa lug bearing and 38.5 MPa lug-root bending. Physical V-01 articulation remains open.
- Required articulation is about 12.94 deg against HRT8E's 14 deg catalog value, so a physical full-14-deg no-contact check is a candidate-retention condition, not a completed proof.

Central yaw result:

- The old conservative yaw-torque screen using 90 kg total lifted mass, 0.5 g horizontal acceleration, DF 2.0, and 100/100 mm CG offset gave about 125 Nm yaw torque and about 250 Nm peak/design. It is no longer the primary design target after the 2026-08-25 user clarification.
- The user-confirmed low-load PoC screen gives about 16 Nm design yaw torque with the 10 kg cart basis. The earlier 24 Nm value is retained only as a 30 kg cart sensitivity.
- Under the new PoC screen, force margin is no longer the obvious blocker. The unresolved part is the gimbal/Cardan/key/fastener/backlash connection path.

### 6.3 Central yaw path comparison

`calculations/central_yaw_path_comparison.py` compares four yaw-torque path concepts.

Current ranking for a fabrication-first low-load PoC:

1. YAW-A: keyed square telescoping guide carries yaw torque, while the two-axis gimbal permits pitch/roll without interrupting the yaw path.
2. YAW-D: dual parallel anti-yaw guides with explicit top compliance/gimbal, reserve only if YAW-A backlash is unacceptable.
3. YAW-C: single 16 mm commercial ball spline, reserve only because it adds procurement/package complexity.
4. YAW-B: oversized direct-torque U-joint, archived as too large/complex for the low-load PoC unless all simpler paths fail.

Key values:

- User-confirmed PoC design yaw torque: about 16 Nm.
- YAW-A contact screen: about 328 N couple force and 0.41 MPa contact pressure with 80 mm overlap and 10 mm contact width.
- Heavy-cart 30 kg sensitivity: about 24 Nm design yaw torque, 484 N couple force, and 0.60 MPa contact pressure.
- Ruland US32 reference is now oversized for the simplified PoC.
- MISUMI No.16 ball spline torque is no longer the main blocker under the low-load screen, but it still adds pitch/roll isolation and procurement complexity.

Current Phase 0 direction is therefore to carry forward YAW-A, not a small U-joint or single 16 mm ball spline, while keeping the central guide `critical_open` until backlash, wear, side-load, key/contact geometry, and a mock-up are complete.

### 6.4 YAW-A candidate parameter definition

`calculations/yaw_a_architecture_screen.py` defines the preferred YAW-A architecture in candidate-parameter form.

Mobility result:

- YAW-A constrains tx, ty, and rz.
- YAW-A leaves tz, rx, and ry.
- A rigid keyed slide without a gimbal binds pitch/roll.
- A loose spherical joint without a yaw lock leaves yaw unconstrained.

Candidate parameters:

| Parameter | Candidate |
|---|---:|
| Gimbal design angle | 8 deg |
| Gimbal hard stop | 10 deg |
| Preferred total yaw clearance | <= 0.2 mm |
| Maximum total yaw clearance | <= 0.3 mm |
| Preferred yaw freeplay | <= 0.25 deg |
| Maximum yaw freeplay | <= 0.5 deg |
| Anti-yaw contact width | >= 10 mm |
| Minimum engaged overlap | >= 80 mm |
| Preferred engaged overlap | >= 100 mm |
| Yaw couple arm through gimbal/yoke | >= 50 mm |
| Gimbal/yoke pin diameter | >= 10 mm |
| Gimbal/yoke lug thickness | >= 8 mm |

These values are candidates for the low-load +/-3 deg review package, not approved fabrication parameters.

## 7. Cart profile receiver screen

`calculations/cart_profile_receiver_screen.py` adds a first pass for the user-preferred aluminum-profile cart receiver.

Current candidate:

| Item | CR-01 candidate |
|---|---:|
| Receiver type | two longitudinal aluminum-profile rails |
| Profile basis | HFS8-4040 or equivalent sourced 40 mm profile |
| Receiver zone | 760 mm x 560 mm |
| Rest pad span | 620 mm x 520 mm |
| Locator topology | one master locator plus one slotted/diamond secondary locator |
| Locator X span | 520 mm |
| Latch count | 2 minimum; 4 placeholder |
| Screened receiver kit mass | about 4.50 kg |

The HFS8 rectangular subframe reserve screens at about 6.43 kg. It remains possible, but it consumes too much of the 10 kg empty-cart mass basis unless the future cart frame needs a self-contained receiver.

Current CR-01 load screen:

- Active worst rest-pad maximum load: about 331 N.
- Active worst rest-pad minimum load: about 81 N, so all four pads remain compressive in the simplified active screen.
- Master locator single-point shear if it carries all horizontal shear: about 154 N.
- Yaw couple force at 520 mm locator span: about 32 N.
- Per-latch uplift with four latches: about 31 N.

This keeps bulk loads low. The remaining risks are connector stiffness, slot slip, local wear, insert plate details, and latch/locator geometry.

## 8. Cart receiver hardpoint screen

`calculations/cart_receiver_hardpoint_screen.py` adds a first-order CR-01-H1 hardpoint screen.

Current candidate:

| Item | CR-01-H1 seed |
|---|---|
| Locator insert | 12 mm locator interface in 8 mm local steel insert or hardened bushing |
| Rest pad insert | 40 x 30 mm contact on 8 mm local pad with shim stack |
| Latch keeper | 5 mm local steel keeper |
| Profile fastening | two M8-class T-slot fasteners per critical hard point as starting topology |
| Anti-slip | dowel/key/positive stop after alignment |

Screened results:

- Locator combined load: about 186 N.
- Locator insert bearing stress: about 1.94 MPa.
- Rest pad contact pressure: about 0.28 MPa.
- Latch keeper bearing: about 0.25 MPa with four latches, about 0.49 MPa with two latches.
- Insert-to-profile slip margin: about 6.45x under placeholder clamp/friction assumptions.
- Local 6 mm tab bending stress: about 16 MPa.

These values say bulk strength is not the likely blocker. The actual blockers are connector stiffness, slot slip, repeated seating wear, alignment repeatability, latch clearance, and latch-closed sensor integration.

## 9. Cart receiver connector topology screen

`calculations/cart_receiver_connector_topology_screen.py` adds the CR-01-H2 connector / positive-stop topology screen.

Current candidate:

| Item | CR-01-H2-B seed |
|---|---|
| Clamp / adjustment | two M8-class T-slot fasteners per critical hard point |
| Final shear/yaw path | shoulder/key/positive stop after mock-up alignment |
| Optional repeatability | 6 mm or larger dowel after alignment if needed |
| Reserve | backing clamp plate if profile wall stiffness or service tests demand it |
| Rejected | slot friction only as final locating |

Screened results:

- Connector design demand: about 186 N.
- Friction-only placeholder slip margin: about 6.45x, but rejected as a final locating method.
- Positive stop bearing stress with 40 x 8 mm contact: about 0.58 MPa.
- Positive stop local tab bending with 6 mm tab and 25 mm cantilever: about 19 MPa.
- Optional 6 mm dowel shear: about 6.6 MPa.
- Optional 6 mm dowel bearing in 8 mm plate: about 3.9 MPa.

These values keep bulk strength low in the active PoC case. The remaining decisions are exact slot nut family, profile wall bearing, backing plate need, replaceable stop geometry, dowel placement, sensor access, and service adjustment.

## 10. Cart receiver connector detail / access screen

`calculations/cart_receiver_connector_detail_screen.py` maps the preferred CR-01-H2-B topology onto each hard point.

Current stack rules:

| Hard point | Constrain | Release | Rule |
|---|---|---|---|
| Master locator | X, Y | - | Fixed locator; H2-B positive stop and optional dowel after alignment |
| Slotted secondary locator | Y | X | Yaw reference without X overconstraint; do not use a round dowel in both axes |
| Rest pad | Z | X, Y | Shim-adjustable seating only; not a hidden horizontal stop |
| Latch keeper | uplift/preload | primary horizontal shear | Retention and sensing only; latch hook must not pull the cart sideways as the shear path |

Screened results:

- Profile wall / stop backing bearing with 3x local factor: about 1.74 MPa.
- Slot nut local clamp screen with 4000 N clamp over a placeholder 18 x 12 mm contact: about 18.5 MPa.
- Mock-up cycling rule: run at least 30 coupling cycles before freezing the connector stack.
- Add backing plate or stiffer local stack if hard-point shift exceeds 0.2 mm, fastener torque relaxation exceeds 20%, profile wall marking appears, or latch preload drifts.
- Reserve 25 mm tool access and a 25 x 25 x 35 mm sensor envelope for latch-closed/cart-present sensing.

These values still do not approve exact slot nut, torque, stop block, dowel, backing plate, sensor bracket, or service access geometry.

## 10A. Cart receiver hardware selection screen

`calculations/cart_receiver_hardware_selection_screen.py` adds CR-01-H4-S1: a removable 12 mm master bushing and replaceable stop, X-releasing secondary locator, 40 x 30 mm shim pad, and 5 mm keeper with a separate mechanical secondary lock. It retains H3 role separation and uses only placeholder local material comparisons; it does not freeze purchased items, fits, torque, or fabrication geometry.

At the existing 3x local screen load, the bushing bearing is about 5.8 MPa, the stop bearing is about 1.7 MPa, stop bending is about 32.7 MPa, optional 6 mm dowel shear is about 19.7 MPa, and rest-pad contact is about 0.8 MPa. The nominal 60 x 40 x 6 mm steel backing bridge remains an evidence-triggered reserve after the 30-cycle mock-up.

## 11. Power and control architecture

The Firgelli baseline candidate is a 12 V actuator. A 24 V power bus is not approved unless:

- The actuator is changed to a 24 V version or 24 V actuator family, or
- A suitably rated DC-DC architecture is explicitly selected.

For the current 12 V candidate:

- Three actuators at 5.5 A each require 16.5 A motor current before controller current and derating.
- The current screen recommends roughly 12 V 23 A / 273 W before final derating.
- Three independent actuator drive channels are required.
- MD13S and MD20A are single-channel candidates; MDD20A is two-channel.

Hall feedback should be treated as incremental. The control architecture needs:

- Power-on homing to a reference switch.
- Lost-pulse detection.
- Maximum mismatch threshold.
- Homing speed and timeout.
- Latch-closed and cart-present interlocks.
- Motor power isolation through relay/contactor, not only MCU software stop.
- Per-channel fusing or equivalent protection.

## 12. Open risks before design freeze or fabrication release

- Central guide mobility and side-load path unresolved.
- End-stroke margin, mechanical stops, and control overshoot not yet allocated.
- Neutral height not optimized from workspace.
- Moving/fixed mass split not complete.
- HRT8E/JNT-BR-01 remains conditional until the actual manufacturer drawing, 14 deg no-contact mock-up, pin retention, attachment, edge distances, fatigue, and shock behavior are confirmed.
- CR-01, CR-01-H1, CR-01-H2-B, CR-01-H3, and CR-01-H4-S1 aluminum-profile cart receiver geometry/hardpoints/connectors are only Phase 1 candidates; exact slot nuts, backing plates, insert plates, profile section, bushing fit, positive-stop screw/dowel geometry, latch sensors, service access, and receiver-zone details are not approved.
- Cart mass should be rechecked after the new frame concept, but 10 kg is now the primary basis.
- Payload CG height, lean angle, and interface moments are only swept assumptions.
- Latch count, preload, secondary lock, and latch sensor not finalized.
- Exact driver/power architecture unresolved.
- Budget is still not tied to supplier quotes.

## 13. Required next step

Detailed CAD may proceed. Do not release tolerance-complete fabrication drawings or manufacturing approval yet.

The next engineering step is:

1. Confirm JNT-BR-01 against the actual HRT8E drawing and a 14 deg no-contact gauge/mock-up.
2. Resolve the central guide/joint mobility.
3. Finalize coupled workspace criteria and end-stroke margin.
4. Split fixed/moving masses and update load sweeps.
5. Plan the CR-01-H4-S1 30-cycle mock-up and select exact purchased hardware only after fit, torque retention, wear, latch, and sensor evidence are available.
6. Decide 12 V vs 24 V actuator/power architecture.
7. Define homing, synchronization, E-stop power isolation, fusing, and latch interlocks.
8. Update the Phase 2 package with measured evidence, then request a separate design-freeze/fabrication decision.
