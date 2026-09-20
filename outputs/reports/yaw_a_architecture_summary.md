# YAW-A Architecture Summary

Status: preliminary. Not ready for `APPROVE PARAMETERS`.

## Result

The preferred central yaw path was converted into candidate Phase 0 parameters. This summary now reflects the 2026-08-25 user clarification: 10 kg carried payload, about 10 kg empty cart mass, 250 to 300 mm disconnected device height, and +/-3 deg pitch/roll are sufficient, with simple fabrication/assembly preferred.

YAW-A definition:

- Keyed square telescoping guide carries yaw torque.
- Two-axis gimbal/yoke permits pitch/roll.
- Yaw is mechanically constrained.
- A loose spherical joint is rejected because yaw would be unconstrained.
- A rigid guide without gimbal is rejected because pitch/roll would bind.

## Candidate Parameters

| Parameter | Candidate |
|---|---:|
| Gimbal design angle | 8 deg |
| Gimbal hard stop | 10 deg |
| Preferred total yaw clearance | <= 0.2 mm |
| Maximum total yaw clearance | <= 0.3 mm |
| Preferred yaw freeplay | <= 0.25 deg |
| Maximum yaw freeplay | <= 0.5 deg |
| Anti-yaw contact width | >= 10 mm |
| Minimum engaged overlap | >= 80 mm |
| Preferred engaged overlap | >= 100 mm |
| Gimbal/yoke yaw couple arm | >= 50 mm |
| Gimbal/yoke pin diameter | >= 10 mm |
| Gimbal/yoke lug thickness | >= 8 mm |

## Key Screens

- Constraint rank: 3, leaving Z, pitch, roll.
- Required gimbal angle at +/-3 deg plus margin: 6.24 deg, so 8 deg design angle passes.
- Required gimbal angle at +/-5 deg plus margin: 9.07 deg, so 10 deg hard stop covers it only as a non-required sensitivity.
- Required gimbal angle at +/-8 deg plus margin: 13.30 deg, so it is not carried as a current baseline.
- 0.2 mm total clearance gives about 0.23 deg yaw freeplay.
- 0.3 mm total clearance gives about 0.34 deg yaw freeplay.
- 0.5 mm total clearance is rejected in the current screen.
- User-confirmed PoC design yaw torque is about 16 Nm with the 10 kg cart basis.
- Heavy-cart 30 kg sensitivity remains about 24 Nm.
- 10 mm pin, 8 mm lug, 50 mm yaw couple arm gives about 2.1 MPa pin shear and 4.1 MPa lug bearing under the user-confirmed primary PoC yaw screen.

## Gate

```text
YAW-A CANDIDATE PARAMETERS DEFINED
USER-CONFIRMED LOW-LOAD +/-3 DEG BASELINE
CENTRAL GUIDE STILL CRITICAL_OPEN
NOT READY FOR APPROVE PARAMETERS
```
