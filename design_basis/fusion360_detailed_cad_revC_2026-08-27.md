# Fusion 360 Detailed CAD Rev C

Date: 2026-08-27

## Purpose

Rev C is the bolt-level mechanical digital mock-up requested after the Rev A fabrication model proved too abstract to identify every profile, steel plate and connection. It is intended for Fusion 360 import, assembly review, vendor-part replacement and final transfer-hole closure.

It is not a fabrication release while yellow/provisional components remain open.

## Main outputs

- `output/NAVIMRO_Fusion360_detailed_CAD_revC.zip`
- `outputs/navimro_fusion360_revC/step/NAVIMRO_detailed_neutral_revC.step`
- `outputs/navimro_fusion360_revC/step/NAVIMRO_detailed_collapsed_revC.step`
- `outputs/navimro_fusion360_revC/step/NAVIMRO_detailed_raised_revC.step`
- `outputs/navimro_fusion360_revC/step/NAVIMRO_detailed_exploded_revC.step`
- `outputs/navimro_fusion360_revC/step/NAVIMRO_module_only_collapsed_revC.step`
- Eight `SUB_*.step` subassemblies.
- Detailed component manifest, aggregated BOM, fastener schedule, procurement gaps and provisional-interface CSV files.

STEP is used because creating a native F3D archive requires Fusion 360 and its API. Fusion 360 directly imports the supplied STEP assembly; save the imported document as F3D when a native archive is required.

## Model content

- 556 named and positioned components at the neutral pose.
- 13 STEP files and four verification renders.
- 4040 profile bodies include visible four-side T-slots and centre bores.
- Separate profile joint plates, screws, washers, T-nuts, nyloc nuts, pivot bolts, deck compression spacers, bearing screws and latch screws.
- Aluminium profile, SS400 plate, clear acrylic, purchased hardware, fasteners, provisional parts and hard stops use separate colors.
- 187 components are provisional because at least one delivered-part dimension remains open.

## Material boundary

| Construction | Parts |
| --- | --- |
| 4040 aluminium profile | Upper and lower perimeter rails, crossmembers, centre spreaders, moving carriage, loose cart-side receiver rails |
| SS400 plate/flat bar | Mount tabs, actuator spreaders, guide risers, LMF tabs, Cardan lugs/bridges/cross, locator plates, latch spreaders/keepers, stops |
| SUJ2 ground shaft | Two 12 x 240 mm moving guide shafts |
| Clear PMMA | One 900 x 800 x 15 mm non-primary deck |
| Commercial hardware | Actuators, U/H brackets, LMF12UU, SK12, split collars, CR-3001 and fasteners |

## Fastener schedule represented in CAD

| Family | Modeled quantity |
| --- | ---: |
| M8 socket screw | 106 |
| M8 flat washer | 122 |
| M8 T-slot nut | 104 |
| M8 nyloc nut | 10 |
| M8 pivot bolt | 8 |
| M6 screw/washer/T-nut | 16 each |
| M5 screw/washer/nyloc | 8 each |
| Acrylic compression spacer | 16 |

The aggregated BOM marks a fastener family provisional if any use of that family depends on a supplier interface. The fastener schedule separates quantities by assembly group and status.

## Corrections made while detailing

1. The old cut list said `NVR-P06 120 mm x4` while the CAD and assembly manual required two 200 mm guide risers. Rev C corrects this to `200 x 50 x 6 mm x2` and adds four base angles plus eight positioned M8 sets.
2. The provisional actuator pin envelope is now the A2 reference range 265 to 415 mm. The calculated motion range remains 273.196 to 385.349 mm.
3. The redundant custom actuator yoke parts `P02/P05` were removed from the active flat-bar cut list because Rev C uses the purchased U/H bracket stack as the provisional interface.
4. Cardan lugs, bridges and LMF tabs were reconciled to the modeled quantities: `P07 x4`, `P08 x2`, `P09 x4`.
5. Cardan bridges and eight frame-attachment fastener sets were added.
6. The six actuator-end bracket bodies, twelve bracket-base fastener sets, two locator plates and four latch spreaders/keepers were added.
7. A module-only collapsed STEP was added because the cart-side receiver parts are loose interface pieces and must not be included in disconnected-height evaluation.

## Verified output

- Re-imported neutral STEP: valid, 722 solids, 900 x 800 x 390 mm full coupled envelope.
- Re-imported module-only collapsed STEP: valid, 664 solids, 900 x 800 x 292 mm envelope.
- ZIP integrity check: 26 files, no CRC error.
- SHA-256 manifest: 23 packaged artifacts.
- Full regression: 132 tests passed.

## Open vendor interfaces

Yellow components are not dimensionally released:

- LA2000-125150 body and both pivot centres;
- supplied M8/eye accessory and U/H bracket width/stack/pins;
- LMF12UU and SK12 mounting patterns;
- split-collar holding data;
- CR-3001 body, keeper, mounting holes and rating;
- master/secondary locator geometry;
- related M5/M6/M8 grip lengths and through-hole/thread choice.

Use `NAVIMRO_revC_provisional_interfaces.csv` and `NAVIMRO_revC_procurement_gaps.csv` to close these items. Do not drill their final holes or release the yellow parts for fabrication before measured dimensions are recorded.

## Reproduction

```powershell
& .\scripts\run_fusion360_detailed.ps1
```
