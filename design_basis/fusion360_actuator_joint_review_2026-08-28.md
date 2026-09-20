# Fusion 360 actuator joint review - 2026-08-28

## Review scope

The user opened `NAVIMRO_detailed_collapsed_revC.step` in Fusion 360 and reported that the actuator mounting method was not clear. The opened Fusion model, the Rev C component manifest, the CadQuery source, and direct solid-intersection checks were reviewed.

## Decision

The radial three-actuator concept remains usable, but the Rev C actuator-end detail is **not a fabrication-ready assembly**. It is a planning envelope and must be rebuilt before actuator/bracket ordering or machining release.

## Rev D addendum

The initial corrective proposal below assumed that the DIHOOL U and H brackets could form one orthogonal two-axis stack. The official IPS-B1 and IPS-B2 drawings and product photographs do not support that assumption: they are alternative single-axis mounts. Rev D therefore supersedes the proposed U/H stack with six NAVIMRO `K02020097 / JMC JFT-8R` spherical rod ends in locally fabricated double-shear yokes.

Each actuator end now has a separate catalog-modeled spherical housing and ball, a real 8.2 mm pin bore, two `NVR-P16` steel lugs, two fitted spacers, an M8 pivot stack, and an explicit provisional M8/A2 adapter. Full lift and pitch/roll-corner screening gives a pin-centre range of `269.040 to 394.209 mm` and a worst required articulation of `10.852 degrees` including a one-degree margin, below the catalog `13 degrees`. Direct solid checks found no actuator-envelope intersection with either frame in the six exported poses and no pivot-pin overlap with the modeled bores.

Rev D closes the geometric defect but does not close the supplier gate. Confirm the delivered A2 male/female M8 interfaces, actual pin-centre limits, rod-end receipt dimensions, pivot shoulder length, Hall wiring/current, and supplier STEP before ordering or fabrication release.

## Findings

1. `LA2000_A2_PROVISIONAL_*` is a conservative cylinder/sphere planning body, not the supplier actuator STEP. It has no physical rear eye, front M8 adapter, eye bore, shoulder, or retaining details.
2. Each `ACT*_LOWER/UPPER_UH_bracket_PROVISIONAL` is one rigid compound. The U and H brackets are not separate moving parts and the model does not show the two orthogonal pivot axes required at an actuator end.
3. Only one pivot fastener is modeled at each actuator end. A true U/H universal stack needs the U-to-H pivot and the H-to-eye pivot to be represented separately unless the delivered hardware proves another arrangement.
4. The purchased bracket candidates are 6 mm-hole `IPS-B1` U and `IPS-B2` H brackets, while Rev C inserts an M8 pivot bolt. This is a direct nominal-size conflict.
5. Pivot holes are not cut in the provisional bracket solids. The modeled pin intersects the bracket by about `603.186 mm3` at each checked end.
6. The actuator planning body also intersects the pivot pin. At actuator 1, the lower pin/body intersection is about `3269.477 mm3` and the upper pin/body intersection is about `492.390 mm3`; this confirms that the eye and bore are not modeled.
7. Bracket/frame contact is represented by overlapping solids rather than mating faces and holes. For actuator 1 in the collapsed pose, the lower bracket intersects the lower spreader by about `3600 mm3`, and the upper bracket intersects the upper spreader by about `3800 mm3`.
8. The actuator planning bodies have major collisions with the supporting structure. In the collapsed pose, actuator 1 intersects its lower spreader by about `18461.867 mm3`; actuators 2 and 3 intersect the lower crossmember by about `16861.5 mm3` each. Upper-frame collisions are also present.
9. Existing Rev C tests verify component uniqueness, presence, valid solids, and export/re-import. They do not verify actuator/frame interference or that fasteners pass through actual bores.
10. Fusion imports the STEP mainly at group level, which further hides individual actuator-end parts and makes the intended assembly sequence difficult to inspect.

## Required corrective model

Build one verified actuator-end subassembly before copying it to all six ends:

- exact delivered `LA2000-125150` A2 body and both end interfaces;
- separate `IPS-B1-6MM-U` and `IPS-B2-6MM-H` components;
- separate orthogonal pivot axes with actual pin diameters, heads, retainers, washers, and spacers;
- explicit eye/adapter bore and width;
- a lower and an upper spreader interface with mating faces, through-holes or threads, edge distances, and tool access;
- revolute joints or parameterized poses that expose the required articulation;
- collision checks at collapsed, neutral, raised, and the full pitch/roll `+/-3 deg` corner sweep.

## Information gate

Before final geometry is released, obtain the supplier drawings or measurements for:

- exact A2 front and rear end type;
- pin-center `Lmin` and `Lmax`;
- eye hole diameter, eye width, shoulder diameter, and M8 thread engagement;
- U/H bracket internal width, plate thickness, hole spacing, included pins, and intended U-to-H stacking method;
- motor/gearbox envelope and cable-exit keep-out.

Until those values are closed, use the current actuator geometry only for rough layout and budget planning. Do not use it to drill the spreaders, order non-returnable actuator variants, or approve fabrication.
