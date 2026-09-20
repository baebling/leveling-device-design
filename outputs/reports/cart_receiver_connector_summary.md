# Cart receiver connector summary

Status: Phase 1 preliminary. Not approved for fabrication.

CR-01-H2 screens the connector and anti-slip topology between the CR-01 aluminum-profile receiver rails and the CR-01-H1 local hard points.

## Current conclusion

Preferred topology:

```text
CR-01-H2-B
two M8-class T-slot fasteners for clamp/adjustment
+ shoulder/key/positive stop after mock-up alignment for final locating
+ optional dowel if repeatability requires it
```

Rejected:

```text
CR-01-H2-A slot friction only
```

Although the placeholder friction slip screen gives about 6.45x margin at the current low-load demand, it is rejected as a final locating method. Slot friction can be used during mock-up adjustment, but the final X/Y/yaw locating path needs a mechanical shoulder, key, dowel, or positive stop.

## Key numbers

| Screen item | Result |
|---|---:|
| Connector design demand | about 186 N |
| Friction-only placeholder slip margin | about 6.45x |
| Positive stop bearing, 40 x 8 mm contact | about 0.58 MPa |
| Positive stop local tab bending, 6 mm tab / 25 mm cantilever | about 19 MPa |
| Optional 6 mm dowel shear | about 6.6 MPa |
| Optional 6 mm dowel bearing in 8 mm plate | about 3.9 MPa |

## Remaining blockers

- Exact slot nut / connector family.
- Backing plate need after profile wall stiffness check.
- Shoulder/key/stop replaceability and access.
- Profile wall bearing and local indentation.
- Dowel location after mock-up alignment.
- Sensor placement for cart-present and latch-closed states.

This remains:

```text
PHASE_1_PRELIMINARY_NOT_FOR_FABRICATION
```
