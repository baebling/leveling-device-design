# Final Candidate Parameter Pack v1.4

Status: Concept approved for Phase 2 detailed CAD on 2026-08-26. Preliminary only.

APPROVE CONCEPT RECEIVED
RADIAL_3_CLEAN ACTIVE CAD BASELINE
BENCH EVIDENCE PENDING BEFORE DESIGN FREEZE
NOT APPROVED FOR FABRICATION

This file consolidates the approved concept parameters and the remaining evidence gates. Detailed CAD is now permitted; the values remain preliminary and are not released for fabrication.

Update v1.3 records the user's rejection of the visually heavy central gimbal/cartridge package. The active design returns to three equal 120-degree radial actuators, uses a compact central keyed-guide/Cardan only for X/Y/yaw constraint, removes the upper service opening, and distributes separate mechanical/electrical limit envelopes symmetrically along the three actuator axes.

Update v1.4 applies the official HRT8E 8 mm bore, 23 mm body and 11 mm eye dimensions to all six actuator joints. The earlier 16 mm yoke gap was too tight for a conservative 14 deg projected envelope and is superseded by an 18 mm detailed seed with replaceable bushings, misalignment spacers and retained-pin envelopes.

## 1. Recommended Review Baseline

| Area | Approved concept baseline | Status | Key reason | Remaining evidence before design freeze |
| --- | --- | --- | --- | --- |
| Architecture | Three-actuator tripod leveling/lifting upper module | selected concept | Provides Z, pitch, and roll with three independent actuator lengths | Central guide/yaw path and joint implementation remain open |
| Active DOF | Z translation, pitch, roll | fixed | Matches project requirement | Do not change without explicit user approval |
| Constrained DOF | X translation, Y translation, yaw | fixed | Must be mechanically constrained | YAW-A must prove this without pitch/roll binding |
| Footprint target | 900 mm L x 800 mm W | provisional | Latest requirement basis | Decide cart receiver envelope to suit the device, not from images |
| Disconnected device height envelope | 250 to 300 mm | user clarified | User said cart can be made to suit this range | Recheck after central guide, yoke, actuator brackets, and stops |
| Collapsed height target | 270 mm WS-01-H20 CAD baseline, within 250 to 300 mm envelope | approved concept / preliminary CAD | Raises the tight lower actuator reserve while staying inside the user-confirmed height envelope | Verify purchased actuator, guide fit, yoke clearance, bracket, and stop hardware before design freeze |
| Lift target | 100 mm | provisional | Latest requirement basis | Combined stroke/end-margin approval still required |
| Baseline leveling | +/-3 deg pitch and +/-3 deg roll | user confirmed | User clarified this is enough | Needs guide/joint mock-up and end-stop margin decision |
| Stretch leveling | +/-5 deg pitch/roll | not required | No longer drives the PoC | Keep only as future stretch option |
| Stress/sensitivity leveling | +/-8 deg pitch/roll | not required | Fails or strains stroke/load screens and is unnecessary | Archive as sensitivity only |
| Material payload target | 10 kg additional carried payload | user confirmed | User clarified higher load is unnecessary | Must not be confused with total lifted mass |
| Analysis payload sweep | 5 and 10 kg primary; 20 kg archived sensitivity | selected analysis case | Keeps the model honest without driving design complexity | Replace after real carried-material mock-up |
| Empty cart mass | about 10 kg primary; 20/30 kg archive sensitivity | user clarified | User expects about 10 kg and can design the cart around the module | Recheck after cart frame concept is sketched |
| Cart receiver fabrication | CR-01 two-rail aluminum profile receiver kit with local metal hard points | candidate layout | Easy machining, assembly, adjustment, and later rework; screens at about 4.50 kg | Exact profile section, connectors, insert plates, and latch/locator zones remain open |
| Cart receiver hardpoints | CR-01-H1 local hardpoint set | candidate detail seed | 12 mm locator interface, 8 mm locator insert, 40 x 30 mm rest pad contact, 5 mm latch keeper, positive anti-slip feature | Exact connector, slot nut, bushing, shim, latch keeper, sensor and stop details remain open |
| Cart receiver connector topology | CR-01-H2-B: T-slot fastener clamp/adjustment plus shoulder/key/positive stop final locating | candidate topology seed | Keeps fabrication and mock-up adjustment simple while preventing a final friction-only locating path | Exact slot nut, profile wall bearing, backing plate, stop block, dowel and service access remain open |
| Cart receiver connector stack | CR-01-H3: master X/Y fixed; secondary Y-only; rest pad Z-only; latch preload/uplift-only | candidate detail seed | Preserves repeatability without overconstraining the receiver | Exact slot nut, backing plate, service access, sensor bracket and cycling test results remain open |
| Cart receiver hardware seed | CR-01-H4-S1: 12 mm removable master bushing/stop; secondary X-slot/diamond Y-only locator; 40 x 30 mm shim pad; 5 mm keeper + secondary lock | candidate hardware seed | Keeps first build simple, adjustable, and serviceable without assigning hidden horizontal load paths | Purchased hardware, fits, torque, stop screws, latch/sensor model and mock-up evidence remain open |
| Moving structure mass sweep | 15 and 22 kg | selected analysis case | Simple PoC should avoid a heavy moving structure | Replace after mass properties and BOM |
| Screening design factor | DF 1.5 baseline, DF 2.0 sensitivity | provisional | Matches low-load PoC direction | Not certification-level safety factor |

