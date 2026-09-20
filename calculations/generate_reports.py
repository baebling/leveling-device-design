import csv
import json
from pathlib import Path

from cad.guide_mechanism import overlap_mm
from cad.parameters import P, ROOT
from calculations.actuator_force import summary as force_summary
from calculations.interface_loads import acrylic_strip_screening, latch_and_pin_screening
from calculations.kinematics import platform_corner_heights, summary as kinematic_summary
from calculations.sensitivity_analysis import angle_sensitivity
from calculations.actuator_limit_package_screen import summary as actuator_limit_summary
from calculations.factory_clevis_gimbal_screen import summary as factory_clevis_gimbal_summary
from cad.parameters import POSES


SOURCES = {
    "firgelli": "https://www.firgelliauto.com/products/super-duty-actuators?variant=39956755316807",
    "timotion": "https://www.timotion.com/kr/products/linear-actuators/ta2p-series",
    "timotion_kr": "https://pre.timotion.com/kr/contact/china",
    "misumi": "https://us.misumi-ec.com/pdf/fa/2010/p2315.pdf",
    "destaco": "https://www.destaco.com/toggle-lock/product/323-R",
    "plexiglas": "https://www.plexiglas.de/files/plexiglas-content/pdf/technische-informationen/211-1-PLEXIGLAS-GS-XT-EN.pdf",
    "arduino": "https://store.arduino.cc/products/arduino-mega-2560-rev3",
    "cytron": "https://www.cytron.io/p-13amp-6v-30v-dc-motor-driver",
    "bno085": "https://www.adafruit.com/product/4754",
    "omron": "https://automation.omron.com/en/ca/products/family/A22E-Estop",
    "meanwell": "https://www.meanwell.com/Upload/PDF/LRS-350/LRS-350-SPEC.PDF",
    "hrt8e": "https://product.minebeamitsumi.com/en/product/category/bearing/rodend/standard/parts/HRTE.html",
    "d4n": "https://www.ia.omron.com/product/item/10697/",
    "collar": "https://www.ruland.com/msp-12-fz.html",
    "mb21": "https://www.firgelliauto.com/products/mb-21-bracket-for-super-duty-actuators",
}


BOM = [
    ["A-001", 3, "Firgelli F-SD-H-450-12V-8in Hall actuator", "purchased", "450 lbf, 203.2 mm stroke, 319-523 mm pin length", "USD", 159.95, SOURCES["firgelli"], "Exact variant stock/shipping to Korea verify at checkout"],
    ["F-001", 1, "HFS8-4040 aluminum extrusion cut set", "purchased_cut", "A6005CSS-T5 equivalent; final cut list after interface measurement", "QUOTE", "", SOURCES["misumi"], "Supplier quote required"],
    ["F-002", 1, "Lower universal plate 900x800x8", "fabricated", "6061-T6 aluminum; waterjet/CNC", "QUOTE", "", "", "Primary load-transfer part; no acrylic substitution"],
    ["F-003", 1, "Upper panel 900x800x15", "fabricated", "Cast PMMA/PLEXIGLAS GS equivalent", "QUOTE", "", SOURCES["plexiglas"], "Panel only; use aluminum spreaders"],
    ["G-001", 1, "50x50x3 / 42x42x3 keyed telescopic guide set", "fabricated", "Aluminum tubes, UHMW shims, independent mechanical stops", "QUOTE", "", "", "Keep >=80 mm overlap; prototype load only"],
    ["G-002", 1, "Compact two-axis Cardan constraint head", "fabricated", "120 mm mount envelope; 12 mm pin seed; +/-7 deg stop per pitch/roll axis", "QUOTE", "", "", "Secondary X/Y/yaw constraint only; keep visually subordinate to radial actuators"],
    ["G-003", 12, "Ruland MSP-12-FZ or equivalent steel stop collar", "purchased", "12 mm bore; 28 mm OD; 11 mm width; two-piece clamp", "USD", 15.36, SOURCES["collar"], "Four per actuator; axial push-off and impact acceptance still require test"],
    ["G-005", 3, "LS-01M twin-rod mechanical limiter cassette", "fabricated", "2x 12x320 mm moving rods; MB21-derived fixed carrier; keyed moving crosshead; four stop collars", "QUOTE", "", "", "Static-bench variant uses actuator internal limits; collar push-off still requires physical mock-up"],
    ["G-006", 3, "Firgelli MB21 fixed body bracket", "purchased", "Official STEP envelope 50x82.854x100 mm; fixed-position body support", "QUOTE", "", SOURCES["mb21"], "Vendor acceptance of external stop reaction is not established"],
    ["L-001", 4, "DESTACO 323-R pull-action latch", "purchased", "360 lbf holding capacity; Toggle Lock Plus", "QUOTE", "", SOURCES["destaco"], "Mechanical latch; guide pins carry shear"],
    ["C-001", 1, "Arduino Mega 2560 Rev3", "purchased", "Prototype supervisory controller", "EUR", 52.80, SOURCES["arduino"], "Prototype only, not safety-rated"],
    ["C-002", 3, "Cytron MD13S motor driver", "purchased", "6-30 V, 13 A continuous", "USD", 15.30, SOURCES["cytron"], "One driver per actuator"],
    ["C-003", 1, "Adafruit BNO085 IMU breakout", "purchased", "9-DOF absolute orientation sensor", "USD", 24.95, SOURCES["bno085"], "Prototype leveling feedback"],
    ["C-004", 1, "Mean Well LRS-350-12 power supply", "purchased", "12 V, 29 A, 348 W", "QUOTE", "", SOURCES["meanwell"], "Bench supply only; mains integration by qualified person"],
    ["J-006", 6, "JNT-CG-01 nested factory-eye gimbal mock-up", "fabricated", "6 mm inner cradle and outer yoke; M8 factory pin; opposed M8 trunnions", "QUOTE", "", "", "Measured mock-up seed only; actual eye width pin stack sweep and root attachment remain open"],
]


