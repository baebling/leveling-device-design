# RADIAL_3_CLEAN actuator joint detail CAD

Date: 2026-08-27

Status: Phase 2 preliminary detailed CAD seed. Not approved for fabrication.

## Decision

Keep the three equal 120-degree radial actuators and replace the blocky placeholder clevises with six serviceable `JNT-BR-01-HRT8E` packages. Each package uses a centered double-shear load path, replaceable lug bushings, compact misalignment spacers and retained M8 pin hardware.

## Official HRT8E inputs

MinebeaMitsumi official data was rechecked on 2026-08-27:

- bore: 8 mm
- body diameter: 23 mm
- eye width: 11 mm
- center height: 8.25 mm
- center-to-end: 46 mm
- thread: M8x1.25
- thread length: 29 mm
- allowable articulation: 14 deg
- axial static limit: 5.29 kN

Source: https://product.minebeamitsumi.com/en/product/category/bearing/rodend/standard/parts/HRTE.html

## Geometry revision

The earlier 16 mm inner-gap seed was retained before the official body dimensions were applied. A conservative flat-lug projection gives about 16.24 mm at 14 deg. Therefore 16 mm cannot conservatively clear the catalogue angle. The active preliminary gap is 18 mm, leaving about 1.76 mm total numerical clearance.

Physical two-plane and diagonal motion still must be checked because the real spherical insert, chamfers, spacer shape and manufacturing variation are not represented completely.

## Active CAD seed

| Item | Preliminary value |
|---|---:|
| Lug thickness | 8 mm |
| Inner gap / pin support span | 18 mm |
| Lug bushing envelope | 12 mm OD x 8.2 mm ID x 8 mm |
| Misalignment spacer envelope | 3.5 mm wide x 10.8 mm OD, two per joint |
| Pin | 8 mm shoulder-pin envelope |
| Pin retention | head + washer + locking-retainer envelope |
| Mounting | four 8.5 mm clearance holes per boxed yoke |

At the regenerated low-load screen, pin double shear is about 8.7 MPa, pin bending about 78.5 MPa, lug bearing about 13.7 MPa and lug-root bending about 38.5 MPa. These are placeholder comparisons, not certified allowables.

## CAD outputs

- `outputs/cad/step/radial_actuator_joint_packages_neutral.step`
- `outputs/renders/phase2_actuator_joint_detail.png`
- Full assembly STEP states under `outputs/cad/step/`

## Still open

- Actual HRT8E purchase and dimensional inspection
- Female-threaded adapter from the selected actuator end to HRT8E M8x1.25
- Exact shoulder bolt or clevis pin grade, shoulder length and lock method
- Bushing material, fit, lubrication and replacement retention
- Bracket material, joining method, backing plate, bolt grade and torque
- 14 deg two-plane and diagonal physical sweep with no contact
- Fatigue, shock, impact and wear validation

V-01 remains open until measured physical evidence is stored in `logs/`.