## 2. Motion and Stroke Candidate

| Parameter | Candidate value | Current interpretation |
| --- | --- | --- |
| Actuator count | 3 independent linear actuators | Keep concept direction |
| Selected workspace | WS-01-H20: 270 mm collapsed height, 0 to 100 mm lift, +/-3 deg pitch/roll | Pre-CAD parameter candidate; physical evidence still required |
| Selected guide package | 195 mm outer / 220 mm inner keyed guide candidate | Retains 88 mm minimum overlap against 80 mm target |
| Actuator soft operating window | 334 to 508 mm | 15 mm candidate keep-out from 319/523 mm catalogue endpoints |
| Minimum-lift +/-3 deg soft reserve | about 11.13 mm beyond the lower soft boundary | Occurs at 0 mm lift and a combined corner; adequate for parameter review but still needs actual endpoint data |
| 250 mm comparison geometry | about 2.54 mm lower soft reserve | Geometrically passes but is not recommended as the CAD baseline |
| Limit hierarchy | 334/508 mm command; 329/513 mm electrical targets; 324/518 mm mechanical-stop guarded boundaries | Strategy only; CAD and bench testing must set actual switch/stop contact geometry |

## 3. Load Cases Driving Selection

Use:

```text
total_lifted_mass = moving_structure_mass + empty_cart_mass + material_payload_mass
```

Current user-confirmed low-load PoC screen from `calculations/user_confirmed_baseline.py`:

| Case | Candidate numbers | Result |
| --- | --- | --- |
| Primary lifted mass screen | 22 kg moving structure + 10 kg cart + 10 kg material = 42 kg | Uses new user-confirmed cart basis |
| Actuator force, +/-3 deg, DF 1.5, 50 mm eccentricity | about 618 N | Passes Firgelli 450 lbf reference rating of about 2002 N |
| Force margin to Firgelli rating | about 3.24x | Preliminary force margin only |
| Actuator force sensitivity, +/-3 deg, DF 2.0, 50 mm eccentricity | about 824 N | Still passes Firgelli reference rating |
| Actuator force sensitivity, +/-3 deg, DF 1.5, 100 mm eccentricity | about 729 N | Still passes Firgelli reference rating |
| Heavy-cart sensitivity, 30 kg cart | about 912 N | Preserved only as an archive/check case |
| Baseline YAW-A design yaw torque | about 16 Nm | From 42 kg, 0.25 g horizontal acceleration, DF 1.5, 50/50 mm CG offset, 1.5x torque screen |
| Heavy-cart YAW-A design yaw torque | about 24 Nm | Preserved for 30 kg cart sensitivity |

Interpretation:

- The current Firgelli actuator can remain the leading low-load PoC candidate.
- The old 90 kg / +/-5 / high-eccentricity cases should not drive the fabrication-first design.
- Force margin is no longer the main blocker; packaging, stroke margin, joints, stops, and assembly simplicity are.

## 4. Actuator and Joint Candidate

