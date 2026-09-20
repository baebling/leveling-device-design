# HMI-less laptop / dual-RS485 electrical topology — Z+15 baseline

## Status and scope

This is an analysis-only, self-weight, open-frame PoC topology. It does not release purchasing, fabrication, control power, motor power, field safety, certification, payload, or person use. No HMI and no spare actuator are included. The laptop USB link is the only operator start path; no command is issued automatically at power-up.

The command datum is retained: command `Z=0~50 mm` equals physical `Z=15~65 mm`, with pitch/roll simultaneously within ±3°. The nominal kinematic pin-length result is 221.281~289.523 mm and the provisional software window is `218~292 mm`. This software window is not a mechanical stop.

## Selected topology

```text
Laptop (USB serial; operator START/HOME/JOG/LIFT/LEVEL/STOP + CSV)
  |
  +-- USB --> PC01 Portenta Machine Control
                  |
                  +-- J5 RS-485, DMC proprietary protocol, short daisy chain
                  |     +--> DC01 DMC-200, address 1 --> LM4075OE-1075 axis 1
                  |     +--> DC02 DMC-200, address 2 --> LM4075OE-1075 axis 2
                  |     +--> DC03 DMC-200, address 3 --> LM4075OE-1075 axis 3
                  |
                  +-- Ethernet --> SG01 ICP DAS tGW-715i-T
                                      static IP, Modbus TCP server/slave, TCP 502
                                      RS-485 Modbus RTU master
                                      +--> IS01 HWT905, decimal ID 11
                                      +--> IS02 HWT905, decimal ID 12

Independent safety branch: E-stop NC -> 24 VDC rated disconnect/contactor -> DMC motor-power feed.
Control/status power is not the E-stop safety substitute.
```

`IF01` is removed from the new topology and new-BOM intent. The DMC chain and the HWT905 chain are physically separate RS-485 segments: DMC proprietary protocol and Modbus RTU must not share a bus. A 120-ohm terminator is installed only at each physical segment end after bench confirmation; cable shield is bonded at one control-enclosure end and PE is never used as the signal return.

## Static configuration and stale-data rules

| Branch | Fixed configuration | Before joining the full network | Stale/failed response action |
|---|---|---|---|
| DMC motion | Addresses 1/2/3, short J5 daisy chain, each axis has a unique address | Verify the DMC 5 V encoder supply/output current, A/B logic and pull-up compatibility, 6 ppr resolution/count scaling, address and three-node multidrop configuration, encoder direction, controlled JOG/STOP, and reverse escape after the internal limit one axis at a time with actuator supported | Portenta command-session timeout, bounded JOG, all-axis STOP and latched fault. A new laptop `START` is required after reconnection. `HOLD_DMC_STOP_BEHAVIOR`: serial STOP is not proof that a Portenta hang or bus failure bounds retained DMC motion. |
| IMU sensing | SG01 static IP, TCP server/slave on TCP 502; Portenta is Modbus TCP client/master; SG01 is RTU master; HWT905 IDs 11 and 12 | Configure one HWT905 at a time, save, power-cycle and read back its ID/settings, then connect both | Missing, malformed, wrong-ID, out-of-order, or older-than-the-configured freshness deadline sample inhibits `LEVEL`, emits a latched communication fault and is logged. The numerical deadline and 20 Hz behaviour remain `HOLD_BENCH_VERIFY`. |

`Moxa MB3180` remains a fallback only; no verified serial-isolation basis exists in current evidence, so it cannot silently replace SG01.

## Power allocation and stop logic

| Load / branch | Basis | Present selection state |
|---|---|---|
| Three actuator motor branches | LM4075OE-1075, 24 V; 0.4 A no-load and 1.5 A loaded per axis from supplied table; provisional peak 7.5 A per axis | Three-axis provisional peak: 22.5 A. With 25% margin: 28.125 A. Motor PSU basis: **24 V, 30 A class**. |
| DMC-200 per axis | 8 A continuous driver capacity | Nominal 1.5 A loaded is below the continuous capacity. Actual motor peak/stall curve and time-at-current are not verified. |
| SG01 gateway | tGW-715i-T: 12--48 VDC, 0.07 A at 24 V | Control-power allocation only; supplier card checkout, price and lead time unresolved. |
| Portenta, two IMUs, encoders, relay/contactor coil and logic branch | Need worst-case data sheets and chosen relay/contactor coil current | Separate protected control-power allocation; do not use old 1 A fuse assumption. |

The E-stop is an independent physical 24 V motor-power interruption, not laptop software STOP. The switching device must have a documented 24 VDC inductive interruption rating at the required current. DMC serial STOP is an additional control response only.

## HOME / motion-state constraint

Normal `HOME` never seeks either actuator end limit. It may return to the saved physical Z=15 command datum only when saved position, Z=15 offset and no-manual-move evidence are valid. Otherwise it returns `HOME_START_UNVERIFIED` and blocks normal HOME/LEVEL. Block-supported, supervised `COMMISSIONING_HOME` or recovery may approach an internal limit, but it cannot automatically enable `LEVEL`; the normal-HOME evidence must be recreated first.

## Unclosed gates

- `HOLD_ACTUATOR_SWITCH_POINTS` — measure all actual internal low/high switch points; 205~305 mm CAD values are not switch-trip values.
- `HOLD_ACTUATOR_PEAK_STALL_CURVE` — supplier evidence for actual peak/stall current, duration, duty cycle and reverse escape after internal limit.
- `HOLD_DMC_ENCODER_MULTIDROP_COMPATIBILITY` — DMC-200 ↔ LM4075OE 5 V A/B 6 ppr electrical/feedback compatibility: DMC 5 V encoder supply/output current, A/B logic/pull-up, count scaling, three-node addresses/multidrop configuration, and reverse escape after internal limit.
- `HOLD_DMC_STOP_BEHAVIOR` — retained-command/watchdog and failure response on master hang or motion-bus loss.
- `HOLD_SG01_QUOTE_CARD_STOCK` — domestic card checkout, VAT/lead/stock evidence for tGW-715i-T.
- `HOLD_SMPS_30A_SKU` — exact 24 V 30 A-class SKU, continuous rating, input protection and applicable certification evidence.
- `HOLD_ESTOP_DC_INTERRUPTION_RATING` — contactor/relay 24 VDC inductive interruption rating and transient treatment.
- `HOLD_BENCH_VERIFY` — end-to-end IMU rate, latency, timeout/reconnect and control performance.
- `HOLD_PHYSICAL_CABLE_GUIDE_VERIFICATION` — physical cable travel/strain relief and central-guide verification over physical Z=15~65 mm; reduce command maximum Z to 35 mm if this fails.

The intentional omission of independent mechanical stops remains an explicit safety deviation. It prevents purchase and fabrication release under the project rules.
