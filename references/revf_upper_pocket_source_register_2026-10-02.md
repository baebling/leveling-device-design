# Rev F upper pocket supplier source register

Checked: **2026-10-02**. Preliminary screening baseline, **NOT APPROVED FOR FABRICATION**.
Scope: 3 factory-finished upper brackets, existing A1–A3 plate machining allowed.
Supervised no-cart/no-payload/no-person self-weight PoC only. No independent
mechanical stopper per current approved spec; this remains an explicit deviation,
not proof that electrical limits provide mechanical protection.

## Source dimensions and unresolved evidence

All dimensions are mm. UNKNOWN means missing evidence, never zero or a guessed
nominal value. The executable baseline and source paths are centralized in
`cad/revf_upper_pocket_inputs.py`. Confirmation date below means the source was
opened or attempted today, not the delivered part was measured.

| Item / exact source identity | Dimension / tolerance | Source and verification on 2026-10-02 | Consequence / gate |
|---|---|---|---|
| LM4075OE-1075, supplied 100 mm STEP | Front eye bore nominal Ø6.0; delivered bore tolerance UNKNOWN; prior OCCT front eye width 20.0000002 | [Local supplied STEP](vendor_cad/LM4075OE-1075-100mm.stp), reread cylinder radius 3 records; [existing OCCT front-eye identification](../outputs/20261001_reve_bom_audit/후속검토_기구전장함체_2026-10-01.md) | STEP is geometry, not a delivered tolerance certificate |
| LM4075OE-1075 sales drawing | `2×Ø6.4`, no bore tolerance shown | [Exact current product](https://www.motorbank.kr/goods/goods_view.php?goodsNo=1000035578) reopened; [archived sales drawing](../web_research/evidence/2026-08-31/LM4075OE_detail_source_900x1530.jpg) visually reopened | **Separate source boundary Ø6.4**, not an upper manufacturing tolerance on Ø6.0. Screen both 6.0 and 6.4; supplier reconciliation and delivered measurement UNKNOWN |
| TRUSCO PHS6, drawing dated 2004/4/24 | Housing head Ø20; housing/race axial width 6.75; ball width 9 (+0/−0.12); bore Ø6 (+0.012/0); M6 straight thread length 12; head center to base 30; overall 40; indicated angle 13° | [Manufacturer drawing](https://image.trusco-sterra2.com/pdf/zumen/PHS6_4500__ZM.pdf) downloaded, rendered, visually inspected today | Outer Ø20 and width 6.75 tolerances UNKNOWN. 6.75 is housing/race width, not the movable ball's 9 width. Preserve spherical freedom and lubrication access |
| BOM label THK PHS6 vs TRUSCO PHS6 | Exact order equivalence **UNKNOWN** | [Legacy THK catalog](../web_research/evidence/2026-08-31/THK_PHS_catalog_en_a23_006.pdf); current [TRUSCO seller route](https://jp.misumi-ec.com/vona2/detail/221005504380/?HissuCode=PHS6) attempted, returned generic catalogue | Common PHS6 text does not prove manufacturer, supplied product or strength equivalence. No silent THK→TRUSCO substitution |
| MISUMI MSB6-35 / MSB6-LC31 candidates | D e9: −0.020/−0.050, minimum diameter 5.95; L=35 or LC=31 nominal; LC ±0.05; SCM435, 33–38 HRC, strength class 10.9 | [Official 2018 drawing](https://kr.misumi-ec.com/pdf/press/2018_pr_1011.pdf) reopened after initial timeout; [exact MSB6-35](https://kr.misumi-ec.com/vona2/detail/110100143940/?HissuCode=MSB6-35) reopened | Continuous smooth shoulder contact length **UNKNOWN**; head-under fillet and thread-transition contact exclusion **UNKNOWN**. Nominal L is not guaranteed usable bearing length. Candidate order and guaranteed shoulder proof strength remain open |
| DNF3030 extrusion | Nominal envelope 30×30; historical slot opening 6.3, lip depth 2.5, floor depth 10.5; delivered section and slot tolerances **UNKNOWN** | [Manufacturer listing](https://www.dycprofile.co.kr/3030%EC%8B%9C%EB%A6%AC%EC%A6%88/715834) attempted (timeout); [current seller](https://alsw.co.kr/goods/goods_view.php?goodsNo=1000000079) reopened; linked PDF download returned HTML, not a valid PDF; [prior section evidence](../outputs/20261002_reve_followthrough/연속검증_중간기록.md) | `profile_slot_width_mm=None`, `profile_slot_verified=False`. Do not treat historical nominal section as current delivered compatibility. Lip contact, T-nut seating and clamp path unresolved |
| Existing F07 K14671215, SP306 candidate, 30-series M6 | Seller drawing SP306: 23×10×5 body; M6 thread. Dimensional tolerances, effective engagement, torque and permitted loads **UNKNOWN** | [Current exact seller SKU](https://www.navimro.com/p/K14671215/) reopened; [seller drawing](https://img.navimro.com/img/pi/detail/1171730.jpg) downloaded and visually inspected today | This is a seller-hosted technical drawing, not a verified manufacturer-controlled drawing for the delivered nut. Rev F selection remains UNKNOWN; do not infer compatibility from “30-series” or M6. Existing F07 is not automatically selected |
| Existing eye-to-ball eccentricity | e=16 nominal along fixed lower hinge tangent pin axis | [Approved spec](../docs/superpowers/specs/2026-10-02-upper-pocket-bracket-design.md), corrected Rev E geometry | Assembly model input, not supplier tolerance. New pocket changing center or contact location invalidates reuse of old kinematics |

No fresh price, lead time, stock or manufacturing acceptance is asserted here.
The historical profile and T-nut numbers are recorded for traceability only and
are not substituted for missing verified values in the executable interface.

## Downstream contract and uncertainty

`load_inputs()` returns 3 brackets, eye bounds `(6.0, 6.4)`, minimum pin 5.95,
e=16, housing Ø20×6.75 and ball width 9. Unknown continuous shoulder length and
verified profile slot width are `None`. `source_complete()` requires positive
finite dimensions, ordered eye bounds, three brackets, verified profile section,
and an empty explicit required-evidence gap list. This checks source completion
only; an artificially complete test fixture does not constitute real evidence.
Missing tolerances and order identity must stay in that list until independently
reviewed evidence resolves them.

The eye disagreement changes diametral clearance and contact distribution; with
minimum pin 5.95 the nominal source-boundary clearances are 0.05 and 0.45. These
are screening values, **not delivered worst-case clearances** because eye
tolerances are UNKNOWN. Any resulting pocket/contact differences permit only
both-boundary screening. Stop fabrication-dimension freezing.

Coordinates: lower center origin, +X right, +Y forward, +Z up; roll about X,
pitch about Y. Required Z=0–50, simultaneous pitch/roll ±3°; constrain X/Y/yaw
mechanically. Static screening uses ±750 N along each actuator axis, both signs,
and adverse simultaneous combinations; target minimum verified yield/proof SF
≥1.5. `M=F e=12,000 N·mm`, `σb=32M/(πd³)` is a pin-only simplified model,
not a complete joint qualification. Tolerances, real contact, fillets, actuator
eye reactions, profile lip and T-nut clamp path must be resolved separately.

`PURCHASE_RELEASE = FABRICATION_RELEASE = CONTROL_POWER_TEST_RELEASE =
MOTOR_POWER_RELEASE = FALSE`. Completing sources cannot turn any release on.
No certification, field safety, fatigue or suitability for people is claimed.
