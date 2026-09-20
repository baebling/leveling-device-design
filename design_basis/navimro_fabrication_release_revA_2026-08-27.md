# NAVIMRO Fabrication Release Rev A

Date: 2026-08-27

Status: **PROTOTYPE FABRICATION BASELINE - VENDOR TRANSFER HOLES REMAIN OPEN**

## Released scope

- Three radial `LA2000-125150` planning envelopes at 0/120/240 degrees.
- 900 x 800 mm upper work surface, 100 mm Z travel, pitch/roll +/-3 degrees.
- Upper/lower 4040 frames, twin moving 12 mm guide shafts, four fixed LMF12UU bushings and compact laminated Cardan.
- Universal slotted lower mounting tabs and the mechanical cart-coupling interface only.
- Cart-side 760 mm receiver rails, master/secondary locators, rest pads and four CR-3001 draw latches.
- STEP pose set, DXF flat parts, acrylic DXF, profile/shaft/flatbar cut lists, fabrication PDF, assembly/order PDF, budget and verification reports.

The cart body, wheels, drive system, AMR/AGV functions, navigation and mobile operation remain outside scope.

## Rev A geometry

| Parameter | Value |
|---|---:|
| Platform | 900 x 800 x 15 mm |
| Disconnected overall height | 300 mm including 5 mm lower shaft projection |
| Upper/lower actuator radius | 400 / 175 mm |
| Collapsed joint separation | 185 mm |
| Lift | 100 mm |
| Commanded pitch/roll | +/-3 degrees |
| Full corner-sweep actuator length | 273.196 to 385.349 mm |
| Provisional actuator pin envelope | 255 to 405 mm |
| Twin guide shafts | 2 x diameter 12 x 240 mm at X=+/-60 mm |
| Fixed bushing stations | Z=110 and 150 mm |
| Moving SK12 stations | platform Z-70 and Z-25 mm |

## Engineering screen

- Moving mass basis: 10 kg payload + 10 kg cart/interface + 18 kg moving structure.
- Design factor: 2.0.
- Factored vertical load: approximately 745 N.
- With a 100 mm plan eccentricity and the worst actuator direction cosine, the estimated maximum actuator axial load remains below 25% of the advertised 2000 N rating.
- The analytical actuator-to-guide radial gap is 30 mm at the lower joint plane.
- X, Y and yaw are constrained by the two fixed-bushing guide paths. The Cardan passes pitch and roll; both guide shafts pass Z.
- Electrical actuator limits, split-collar Z stops and adjustable Cardan angle stops are independent.

These calculations are a sizing screen, not certification. They do not validate the delivered joint stack, frame section properties, dynamic impact, fatigue or person-carrying use.

## Deliberately open holes

The NAVIMRO pages provide LMF12UU bore/outer diameter/length and SK12 bore, but not every mounting-hole pattern needed for a fabrication release. The actuator page also does not prove the delivered eye width/hole, pin stack or pin-centre minimum/maximum length. Therefore:

- `NVR-P06` SK12 riser holes;
- `NVR-P09` LMF12UU transfer tabs;
- `NVR-P11` CR-3001 latch spreaders;
- `NVR-P12` CR-3001 keepers;
- final actuator U/H/yoke stack holes

must be clamped and transfer-drilled from delivered parts. Their DXFs contain outer profiles and reference centre lines only.

## Budget gate

- Known NAVIMRO 49-line subtotal: 2,799,522 KRW including VAT.
- Freight/fabrication/tool/consumable/contingency reserves: 1,000,000 KRW.
- Planned total: 3,799,522 KRW.
- Headroom below the user cap: 200,478 KRW.

The logged-in 2026-08-27 fan/filter prices are included. Freight and local machining remain allowances until written quotes replace them.

## Mandatory order blockers

1. Written actuator confirmation: supplied M8/eye accessories, both ends, pin-centre Lmin/Lmax, Hall/limit wiring, current/inrush and matching STEP.
2. Written U/H bracket stack confirmation and a sample free-articulation check.
3. CR-3001 rating/keeper confirmation and shaft-collar torque/holding evidence.
4. Driver/PSU/breaker check against confirmed actuator current.
5. Consolidated NAVIMRO quotation plus local fabrication quotation within 4,000,000 KRW.

## Important correction history

- The first NAVIMRO guide model fixed both guide shafts to the lower frame. The shafts had to reach the raised carriage and therefore protruded above the collapsed deck, violating the 250-300 mm height target. Rev A fixes the LMF bushings to the lower tower and moves the 240 mm shafts with the upper carriage; the collapsed physical envelope is now 300 mm.
- The first Cardan placeholder used two intersecting solid rods, which was not a directly fabricable cross. Rev A uses six 50 x 50 x 6 mm flatbar laminates bolted into a 36 mm block with four opposed M8 trunnions.
- Fan and filter were previously zero-price lines. Logged-in product pages verified 5,489 KRW and 660 KRW, and the BOM/test expectations were updated.
- A full regression initially failed because the old test still expected those two unknown prices. The test was corrected after the BOM prices were verified; 123 tests then passed.

## Regeneration

From the project root on Windows:

```powershell
& .\scripts\run_navimro_fabrication.ps1
```

The script regenerates STEP, DXF, CSV, renders, calculations, both PDFs and `outputs/navimro_fabrication/artifact_manifest.json`, then runs all tests.

