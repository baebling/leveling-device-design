# Project instructions

This workspace contains a preliminary PoC concept for a cart-mounted leveling and lifting upper module.

## Scope gate

- Work only on the leveling/lifting upper module, its universal lower mounting interface, and the mechanical cart coupling interface.
- Do not design an AMR, AGV, wheel, caster, drive unit, navigation system, robot arm, or the cart body.
- Treat the newest requirements in `references/수평유지장치 요구사항.txt` as authoritative when reference files conflict.
- Never infer actual cart dimensions, mass, materials, or hole positions from images.
- Keep uncertain inputs parameterized and record assumptions.

## Phase gate

- Phase 1 is the current approved scope.
- Do not begin detailed parametric CAD, fabrication drawings, embedded control code, or manufacturing exports until the user types `APPROVE CONCEPT`.
- All Phase 1 geometry is preliminary and must be marked as not approved for fabrication.

## Engineering rules

- The permitted upper-platform degrees of freedom are Z translation, pitch, and roll.
- Mechanically constrain X translation, Y translation, and yaw.
- Separate electrical limit switches from independent mechanical stops.
- Use mechanical locating and latching for the cart; electromagnets may not be the primary lock.
- State load cases, safety factors, coordinate systems, equations, uncertainty, and unresolved risks.
- Do not claim certification, field safety, or suitability for carrying people.

