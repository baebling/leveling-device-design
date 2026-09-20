# Frame, Guide, Joint, And Locating Sources

Access date: 2026-08-24

## Frame Candidates

| Source ID | Candidate | Key official values | Decision |
|---|---|---|---|
| SRC-FRM-001 | MISUMI KHFS8/HFS8-4040 | 40x40 mm, 1.73 kg/m, area 640 mm2, Ix/Iy 10.4e4 mm4 | Baseline profile |
| SRC-FRM-002 | MISUMI GFS8-4040 | 40x40 mm class, 2.17 kg/m, Ix/Iy 13.76e4 mm4 | Stiffer alternative |
| SRC-FRM-003 | Bosch Rexroth profile system | Industrial profile/catalog benchmark | Supplier benchmark, not selected yet |
| SRC-FRM-004 | MISUMI Korea economy frames | Domestic price screening | Procurement reference only |

## Guide And Locating Candidates

| Source ID | Candidate | Key official values | Decision |
|---|---|---|---|
| SRC-GDE-001 | THK HSR LM guide | HSR 15+ dynamic load ratings from 10.9 kN upward | High-rigidity but likely overkill for central anti-yaw guide |
| SRC-GDE-002 | HIWIN MGN15H | Dynamic 6370 N, static 9110 N | Compact guide candidate |
| SRC-GDE-003 | MISUMI TPCAT tapered locating pin | Tool steel equivalent, 58-62 HRC, CAD data | Cart locator candidate |
| SRC-GDE-004 | KIPP locating pins/rest pads | Ball-end and locating/rest pad families | Alternative locating hardware |

## Joint Candidates

| Source ID | Candidate | Key official values | Decision |
|---|---|---|---|
| SRC-JNT-001 | MISUMI PHSOSM8 | Radial static load 2.69 kN, allowable angle 12 deg | Minimum low-cost joint candidate |
| SRC-JNT-002 | THK POS8 | 8 mm ID rod end; CAD/catalog available | Candidate, load table must be checked |
| SRC-JNT-003 | Minebea/MISUMI HRT8E | Static radial 26770 N, allowable tilt 14 deg | Robust preferred joint candidate if cost/availability works |

## Provisional Structural Decision

- Keep the current hybrid architecture: aluminum profile frame plus metal load-transfer plates; acrylic only as panel/cover and local supported top surface.
- Baseline profile: HFS8-4040 or equivalent 40x40 heavy 8-series profile. Use 4080/GFS8 where spans or actuator brackets drive deflection.
- Rod ends should be at least M8 with allowable articulation greater than the required joint angle. For safety margin and shock uncertainty, HRT8E-class static capacity is preferable to small stainless oil-free PHSOSM8 for load-bearing actuator joints.

## Open Items

- Bracket plate thickness and bolt sizes must be derived from actual bracket geometry.
- Central guide type remains unresolved: keyed square tube is low-cost, but LM guides give better quantified load ratings.
- Final material choice must consider local fabrication and available stock thicknesses.