| Area | Candidate value | Status | Approval blocker |
| --- | --- | --- | --- |
| Baseline actuator | Firgelli F-SD-H-450-12V-8in Hall | leading low-load PoC candidate | Passes the user-confirmed 10 kg payload / 10 kg cart / +/-3 deg force screen |
| Baseline actuator stroke | 203.2 mm | provisional | Stroke margin depends on chosen height/angle envelope |
| Baseline actuator length | 319 mm retracted, 523 mm extended | provisional | Verify purchased SKU drawing |
| Industrial actuator upgrade criterion | Upgrade only if the simple 10 kg/+/-3 package fails | open | Avoid industrial actuator complexity unless needed |
| Actuator joint angular allowance | >=13 deg for +/-3 baseline | open | Recalculate after final geometry |
| Actuator joint static load screen | >=2 x calculated maximum actuator axial force | open | Not a certification safety factor |
| HRT8E-style M8 rod end | Leading +/-3 actuator joint candidate | conditional | Use its 5.29 kN axial static limit; retain only if JNT-BR-01 preserves 14 deg physical articulation |
| JNT-BR-01-HRT8E bracket | Official 8/23/11 mm HRT8E envelope; centered boxed double-shear yoke; 8 mm lugs/pin; 18 mm span; replaceable bushings and retained-pin envelopes | implemented detailed seed | Removes threaded-shank cantilever; physical part, actuator adapter, fits, retention, attachment and V-01 mock-up remain open |
| RBLD8-style high-angle link ball | Reserve | provisional | Use if HRT8E-style packaging loses angular margin |
| RBLD12-style high-angle link ball | Upsize reserve | conditional | Reduces stress and can pass the low-load numeric standoff screen, but should not replace a clean load path |
| Bracket load path | Force line through ball center; avoid unsupported threaded-stud cantilever | hard constraint | M8 10 mm standoff bending remains a bottleneck; boxed/double-shear brackets are preferred |
| Pin/lug screen | JNT-BR-01 8 mm pin/lug passes the preliminary comparison at the revised 18 mm span | screened | Pin bending remains controlling; recheck after actual pin grade, spacer stack, attachment and measured loads |

## 5. Central Guide and Yaw Path Candidate

Current preferred physical layout is `RADIAL_3_CLEAN`; the compact YAW-A principle remains only as the central constraint subassembly:

```text
keyed square telescoping guide carries yaw torque
two-axis gimbal/yoke permits pitch and roll
X, Y, and yaw remain mechanically constrained
```

| Parameter | Candidate value | Status | Rationale |
| --- | --- | --- | --- |
| YAW-A constraint definition | constrain tx, ty, rz; allow tz, rx, ry | selected concept, critical open | Constraint rank 3 preserves required platform DOF |
| Gimbal design angle | 8 deg | provisional | Covers user-confirmed +/-3 pitch/roll plus 2 deg margin |
| Gimbal hard stop envelope | 10 deg total tilt; use independent +/-7 deg pitch and roll pin stops | provisional | Four simple pin stops keep the diagonal total tilt at about 9.89 deg; 10 deg is not a per-pin angle |
| Gimbal axis order | lower fixed +Y pitch pin, then upper local +X roll pin; `R = Ry(pitch) Rx(roll)` | selected concept | Keeps selected world-heading yaw at zero in the complete +/-3 degree grid and prohibits a third azimuth joint |
| Total yaw clearance | <=0.2 mm preferred, <=0.3 mm max | provisional | 0.2 mm gives about 0.23 deg estimated freeplay; 0.5 mm is rejected |
| Yaw freeplay target | <=0.25 deg target, <=0.5 deg max | provisional | Derived from clearance over 50 mm couple separation |
| Anti-yaw contact face | >=10 mm width, >=80 mm overlap, >=100 mm preferred overlap | provisional | At about 16 Nm PoC design torque, 80 mm overlap gives about 0.41 MPa contact pressure |
| Yoke yaw couple arm | >=50 mm | provisional | Keeps pin force around 328 N at the PoC design yaw torque |
| Yoke pin | >=10 mm diameter | provisional | Preliminary double-shear stress about 2.1 MPa |
| Yoke lug | >=8 mm thickness | provisional | Preliminary bearing stress about 4.1 MPa |
| Guide tube torsion reference | 50 x 3 mm square tube | screened | Tube itself is not the obvious torsional bottleneck at the simplified PoC torque |

At the active approximately 16.38 Nm YAW-A design torque and 3 degree pitch, approximately 16.36 Nm projects into the constrained yoke direction and approximately 0.86 Nm couples into the pitch/roll holding path. This is a load-path observation, not a holding-capacity approval.

Rejected or reserve paths:

