# Manual 3-RPS Rev M1 final verification record

## 1. Frozen design basis

- Manual 3-RPS upper leveling/lifting module; no powered actuator or electrical control in the active design.
- Lower and upper profile frames: `700 x 700` envelope.
- Collapsed height: `300 mm`; common Z adjustment target `50 mm`; pitch and roll target `+/-3 deg`.
- Lower/upper support radii: `75 / 250 mm`; support azimuths `90/210/330 deg`.
- Permitted platform motions: Z, pitch, roll. The three radial RPS legs constrain X, Y, and yaw.
- Design leg load `600 N`; total test article mass basis remains 20 kg (10 kg cart estimate plus 10 kg payload), with no people carrying claim.

## 2. Product-image and catalog evidence

The dimensions were not inferred from generic thumbnails. The saved official evidence is under `web_research/evidence/2026-09-01/manual_rev_m1/`.

- THK PHS10: bore10 H7, OD26, ring width14, overall56, centre-to-thread-end43, M10 x1.5, thread depth21, static radial capacity13.2 kN, permissible tilt at least8 deg.
- IMAO BJ775-08040-SUS: diameter8, maximum envelope9.4, grip40 +0.5/0, end allowance8 +/-1, mass42 g; recommended mounting hole `diameter8 +0.1/0`.
- igus JFM-2528-21: ID25, OD28, flange OD35, L21, flange t1.5; housing `28.000..28.021`; shaft `24.948..25.000`.
- NAVIMRO profile/bracket images: DNF4040 slot8.3 +/-0.3; DNF3030 slot6.3 +0.2/0; 4035 envelope40 x40 x35; DCB3025 envelope30 x30 x25.

## 3. Detailed Fusion model

- Native file: `outputs/manual_3rps_rev_m1_fusion_native/Manual_3RPS_RevM1_NATIVE.f3d`.
- Neutral STEP: `outputs/manual_3rps_rev_m1_fusion_native/Manual_3RPS_RevM1_NEUTRAL.step`.
- Native leaf components: 129; neutral STEP solids: 253.
- Functional groups exported separately: lower frame, lower brackets, lower adapters, lower joints, manual struts, upper frame, upper brackets, upper joints, fasteners.
- Every bolt, slot-nut proxy, pivot set, shim, coarse pin, guide, bushing, plug, jam nut, and frame item is positioned in the native assembly.

## 4. Engineering checks

- 27-point workspace sweep: Z `0/25/50`, pitch `-3/0/+3`, roll `-3/0/+3` degrees.
- Required pin-centre range: `219.1426..279.6423`; available manual range `213..303`; margins `6.1426 / 23.3577`.
- Maximum 3-RPS constraint residual: `6.54e-13 mm`.
- Maximum PHS articulation demand: `4.096 deg`, below the catalog minimum permissible `8 deg`.
- PHS10 static-capacity factor at 600 N: `22.0`; conservative M10 engagement factor `13.16`; outer-tube Euler factor `119`; coarse-hole bearing stress `18.75 MPa`.

## 5. Interference and section troubleshooting

Initial Fusion interference run found 20 positive-volume contacts. Review identified four causes:

1. M5 plug retainer intersected the M10 fine-adjustment stud.
2. Upper clevis gap16 was narrower than the modeled PHS10 holder envelope17.
3. A2/A3 upper mounting bolts intersected rotated clevis ears.
4. Slot-nut proxies penetrated profile walls by 0.1 mm.

Corrections moved the retainer, changed the upper gap to20 with two 3 mm shims, widened the upper base to100 with 84 mm mounting pitch, and corrected slot-nut Z. The next run had six contacts because the M5 retainer still touched the JFM flange. The retainer was changed to M4 with 32 mm modeled grip and moved to a 22.5 mm offset. Fusion then returned zero contacts.

During final product-dimension reconciliation, the coarse holes were corrected from `diameter8.2` to the IMAO recommendation `diameter8 +0.1/0`. This affects 21 cross holes across the three struts. All checks were rerun after this change.

## 6. Corrected verification round 1

- Fusion `Design.analyzeInterference`: three passes, 129 leaf occurrences each, zero contacts in every pass, repeatable.
- Fusion section analyses: three A1 sections at X offsets `0/+3/-3`; tube nesting, JFM/guide/plug/stud stack, both clevises, shims, and pivot paths visually inspected.
- Independent CadQuery/OpenCascade STEP audit: envelope `700 x700 x300`; 36 cross-group reports zero; nine within-group reports zero; cross/internal collision counts `0/0`.
- BOM-CAD audit: three passes; 28 BOM rows; all 129 native component names covered; zero uncovered; all quantities matched; no active electrical item; projected budget below 4,000,000 KRW.

## 7. Corrected verification round 2

The unchanged corrected source was regenerated in Fusion and the complete sequence above was repeated.

- Fusion interference passes: `0 / 0 / 0`.
- Fusion section passes: three regenerated images.
- Independent STEP audit: 253 solids, `700 x700 x300`, cross/internal collisions `0 / 0`.
- BOM-CAD passes: three, repeatable, all pass; 129/129 components covered.
- Round 2 results match round 1.

## 8. BOM and budget

- Canonical data: `procurement/manual_rev_m1_bom_data_2026-09-02.json`.
- BOM rows: 28.
- Known VAT-included subtotal: 320,845 KRW.
- Budgetary total including quote allowances: 2,257,845 KRW.
- Remaining against 4,000,000 KRW cap: 1,742,155 KRW.
- Quote/option-selection rows: 13.
- Active BOM excludes actuators, controllers, batteries, sensors, diodes, fuses, and all other powered-control parts. The prior powered architecture remains archived in `design_basis/archived_powered_control_architecture_2026-09-01.md`.

## 9. Verification-tool issue and correction

The first BOM electrical-item scan falsely detected `IMU` inside the word `aluminum`. The scan was corrected from substring matching to alphanumeric word-boundary matching, then all three BOM-CAD passes were rerun successfully. This did not change the BOM or CAD.

## 10. Order-release decision

The design is ready for supplier quotation and one-set trial manufacture, but not for unconditional batch ordering. Release remains on hold until:

- exact BJ775-08040-SUS delivered quote and code confirmation;
- tube stock inspection confirms JFM shaft/housing tolerances are achievable;
- supplier drawings for both shoulder-pin sets and DIN439 M10 thin nuts are accepted;
- one A1 custom-part set is dry-built and measured before the other two sets are finalized.

This record does not claim certification, field safety, or suitability for carrying people.
