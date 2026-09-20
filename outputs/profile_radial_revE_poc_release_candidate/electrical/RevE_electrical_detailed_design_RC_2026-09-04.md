# Rev E electrical detailed design - release candidate

+Date: 2026-09-04  
+Status: `ELECTRICAL_DETAIL_RC_COMPLETE`, `POWER_RELEASE=FALSE`, `PURCHASE_RELEASE=FALSE`
+
+## Architecture
+
+One Mega2560-compatible board commands three brushed-DC axes through two Cytron MDD10A boards. D1 uses both channels for axes 1 and 2; D2 uses channel 1 for axis 3 and its fourth channel is hard-commanded to PWM 0. The IMU is a GY-521/MPU6050 on I2C. The PC or available Jetson Nano is optional for USB commands and logging; the real-time loop runs on the Mega.
+
+The MDD10A has one shared motor-supply input per two-channel board. Therefore this revision adds two provisional 10 A board-input fuses, while the three existing 5 A fuses are placed in one output lead per actuator. All fuse ratings remain blocked until startup, running, stall, and lowering-regeneration measurements are available.
+
+## Enclosure result
+
+- External enclosure: 400 x 500 x 155 mm.
+- Device envelopes in assumed 360 x 460 x 127 mm usable space: 9.
+- Component overlap pairs: 0.
+- AC-to-logic planar separation: 60 mm, requirement 50 mm.
+- DIN rail cut seed: 320 mm x 2.
+- Envelope audit: PASS.
+- Drilling release: FALSE until the SL902 backplate and board hole patterns are physically verified.
+
+## Power and grounding
+
+The 230 VAC input passes through the accessible 2-pole breaker to the LRS-350-24. Protective earth goes directly to the PSU FG terminal and dedicated metal-bond points; it is never switched or fused. The ABS enclosure does not replace protective bonding of the PSU, DIN rail, or lower aluminum frame. AC, motor-power, and logic routes are physically separated.
+
+The regulated 5 V branch powers the Mega 5 V rail, encoders, and GY-521. When external 5 V is connected, the USB cable must be data-only with VBUS disconnected to prevent two 5 V sources from opposing each other. The exact TS0481 power-selector behavior must be verified on receipt.
+
+## Candidate BOM budget
+
+- Known screen-price subtotal including the added input fuses: 1,278,437 KRW.
+- 3.6M target margin before machining, freight, and open quotes: 2,321,563 KRW.
+- 4.0M absolute-budget margin before machining, freight, and open quotes: 2,721,563 KRW.
+
+This subtotal is not a final quotation and does not authorize purchase.
+
+## Mandatory release gates
+
+1. Written actuator current, encoder, limit, and duty-cycle data or a measured first article.
+2. One-axis unloaded startup/running/stall-protected current and 24 V bus peak measurement.
+3. MDD10A channel current below 8 A continuous and total PSU demand below 11.68 A.
+4. Lowering/braking bus peak at or below 28 V.
+5. Physical enclosure/backplate, PCB mounting holes, terminal covers, bend radius, and tool access verified.
+6. Competent-person review of all 230 VAC work before energization.
+
+Source basis: Cytron MDD10A manufacturer page (5-30 V Rev2.0, 10 A continuous/channel, 30 A peak, regeneration, 84.5 x 62 mm) and Mean Well LRS-350 official datasheet (24 V, 14.6 A, 215 x 115 x 30 mm).
+