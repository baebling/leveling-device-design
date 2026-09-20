"""Build the Rev E domestic-source master BOM from the audited Rev D table.

The generated BOM is a CAD-stage list, not a purchase release.  It keeps the
mechanical rows that still match Rev E, applies the changed geometry notes, and
replaces the former high-cost/imported controls with the researched domestic
bench-control architecture.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "procurement" / "profile_radial_revd_final_master_bom_2026-09-01.csv"
CSV_OUT = ROOT / "procurement" / "profile_radial_reve_domestic_master_bom_2026-09-02.csv"
MD_OUT = ROOT / "procurement" / "profile_radial_reve_domestic_master_bom_2026-09-02.md"
BUDGET_KRW = 4_000_000


def update(row: dict[str, str], **values: object) -> dict[str, str]:
    result = dict(row)
    result.update({key: str(value) for key, value in values.items()})
    unit_price = int(result["unit_price_krw_screen"] or 0)
    order_qty = int(float(result["order_qty"] or 0))
    result["extended_price_krw_screen"] = str(unit_price * order_qty)
    return result


def won(value: int) -> str:
    return f"{value:,}원"


with SOURCE.open("r", encoding="utf-8-sig", newline="") as handle:
    reader = csv.DictReader(handle)
    fieldnames = reader.fieldnames
    assert fieldnames is not None
    source_rows = list(reader)


replacement: dict[str, dict[str, object]] = {
    "S02": {
        "installation_or_cut_note": "하부 횡재 Y=330/95/-47.5/-330 mm; 620 mm 4개, 직각 절단 길이 재확인",
    },
    "M01": {
        "procurement_status": "HOLD_EXACT_OPTION_AND_CURRENT_VERIFY",
        "installation_or_cut_note": (
            "Rev E 실제 STEP 기준. 세 대 모두 DC24V/100 mm/5 V encoder/6 ppr/10 mm/s/750 N으로 주문 옵션 확인; "
            "정격·기동·스톨전류와 배선색은 판매자 서면 확인 전 발주 금지"
        ),
    },
    "M02": {
        "procurement_status": "HOLD_VENDOR_DRAWING_AND_PIN_CHECK",
        "installation_or_cut_note": (
            "Fusion에는 사진 판독 외형과 36 mm 바닥홀 피치를 반영. 내부 폭, 핀 중심 오프셋, Ø6 핀/리테이너 동봉 여부는 "
            "판매자 치수도면으로 확인 후 어댑터 도면 동결"
        ),
    },
    "C01": {
        "supplier_code": "A1_LMB_RADIAL_ADAPTER_REVE_120x70x8",
        "specification": "A6061-T6, 120x70x8; 2xD9 profile holes at X +/-48; 2xM8x1.25 LMB taps at 36 mm pitch",
        "procurement_status": "HOLD_REVE_DXF_AND_LMB_DRAWING",
        "installation_or_cut_note": "Rev E CAD 형상 확정; LMB-10 공급도면 확인 후 제작용 DXF/공차도 발행",
    },
    "C02": {
        "supplier_code": "A2_LMB_RADIAL_ADAPTER_REVE_120x70x8",
        "specification": "A6061-T6, 120x70x8; 2xD9 profile holes at local X +/-48; 2xM8x1.25 LMB taps at 36 mm pitch",
        "procurement_status": "HOLD_REVE_DXF_AND_LMB_DRAWING",
        "installation_or_cut_note": "Rev E CAD 형상 확정; LMB-10 공급도면 확인 후 제작용 DXF/공차도 발행",
    },
    "C03": {
        "supplier_code": "A3_LMB_RADIAL_ADAPTER_REVE_120x70x8",
        "specification": "A6061-T6, 120x70x8; 2xD9 profile holes at local X -70/+30; 2xM8x1.25 LMB taps at 36 mm pitch",
        "procurement_status": "HOLD_REVE_DXF_AND_LMB_DRAWING",
        "installation_or_cut_note": "A3만 100 mm 비대칭 체결 피치. Rev E CAD 기준이며 판매자 도면 확인 후 제작용 DXF/공차도 발행",
    },
    "F08": {
        "procurement_status": "HOLD_FINAL_STACK_CONFIRM",
        "installation_or_cut_note": "상부 횡축. 실제 STEP 전면 아이 약 19 mm + PHS6 폭 9 mm + F09 와셔 2장 적층을 실물 치수로 재확인",
    },
    "F09": {
        "item": "M6 평와셔",
        "specification": "M6, t1.5 nominal, plain washer; upper pivot lateral centering",
        "used_qty": 6,
        "procurement_status": "HOLD_FINAL_STACK_CONFIRM",
        "installation_or_cut_note": "축당 2장. 전면 아이 약 19 + PHS6 9 + 와셔 1.5x2 = 약 31 mm 적층; 심 대체로 표기하지 않음",
    },
    "E01": {
        "item": "2채널 양방향 DC 모터 드라이버",
        "specification": "Cytron MDD10A, 5-30 VDC, 10 A continuous/channel, PWM+DIR, regenerative H-bridge",
        "used_qty": 2,
        "order_qty": 2,
        "order_unit": "EA",
        "supplier": "DeviceMart",
        "supplier_code": "1280280/MDD10A",
        "unit_price_krw_screen": 39930,
        "price_status": "VAT포함 화면가 2026-09-02",
        "procurement_status": "HOLD_ACTUATOR_CURRENT_COMMISSIONING",
        "product_url": "https://www.devicemart.co.kr/goods/view?no=1280280",
        "installation_or_cut_note": "두 보드의 4채널 중 3채널 사용. 역극성 보호 없음; 액추에이터 실측 기동/스톨전류가 채널 및 PSU 한계 이내인지 확인",
    },
    "E02": {
        "item": "Mega2560 호환 제어보드",
        "specification": "SunFounder TS0481 Mega 2560 R3 compatible, USB Type-C cable included",
        "supplier": "DeviceMart",
        "supplier_code": "1382306/TS0481",
        "unit_price_krw_screen": 34980,
        "price_status": "VAT포함 화면가 2026-09-02",
        "procurement_status": "CAD_STAGE_SELECTED",
        "product_url": "https://www.devicemart.co.kr/goods/view?no=1382306",
        "installation_or_cut_note": "PC에서 USB로 파라미터 조정/로그 가능. 엔코더 3축과 MDD10A 3채널을 단일 보드에서 처리",
    },
    "E03": {
        "item": "6축 IMU 모듈",
        "specification": "VOLT GY-521 / MPU6050, I2C, 3-axis gyro + 3-axis accelerometer",
        "supplier": "DeviceMart",
        "supplier_code": "15960724/VLT-GY006",
        "unit_price_krw_screen": 6490,
        "price_status": "VAT포함 화면가 2026-09-02",
        "procurement_status": "CAD_STAGE_SELECTED_CALIBRATION_REQUIRED",
        "product_url": "https://www.devicemart.co.kr/goods/view?no=15960724",
        "installation_or_cut_note": "상판 강체에 수평 기준축을 표시해 고정; 장착 후 영점·온도 드리프트 보정 필요",
    },
    "E04": {
        "item": "24 V AC-DC 전원공급기",
        "specification": "Mean Well LRS-350-24, 24 VDC, 14.6 A, 350 W",
        "supplier": "DeviceMart",
        "supplier_code": "13231965/LRS-350-24",
        "unit_price_krw_screen": 45650,
        "price_status": "VAT포함 화면가 2026-09-02",
        "procurement_status": "HOLD_ACTUATOR_CURRENT_COMMISSIONING",
        "product_url": "https://www.devicemart.co.kr/goods/view?no=13231965",
        "installation_or_cut_note": "접지 필수. 액추에이터 3축 동시 기동/스톨 전류 합이 14.6 A 이내인지 실측 후 동시구동 제한 결정",
    },
    "E05": {
        "item": "방수형 24 V-5 V 강압 모듈",
        "specification": "SZH-BPM003, input 15-40 VDC, output 5 VDC 3 A",
        "supplier": "DeviceMart",
        "supplier_code": "1330743/SZH-BPM003",
        "unit_price_krw_screen": 9350,
        "price_status": "VAT포함 화면가 2026-09-02",
        "procurement_status": "CAD_STAGE_SELECTED",
        "product_url": "https://www.devicemart.co.kr/goods/view?no=1330743",
        "installation_or_cut_note": "Mega/IMU/엔코더 로직 전용 5 V 분기. 모터 전원과 배선·접지를 분리 배치",
    },
    "E09A": {
        "item": "방수 인라인 ATO 퓨즈홀더",
        "specification": "SZH-FU005, ATO/ATC blade fuse holder",
        "used_qty": 4,
        "order_qty": 4,
        "order_unit": "EA",
        "supplier": "DeviceMart",
        "supplier_code": "12170196/SZH-FU005",
        "unit_price_krw_screen": 1870,
        "price_status": "VAT포함 화면가 2026-09-02",
        "procurement_status": "CAD_STAGE_SELECTED",
        "product_url": "https://www.devicemart.co.kr/goods/view?no=12170196",
        "installation_or_cut_note": "24 V 액추에이터 드라이버 분기 3개와 5 V 로직 분기 1개에 각각 설치",
    },
    "E09B": {
        "item": "ATO 블레이드 퓨즈 5 A",
        "specification": "32 VDC automotive blade fuse, 5 A; pack minimum/order quantity 10",
        "used_qty": 3,
        "order_qty": 10,
        "order_unit": "EA",
        "supplier": "DeviceMart",
        "supplier_code": "11509/ATO-5A",
        "unit_price_krw_screen": 110,
        "price_status": "VAT포함 화면가 2026-09-02",
        "procurement_status": "HOLD_ACTUATOR_CURRENT_COMMISSIONING",
        "product_url": "https://www.devicemart.co.kr/goods/view?no=11509",
        "installation_or_cut_note": "축당 1개, 나머지는 예비. 실측 기동·스톨전류 검토 전 임의 증용량 금지",
    },
    "E09C": {
        "item": "ATO 블레이드 퓨즈 1 A",
        "specification": "32 VDC automotive blade fuse, 1 A",
        "used_qty": 1,
        "order_qty": 3,
        "order_unit": "EA",
        "supplier": "DeviceMart",
        "supplier_code": "16020344/ATO-1A",
        "unit_price_krw_screen": 726,
        "price_status": "VAT포함 화면가 2026-09-02",
        "procurement_status": "CAD_STAGE_SELECTED",
        "product_url": "https://www.devicemart.co.kr/goods/view?no=16020344",
        "installation_or_cut_note": "5 V 로직 분기 1개 사용, 2개 예비",
    },
    "E20": {
        "item": "35 mm DIN 레일",
        "specification": "JTRN 4, steel, 1 m; cut to enclosure layout length",
        "used_qty": 1,
        "order_qty": 1,
        "order_unit": "EA",
        "supplier": "DeviceMart",
        "supplier_code": "12538843/JTRN-4-1M",
        "unit_price_krw_screen": 16720,
        "price_status": "VAT포함 환산가, 결제화면 재확인",
        "procurement_status": "HOLD_ENCLOSURE_LAYOUT_CUT_LENGTH",
        "product_url": "https://www.devicemart.co.kr/goods/view?no=12538843",
        "installation_or_cut_note": "E08 차단기 및 DIN 부품용. 전장함 내부 배치 확정 후 절단·디버링",
    },
}


removed = {"E10", "E14"}
status_normalization = {
    "ORDER": "CAD_STAGE_SELECTED",
    "ORDER_CUT_TO_LENGTH": "HOLD_CUT_LENGTH_CONFIRM",
    "ORDER_LAYOUT_KIT": "HOLD_ELECTRICAL_LAYOUT",
    "ORDER_LAYOUT_VERIFY": "HOLD_ELECTRICAL_LAYOUT",
    "ORDER_VENDOR_CONTENT_VERIFY": "HOLD_VENDOR_CONTENT_VERIFY",
    "ORDER_SIZE_VERIFY": "HOLD_SIZE_VERIFY",
    "ORDER_SUPERVISED_BENCH": "CAD_STAGE_SELECTED_SUPERVISED_BENCH",
}
rows: list[dict[str, str]] = []
for source_row in source_rows:
    bom_id = source_row["bom_id"]
    if bom_id in removed:
        continue
    row = update(source_row, **replacement.get(bom_id, {}))
    row["procurement_status"] = status_normalization.get(
        row["procurement_status"], row["procurement_status"]
    )
    rows.append(row)


with CSV_OUT.open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


known_total = sum(int(row["extended_price_krw_screen"] or 0) for row in rows)
quote_rows = [row for row in rows if int(row["unit_price_krw_screen"] or 0) == 0]
by_supplier: dict[str, int] = defaultdict(int)
for row in rows:
    by_supplier[row["supplier"]] += int(row["extended_price_krw_screen"] or 0)

status_counts: dict[str, int] = defaultdict(int)
for row in rows:
    status_counts[row["procurement_status"]] += 1

lines = [
    "# Profile Radial 3-RPS Rev E 국내 구매형 CAD 단계 BOM",
    "",
    "> 기준일: 2026-09-02  ",
    "> 상태: `CAD_STAGE_COMPLETE`, `purchase_release=false`, `fabrication_release=false`, `commissioning_release=false`",
    "",
    "검토용 Excel 파일: `outputs/profile_radial_revE_actual_vendor/Profile_Radial_3RPS_RevE_Domestic_BOM_2026-09-02.xlsx`",
    "",
    "## 판정",
    "",
    f"- 총 {len(rows)}개 BOM 행이며, 화면가가 있는 품목의 합계는 **{won(known_total)}**다.",
    f"- 400만원 예산에서 화면가 기준 잔액은 **{won(BUDGET_KRW - known_total)}**다. 다만 맞춤가공 {len(quote_rows)}행, 배송비, 전장함 가공, 세금 변동은 미포함이다.",
    "- CAD 단계의 부품 구성은 닫혔지만 `M01` 액추에이터 전류/배선, `M02` LMB-10 공급도면과 동봉핀, 맞춤판 제작도면이 닫히지 않아 지금 주문하면 안 된다.",
    "- 외장 TVS 다이오드 행은 삭제했다. MDD10A가 회생형 H-브리지이므로 모터 출력 양단에 검증되지 않은 24 V TVS를 고정 적용하지 않는다.",
    "- USB 데이터 케이블 행은 삭제했다. 선택한 TS0481에 Type-C 케이블이 포함된다.",
    "",
    "## 제어 구조",
    "",
    "`PC(선택) -> Mega2560 1대 -> MDD10A 2대/3채널 -> LM4075OE 3대`",
    "",
    "`MPU6050 -> I2C -> Mega2560`, `액추에이터 엔코더 A/B 3조 -> Mega2560`, `24 V PSU -> 모터`, `24->5 V buck -> 로직/엔코더`",
    "",
    "이 구성은 축마다 제어기를 한 대씩 사지 않는다. Mega 한 대가 수평 제어와 세 엔코더를 처리하고, 2채널 드라이버 두 대 중 세 채널만 사용한다.",
    "",
    "## 공급처별 화면가",
    "",
    "| 공급처 | 화면가 합계 | 비고 |",
    "|---|---:|---|",
]
for supplier, subtotal in sorted(by_supplier.items(), key=lambda item: (-item[1], item[0])):
    note = "견적 필요" if subtotal == 0 else "배송/결제 화면 재확인"
    lines.append(f"| {supplier} | {won(subtotal)} | {note} |")

lines.extend(
    [
        "",
        "## 주문 전 필수 게이트",
        "",
        "1. `M01`: 세 액추에이터가 DC24V/100 mm/10 mm/s/750 N/5 V 6ppr 엔코더 옵션인지 견적서에 문자열로 명시한다.",
        "2. `M01`: 정격, 기동, 스톨전류와 엔코더 배선색/출력레벨을 판매자에게 서면 확인한다.",
        "3. `M02`: LMB-10의 내부 폭, 전체 외형, 바닥홀 피치, 핀 중심 위치, 핀/리테이너 동봉 여부가 표시된 치수도면을 받는다.",
        "4. `C01-C03`: LMB-10 공급도면을 반영해 Rev E 제작용 DXF와 공차도를 다시 발행하고 Fusion 간섭검사를 3회 반복한다.",
        "5. `E01/E04/E09B`: 한 축 무부하 통전시험으로 기동·정상·정지·스톨 직전 전류와 회생 과도전압을 측정한 뒤 퓨즈와 동시구동 조건을 동결한다.",
        "6. 가공견적, 배송, 세금, 예비품을 포함한 총액이 400만원 이하인지 다시 합산한다.",
        "",
        "## 전체 BOM",
        "",
        "| ID | 시스템 | 품목 | 정확 사양 | 사용/주문 | 공급처·코드 | 화면가 합계 | 상태 |",
        "|---|---|---|---|---:|---|---:|---|",
    ]
)
for row in rows:
    specification = row["specification"].replace("|", "/")
    item = row["item"].replace("|", "/")
    supplier_code = f'{row["supplier"]} `{row["supplier_code"]}`'
    total = int(row["extended_price_krw_screen"] or 0)
    total_text = won(total) if total else "견적"
    lines.append(
        f'| `{row["bom_id"]}` | {row["system"]} | [{item}]({row["product_url"]}) | {specification} | '
        f'{row["used_qty"]}/{row["order_qty"]} {row["order_unit"]} | {supplier_code} | {total_text} | `{row["procurement_status"]}` |'
    )

lines.extend(
    [
        "",
        "## 상태 집계",
        "",
        "| 상태 | 행 수 |",
        "|---|---:|",
    ]
)
for status, count in sorted(status_counts.items()):
    lines.append(f"| `{status}` | {count} |")

lines.extend(
    [
        "",
        "## 제외한 과거 항목",
        "",
        "- `DMD-150` 3대: MDD10A 2대로 대체.",
        "- `WT901C`: MPU6050 모듈로 대체. PoC 정지 시험대에서 고가 AHRS는 필수가 아니다.",
        "- `DMC-200` 3대: 축별 독립 전용제어기 비용이 커서 제외.",
        "- `SDCMG3260T + WT901C-CAN`: 국내 즉시 구매·통합자료를 확인하지 못했고 제어 단순화 효과가 불명확해 제외.",
        "- `SMCJ24CA/1.5KE24CA`: 실제 모터단 파형 검증 없이 24 V 출력에 고정 적용하는 것이 부적절해 제외.",
        "- 별도 USB 케이블: TS0481 동봉품과 중복되어 제외.",
        "",
        "세부 치수, 절단 위치와 조립 검증 근거는 `design_basis/Profile_Radial_3RPS_RevE_CAD_validation_2026-09-02.md`를 따른다.",
    ]
)

MD_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"wrote {CSV_OUT.relative_to(ROOT)} ({len(rows)} rows)")
print(f"wrote {MD_OUT.relative_to(ROOT)}")
print(f"known subtotal: {known_total:,} KRW")
print(f"budget remainder before quotes/shipping: {BUDGET_KRW - known_total:,} KRW")
