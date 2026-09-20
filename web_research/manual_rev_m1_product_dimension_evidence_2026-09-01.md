# Manual Rev M1 product-dimension evidence register

Date checked: 2026-09-01

Status: dimension basis for detailed CAD; purchase and fabrication release
remain false until the repeated CAD/BOM audit is complete.

## Evidence hierarchy

1. Manufacturer dimensioned drawing or catalogue PDF.
2. Manufacturer product page.
3. Distributor product page for availability and price only.
4. Supplier stock list for raw tube nominal size only; received stock must be
   measured before machining.

## Confirmed purchased components

| CAD item | Selected model | Drawing dimensions used in CAD | Evidence | Confidence |
|---|---|---|---|---|
| Upper rod end | THK PHS10, right-hand female thread | bore 10 H7; outer diameter 26; inner-ring width 14; overall length 56; ring centre to thread end 43; M10 x 1.5 female thread; thread depth 21; published minimum permissible tilt 8 deg; static radial capacity 13.2 kN | [THK product page](https://www.thk.com/us/en/products/joints/rod_end/phs/phs/), [manufacturer catalogue PDF](https://tech.thk.com/en/products/pdfs/en_a23_006.pdf), saved as `evidence/2026-09-01/manual_rev_m1/THK_PHS_catalog_en_a23_006.pdf` | High |
| Coarse lock pin | IMAO BJ775-08040-SUS | shank 8 (-0.03/-0.13); maximum ball envelope 9.4; grip length 40 (+0.5/0); end allowance 8; ring A 28; head diameter 11; ring-wire diameter 6.5; overall head heights 34 and 22; mass 42 g; listed minimum double-shear load 65 kN; recommended mating hole 8 (+0.1/0) | [manufacturer catalogue PDF](https://www.imao.co.jp/files/ja/pdf/bj775-sus.pdf), saved as `evidence/2026-09-01/manual_rev_m1/IMAO_BJ775_SUS.pdf` | High |
| Upper linear guide bush | igus JFM-2528-21 | nominal ID 25; OD 28; flange OD 35; body length 21.0; flange thickness 1.5; installed ID 25.040-25.124; housing bore 28.000-28.021; shaft 24.948-25.000 | [igus product page](https://www.igus.com/iglide-ibh/flange-bearings/product-details/iglide-j-m?artnr=JFM-2528-21), [manufacturer catalogue PDF](https://www.igus.com/_product_files/download/pdf/j_1.pdf), saved as `evidence/2026-09-01/manual_rev_m1/IGUS_JFM_catalog.pdf` | High |
| Domestic JFM source | igus JFM-2528-21 | distributor listing repeats ID 25, OD 28, flange 35, length 21 and quotes VAT-included price | [DeviceMart listing](https://www.devicemart.co.kr/goods/view?no=10896543) | Medium for procurement; manufacturer drawing remains dimensional authority |

## Confirmed profile and connector geometry

| CAD item | Dimensions read from supplied/detail-page image | Saved evidence image | Confidence |
|---|---|---|---|
| DNF4040 profile | 40 x 40 section; slot 8.3 +/-0.3; centre bore 6.8 suitable for M8 tapping | `evidence/2026-08-31/NAVIMRO_DNF4040_detail_1024x672.jpg` | High for the displayed option |
| DNF3030 profile | 30 x 30 section; slot 6.3 +0.2/0; centre bore 6; A6N01S-T5 | `evidence/2026-08-31/NAVIMRO_DNF3030_detail_600x713.jpg` | High for the displayed option |
| 4035 inside bracket | 40 x 40 x 35 envelope; thickness 6; two 9 x 18 slots | `evidence/2026-08-31/NAVIMRO_4035_bracket_detail_996x1810.jpg` | High for envelope, slot and thickness |
| DCB3025 inside bracket | 30 x 30 x 25 envelope; two diameter-7 holes; ADC-8 material | `evidence/2026-08-31/NAVIMRO_DCB_bracket_detail_610x383.jpg` | High for envelope and holes |

## Raw tube and custom-part controls

The selected telescoping members are aluminium round tubes `OD32 x 2t` and
`OD25 x 2t`. Korean sellers list both nominal sizes, but no mill tolerance is
assumed from a storefront image. The following inspection and machining notes
are therefore part of the design, not optional workshop advice:

- Measure OD, ID, ovality, straightness, and wall thickness of all three cut
  lengths before machining.
- Finish-ream the upper 21 mm of each OD32 outer tube to `28 H7` for the igus
  bush; do not press the bush into an unmeasured as-extruded bore.
- Reject or polish the OD25 inner tube if its guide surface exceeds the igus
  recommended `24.948-25.000 mm` shaft range.
- Finish-fit the lower POM guide ring to each measured pair and retain it with
  three M3 radial screws. The guide ring is a custom part, not a catalogue
  bearing.

## Custom geometry and unresolved purchase checks

- Lower and upper clevises are custom bolted A6061-T6 parts. No welding is
  required.
- M8 and M10 shoulder-bolt grip lengths in the BOM are derived from the final
  CAD stack, not from nominal thread length.
- Verify checkout availability and pack quantity for every distributor item
  immediately before purchase. Availability evidence can change and does not
  alter the manufacturer dimensions above.
- `purchase_release=false` and `fabrication_release=false` until the final
  repeat audit report explicitly changes those flags.
