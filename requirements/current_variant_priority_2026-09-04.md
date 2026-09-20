# Current variant priority - 2026-09-04

> **SUPERSEDED:** 2026-09-07 사용자가 수동 `M2R2-S220`을 우선순위 1로 확정했다. 현행 기준은 `current_variant_priority_2026-09-07.md`이며, 이 문서는 전동 Rev E 이력으로만 보존한다.

## Priority 1

`POWERED_PROFILE_RADIAL_3RPS_REVE_POC_RC1`

- LM4075OE-1075 DC24V/100 mm/10 mm/s/750 N/5 V 6ppr encoder x3
- Cytron MDD10A x2, three of four channels used
- Mega2560 compatible controller x1
- GY-521/MPU6050 x1
- Mean Well LRS-350-24 x1 and 24 V-to-5 V converter x1
- Z 0/25/50 mm, pitch/roll -3/0/+3 degrees
- 10 kg payload acceptance at +/-0.5 degrees for 10 seconds
- stationary indoor supervised PoC only

Current status:

```text
DIGITAL_PACKAGE = PASS
FIRMWARE_COMPILE = PASS_ARDUINO_AVR_MEGA
PURCHASE_RELEASE = FALSE
FABRICATION_RELEASE = FALSE
POWER_RELEASE = FALSE
POC_ACCEPTANCE = FALSE
```

The open gates are the LMB-10 drawing/first article, exact actuator current and wiring data, physical enclosure mounting verification, machining quotations, one-axis commissioning, and the final 10 kg test matrix.

## Priority 2

`MANUAL_TURNBUCKLE_3RPS_REV_M2_BACKUP`

This option remains preserved but is not the active procurement basis unless Priority 1 fails its supplier or powered-commissioning gates.