| Path | Current decision | Reason |
| --- | --- | --- |
| Rigid keyed slide without gimbal | reject | Binds pitch/roll |
| Loose spherical central joint without yaw lock | reject | Leaves yaw unconstrained |
| Small 8 mm U-joint as sole yaw path | reject | Still below the simplified PoC design yaw torque |
| 12 mm U-joint or 16 mm ball spline | reserve only | May pass simplified torque numerically, but adds package/procurement/yaw-path complexity |
| Large direct-torque U-joint | archive as oversized reserve | No longer attractive for low-load PoC |
| Dual anti-yaw guides | reserve | Load screen pass, but width/alignment/overconstraint risk |

## 6. Frame and Cart Coupling Candidate

| Area | Candidate value | Status | Approval blocker |
| --- | --- | --- | --- |
| Frame profile | MISUMI HFS8-4040 for module/local stiff rails; exact cart receiver profile TBD | provisional | Connection stiffness, bracket, bolt, slot, and plate details unresolved |
| Stiffer frame reserve | MISUMI GFS8-4040 | conditional | Only upgrade if connection and deflection checks demand it |
| Top plate concept | HFS8 frame plus panel/metal load spreader concept | provisional | Acrylic must not be treated as sole structural member |
| Cart receiver fabrication | Aluminum profile rails/subframe plus bolted local insert plates | user preferred | Supports mock-up adjustment without welding; local inserts prevent profile-slot wear at concentrated contacts |
| Preferred cart receiver layout | CR-01: two longitudinal HFS8-4040 receiver rails, 760 mm x 560 mm receiver zone | provisional | About 4.50 kg screened mass, lighter than a self-contained rectangular subframe |
| Preferred cart receiver hardpoints | CR-01-H1: 12 mm locator / 8 mm local insert / shim rest pads / steel latch keepers | provisional | Bulk stresses are low in the active low-load screen; repeatability and slot slip remain the real risks |
| Preferred cart receiver connector | CR-01-H2-B: two M8-class T-slot fasteners for adjustment plus shoulder/key/positive stop for final shear/yaw locating | provisional | Friction-only passes a simplified slip screen but is rejected as a final locating method |
| Preferred connector stack rules | CR-01-H3: master locator fixes X/Y; slotted secondary locator fixes Y and releases X; rest pads carry Z seating; latch keepers carry preload/uplift | provisional | Prevents a hidden overconstraint while keeping the receiver easy to adjust and service |
| Preferred receiver hardware seed | CR-01-H4-S1: removable 12 mm master locator/bushing + 40 x 8 mm stop, 20 mm X-slot/diamond secondary, 40 x 30 mm shim seat, 5 mm keeper + secondary lock | provisional | Narrows the H3 rules into a mock-up assembly seed while retaining adjustment and replaceable wear surfaces |
| Cart receiver reserves | CR-02 HFS8 rectangular subframe; CR-03 GFS8 two-rail reserve; CR-04 30 mm profile study | conditional | Use only if cart cross support, stiffness, or mass budget pushes away from CR-01 |
| Cart locating principle | Tapered locating pins/rest pads carry shear; latches carry preload/uplift | provisional | Receiver geometry may be designed into the new profile cart frame |
| Cart locator topology | One master locator plus one slotted/diamond secondary locator; four rest pads | provisional | Avoids overconstraint while preserving repeatable seating |
| Latch family | DESTACO 323-R or safety-hook equivalent | provisional | Final SKU after receiver geometry is chosen |
| Latch count | 2 or more; current placeholder 4 | open | Do not freeze until cart interface layout is chosen |
| Secondary latch lock | required | open | Choose safety-hook latch or separate lock feature |
| Latch-closed sensing | required | open | Add to control architecture |

Low-load interface/latch screen:

