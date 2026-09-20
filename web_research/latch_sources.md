# Latch And Cart Coupling Sources

Access date: 2026-08-24

## Candidate Summary

| Source ID | Manufacturer | Candidate | Key official values | Fit for PoC | Decision |
|---|---|---|---|---|---|
| SRC-LAT-001 | DESTACO | 323-R pull-action latch | 360 lbf maximum holding capacity, U-hook, flange mount | Low-cost latch for clamping/uplift restraint | Current provisional latch |
| SRC-LAT-002 | Southco | TL / draw latch families | Over-center draw latch families; mechanical advantage and anti-rattle use | Good alternative with broad industrial family | Candidate, specific SKU TBD |
| SRC-LAT-003 | Elesa+Ganter | GN 850 | Holding capacity by size; rapid closing/fastening | Good metric catalog alternative | Candidate, size TBD |
| SRC-LAT-004 | Elesa+Ganter | GN 850.2 safety hook | Spring-loaded safety hook resists accidental/vibration unlocking | Better safety function than basic latch | Preferred family for later review if cost allows |

## Coupling Rule

The latch must not be treated as the primary horizontal shear member. The coupling should divide functions:

- Round locator + diamond/slot locator: repeatability and X/Y/yaw location.
- Tapered guide/rest pads: rough entry, support, contact load distribution.
- Draw latches: vertical uplift restraint, preload, anti-rattle.
- Secondary lock or safety clip: vibration/accidental release prevention.
- Latch closed sensor: interlock input, not a structural restraint.

## Provisional Variables

| Variable | Value | Status | Basis |
|---|---:|---|---|
| latch_count | 4 | PROVISIONAL | Keeps per-latch uplift small and provides symmetric clamping |
| latch_type | pull-action / over-center draw latch with lock feature | TARGET | SRC-LAT-001 through SRC-LAT-004 |
| horizontal_shear_restraint | guide pins / shear keys | HARD_CONSTRAINT | New instruction and original project rules |
| secondary_lock_required | yes | HARD_CONSTRAINT | Original project safety rule |

## Open Items

- Actual cart-side bracket geometry and allowed modification method are still unknown.
- Manual release force and operator access side are unknown.
- Latch holding capacity must be derated after bracket stiffness and shock assumptions are known.
