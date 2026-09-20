# Target Requirements

## 2026-09-01 active manual targets

The following targets supersede powered-actuator and electronic-control targets for the current PoC.

| ID | Target | Current value | Status | Notes |
|---|---|---:|---|---|
| MR-001 | Active mechanism | Three manually adjustable linear struts at 120 deg | USER DIRECTED | Powered variant is archived |
| MR-002 | Manual Z adjustment | 0-50 mm | PROVISIONAL | Preserve the previous workspace if practical |
| MR-003 | Manual pitch | +/-3 deg | USER CONFIRMED | Set by measured strut lengths |
| MR-004 | Manual roll | +/-3 deg | USER CONFIRMED | Set by measured strut lengths |
| MR-005 | Nominal pin-centre length | 230 mm | DERIVED | Existing 3-RPS kinematic datum |
| MR-006 | Required 27-pose length range | 212.137-297.864 mm | DERIVED | Before real joint-stack and tolerance updates |
| MR-007 | Preliminary manual strut envelope | 205-305 mm | PROVISIONAL | Exact screw and end adapters remain open |
| MR-008 | Active power bus | None | USER DIRECTED | 24 V powered architecture is archived |
| MR-009 | Active sensors/controllers | None | USER DIRECTED | Use a mechanical level or digital angle gauge for setup only |
| MR-010 | Length retention | Positive mechanical lock | HARD CONSTRAINT | Friction clamp alone is insufficient |
| MR-011 | Purchase/fabrication release | false | OPEN GATE | Requires manual-strut selection, calculation and new Fusion audit |

The original TR table below is retained as design history. Where it conflicts with MR-001 through MR-011, the MR rows are authoritative for the active manual variant.

Targets may be adjusted with tradeoff reporting.

| ID | Target | Initial value | Status | Notes |
|---|---|---:|---|---|
| TR-001 | Overall length | 900 mm | TARGET | Keep if possible under cart footprint |
| TR-002 | Overall width | 800 mm | TARGET | Keep if possible under cart footprint |
| TR-003 | Disconnected leveling-device height envelope | 250-300 mm | USER CONFIRMED | User said the cart can be designed around this device height before coupling |
| TR-004 | Collapsed height planning value | 270 mm WS-01-H20 candidate, 250-300 mm envelope | PROVISIONAL | The 250 mm comparison geometry leaves only 2.54 mm beyond a 15 mm lower soft reserve; 270 mm gives 11.13 mm and remains inside the user-confirmed envelope |
| TR-005 | Vertical lift | 50-100 mm | TARGET | Compare 50/75/100 mm; 100 mm is not yet a full-angle workspace guarantee |
| TR-006 | Pitch range | ±3 deg | USER CONFIRMED | Needs coupled workspace, guide mobility, joint angle and stop-margin proof |
| TR-007 | Roll range | ±3 deg | USER CONFIRMED | Same as pitch |
| TR-008 | Leveling error | target ±1.0 deg, acceptance ±1.5 deg | PROVISIONAL | Needs physical backlash/vibration/sensor test |
| TR-009 | Power bus | DC 12 V | USER CONFIRMED | NAVIMRO delivery specification is 12 V; do not apply the DHLA6000 24 V page values |
| TR-010 | Operating environment | indoor / dry PoC | ASSUMED | Outdoor/IP target only if user requires |
| TR-011 | Rated material payload | 10 kg | USER CONFIRMED | Additional material payload excluding empty cart and module mass |
| TR-012 | Design material payload sweep | 5, 10 kg primary; 20 kg archived sensitivity | DERIVED | 10 kg drives the current PoC |
| TR-013 | Empty cart mass | 10 kg primary; 20/30 kg archived sensitivity | USER CONFIRMED | User expects about 10 kg and can design the cart around the module |
| TR-014 | Moving structure mass sweep | 15, 22 kg | DERIVED | Replace after fixed/moving mass split and BOM |
| TR-015 | Cart receiver fabrication direction | CR-01 two-rail aluminum profile receiver with local metal hard points | USER PREFERRED | 760 x 560 mm receiver-zone seed; exact profile section, connectors, insert plates, and receiver zones remain open |
| TR-016 | Cart receiver hardpoint seed | CR-01-H1: 12 mm locator, 8 mm local insert, shim rest pad, 5 mm latch keeper, positive anti-slip feature | DERIVED | Phase 1 screen only; exact bushing, connector, slot nut, shim, latch keeper, sensor, and stop details remain open |
| TR-017 | Cart receiver connector topology seed | CR-01-H2-B: T-slot clamp/adjustment plus shoulder/key/positive stop final locating | DERIVED | Slot friction only is rejected for final locating; exact slot nut, backing plate, stop block, dowel, and profile wall bearing remain open |
| TR-018 | Cart receiver connector stack rule | CR-01-H3: master locator X/Y fixed; secondary locator Y-only; rest pad Z-only; latch keeper preload/uplift-only | DERIVED | Prevents overconstraint; exact slot nut, backing plate, stop block, dowel, shim lock, and sensor brackets remain open |
| TR-019 | Cart receiver mock-up hardware seed | CR-01-H4-S1: 12 mm removable master locator/bushing and replaceable stop; secondary X-slot/diamond Y-only locator; 40 x 30 mm shim pad; 5 mm keeper with secondary lock | DERIVED | Simplifies fabrication/assembly direction while keeping purchased hardware, fits, torque, screw patterns, latch, and sensors open |
| TR-020 | Actuator bracket seed | JNT-BR-01-HRT8E: centered double-shear 8 mm pin / 8 mm lug / 18 mm supported pin span detailed seed; preserve full 14 deg HRT8E articulation | DERIVED | Uses official 8 mm bore, 23 mm body, 11 mm eye and 5.29 kN axial static data; exact spacers, pin retention, attachment, fits, fatigue/shock, and physical no-contact mock-up remain open |
| TR-021 | Pre-CAD workspace and guide candidate | WS-01-H20: 270 mm collapsed, 100 mm lift, +/-3 deg, 195 mm outer / 220 mm inner guide | DERIVED | 11.13 mm minimum actuator soft reserve and 88 mm minimum guide overlap in the nine-corner grid; bench evidence required |
| TR-022 | Static-bench travel limit hierarchy | 334-508 mm commanded Hall-count window; factory built-in electrical endpoints; 324/518 mm external mechanical-stop bounds | USER-REDUCED | External D4N/cams are omitted for stationary supervised tests; retain independent mechanical collars |
| TR-023 | Factory-eye joint seed | JNT-CG-01 nested two-axis trunnion; 8.2 mm factory hole; 12 mm inner gap; 6 mm plates; 22 mm trunnion span | DERIVED | Zero-offset measured-mockup seed replacing the serial HRT8E adapter; purchased eye and pin stack must be measured |
