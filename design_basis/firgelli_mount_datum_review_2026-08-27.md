# Firgelli actuator mounting-datum review

Status: `PHASE_2_PRELIMINARY_NOT_FOR_FABRICATION`

## Decision

LS-01 fixed geometry now uses the official Firgelli MB21 body-bracket envelope as its layout datum. The moving geometry uses the official actuator front-clevis pin centre. The previous 42 mm moving-crosshead offset and chrome-rod clamp-like ring are retired.

This is a packaging decision only. The manufacturer pages describe MB21 as a fixed-position body support, but do not establish that the actuator housing or MB21 may react an external mechanical-stop impact. That acceptance remains a physical/vendor gate.

## Archived official STEP files

| File | SHA-256 |
|---|---|
| `F-SD-H-450-12v-8in.stp` | `54C6267D38D44EE6F9F9F247B51460A1983C2B19D89259968ECC6A103ADC8A34` |
| `Bracket_Assembly_MB-21.stp` | `CB0D8D22E77FF1A4FD0FBB7C60CC4301DA3282BE7FAB3E37FB79E7DA2A9BCCF0` |
| `Bracket_Assembly_MB-20.stp` | `7BE1541AF76A94C975FB3D6030CCED2991736463F716F90EDB7A9D6D6FB04538` |
| `MB-17_Assembly.stp` | `6FE08F3228442187239E2BC1E80A9FDA65A57F215AA1D27F311DB469B6A45197` |

## Extracted layout evidence

- Actuator STEP overall envelope: about 115.13 x 360.55 x 43.13 mm.
- STEP pin-centre span extracted from the model: about 318.017 mm, consistent with the official 319 mm nominal retracted length.
- Fixed body zone extracted from the STEP: about 45.17 to 288.73 mm from the rear pin.
- MB21 STEP overall envelope: 50 x 82.854 x 100 mm.
- MB21 at the selected 220 mm station spans 170 to 270 mm and remains inside the extracted body zone with about 18.73 mm minimum reserve.
- The actuator STEP contains separate moving rod/front-clevis and moving shoulder solids, so the front pin is the traceable moving datum.

## Joint compatibility decision

The selected Super Duty actuator has an integral 8.2 mm mounting eye at both ends. A serial HRT8E adapter was screened with a provisional 32 mm extension at each end. Removing 64 mm from the worst current joint distance leaves about 281.14 mm, below the catalogue 319 mm retracted length. The serial HRT8E topology is therefore archived for the active geometry.

The active measured-mock-up seed is `JNT-CG-01`. It keeps the actuator mounting-hole centre as the kinematic centre, uses the factory M8 pin for one rotation axis, and uses opposed M8 shoulder-screw trunnions for the orthogonal axis. This avoids stacking a second full through-pin across the first and adds no serial centre offset.

The official family drawing confirms an 8.2 mm hole and 20 mm eye outside diameter, but it is for a 220 lbf 2-inch model. The selected 450 lbf 8-inch eye thickness and pin stack must therefore be measured before machining even one cradle.

## Official sources

- Firgelli Super Duty actuator: https://www.firgelliauto.com/products/super-duty-actuators
- Firgelli MB21 fixed body bracket: https://www.firgelliauto.com/products/mb-21-bracket-for-super-duty-actuators
- Firgelli MB20 body swivel bracket: https://www.firgelliauto.com/products/mb-20-mounting-bracket-for-super-duty-actuators
- Firgelli MB17 clevis bracket: https://www.firgelliauto.com/products/mb-17-mounting-bracket-for-super-duty-actuators

## Next gate

Measure the purchased actuator eye thickness and supplied pin stack, then build one shim-adjustable `JNT-CG-01` cradle and one LS-01M cassette. Sweep both axes and load that single joint before copying the geometry to the remaining five ends.

Archived family-drawing SHA-256: `77AD4AA2E69FDC1A7573B641C8251930E8FBF0317A8782BDABD9999071E0BB05`.