def _fmt(value, digits=2):
    return f"{value:.{digits}f}"


def write_bom(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "phase2_bom.csv"
    headers = ["item", "qty", "description", "make_buy", "specification", "currency", "unit_price_observed_2026-08-23", "official_source", "procurement_note"]
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(BOM)
    usd = sum(float(row[6]) * row[1] for row in BOM if row[5] == "USD" and row[6] != "")
    eur = sum(float(row[6]) * row[1] for row in BOM if row[5] == "EUR" and row[6] != "")
    md = [
        "# Phase 2 preliminary BOM", "", "**PRELIMINARY — NOT APPROVED FOR FABRICATION**", "",
        f"공식 판매 페이지에서 가격을 확인할 수 있었던 항목의 부분합은 **USD {usd:.2f} + EUR {eur:.2f}**입니다. 구조재, 가공품, 래치, 전원장치, 세금·배송비는 견적 대상이므로 이 값은 총사업비가 아닙니다.", "",
        "| Item | Qty | Description | Unit price | Source / note |", "|---|---:|---|---:|---|",
    ]
    for row in BOM:
        price = f"{row[5]} {row[6]}" if row[6] != "" else "QUOTE"
        source = f"[official]({row[7]})" if row[7] else row[8]
        md.append(f"| {row[0]} | {row[1]} | {row[2]} | {price} | {source} |")
    (output_dir / "phase2_bom.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return csv_path


def write_reports(root: Path = ROOT):
    out = root / "outputs" / "phase2"
    calc_dir = root / "outputs" / "calculations"
    out.mkdir(parents=True, exist_ok=True)
    calc_dir.mkdir(parents=True, exist_ok=True)
    kin = kinematic_summary()
    force = force_summary()
    sensitivity = angle_sensitivity()
    latch = latch_and_pin_screening()
    acrylic_250 = acrylic_strip_screening(250, 100, 15, 240)
    acrylic_500 = acrylic_strip_screening(500, 100, 15, 240)
    acrylic_long = acrylic_strip_screening(250, 100, 15, 800)
    envelope = platform_corner_heights(POSES["max_pitch_roll"])
    actuator_limit = actuator_limit_summary()
    factory_gimbal = factory_clevis_gimbal_summary()
    results = {
        "kinematics": kin, "force": force, "angle_sensitivity": sensitivity,
        "latch_interface": latch, "acrylic_250N_240mm": acrylic_250,
        "acrylic_500N_240mm": acrylic_500, "acrylic_250N_800mm": acrylic_long,
        "inclined_tripod_geometry": {
            "upper_joint_radius_mm": P.support_radius_mm,
            "lower_joint_radius_mm": P.base_support_radius_mm,
            "horizontal_offset_mm": P.actuator_horizontal_offset_mm,
            "collapsed_vertical_separation_mm": P.actuator_vertical_separation_collapsed_mm,
            "collapsed_incline_from_horizontal_deg": P.actuator_incline_from_horizontal_deg,
        },
        "guide_overlap_collapsed_mm": overlap_mm(P.platform_joint_z_collapsed_mm),
        "guide_overlap_raised_mm": overlap_mm(P.platform_joint_z_collapsed_mm + P.target_lift_mm),
        "max_pitch_roll_corner_height_range_mm": [min(envelope), max(envelope)],
        "actuator_limit_package": actuator_limit,
        "factory_clevis_gimbal": factory_gimbal,
    }
    (calc_dir / "phase2_results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    engineering = f"""# Phase 2 preliminary engineering report

**PRELIMINARY — NOT APPROVED FOR FABRICATION — 사람 운송용이 아님**

## 결론

권장 구조는 **중앙에서 외곽으로 펼쳐지는 방사형 사선 액추에이터 3개**와 중앙 키드 텔레스코픽 가이드/2축 Cardan 헤드를 조합한 inclined tripod입니다. 상·하부 관절 삼각형의 방향을 같게 하여 축력을 방사형으로 만들었으므로, 꼬임형 배치보다 yaw 토크가 작고 세 브래킷을 동일 형상으로 제작할 수 있습니다. 허용 자유도는 Z, pitch, roll이며 중앙 사각 가이드가 X, Y, yaw를 기계적으로 구속합니다.

온라인 구매 가능한 Firgelli 8-inch 액추에이터를 접힘 상태에서 수평 기준 약 **{P.actuator_incline_from_horizontal_deg:.1f}°**로 눕히면 승인된 WS-01-H20 접힘 높이 **{P.commercial_collapsed_height_mm:.0f} mm**를 만족합니다. 중립 높이는 {P.commercial_neutral_height_mm:.0f} mm, 완전 상승 높이는 {P.commercial_raised_height_mm:.0f} mm입니다. 이 값은 수평 자세의 장치 높이이며 기울기 시 높은 모서리의 절대 높이는 별도로 증가합니다.

## 좌표계와 운동학

- 원점: 하부 인터페이스 판 중앙; +X 전방, +Y 좌측, +Z 상향
- 회전 순서: roll(+X) 후 pitch(+Y)
- 상부 관절 위치: `p_i = R_y(pitch) R_x(roll) [x_i,y_i,0]^T + [0,0,z_c]^T`
- 액추에이터 길이: `L_i = ||p_i - b_i||`
- 상부 관절 반경: {P.support_radius_mm:.1f} mm; A1(400,0), A2(-200,346.4), A3(-200,-346.4)
- 하부 관절 반경: {P.base_support_radius_mm:.1f} mm; 수평 오프셋 {P.actuator_horizontal_offset_mm:.1f} mm
- 접힘 수직 관절간격: {P.actuator_vertical_separation_collapsed_mm:.1f} mm; 레벨 액추에이터 길이 {P.actuator_level_length_at_lift0_mm:.1f} mm

±3°/Z=0…100 mm 코너 그리드에서 길이는 **{kin['minimum_length_mm']:.2f}…{kin['maximum_length_mm']:.2f} mm**, 필요 범위 {kin['required_span_mm']:.2f} mm입니다. 선정 액추에이터에 대한 최소단 여유 {kin['retracted_margin_mm']:.2f} mm, 최대단 여유 {kin['extended_margin_mm']:.2f} mm로 예비 통과했습니다. 기계식 스톱은 전기 리미트와 독립적으로 설치합니다.

## 하중 스크리닝

10 kg 탑재물 + 22 kg 이동구조, 1.5 동적계수, 안전계수 2.0, 무편심 조합에서 사선 방향코사인을 포함한 최대 축력은 **{force['worst_case']['max_compression_n']:.1f} N**입니다. 450 lbf({P.actuator_dynamic_force_n:.1f} N) 정격에 대한 예비 여유는 {force['rating_margin_n']:.1f} N입니다. 설계 입력은 무편심이지만 별도 결과 JSON에 50/100 mm 편심 민감도를 기록했습니다.

본 계산은 축방향 정적 평형입니다. 핀 베어링/전단, 브래킷 굽힘, 액추에이터 좌굴, 프레임 국부응력, 가속 충격, 피로, 제어 오차는 상세 검증 전까지 미해결입니다.

## 중앙 가이드와 인터페이스

- 50x50x3 외관 / 42x42x3 내관, UHMW 간극 패드(5–10 kg PoC 전용 예비 크기)
- 계산 겹침: 접힘 {results['guide_overlap_collapsed_mm']:.1f} mm, 상승 {results['guide_overlap_raised_mm']:.1f} mm (최소 요구 {P.guide_min_overlap_mm:.0f} mm)
- Gimbal 설계 포락선 {P.cardan_design_angle_deg:.0f}°, 축별 독립 스토퍼 ±{P.gimbal_pin_stop_angle_deg:.0f}°, 대각 총 기울기 <{P.cardan_hard_stop_angle_deg:.0f}°
- 카트 결합: 원뿔형 가이드 핀이 X/Y/yaw 전단과 위치결정을 담당하고 4개 기계식 래치가 인장/클램프를 담당합니다. 전자석은 사용하지 않습니다.
- 카트측 치수는 이미지에서 추정하지 않았으며 CAD의 650x500 mm 리시버는 인터페이스 검토용 매개변수 더미입니다.

## 민감도

| 각도 | 최소 길이 | 최대 길이 | 필요 범위 | 판정 |
|---:|---:|---:|---:|---|
"""
    for row in sensitivity:
        engineering += f"| ±{row['angle_deg']:.0f}° | {row['minimum_length_mm']:.1f} | {row['maximum_length_mm']:.1f} | {row['required_span_mm']:.1f} | {'PASS' if row['passes_commercial_actuator'] else 'FAIL'} |\n"
    engineering += f"""

±5°는 액추에이터 스트로크 민감도상 통과하지만 조인트 각도·프레임 간섭·제어 안정성을 아직 승인하지 않았으므로 기본 성능은 ±3°로 유지합니다. ±8°는 최소길이 여유가 부족하여 실패합니다. 최대 pitch+roll/완전상승 상태의 상판 외곽 높이 범위는 약 {min(envelope):.1f}…{max(envelope):.1f} mm입니다.

## 미확정 입력과 다음 단계

실제 카트 인터페이스 도면, 탑재물 질량중심/체결 패턴, 허용 처짐, 운행 가속도/충격 스펙트럼, 사용 주기, 전원 방식, 환경 등급, 핀/베어링 재질이 필요합니다. 이 입력을 고정한 뒤 상세 공차, 체결부 계산, FEA 및 제작도면 승인을 진행해야 합니다.
"""
    (out / "phase2_engineering_report.md").write_text(engineering, encoding="utf-8")

    decision = f"""# 사선 액추에이터 구조 선정

**선정안: 바깥방향 방사형 inclined tripod**

사용자 입력은 900×800 mm 평면, 연결 전 높이 250–300 mm 범위, 승인 기준 접힘 높이 270 mm, 탑재 10 kg, 관절 배치 자유, 제작 용이성 우선입니다.

| 대안 | 제작 난도 | 안정성/하중경로 | 250 mm 접힘 | 결론 |
|---|---|---|---|---|
| 방사형 사선 3점 | 낮음–중간 | 세 축의 횡력이 중심에서 상쇄되고 동일 브래킷 3개 사용 | 가능 | **선정** |
| 상·하부 삼각형을 비튼 twisted tripod | 중간 | 시각적으로 좋지만 중앙 가이드에 상시 yaw 토크 발생 | 가능 | 제외 |
| 수평 액추에이터+벨크랭크 | 높음 | 낮게 만들 수 있으나 핀·베어링·백래시·부품수 증가 | 가능 | 향후 대안 |
| 3개 소형 시저리프트 | 높음 | Z에는 유리하나 pitch/roll 동기화와 유격 관리가 어려움 | 조건부 | 제외 |

## 확정 기하

- 상부 관절: 반경 {P.support_radius_mm:.1f} mm의 정삼각형
- 하부 관절: 반경 {P.base_support_radius_mm:.1f} mm의 정삼각형
- 액추에이터 수평 오프셋: {P.actuator_horizontal_offset_mm:.1f} mm
- 접힘 수직 간격: {P.actuator_vertical_separation_collapsed_mm:.1f} mm
- 접힘 액추에이터 길이: {P.actuator_level_length_at_lift0_mm:.1f} mm
- 접힘 각도: 수평 기준 {P.actuator_incline_from_horizontal_deg:.1f}°
- 수평 접힘/중립/상승 높이: {P.commercial_collapsed_height_mm:.0f}/{P.commercial_neutral_height_mm:.0f}/{P.commercial_raised_height_mm:.0f} mm

세 액추에이터의 하단을 중앙 근처에 배치하고 상단을 상판 외곽으로 펼칩니다. 각 클레비스 핀은 원주 접선방향이므로 액추에이터가 방사형 수직면 안에서 회전할 수 있습니다. 중앙 키드 가이드가 X/Y/yaw를 담당하며 액추에이터는 Z/pitch/roll 구동에 집중합니다.

## 제작 주의점

하부 관절 중심 간격이 약 {3 ** 0.5 * P.base_support_radius_mm:.1f} mm이므로 중앙 가이드, 클레비스 측판, 액추에이터 모터 하우징의 실제 STEP 조립 검토가 필요합니다. 현재 CAD는 제조사 외형을 단순화한 운동 포락체이며 브래킷 공차·핀 베어링 계산 전에는 제작할 수 없습니다.
"""
    (out / "diagonal_design_decision.md").write_text(decision, encoding="utf-8")

    positions = actuator_limit["positions"]
    vendor_datum = actuator_limit["vendor_mount_datum"]
    stop_screen = actuator_limit["static_screen"]
    switch = actuator_limit["switch_candidate"]
    limit_report = f"""# LS-01 actuator limit package summary

**PRELIMINARY - NOT APPROVED FOR FABRICATION**

LS-01M is the user-requested static-bench simplification. Each actuator keeps a symmetric twin-rod moving striker, an MB21-derived fixed guide/stop carrier and four mechanical shaft collars. The external D4N switches, trip cams and slotted switch brackets are omitted from the active CAD and BOM. Electrical end interruption relies on the actuator's built-in non-adjustable limits; the external collars remain the independent mechanical path.

| Item | Preliminary value |
|---|---:|
| Fixed carrier station from lower pin | {positions['fixed_guide_station_from_base_pin_mm']:.0f} mm |
| Moving crosshead offset from upper pin | {positions['moving_crosshead_offset_from_top_pin_mm']:.0f} mm |
| Lower mechanical / electrical offsets | {positions['lower_mechanical_collar_offset_from_crosshead_mm']:.0f} / {positions['lower_electrical_cam_offset_from_crosshead_mm']:.0f} mm |
| Upper electrical / mechanical offsets | {positions['upper_electrical_cam_offset_from_crosshead_mm']:.0f} / {positions['upper_mechanical_collar_offset_from_crosshead_mm']:.0f} mm |
| Electrical-to-mechanical allowance | {positions['electrical_to_mechanical_allowance_lower_mm']:.0f} mm each direction |
| Static package reference load | {stop_screen['design_package_static_load_n']:.1f} N |
| Equal-share load per 12 mm rod | {stop_screen['equal_share_load_per_rod_n']:.1f} N |
| Rod axial stress screen | {stop_screen['guide_rod_axial_stress_mpa']:.2f} MPa |
| Collar-face average contact screen | {stop_screen['collar_face_contact_pressure_mpa']:.2f} MPa |
| Minimum verified axial holding target per collar | {stop_screen['minimum_verified_axial_holding_per_collar_n']:.1f} N |
| MB21 official STEP envelope | {vendor_datum['mb21_envelope_mm'][0]:.0f} x {vendor_datum['mb21_envelope_mm'][1]:.3f} x {vendor_datum['mb21_envelope_mm'][2]:.0f} mm |
| MB21 axial range from rear pin | {vendor_datum['mb21_axial_range_from_rear_pin_mm'][0]:.0f} to {vendor_datum['mb21_axial_range_from_rear_pin_mm'][1]:.0f} mm |
| Remaining source-STEP body reserve | {vendor_datum['far_end_reserve_mm']:.2f} mm minimum |

The D4N package remains archived as a future upgrade if the module becomes mobile, unattended, higher-speed or subject to a formal safety review. It is not in the current purchase BOM.

The fixed datum now follows the official MB21 body-bracket envelope, and the moving datum is the official front clevis pin centre. The moving crosshead must capture a clevis adapter with keyed faces and may not clamp the chrome rod. The STEP-derived fit does not establish Firgelli acceptance of external stop reaction.

This package is statically screened only. Collar push-off, fixed-carrier attachment, actuator-housing acceptance, JNT-CG-01 measured fit, one-rod load concentration, impact energy, fatigue and cable routing require physical evidence before any fabrication approval.
"""
    (out / "actuator_limit_package_summary.md").write_text(limit_report, encoding="utf-8")

    gimbal = factory_gimbal["nested_gimbal"]
    serial = factory_gimbal["serial_adapter"]
    gimbal_report = f"""# JNT-CG-01 factory-eye nested-gimbal seed

**STATIC BENCH POC - MEASURED MOCK-UP REQUIRED**

The official Firgelli drawing identifies 8.2 mm front and rear mounting holes and 9/11 mm end-thickness dimensions. A serial HRT8E adapter at both ends was screened first. With a provisional {serial['assumed_extension_each_end_mm']:.0f} mm extension per end, the worst effective actuator pin length becomes {serial['effective_minimum_actuator_pin_length_mm']:.2f} mm, below the {serial['catalog_retracted_length_mm']:.0f} mm catalogue endpoint, so that topology is rejected for the current geometry.

JNT-CG-01 keeps both rotational axes at the factory pin centre. A 12 mm inner-cradle gap receives the measured factory eye; the factory M8 pin supplies one axis and two opposed M8 shoulder-screw trunnions supply the orthogonal axis without a second crossing through-pin.

| Item | Preliminary result |
|---|---:|
| Active axial design force | {gimbal['design_force_n']:.1f} N |
| Factory hole | {gimbal['factory_hole_mm']:.1f} mm |
| Adjustable mock-up eye-gap range reference | {gimbal['factory_eye_width_mockup_range_mm'][0]:.0f} to {gimbal['factory_eye_width_mockup_range_mm'][1]:.0f} mm |
| Plate thickness | {gimbal['plate_thickness_mm']:.0f} mm |
| Trunnion supported span | {gimbal['trunnion_supported_span_mm']:.0f} mm |
| M8 pin double shear | {gimbal['pin_double_shear_mpa']:.2f} MPa |
| M8 pin bending | {gimbal['pin_bending_mpa']:.2f} MPa |
| Lug bearing | {gimbal['lug_bearing_mpa']:.2f} MPa |

The family drawing confirms an 8.2 mm hole and 20 mm eye OD, but it is the 220 lbf 2-inch drawing rather than the selected 450 lbf 8-inch model. The 9/11 mm local dimensions are used only to bracket an adjustable mock-up gap. The standalone STEP is `outputs/cad/step/jnt_cg01_factory_clevis_gimbal_seed.step`. Root attachment holes, fits, welds, shoulder-screw engagement and purchased-part sweep are intentionally not released. Replace the mock-up gap with caliper measurements from the purchased actuator before producing six joints.
"""
    (out / "factory_clevis_gimbal_summary.md").write_text(gimbal_report, encoding="utf-8")

    acrylic = f"""# 아크릴 적용성 검토

**결론: 전체 하중구조를 아크릴로 만드는 안은 권장하지 않으며, 알루미늄 골격 + 주조 아크릴 상판/커버의 하이브리드를 권장합니다.**

PLEXIGLAS GS 공식 자료의 대표값은 밀도 1.19 g/cm³, 인장강도 80 MPa, 굽힘강도 115 MPa, 탄성계수 3300 MPa입니다. 그러나 제조사가 장기 안전응력을 40°C 이하에서 대략 5–10 MPa로 제시하며 노치 충격과 응력집중에 민감하므로, 단기 파단강도를 구조 허용응력으로 사용하면 안 됩니다.

100 mm 폭 × 15 mm 두께, 240 mm 지지간격의 단순지지 스트립 중앙하중 스크리닝:

| 하중 | 굽힘응력 | 중앙 처짐 | 5 MPa 기준 |
|---:|---:|---:|---|
| 250 N | {acrylic_250['stress_mpa']:.2f} MPa | {acrylic_250['deflection_mm']:.2f} mm | 경계 통과 |
| 500 N | {acrylic_500['stress_mpa']:.2f} MPa | {acrylic_500['deflection_mm']:.2f} mm | 실패 |
| 250 N, 800 mm span | {acrylic_long['stress_mpa']:.2f} MPa | {acrylic_long['deflection_mm']:.2f} mm | 실패 |

따라서 15 mm 주조 아크릴 상판은 프레임 지지간격을 240 mm 수준으로 유지하고, 모든 액추에이터·Cardan·탑재물 체결점 아래에 알루미늄 하중분산판을 두는 비주요 패널로만 사용합니다. 하부 범용판, 클레비스, 핀, 래치 키퍼, 중앙 가이드 및 기계식 스톱은 금속이어야 합니다. 레이저가공 모서리는 연마/라운딩하고 볼트 구멍은 큰 와셔·부싱과 여유공을 사용하며, 나사산을 아크릴에 직접 내지 않습니다.

주조 아크릴 위주의 축소 전시형은 탑재 5 kg 이하, 승강 50 mm 이하, 실제 운행 카트 미탑재 조건에서만 별도 검토할 수 있습니다. 이 경우에도 관절과 안전스톱은 금속을 유지합니다.
"""
    (out / "acrylic_feasibility.md").write_text(acrylic, encoding="utf-8")

    procurement = f"""# 구매 가능 부품 조사

확인일: 2026-08-23. 가격·재고·배송 가능 여부는 변동하므로 발주 직전 공식 판매처에서 재확인해야 합니다.

## 권장 액추에이터

- [Firgelli Super Duty Hall actuator]({SOURCES['firgelli']}): F-SD-H-450-12V-8in 구성, 450 lbf, 203.2 mm stroke, 319/523 mm retract/extend, 12 V, 최대 5.5 A, 무부하 6 mm/s, 25% duty, IP66, Hall 41.1 pulses/mm. 8.2 mm 양단 clevis와 internal non-adjustable limits를 사용한다.
- [Firgelli MB21 body bracket]({SOURCES['mb21']}): Super Duty 본체에 직접 고정하는 fixed-position support다. 공식 STEP를 보관하고 LS-01 고정 datum의 포락체로 사용했지만, 외부 stop reaction 전달 허용은 제조사 확인 전 open이다.
- [TiMOTION TA2P]({SOURCES['timotion']}): 3500 N push/2000 N pull, 20–1000 mm stroke, Hall 또는 가변저항 피드백, IP66M. 설치 길이는 stroke+108 mm 이상으로 더 낮은 패키징이 가능해 보이나 가격·MOQ·납기는 [TiMOTION Korea]({SOURCES['timotion_kr']}) 견적 필요. 기구 높이를 낮추려면 우선 RFQ할 대안입니다.

## 프레임·결합·제어

- [MISUMI HFS8-4040]({SOURCES['misumi']}): 40×40 mm, A6005CSS-T5, 약 1.73 kg/m. 절단 길이와 지역 가격은 견적.
- [DESTACO 323-R]({SOURCES['destaco']}): pull-action latch, 360 lbf holding capacity. 4개 적용하되 전단 위치결정은 가이드 핀이 담당.
- [Arduino Mega 2560 Rev3]({SOURCES['arduino']}), [Cytron MD13S]({SOURCES['cytron']}), [Adafruit BNO085]({SOURCES['bno085']}): PoC 제어용. 안전기능은 별도 하드와이어 회로로 분리.
- [Mean Well LRS-350-12]({SOURCES['meanwell']}): 12 V/29 A, 348 W로 3×5.5 A 액추에이터의 정격 최대전류 합을 수치상 상회. 실제 돌입전류·배선·퓨즈·EMI 검토 필요.
- [Omron A22E]({SOURCES['omron']}): 22/25 mm 패널형 비상정지 스위치 계열. 안전 릴레이/접촉기 구성은 별도 설계.

공식 Firgelli 8-inch actuator, MB21, MB20, MB17 STEP 원본은 `references/vendor/firgelli/`에 보존했습니다. 해시는 `design_basis/firgelli_mount_datum_review_2026-08-27.md`에 기록했습니다.
"""
    (out / "purchase_research.md").write_text(procurement, encoding="utf-8")
    write_bom(out)
    return results


if __name__ == "__main__":
    write_reports()
