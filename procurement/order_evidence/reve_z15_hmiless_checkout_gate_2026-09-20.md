# Rev E Z+15 HMI-less checkout gate — 2026-09-20

## Verdict

**HOLD — this BOM is a preliminary purchase-planning list, not an order release.**

The known displayed-price subtotal is **3,350,915 KRW**. It excludes the 109,333 KRW PC01 import/freight planning allowance (AL01) and the non-priced placeholder lines E04, E09C and SG01. It is not a supplier quotation, checkout total or landed-cost estimate.

## Architecture reflected in this revision

- HMI-less operation: laptop USB is the start path.
- DMC #1/#2/#3 remain on the short direct Portenta RS-485 daisy chain.
- HWT905 #11/#12 remain on a separate RS-485 bus behind the candidate isolated Ethernet-RS485 gateway.
- HM01, SH01, LG01 and IF01 are removed from active order rows.
- CB02 is retained as the fixed Portenta-to-SG01 Ethernet cable.
- E04 is a zero-price 24 V, continuous 30 A or greater motor-PSU specification placeholder. The selection basis is 3 × 7.5 A provisional peak × 1.25 = 28.125 A.
- SG01 is a zero-price `ICP DAS tGW-715i-T` technical candidate, not a confirmed domestic purchase item.

## Checkout blockers

| Hold | What must be evidenced before checkout or powered testing |
|---|---|
| `HOLD_ACTUATOR_SWITCH_POINTS` | Measured internal end-switch trip points, not nominal CAD stroke only. |
| `HOLD_ACTUATOR_PEAK_STALL_CURVE` | LM4075OE-1075 peak/stall-current evidence for 24 V operation. |
| `HOLD_DMC_ENCODER_MULTIDROP_COMPATIBILITY` | DMC 5 V encoder output/current, A/B logic, 6 ppr scale, address 1/2/3 and RS-485 response evidence. |
| `HOLD_DMC_STOP_BEHAVIOR` | Loss-of-command/timeout and all-axis STOP behavior. |
| `HOLD_SG01_QUOTE_CARD_STOCK` | Domestic price, stock, delivery and card-checkout evidence for the isolated gateway. |
| `HOLD_SMPS_30A_SKU` | Domestic 24 V 30 A-class PSU SKU and short-circuit, inrush, grounding and thermal evidence. |
| `HOLD_CONTROL_FUSE_RATING` | Actual Portenta, HWT905 and SG01 branch current and compatible holder/wire/fuse rating. |
| `HOLD_ESTOP_DC_INTERRUPTION_RATING` | Selected E-stop DC interruption path/rating evidence. |
| `HOLD_BENCH_VERIFY` | Supervised bench wiring and one-axis-to-three-axis staged test record. |
| `HOLD_PHYSICAL_CABLE_GUIDE_VERIFICATION` | Cable routing/strain relief and physical guide clearance at the Z+15 range. |
| `HOLD_NO_INDEPENDENT_MECHANICAL_STOPS` | Project-rule conflict remains unresolved because the agreed PoC omits independent mechanical stops. |

`PURCHASE_RELEASE`, `FABRICATION_RELEASE`, `CONTROL_POWER_TEST_RELEASE` and `MOTOR_POWER_RELEASE` remain false. Regular HOME must validate saved state and the physical Z=15 mm datum without seeking an actuator end limit. Only supervised, block-supported commissioning/recovery may approach a limit, and it cannot enable LEVEL automatically.

## Commercial constraints

- No spare actuator is included. M01 remains exactly three working units.
- PC01 is retained with its existing displayed price and AL01 planning allowance. Its landed cost is still open.
- Zero-price placeholders are not quotes and must not be typed into a cart as 0 KRW parts.
- Unaffected suppliers and displayed prices have not been silently substituted.

## Evidence reviewed

- `verification/reve_z15_electrical_gate_2026-09-20.md`
- `verification/reve_z15_workspace_audit_2026-09-20.md`
- `procurement/reve_portenta_order_bom_2026-09-18.csv`
- `procurement/reve_portenta_order_bom_2026-09-18.xlsx`