| Screen item | Current value | Interpretation |
| --- | ---:| --- |
| Active interface vertical design load | about 618 N | Same order as primary actuator force screen |
| Active worst interface moment | about 108 Nm | Driven by payload CG height sensitivity, not by cart mass |
| Active guide-pin shear design load | about 154 N | Locating/rest geometry carries shear |
| Active total latch uplift design load | about 124 N | Latches are for preload/uplift and retention, not primary shear |
| Active per-latch uplift with 4 latches | about 31 N | Final latch count still follows receiver layout |
| CR-01 active worst rest-pad max load | about 331 N | Four pads remain compressive in the current active low-load screen |
| CR-01 locator yaw couple force at 520 mm span | about 32 N | Locator loads are low; wear, stiffness, and backlash still matter more than bulk strength |
| CR-01-H1 locator insert bearing | about 1.94 MPa | 12 mm locator interface in 8 mm local steel insert seed |
| CR-01-H1 rest pad contact pressure | about 0.28 MPa | 40 x 30 mm contact seed at the active max pad load |
| CR-01-H1 latch keeper bearing | about 0.25 MPa with 4 latches; about 0.49 MPa with 2 latches | Latch remains retention/preload only |
| CR-01-H1 insert fastening slip margin | about 6.45x with placeholder clamp/friction | Still requires dowel/key/positive stop after alignment |
| CR-01-H2 positive stop bearing | about 0.58 MPa | 40 x 8 mm contact seed at about 186 N connector demand |
| CR-01-H2 positive stop local tab bending | about 19 MPa | 6 mm tab with 25 mm cantilever seed |
| CR-01-H2 optional dowel shear | about 6.6 MPa | 6 mm dowel seed after mock-up alignment if repeatability requires it |
| CR-01-H3 profile wall / stop bearing | about 1.74 MPa | Uses 3x local load factor on the H2 connector demand |
| CR-01-H3 slot nut clamp contact pressure | about 18.5 MPa | Assumes 4000 N clamp over 18 x 12 mm contact; exact slot nut still open |
| CR-01-H3 mock-up trigger | 30 cycles; add backing/stiffer stack if shift >0.2 mm or torque relaxation >20% | Bench rule before freezing connector stack |
| CR-01-H3 service reserve | 25 mm tool access; 25 x 25 x 35 mm sensor envelope seed | Placeholder for latch-closed/cart-present sensor access |
| CR-01-H4 removable locator bushing | about 5.8 MPa bearing at 3x local screen load | 12 mm pin x 8 mm bushing seed; retain a replaceable wear surface |
| CR-01-H4 replaceable stop block | about 1.7 MPa bearing; about 32.7 MPa bending | 40 x 8 mm contact and 8 mm stop / 25 mm cantilever seed |
| CR-01-H4 optional 6 mm dowel | about 19.7 MPa shear; about 11.6 MPa bearing | Use only after mock-up alignment is frozen; do not make a second X/Y round locator |
| CR-01-H4 rest pad | about 0.8 MPa contact at 3x Z local factor | 40 x 30 mm pad; transfers Z seating only |
| CR-01-H4 backing rule | 60 x 40 x 6 mm steel backing bridge only on evidence | Add after 30-cycle shift, torque-loss, marking, or preload-drift trigger |
| JNT-BR-01 HRT8E axial capacity | about 2.72x axial-static margin to 2x screen | 5.29 kN axial static versus about 1.94 kN screen demand; do not substitute 26.77 kN radial value |
| JNT-BR-01 articulation | about 12.94 deg required; about 1.06 deg residual to 14 deg | Full 14 deg bracket no-contact check is mandatory |
| JNT-BR-01 local pin/lug screen | pin shear about 8.7 MPa; pin bending about 78.5 MPa; lug bearing about 13.7 MPa; lug root bending about 38.5 MPa | 8 mm pin / 8 mm lug / 18 mm supported-span / 32 mm width / 30 mm root-length preliminary comparison |

## 7. Control, Sensor, and Power Candidate

| Area | Candidate value | Status | Approval blocker |
| --- | --- | --- | --- |
| Independent actuator channels | 3 | fixed | Required for pitch/roll control |
| Tilt sensor PoC | BNO085 breakout | provisional | Test vibration, drift, mounting, magnetic environment |
| Industrial tilt sensor option | WT901C | conditional | Confirm exact interface SKU and protocol |
| Control deadband | +/-0.5 deg | provisional | Refine after sensor/actuator bench test |
| Target final leveling error | +/-1.0 deg | provisional | Do not guarantee until tested |
| Acceptance leveling limit | +/-1.5 deg | provisional | Revise after measured behavior |
| Position reference | Power-on homing to lower reference switch | open | Define homing speed, timeout, and stop behavior |
| Lost pulse detection | required | open | Needed because Hall feedback is incremental |
| Motor driver | MD13S x3, MD20A x3, MDD20A + single-channel driver, or multi-axis controller | open | Choose after bus voltage/current architecture |
| Actuator bus voltage | 12 V PoC baseline if Firgelli candidate is kept; 24 V only after actuator reselection | provisional | Do not mix a 12 V actuator with a blanket 24 V bus |
| 12 V supply class | about 12 V 23 A / 273 W before final derating | provisional | Revise after measured current and concurrency limits |
| Motor power isolation | Main relay or DC contactor must remove actuator motor power | open hard constraint | Define after bus voltage is resolved |
| Per-channel protection | Fuse or breaker per actuator drive channel | open hard constraint | Select after driver and bus voltage decision |

