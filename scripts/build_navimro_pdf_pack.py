"""Build and visually stable PDF drawing/assembly packs for NAVIMRO Rev A."""

import csv
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A3, A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle

from cad.navimro_fabrication_exports import FLATBAR_PARTS, PROFILE_CUTS, flatbar_usage_mm
from cad.navimro_fabrication_parameters import N
from calculations.navimro_fabrication_budget import ALLOWANCES, budget_summary
from calculations.navimro_fabrication_verification import verification_results


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output" / "pdf"
RENDER_DIR = ROOT / "outputs" / "navimro_fabrication" / "renders"
BOM_PATH = ROOT / "procurement" / "navimro_single_order_bom.csv"
REV = "A"
DATE = "2026-08-27"

NAVY = colors.HexColor("#16334A")
TEAL = colors.HexColor("#2B7A78")
CYAN = colors.HexColor("#D9F0F2")
LIGHT = colors.HexColor("#F2F5F7")
MID = colors.HexColor("#D2DCE2")
ORANGE = colors.HexColor("#D98324")
RED = colors.HexColor("#B33A2B")
INK = colors.HexColor("#17232D")


def register_fonts():
    regular = Path("C:/Windows/Fonts/malgun.ttf")
    bold = Path("C:/Windows/Fonts/malgunbd.ttf")
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont("Doc", str(regular)))
        pdfmetrics.registerFont(TTFont("DocBold", str(bold)))
    else:
        pdfmetrics.registerFont(TTFont("Doc", str(regular)))
        pdfmetrics.registerFont(TTFont("DocBold", str(regular)))


def styles():
    return {
        "body": ParagraphStyle("body", fontName="Doc", fontSize=8.5, leading=12, textColor=INK),
        "small": ParagraphStyle("small", fontName="Doc", fontSize=7, leading=9, textColor=INK),
        "tiny": ParagraphStyle("tiny", fontName="Doc", fontSize=6.2, leading=7.5, textColor=INK),
        "head": ParagraphStyle("head", fontName="DocBold", fontSize=13, leading=16, textColor=NAVY),
        "center": ParagraphStyle("center", fontName="Doc", fontSize=8, leading=10, alignment=TA_CENTER, textColor=INK),
    }


S = None


def p(text, style="body"):
    return Paragraph(str(text), S[style])


def draw_paragraph(c, text, x, y_top, width, height, style="body"):
    paragraph = p(text, style)
    _, h = paragraph.wrap(width, height)
    paragraph.drawOn(c, x, y_top - h)
    return h


def draw_table(c, rows, x, y_top, widths, row_heights=None, font_size=7.0, header=True, max_height=500):
    data = []
    for row_index, row in enumerate(rows):
        style = "tiny" if font_size <= 6.5 else "small"
        data.append([cell if isinstance(cell, Paragraph) else p(cell, style) for cell in row])
    table = Table(data, colWidths=widths, rowHeights=row_heights, repeatRows=1 if header else 0)
    commands = [
        ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#82939F")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
    ]
    if header:
        commands.extend([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "DocBold"),
        ])
    for i in range(1 if header else 0, len(rows)):
        if i % 2 == 0:
            commands.append(("BACKGROUND", (0, i), (-1, i), LIGHT))
    table.setStyle(TableStyle(commands))
    _, h = table.wrap(sum(widths), max_height)
    table.drawOn(c, x, y_top - h)
    return h


def draw_image(c, path, x, y, width, height):
    path = Path(path)
    if not path.exists():
        c.setStrokeColor(RED)
        c.rect(x, y, width, height)
        draw_paragraph(c, f"Missing image: {path.name}", x + 8, y + height - 8, width - 16, height - 16, "small")
        return
    image = ImageReader(str(path))
    iw, ih = image.getSize()
    scale = min(width / iw, height / ih)
    w, h = iw * scale, ih * scale
    c.drawImage(image, x + (width - w) / 2.0, y + (height - h) / 2.0, width=w, height=h, mask="auto")


def title_block(c, page_no, title, sheet_size):
    width, _ = sheet_size
    y = 18
    c.setStrokeColor(NAVY)
    c.setLineWidth(0.8)
    c.rect(24, y, width - 48, 42)
    c.line(width - 310, y, width - 310, y + 42)
    c.line(width - 175, y, width - 175, y + 42)
    c.setFont("DocBold", 9)
    c.setFillColor(NAVY)
    c.drawString(32, y + 25, "NAVIMRO RADIAL-3 LEVELING MODULE")
    c.setFont("Doc", 7)
    c.setFillColor(INK)
    c.drawString(32, y + 11, title)
    c.drawString(width - 300, y + 25, f"REV {REV} | {DATE}")
    c.drawString(width - 300, y + 11, "Units: mm | Prototype bench rig")
    c.drawString(width - 165, y + 25, f"SHEET {page_no}")
    c.drawString(width - 165, y + 11, "Verify transfer holes")


