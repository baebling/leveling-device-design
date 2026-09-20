# NAVIMRO Non-Flat Pin/Lug Interface Assumption

Date: 2026-08-27

Status: preliminary procurement-driven CAD assumption; not approved for fabrication.

## User Direction

Proceed on the assumption that NAVIMRO `K92931811 / LA2000-125150` is supplied without the flat top and bottom panels shown later in the generic detail image. Assume that the actuator uses a threaded rod-end accessory terminating in an eye/pin interface.

## What The Detail Image Actually Shows

- The first product-detail section depicts an actuator body plus a separate accessory marked `diameter 10` and `M8`.
- Flat top and bottom panels appear later in an installation example.
- The same image is labelled DHLA6000-A2, while the NAVIMRO listing is DHLA2000 `LA2000-125150`.

Therefore, the non-flat interface is a user-directed planning assumption, not proof of the delivered contents.

## Preliminary Mechanical Interface

- Treat the rod-end accessory as an M8-threaded adapter with an eye/pin termination.
- Treat both actuator ends as articulated; do not introduce a rigid end connection.
- Reserve one NAVIMRO 6 mm U bracket and one H bracket at each of the six actuator ends.
- Use a fabricated shared-centre orthogonal outer yoke so the two rotation axes do not add actuator length.
- Keep eye-hole diameter, eye width, rear-end interface, M8 thread engagement and pin retention parameterized until a seller drawing is received.
- Do not use the M8 thread or the adapter as an unsupported transverse bending member.

## Selected Planning Geometry

| Parameter | Value |
|---|---:|
| Upper joint radius | 400 mm |
| Lower joint radius | 175 mm |
| Collapsed vertical joint separation | 185 mm |
| Disconnected module height | 270 mm |
| Lift target | 100 mm |
| Pitch/roll target | +/-3 deg |
| Required actuator pivot-centre range | 273.20 to 385.35 mm |
| Provisional pin/lug actuator range | 255 to 405 mm |
| Retract/extend physical reserve | 18.20 / 19.65 mm |

The provisional range is borrowed from the official DHLA2000 A1 pin-end formula only for workspace planning. It must be replaced by the supplied accessory's actual pivot-centre dimensions.

## Purchase Gate

Before the one-time non-returnable order is released, obtain written confirmation of:

1. no flat panels supplied;
2. included quantity and part number of the pictured `diameter 10 / M8` accessory;
3. eye-hole diameter, eye width and pin hardware;
4. both-end mounting interfaces and pivot-centre Lmin/Lmax;
5. compatibility with `IPS-B1-6MM-U` and `IPS-B1-6MM-H`;
6. Hall/limit wiring, rated and stall current, and matching STEP files.

The design may continue parametrically before this reply, but cut/drill drawings and the purchase release remain blocked.

## Preliminary CAD Seed

- Source: `cad/navimro_pin_lug_gimbal.py`
- STEP: `outputs/cad/step/navimro_pin_lug_gimbal_assumption.step`
- Render: `outputs/renders/navimro_pin_lug_gimbal_assumption.png`

The seed keeps the assumed 6 mm eye-pin axis and the opposed M8 trunnion axis orthogonal and coincident. It is an interface study only; the yellow U-bracket envelope is translucent to expose the assumed M8-to-eye accessory. No root attachment or fabrication hole pattern is released.
