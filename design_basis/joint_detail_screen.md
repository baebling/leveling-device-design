# Joint Detail Screen

Status: preliminary Phase 0 detail screen. Not approved for fabrication.

Current-use note: this document includes earlier conservative +/-5 deg and high-yaw-torque checks. The active design direction is now the user-confirmed 10 kg / +/-3 deg low-load PoC baseline, but the bracket load-path warning still applies.

## Purpose

`design_basis/joint_candidate_screen.md` identified viable joint families by angle and catalog static capacity. This follow-up checks first-order packaging risks:

- Actuator joint pin double shear.
- Bracket lug bearing stress.
- Threaded stud cantilever bending if the bracket load line is offset.
- Central Cardan yaw-torque requirement.
- Central square-tube torsion as a possible yaw-torque path reference.

All values are screening calculations only. They do not approve material, heat treatment, thread engagement, fatigue, backlash, fasteners, welds, or fabrication drawings.

## Actuator Joint Equations

The script `calculations/joint_detail_screen.py` uses:

```text
tau_pin = F / (2 * pi * d_pin^2 / 4)
p_bearing = F / (d_pin * t_lug)
sigma_stud = 32 * F * e / (pi * d_root^3)
```

Where:

- `F` is the worst-case actuator axial force from `load_distribution.py`.
- `d_pin` is the joint pin diameter.
- `t_lug` is the assumed lug thickness.
- `e` is an unsupported threaded-stud standoff.
- `d_root` is a conservative root-diameter placeholder.

Preliminary allowable placeholders:

- Pin shear: 100 MPa.
- Lug bearing: 100 MPa.
- Stud bending: 150 MPa.

These are not final material allowables. They exist only to show which load path is dangerous.

## Actuator Joint Result

For the archived +/-5 deg stretch screen under the current low-load mass basis:

| Candidate | Pin shear | Lug bearing | Cantilevered stud bending at 10 mm standoff | Max standoff for 150 MPa placeholder | Result |
|---|---:|---:|---:|---:|---|
| RBLD8-style M8 link ball | 10.9 MPa | 17.1 MPa | 407 MPa | 3.7 mm | Redesign load path |
| RBLD12-style M12 link ball | 4.9 MPa | 11.4 MPa | 119 MPa | 12.6 mm | Passes numeric standoff screen; reserve only |

Interpretation:

- Double-shear pin stress and lug bearing are not the current bottleneck in this screen.
- In the later JNT-BR-01 HRT8E package screen, pin bending remains the controlling local comparison. The official 23 x 11 mm envelope superseded the old 16 mm gap with an 18 mm detailed CAD seed; do not widen it again without recalculation.
- Unsupported threaded-stud bending remains the bottleneck for M8-style packages.
- The joint bracket must route actuator force through the ball center or very close to it.
- Do not treat a threaded shank as a convenient cantilever spacer even when an upsize passes a first-order screen.
- If packaging forces a standoff, the design should upsize the joint and/or use a clevis-yoke/boxed bracket arrangement that eliminates stud bending.

This modifies the earlier candidate conclusion:

- HRT8E remains a possible +/-3 deg baseline rod-end candidate only if the bracket preserves full articulation and avoids threaded-stud cantilever bending.
- RBLD8-style link ball remains a high-angle candidate by catalog angle, but not as an unsupported standoff joint.
- RBLD12-style upsize should be kept as a reserve if packaging cannot make M8 compact enough.

## Central Cardan Torque

The central guide must mechanically constrain yaw. If a universal joint or gimbal interrupts the yaw torque path, that joint must transmit the yaw torque, not just articulate.

The preliminary yaw torque screen uses:

```text
F_horizontal = m * g * a_horizontal * design_factor
T_yaw = F_horizontal * r_cg
```

Screen case:

- Total lifted mass: 90 kg.
- Horizontal acceleration: 0.5 g.
- Design factor: 2.0.
- CG offset radius: 141 mm from 100 mm X and 100 mm Y offsets.

Result:

- Yaw torque: about 125 Nm.
- Peak/design torque with 2x screen: about 250 Nm.

Ruland examples:

| Candidate | Catalog angle | Rated torque | Peak torque | Result |
|---|---:|---:|---:|---|
| MUS15-8-8-F | 45 deg | 15.3 Nm | not listed in screen | Fails torque screen |
| MUSSK22-12-12-F | 45 deg | 39 Nm | 197 Nm | Fails conservative torque screen |

Interpretation:

- The small Ruland U-joints are useful references for geometry and angle, but should not be used as the sole yaw-torque path in the current concept.
- The central Cardan/gimbal must either be a much higher torque implementation, or yaw torque should be carried by a separate keyed/anti-yaw path that does not overload the U-joint.

## Square Tube Torsion Reference

The current 50 mm square, 3 mm wall central guide tube was screened as a closed thin-wall torsion member.

At 125 Nm:

- Estimated torsional shear: about 9.4 MPa.
- Estimated twist over 190 mm: about 0.17 deg.

This suggests the tube itself is not the obvious torsional bottleneck. The remaining risk is the connection through the Cardan/gimbal, keys, sliders, bearings, fasteners, and backlash.

## Design Conditions Carried Forward

Before parameter approval:

1. Actuator joint force should pass through the ball center; unsupported threaded-stud standoff should be avoided.
2. Use double-shear or boxed brackets for actuator pins where possible.
3. Keep RBLD12-style upsize available if M8 packaging cannot remove bending.
4. Do not approve a small catalog U-joint as the sole yaw-torque path.
5. Define a yaw-torque path through the central guide, gimbal, keys, fasteners, and upper platform.
6. Recalculate after actual mass, cart interface, and final pitch/roll workspace are selected.

```text
JOINT DETAIL SCREEN COMPLETE
ACTUATOR STUD CANTILEVER BENDING IS A DESIGN BLOCKER
SMALL CENTRAL U-JOINTS FAIL CONSERVATIVE YAW TORQUE SCREEN
CENTRAL CARDAN/YAW TORQUE PATH STILL CRITICAL_OPEN
NOT READY FOR APPROVE PARAMETERS
```
