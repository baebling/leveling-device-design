# Rev E powered PoC commissioning and acceptance protocol

Status: `PROCEDURE RELEASED`, `PHYSICAL TEST NOT EXECUTED`

This protocol applies only to a stationary indoor supervised proof-of-concept. It is not a safety-certification test and the platform must not carry people.

## Instruments and preparation

- True-RMS DC clamp meter or inline current meter with suitable range
- 0-30 VDC logger or oscilloscope for 24 V bus peak capture
- Digital angle reference with at least 0.1 degree resolution
- Vernier caliper, steel rule, torque tools, insulated hand tools
- Temperature probe or IR thermometer
- Independent support blocks capable of carrying the complete upper frame and test mass
- 10 kg verified test mass

Before energization, record every SKU, quantity, serial/lot where available, actual dimensions, and drawing revision. Reject or quarantine any item that differs from the candidate BOM or frozen interface register.

## Gate A - first-article mechanical inspection

1. Measure the LMB-10 base, hole pitch, pivot center, inner gap, pin diameter, grip length, and retainers.
2. Measure both LM4075OE eye widths, bores, collapsed pin distance, cable exit, and connector/wire count.
3. Enter results in the supplier interface register and regenerate C01-C03 if any value differs.
4. Assemble only A1 with the upper frame independently supported.
5. Verify free lower-pivot rotation, PHS6 articulation, bolt access, motor-body clearance, and a retained pin at both joints.
6. Do not continue if a bolt thread crosses a bearing/eye shear plane, a bracket must be forced, or less than 1 mm running clearance exists at any non-contact interface.

## Gate B - unpowered three-axis inspection

1. Assemble all three axes and independent mechanical stops.
2. Check fastener engagement and witness-mark all final fasteners.
3. Move the supported upper frame through Z 0/25/50 mm and pitch/roll -3/0/+3 degree combinations.
4. Record the 27 pose checks. Required result: no unexpected contact, binding, stop contact inside the command range, cable tension, or loss of pin retention.
5. Repeat visual section checks at the three lower joints and three upper joints.

## Gate C - electrical dead checks

1. Keep AC disconnected. Verify protective-earth continuity from plug PE to PSU FG, DIN rail, and the dedicated lower-frame bond point.
2. Verify no continuity from L/N to PE, no 24 V short, and correct fuse values.
3. Verify MDD10A polarity; the board has no reverse-polarity protection.
4. Verify every motor and encoder conductor end-to-end against the point-to-point table.
5. With the Mega externally powered from the 5 V converter, use a USB data cable with VBUS disconnected.

## Gate D - PSU and logic

1. Disconnect both MDD10A Vmotor inputs and all actuators.
2. Energize through Q1 and confirm 24.0 VDC and 5.00 VDC before connecting loads.
3. Confirm firmware reset leaves all four PWM outputs at zero.
4. Confirm IMU telemetry updates faster than 200 ms and `ZERO_IMU` produces near-zero pitch/roll on the reference plane.

## Gate E - one-axis powered commissioning

1. Connect only D1 channel 1 and actuator A1 with the frame mechanically supported.
2. Use short low-PWM motions to establish extension polarity and encoder sign.
3. Run supervised `HOME`; independently verify that the actuator internal retract limit removes motor power.
4. Measure encoder counts over at least 50 mm in extension and retraction. Record counts/mm and backlash.
5. Measure startup peak, steady unloaded current, controlled obstruction current without dwelling at stall, and stop current.
6. During lowering and braking, record the highest 24 V bus value.
7. Stop and redesign if channel continuous current exceeds 8 A, total projected demand exceeds 11.68 A, or bus voltage exceeds 28 V.

## Gate F - three-axis unloaded

1. Repeat Gate E for A2 and A3.
2. Save all counts/mm and the reviewed sensitivity matrix with `SAVE_CAL`.
3. Test `JOG`, `LIFT 0`, `LIFT 25`, and `LIFT 50` sequentially.
4. Verify 100 ms reversal dead time, PWM ramp, no-pulse fault, wrong-direction fault, IMU stale fault, 5 degree tilt fault, and 30 second timeout.
5. Run `LEVEL` from each of the nine pitch/roll combinations three times without payload.

## Gate G - 10 kg acceptance

At Z=25 mm, test pitch/roll input combinations -3/0/+3 degrees, nine combinations total, three trials each. For every trial record initial angle, final angle, time to tolerance, 10-second hold maximum error, current, bus peak, temperature, noise/binding, and pass/fail.

Acceptance requires all 27 trials to reach and remain within +/-0.5 degrees on both axes in 30 seconds, hold for at least 10 seconds, and exhibit no interference, binding, unexpected stop contact, pin migration, loose fastener, or overheating.

## Final release

Purchase release, fabrication release, power release, and PoC acceptance are separate decisions. Close only the gate supported by evidence. Any supplier or physical discrepancy triggers CAD, drawing, BOM, and full validation reruns before further assembly.
