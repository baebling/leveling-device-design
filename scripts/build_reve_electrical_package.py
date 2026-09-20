"""Build Rev E electrical layout, wiring tables, RFQs, and candidate BOM."""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import cadquery as cq
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "profile_radial_revE_poc_release_candidate"
ELEC = OUT / "electrical"
PROC = OUT / "procurement"
INTERFACES = OUT / "supplier_interfaces"
PDF_OUT = ROOT / "output" / "pdf" / "Profile_Radial_3RPS_RevE_Electrical_Drawings_RC_2026-09-04.pdf"
SOURCE_BOM = ROOT / "procurement" / "profile_radial_reve_domestic_master_bom_2026-09-02.csv"
BUDGET_KRW = 4_000_000
TARGET_KRW = 3_600_000


@dataclass(frozen=True)
class Device:
    ref: str
    description: str
    x: float
    y: float
    width: float
    height: float
    z: float
    depth: float
    zone: str
    dimension_basis: str
    mounting_gate: str


DEVICES = (
    Device("PS1", "Mean Well LRS-350-24", 25, 250, 115, 215, 3, 30, "AC/DC boundary", "official 215x115x30", "M4 hole pattern verify on receipt"),
    Device("Q1", "ABE32b 2P breaker", 35, 65, 36, 80, 8, 75, "220 VAC", "conservative envelope", "vendor outline verify"),
    Device("X1", "AC terminal block", 85, 85, 100, 25, 8, 25, "220 VAC", "layout envelope", "cut/cover verify"),
    Device("F1-F2", "MDD input fuse holders", 155, 280, 60, 80, 8, 25, "24 VDC", "layout envelope", "actual lead bend verify"),
    Device("D1", "Cytron MDD10A axes 1-2", 265, 390, 84.5, 62, 12, 22, "24 V power", "official 84.5x62", "PCB hole pattern verify"),
    Device("D2", "Cytron MDD10A axis 3", 265, 300, 84.5, 62, 12, 22, "24 V power", "official 84.5x62", "PCB hole pattern verify"),
    Device("A1", "Mega2560 compatible", 248, 215, 102, 54, 12, 22, "5 V logic", "Mega full-size envelope", "TS0481 holes verify"),
    Device("U1", "24 V to 5 V buck", 275, 160, 55, 35, 12, 25, "5 V logic", "conservative envelope", "module outline verify"),
    Device("X2", "SELV terminal block", 245, 85, 105, 25, 8, 25, "24/5 VDC", "layout envelope", "cut/cover verify"),
)


def ensure_dirs() -> None:
    for path in (OUT, ELEC, PROC, INTERFACES, PDF_OUT.parent):
        path.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, fieldnames: tuple[str, ...], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_interface_register() -> list[dict]:
    rows = [
        ("M01-01", "LM4075OE-1075", "motor_voltage", "24", "VDC", "user-selected option", "HIGH", "LOCKED"),
        ("M01-02", "LM4075OE-1075", "stroke", "100", "mm", "supplier listing/STEP", "HIGH", "LOCKED"),
        ("M01-03", "LM4075OE-1075", "speed", "10", "mm/s", "supplier listing", "HIGH", "LOCKED"),
        ("M01-04", "LM4075OE-1075", "rated_force", "750", "N", "supplier listing", "HIGH", "LOCKED"),
        ("M01-05", "LM4075OE-1075", "encoder_supply", "5", "VDC", "selected option", "MEDIUM", "VERIFY_WRITTEN"),
        ("M01-06", "LM4075OE-1075", "encoder_resolution", "6", "ppr", "supplier listing", "MEDIUM", "VERIFY_COUNTS_PER_MM"),
        ("M01-07", "LM4075OE-1075", "collapsed_pin_distance", "205.0", "mm", "vendor STEP measurement", "HIGH", "LOCKED_CAD"),
        ("M01-08", "LM4075OE-1075", "rear_eye_width", "18.0", "mm", "vendor STEP measurement", "HIGH", "LOCKED_CAD"),
        ("M01-09", "LM4075OE-1075", "front_eye_width_at_bore", "19.0", "mm", "vendor STEP measurement", "HIGH", "LOCKED_CAD"),
        ("M01-10", "LM4075OE-1075", "pivot_bore", "6.4", "mm", "vendor STEP measurement", "HIGH", "LOCKED_CAD"),
        ("M01-11", "LM4075OE-1075", "rated_current", "", "A", "supplier response/measurement required", "OPEN", "BLOCKS_POWER_RELEASE"),
        ("M01-12", "LM4075OE-1075", "startup_current", "", "A", "measurement required", "OPEN", "BLOCKS_POWER_RELEASE"),
        ("M01-13", "LM4075OE-1075", "stall_current", "", "A", "supplier response/measurement required", "OPEN", "BLOCKS_POWER_RELEASE"),
        ("M01-14", "LM4075OE-1075", "encoder_wire_colors_levels", "", "text", "supplier response required", "OPEN", "BLOCKS_HARNESS_RELEASE"),
        ("M01-15", "LM4075OE-1075", "internal_limit_behavior", "", "text", "supplier response/bench test required", "OPEN", "BLOCKS_HOME_RELEASE"),
        ("M01-16", "LM4075OE-1075", "duty_cycle", "", "%/min", "supplier response required", "OPEN", "BLOCKS_THERMAL_RELEASE"),
        ("M02-01", "LMB-10", "base_hole_pitch", "36.0", "mm", "photograph-derived CAD assumption", "LOW", "BLOCKS_FABRICATION_RELEASE"),
        ("M02-02", "LMB-10", "base_envelope", "56x26", "mm", "photograph-derived CAD assumption", "LOW", "BLOCKS_FABRICATION_RELEASE"),
        ("M02-03", "LMB-10", "inner_gap", "", "mm", "supplier drawing/measurement required", "OPEN", "BLOCKS_PIN_STACK_RELEASE"),
        ("M02-04", "LMB-10", "pivot_center_from_base", "", "mm", "supplier drawing/measurement required", "OPEN", "BLOCKS_CAD_FREEZE"),
        ("M02-05", "LMB-10", "pin_diameter_length", "", "mm", "supplier drawing/measurement required", "OPEN", "BLOCKS_PIN_RELEASE"),
        ("M02-06", "LMB-10", "pin_retainers_included", "", "yes/no", "supplier response required", "OPEN", "BLOCKS_BOM_RELEASE"),
    ]
    result = [dict(zip(("interface_id", "part", "parameter", "value", "unit", "source", "confidence", "gate"), row)) for row in rows]
    write_csv(INTERFACES / "RevE_supplier_interface_register_2026-09-04.csv", tuple(result[0]), result)
    return result


