# Manual 3-RPS Rev M1 working decisions

Date: 2026-09-01
Status: design in progress; not released for purchase or fabrication

## Selected topology for detailed CAD

Each powered LM4075OE axis is replaced by one two-stage manual strut:

1. A 32 mm OD x 2 mm wall x 160 mm aluminium outer round tube.
2. A 25 mm OD x 2 mm wall x 150 mm aluminium inner round tube.
3. Six coarse positions at 15 mm pitch, retained by an 8 mm positive-lock pin.
4. A 0-15 mm M10 x 1.5 fine adjustment screw.
5. A THK PHS10 female rod end at the upper joint.
6. An M8 lower pivot in a bolted A6061 clevis.
7. An igus JFM-2528-21 flanged sleeve bearing at the upper end of the outer
   tube and a custom POM lower guide ring at the lower end of the inner tube.

The intended pin-centre adjustment is 205-295 mm. Coarse travel is 75 mm and
fine travel is 15 mm. The fine adjuster is disconnected from the upper pin,
turned, locked with jam nuts, and reconnected while the upper frame is
independently supported. Adjustment under payload is not allowed.

## Geometry retained from powered Rev D

- Lower frame: 700 x 700 mm, DNF4040 profile family.
- Upper frame: 700 x 700 mm, DNF3030 profile family.
- Support azimuths: 90, 210, and 330 degrees.
- Lower support radius: 75 mm.
- Upper support radius: 250 mm.
- Lower pin centre Z: 84 mm.
- Upper ring centre Z at collapsed neutral: 235 mm.
- Allowed motion: Z 0-50 mm, pitch/roll +/-3 degrees.
- Three local lower adapters: A6061-T6, 120 x 80 x 8 mm. There is no central
  hub plate.

The Rev D spatial constraint model, rather than the earlier equal-radius
screen, is the active kinematic datum for Rev M1. Its 27-pose grid requires
218.958-279.846 mm pin-centre length, leaving about 13.96 mm lower margin and
15.15 mm upper margin in the selected 205-295 mm manual range.

## Product-backed dimensions to verify before CAD release

- DNF4040 and DNF3030 section, slot, and centre-bore dimensions.
- 4035 and DCB3025 frame connector envelope and hole positions.
- THK PHS10: M10 x 1.5 female thread, 10 mm bore, 26 mm outer diameter,
  14 mm inner-ring width, 43 mm ring-centre-to-thread-end dimension, and
  8 degree minimum listed permissible tilt angle.
- IMAO BJ775-08040-SUS: 8 mm shank, 40 mm grip length, 9.4 mm ball diameter,
  8 mm end allowance, and 65 kN listed minimum double-shear force.
- igus JFM-2528-21: 25 mm nominal shaft, 28 mm housing bore, 35 mm flange
  diameter, 21.0 mm bearing length, and 1.5 mm flange thickness. The upper
  21.0 mm of the outer tube is finish-reamed to 28H7 after cutting.

## Active axial stack, local to each strut

- Lower pivot centre: `s = 0 mm`.
- Outer tube: `s = -16 to 144 mm`.
- Outer coarse-pin hole centre: `s = 115 mm`.
- Inner tube at coarse position 0: `s = 8 to 158 mm`.
- Inner-hole offsets from its lower end: 107, 92, 77, 62, 47, and 32 mm.
- At coarse position 75 mm, the remaining telescopic overlap is 61 mm.
- PHS10 thread end is 43 mm below its ring centre.
- The fine-adjuster free span is 4-19 mm for each coarse position, producing
  pin-centre lengths of 205-295 mm without relying on thread runout.

Tube mill tolerance is not assumed. Each supplied tube is measured before
machining; the bushing housing is finish-reamed and the POM guide ring is
finish-fitted to the measured bores and shafts.

The first Fusion interference run found and corrected three real layout
problems: the plug cross-bolt was moved below the M10 stud engagement, the
upper clevis gap was increased from 16 to 20 mm with two 3 mm side shims, and
the upper profile fasteners were moved outboard on a 100 mm base. These are
active design dimensions, not optional assembly adjustments.

The corrected Fusion run exposed a second issue: the M5 plug-retainer head and
nut touched the JFM flange. The retainer was therefore changed to M4 and placed
22.5 mm below the inner-tube end, leaving modelled clearance to both the JFM
flange and the end of the M10 stud.

## Release gates

- Complete detailed product-image evidence register.
- Generate a native Fusion 360 assembly with separately named components and
  all pins, bolts, nuts, spacers, tubes, clevises, and joint hardware.
- Pass assembly, interference, and section checks three times.
- Generate a flat BOM and repeat BOM-to-CAD checks three times.
- Repeat the complete audit once after any corrections.

`purchase_release=false`

`fabrication_release=false`
