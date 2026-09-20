# NAVIMRO Single-Order BOM

Date checked: 2026-08-28

Status: **PRE-ORDER PACKAGE - DO NOT PLACE THE ORDER UNTIL THE HOLD ITEMS BELOW ARE CLOSED**

## Decision

The project can be reworked into a NAVIMRO-only procurement package while preserving the approved three-actuator radial layout. The purchasing baseline uses:

- three DIHOOL `LA2000-125150` actuators planned without flat panels and with provisional M8 interfaces at both ends;
- six JMC `JFT-8R` spherical rod ends, one at each actuator end, in locally fabricated double-shear yokes;
- a 4040 aluminum-profile upper/lower frame and cart-side receiver rails;
- a 15 mm acrylic non-primary deck supported by the frame and steel spreaders;
- a twin 12 mm moving-shaft central guide with four fixed flange bushings, two side-mounted SK12 supports, a compact laminated Cardan and independent welded stops;
- mechanical cart locators made from steel flat bar, with four latches used only to draw the module onto the locators;
- three independent DMD-150 motor controllers, a Mega2560-compatible controller, BNO055 PoC IMU and a 12 V / 29 A bench power system;
- enclosure, branch breakers, wire, terminals, glands, ferrules, cooling and mounting accessories from NAVIMRO.

The machine remains a supervised, stationary, low-speed test rig. It is not approved for carrying people, mobile operation or unattended operation.

## Cost Snapshot

The CSV contains 50 audit rows and 46 active order lines. The known-price subtotal is **2,687,993 KRW including VAT**. It includes six JFT-8R rod ends, the logged-in fan/filter prices and two 6 m steel flat bars. It excludes:

- profile/steel freight-collect charges and any long-item surcharge;
- local cutting, drilling, tapping, deburring and acrylic machining;
- exact M4 LMF/SK fastener packs, sixteen deck compression sleeves and the motor-terminal TVS because those NAVIMRO SKUs are not yet released;
- any price change after 2026-08-27.

The 15 mm acrylic listing is a two-sheet pack. One sheet is used and one remains as a spare. This is intentionally retained because the user requires a single purchase and the exact listed pack avoids a later material order.

Machine-readable rows and direct product links are in `procurement/navimro_single_order_bom.csv`. The subtotal can be reproduced with:

```powershell
& 'C:\Users\gangm\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\calculations\navimro_single_order_cost.py
```

## Frame Cut Set

| Length | Quantity | Use |
|---:|---:|---|
| 840 mm | 2 | Upper long rails |
| 820 mm | 2 | Lower long rails |
| 760 mm | 2 | Cart-side receiver rails |
| 660 mm | 4 | Upper end and cross rails |
| 640 mm | 5 | Lower end and cross rails, including actuator support |
| 420 mm | 2 | Upper radial supports |
| 240 mm | 1 | Moving guide carriage |

Total: 18 pieces and 11,760 mm of `DF 4040-8`. Three 500 mm `DAB4040` angle bars provide approximately thirty-six 40 mm joint angles after saw kerf.

## Purchase Status Meaning

| Status | Meaning |
|---|---|
| `READY` | Listing, option, quantity and role are defined. Recheck price/stock at quote time. |
| `READY_AFTER_DRAWING_CONFIRM` | Quantity is defined, but holes/cuts must follow the revised NAVIMRO CAD. |
| `PROVISIONAL` | Useful full-thread mock-up hardware; final pivot grip length may change. |
| `READY_FOR_POC` | Acceptable for this one-off stationary PoC, but not a long-life production selection. |
| `HOLD_*` | Do not release the entire one-time order until the stated vendor reply is received. |
| `LOGIN_PRICE` | Exact product is selected, but the public page hides its price. |

## Mandatory Hold Items

1. `K92931811`: the planning assumption is no supplied flat panels and an included M8-to-eye/pin accessory. Confirm the accessory contents, both-end interfaces, pivot-centre Lmin/Lmax, Hall option, wiring, rated/peak current and matching STEP in writing.
2. `K02020097 / JFT-8R`: purchase six only after confirming the delivered A2 interface is M8x1.25-compatible at both ends. The U/H bracket rows are retained at quantity zero for audit only.
3. `K06182829 / LMF12UU` and `K19818870 / SK12`: confirm delivered hole/counterbore geometry, then select the exact M4 screws, washers, nuts/T-nuts and sixteen ID8.6/OD18/L15 deck sleeves in the same NAVIMRO order.
4. `K61836622`: latch holding rating and keeper inclusion are not published. The locators and stops carry X/Y/yaw shear; the latch only supplies seating preload.
5. `K63669714`, `K47937908` and `K63064199`: the official DMD-150 interface is now confirmed, including 12 A continuous without added cooling, 15 A with cooling and 180 W at 12 V. Close actuator rated/start/stall current, thermal margin and three-axis concurrency before confirming the PSU and 10 A branch breakers.
6. Motor regeneration protection: the DMD-150 manual warns that lowering/braking can return energy to the DC bus and trip an SMPS. Select a NAVIMRO-orderable bidirectional TVS or approved equivalent, verify pulse-energy suitability and complete a loaded-lowering DC-bus overshoot test. The manual's `1.5KE24CA` is an example, not a released BOM line.
7. `K92854706`: confirm the number of reels, length per reel, conductor voltage rating and whether the set supplies enough red/black cable for all three actuator branches.
8. Recheck the 2026-08-27 logged-in prices for `K77669622` (5,489 KRW VAT included) and `K77677462` (660 KRW VAT included) in the consolidated quote.

## Fabricated Parts From Purchased Stock

These are not missing purchased items. They are cut/drilled locally from `K52633446` steel flat bar and the profile angle stock:

- six double-shear actuator yokes made from `NVR-P03/P04` bases and twelve `NVR-P16` bored lugs, plus twelve fitted spacers;
- the compact central pitch/roll Cardan with a four-layer 50x50x24 mm cross block, vertically separated M8 axes and adjustable stops set beyond the +/-3 degree command range;
- two 200 mm offset guide risers, four 50x76 LMF transfer tabs, four riser feet and eight pieces forming the fixed/moving Z-stop pairs;
- four cart latch keepers, one master locator, one Y-only secondary locator and four rest pads;
- actuator and center-guide load spreaders;
- control-box support tabs if needed.

The listed full-thread M8 bolts are acceptable only for fit-up. Select a shoulder or partially threaded M8 pivot with an unthreaded bearing span after measuring the delivered JFT-8R ball width; use a positive-retention nut at all six joints.

## What This Package Does Not Include

- the cart body, wheels, drive system, navigation or AMR/AGV hardware;
- a battery, BMS, charger, battery disconnect/fuse or battery enclosure because the active prototype is an AC-powered stationary bench;
- finished control firmware, a final point-to-point wiring schematic or a fabricated wire harness;
- a safety-rated emergency-stop/contactor circuit; the listed two-pole breaker is only the supervised bench disconnect;
- workshop tools, drill bits, taps, saw blades, crimpers or measuring tools;
- outsourced machining labor;
- certification, guarding for public use, or a safety-rated control system.

Those exclusions follow the project scope. A ferrule crimper and insulated-terminal crimper must already be available; otherwise they should be added to the same NAVIMRO quote as tools, not design components.

The exact included/open electrical boundary is recorded in `procurement/electrical_control_completeness_2026-08-28.md`.
