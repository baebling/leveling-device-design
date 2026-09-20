# Procurement Sources

Access date: 2026-08-24

## Price Notes

| Source ID | Item | Price observed | Use |
|---|---|---:|---|
| SRC-ACT-001 | Firgelli F-SD-H-450 series | Existing project BOM used USD 159.95/actuator; official page confirms family/specs | Baseline actuator cost placeholder |
| SRC-LAT-001 | DESTACO 323-R | Existing project BOM used quote state; official page confirms 360 lbf capacity | Quote required |
| SRC-FRM-004 | MISUMI Korea economy 4040 frame | From 1205 KRW listed for economy 4040 class | Budget screen only |
| SRC-SEN-001 | Adafruit BNO085 breakout | USD 29.50 | Sensor budget |
| SRC-DRV-001 | Cytron MD13S | RM61.20 / USD 15.30 class from official Cytron pages | Driver budget |
| SRC-DRV-002 | Cytron MD20A | RM97.44 | Driver fallback budget |
| SRC-PWR-001 | Mean Well LRS-350-24 | USD 46.50 | Low-cost power budget |
| SRC-SAF-001 | Omron A22E | Quote required | Safety budget |

## Procurement Rule

- Final price must be recorded with date, source, currency, quantity, shipping/tax status, and whether the seller is manufacturer/authorized distributor/open-market.
- Open-market prices can screen budget only; they cannot justify load rating or safety behavior.
- Korean domestic procurement should be preferred when two candidates are technically equivalent.

## Budget Risk

The 4,000,000 KRW limit is realistic for a conservative PoC only if:

- actuator choice stays in a low/mid-cost class;
- high-end industrial actuators are not required;
- frame is profile + simple plates rather than complex machined weldment;
- external covers and finish are minimized;
- retained mechanical stops and bench electrical protection are not reduced below the active static-bench boundary.

## NAVIMRO Check - 2026-08-27

The NAVIMRO internal search was checked for the first-build procurement items.

| Item | NAVIMRO result | Decision |
|---|---|---|
| Firgelli `F-SD-H-450-12V-8in` | No exact listing; the result page returned unrelated token matches | Not orderable as a listed product; ask NAVIMRO for a special-order quote or buy from Firgelli/another importer |
| Firgelli `MB21` | No exact Firgelli/MB21 product link in the internal search | Same as actuator; do not substitute a visually similar bracket |
| BOTECO `Y708028.VBD12` two-piece collar | Listed as 12 mm bore, 28 mm OD, 11 mm width, black-oxide steel, product code `K94509288`, VAT-included 28,589 KRW, expected 2026-09-04 dispatch, non-returnable | Geometry matches the LS-01M collar envelope; buy only for the one-cassette mock-up and perform push-off testing |
| IMAO `SW12-02` shoulder bolt | M8x1.25 option listed as `K25214077`, VAT-included 10,769 KRW, expected 2026-09-04 dispatch, non-returnable | Do not order until the purchased actuator eye and cradle stack are measured |

NAVIMRO prices and dispatch dates are observations from 2026-08-27 and may change. The exact actuator is still the first procurement blocker.

## NAVIMRO-Centered Redesign Candidate - 2026-08-27

Further internal search found a compact DIHOOL family that is a better packaging match than the initially screened DHLA35.

| Item | NAVIMRO code | Observed price | Candidate use |
|---|---|---:|---|
| DIHOOL `LA2000-125150`, 12 V / 2000 N / 150 mm / 5 mm/s | `K92931811` | 115,489 KRW VAT included | Preferred procurement-driven actuator redesign candidate; 3 required |
| DIHOOL U bracket `IPS-B1-6MM-U` | `K92931726` | 10,439 KRW VAT included | Purchased 6 mm bracket candidate |
| DIHOOL H bracket `IPS-B1-6MM-H` | `K92931725` | 10,439 KRW VAT included | Alternative purchased 6 mm bracket candidate |
| Cytron `MD10C` | `K27740830` | 25,289 KRW VAT included | One independent driver per actuator; dispatch shown as unavailable/blank at check time |
| Arduino Mega 2560 | `K62252128` | 80,289 KRW VAT included | PoC supervisory controller; dispatch shown as unavailable/blank at check time |
| Adafruit BNO055 | `K27732921` | 115,489 KRW VAT included | Available PoC tilt sensor, but not preferred for a new long-life design |

The actuator and brackets were shown as made-to-order and non-returnable. The provisional 150 mm actuator pin-centre range is 255 to 405 mm from the family drawing formula. Exact dimensions, Hall option, wiring and STEP must be confirmed by NAVIMRO before order. See `design_basis/navimro_dhla2000_redesign_feasibility_2026-08-27.md`.

## NAVIMRO Single-Order Completeness Pass - 2026-08-27

The procurement scope was expanded from the actuator mock-up to all purchased materials and accessories for the stationary PoC. The resulting source-backed package is `procurement/navimro_single_order_bom.csv` with 49 order lines.

Key replacements and additions:

- Daeyoung `DF 4040-8` cut profiles and `DAB4040` angle stock replace the foreign profile quote.
- A 50 x 6 x 6000 mm NAVIMRO steel flat bar supplies locally fabricated yokes, Cardan plates, spreaders and cart locators.
- The central guide changes to two 12 mm ground shafts, four `LMF12UU` bushes and four `SK12` supports.
- Motorbank `DMD-150` replaces the Cytron listing whose dispatch date was blank.
- `NES-350-12`, three DC-rated Siemens branch breakers, an LS AC breaker, enclosure, wire, terminals, grounding, DIN rail, fan and filter complete the bench electrical package.
- The known-price subtotal is 2,764,784 KRW including VAT. The 80 mm fan/filter login prices, freight and local machining remain outside that subtotal.

The exact product links, quantities, prices, dispatch observations and release conditions are kept in the CSV rather than duplicated here. The one-time order remains blocked until the actuator/bracket drawings, Hall/wiring/current information, collar/latch data and wire-set length are confirmed in writing.

## DMD-150 Manufacturer Manual Review - 2026-08-28

The Motorbank official manual and Arduino example close the DMD-150 control-interface uncertainty. The driver accepts 3.3/5 V TTL-level IN1/IN2/PWM control, uses both direction inputs low for braking and both high for floating/coast, and calls for approximately 0.1 s of braking before a full-duty direction reversal. The manual rates 12 V output at 180 W, with 12 A continuous current without added cooling and 15 A with simple cooling.

The same manual warns that lowering or braking can regenerate onto the DC bus and trip an SMPS overvoltage function. A motor-terminal bidirectional TVS and a loaded-lowering bus-voltage test are now release conditions. The cited `1.5KE24CA` is only a manufacturer example; no exact NAVIMRO product code has yet been verified.
