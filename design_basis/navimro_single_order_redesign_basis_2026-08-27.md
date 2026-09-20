# NAVIMRO Single-Order Redesign Basis

Date: 2026-08-27

Status: procurement architecture selected; active Firgelli CAD replacement pending vendor drawings.

## Scope And Requirements

The redesign retains the approved `RADIAL_3_CLEAN` concept and changes the purchased-part ecosystem to NAVIMRO. It covers only the leveling/lifting upper module, the universal lower mounting interface and the mechanical cart coupling interface.

Design inputs remain:

- 10 kg payload;
- approximately 10 kg empty cart as context, not a structural cart design input;
- disconnected module height 250 to 300 mm, candidate 270 mm;
- Z lift target 100 mm;
- pitch and roll +/-3 degrees;
- stationary, supervised, low-speed PoC;
- easy cutting, drilling and bolted assembly preferred over complex machining.

## Selected Architecture

### Radial actuation

Three non-flat pin/lug `LA2000-125150` actuators remain 120 degrees apart. The screening radii are 400 mm upper and 175 mm lower, with 185 mm collapsed vertical joint separation. The disconnected height is 270 mm. The calculated actuator range over 0 to 100 mm lift and the nine +/-3 degree pitch/roll corners is 273.20 to 385.35 mm. Against the provisional A1-style pin-centre range of 255 to 405 mm this leaves 18.20 mm retract and 19.65 mm extend margin.

This is not yet a release calculation because the exact M8 accessory and pivot-centre drawing are missing. Both actuator ends use pin joints and shared-centre orthogonal yokes; the adapter eye is not treated as a rigid frame connection.

### Central constraint

The earlier fabricated nested-square-tube guide is replaced by two parallel 12 mm vertical shafts, four `LMF12UU` flange bushings and four `SK12` supports. The paired shafts constrain X translation, Y translation and yaw while allowing Z translation. A compact two-axis Cardan between the carriage and upper frame allows pitch and roll.

Independent mechanical limits are provided by:

- four split collars on the guide shafts for upper/lower Z travel boundaries;
- fabricated hard stops on both Cardan axes at +/-7 degrees per axis;
- actuator internal electrical endpoints remain separate from these mechanical stops.

### Frame and deck

The load path is 4040 aluminum profile, not acrylic. The 15 mm acrylic is a supported deck/panel only. Steel spreaders made from 50 x 6 mm flat bar distribute actuator, guide and cart-interface loads into the profile frame.

### Cart coupling

The cart-side interface uses two 760 mm 4040 receiver rails, a master X/Y locator, a secondary Y-only locator, rest pads and four draw latches. The steel locators and positive stops carry shear and yaw; the latches only seat the module and resist uplift. This preserves the project rule that latching is mechanical and not electromagnetic.

### Electrical architecture

The 12 V bus uses one 29 A / 348 W supply, three independent DMD-150 channels and one DC-rated 10 A breaker per actuator branch. The official DMD-150 manual rates each channel at 12 A continuous without added cooling, 15 A with simple cooling and 180 W at 12 V; the public 360 W label is the 24 V value. Mega2560 5 V logic is compatible with its IN1/IN2/PWM interface. A 5 V / 3 A converter powers the controller and IMU. A reachable two-pole AC breaker is the stationary bench disconnect; it is not described as a safety-rated emergency stop.

The same manual warns that lowering or braking can return energy to the DC bus and cause an SMPS overvoltage trip. Motor-terminal bidirectional TVS suppression, controlled PWM ramps and a loaded-lowering bus-voltage test are therefore mandatory release items. The manual cites `1.5KE24CA` as an example, but no exact NAVIMRO-orderable suppression part has yet been released.

The controller can perform initial supervised tests over USB. The purchase package therefore does not require a display or local keypad. Control firmware is not yet designed or released.

## Manufacturing Strategy

- NAVIMRO supplies every purchased material and component in the BOM.
- 4040 profiles are ordered at final length.
- Angle bars and 50 x 6 steel flat bar are saw-cut and drilled locally.
- No welded primary frame is required.
- Hardened 12 mm shafts are clamped in SK12 supports and are not drilled.
- Joint shims are fitted only after the actuator/bracket drawing is received.

## Known False Starts And Corrections

1. DIHOOL DHLA35 200 mm was rejected because its approximately 453 mm retracted length could not fit the height/workspace envelope.
2. The first NAVIMRO control BOM used Cytron MD10C and a genuine Arduino Mega listing, but both showed no dispatch date. DMD-150 and a Mega2560 PRO Type-C board replaced them.
3. Common glass fuse listings were rejected for motor branches because the selected NAVIMRO page explicitly disallowed DC use. A DC-rated Siemens breaker was selected instead.
4. A two-piece BOTECO collar was first found at 28,589 KRW. The geometry-equivalent single-split `Y710028.VBD12` at 16,489 KRW was selected for the low-duty PoC, with holding-force verification retained.
5. The original nested square-tube central guide required more custom stock and fitting. Twin round shafts and commercial bushings reduce fabrication effort and are available in the same order.
6. The public fan and filter pages hide prices behind login. They remain exact selected SKUs but are excluded from the current known-price subtotal.
7. The first procurement list omitted enclosure-installation details. DIN rail, protective-earth wire, crimp terminals and PCB standoffs were added during the completeness pass.
8. The distributor's generic DMD-150 `360 W` description was initially copied into the BOM. The official manual shows 180 W at 12 V and 360 W at 24 V, so the 12 V design record was corrected. The deeper manual review also exposed the previously omitted regeneration/TVS requirement.

## Remaining Gates

1. Receive the vendor documents in `procurement/navimro_preorder_inquiry_2026-08-27.md`.
2. Replace the Firgelli geometry in active CAD with exact DIHOOL STEP and bracket drawings.
3. Re-run all named poses and actuator workspace calculations.
4. Complete joint pin-stack, guide support, Cardan stop and enclosure layout drawings, including DMD-150 cooling and short-lead motor-terminal suppression placement.
5. Freeze cut/drill drawings and then release the single NAVIMRO order.
6. After receipt, measure the non-returnable actuators and build one joint/guide mock-up before assembling the full module.

Until gates 1 through 5 pass, this package is a complete sourcing plan but not a click-to-buy fabrication release.