## 8. Candidate Decision Set for User Review

Recommended candidate direction to judge next:

1. Keep the three-actuator tripod concept.
2. Treat +/-3 deg pitch/roll and 100 mm lift as the baseline review target.
3. Archive +/-5 deg as a future stretch option, not a current requirement.
4. Archive +/-8 deg as sensitivity only.
5. Use three 120-degree radial actuators as the dominant physical layout; keep the keyed square guide plus compact two-axis Cardan visually and structurally subordinate.
6. Keep the current Firgelli 450 lbf actuator as the leading low-load PoC candidate unless packaging, duty, current, or tests fail.
7. Carry HRT8E-style M8 rod ends forward only with JNT-BR-01's centered double-shear load path, 5.29 kN axial capacity basis, and a 14 deg no-contact mock-up; retain high-angle link balls as reserve.
8. Keep cart coupling mechanical: locating pins/rest pads for shear and latch/secondary lock for preload/uplift.
9. Carry CR-01 as the preferred cart-side receiver layout: two 760 mm HFS8-4040 longitudinal rails in a 760 x 560 mm receiver zone.
10. Carry CR-01-H1 as the hardpoint seed: 12 mm locator, 8 mm local insert, 40 x 30 mm rest pads, 5 mm latch keepers, two M8-class fasteners per critical hard point, and dowel/key/positive stop after alignment.
11. Carry CR-01-H2-B as the connector topology seed: slot fasteners for adjustment/clamp and shoulder/key/positive stop for final locating; keep backing plate and through-bolting as reserves.
12. Carry CR-01-H3 as the connector-stack rule set: avoid secondary locator X overconstraint, avoid rest-pad hidden side stops, and avoid latch horizontal shear.
13. Carry CR-01-H4-S1 as the mock-up hardware seed, but keep exact purchased items, fits, torque, screw patterns, latch model, and sensor brackets open until bench evidence is available.
14. Keep 12 V power only if the 12 V actuator is kept; otherwise reselect the actuator/power bus together.

## 9. Must Resolve Before Design Freeze or Fabrication Release

- New aluminum-profile cart receiver envelope: CR-01, CR-01-H1, CR-01-H2-B, CR-01-H3, and CR-01-H4-S1 are current candidates, but exact profile section, slot nut, backing plate, insert plates, receiver zones, latch locations, sensor placement, profile wall bearing, bushing fit, dowel/stop screw geometry, service access, and cycling test results remain unapproved.
- Confirmation that the cart target remains about 10 kg after its frame concept is sketched.
- Moving/fixed mass split from CAD mass properties and BOM.
- HRT8E-style rod-end actual manufacturer drawing, 14 deg no-contact mock-up, pin retention, and bracket topology with no threaded-stud cantilever load path.
- YAW-A physical mock-up after the completed kinematic proof: guide/yoke axis clearance, yaw key/contact, backlash, side load, wear, and contamination.
- V-03 actuator endpoint/switch-before-stop evidence for the completed electrical-versus-mechanical limit hierarchy.
- Cart-present and latch-closed interlock layout.
- Confirmation that a 12 V PoC power architecture is acceptable.

Until these are resolved, the project remains:

```text
PHASE 0 DIRECTION REVIEWED
USER-CONFIRMED LOW-LOAD +/-3 DEG BASELINE
CR-01-H2 CONNECTOR TOPOLOGY SCREENED
CR-01-H4 HARDWARE SEED SCREENED
JNT-BR-01 HRT8E BRACKET SEED SCREENED
YAW-A AXIS ORDER AND STOP ENVELOPE SCREENED
WS-01-H20 270 MM WORKSPACE CANDIDATE SCREENED
APPROVE CONCEPT RECEIVED 2026-08-26
PHASE 2 DETAILED CAD BASELINE GENERATED
RADIAL_3_CLEAN ACTIVE DESIGN
LARGE CENTRAL GIMBAL/CARTRIDGE VARIANT ARCHIVED
BENCH EVIDENCE PENDING BEFORE DESIGN FREEZE
NOT APPROVED FOR FABRICATION
```