def write_rfqs() -> None:
    motion = """# MotionGearOn written-data request - LM4075OE-1075\n\n+Project use: stationary indoor 3-axis leveling PoC, three identical actuators.\n+Requested order option: DC24V / stroke 100 mm / 10 mm/s / 750 N / optical encoder 5 V / 6 ppr.\n+\n+Please confirm in writing for the exact supplied revision:\n+\n+1. Exact order-option text or SKU that guarantees all values above.\n+2. Rated running current, startup/inrush current, and stall current at 24 V.\n+3. Motor lead colors and polarity for extension/retraction.\n+4. Encoder supply, A/B output type and logic levels, wire colors, phase relation, and counts definition.\n+5. Internal upper/lower limit behavior and whether the motor circuit opens automatically at each end.\n+6. Duty cycle and any thermal-rest requirement.\n+7. Confirmation that the provided LM4075OE-1075 100 mm STEP matches the delivered mechanical revision.\n+8. Unit price, VAT, domestic shipping, lead time, and warranty for one validation sample and for three units.\n+\n+No substitution to 12 V, a different stroke, a 7-24 V encoder option, or a different connector revision is permitted without written approval.\n+"""
    motorbank = """# Motorbank drawing/content request - LMB-10\n\n+Project use: lower pivot bracket for LM4075/LM4075OE in a stationary indoor leveling PoC.\n+\n+Please provide a dimensioned drawing or CAD and confirm:\n+\n+1. Base overall length, width, thickness, hole diameters, and center-to-center pitch.\n+2. Pivot center position from the base mounting plane and base-hole datums.\n+3. Inner clear gap between ears and ear thickness.\n+4. Pivot pin diameter, usable grip length, total length, and fit/tolerance.\n+5. Whether the pin, washers, cotter/R-clip, or other retainers are included in product 1000007655/LMB-10.\n+6. Material/finish and compatible LM4075 variants.\n+7. Unit price, VAT, domestic shipping, and lead time for one validation sample and three production units.\n+\n+The current CAD uses only a provisional 36 mm base-hole pitch and 56x26 mm envelope. It will not be released for fabrication until your drawing or a measured first article replaces these assumptions.\n+"""
    (INTERFACES / "RFQ_MotionGearOn_LM4075OE_2026-09-04.md").write_text(motion, encoding="utf-8")
    (INTERFACES / "RFQ_Motorbank_LMB10_2026-09-04.md").write_text(motorbank, encoding="utf-8")


