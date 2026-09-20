# Manual 3-RPS Rev M1 custom-part and assembly specification

Date: 2026-09-02  
Status: detailed CAD review complete; quotation and received-part inspection required before order release

## Coordinate and process rules

- Assembly coordinates are Fusion coordinates: lower frame bottom `Z=0`, collapsed upper-frame top `Z=300 mm`.
- Support labels are `A1=90 deg`, `A2=210 deg`, and `A3=330 deg` about the assembly origin.
- All dimensions below are millimetres. Remove sharp edges and burrs without rounding functional datums.
- Clevises are machined from one A6061-T6 billet. No welding is permitted.
- Do not machine the batch from nominal tube dimensions alone. Inspect the received tube first.
- Coarse and fine adjustment is performed only with payload removed and the upper frame independently supported.

## C01 lower local adapters, three variants

Common blank: `120 x 80 x 8`, A6061-T6.

- Two profile holes: `diameter 9 through`, centres at assembly global `X = +/-48` from each adapter centre.
- Two clevis holes: drill `diameter 6.8`, tap `M8 x 1.25 through`, centres `+/-20` along that support's radial axis.
- A1 radial direction: `(0, +1)`; tapped-hole offsets `(0, +/-20)`.
- A2 radial direction: `(-0.866025, -0.5)`; tapped-hole offsets `(+/-17.3205, +/-10)` with matching signs.
- A3 radial direction: `(+0.866025, -0.5)`; tapped-hole offsets `(+/-17.3205, -/+10)`.
- Mark each part `A1`, `A2`, or `A3`; the hole patterns are not interchangeable.

## C02 lower one-piece clevises

One local geometry, installed at the three support azimuths.

- Base: `60 radial x 50 tangential x 8`.
- Two base clearance holes: `diameter 8.6`, `40` pitch on radial centreline.
- Ear length: `50 radial`; ear thickness `6`; clear gap `34`; outside width `46`.
- Pivot bore: `diameter 8.2 through both ears`, coaxial; centre `28` above base top.
- Pivot axis is tangential to the support circle.

## C03 upper one-piece clevises, three installed orientations

- Base: `100 global-X x 60 global-Y x 8`.
- Two profile clearance holes: `diameter 6.6`, `84` pitch on global X centreline.
- Ear length: `50 radial`; ear thickness `6`; clear gap `20`; outside width `32`.
- Pivot bore: `diameter 10.2 through both ears`, coaxial.
- In the collapsed assembly the base occupies `Z=262..270`; pivot centre is `Z=235`.
- Mark A1/A2/A3 after machining so each radial ear orientation is retained.

## C04 finished outer tubes

- Blank: aluminum tube `OD32 x ID28 x L160`; 6061-T6 preferred.
- Lower pivot bore: `diameter 8.2`, centre `16` from lower tube end.
- Coarse-pin bore: `diameter 8 +0.1/0`, centre `131` from lower tube end.
- JFM housing: final `diameter 28.000..28.021` for the last `21` at the upper end.
- Keep pivot and coarse bores normal to the strut axis and parallel to one another.

## C05 finished inner tubes

- Blank: aluminum tube `OD25 x ID21 x L150`; final sliding OD `24.948..25.000`.
- Six coarse holes: `diameter 8 +0.1/0`, centres `32, 47, 62, 77, 92, 107` from lower end.
- Plug retainer hole: `diameter 4.2`, centre `127.5` from lower end.
- Ream the six paired walls in one setup to maintain pin alignment.

## C06 POM lower guide rings

- POM-C, `OD27.6 x ID25.10 x L12`.
- Dry-fit with the actual tubes. A split installation is permitted if required by assembly sequence.

## C07 M10 threaded plugs

- A6061-T6, `OD20.8 x L30`.
- Axial female thread `M10 x 1.5`, useful depth at least `22`.
- Retainer cross hole `diameter 4.2`, centre `7.5` from plug lower end (`22.5` from outer end).
- Cross-drill the plug and C05 inner tube together after dry fit.

## F08/F09 pivot pins and F10 shims

- Lower pin: shoulder `diameter 7.98 h9`, grip `46`, head `diameter14 x 7`, M8 threaded end, `13 AF x 6.5` prevailing-torque locknut.
- Upper pin: shoulder `diameter 9.98 h9`, grip `32`, head `diameter16 x 5`, M10 threaded end, `17 AF x 8` prevailing-torque locknut.
- No thread may lie within a clevis ear, tube pivot bore, shim, or PHS10 bore.
- Upper shim: SUS304, `ID10.2 x OD18 x t3`, six used; thickness tolerance `+/-0.05` preferred.

## Manual strut assembly order

1. Inspect C04/C05 dimensions and remove internal burrs from all cross holes.
2. Press one JFM-2528-21 into the reamed upper end of each C04 tube; support the bearing flange.
3. Install one C06 guide at the lower end of each C04 tube.
4. Insert C07 into C05, align the `diameter 4.2` hole, and retain with the M4 x 40/nyloc set without crushing the tube.
5. Cut the M10 x 1.5 rod into three `L53` studs; deburr and verify thread engagement in both C07 and PHS10.
6. Lock the stud to C07 with the lower thin nut. Leave the upper thin nut loose for final setting.
7. Insert C05 through C06 and JFM, select a coarse hole with BJ775-08040-SUS, then install the PHS10.
8. Mount C04 at the lower clevis with the F08 pin set.
9. Place one F10 shim on each side of PHS10 and mount it in C03 with the F09 pin set.
10. With the upper frame separately supported, remove the upper pivot pin as needed, rotate PHS10 for fine adjustment, reinstall the pin, and lock the upper thin nut.

## Received-part inspection hold points

- `PHS10`: right-hand M10 x 1.5; bore 10 H7; ring width 14; OD26; thread depth21.
- `BJ775-08040-SUS`: diameter8; grip40 +0.5/0; do not accept another grip length.
- `JFM-2528-21`: ID25; OD28; flange35; L21; flange t1.5.
- `DNF4040`: slot `8.3 +/-0.3`; `DNF3030`: slot `6.3 +0.2/0`.
- Dry-build one complete A1 strut and both clevises before releasing the other two sets for final machining.

## Release statement

The CAD and dimension basis are complete enough for quotation and one-set trial manufacture. Batch purchase/fabrication remains on hold until exact supplier drawings, delivered prices, and received-part measurements satisfy the items above.
