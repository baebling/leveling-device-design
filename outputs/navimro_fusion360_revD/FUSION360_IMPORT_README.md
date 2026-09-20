# Fusion 360 import - NAVIMRO detailed CAD Rev D

## Recommended file

Import `step/NAVIMRO_detailed_neutral_revD.step` into Fusion 360 with **Upload** or **File > Open**. The STEP assembly contains named groups and components. Use `ACT1_complete_mounting_cassette_neutral_revD.step` for the clearest actuator mounting inspection, `NAVIMRO_detailed_exploded_revD.step` for assembly order, and the `SUB_*.step` files for smaller editable subassemblies.

## Model scope

- 559 positioned mechanical components at the neutral pose.
- 4040 profiles include visible T-slots.
- Profile joint plates, screws, washers, T-nuts, nyloc nuts, guide fasteners, pivot pins, deck spacers and latch fasteners are modeled.
- Aluminium profile, SS400 plate, acrylic, purchased parts and fasteners use separate colors.
- Six catalog-modeled JMC JFT-8R rod ends replace the invalid rigid U/H stacks from Rev C.
- Each actuator end now contains a separate spherical rod end, two bored steel lugs, two spacers, one bored M8 pin stack and an explicit M8/A2 adapter.
- 157 components remain yellow/provisional because the delivered A2 actuator interfaces and several other supplier interfaces remain unverified.
- The package is a mechanical digital mock-up. Electrical panel internal parts are documented in the procurement BOM but are not mounted on the moving mechanical module.

## Fusion 360 notes

1. STEP is used because a native `.f3d` file requires Fusion 360 itself and its API. Fusion 360 imports these STEP files directly.
2. After import, save the document as F3D if a native editable archive is required.
3. Do not combine or rename yellow components until vendor measurements are entered.
4. Replace `LA2000_A2_PROVISIONAL_*` and `ACT*_M8_A2_ADAPTER_PROVISIONAL` from the delivered actuator or supplier STEP. JFT-8R geometry is catalog-modeled but still requires receipt inspection.
5. The corrected guide riser baseline is `NVR-P06 200x50x6 x2`; the old `120 mm x4` entry was inconsistent and has been superseded.
6. `NAVIMRO_module_only_collapsed_revD.step` excludes the loose cart-side coupling parts and is the correct file for checking the 300 mm disconnected module height.
7. Full detailed states include collapsed, neutral, raised, max pitch, max roll and max pitch+roll.

## Color key

- Grey: 4040 aluminium profile
- Dark blue: fabricated SS400 plate
- Transparent cyan: acrylic deck
- Black/silver: fasteners
- Yellow: purchased or vendor-dependent provisional interface
- Red: mechanical stop

## Release restriction

Do not release the A2 adapter/thread detail, spacer thickness, pivot hardware, guide transfer holes, latch keepers or locator pins for fabrication until the provisional-interface CSV is closed with measured values. The six P03/P04/P16 yokes require local cutting, drilling, jig alignment and welding.
