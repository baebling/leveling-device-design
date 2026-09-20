# Hard Constraints

These constraints are not to be changed without explicit user approval.

| ID | Constraint | Source | Notes |
|---|---|---|---|
| HC-001 | Design scope is the leveling/lifting upper module, lower mounting interface, and mechanical cart coupling only. | User prompt / AGENTS.md | No AMR, AGV, wheel, drive, navigation, robot arm, or cart-body design |
| HC-002 | Controlled upper platform DOF are Z translation, pitch, and roll. | User prompt / AGENTS.md | X, Y, yaw must be mechanically constrained |
| HC-003 | Human riding is prohibited. | User prompt | Do not claim people-carrying suitability |
| HC-004 | Cart lock must be mechanical locating/latching. | User prompt / AGENTS.md | Electromagnets may not be primary lock |
| HC-005 | Electrical limits and mechanical stops must be separate. | User prompt / AGENTS.md | Static-bench variant uses factory internal electrical limits plus independent external mechanical collars; internal limits are not the only stop |
| HC-006 | Do not infer real cart dimensions, material, mass, or hole positions from images. | User prompt / AGENTS.md | Keep cart interface parameterized until measured |
| HC-007 | Prototype budget limit is 4,000,000 KRW. | User prompt | Safety-critical functions must not be cut to meet budget |
| HC-008 | No released fabrication drawings until measured joint and stop inputs close. | New parameter prompt / user scope reduction 2026-08-27 | Current STEP files are measured-mockup seeds; hole fits tolerances and root attachments remain unreleased |
