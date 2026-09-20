# JNT-CG-01 factory-eye nested-gimbal seed

**STATIC BENCH POC - MEASURED MOCK-UP REQUIRED**

The official Firgelli drawing identifies 8.2 mm front and rear mounting holes and 9/11 mm end-thickness dimensions. A serial HRT8E adapter at both ends was screened first. With a provisional 32 mm extension per end, the worst effective actuator pin length becomes 281.14 mm, below the 319 mm catalogue endpoint, so that topology is rejected for the current geometry.

JNT-CG-01 keeps both rotational axes at the factory pin centre. A 12 mm inner-cradle gap receives the measured factory eye; the factory M8 pin supplies one axis and two opposed M8 shoulder-screw trunnions supply the orthogonal axis without a second crossing through-pin.

| Item | Preliminary result |
|---|---:|
| Active axial design force | 876.4 N |
| Factory hole | 8.2 mm |
| Adjustable mock-up eye-gap range reference | 9 to 11 mm |
| Plate thickness | 6 mm |
| Trunnion supported span | 22 mm |
| M8 pin double shear | 8.72 MPa |
| M8 pin bending | 95.89 MPa |
| Lug bearing | 18.26 MPa |

The family drawing confirms an 8.2 mm hole and 20 mm eye OD, but it is the 220 lbf 2-inch drawing rather than the selected 450 lbf 8-inch model. The 9/11 mm local dimensions are used only to bracket an adjustable mock-up gap. The standalone STEP is `outputs/cad/step/jnt_cg01_factory_clevis_gimbal_seed.step`. Root attachment holes, fits, welds, shoulder-screw engagement and purchased-part sweep are intentionally not released. Replace the mock-up gap with caliper measurements from the purchased actuator before producing six joints.
