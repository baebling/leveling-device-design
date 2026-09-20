# JNT-CG-01 factory-eye nested-gimbal seed

Status: `MEASURED_MOCKUP_SEED - NOT APPROVED FOR FABRICATION`

## Why the joint changed

The selected Firgelli actuator has integral 8.2 mm mounting holes at both ends. The archived family drawing also shows a 20 mm eye OD, but it is for the 220 lbf 2-inch model and is not a selected-model fabrication drawing. A serial clevis-to-HRT8E adapter was screened with a provisional 32 mm extension at each end. At the worst +/-3 degree position, the effective actuator pin distance falls below the 319 mm catalogue retracted length, so the serial topology is rejected for the current support geometry.

JNT-CG-01 keeps the actuator mounting-hole centre as the kinematic centre. The factory M8 pin supplies the first rotation axis. Two opposed M8 shoulder-screw trunnions on an inner cradle supply the orthogonal axis. The trunnions are opposed stubs and do not cross the factory through-pin.

## Preliminary seed

| Parameter | Value |
|---|---:|
| Factory mounting hole | 8.2 mm |
| Adjustable mock-up gap reference | 9 to 11 mm |
| Inner cradle gap seed | 12 mm, measure before machining |
| Plate thickness | 6 mm |
| Factory pin | M8 envelope |
| Opposed trunnions | M8 shoulder-screw envelopes |
| Trunnion supported span | 22 mm |
| Kinematic centre offset | 0 mm |

At the active low-load design force of about 876 N, the preliminary M8 pin screen gives about 8.72 MPa double-shear stress, 95.9 MPa bending stress and 18.3 MPa lug bearing stress. These values select a mock-up topology only; they do not size fatigue, welds, threads or root attachment.

## CAD output

- `outputs/cad/step/jnt_cg01_factory_clevis_gimbal_seed.step`
- `outputs/renders/jnt_cg01_factory_clevis_gimbal.png`

The STEP intentionally has no final root holes, fits, weld symbols or shoulder-screw thread depth.

## Required measurement sequence

1. Measure the purchased front and rear eye thickness at three positions.
2. Measure the supplied pin diameter, shoulder length and retained stack.
3. Print or machine one inner cradle with adjustable shim washers.
4. Sweep both axes to at least the calculated requirement while checking actuator-housing contact.
5. Load one joint statically before copying it to the other five locations.

Official drawing reference: https://www.firgelliauto.com/products/super-duty-actuators
