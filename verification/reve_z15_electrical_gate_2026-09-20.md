# Rev E Z+15 electrical gate — 2026-09-20

## Result

**HOLD — electrical architecture basis coherent; no ordering or motor-power release.**

| Checked item | Result | Reason |
|---|---|---|
| HMI-less operator path | PASS-BASIS | Laptop USB is the only start path; HMI/IF01 excluded from the new intent. |
| DMC bus separation | PASS-BASIS | Portenta J5 short daisy chain for DMC #1/#2/#3 only. |
| IMU bus separation | PASS-BASIS | Ethernet to isolated tGW-715i-T candidate, then separate Modbus RTU #11/#12. |
| Motor PSU sizing basis | PASS-BASIS | 3 × provisional 7.5 A × 1.25 = 28.125 A; select a 24 V 30 A class only after SKU gate. |
| DMC nominal current comparison | PASS-BASIS | 1.5 A loaded per axis is below stated 8 A continuous capacity; exact peak behaviour is not established. |
| DMC encoder / three-node RS-485 compatibility | REQUIRED / OPEN | Verify DMC 5 V encoder supply/output current, A/B logic/pull-up, 6 ppr count scaling, address 1/2/3 multidrop settings and reverse escape after an internal limit. |
| Independent motor power interruption | REQUIRED / OPEN | E-stop contactor/disconnect rating and selected SKU are not yet evidenced. |
| Regular HOME | PASS-RULE | Must not seek limits; requires saved state, Z=15 datum and no-move evidence. |
| Commissioning/recovery HOME | LIMITED | Block-supported and supervised only; cannot automatically enable LEVEL. |
| Z+15 synchronization | PASS-DOCUMENT | Physical Z=15~65 mm, command Z=0~50 mm, nominal range 221.281~289.523 mm and provisional 218~292 mm are synchronized. |

## Mandatory holds before any order or powered actuator test

1. `HOLD_ACTUATOR_SWITCH_POINTS`
2. `HOLD_ACTUATOR_PEAK_STALL_CURVE`
3. `HOLD_DMC_ENCODER_MULTIDROP_COMPATIBILITY`
4. `HOLD_DMC_STOP_BEHAVIOR`
5. `HOLD_SG01_QUOTE_CARD_STOCK`
6. `HOLD_SMPS_30A_SKU`
7. `HOLD_ESTOP_DC_INTERRUPTION_RATING`
8. `HOLD_BENCH_VERIFY`
9. `HOLD_PHYSICAL_CABLE_GUIDE_VERIFICATION`
10. `HOLD_NO_INDEPENDENT_MECHANICAL_STOPS`

The last hold is a project-rule conflict, so no electrical document may turn `PURCHASE_RELEASE`, `FABRICATION_RELEASE`, `CONTROL_POWER_TEST_RELEASE`, or `MOTOR_POWER_RELEASE` true.
