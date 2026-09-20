# Unresolved Inputs

| Priority | Input | Why it matters | Current handling |
|---|---|---|---|
| P0 | Whether 100 kg in early sketch is payload, gross cart load, or obsolete | Drives actuator, frame, latch, and base interface sizing | Treat as unresolved; do not design to 100 kg without approval |
| P0 | CR-01 aluminum-profile cart lower frame interface envelope | Determines guide pin spacing, latch bracket, receiver rail geometry | Current seed is two 760 mm HFS8 rails in a 760 x 560 mm receiver zone; exact connectors/profile section/insert plates/receiver zones remain open |
| P0 | CR-01-H1/H2/H3/H4 hardpoint and connector details | Determines repeatable seating, slot slip resistance, latch release clearance and sensor mounting | Current H4-S1 seed adds 12 mm removable master bushing, 40 x 8 mm replaceable stop, X-slot/diamond secondary, 40 x 30 mm shim pad, 5 mm keeper and secondary lock; exact slot nut, backing plate, bushing fit, torque, stop screws, dowel need, latch model, and sensor placement remain open |
| P0 | JNT-BR-01-HRT8E actuator bracket package | Determines actual joint articulation, pin bending, rod-end load direction, and attachment stiffness | Official 8/23/11 mm HRT8E dimensions are now reflected in an 18 mm-gap detailed CAD seed; obtain the physical part, prove 14 deg two-plane/diagonal no-contact articulation, then freeze spacers, pin retention, joining, attachment, fits, fatigue and shock behavior |
| P0 | WS-01-H20 physical actuator/guide/stop confirmation | Determines whether the selected 270 mm workspace retains its calculated margin after real actuator dimensions, switch overrun, and stop contacts | Use 270 mm / 195 mm outer guide / 220 mm inner guide only as a pre-CAD candidate; complete V-02 and V-03 in `design_basis/pre_cad_verification_plan.md` |
| P0 | Pre-CAD bench evidence | The selected YAW-A, JNT-BR-01, travel hierarchy, and CR-01-H4 candidates contain physical-contact assumptions | Complete V-01 to V-04 with measurement records; do not treat calculation-only pass as a fabrication release |
| P0 | Final payload rating | 10 kg PoC vs archived 20 kg sensitivity changes actuator margin | Use user-confirmed 10 kg rated material payload |
| P0 | Maximum allowed payload eccentricity | Controls actuator force and possible uplift | Use 50 mm target / 100 mm stress case |
| P0 | Pitch/Roll final range | ±3 is the current user-confirmed target; ±5 is future stretch only | Use ±3 deg PoC |
| P0 | Cart frame mass after concept sketch | Confirms the new cart stays near the 10 kg basis | Use 10 kg primary and 20/30 kg archived sensitivity until cart BOM exists |
| P1 | Cart and loaded material CG height | Needed for interface moments and overturning inputs | Use TBD; do not certify stability |
| P1 | Operating cycle count and demo timing | Needed for duty cycle validation | Use 10-cycle and 30-cycle test scenarios in report |
| P1 | Indoor/outdoor, dust/water, temperature | Determines IP rating and materials | Assume indoor dry PoC |
| P1 | Manufacturing method and local shop capability | Determines plate thickness, tolerances, and joining method | User prefers aluminum profile + bolt assembly; exact profile family, connector type, and insert plate fabrication remain open |
