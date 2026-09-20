# Fusion 360 import - NAVIMRO detailed CAD Rev C

## Recommended file

Import `step/NAVIMRO_detailed_neutral_revC.step` into Fusion 360 with **Upload** or **File > Open**. The STEP assembly contains named groups and components. Use `NAVIMRO_detailed_exploded_revC.step` to inspect assembly order, and the `SUB_*.step` files when a smaller editable subassembly is easier to work with.

## Model scope

- 556 positioned mechanical components at the neutral pose.
- 4040 profiles include visible T-slots.
- Profile joint plates, screws, washers, T-nuts, nyloc nuts, guide fasteners, pivot pins, deck spacers and latch fasteners are modeled.
- Aluminium profile, SS400 plate, acrylic, purchased parts and fasteners use separate colors.
- 187 components are yellow/provisional because supplier interfaces remain unverified.
- The package is a mechanical digital mock-up. Electrical panel internal parts are documented in the procurement BOM but are not mounted on the moving mechanical module.

## Fusion 360 notes

1. STEP is used because a native `.f3d` file requires Fusion 360 itself and its API. Fusion 360 imports these STEP files directly.
2. After import, save the document as F3D if a native editable archive is required.
3. Do not combine or rename yellow components until vendor measurements are entered.
4. Replace `LA2000_A2_PROVISIONAL_*`, `ACT*_UH_bracket_PROVISIONAL`, `LMF12UU`, `SK12`, `CR3001`, locator and their yellow fasteners from supplier STEP or delivered-part measurements.
5. The corrected guide riser baseline is `NVR-P06 200x50x6 x2`; the old `120 mm x4` entry was inconsistent and has been superseded.
6. `NAVIMRO_module_only_collapsed_revC.step` excludes the loose cart-side coupling parts and is the correct file for checking the disconnected module height.

## Color key

- Grey: 4040 aluminium profile
- Dark blue: fabricated SS400 plate
- Transparent cyan: acrylic deck
- Black/silver: fasteners
- Yellow: purchased or vendor-dependent provisional interface
- Red: mechanical stop

## Release restriction

Do not release flat-part drilling, actuator brackets, guide transfer holes, latch keepers or locator pins for fabrication until the provisional-interface CSV is closed with measured values.
