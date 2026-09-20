# Standards Review

Access date: 2026-08-24

## Applicable Framework

The concept remains a PoC machine module, not a certified field machine. The standards below are used to structure risk reduction, emergency stop, fabrication tolerances, and fastener selection. They do not imply certification.

| Source ID | Standard | Current status found | Use in this project |
|---|---|---|---|
| SRC-STD-001 | ISO 12100:2010 | Published/current; last confirmed 2022; revision draft under development | Risk assessment and risk reduction logic |
| SRC-STD-002 | ISO 13850:2015 | Published/current; last confirmed 2020 | Emergency stop function concept |
| SRC-STD-003 | ISO 2768-1:1989 | Published/current; last confirmed 2022; replacement expected | General tolerance reference after fabrication approval |
| SRC-STD-004 | ISO 898-1:2013 | Published/current; to be revised | Bolt property class baseline |
| SRC-STD-005 | KS B ISO 12100 | Korean national standard detail confirmed 2023-12-26 | Korean safety terminology and report alignment |
| SRC-STD-006 | KOSHA Smart Guide | Public KOSHA guidance | Control box, emergency stop circuit, and interlock documentation checklist |

## Design Implications

- Use ISO 12100/KS B ISO 12100 as a documentation framework: hazards, protective measures, residual risks, validation method.
- Use ISO 13850 as the basis for requiring an emergency stop function independent of normal software commands.
- Use ISO 2768 only after `APPROVE PARAMETERS` and later fabrication drawing approval. Do not create detailed manufacturing drawings in Phase 0.
- Use ISO 898-1 for bolt property classes. Proposed baseline: property class 8.8 for structural metric bolts, stainless only when corrosion or exposed handling needs dominate and strength is checked separately.
- KOSHA guidance reinforces the need for an emergency stop circuit diagram and interlock list, even for PoC documentation.

## Open Items

- Confirm whether the final demonstration setup falls under any KCs self-declaration category. Current work must not claim KCs compliance.
- Confirm institute/shop fabrication tolerance convention before selecting ISO 2768 tolerance class.
- Confirm whether electrical work will use 12 V or 24 V as the main actuator bus before selecting E-stop contact blocks, fusing, and driver ratings.