def page_header(c, heading, subheading, sheet_size):
    width, height = sheet_size
    c.setFillColor(NAVY)
    c.rect(24, height - 64, width - 48, 40, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("DocBold", 16)
    c.drawString(38, height - 47, heading)
    c.setFont("Doc", 8)
    c.drawRightString(width - 38, height - 46, subheading)


def finish_page(c, page_no, title, sheet_size):
    title_block(c, page_no, title, sheet_size)
    c.showPage()


def cover_page(c, sheet_size, assembly_image):
    width, height = sheet_size
    c.setFillColor(NAVY)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("DocBold", 28)
    c.drawString(56, height - 92, "NAVIMRO RADIAL-3")
    c.setFont("DocBold", 22)
    c.drawString(56, height - 126, "제작 CAD 및 가공도면 패키지")
    c.setFont("Doc", 11)
    c.drawString(58, height - 154, "10 kg payload | Z 100 mm | pitch/roll +/-3 deg | stationary proof-of-concept")
    c.setFillColor(colors.white)
    c.roundRect(54, 92, width - 108, height - 285, 4, fill=1, stroke=0)
    draw_image(c, assembly_image, 66, 104, width - 132, height - 309)
    c.setFillColor(colors.HexColor("#F3C969"))
    c.setFont("DocBold", 11)
    c.drawString(58, 58, "REV A - 공급품 실측 전 vendor mounting holes는 가공하지 않음")
    c.setFillColor(colors.white)
    c.setFont("Doc", 8)
    c.drawRightString(width - 58, 58, f"{DATE} | Sheet 1")
    c.showPage()


def dimension_line(c, x1, y1, x2, y2, label, offset=0):
    c.setStrokeColor(NAVY)
    c.setFillColor(NAVY)
    c.setLineWidth(0.6)
    c.line(x1, y1 + offset, x2, y2 + offset)
    c.line(x1, y1 + offset - 4, x1, y1 + offset + 4)
    c.line(x2, y2 + offset - 4, x2, y2 + offset + 4)
    c.setFont("Doc", 7)
    c.drawCentredString((x1 + x2) / 2.0, (y1 + y2) / 2.0 + offset + 3, label)


def general_arrangement_page(c, page_no, sheet_size):
    width, height = sheet_size
    page_header(c, "GA-01 전체 조립 및 기준치수", "900 x 800 platform | collapsed overall 300", sheet_size)
    draw_image(c, RENDER_DIR / "navimro_front.png", 30, 345, 545, 410)
    draw_image(c, RENDER_DIR / "navimro_top.png", 590, 345, 565, 410)
    dimension_line(c, 115, 355, 490, 355, "900")
    dimension_line(c, 675, 355, 1070, 355, "800")
    rows = [
        ("항목", "기준값", "비고"),
        ("상판 외형", "900 x 800 x 15", "투명 아크릴, 비구조 덮개"),
        ("접힘 전체 높이", "300", "가이드축 하부 5 mm 포함"),
        ("상판 joint plane", "Z=235 접힘 / Z=335 상승", "상부 프레임 중심면"),
        ("상부 관절 반경", "R400", "0/120/240 deg"),
        ("하부 관절 반경", "R175", "상부와 같은 방사각"),
        ("가이드축", "2 x Ø12 x 240", "X=+/-60, 움직이는 축"),
        ("허용 운동", "Z, pitch, roll", "X/Y/yaw는 twin guide가 구속"),
    ]
    draw_table(c, rows, 45, 320, [170, 185, 315], font_size=7.0, max_height=230)
    draw_paragraph(c, "연결된 cart-side 4040 receiver rail은 카트 쪽 인터페이스 부품이며, 수평유지장치 단독 높이 산정에서 제외한다. 실제 카트 본체 치수와 구멍은 본 도면에서 정의하지 않는다.", 750, 315, 390, 100, "small")
    finish_page(c, page_no, "GA-01 GENERAL ARRANGEMENT", sheet_size)


def kinematics_page(c, page_no, sheet_size, verification):
    width, height = sheet_size
    page_header(c, "KIN-01 액추에이터 배치 및 작업영역", "DHLA2000 pin/lug planning envelope", sheet_size)
    draw_image(c, RENDER_DIR / "navimro_top.png", 35, 335, 600, 435)
    upper = list(N.upper_points_xy)
    lower = list(N.lower_points_xy)
    rows = [("Axis", "Lower joint X,Y,Z", "Upper joint local X,Y,Z", "Radial angle")]
    for i, ((lx, ly), (ux, uy)) in enumerate(zip(lower, upper), start=1):
        rows.append((f"A{i}", f"{lx:.1f}, {ly:.1f}, {N.base_joint_z_mm:.1f}", f"{ux:.1f}, {uy:.1f}, 0", f"{(i-1)*120} deg"))
    draw_table(c, rows, 660, 730, [65, 165, 185, 90], font_size=7.0, max_height=180)
    w = verification["workspace"]
    checks = [
        ("검토", "값"),
        ("전체 corner sweep", f"{w['minimum_pin_length_mm']:.3f} - {w['maximum_pin_length_mm']:.3f} mm"),
        ("가정 pin-center 범위", f"{N.actuator_min_pin_length_mm:.0f} - {N.actuator_max_pin_length_mm:.0f} mm"),
        ("수축 여유", f"{w['retraction_margin_mm']:.3f} mm"),
        ("신장 여유", f"{w['extension_margin_mm']:.3f} mm"),
        ("명령 범위", "Z 0-100 mm, pitch/roll +/-3 deg"),
    ]
    draw_table(c, checks, 660, 545, [220, 285], font_size=7.0, max_height=180)
    c.setFillColor(colors.HexColor("#FFF2D8"))
    c.roundRect(660, 330, 505, 150, 4, fill=1, stroke=0)
    draw_paragraph(c, "발주 전 필수 확인", 680, 455, 465, 30, "head")
    draw_paragraph(c, "상품 상세 이미지는 A1 본체와 M8/Ø10 부속을 보여 주지만, pin-center 최소/최대 길이와 실제 eye 폭/구멍은 표에 없다. 공급사 회신값이 255-405 mm 가정을 만족하지 않으면 상부/하부 반경 또는 joint Z를 다시 계산해야 한다.", 680, 420, 465, 90, "body")
    finish_page(c, page_no, "KIN-01 ACTUATOR LAYOUT", sheet_size)


def guide_page(c, page_no, sheet_size):
    width, height = sheet_size
    page_header(c, "GUIDE-01 중앙 가이드 및 Cardan", "moving shafts / fixed bushings / independent stops", sheet_size)
    draw_image(c, RENDER_DIR / "navimro_guide_detail.png", 38, 185, 650, 575)
    rows = [
        ("Part", "Qty", "Datum / dimension", "Assembly note"),
        ("Ø12 guide shaft", "2", "L=240, X=+/-60", "상판과 함께 움직임"),
        ("LMF12UU", "4", "fixed Z=110,150", "입고품으로 transfer-drill"),
        ("SK12", "4", "moving Z=platform-70,-25", "축을 상부 carriage에 고정"),
        ("Z stop collar", "4", "moving offsets -165,-125", "fixed bumper Z=70,210과 접촉"),
        ("Cardan cross", "1", "50x50x36 laminate", "50x50x6 6장 적층"),
        ("Cardan trunnion", "4", "M8 opposed", "두 축이 같은 중심을 공유"),
        ("Angle stop", "4", "M8 adjustable", "명령 +/-3 deg보다 바깥에서 설정"),
    ]
    draw_table(c, rows, 710, 735, [105, 55, 165, 270], font_size=6.5, max_height=340)
    c.setFillColor(CYAN)
    c.roundRect(710, 245, 405, 170, 4, fill=1, stroke=0)
    draw_paragraph(c, "조립 순서", 730, 390, 365, 28, "head")
    draw_paragraph(c, "1) 두 riser를 lower frame에 직각 고정. 2) LMF12UU 네 개를 축을 통과시킨 상태로 clamp 후 transfer-drill. 3) 상부 carriage의 SK12 네 개를 같은 축 위에서 조임. 4) 무전원으로 0-100 mm 왕복해 binding이 없는 위치에서 최종 체결. 5) collar와 angle stop은 소프트 한계보다 약간 바깥에서 맞춘다.", 730, 355, 365, 105, "body")
    finish_page(c, page_no, "GUIDE-01 CENTRAL GUIDE", sheet_size)


def profile_cut_page(c, page_no, sheet_size):
    width, height = sheet_size
    page_header(c, "CUT-01 프로파일 및 축 절단표", "square cut unless noted", sheet_size)
    rows = [("Part", "Name", "Material", "L", "Qty", "End finish")]
    for row in PROFILE_CUTS:
        rows.append((row[0], row[1], row[2], f"{row[3]:.0f}", str(row[4]), row[5]))
    draw_table(c, rows, 55, 735, [90, 210, 220, 70, 60, 180], font_size=7.0, max_height=500)
    draw_paragraph(c, "4040 총 18개, 총 길이 11,000 mm. 절단면 직각도와 길이공차는 공급사 절단품 기준으로 검사하고, 조립 직전 모든 모서리를 디버링한다. Ø12 경화축은 드릴 가공하지 않고 240 mm로 절단 후 단면만 디버링한다.", 720, 700, 395, 120, "body")
    draw_paragraph(c, "Profile identification", 720, 550, 395, 30, "head")
    y = 510
    for part, name, _, length, qty, _ in PROFILE_CUTS:
        c.setFillColor(MID)
        c.rect(730, y, min(330, length * 0.35), 18, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("Doc", 7)
        c.drawString(735, y + 5, f"{part}  {length:.0f} mm x {qty}")
        y -= 31
    finish_page(c, page_no, "CUT-01 PROFILE CUT LIST", sheet_size)


def flatbar_cut_page(c, page_no, sheet_size):
    width, height = sheet_size
    page_header(c, "CUT-02 50x6 SS400 평철 절단표", "2 bars x 6000 | one bar retained as rework stock", sheet_size)
    rows = [("Part", "Name", "L", "Qty", "Feature", "Transfer")]
    for part in FLATBAR_PARTS:
        rows.append((part.part_no, part.name, f"{part.length_mm:.0f}", str(part.quantity), part.feature, part.vendor_holes))
    draw_table(c, rows, 45, 735, [75, 205, 55, 50, 210, 70], font_size=6.2, max_height=590)
    cut, kerf, reserve = flatbar_usage_mm()
    c.setFont("DocBold", 9)
    c.setFillColor(NAVY)
    c.drawString(740, 705, f"Cut total {cut:.0f} + kerf {kerf:.0f} = {cut+kerf:.0f} mm")
    c.drawString(740, 684, f"Reserve from 12,000 mm stock = {reserve:.0f} mm")
    bar_x, bar_w = 745, 350
    y = 620
    used_first = min(6000.0, cut + kerf)
    for index, used in enumerate((used_first, max(0.0, cut + kerf - 6000.0)), start=1):
        c.setFillColor(MID)
        c.rect(bar_x, y, bar_w, 32, fill=1, stroke=0)
        c.setFillColor(TEAL)
        c.rect(bar_x, y, bar_w * used / 6000.0, 32, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("Doc", 7)
        c.drawString(bar_x + 5, y + 11, f"BAR {index}: used {used:.0f} / 6000")
        y -= 58
    draw_paragraph(c, "두 번째 평철은 Cardan 적층 블록, transfer-drill 수정, latch keeper 재가공을 위한 의도적 여분이다. 1차 절단은 NVR-P01-P14 표에 따라 진행하되 vendor transfer 부품은 외형 절단까지만 하고 구멍은 뚫지 않는다.", 740, 460, 375, 120, "body")
    finish_page(c, page_no, "CUT-02 FLAT BAR CUT LIST", sheet_size)


def draw_slot(c, cx, cy, length, width):
    c.roundRect(cx - length / 2.0, cy - width / 2.0, length, width, width / 2.0, fill=0, stroke=1)


def part_sketch(c, part, x, y, w, h):
    c.setStrokeColor(colors.HexColor("#6B7E8A"))
    c.setFillColor(colors.white)
    c.rect(x, y, w, h, fill=1, stroke=1)
    scale = min((w - 36) / part.length_mm, (h - 54) / N.flatbar_width_mm)
    length = part.length_mm * scale
    width = N.flatbar_width_mm * scale
    px = x + (w - length) / 2.0
    py = y + 28 + (h - 54 - width) / 2.0
    c.setStrokeColor(NAVY)
    c.setLineWidth(0.8)
    c.rect(px, py, length, width, fill=0, stroke=1)
    cx, cy = px + length / 2.0, py + width / 2.0
    if part.feature == "two_24x11_slots":
        draw_slot(c, cx - 35 * scale, cy, 24 * scale, 11 * scale)
        draw_slot(c, cx + 35 * scale, cy, 24 * scale, 11 * scale)
    elif part.feature in ("pivot_8.5_root_8.5",):
        c.circle(cx - 20 * scale, cy, 4.25 * scale)
        c.circle(cx + 20 * scale, cy - 14 * scale, 4.25 * scale)
        c.circle(cx + 20 * scale, cy + 14 * scale, 4.25 * scale)
    elif part.feature == "two_24x9_slots":
        draw_slot(c, cx - 30 * scale, cy, 24 * scale, 9 * scale)
        draw_slot(c, cx + 30 * scale, cy, 24 * scale, 9 * scale)
    elif part.feature in ("four_8.5_holes",):
        for dx in (-15, 15):
            for dy in (-14, 14):
                c.circle(cx + dx * scale, cy + dy * scale, 4.25 * scale)
    elif part.feature == "one_11_hole_two_9_slots":
        c.circle(cx, cy, 5.5 * scale)
        draw_slot(c, cx - 38 * scale, cy, 18 * scale, 9 * scale)
        draw_slot(c, cx + 38 * scale, cy, 18 * scale, 9 * scale)
    elif part.vendor_holes == "YES":
        c.setDash(3, 2)
        c.line(cx - length / 2.0 + 8, cy, cx + length / 2.0 - 8, cy)
        c.setDash()
    c.setFillColor(NAVY)
    c.setFont("DocBold", 7)
    c.drawString(x + 7, y + h - 13, f"{part.part_no} {part.name}")
    c.setFont("Doc", 6)
    c.setFillColor(INK)
    c.drawString(x + 7, y + 8, f"{part.length_mm:.0f} x 50 x 6 | QTY {part.quantity} | {part.feature}")


def part_sheet(c, page_no, sheet_size, parts, sheet_code):
    width, height = sheet_size
    page_header(c, f"{sheet_code} 평철 부품 템플릿", "DXF controls CNC geometry; print is reference only", sheet_size)
    cols, rows_count = 2, 4
    cell_w, cell_h = 550, 140
    start_x, start_y = 40, 570
    for index, part in enumerate(parts):
        col = index % cols
        row = index // cols
        part_sketch(c, part, start_x + col * 575, start_y - row * 150, cell_w, cell_h)
    draw_paragraph(c, "공통: SS400 50x6, 절단 및 천공 후 양면 디버링, 모서리 C0.5 수준. DXF의 CUT_OUTER/CUT_HOLES만 가공하고 REFERENCE/NOTES layer는 가공하지 않는다. Transfer 표기 부품은 외형만 절단한다.", 45, 90, 1090, 35, "small")
    finish_page(c, page_no, f"{sheet_code} FLAT-BAR PART TEMPLATES", sheet_size)


def acrylic_page(c, page_no, sheet_size):
    width, height = sheet_size
    page_header(c, "PANEL-01 상부 아크릴 덮개", "NVR-U02 | 900 x 800 x 15 clear PMMA", sheet_size)
    x, y, w, h = 80, 190, 760, 520
    c.setFillColor(colors.HexColor("#D9F5F7"))
    c.setStrokeColor(NAVY)
    c.rect(x, y, w, h, fill=1, stroke=1)
    sx, sy = w / N.platform_length_mm, h / N.platform_width_mm
    holes = set()
    for hx in (-400.0, -200.0, 0.0, 200.0, 400.0):
        holes.add((hx, -350.0)); holes.add((hx, 350.0))
    for hy in (-175.0, 0.0, 175.0):
        holes.add((-400.0, hy)); holes.add((400.0, hy))
    for hx, hy in holes:
        c.circle(x + w/2 + hx*sx, y + h/2 + hy*sy, 4.25*min(sx,sy), fill=0, stroke=1)
    c.circle(x+w/2-N.locator_x_mm*sx, y+h/2, 5.5*min(sx,sy), fill=0, stroke=1)
    draw_slot(c, x+w/2+N.locator_x_mm*sx, y+h/2, 24*sx, 11*sy)
    dimension_line(c, x, y-20, x+w, y-20, "900")
    dimension_line(c, x+w+25, y, x+w+25, y+h, "800")
    rows = [
        ("Feature", "Coordinates from panel center", "Size"),
        ("Perimeter attachment", "X=-400,-200,0,200,400 at Y=+/-350; X=+/-400 at Y=-175,0,175", "Ø8.5 THRU"),
        ("Master locator", "X=-260, Y=0", "Ø11 THRU"),
        ("Secondary locator", "X=+260, Y=0", "24 x 11 slot"),
        ("CR-3001 mounting", "Not pre-drilled", "Transfer from delivered clamp"),
    ]
    draw_table(c, rows, 875, 700, [130, 210, 120], font_size=6.5, max_height=260)
    draw_paragraph(c, "아크릴은 구조 하중을 직접 전달하지 않는다. actuator spreader, locator, latch 체결부는 반드시 하부 4040 프레임 또는 6 mm steel spreader까지 관통 체결하고 아크릴을 압축 스페이서로 보호한다.", 880, 385, 250, 130, "body")
    finish_page(c, page_no, "PANEL-01 ACRYLIC DECK", sheet_size)


def coupling_page(c, page_no, sheet_size):
    width, height = sheet_size
    page_header(c, "COUPLING-01 카트 기계 인터페이스", "mechanical locating and latching only", sheet_size)
    draw_image(c, RENDER_DIR / "navimro_neutral_iso.png", 30, 250, 670, 505)
    rows = [
        ("Element", "Nominal location", "Function"),
        ("Master round locator", "X=-260, Y=0", "X/Y datum"),
        ("Secondary relieved locator", "X=+260, Y=0", "Y datum without over-constraint"),
        ("CR-3001 latch x4", "X=+/-330, Y=+/-260", "Draw-down preload only"),
        ("Rest pads x4", "Near latch hardpoints", "Z seating and load spread"),
        ("Cart-side rails x2", "L760, Y=+/-260", "Loose interface pieces supplied for cart adaptation"),
    ]
    draw_table(c, rows, 730, 720, [165, 170, 245], font_size=7.0, max_height=300)
    c.setFillColor(colors.HexColor("#FCE7E2"))
    c.roundRect(730, 300, 390, 200, 4, fill=1, stroke=0)
    draw_paragraph(c, "설계 경계", 750, 475, 350, 28, "head")
    draw_paragraph(c, "본 도면은 수평유지장치와 카트 사이의 범용 결합면만 정의한다. 카트 본체, 바퀴, 구동계, 주행부는 설계하지 않는다. 실제 카트 치수는 추정하지 않으며, 760 mm receiver rail과 slotted lower tabs를 완성된 카트 구조에 맞춰 배치한다. 전자석은 주 잠금장치로 사용하지 않는다.", 750, 440, 350, 130, "body")
    finish_page(c, page_no, "COUPLING-01 CART INTERFACE", sheet_size)


def inspection_page(c, page_no, sheet_size, verification):
    width, height = sheet_size
    page_header(c, "QA-01 제작 및 입고검사 기준", "prototype release checklist", sheet_size)
    rows = [
        ("Gate", "Acceptance", "Method / record"),
        ("DHLA2000 length", "Delivered pin-center range covers 273.20-385.35", "Caliper/tape at both internal limits"),
        ("Rod-end eye", "Hole, width and M8 engagement recorded", "Photo plus measured sketch"),
        ("U/H bracket", "Free articulation, no thread in bearing plane", "Assemble one sample joint"),
        ("4040 cuts", "+/-0.5 length, square/deburred", "Tape, square, visual"),
        ("Twin guide", "Manual 0-100 sweep without binding", "No actuator connected"),
        ("Yaw constraint", "No visible rack/skew under hand load", "Both shafts engaged in all 4 bushings"),
        ("Mechanical stops", "Contact before overtravel/bushing disengagement", "Slow manual setup"),
        ("Electrical branch", "Measured inrush below driver/breaker/PSU allowance", "Clamp meter record"),
        ("Proof load", "1.25 x intended 38 kg moving mass equivalent, stationary", "Incremental test, inspect after unload"),
    ]
    draw_table(c, rows, 50, 735, [150, 390, 430], font_size=7.0, max_height=500)
    loads = verification["loads"]
    facts = [
        ("Factored load screen", f"{loads['design_vertical_load_n']:.1f} N"),
        ("Worst estimated actuator axial", f"{loads['worst_estimated_actuator_axial_force_n']:.1f} N"),
        ("Advertised actuator rating", f"{loads['actuator_rating_n']:.0f} N"),
        ("Calculated utilization", f"{loads['actuator_rating_utilization']*100:.1f}%"),
        ("Nominal actuator-guide radial gap", f"{verification['clearance']['minimum_nominal_radial_gap_mm']:.1f} mm"),
    ]
    draw_table(c, facts, 760, 300, [250, 180], font_size=7.0, max_height=180)
    draw_paragraph(c, "계산 여유는 공급품 치수, 연결부 강성, 동하중, 백래시 또는 제작오차를 인증하지 않는다. 사람 탑승, 이동 중 운전, 무인 운전에는 사용하지 않는다.", 760, 150, 360, 60, "small")
    finish_page(c, page_no, "QA-01 FABRICATION INSPECTION", sheet_size)


def build_fabrication_pdf(path):
    sheet = landscape(A3)
    c = canvas.Canvas(str(path), pagesize=sheet, pageCompression=1)
    verification = verification_results()
    cover_page(c, sheet, RENDER_DIR / "navimro_collapsed_iso.png")
    general_arrangement_page(c, 2, sheet)
    kinematics_page(c, 3, sheet, verification)
    guide_page(c, 4, sheet)
    profile_cut_page(c, 5, sheet)
    flatbar_cut_page(c, 6, sheet)
    part_sheet(c, 7, sheet, FLATBAR_PARTS[:7], "PART-01")
    part_sheet(c, 8, sheet, FLATBAR_PARTS[7:], "PART-02")
    acrylic_page(c, 9, sheet)
    coupling_page(c, 10, sheet)
    inspection_page(c, 11, sheet, verification)
    c.save()


def simple_cover(c, sheet, title, subtitle, image):
    width, height = sheet
    c.setFillColor(NAVY); c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setFillColor(colors.white); c.setFont("DocBold", 25); c.drawString(45, height-85, title)
    c.setFont("Doc", 11); c.drawString(47, height-115, subtitle)
    c.setFillColor(colors.white); c.roundRect(42, 110, width-84, height-270, 4, fill=1, stroke=0)
    draw_image(c, image, 52, 120, width-104, height-290)
    c.setFillColor(colors.HexColor("#F3C969")); c.setFont("DocBold", 10)
    c.drawString(47, 75, "한 번의 발주 전 HOLD 항목을 서면으로 닫고 총액 4,000,000원 이하를 확인")
    c.setFillColor(colors.white); c.setFont("Doc", 7); c.drawRightString(width-45, 45, f"REV {REV} | {DATE}")
    c.showPage()


def a4_header(c, heading, page_no, sheet):
    width, height = sheet
    c.setFillColor(NAVY); c.rect(24, height-56, width-48, 32, fill=1, stroke=0)
    c.setFillColor(colors.white); c.setFont("DocBold", 13); c.drawString(34, height-45, heading)
    c.setFillColor(INK); c.setFont("Doc", 7); c.drawRightString(width-28, 20, f"NAVIMRO Rev {REV} | {DATE} | {page_no}")


def a4_finish(c):
    c.showPage()


def budget_page(c, page_no, sheet):
    width, height = sheet
    a4_header(c, "1. 예산 및 단일발주 기준", page_no, sheet)
    summary = budget_summary()
    rows = [("Budget item", "KRW", "Basis"), ("NAVIMRO BOM 49 lines", f"{summary['navimro_known_subtotal_krw']:,}", "VAT included, verified prices")]
    for name, value, basis in ALLOWANCES:
        rows.append((name.replace("_", " "), f"{value:,}", basis))
    rows.extend([
        ("PLANNED TOTAL", f"{summary['planned_total_krw']:,}", "Must remain <= cap"),
        ("BUDGET CAP", f"{summary['budget_cap_krw']:,}", "User confirmed"),
        ("HEADROOM", f"{summary['headroom_krw']:,}", "Current reserve"),
    ])
    draw_table(c, rows, 38, height-85, [195, 95, 225], font_size=6.5, max_height=430)
    c.setFillColor(CYAN); c.roundRect(38, 85, width-76, 140, 4, fill=1, stroke=0)
    draw_paragraph(c, "발주 규칙", 55, 205, width-110, 25, "head")
    draw_paragraph(c, "나비엠알오 견적서에 49개 BOM 행, VAT, 장척물 운임, 출하일을 한 번에 묶는다. 현지 가공 견적과 예비비를 합쳐 400만원을 넘으면 수량을 임의로 줄이지 말고 먼저 설계를 재검토한다. 로그인 확인 가격: fan 5,489원, filter 660원.", 55, 175, width-110, 80, "body")
    a4_finish(c)


def bom_pages(c, start_page, sheet):
    with BOM_PATH.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    chunks = [rows[i:i+17] for i in range(0, len(rows), 17)]
    for chunk_index, chunk in enumerate(chunks):
        page_no = start_page + chunk_index
        a4_header(c, f"2. NAVIMRO BOM ({chunk_index+1}/{len(chunks)})", page_no, sheet)
        table_rows = [("ID", "Code", "Description", "Qty", "KRW", "Status")]
        for row in chunk:
            table_rows.append((
                row["line_id"], row["navimro_code"], row["description"], row["order_qty"],
                f"{int(row['extended_price_krw']):,}", row["order_status"].replace("READY_AFTER_DRAWING_CONFIRM", "READY_AFTER_DWG"),
            ))
        draw_table(c, table_rows, 26, sheet[1]-75, [38, 72, 230, 35, 65, 95], font_size=6.0, max_height=500)
        a4_finish(c)
    return start_page + len(chunks)


def hold_page(c, page_no, sheet):
    width, height = sheet
    a4_header(c, "3. 주문 해제 전 HOLD 체크리스트", page_no, sheet)
    rows = [
        ("Line", "Written evidence required", "Release condition"),
        ("M001", "M8/eye accessory contents, both-end geometry, pin-center Lmin/Lmax, Hall, current, STEP", "273.20-385.35 mm workspace covered"),
        ("M002/M003", "U/H bracket inner width, included pins/spacers/retainers, compatible stack", "One sample joint articulates without thread bearing"),
        ("G004", "Split-collar torque/holding data", "Bench push-off test plan accepted"),
        ("L001", "CR-3001 holding rating and keeper inclusion", "Latch used only for seating preload"),
        ("E001/E004", "Driver and PSU current margin", "Measured/declared actuator inrush accepted"),
        ("E011", "Wire reel count, length and voltage rating", "Enough red/black conductor for 3 branches"),
    ]
    draw_table(c, rows, 28, height-80, [65, 300, 170], font_size=6.5, max_height=380)
    c.setFillColor(colors.HexColor("#FCE7E2")); c.roundRect(35, 95, width-70, 120, 4, fill=1, stroke=0)
    draw_paragraph(c, "금지", 52, 195, width-104, 25, "head")
    draw_paragraph(c, "상품페이지가 존재한다는 이유만으로 주문하지 않는다. M001은 주문제작/반품불가 품목이다. 서면 회신을 프로젝트 폴더에 저장한 뒤 파라미터와 STEP를 재생성하고, 가격 포함 총액이 400만원 이하일 때 한 번에 발주한다.", 52, 165, width-104, 70, "body")
    a4_finish(c)


def incoming_page(c, page_no, sheet):
    width, height = sheet
    a4_header(c, "4. 입고검수 및 transfer-drill 기록", page_no, sheet)
    rows = [
        ("Measurement", "Target / field", "Record"),
        ("Actuator pin-center retracted", ">=255 assumption; actual ______ mm", "Photo ID ______"),
        ("Actuator pin-center extended", "<=405 assumption; actual ______ mm", "Photo ID ______"),
        ("Eye hole / width / thread engagement", "Ø____ / ____ / ____ mm", "Part count ______"),
        ("U bracket inner / outer width", "____ / ____ mm", "Pin supplied Y/N"),
        ("H bracket axis stack", "____ mm", "Free rotation Y/N"),
        ("LMF12UU flange pattern", "Transfer from actual part", "Template ID ______"),
        ("SK12 base pattern", "Transfer from actual part", "Template ID ______"),
        ("CR-3001 base and keeper", "Transfer from actual part", "Keeper included Y/N"),
    ]
    draw_table(c, rows, 30, height-80, [185, 220, 135], font_size=6.5, max_height=430)
    draw_paragraph(c, "Transfer-drill 절차: 부품을 기준면에 clamp - 축/관절이 자유롭게 움직이는지 확인 - Ø3 pilot - 최종 구멍 - 양면 디버링 - part number 각인. 웹 이미지에서 구멍 간격을 스케일링하여 사용하지 않는다.", 38, 125, width-76, 70, "body")
    a4_finish(c)


def assembly_sequence_page(c, page_no, sheet):
    width, height = sheet
    a4_header(c, "5. 기계 조립 순서", page_no, sheet)
    steps = [
        ("01", "하부 4040 frame", "820x2, 640x2, 560x2를 평판 위에서 직각 조립. lower mount tab은 카트/base 실물에 맞춰 slot 위치 조정."),
        ("02", "고정 bushing tower", "riser 2개와 LMF12UU 4개를 축 통과 상태에서 정렬. 축간거리 120 유지."),
        ("03", "moving guide", "Ø12x240 축 2개를 SK12 4개와 240 profile carriage에 결합. 무전원 Z 왕복."),
        ("04", "Cardan", "50x50x6 6장을 적층해 36 block 구성. 네 M8 trunnion과 lower/upper yoke를 동심 조립."),
        ("05", "상부 frame", "840x2, 660x2, 560x2, 420x2 조립 후 upper joint spreader를 frame에 직접 체결."),
        ("06", "actuator x3", "한 축씩 pin/lug joint 체결. 모든 자세에서 eye/rod에 굽힘이 걸리지 않는지 확인."),
        ("07", "deck/coupling", "아크릴을 cover로 장착. locator/latch 하중은 steel spreader와 4040으로 전달."),
        ("08", "stop setting", "Z collar와 Cardan M8 stop을 software +/-3 deg, Z 0-100 범위보다 바깥에서 설정."),
    ]
    y = height - 88
    for num, title, body in steps:
        c.setFillColor(TEAL); c.circle(53, y-8, 15, fill=1, stroke=0)
        c.setFillColor(colors.white); c.setFont("DocBold", 8); c.drawCentredString(53, y-11, num)
        c.setFillColor(NAVY); c.setFont("DocBold", 9); c.drawString(78, y, title)
        draw_paragraph(c, body, 78, y-14, width-115, 45, "small")
        y -= 61
    a4_finish(c)


def wiring_page(c, page_no, sheet):
    width, height = sheet
    a4_header(c, "6. 벤치 제어함 배선 개요", page_no, sheet)
    def box(x, y, w, h, label, fill=LIGHT):
        c.setFillColor(fill); c.setStrokeColor(NAVY); c.roundRect(x,y,w,h,4,fill=1,stroke=1)
        c.setFillColor(INK); c.setFont("DocBold",7); c.drawCentredString(x+w/2,y+h/2-2,label)
    box(40, 430, 80, 45, "AC CORD")
    box(155, 430, 90, 45, "2P 10A\nBREAKER")
    box(285, 420, 105, 65, "12V 29A\nPSU")
    for i, yy in enumerate((515,430,345), start=1):
        box(455, yy, 80, 42, f"DC CB {i}")
        box(575, yy, 100, 42, f"DMD-150 {i}")
        box(715, yy, 105, 42, f"ACTUATOR {i}")
        c.setStrokeColor(NAVY); c.line(390,452,455,yy+21); c.line(535,yy+21,575,yy+21); c.line(675,yy+21,715,yy+21)
    box(285, 285, 105, 48, "12V->5V\nDC-DC")
    box(455, 285, 105, 48, "MEGA2560")
    box(625, 285, 105, 48, "BNO055")
    c.setStrokeColor(NAVY); c.line(337,420,337,333); c.line(390,309,455,309); c.line(560,309,625,309)
    c.line(120,452,155,452); c.line(245,452,285,452)
    c.setStrokeColor(colors.green); c.setLineWidth(2); c.line(80,405,337,405)
    c.setFillColor(colors.green); c.setFont("DocBold",7); c.drawString(85,390,"PE: AC cord -> PSU chassis; exposed electrical metal only")
    c.setStrokeColor(ORANGE); c.setLineWidth(1)
    for yy in (515,430,345): c.line(507,285,625,yy)
    draw_paragraph(c, "DMD-150 3개는 각 actuator마다 독립 채널로 사용한다. BNO055의 pitch/roll은 supervisory control 입력이며 안전등급이 아니다. actuator current/inrush를 확인하기 전 breaker와 PSU 적합성을 확정하지 않는다. 주전원 차단은 enclosure 외부에서 접근 가능한 2P breaker로 한다.", 45, 190, width-90, 105, "body")
    a4_finish(c)


def commissioning_page(c, page_no, sheet):
    width, height = sheet
    a4_header(c, "7. 시운전 순서 및 중지 기준", page_no, sheet)
    rows = [
        ("Stage", "Action", "Stop immediately if"),
        ("A", "전원 없이 전체 Z와 +/-3 deg 수동 sweep", "binding, shaft disengagement, joint side-load"),
        ("B", "actuator 1개씩 무부하 jog", "비정상 소음, current 급상승, limit 오동작"),
        ("C", "3축 무부하 저속 동기화", "상판 rack/yaw, guide stick-slip"),
        ("D", "5 kg 균등하중", "permanent set, loose fastener, acrylic load path"),
        ("E", "10 kg payload plus 10 kg cart/interface equivalent", "joint separation, latch lift, collar slip"),
        ("F", "1.25x stationary proof load, incremental", "any yielding, crack, residual tilt"),
    ]
    draw_table(c, rows, 30, height-80, [60, 290, 190], font_size=6.5, max_height=340)
    c.setFillColor(colors.HexColor("#FFF2D8")); c.roundRect(35, 105, width-70, 180, 4, fill=1, stroke=0)
    draw_paragraph(c, "사용 제한", 52, 260, width-104, 28, "head")
    draw_paragraph(c, "정지된 시험대에서만 저속·감시하에 사용한다. 사람을 싣지 않는다. 카트가 움직이는 동안 작동하지 않는다. 무인 운전, 현장 안전 적합성, 인증은 본 패키지의 범위가 아니다. 전기적 limit과 기계적 stop 중 하나가 작동하지 않으면 다음 단계로 진행하지 않는다.", 52, 225, width-104, 105, "body")
    a4_finish(c)


def deliverables_page(c, page_no, sheet):
    width, height = sheet
    a4_header(c, "8. 산출물과 현재 결정 상태", page_no, sheet)
    rows = [
        ("Deliverable", "Location / count", "Use"),
        ("Assembly STEP", "outputs/navimro_fabrication/step - 6 states", "CAD review and interference inspection"),
        ("Flatbar DXF", "outputs/navimro_fabrication/dxf - NVR-P01..P14", "Laser/waterjet or drill templates"),
        ("Acrylic DXF", "NVR-U02_upper_acrylic_deck.dxf", "Panel cutting"),
        ("Cut lists", "2 CSV files", "4040, shafts and flatbar"),
        ("Verification", "JSON + Markdown", "Workspace, load and clearance audit"),
        ("Budget", "CSV + Markdown", "4M KRW release gate"),
        ("This assembly/order pack", "PDF", "Procurement, inspection, assembly, wiring"),
        ("Fabrication drawing pack", "PDF", "Shop drawings and QA"),
    ]
    draw_table(c, rows, 30, height-80, [160, 245, 135], font_size=6.5, max_height=380)
    draw_paragraph(c, "현재 상태: 설계와 도면은 Rev A prototype fabrication baseline까지 작성되었다. 실제 주문 해제는 actuator/U-H bracket/CR-3001/collar/current의 HOLD 회신 후다. 회신 치수를 반영하면 동일 스크립트에서 STEP, DXF, 도면 PDF를 재생성한다.", 38, 135, width-76, 90, "body")
    a4_finish(c)


def build_assembly_pdf(path):
    sheet = landscape(A4)
    c = canvas.Canvas(str(path), pagesize=sheet, pageCompression=1)
    simple_cover(c, sheet, "NAVIMRO 조립·발주 패키지", "3-actuator radial leveling module | 4,000,000 KRW budget gate", RENDER_DIR / "navimro_neutral_iso.png")
    budget_page(c, 2, sheet)
    next_page = bom_pages(c, 3, sheet)
    hold_page(c, next_page, sheet); next_page += 1
    incoming_page(c, next_page, sheet); next_page += 1
    assembly_sequence_page(c, next_page, sheet); next_page += 1
    wiring_page(c, next_page, sheet); next_page += 1
    commissioning_page(c, next_page, sheet); next_page += 1
    deliverables_page(c, next_page, sheet)
    c.save()


def main():
    global S
    register_fonts()
    S = styles()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fabrication = OUTPUT_DIR / "NAVIMRO_leveling_module_fabrication_drawings_revA.pdf"
    assembly = OUTPUT_DIR / "NAVIMRO_leveling_module_assembly_and_order_pack_revA.pdf"
    build_fabrication_pdf(fabrication)
    build_assembly_pdf(assembly)
    print(fabrication)
    print(assembly)


if __name__ == "__main__":
    main()
