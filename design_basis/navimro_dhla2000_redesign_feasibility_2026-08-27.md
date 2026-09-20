# NAVIMRO DHLA2000 Redesign Feasibility

Date: 2026-08-27

Status: procurement-driven redesign candidate only. The active `RADIAL_3_CLEAN` CAD and fabrication status are unchanged.

## Conclusion

The three-actuator radial concept can be redesigned around items currently listed by NAVIMRO. The preferred actuator candidate is the DIHOOL `LA2000-125150`, NAVIMRO product code `K92931811`: 12 V, 2000 N, 150 mm stroke, 5 mm/s, IP43, built-in limit switch family, listed at 115,489 KRW VAT included when checked. The listing is made-to-order and non-returnable.

The associated DIHOOL 6 mm brackets are listed and are restored as the preferred pin/lug joint candidates:

- U type `IPS-B1-6MM-U`, NAVIMRO `K92931726`, 10,439 KRW VAT included.
- H type `IPS-B1-6MM-H`, NAVIMRO `K92931725`, 10,439 KRW VAT included.

The user-supplied detail image shows the actuator plus a separate accessory marked `diameter 10` and `M8`; flat panels appear later as an installation example. The current assumption is that flat panels are not supplied and the threaded accessory ends in an eye/pin interface. The purchased U/H brackets still require a custom shared-centre outer yoke cut from BOM steel flat bar.

## Preliminary Geometry

The preferred screening geometry preserves the current upper joint radius and the user-confirmed disconnected height:

| Parameter | Candidate value |
|---|---:|
| Upper joint radius | 400 mm |
| Lower joint radius | 175 mm |
| Collapsed vertical joint separation | 185 mm |
| Base joint Z | 50 mm |
| Top above upper joint | 35 mm |
| Disconnected collapsed height | 270 mm |
| Level/collapsed actuator length | 291.29 mm |
| Lift target | 100 mm |
| Pitch/roll target | +/-3 deg |

The official DIHOOL drawings show two different mounting cases for the relevant range. A1 uses `Lmin = stroke + 105 mm`, giving 255 to 405 mm for 150 mm stroke. A2 uses `Lmin = stroke + 115 mm`, giving 265 to 415 mm. The NAVIMRO listing does not identify A1/A2 and its detail image visibly contains DHLA6000-A2 material, so the listing image cannot identify the delivered variant. See `design_basis/navimro_web_drawing_review_2026-08-27.md`.

`calculations/navimro_dhla2000_workspace_screen.py` checks lift in 5 mm increments and all nine combinations of pitch/roll at -3, 0 and +3 degrees. The result is:

| Result | Value |
|---|---:|
| Minimum actuator length | 273.20 mm |
| Maximum actuator length | 385.35 mm |
| Required coupled span | 112.15 mm |
| Selected pin/lug planning margin | 18.20 / 19.65 mm |
| A2 reference retraction / extension margin | 8.20 / 29.65 mm |
| 5 mm planning keep-out | Pass for selected pin/lug planning case |

This is a geometric screen, not a fabrication release. Purchased STEP geometry, motor-box interference, joint-angle mobility, central-guide overlap, tolerance stack and mechanical-stop locations must be rechecked after seller confirmation.

## Force and Control Implications

The official DIHOOL page rates the 5 mm/s option at 2000 N push, pull and self-locking capacity, with 10% duty and maximum two-minute continuous use. This is above the current approximately 876 N active joint design screen, but the joint package and actual load test remain separate gates.

The official family supports optional Hall sensing and limit feedback, while the NAVIMRO SKU text does not explicitly confirm Hall feedback or the exact cable/wire configuration. Therefore:

- do not assume Hall pulses are included;
- obtain the exact wiring diagram and option code from NAVIMRO before ordering;
- if the listed SKU is limit-only, IMU feedback can close pitch/roll for a supervised stationary PoC, but accurate individual actuator position and repeatable Z height are not established;
- a Hall-equipped made-to-order option is preferred if NAVIMRO can supply it under the same product family.

NAVIMRO also lists a Cytron `MD10C` 13 A single-channel motor driver, Arduino Mega 2560 and Adafruit BNO055. These show that a NAVIMRO-centered PoC control BOM is possible, but dispatch availability for the driver/controller must be reconfirmed and BNO055 remains a one-off PoC choice rather than a preferred new-design sensor.

## Rejected First Pass

The first NAVIMRO candidate screened was the DIHOOL DHLA35 200 mm stroke actuator. Its provisional retracted length is about 453 mm. No geometry was found that simultaneously kept the 900 x 800 mm platform, 250 to 300 mm disconnected height, practical lower-joint spacing and the required workspace. The failure was packaging length rather than force. The compact DHLA2000 family was then found and replaces DHLA35 as the procurement-driven redesign candidate.

## Purchase Hold Points

Before ordering the non-returnable made-to-order actuators, obtain written confirmation of:

1. Written confirmation that `K92931811 / LA2000-125150` is supplied without flat panels and includes the pictured M8 rod-end accessory.
2. Exact eye-hole diameter, eye width, M8 thread engagement, rear mounting interface and pivot-centre Lmin/Lmax.
3. Hall sensor inclusion or exclusion, pulses per millimetre if included, limit-feedback wires and connector pinout.
4. Rated current, stall/current-limit recommendation and simultaneous three-axis power recommendation.
5. Exact bracket hole pattern, bracket material/thickness and included pins/retainers.
6. STEP file for the ordered 150 mm configuration.

Only after those six items are closed should the active CAD parameters, BOM and fabrication drawings be changed.

## Sources

- [NAVIMRO DIHOOL LA2000-125150](https://www.navimro.com/g/3267401/)
- [DIHOOL DHLA2000 official specifications](https://www.dihool.com/lang_en/Linear-Actuator-DHLA2000-Actuator_detail/6672_336)
- [NAVIMRO DIHOOL U bracket](https://www.navimro.com/g/3266724/)
- [NAVIMRO DIHOOL H bracket](https://www.navimro.com/g/3266613/)
- [NAVIMRO Cytron MD10C](https://www.navimro.com/g/437632/)
- [NAVIMRO Arduino Mega 2560](https://www.navimro.com/g/2261376/)
- [NAVIMRO Adafruit BNO055](https://www.navimro.com/g/437068/)
