# Travel Limit And Mechanical Stop Strategy

Status: Phase 1 preliminary strategy. Not approved for fabrication.

## Limit Hierarchy

The actuator catalogue range is currently 319 to 523 mm pin-to-pin. It is not acceptable to use the actuator internal end condition as the system stop. For the recommended `WS-01-H20` workspace candidate, use the following preliminary hierarchy in actuator-length coordinates:

| Direction | Commanded soft boundary | Electrical limit target | Mechanical stop guarded boundary | Catalogue endpoint |
|---|---:|---:|---:|---:|
| Retraction | 334 mm minimum | 329 mm minimum | 324 mm minimum | 319 mm retracted |
| Extension | 508 mm maximum | 513 mm maximum | 518 mm maximum | 523 mm extended |

Motion order during retraction is: commanded soft limit -> electrical limit -> independent physical stop -> actuator catalogue end. Extension is the mirrored sequence. The 15 mm commanded keep-out consists of preliminary allowance for catalogue-end uncertainty, position-feedback/deceleration behavior, and assembly tolerance. The 5 mm electrical-to-stop allowance and 5 mm hard endpoint guard are also provisional; physical switch repeatability and actual actuator end dimensions must set the final values.

## Mechanical Architecture Rules

- Install a separate lower and upper lift stop as load-bearing physical contacts. Use external guide shoulders/collars or an equivalent geometry; do not put a solid stop block across the sliding inner tube.
- Install separate electrical limit/interlock switches for each travel direction. They interrupt the motion before the associated stop but are not load-carrying stops.
- The YAW-A angular stops are separate: pitch +/-7 degrees and roll +/-7 degrees, made as four adjustable stop contacts. They are not replacements for lift stops or electrical limits.
- CAD must check all permitted Z/pitch/roll poses and every practical stop-contact permutation. In every such state, every actuator must remain inside the actual manufacturer endpoints.
- CAD must provide a way to inspect and adjust stop contact. Stops must not be normal running supports.

## Selected Workspace Check

The `WS-01-H20` 270 mm collapsed-height candidate passes every `0/50/75/100 mm` and `-3/0/+3 degree` grid point inside the 334 to 508 mm commanded soft window. Its limiting condition is the 0 mm lift, combined +/-3 degree corner: shortest actuator length about 345.13 mm, or 11.13 mm beyond the lower soft boundary. The 100 mm-lift extreme remains far from the extension soft limit.

This is a geometry check only. It does not demonstrate that a real actuator can stop in the provisional 5 mm distance or that the stops can absorb impact.

## Preliminary Stop Load Reference

For the active low-load basis, the lifted mass is 42 kg: 10 kg material payload + approximately 10 kg cart + 22 kg maximum moving structure candidate. A 2.0 static reference factor gives:

```text
F_reference = 42 kg * 9.80665 m/s^2 * 2.0 = about 824 N
```

If two contacts shared load equally, that would be about 412 N each. This is **not** a stop-capacity design: impact energy, actuator speed, loss of position, compliance, unequal contact, fatigue, misalignment, and a falling load are not quantified. No stop may be considered safety-certified from this reference.

## Bench Acceptance Before Parameter Approval

1. Measure actual retracted/extended pin-to-pin length and verify internal-limit behavior for each purchased actuator.
2. At lowest practicable test speed, verify that each electrical limit removes drive before its corresponding physical stop. Record post-switch motion and repeatability over at least 10 cycles.
3. With electrical drive disabled, manually verify that every lift and gimbal stop reaches its intended contact before tube interference or actuator endpoint contact.
4. Inspect the keyed guide after the 10-cycle sequence for tube scrape, wear-pad damage, stop marking, fastener loosening, and increase in yaw freeplay.

```text
LIMIT HIERARCHY DEFINED AS A PRE-CAD STRATEGY
PHYSICAL STOP GEOMETRY AND TEST EVIDENCE STILL REQUIRED
```
