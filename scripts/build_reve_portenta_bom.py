"""Reproducible preliminary BOM; never author XLSX outside @oai/artifact-tool.

Run without arguments for CSV/JSON; --workbook preview then inspect PNGs;
--workbook export creates the single approved XLSX after visual review.
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "procurement/reve_final_order_bom_2026-09-17.csv"
OUT = ROOT / "procurement/reve_portenta_order_bom_2026-09-18"
WORK = ROOT / ".superpowers/sdd/2026-09-20-reve-z15-rebaseline/task4_workbook"
NODE = Path(r"C:\Users\gangm\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe")
RELEASE = "HOLD_VENDOR_REPLY"
BUDGET_VERDICT = "판정 보류"
# These are exclusive to the retired Mega/MDD/MPU architecture. DMC encoder
# 5 V supply is NOT assumed proven: vendor current/level confirmation is a gate.
DELETIONS = {
    "M01S": "No spare actuator approved in this budget.",
    "E01": "MDD10A replaced by three DMC-200 drives.",
    "E02": "Mega2560 replaced by one Portenta Machine Control.",
    "E03": "MPU6050 replaced by two addressed HWT905-RS485 sensors.",
    "E05": "Mega/MPU 5 V buck removed; 24 V controller/sensors/HMI. DMC 5 V encoder supply remains HOLD.",
    "E25": "M3 plastic Mega/buck PCB supports no longer apply to enclosed/DIN hardware.",
    "E26": "Mega Dupont jumpers superseded by screw-terminal wiring.",
}


def _new(id_, item, model, vendor, price, url, notes, *, qty=1, use=1,
         unit="EA", lead="결제 전 재확인", status="CHECKOUT_RECONFIRM", category="제어계",
         origin="국내 판매·출하 조건 재확인", evidence="Task2 공급처 원문; 2026-09-20 확인"):
    price_basis = "VAT포함 공개 화면가; 결제 전 재확인" if price else "비가격 placeholder; SKU·가격·재고·카드결제 미확정"
    return {"발주구분": "BASE", "ID": id_, "분류": category, "품목": item,
            "규격": model, "사용수량": use, "주문수량": qty, "주문단위": unit,
            "공급처": vendor, "상품번호/형번": model, "단가(VAT포함)": price,
            "확장금액": qty * price, "가격기준": price_basis,
            "납기": lead, "주문상태": status, "대체허용": "검토 없이 대체 금지",
            "CAD/조립확인": "전장 배치·결선 Task3 / 실물 조립 확인 필요",
            "구매URL": url, "주문/조립 메모": notes, "확인일": "2026-09-20",
            "출하구분": origin, "증빙": evidence, "구매릴리스": RELEASE, "예산판정": BUDGET_VERDICT}


def build_rows() -> list[dict[str, object]]:
    with SOURCE.open(encoding="utf-8-sig", newline="") as f:
        rows = [dict(r) for r in csv.DictReader(f) if r["ID"] not in DELETIONS]
    for r in rows:
        for key in ("사용수량", "주문수량", "단가(VAT포함)"):
            r[key] = int(r[key])
        r["확장금액"] = r["주문수량"] * r["단가(VAT포함)"]
        r.update({"출하구분": "기존 9/17 BOM 유지; 국내재고·출하 재확인",
                  "증빙": "procurement/reve_final_order_bom_2026-09-17.csv (기존 계획가 포함)",
                  "구매릴리스": RELEASE, "예산판정": BUDGET_VERDICT})
        if r["ID"] == "E04":
            r.update({
                "품목": "24 V 30 A급 모터 전원공급기 (SKU 보류)",
                "규격": "DC 24 V, 연속 30 A 이상, 720 W 이상; 정격·돌입·접지·보호 확인 필요",
                "공급처": "국내 SKU 미선정",
                "상품번호/형번": "HOLD_SMPS_30A_SKU",
                "단가(VAT포함)": 0,
                "확장금액": 0,
                "가격기준": "비가격 placeholder; 국내 SKU·가격·재고·카드결제 미확정",
                "주문상태": "HOLD_SMPS_30A_SKU",
                "CAD/조립확인": "3×7.5 A provisional peak×1.25=28.125 A. 24 V 30 A급은 선정 기준일 뿐 구매 품목 아님.",
                "주문/조립 메모": "기존 LRS-350-24(14.6 A)는 현 3축 전동 구동 PSU로 사용 금지. 30 A급 국내 SKU와 단락/돌입/접지/방열 자료 확인 전 주문·모터전원 인가 금지.",
                "출하구분": "국내 공급처·카드결제·재고·납기 미확정",
                "증빙": "verification/reve_z15_electrical_gate_2026-09-20.md; HOLD_SMPS_30A_SKU",
            })
        if r["ID"] == "E09C":
            r.update({
                "품목": "24 V 제어 분기 퓨즈 (정격 보류)",
                "규격": "HOLD_CONTROL_FUSE_RATING; 기존 1 A 제품은 발주 대상 아님",
                "공급처": "국내 SKU 미선정",
                "상품번호/형번": "HOLD_CONTROL_FUSE_RATING",
                "단가(VAT포함)": 0,
                "확장금액": 0,
                "가격기준": "비가격 placeholder; 분기 부하·전선·홀더 정격 확인 전 미선정",
                "주문상태": "HOLD_CONTROL_FUSE_RATING",
                "CAD/조립확인": "Portenta·HWT905·SG01 분기 최악전류와 퓨즈홀더 정격을 확인 후 선정.",
                "주문/조립 메모": "기존 1 A 규격을 유지하거나 주문하지 않는다. HMI/KC522 제거 후 실제 제어부 구성 기준으로 재산정.",
                "출하구분": "국내 SKU·재고·카드결제 미확정",
                "증빙": "verification/reve_z15_electrical_gate_2026-09-20.md; 기존 1 A 주장 폐기",
            })
        if r["ID"] == "F06":
            r["사용수량"] = 23
            r["주문/조립 메모"] += "; DG60103 측정용 홀더 1개용 M8 너트 추가 사용(100개 팩 내)."
        if r["ID"] in {"E06", "E11", "E12", "E18", "E22"}:
            r["CAD/조립확인"] = "기존 부품 유지 / 새 제어계 배치·DC 차단·배선 Task3 재검토"
        if r["ID"] == "E16":
            r["주문/조립 메모"] = "버튼·접점·단거리 제어배선용 유지. RS485는 별도 차폐 연선 CB01 사용."
    # Retained baseline is allowed to differ only for active electrical sizing rows E04/E09C.
    retained_unaffected = [r for r in rows if r["ID"] not in {"E04", "E09C"}]
    assert sum(r["확장금액"] for r in retained_unaffected) == 1_300_779, "Unrelated retained baseline changed: review before regenerating."
    rows.append(_new("PC01", "Portenta Machine Control", "AKX00032 / 13963538", "디바이스마트", 546667,
        "https://www.devicemart.co.kr/goods/view?no=13963538", "DigiKey 해외조달. 표시가546667원은 최종 도착원가 아님. 약관15만원 이상 관부가세 고객 부담·취소불가. AL01은 계획 충당액이며 실제 관세/수입VAT/운임 견적 필요.",
        lead="화면 4~5일 vs 해외약관 평균10~15일 충돌 / 공급처 확정 필요", status="HOLD_LANDED_COST", origin="DigiKey 해외조달 / 고객 별도 관부가세 / 재고244 해외연계", evidence="Task1 AKX00032_devicemart_product_page.html: display L9695, terms L11681–11683"))
    rows[-1]["가격기준"] = "화면 표시가546667원(사이트 VAT포함 표기); 별도 관세·수입VAT·운임 포함 여부 미확정"
    rows.append(_new("AL01", "PC01 수입·운임 계획 충당액(주문품 아님)", "PC01 화면가×20% 반올림 / 비확정 계획액", "PC01 해외조달 비용 충당(수취인 미확정)", 109333,
        "https://www.devicemart.co.kr/goods/view?no=13963538", "546667×20%=109333.4→109333원 계획 충당. 확정 세액 아님; 실제 세율·과세표준·운임 계산 아님. 견적 수령 후 실제 도착원가로 대체하며 추가비용 가능. 장바구니 입력 금지.",
        category="계획충당", unit="ALLOWANCE", lead="PC01 최종 도착원가 회신 전 미확정", status="PLANNING_ALLOWANCE_NOT_QUOTE", origin="수입 관부가세·운임 불확실성 / 계획 가정", evidence="판매약관 비용부담 근거: Task1 archive L11681; 20%는 Task2 fix1 보수적 계획 가정"))
    rows[-1]["가격기준"] = "보수적 20% 계획 충당액; VAT포함 판매가/확정 세액/공급처 견적 아님"
    for i in range(1, 4):
        rows.append(_new(f"DC0{i}", f"DMC-200 축{i} 위치제어 드라이버", "DMC-200 / 1000008040", "모터뱅크", 94380,
            "https://www.motorbank.kr/goods/goods_view.php?goodsNo=1000008040", "엔코더 레벨·pull-up·5V전류·계수·내장리미트 복귀·0x0E/0x0F·3노드 회신 전 주문 금지.",
            status=RELEASE, evidence="Task1 supplier matrix / DMC-200_motorbank_product_page.html"))
    for i, where in [(1, "상부"), (2, "하부")]:
        rows.append(_new(f"IS0{i}", f"{where} 절대 경사센서", "HWT905-RS485 / 3973625857 / 옵션03(+46200)", "G마켓 케이일레븐홀딩스", 182530,
            "https://item.gmarket.co.kr/Item?goodsCode=3973625857", "RS485형 정확 선택; 9~36V. 각각 고유주소/20Hz 폴링은 입고 검증. MK700 제외.",
            lead="9/21 출발 표시 / 무료배송", origin="국내배송 전용; 수량2 재고 결제 전 재확인", evidence="Task1 HWT905_RS485_gmarket_evidence_2026-09-20.md"))
    rows.extend([
        _new("MV01", "독립 Z 검증 디지털 인디케이터", "Mitutoyo 543-730B / K56222641 / 50.8mm / Ø8mm stem", "나비엠알오", 681989,
             "https://www.navimro.com/p/K56222641/", "정지한 0/25/50mm Z를 독립 측정·사진 보고용. 폐루프 제어 아님. 최소 예압0.2~0.3mm, 측정범위 초과 금지. HOME/기울임 때 분리.", lead="9/28 출하 표시", category="독립검증", origin="국내몰 출하일 표시; 원산지 일본 / 창고 재고 재확인", evidence="gauge.html + gauge_official.html; 공식 stem Ø8mm·50.8mm"),
        _new("MV02", "Ø8mm 측정기 관절 홀더(베이스 없음)", "NOGA DG60103 / HT3205(DG-60103) / 456-0157", "툴앤샵", 142670,
             "https://www.toolnshop.kr/view/?goods=11469", "제조사 Ø6/8/3⁄8 클램프·판매자 M8×1.25 확인. MV01 stem Ø8 호환. F06 여분너트로 4040에 고정; 도달범위·강성·이탈은 실물 확인. YMB-BV 제외.", lead="재고 유 / 9/21 출고 표시", category="독립검증", origin="국내 툴앤샵 출하 / 카드결제", evidence="noga_official.html + noga_seller.html"),
        _new("SH02", "측정 홀더 배송비", "툴앤샵 CJ택배 / 50만원 미만", "툴앤샵", 3000,
             "https://www.toolnshop.kr/view/?goods=11469", "홀더142670원 주문에 표시된 배송비 1건.", category="배송", origin="국내배송", evidence="noga_seller.html"),
        _new("SG01", "절연 Ethernet-RS485 게이트웨이 (SKU 보류)", "ICP DAS tGW-715i-T", "국내 판매처·카드결제 미확인", 0,
             "HOLD_SG01_QUOTE_CARD_STOCK", "Portenta Ethernet↔SG01 TCP 502↔HWT905 RS485 #11/#12 전용 버스. ICP DAS tGW-715i-T는 기술 후보일 뿐 국내 가격·재고·납기·카드결제 증빙 전 주문 금지.", lead="HOLD_SG01_QUOTE_CARD_STOCK", status="HOLD_SG01_QUOTE_CARD_STOCK", category="제어계", origin="국내 구매 가능성만 조사됨; 상업 조건 미확인", evidence="verification/reve_z15_electrical_gate_2026-09-20.md; ICP DAS tGW-715i-T datasheet basis"),
        _new("CB01", "차폐 3쌍 통신 케이블", "광일전선 UL2919 / 3P×24AWG / 13352", "디바이스마트", 3850,
             "https://www.devicemart.co.kr/goods/view?no=13352", "6m: 짧은 모터버스 약3m+상하센서 약2m+서비스1m 계획. Task3 배치 후 절단. 체인용 아님; 저속 실내 여유루프. 기존 E16은 접점선.", qty=6, use=6, unit="M", lead="3~4일 준비", evidence="13352.html / VAT포함3850원·m단위"),
        _new("RT01", "RS485 종단저항", "제일전자 1/4W 1% 121F / 120Ω / 1997", "디바이스마트", 44,
             "https://www.devicemart.co.kr/goods/view?no=1997", "필요한 버스 끝에만 최대2개 계획. 내장 종단과 중복 금지, Task3 확정. 10개는 최소주문 단위.", qty=10, use=2, lead="1~2일 준비", evidence="resistor.html"),
        _new("CB02", "Portenta-SG01 Ethernet 케이블", "Anyport AP-6UTP-2M(G) / 10932540", "디바이스마트", 1320,
             "https://www.devicemart.co.kr/goods/view?no=10932540", "Portenta-SG01 고정 2m. SG01 실제 배치·전원·RJ45 여유 확인 전 절단/이동부 사용 금지.", lead="3~4일 준비", evidence="ethernet_web_evidence.md / HTML archive fetch 실패; Task3 HMI-less architecture"),
        _new("CB03", "Portenta 프로그래밍 USB 데이터 케이블", "Coms C3886 / USB-A to Micro-B / 1061716", "디바이스마트", 2750,
             "https://www.devicemart.co.kr/goods/view?no=1061716", "Machine Control 외장 포트는 Micro-B(제조사 핀아웃). H7의 USB-C와 혼동 금지. 기존 Mega 포함선 삭제 후 확보. 판매제목1m/설명1.5m 차이 있으나 직결 진단에 충분; USB-A PC 필요.", lead="2~3일 준비", evidence="program_micro_usb.html + Task1 AKX00032-full-pinout.pdf / VAT포함2750원"),
    ])
    validate_budget(rows)
    return rows


def known_price_subtotal(rows) -> int:
    """Known displayed purchase-price subtotal, excluding non-price placeholders and allowance."""
    return sum(r["확장금액"] for r in rows if r["발주구분"] == "BASE" and r["ID"] != "AL01" and r["단가(VAT포함)"] > 0)


def validate_budget(rows) -> int:
    ids = [r["ID"] for r in rows]
    required = {"PC01", "DC01", "DC02", "DC03", "IS01", "IS02", "SG01", "E04"}
    retired = {"HM01", "SH01", "LG01", "IF01"}
    if len(ids) != len(set(ids)) or not required <= set(ids) or set(ids) & (set(DELETIONS) | retired):
        raise ValueError("Missing, duplicate or retired control IDs")
    for r in rows:
        if not isinstance(r["주문수량"], int) or r["주문수량"] <= 0 or not isinstance(r["단가(VAT포함)"], int) or r["단가(VAT포함)"] < 0:
            raise ValueError("Quantity/price must be nonnegative typed integers; quantity > 0")
        if r["확장금액"] != r["주문수량"] * r["단가(VAT포함)"]:
            raise ValueError("Extended amount mismatch")
        if not all(r.get(k) for k in ("구매URL", "증빙", "주문상태", "공급처", "상품번호/형번")) or r.get("구매릴리스") != RELEASE or r.get("예산판정") != BUDGET_VERDICT:
            raise ValueError("Missing traceability or false release")
    actuators = [(r["ID"], r["주문수량"]) for r in rows if "액추에이터" in r["품목"]]
    if actuators != [("M01", 3)]:
        raise ValueError("Only three working actuators; no spare")
    for hold in ("HOLD_SG01_QUOTE_CARD_STOCK", "HOLD_SMPS_30A_SKU"):
        if hold not in "\n".join(str(r) for r in rows):
            raise ValueError(f"Missing required commercial hold: {hold}")
    rows_by_id = {r["ID"]: r for r in rows}
    if rows_by_id["SG01"]["단가(VAT포함)"] != 0 or rows_by_id["E04"]["단가(VAT포함)"] != 0:
        raise ValueError("Commercially unverified SG01/SMPS placeholders must not carry an invented price")
    return known_price_subtotal(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workbook", choices=("preview", "export"))
    args = parser.parse_args()
    rows = build_rows()
    known_subtotal = validate_budget(rows)
    with OUT.with_suffix(".csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    WORK.mkdir(parents=True, exist_ok=True)
    allowance = next(r["확장금액"] for r in rows if r["ID"] == "AL01")
    payload = {"rows": rows, "known_price_subtotal": known_subtotal, "planning_allowance": allowance,
               "release": RELEASE, "budget_verdict": BUDGET_VERDICT, "xlsx": str(OUT.with_suffix(".xlsx"))}
    (WORK / "bom_data.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Rows={len(rows)} known-price subtotal={known_subtotal:,} KRW; non-priced commercial holds excluded; allowance={allowance:,} KRW (not quote); release={RELEASE}")
    if args.workbook:
        subprocess.run([str(NODE), str(ROOT / "scripts/build_reve_portenta_bom_workbook.mjs"), args.workbook], check=True)


if __name__ == "__main__":
    main()
