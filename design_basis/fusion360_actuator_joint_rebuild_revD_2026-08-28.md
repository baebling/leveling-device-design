# Fusion 360 actuator joint rebuild Rev D - 2026-08-28

## Decision

Keep the approved three-actuator radial mechanism, but replace the invalid Rev C U/H compound with one spherical rod end at each actuator end. The active joint is NAVIMRO `K02020097 / JMC JFT-8R`, quantity six. The DIHOOL U and H bracket rows remain in the BOM at quantity zero as audit history.

This is a preliminary stationary-PoC digital mock-up and is not approved for fabrication. The A2 actuator is still a conservative envelope because its exact delivered end interfaces and matching STEP have not been received.

## How one actuator is assembled

1. Bolt the lower `NVR-P04` spreader to the 640 mm lower actuator crossmember with two underside M8 screw/washer/T-nut sets.
2. Cut two `NVR-P16` lugs from 50x6 SS400 flat bar. Drill each Ø8.2 hole 15 mm from the free end.
3. Align both lugs around a 20 mm internal gap with an Ø8 jig pin, then weld them to the underside of P04. The pin, not the plate edge, controls coaxiality.
4. Fully engage the JFT-8R M8 female thread on the confirmed A2 end adapter and lock it with a jam nut. Do not use a long exposed threaded standoff.
5. Put one fitted spacer on each side of the 12 mm rod-end ball. Insert the M8 shoulder/part-thread pivot through lug, spacer, rod end, spacer and opposite lug, then positively retain it.
6. Repeat the same construction on the upper `NVR-P03` spreader. P03 bolts under the upper 660 mm member and its P16 lugs point downward.
7. Repeat the cassette at the other two 120-degree locations. The complete model contains six rod ends, twelve P16 lugs and six pivot stacks.

## Active dimensions

| Item | Rev D value |
|---|---:|
| Lower joint radius | 195 mm |
| Upper joint radius | 400 mm |
| Lower pin Z | -10 mm |
| Upper pin offset below platform datum | -38 mm |
| Yoke internal gap | 20 mm |
| P16 lug | 50x6x27 mm, Ø8.2 |
| Pivot | nominal M8, 36 mm modeled stack |
| Lower actuator crossmember | 640 mm |
| Upper end/crossmember | 660 mm |
| Disconnected collapsed module height | 300 mm |

## Verification

- Full lift sweep: 0 to 100 mm in 5 mm increments.
- Pitch and roll sweep: -3, 0 and +3 degrees at every lift point.
- Pin-centre length range: 269.040 to 394.209 mm inside the provisional 265 to 415 mm window.
- Worst joint-axis deviation: 9.852 degrees; required with one-degree margin: 10.852 degrees, below the JFT-8R catalog value of 13 degrees.
- Preliminary maximum actuator axial force: 876.4 N with project load factor.
- M8 pin double shear: 8.72 MPa; local pin bending screen: 87.17 MPa.
- 6 mm lug bearing: 18.26 MPa; lug root bending screen: 57.06 MPa.
- JFT-8R catalog breaking-load margin against twice the screened axial load: 4.25.
- Direct CAD intersection checks: no actuator-envelope/frame collision in collapsed, neutral, raised, max-pitch, max-roll or combined max-pitch-roll poses; no pivot overlap with modeled rod-end/lug/spacer bores.

## New DHLA6000 A2 supplier-page evidence

The official DIHOOL `DHLA6000-A2 24V` page was reviewed on 2026-08-28 after the user supplied the link. It describes A2 as a flat-base-plate plus M8-threaded installation and states that the central aluminum-tube mounting head is removable and replaceable. This supports keeping an explicit, replaceable M8 adapter component between the actuator envelope and JFT-8R rather than merging the joint into the actuator body.

The same page identifies a 72 W DHLA6000 family, displays 2.25 A on the 24 V page, and lists optional Hall sensors, built-in limits, IP43 and a 10% duty cycle. It also advertises a `DHLA6000-A2.STEP` file, but the direct file request returned HTTP 403 during this review.

These facts do not close the Rev D release gate. The active NAVIMRO BOM row is `K92931811 / LA2000-125150`, previously treated as a DHLA2000 12 V item. The DHLA6000 page does not establish the delivered K92931811 model, M8 thread gender, engagement length, supplied plates/accessories, pin-centre range or electrical current. Rev D geometry therefore remains unchanged and `A2_M8_INTERFACE_PROVISIONAL` remains provisional. Switching the purchase to DHLA6000 would require a new envelope, mass, interference, driver, supply and budget check.

The user confirmed on 2026-08-28 that NAVIMRO supplies the selected item as DC 12 V, 2000 N, 150 mm stroke and 5 mm/s. These four procurement specifications are now fixed for Rev D and the 12 V bus is selected. This confirmation does not identify the A1/A2 installation subtype or close the M8-interface, pin-centre, Hall, wiring, current or matching-STEP gates.

The official `DHLA6000-A2 12V` and `DHLA6000-A2 24V` pages use the same A2 outline image, installation description, interactive-model filename and STEP filename. Their page-level current values differ as expected, 4.5 A at 12 V and 2.25 A at 24 V. This is strong evidence that the two voltage variants share the mechanical DHLA6000-A2 hardware, although the manufacturer does not explicitly state interchangeability. It still does not prove that the selected `LA2000-125150` shares DHLA6000 geometry. The selected 2000 N / 5 mm/s combination also differs from the DHLA6000 table, which pairs 2000 N with 15 mm/s, so cross-family geometry remains prohibited without the actual K92931811 drawing or STEP.

## Remaining release gates

- Have the quotation and nameplate repeat DC 12 V, 2000 N, 150 mm stroke and 5 mm/s, and identify the exact manufacturer subtype and A1/A2 installation variant.
- Confirm whether each delivered A2 end is male or female M8x1.25 and provide the exact engagement length.
- Confirm supplier pin-centre minimum/maximum length, stroke, Hall option, wiring, rated/starting/stall current and matching STEP.
- Measure one received JFT-8R before freezing spacer thickness and shoulder-bolt grip length.
- Freeze P03/P04/P16 welding dimensions only after a one-cassette jig trial confirms free articulation without binding.
- Keep CR-3001 keeper/rating, shaft-collar holding data and remaining yellow transfer holes on hold.

## Fusion inspection files

- `outputs/navimro_fusion360_revD/step/ACT1_complete_mounting_cassette_neutral_revD.step`
- `outputs/navimro_fusion360_revD/step/NAVIMRO_detailed_neutral_revD.step`
- `outputs/navimro_fusion360_revD/step/NAVIMRO_module_only_collapsed_revD.step`
- `outputs/navimro_fusion360_revD/renders/actuator_joint_closeup.png`

Use the actuator-1 cassette first. It intentionally omits unrelated frame parts so the two P16 lugs, spacers, M8 pin, JFT-8R, A2 envelope and both supporting profile members can be inspected as one assembly.
