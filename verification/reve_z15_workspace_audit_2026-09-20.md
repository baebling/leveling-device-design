# Rev E physical Z=15--65 mm workspace audit

## Result

`PASS-DIGITAL` — preliminary finite CAD/kinematics screen only. It does **not** grant fabrication or purchase release.

## Exact finite grid

| Dimension | Samples | Values |
|---|---:|---|
| Physical Z | 11 | 15, 20, …, 65 mm |
| Pitch | 13 | -3.0, -2.5, …, +3.0° |
| Roll | 13 | -3.0, -2.5, …, +3.0° |
| Pose samples | 1859 | 11 × 13 × 13 |
| Pin-length evaluations | 5577 | three axes per pose |

The retained `revd_data.pin_lengths` calculation returned a minimum of **221.281490 mm** at physical Z=15 mm, pitch=+3.0°, roll=+3.0°, axis 3; and a maximum of **289.522702 mm** at physical Z=65 mm, pitch=-3.0°, roll=-3.0°, axis 3. This is within the finite-screen bounds 221.0--290.0 mm.

## Rev E CAD collisions at physical Z=65 mm

`cad.profile_radial_reve_actual_vendor.collision_audit` was run for the required nine pitch/roll corner-and-centre combinations.

| Pitch (°) | Roll (°) | Result | Maximum unintended intersection (mm³) |
|---:|---:|---|---:|
| -3.0 | -3.0 | PASS | 0.000000 |
| -3.0 | +0.0 | PASS | 0.000000 |
| -3.0 | +3.0 | PASS | 0.000000 |
| +0.0 | -3.0 | PASS | 0.000000 |
| +0.0 | +0.0 | PASS | 0.000000 |
| +0.0 | +3.0 | PASS | 0.000000 |
| +3.0 | -3.0 | PASS | 0.000000 |
| +3.0 | +0.0 | PASS | 0.000000 |
| +3.0 | +3.0 | PASS | 0.000000 |

All nine CAD results: **PASS**.

## Limits and next gate

- This finite sampling is not a continuous-workspace proof.
- Actual actuator internal limit-switch trip points remain unverified.
- Guide overlap is not asserted unless the modeled assemblies explicitly contain and check that guide.
- This result grants no fabrication or purchase release.
- If a later physical guide or cable check fails, retain the physical Z=15 mm datum and reduce command maximum Z to 35 mm.
