# Rev E Z+15 electrical selection basis — 2026-09-20

## Decision

The least-complex electrical architecture for the approved self-weight PoC is a laptop-commanded Portenta Machine Control with two separate communication branches: its J5 RS-485 daisy chain exclusively for three DMC-200 units, and Ethernet through one isolated gateway exclusively for two HWT905 Modbus RTU sensors. It eliminates the HMI and `IF01`; it does not eliminate the independently interrupted motor 24 V branch.

```text
Laptop USB -> PC01 Portenta
                   |- J5 RS-485 -> DMC-200 #1 -> #2 -> #3
                   `- Ethernet -> SG01 tGW-715i-T (TCP 502) -> HWT905 #11/#12
E-stop NC -> rated 24 VDC contactor/disconnect -> DMC motor 24 V feed
```

The Portenta is the Modbus TCP client/master. `SG01` has a static IP and is a TCP server/slave on TCP 502, then the RS-485 Modbus RTU master. Each HWT905 is configured alone, settings saved, power-cycled and read back before the two-device bus is formed. DMC address 1/2/3 and IMU decimal ID 11/12 are fixed in the commissioning record.

## Current basis, not an approval

The supplied LM4075OE-1075 table states 24 V no-load 0.4 A and loaded 1.5 A per axis. No measured or supplier-confirmed stall curve is available. Therefore 7.5 A/axis is only a provisional sizing assumption:

```text
3 x 7.5 A = 22.5 A provisional simultaneous peak
22.5 A x 1.25 = 28.125 A selection requirement
=> 24 V, 30 A class motor PSU basis
```

DMC-200's stated 8 A continuous capacity is compatible with the 1.5 A nominal loaded datum per axis, but it does not confirm peak-duration behaviour, fuse coordination, cable gauge, contactor rating, bus regeneration or actuator compatibility. The gateway contribution is small (tGW-715i-T nominal 0.07 A at 24 V) but control-current allocation is not released until Portenta, IMU, encoder, relay/contactor coil and protection data are summed from final part data sheets.

## Motion and response expectations

The Portenta must impose a bounded JOG envelope and a command-session timeout. Session loss, invalid command acknowledgement, stale sensor data, wrong address, malformed response, or network disconnect causes all-axis control STOP request, a latched fault, CSV event record and a fresh laptop `START` requirement after reconnection. This is a control rule only. Because retained DMC command and watchdog response after a Portenta hang/motion-bus loss are unknown, motor power remains independently interruptible with E-stop.

Normal HOME does not contact an internal actuator limit. It uses only valid saved position, physical `Z=15` datum offset and no-manual-move evidence. `COMMISSIONING_HOME` or recovery is block-supported and supervised; it may search limits but must not automatically enable LEVEL afterwards. The command range is physical Z=15~65 mm, with a provisional 218~292 mm absolute pin-length software window. This has no mechanical-stop function.

## Gate list

| Gate | Closure evidence required |
|---|---|
| `HOLD_ACTUATOR_SWITCH_POINTS` | Three physical `L_low_switch` / `L_high_switch` measurements, reverse-escape check, then re-run Z/pin/collision review. |
| `HOLD_ACTUATOR_PEAK_STALL_CURVE` | Written supplier or measured 24 V peak/stall current, duration and duty curve. |
| `HOLD_DMC_STOP_BEHAVIOR` | Bench fault injection: Portenta reset/hang and motion-bus unplug response, confirmed DMC retained-command/watchdog result. |
| `HOLD_SG01_QUOTE_CARD_STOCK` | Domestic VAT-included price, card purchase route, inventory and lead-time evidence for tGW-715i-T. |
| `HOLD_SMPS_30A_SKU` | Exact 24 V 30 A-class SKU with continuous rating, input/protection details and applicable certification. |
| `HOLD_ESTOP_DC_INTERRUPTION_RATING` | Selected disconnect device's 24 VDC inductive interruption rating, coil suppression and wiring/branch fuse basis. |
| `HOLD_BENCH_VERIFY` | Two-sensor 20 Hz, latency/freshness, reconnect and control-loop bench evidence. |
| `HOLD_PHYSICAL_CABLE_GUIDE_VERIFICATION` | Cable travel, strain relief and central-guide clearance at physical Z=15~65. If it fails, retain datum and cap command Z at 35 mm. |
| `HOLD_NO_INDEPENDENT_MECHANICAL_STOPS` | This is an intentional user-requested deviation, not a closable electrical claim; project purchase/fabrication release remains false until the project mechanical-stop rule is satisfied. |

## Explicit exclusions

This is not a final wiring drawing, code release, purchase release, fabrication release or field-safety assertion. It is for an indoor, supervised, no-cart/no-payload/no-person self-weight demonstration only.
