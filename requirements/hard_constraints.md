# Hard Constraints

These constraints are not to be changed without explicit user approval. The 2026-10-02 decision in `references/수평유지장치 요구사항.txt` explicitly narrows HC-005 and HC-008 for a supervised, indoor, self-weight-only PoC; the historical general rule remains visible below. See `current_variant_priority_2026-10-02.md` for current release gates.

| ID | Constraint | Source | Notes |
|---|---|---|---|
| HC-001 | Design scope is the leveling/lifting upper module, lower mounting interface, and mechanical cart coupling only. | User prompt / AGENTS.md | No AMR, AGV, wheel, drive, navigation, robot arm, or cart-body design |
| HC-002 | Controlled upper platform DOF are Z translation, pitch, and roll. | User prompt / AGENTS.md | X, Y, yaw must be mechanically constrained |
| HC-003 | Human riding is prohibited. | User prompt | Do not claim people-carrying suitability |
| HC-004 | Cart lock must be mechanical locating/latching. | User prompt / AGENTS.md | Electromagnets may not be primary lock |
| HC-005 | Electrical limits and independent mechanical stops are separate protections in the general design rule. | User prompt / AGENTS.md; 2026-10-02 user PoC decision | For the supervised indoor self-weight PoC only, the user excludes the independent stop as an explicit deviation; factory limits, software travel window and E-stop do not become an equivalent mechanical stop. Reassess stops before any cart, payload, person, unattended or field use. |
| HC-006 | Do not infer real cart dimensions, material, mass, or hole positions from images. | User prompt / AGENTS.md | Keep cart interface parameterized until measured |
| HC-007 | Prototype budget limit is 4,000,000 KRW. | User prompt | Safety-critical functions must not be cut to meet budget |
| HC-008 | No released fabrication drawings until the current joint, bracket, fit, load, interference and electrical inputs close. | New parameter prompt / user scope reduction 2026-08-27; 2026-10-02 user PoC decision | The older stop-input prerequisite is superseded only for the narrow HC-005 deviation. Current STEP files and the factory-finished pocket bracket are review inputs, not released fabrication evidence. |
| HC-009 | Only existing A1–A3 lower aluminum plates and three factory-finished upper pocket brackets are metal-processing exceptions. | 2026-10-02 user decision | No other on-site metal cutting, drilling, tapping or welding. Plastic enclosure/backplate mounting, button and gland holes are allowed after layout review. |
| HC-010 | Purchase, fabrication, control-power and motor-power releases remain separate and false pending their own evidence. | 2026-10-02 user decision | No people, payload, field-safety or certification claim follows from the supervised self-weight scope. |
