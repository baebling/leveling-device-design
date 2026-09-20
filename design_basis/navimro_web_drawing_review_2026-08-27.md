# NAVIMRO / DIHOOL Web Drawing Review

Date: 2026-08-27

## Answer

The user directed the redesign to assume that flat mounting panels are not supplied. The planning interface is therefore an M8 threaded rod-end accessory terminating in an eye/pin joint. This is sufficient for preliminary CAD and workspace screening, but the non-returnable NAVIMRO `K92931811` still needs written confirmation of the supplied adapter and pivot dimensions before purchase.

## What Can Be Confirmed From Web Drawings

The official DIHOOL DHLA2000 drawings distinguish two mounting variants:

| Variant | Official formula for S < 500 mm | 150 mm stroke range | Interface |
|---|---|---|---|
| A1 | `Lmin = S + 105` | 255 to 405 mm | 6.1 mm pin holes at both ends |
| A2 | `Lmin = S + 115` | 265 to 415 mm | plate/fork arrangement shown in the A2 drawing |

The A1 drawing also provides the body and end-eye envelope needed for preliminary packaging. Official generic A1 and A2 STEP files are linked from the manufacturer page.

The NAVIMRO U/H bracket detail images provide usable preliminary dimensions:

- U bracket: 6 mm pivot pin, 26.5 mm outside width, 45 mm base length and mounting-hole dimensions shown.
- H bracket: 6 mm pivot hole, 62 mm base width, 18 mm lug width and mounting-hole pattern shown.

These dimensions are adequate to model the purchased brackets and design the custom orthogonal outer yoke.

## Why The NAVIMRO Listing Still Needs Confirmation

The two NAVIMRO links supplied by the user do not identify equivalent 150 mm A1/A2 options:

- `3267413` is actually the 500 mm-stroke `LA2000-125500 / K92931822` listing, even though its detail material shows DHLA2000-A1;
- `3267401` is the required 150 mm-stroke `LA2000-125150 / K92931811` listing, while its detail material visibly says DHLA6000-A2;
- the first portion of that detail material depicts an actuator plus a separate accessory marked `diameter 10` and `M8`, while the flat panels appear later as an installation example;
- the representative image is likewise not a dimensioned exact 150 mm SKU drawing;
- Hall sensing is optional on the DIHOOL family page, but the NAVIMRO SKU does not state whether it is included;
- wire count, connector, limit feedback and current are not fixed by the drawing.

The user-selected planning assumption is therefore reasonable, but it is not proof of supplied contents. The remaining seller question is:

> Confirm that `K92931811 / LA2000-125150` is supplied without flat panels and includes the pictured M8-to-eye/pin rod-end accessory. Provide the eye-hole diameter, eye width, thread engagement, both-end interfaces, pivot-centre Lmin/Lmax, Hall/limit-feedback wiring, current and matching STEP.

## Workspace Result For Both Web Cases

With the non-flat pin/lug planning interface, the collapsed vertical joint separation returns to 185 mm. The disconnected height is 270 mm and remains inside the 250 to 300 mm requirement. The 0 to 100 mm lift and +/-3 degree nine-corner screen requires 273.20 to 385.35 mm.

| Case | Retract margin | Extend margin | 5 mm planning window |
|---|---:|---:|---|
| Pin/lug planning case using A1-style 255 to 405 mm | 18.20 mm | 19.65 mm | Pass |
| A2 reference case, 265 to 415 mm | 8.20 mm | 29.65 mm | Pass, but not selected |

The pin/lug case is now the selected planning baseline. Each actuator end uses the listed 6 mm U/H bracket candidates plus a shared-centre orthogonal outer yoke so pitch and roll do not impose bending on the actuator. The assumed 255 to 405 mm range is provisional until NAVIMRO provides pivot-centre dimensions for the supplied accessory.

## Sources

- [NAVIMRO K92931811 listing](https://www.navimro.com/g/3267401/)
- [NAVIMRO K92931822 500 mm listing used for the A1 detail image](https://www.navimro.com/g/3267413/)
- [DIHOOL DHLA2000 12 V A1](https://www.dihool.com/lang_en/Linear-Actuator-DHLA2000-Actuator_detail/1468_336)
- [DIHOOL DHLA2000 12 V A2](https://www.dihool.com/lang_en/Linear-Actuator-DHLA2000-Actuator_detail/6672_336)
- [NAVIMRO U bracket drawing](https://www.navimro.com/g/3266724/)
- [NAVIMRO H bracket drawing](https://www.navimro.com/g/3266613/)