def build_candidate_bom() -> tuple[list[dict], int]:
    with SOURCE_BOM.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    for row in rows:
        if row["bom_id"] == "E09A":
            row["used_qty"] = "6"
            row["order_qty"] = "6"
            row["extended_price_krw_screen"] = str(int(row["unit_price_krw_screen"]) * 6)
            row["installation_or_cut_note"] = "MDD10A 입력 2 + 모터 출력 3 + 5V buck 입력 1. 실제 전류 확인 후 퓨즈 정격 동결"
        if row["bom_id"] in {"E06", "F18", "F19"}:
            row["procurement_status"] = "DETAIL_LAYOUT_COMPLETE_VERIFY_ON_RECEIPT"
        if row["bom_id"] == "E20":
            row["used_qty"] = "2"
            row["installation_or_cut_note"] = "전장함 배치 기준 320 mm 2개 절단; 실물 백플레이트 폭 확인 후 절단"
            row["procurement_status"] = "DETAIL_LAYOUT_COMPLETE_CUT_AFTER_RECEIPT"

    new_row = {key: "" for key in fieldnames}
    new_row.update(
        {
            "bom_id": "E09D",
            "system": "전장",
            "assembly": "MDD10A 24V 입력 분기",
            "item": "ATO 블레이드 퓨즈 10 A",
            "specification": "Eaton BK/ATC-10, 10 A, 32 VDC, ATO blade",
            "used_qty": "2",
            "order_qty": "3",
            "order_unit": "EA",
            "supplier": "DeviceMart",
            "supplier_code": "8999372/BK-ATC-10",
            "unit_price_krw_screen": "1991",
            "extended_price_krw_screen": str(1991 * 3),
            "price_status": "VAT포함 화면가 2026-09-04",
            "procurement_status": "HOLD_ACTUATOR_CURRENT_COMMISSIONING",
            "product_url": "https://www.devicemart.co.kr/goods/view?no=8999372",
            "installation_or_cut_note": "MDD10A 보드별 24V 입력 1개 사용, 1개 예비. 실측 전류 후 정격 재검토",
        }
    )
    insert_at = next(index for index, row in enumerate(rows) if row["bom_id"] == "E09B")
    rows.insert(insert_at, new_row)
    subtotal = sum(int(row["extended_price_krw_screen"] or 0) for row in rows)
    with (PROC / "Profile_Radial_3RPS_RevE_PoC_candidate_BOM_2026-09-04.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return rows, subtotal


def build_enclosure_cad() -> dict:
    assembly = cq.Assembly(name="REVE_ELECTRICAL_ENCLOSURE_RC")
    assembly.add(cq.Workplane("XY").box(400, 500, 3).translate((200, 250, 1.5)), name="SL902_BACKPLATE_ASSUMED", color=cq.Color(0.75, 0.78, 0.80))
    wall_color = cq.Color(0.80, 0.82, 0.84, 0.35)
    assembly.add(cq.Workplane("XY").box(400, 4, 155).translate((200, 2, 77.5)), name="ENCLOSURE_WALL_BOTTOM", color=wall_color)
    assembly.add(cq.Workplane("XY").box(400, 4, 155).translate((200, 498, 77.5)), name="ENCLOSURE_WALL_TOP", color=wall_color)
    assembly.add(cq.Workplane("XY").box(4, 492, 155).translate((2, 250, 77.5)), name="ENCLOSURE_WALL_LEFT", color=wall_color)
    assembly.add(cq.Workplane("XY").box(4, 492, 155).translate((398, 250, 77.5)), name="ENCLOSURE_WALL_RIGHT", color=wall_color)
    zone_colors = {
        "220 VAC": cq.Color(0.72, 0.13, 0.10),
        "AC/DC boundary": cq.Color(0.38, 0.41, 0.45),
        "24 VDC": cq.Color(0.91, 0.52, 0.12),
        "24 V power": cq.Color(0.91, 0.52, 0.12),
        "5 V logic": cq.Color(0.08, 0.45, 0.65),
        "24/5 VDC": cq.Color(0.18, 0.55, 0.35),
    }
    for device in DEVICES:
        block = cq.Workplane("XY").box(device.width, device.height, device.depth).translate(
            (device.x + device.width / 2, device.y + device.height / 2, device.z + device.depth / 2)
        )
        assembly.add(block, name=device.ref + "_" + device.description.replace(" ", "_"), color=zone_colors[device.zone])
    for index, y in enumerate((45, 120), start=1):
        rail = cq.Workplane("XY").box(320, 35, 7.5).translate((200, y + 17.5, 7))
        assembly.add(rail, name=f"DIN_RAIL_{index}_320mm", color=cq.Color(0.55, 0.57, 0.60))
    step_path = ELEC / "RevE_SL902_enclosure_layout_RC.step"
    assembly.save(str(step_path), exportType="STEP", mode="default")

    clearances = []
    minimum = 1e9
    overlap_pairs = []
    for i, first in enumerate(DEVICES):
        for second in DEVICES[i + 1 :]:
            dx = max(first.x - (second.x + second.width), second.x - (first.x + first.width), 0)
            dy = max(first.y - (second.y + second.height), second.y - (first.y + first.height), 0)
            clearance = (dx * dx + dy * dy) ** 0.5
            if dx == 0 and dy == 0:
                overlap_pairs.append((first.ref, second.ref))
            minimum = min(minimum, clearance)
            clearances.append({"pair": f"{first.ref}__{second.ref}", "planar_clearance_mm": round(clearance, 3)})
    in_bounds = all(d.x >= 20 and d.y >= 20 and d.x + d.width <= 380 and d.y + d.height <= 480 and d.z + d.depth <= 130 for d in DEVICES)
    ac_right = max(d.x + d.width for d in DEVICES if d.zone == "220 VAC")
    selv_left = min(d.x for d in DEVICES if d.zone in {"24/5 VDC", "5 V logic"})
    segregation = selv_left - ac_right
    result = {
        "enclosure_external_mm": [400, 500, 155],
        "assumed_usable_backplate_mm": [360, 460],
        "assumed_usable_height_mm": 127,
        "device_count": len(DEVICES),
        "component_overlap_pairs": overlap_pairs,
        "all_devices_in_assumed_bounds": in_bounds,
        "ac_to_logic_planar_segregation_mm": segregation,
        "minimum_required_ac_to_logic_mm": 50,
        "din_rail_cut_mm": [320, 320],
        "gland_centers_bottom_wall_x_mm": [30, 150, 190, 230, 280, 320, 360],
        "passes_layout_envelope": in_bounds and not overlap_pairs and segregation >= 50,
        "mounting_release": False,
        "mounting_release_reason": "SL902 backplate and all board mounting-hole patterns must be verified on receipt.",
        "clearances": clearances,
    }
    (ELEC / "RevE_enclosure_layout_validation.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    write_csv(ELEC / "RevE_enclosure_layout.csv", tuple(asdict(DEVICES[0])), [asdict(device) for device in DEVICES])
    return result


def render_layout() -> None:
    fig, ax = plt.subplots(figsize=(8, 9.5), dpi=150)
    ax.set_xlim(0, 400)
    ax.set_ylim(0, 500)
    ax.set_aspect("equal")
    ax.add_patch(Rectangle((0, 0), 400, 500, facecolor="#f3f4f6", edgecolor="#111827", linewidth=2))
    palette = {"220 VAC": "#b91c1c", "AC/DC boundary": "#4b5563", "24 VDC": "#ea580c", "24 V power": "#ea580c", "5 V logic": "#0284c7", "24/5 VDC": "#16a34a"}
    for device in DEVICES:
        ax.add_patch(Rectangle((device.x, device.y), device.width, device.height, facecolor=palette[device.zone], edgecolor="white", alpha=0.86))
        ax.text(device.x + device.width / 2, device.y + device.height / 2, f"{device.ref}\n{device.description}", color="white", ha="center", va="center", fontsize=7, weight="bold", wrap=True)
    ax.axvspan(185, 245, color="#d1d5db", alpha=0.5)
    ax.text(215, 25, "60 mm AC / logic routing corridor", ha="center", va="center", fontsize=7)
    for x, label in zip((30, 150, 190, 230, 280, 320, 360), ("AC", "M1", "M2", "M3", "E1", "E2", "E3")):
        ax.plot(x, 5, "ko", ms=5)
        ax.text(x, 12, label, ha="center", fontsize=7)
    ax.set_title("Rev E SL902 enclosure layout RC\n400 x 500 x 155 mm | verify physical backplate and hole patterns", fontsize=12, weight="bold")
    ax.set_xlabel("X mm")
    ax.set_ylabel("Y mm")
    ax.grid(color="#9ca3af", linewidth=0.3, alpha=0.5)
    fig.tight_layout()
    fig.savefig(ELEC / "RevE_SL902_enclosure_layout_RC.png")
    plt.close(fig)


def wiring_tables() -> None:
    io_rows = []
    for axis, pins in enumerate(((2, 22, 5, 30), (3, 23, 6, 31), (18, 24, 7, 32)), start=1):
        io_rows.extend(
            (
                {"function": f"ENC{axis}_A", "mega_pin": f"D{pins[0]}", "remote_ref": f"A{axis} encoder A", "signal_type": "5V pulse input", "gate": "supplier level/color verify"},
                {"function": f"ENC{axis}_B", "mega_pin": f"D{pins[1]}", "remote_ref": f"A{axis} encoder B", "signal_type": "5V pulse input", "gate": "supplier level/color verify"},
                {"function": f"MOTOR{axis}_PWM", "mega_pin": f"D{pins[2]}", "remote_ref": "D1" if axis < 3 else "D2", "signal_type": "5V PWM output", "gate": "locked"},
                {"function": f"MOTOR{axis}_DIR", "mega_pin": f"D{pins[3]}", "remote_ref": "D1" if axis < 3 else "D2", "signal_type": "5V direction output", "gate": "locked"},
            )
        )
    io_rows.extend(
        (
            {"function": "IMU_SDA", "mega_pin": "D20/SDA", "remote_ref": "GY-521 SDA", "signal_type": "I2C", "gate": "module logic-level bench verify"},
            {"function": "IMU_SCL", "mega_pin": "D21/SCL", "remote_ref": "GY-521 SCL", "signal_type": "I2C", "gate": "module logic-level bench verify"},
            {"function": "UNUSED_CH4_PWM", "mega_pin": "D8", "remote_ref": "D2 CH2 PWM", "signal_type": "held 0", "gate": "locked"},
            {"function": "UNUSED_CH4_DIR", "mega_pin": "D33", "remote_ref": "D2 CH2 DIR", "signal_type": "held low", "gate": "locked"},
        )
    )
    write_csv(ELEC / "RevE_io_map.csv", tuple(io_rows[0]), io_rows)

    terminals = [
        ("X1-1", "AC L switched", "Q1-L-OUT", "PS1-L", "1.5 mm2", "black/brown"),
        ("X1-2", "AC N switched", "Q1-N-OUT", "PS1-N", "1.5 mm2", "blue"),
        ("X1-3", "Protective earth", "J1-PE", "PS1-FG", "2.5 mm2", "green/yellow"),
        ("X1-4", "Protective earth bond", "X1-3", "DIN rail/lower frame", "2.5 mm2", "green/yellow"),
        ("X2-1", "+24 V source", "PS1 +V", "F1/F2/F6 inputs", "14 AWG", "red"),
        ("X2-2", "0 V power", "PS1 -V", "D1/D2/U1 inputs", "14 AWG", "black"),
        ("X2-3", "+24 V D1 fused", "F1 output", "D1 Vmotor+", "14 AWG", "red"),
        ("X2-4", "0 V D1", "X2-2", "D1 GND", "14 AWG", "black"),
        ("X2-5", "+24 V D2 fused", "F2 output", "D2 Vmotor+", "14 AWG", "red"),
        ("X2-6", "0 V D2", "X2-2", "D2 GND", "14 AWG", "black"),
        ("X2-7", "+24 V logic fused", "F6 output", "U1 IN+", "24 AWG", "red"),
        ("X2-8", "0 V logic input", "X2-2", "U1 IN-", "24 AWG", "black"),
        ("X2-9", "+5 V logic", "U1 OUT+", "Mega/encoders/IMU", "24 AWG", "red"),
        ("X2-10", "Logic common", "U1 OUT-", "Mega/D1/D2/encoders/IMU", "24 AWG", "black"),
    ]
    terminal_rows = [dict(zip(("terminal", "net", "from", "to", "wire", "color"), row)) for row in terminals]
    write_csv(ELEC / "RevE_terminal_map.csv", tuple(terminal_rows[0]), terminal_rows)

    wires = [
        ("W001", "J1-L", "Q1-L-IN", "AC_L", "1.5 mm2", "brown", 350, "mains competent-person work"),
        ("W002", "J1-N", "Q1-N-IN", "AC_N", "1.5 mm2", "blue", 350, "mains competent-person work"),
        ("W003", "J1-PE", "X1-3", "PE", "2.5 mm2", "green/yellow", 300, "do not switch/fuse"),
        ("W004", "Q1-L-OUT", "X1-1", "AC_L_SW", "1.5 mm2", "brown", 250, "ferrules both ends"),
        ("W005", "Q1-N-OUT", "X1-2", "AC_N_SW", "1.5 mm2", "blue", 250, "ferrules both ends"),
        ("W006", "X1-1", "PS1-L", "AC_L_SW", "1.5 mm2", "brown", 350, "route left zone"),
        ("W007", "X1-2", "PS1-N", "AC_N_SW", "1.5 mm2", "blue", 350, "route left zone"),
        ("W008", "X1-3", "PS1-FG", "PE", "2.5 mm2", "green/yellow", 400, "ring/fork to verified stud"),
        ("W009", "X1-4", "lower frame bond", "PE", "2.5 mm2", "green/yellow", 1500, "star washer on dedicated bond point"),
        ("W010", "PS1 +V", "X2-1", "+24V", "14 AWG", "red", 550, "polarity check"),
        ("W011", "PS1 -V", "X2-2", "0V", "14 AWG", "black", 550, "single DC common"),
        ("W012", "X2-1", "F1", "+24V_D1", "14 AWG", "red", 300, "10A candidate"),
        ("W013", "F1", "D1 V+", "+24V_D1_FUSED", "14 AWG", "red", 450, "10A candidate"),
        ("W014", "X2-2", "D1 GND", "0V", "14 AWG", "black", 450, ""),
        ("W015", "X2-1", "F2", "+24V_D2", "14 AWG", "red", 350, "10A candidate"),
        ("W016", "F2", "D2 V+", "+24V_D2_FUSED", "14 AWG", "red", 450, "10A candidate"),
        ("W017", "X2-2", "D2 GND", "0V", "14 AWG", "black", 450, ""),
        ("W018", "X2-1", "F6-1A", "+24V_LOGIC", "24 AWG", "red", 300, "1A"),
        ("W019", "F6-1A", "U1 IN+", "+24V_LOGIC_FUSED", "24 AWG", "red", 300, ""),
        ("W020", "X2-2", "U1 IN-", "0V", "24 AWG", "black", 300, ""),
        ("W021", "U1 OUT+", "X2-9", "+5V", "24 AWG", "red", 250, "set/verify 5.00V before load"),
        ("W022", "U1 OUT-", "X2-10", "LOGIC_GND", "24 AWG", "black", 250, ""),
    ]
    motor_map = ((1, "D1-M1A", "D1-M1B"), (2, "D1-M2A", "D1-M2B"), (3, "D2-M1A", "D2-M1B"))
    wire_id = 23
    for axis, out_a, out_b in motor_map:
        wires.extend(
            (
                (f"W{wire_id:03d}", out_a, f"F-A{axis}-5A", f"MOTOR_A{axis}_A", "14 AWG", "red", 1800, "5A provisional; output fuse"),
                (f"W{wire_id+1:03d}", f"F-A{axis}-5A", f"ACT{axis}-M1", f"MOTOR_A{axis}_A_FUSED", "14 AWG", "red", 1800, "verify extension polarity"),
                (f"W{wire_id+2:03d}", out_b, f"ACT{axis}-M2", f"MOTOR_A{axis}_B", "14 AWG", "black", 1800, "verify extension polarity"),
            )
        )
        wire_id += 3
    for axis, enc_a, enc_b, pwm, direction in ((1, 2, 22, 5, 30), (2, 3, 23, 6, 31), (3, 18, 24, 7, 32)):
        for suffix, source, target, color in (
            ("V", "X2-9", f"ACT{axis}-ENC-V+", "red"),
            ("G", "X2-10", f"ACT{axis}-ENC-GND", "black"),
            ("A", f"ACT{axis}-ENC-A", f"Mega-D{enc_a}", "green"),
            ("B", f"ACT{axis}-ENC-B", f"Mega-D{enc_b}", "white"),
            ("P", f"Mega-D{pwm}", f"D{1 if axis < 3 else 2}-CH{axis if axis < 3 else 1}-PWM", "yellow"),
            ("D", f"Mega-D{direction}", f"D{1 if axis < 3 else 2}-CH{axis if axis < 3 else 1}-DIR", "blue"),
        ):
            wires.append((f"W{wire_id:03d}", source, target, f"A{axis}_{suffix}", "24 AWG", color, 2000 if suffix in "VGAB" else 600, "wire color at actuator remains supplier-TBC" if suffix in "VGAB" else ""))
            wire_id += 1
    wires.extend(
        (
            (f"W{wire_id:03d}", "Mega-D20/SDA", "GY521-SDA", "I2C_SDA", "24 AWG", "green", 500, "keep away from motor wires"),
            (f"W{wire_id+1:03d}", "Mega-D21/SCL", "GY521-SCL", "I2C_SCL", "24 AWG", "white", 500, "keep away from motor wires"),
            (f"W{wire_id+2:03d}", "X2-9", "GY521-VCC", "+5V_IMU", "24 AWG", "red", 500, "module accepts 3-5V; bench logic check"),
            (f"W{wire_id+3:03d}", "X2-10", "GY521-GND", "IMU_GND", "24 AWG", "black", 500, ""),
            (f"W{wire_id+4:03d}", "X2-9", "Mega-5V", "+5V_MEGA", "24 AWG", "red", 350, "USB VBUS must be disconnected when externally powered"),
            (f"W{wire_id+5:03d}", "X2-10", "Mega-GND", "LOGIC_GND", "24 AWG", "black", 350, ""),
            (f"W{wire_id+6:03d}", "Mega-D8", "D2-CH2-PWM", "UNUSED_PWM", "24 AWG", "yellow", 350, "firmware holds 0"),
            (f"W{wire_id+7:03d}", "Mega-D33", "D2-CH2-DIR", "UNUSED_DIR", "24 AWG", "blue", 350, "firmware holds low"),
        )
    )
    wire_rows = [dict(zip(("wire_id", "from", "to", "net", "wire_size", "color", "cut_length_mm", "note"), row)) for row in wires]
    write_csv(ELEC / "RevE_point_to_point_wiring.csv", tuple(wire_rows[0]), wire_rows)

    harnesses = [
        {"harness": f"H-A{axis}-MOTOR", "qty": 1, "conductors": "2 x 14 AWG", "cut_length_mm_each": 1800, "service_loop_mm": 300, "termination": "ferrule/actuator supplier termination TBC", "gate": "motor colors and final enclosure position"}
        for axis in range(1, 4)
    ] + [
        {"harness": f"H-A{axis}-ENC", "qty": 1, "conductors": "4 x 24 AWG", "cut_length_mm_each": 2000, "service_loop_mm": 300, "termination": "Mega terminal/actuator supplier termination TBC", "gate": "encoder colors and levels"}
        for axis in range(1, 4)
    ] + [
        {"harness": "H-IMU", "qty": 1, "conductors": "4 x 24 AWG", "cut_length_mm_each": 500, "service_loop_mm": 100, "termination": "2.54 mm headers", "gate": "route and logic-level bench check"},
        {"harness": "H-USB-DATA", "qty": 1, "conductors": "USB data only", "cut_length_mm_each": 1500, "service_loop_mm": 100, "termination": "Type-C to PC", "gate": "VBUS red conductor disconnected when external 5V is active"},
    ]
    write_csv(ELEC / "RevE_harness_schedule.csv", tuple(harnesses[0]), harnesses)


def draw_block_schematic(pdf: canvas.Canvas) -> None:
    w, h = landscape(A4)
    pdf.setFillColor(colors.HexColor("#111827")); pdf.rect(0, h - 18*mm, w, 18*mm, fill=1, stroke=0)
    pdf.setFillColor(colors.white); pdf.setFont("Helvetica-Bold", 15); pdf.drawString(12*mm, h-11.5*mm, "REV E ELECTRICAL RC | POWER AND CONTROL SCHEMATIC")
    boxes = [
        (15, 125, 35, 24, "220 VAC\nJ1"), (62, 125, 35, 24, "Q1\n2P 10A"), (110, 125, 50, 24, "PS1\n24V 14.6A"),
        (178, 155, 35, 18, "F1 10A"), (178, 125, 35, 18, "F2 10A"), (178, 95, 35, 18, "F6 1A"),
        (230, 150, 46, 26, "D1 MDD10A\nAXIS 1/2"), (230, 115, 46, 26, "D2 MDD10A\nAXIS 3"),
        (230, 78, 46, 20, "U1 24->5V"), (173, 45, 48, 24, "Mega2560\nUSB host"), (232, 45, 44, 24, "MPU6050\nD20/D21"),
    ]
    pdf.setFillColor(colors.HexColor("#f9fafb")); pdf.setStrokeColor(colors.HexColor("#374151")); pdf.setFont("Helvetica-Bold", 8)
    for x,y,bw,bh,label in boxes:
        pdf.rect(x*mm,y*mm,bw*mm,bh*mm,fill=1,stroke=1)
        pdf.setFillColor(colors.HexColor("#111827"))
        for line_i,line in enumerate(label.split("\n")):
            pdf.drawCentredString((x+bw/2)*mm,(y+bh/2+3-line_i*5)*mm,line)
        pdf.setFillColor(colors.HexColor("#f9fafb"))
    arrows = [((50,137),(62,137)),((97,137),(110,137)),((160,137),(178,164)),((160,137),(178,134)),((160,137),(178,104)),((213,164),(230,163)),((213,134),(230,128)),((213,104),(230,88)),((253,78),(197,69)),((221,57),(232,57))]
    pdf.setLineWidth(1.2)
    for (x1,y1),(x2,y2) in arrows:
        pdf.line(x1*mm,y1*mm,x2*mm,y2*mm)
    pdf.setFont("Helvetica", 7.5); pdf.setFillColor(colors.HexColor("#111827"))
    pdf.drawString(15*mm,25*mm,"D1 outputs: A1/A2 through one 5A output fuse per actuator. D2 CH1: A3. D2 CH2: PWM=0 and DIR=LOW.")
    pdf.drawString(15*mm,19*mm,"External 5V powers Mega/encoders/IMU. Disconnect USB VBUS when the PC data cable is connected.")
    pdf.drawString(15*mm,13*mm,"RC only: current ratings, actuator wiring, and regeneration behavior remain commissioning gates.")
    pdf.showPage()


def draw_layout_pdf(pdf: canvas.Canvas) -> None:
    w, h = landscape(A4)
    pdf.setFillColor(colors.HexColor("#111827")); pdf.rect(0,h-18*mm,w,18*mm,fill=1,stroke=0)
    pdf.setFillColor(colors.white); pdf.setFont("Helvetica-Bold",15); pdf.drawString(12*mm,h-11.5*mm,"REV E ELECTRICAL RC | SL902 BACKPLATE LAYOUT")
    ox, oy, scale = 35*mm, 25*mm, 0.32*mm
    pdf.setFillColor(colors.HexColor("#f3f4f6")); pdf.setStrokeColor(colors.HexColor("#111827")); pdf.rect(ox,oy,400*scale,500*scale,fill=1,stroke=1)
    palette={"220 VAC":"#b91c1c","AC/DC boundary":"#4b5563","24 VDC":"#ea580c","24 V power":"#ea580c","5 V logic":"#0284c7","24/5 VDC":"#16a34a"}
    for d in DEVICES:
        pdf.setFillColor(colors.HexColor(palette[d.zone])); pdf.rect(ox+d.x*scale,oy+d.y*scale,d.width*scale,d.height*scale,fill=1,stroke=0)
        pdf.setFillColor(colors.white); pdf.setFont("Helvetica-Bold",6); pdf.drawCentredString(ox+(d.x+d.width/2)*scale,oy+(d.y+d.height/2)*scale,d.ref)
    tx=185*mm; ty=175*mm; pdf.setFillColor(colors.HexColor("#111827")); pdf.setFont("Helvetica-Bold",10); pdf.drawString(tx,ty,"LAYOUT RULES")
    pdf.setFont("Helvetica",8)
    notes=["External enclosure: 400x500x155 mm","Assumed usable plate: 360x460 mm","DIN rail: 320 mm x 2, verify before cut","AC-to-logic corridor: 60 mm","Bottom glands X: 30/150/190/230/280/320/360","PS1 official envelope: 215x115x30 mm","MDD10A official envelope: 84.5x62 mm","All mounting holes: verify physical parts","Keep motor and encoder cable routes separate","Provide tool access and a free-air path above drivers"]
    for n in notes:
        ty-=7*mm; pdf.drawString(tx,ty,n)
    pdf.setFillColor(colors.HexColor("#991b1b")); pdf.setFont("Helvetica-Bold",8)
    pdf.drawString(185*mm,24*mm,"NOT RELEASED FOR ENCLOSURE DRILLING")
    pdf.drawString(185*mm,19*mm,"Verify physical backplate and all mounting holes first.")
    pdf.showPage()


def draw_pinmap_pdf(pdf: canvas.Canvas) -> None:
    w,h=landscape(A4); pdf.setFillColor(colors.HexColor("#111827")); pdf.rect(0,h-18*mm,w,18*mm,fill=1,stroke=0)
    pdf.setFillColor(colors.white); pdf.setFont("Helvetica-Bold",15); pdf.drawString(12*mm,h-11.5*mm,"REV E ELECTRICAL RC | MEGA2560 I/O AND TERMINAL MAP")
    pdf.setFillColor(colors.HexColor("#111827")); pdf.setFont("Helvetica-Bold",9)
    cols=(15,62,110,170,225); headers=("FUNCTION","MEGA","DESTINATION","TYPE","STATUS")
    for x,label in zip(cols,headers): pdf.drawString(x*mm,175*mm,label)
    rows=[("ENC1 A/B","D2/D22","ACT1 encoder","5V pulse","wire TBC"),("ENC2 A/B","D3/D23","ACT2 encoder","5V pulse","wire TBC"),("ENC3 A/B","D18/D24","ACT3 encoder","5V pulse","wire TBC"),("PWM 1/2/3","D5/D6/D7","D1 CH1/CH2, D2 CH1","output","locked"),("DIR 1/2/3","D30/D31/D32","D1 CH1/CH2, D2 CH1","output","locked"),("IMU SDA/SCL","D20/D21","GY-521","I2C","bench verify"),("UNUSED CH4","D8/D33","D2 CH2","PWM0/DIR0","locked")]
    pdf.setFont("Helvetica",8); y=164
    for row in rows:
        for x,value in zip(cols,row): pdf.drawString(x*mm,y*mm,value)
        y-=11
    pdf.setFont("Helvetica-Bold",9); pdf.drawString(15*mm,75*mm,"TERMINALS")
    pdf.setFont("Helvetica",7.5); terms=["X1-1/2: switched AC L/N to PS1","X1-3/4: PE star point, PS1 FG, DIN rail/lower frame bond","X2-1/2: +24V/0V source","X2-3/4: fused D1 +24V/0V","X2-5/6: fused D2 +24V/0V","X2-7/8: fused buck input +24V/0V","X2-9/10: +5V/logic common"]
    y=64
    for term in terms: pdf.drawString(15*mm,y*mm,term); y-=7
    pdf.setFillColor(colors.HexColor("#991b1b")); pdf.setFont("Helvetica-Bold",8); pdf.drawString(150*mm,25*mm,"SUPPLIER ENCODER COLORS/LEVELS AND CURRENT DATA ARE OPEN RELEASE GATES")
    pdf.showPage()


def write_electrical_pdf() -> None:
    pdf = canvas.Canvas(str(PDF_OUT), pagesize=landscape(A4), pageCompression=1)
    pdf.setTitle("Profile Radial 3-RPS Rev E Electrical Drawings RC")
    draw_block_schematic(pdf); draw_layout_pdf(pdf); draw_pinmap_pdf(pdf)
    pdf.save()


def write_design_note(layout: dict, subtotal: int) -> None:
    note = f"""# Rev E electrical detailed design - release candidate\n\n+Date: 2026-09-04  \n+Status: `ELECTRICAL_DETAIL_RC_COMPLETE`, `POWER_RELEASE=FALSE`, `PURCHASE_RELEASE=FALSE`\n+\n+## Architecture\n+\n+One Mega2560-compatible board commands three brushed-DC axes through two Cytron MDD10A boards. D1 uses both channels for axes 1 and 2; D2 uses channel 1 for axis 3 and its fourth channel is hard-commanded to PWM 0. The IMU is a GY-521/MPU6050 on I2C. The PC or available Jetson Nano is optional for USB commands and logging; the real-time loop runs on the Mega.\n+\n+The MDD10A has one shared motor-supply input per two-channel board. Therefore this revision adds two provisional 10 A board-input fuses, while the three existing 5 A fuses are placed in one output lead per actuator. All fuse ratings remain blocked until startup, running, stall, and lowering-regeneration measurements are available.\n+\n+## Enclosure result\n+\n+- External enclosure: 400 x 500 x 155 mm.\n+- Device envelopes in assumed 360 x 460 x 127 mm usable space: {layout['device_count']}.\n+- Component overlap pairs: {len(layout['component_overlap_pairs'])}.\n+- AC-to-logic planar separation: {layout['ac_to_logic_planar_segregation_mm']} mm, requirement 50 mm.\n+- DIN rail cut seed: 320 mm x 2.\n+- Envelope audit: {'PASS' if layout['passes_layout_envelope'] else 'FAIL'}.\n+- Drilling release: FALSE until the SL902 backplate and board hole patterns are physically verified.\n+\n+## Power and grounding\n+\n+The 230 VAC input passes through the accessible 2-pole breaker to the LRS-350-24. Protective earth goes directly to the PSU FG terminal and dedicated metal-bond points; it is never switched or fused. The ABS enclosure does not replace protective bonding of the PSU, DIN rail, or lower aluminum frame. AC, motor-power, and logic routes are physically separated.\n+\n+The regulated 5 V branch powers the Mega 5 V rail, encoders, and GY-521. When external 5 V is connected, the USB cable must be data-only with VBUS disconnected to prevent two 5 V sources from opposing each other. The exact TS0481 power-selector behavior must be verified on receipt.\n+\n+## Candidate BOM budget\n+\n+- Known screen-price subtotal including the added input fuses: {subtotal:,} KRW.\n+- 3.6M target margin before machining, freight, and open quotes: {TARGET_KRW - subtotal:,} KRW.\n+- 4.0M absolute-budget margin before machining, freight, and open quotes: {BUDGET_KRW - subtotal:,} KRW.\n+\n+This subtotal is not a final quotation and does not authorize purchase.\n+\n+## Mandatory release gates\n+\n+1. Written actuator current, encoder, limit, and duty-cycle data or a measured first article.\n+2. One-axis unloaded startup/running/stall-protected current and 24 V bus peak measurement.\n+3. MDD10A channel current below 8 A continuous and total PSU demand below 11.68 A.\n+4. Lowering/braking bus peak at or below 28 V.\n+5. Physical enclosure/backplate, PCB mounting holes, terminal covers, bend radius, and tool access verified.\n+6. Competent-person review of all 230 VAC work before energization.\n+\n+Source basis: Cytron MDD10A manufacturer page (5-30 V Rev2.0, 10 A continuous/channel, 30 A peak, regeneration, 84.5 x 62 mm) and Mean Well LRS-350 official datasheet (24 V, 14.6 A, 215 x 115 x 30 mm).\n+"""
    (ELEC / "RevE_electrical_detailed_design_RC_2026-09-04.md").write_text(note, encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> int:
    ensure_dirs()
    interfaces = build_interface_register()
    write_rfqs()
    rows, subtotal = build_candidate_bom()
    layout = build_enclosure_cad()
    render_layout()
    wiring_tables()
    write_electrical_pdf()
    write_design_note(layout, subtotal)
    result = {
        "revision": "E-RC1",
        "supplier_interface_count": len(interfaces),
        "open_supplier_interfaces": sum(1 for row in interfaces if row["confidence"] == "OPEN"),
        "candidate_bom_rows": len(rows),
        "known_subtotal_krw": subtotal,
        "target_margin_krw": TARGET_KRW - subtotal,
        "absolute_budget_margin_krw": BUDGET_KRW - subtotal,
        "enclosure_layout_pass": layout["passes_layout_envelope"],
        "purchase_release": False,
        "power_release": False,
    }
    (OUT / "RevE_electrical_build_summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    artifacts = [path for path in OUT.rglob("*") if path.is_file()] + [PDF_OUT]
    manifest = {"revision": "E-RC1", "artifacts": [{"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": sha256(path)} for path in sorted(artifacts)]}
    (OUT / "RevE_electrical_artifact_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
