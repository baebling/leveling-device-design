# Rev E PoC release-candidate audit

+Date: 2026-09-04  
+Digital package: `PASS`  
+Purchase/fabrication/power/PoC acceptance: `FALSE`
+
+## Completed digitally
+
+- OpenCascade 27-pose audit repeated three times: PASS.
+- Pin distance: 210.771741-276.937115 mm inside 205-305 mm.
+- PHS6 maximum articulation: 4.096369 degrees below 8 degrees.
+- Existing Fusion-native interference evidence: three repeats, zero unexpected interference.
+- Existing Fusion section evidence: three section images present and hashed.
+- Fabrication RC: nine unique DXFs, one nine-sheet PDF, hole table, cut list, and assembly sequence.
+- Electrical RC: enclosure STEP/layout, circuit PDF, terminal map, point-to-point wiring, harness schedule, I/O map, and revised candidate BOM.
+- Firmware: command/state/fault/calibration implementation and static interface audit.
+
+## Still blocked by external evidence
+
+- LMB-10 supplier drawing or measured first article.
+- LM4075OE rated/start/stall current, exact encoder wiring/levels, internal limit behavior, and duty cycle.
+- Physical enclosure/backplate and PCB mounting-hole verification.
+- Arduino compilation on an installed board toolchain and hardware-in-loop checks.
+- One-axis current/counts/regeneration test, three-axis unloaded test, and 10 kg 27-trial acceptance.
+
+No purchase or fabrication should be released from this audit alone.
+