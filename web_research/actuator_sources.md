# Actuator Sources

Access date: 2026-08-24

## Candidate Summary

| Source ID | Manufacturer | Candidate | Key official values | Fit for PoC | Decision |
|---|---|---|---|---|---|
| SRC-ACT-001 | Firgelli | F-SD-H-450-12V-8in Hall | 450 lbf, 8 in stroke, 319/523 mm, 6 mm/s, 5.5 A, 12 V, 25% duty, IP66, Hall feedback, built-in limits | Plausible low-cost candidate for conservative PoC | Candidate only; not approved until coupled workspace, joint angle, homing, current and package checks pass |
| SRC-ACT-002 | Ewellix | CAHB-10 | 1500 N push/pull, 50-300 mm stroke, 12/24 V, IP66S, 25% duty | Good documentation, likely marginal under worst load | Alternative only |
| SRC-ACT-003 | TiMOTION | MA2 | 8000 N push, 4000 N pull, 25-1000 mm stroke, IP69K static, Hall/pot options | Robust if budget/space allow | Industrial candidate if calculations demand it |
| SRC-ACT-004 | LINAK | LA36 | 6800 N, 100-1200 mm stroke, 12/24/36/48 V, IP66 dynamic/IP69K static | Industrial-grade candidate | Candidate if calculations demand it, but likely costly/large |
| SRC-ACT-005 | Thomson | Electrak HD | 25% duty for many variants, IP66 dynamic/IP67/IP69K static, load-lock ball nut | High reliability benchmark | Candidate if calculations demand it, but likely costly/large |
| SRC-ACT-006 | Progressive Automations | PA-17 | 850/2000 lbf dynamic options, up to 4000 lbf static, IP65, 25% duty | Oversized fallback for high safety factor or 100 kg study | Do not choose unless scope changes |
| SRC-ACT-007 | Firgelli | MB21 body bracket | Fixed-position Super Duty body support; rubber gasket; official STEP 50 x 82.854 x 100 mm envelope | Traceable LS-01 fixed datum | Candidate only; external stop reaction is not published |
| SRC-ACT-008 | Firgelli | MB17 clevis bracket | 8 mm pin, 180 deg pivot, official STEP | Clevis mounting reference | Reference only; does not supply spherical articulation |
| SRC-ACT-009 | Firgelli | MB20 body swivel bracket | Body-mounted swivel support with rubber gasket and official STEP | Alternate body datum | Not selected for fixed LS-01 datum |
| SRC-ACT-010 | Firgelli | Super Duty family mounting-end drawing | 8.2 +/-0.10 mm mounting hole and 20 mm eye OD on the referenced 220 lbf 2-inch drawing | Mounting-eye topology reference | Reference only; selected 450 lbf 8-inch eye thickness must be measured |

## Candidate Logic

- The current geometry requires a coupled Z-pitch-roll workspace check, not a separate lift/tilt check.
- With a 5 mm end margin, the current CAD geometry supports at least about +/-5.75 deg symmetric pitch/roll over 0-100 mm lift. With a 15 mm end margin, this drops to about +/-3.5 deg.
- Minimum lift at +/-3 deg with a 15 mm end margin leaves only about 2.5 mm effective margin, so the geometry should not yet be approved as a full-workspace claim.
- Design loads now include material payload 5/10/20 kg, cart 10/20/30 kg, and moving structure 22/30/40 kg. This makes the Firgelli 450 lbf unit a candidate for conservative 10 kg PoC work, not a final selection.
- Upgrade to TiMOTION MA2, LINAK LA36, Thomson Electrak HD, or another industrial actuator should be investigated only if calculated force, static holding, duty cycle, speed, package length, or control requirements cannot be satisfied by the baseline candidate.

## Duty Cycle Interpretation

The common 25% duty-cycle rating means a demo script must be timed. For a 100 mm lift at about 6 mm/s, one extension is roughly 17 s at no load; extend/return is roughly 34 s plus correction motions. A 10-cycle continuous demo should include waiting time so motor-on time stays below rated duty. This requires validation with the final actuator datasheet and actual loaded speed.

## Open Items

- Resolve bus voltage: current candidate is 12 V; 24 V requires actuator reselection/24 V variant or a deliberately sized DC-DC architecture.
- Define homing and lost-pulse handling because Hall feedback is incremental.
- Confirm static holding/brake/self-locking behavior using the final selected actuator datasheet, not only dynamic force.
- Confirm lead time and domestic procurement route.
- Obtain vendor confirmation that MB21 and the actuator housing can react LS-01 external stop loads, or move the fixed stop frame to the lower yoke.
- Measure the purchased front and rear eye thickness, pin stack and shoulder geometry before machining the JNT-CG-01 cradle.
- Keep the serial HRT8E adapter archived unless the support geometry or actuator retracted length changes; its provisional 64 mm total extension fails the present workspace.
