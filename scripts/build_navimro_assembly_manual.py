"""Build the visual NAVIMRO Rev B mechanical assembly manual."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas

import scripts.build_navimro_pdf_pack as base


ROOT = Path(__file__).resolve().parents[1]
IMAGE_DIR = ROOT / "outputs" / "navimro_fabrication" / "assembly_guide"
OUTPUT = ROOT / "output" / "pdf" / "NAVIMRO_visual_assembly_manual_revB.pdf"
SHEET = landscape(A4)
NAVY = colors.HexColor("#16334A")
ORANGE = colors.HexColor("#D98324")
TEAL = colors.HexColor("#2B7A78")
INK = colors.HexColor("#17232D")
LIGHT = colors.HexColor("#F2F5F7")


def header(c, title, page):
    width, height = SHEET
    c.setFillColor(NAVY)
    c.rect(0, height - 55, width, 55, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("DocBold", 16)
    c.drawString(30, height - 36, title)
    c.setFont("Doc", 7)
    c.drawRightString(width - 30, height - 34, f"VISUAL ASSEMBLY MANUAL | REV B | PAGE {page}")
    c.setStrokeColor(colors.HexColor("#AAB8C2"))
    c.line(30, 26, width - 30, 26)
    c.setFillColor(INK)
    c.setFont("Doc", 6.5)
    c.drawString(30, 14, "Prototype bench rig - supplier transfer holes must be verified on delivered parts")


def badge(c, number, x, y, color=ORANGE):
    c.setFillColor(color)
    c.circle(x, y, 14, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("DocBold", 9)
    c.drawCentredString(x, y - 3, str(number))


def info_box(c, title, parts, actions, checks, x=560, y=74, w=250, h=440):
    c.setFillColor(LIGHT)
    c.roundRect(x, y, w, h, 5, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("DocBold", 13)
    c.drawString(x + 18, y + h - 30, title)
    y_top = y + h - 54
    for label, body, color in (
        ("사용 부품", parts, NAVY),
        ("조립 방법", actions, ORANGE),
        ("완료 판정", checks, TEAL),
    ):
        c.setFillColor(color)
        c.setFont("DocBold", 9)
        c.drawString(x + 18, y_top, label)
        y_top -= 10
        used = base.draw_paragraph(c, body, x + 18, y_top, w - 36, 115, "small")
        y_top -= used + 20


def cover(c):
    width, height = SHEET
    c.setFillColor(NAVY)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("DocBold", 27)
    c.drawString(42, height - 75, "NAVIMRO 수평유지장치")
    c.setFont("DocBold", 22)
    c.drawString(42, height - 108, "그림으로 따라 하는 기계 조립 매뉴얼")
    c.setFont("Doc", 10)
    c.drawString(44, height - 132, "하부 프레임부터 카트 결합부까지 8단계 누적 조립 | Rev B")
    c.setFillColor(colors.white)
    c.roundRect(38, 58, width - 76, height - 220, 5, fill=1, stroke=0)
    base.draw_image(c, IMAGE_DIR / "00_exploded.png", 50, 70, width - 100, height - 244)
    c.setFillColor(colors.HexColor("#F3C969"))
    c.setFont("DocBold", 9)
    c.drawString(43, 34, "주황색 부품이 각 단계에서 새로 장착되는 부품입니다. 회색은 이전 단계에서 이미 조립된 부분입니다.")
    c.showPage()


def overview(c):
    width, height = SHEET
    header(c, "0. 전체 구조를 먼저 이해하기", 2)
    base.draw_image(c, IMAGE_DIR / "00_exploded.png", 28, 54, 515, 470)
    rows = [
        ("1", "하부 4040 프레임", "고정 기준면"),
        ("2", "고정 가이드 타워", "LMF12UU가 축을 안내"),
        ("3", "이동 가이드", "축과 carriage가 상하 이동"),
        ("4", "중앙 Cardan", "Z 이외 pitch/roll만 허용"),
        ("5", "상부 4040 프레임", "하중을 받는 구조체"),
        ("6", "액추에이터 3개", "0/120/240도 방사 배치"),
        ("7", "아크릴 상판", "비구조성 덮개"),
        ("8", "카트 결합부", "locator + 기계식 latch"),
    ]
    table = [("순서", "부품군", "역할"), *rows]
    base.draw_table(c, table, 570, 500, [40, 120, 120], font_size=7.0, max_height=330)
    c.setFillColor(colors.HexColor("#FFF2D8"))
    c.roundRect(570, 78, 238, 130, 5, fill=1, stroke=0)
    base.draw_paragraph(c, "핵심 연결 관계", 588, 188, 205, 24, "head")
    base.draw_paragraph(c, "하부 프레임은 움직이지 않습니다. Ø12 축과 carriage, Cardan, 상부 프레임은 한 덩어리로 위아래 이동합니다. 액추에이터 3개는 하부 프레임과 상부 프레임 사이를 핀 관절로 연결합니다.", 588, 158, 205, 90, "small")
    c.showPage()


STEPS = (
    (
        "1. 하부 4040 프레임 조립",
        "01_lower_frame.png",
        "NVR-L01: 820 mm x2, 640 mm x2, 560 mm x2<br/>NVR-P01: 슬롯형 장착 탭 x4",
        "평평한 작업대에서 820 mm 레일 두 개를 좌우에 놓고 640 mm 레일로 사각 외곽을 만듭니다. 560 mm 크로스멤버 두 개는 중심에서 x=+/-60 mm 위치에 평행하게 놓습니다. 직각 브래킷은 먼저 손조임하고 두 대각선 길이가 같아진 뒤 본조임합니다.",
        "외곽이 비틀리지 않고 네 모서리가 작업대에 닿아야 합니다. 두 대각선 차이는 2 mm 이하, 크로스멤버 중심 간격은 120 mm입니다.",
    ),
    (
        "2. 고정 가이드 타워 조립",
        "02_fixed_tower.png",
        "NVR-P06: 200 mm riser x2<br/>NVR-B02: LMF12UU x4<br/>NVR-G07: 고정 Z-stop block x4",
        "두 riser를 560 mm 크로스멤버 위에 수직으로 세웁니다. 각 riser에 LMF12UU를 z=110/150 mm 높이로 두 개씩 배치합니다. 아직 구멍을 최종 가공하지 말고 실제 부싱을 클램프로 고정한 상태에서 Ø12 축 두 개를 동시에 끼워 정렬합니다.",
        "두 축이 평행하고 축간거리 120 mm가 유지되어야 합니다. 축을 손으로 통과시킬 때 걸림이 없어야 하며, 그 위치에서만 전사 가공합니다.",
    ),
    (
        "3. 이동 축과 carriage 조립",
        "03_moving_guide.png",
        "NVR-S01: Ø12 x240 축 x2<br/>NVR-G01: 240 mm 4040 x2<br/>NVR-B01: SK12 x4<br/>NVR-G06: split collar x4",
        "Ø12 축을 고정 LMF12UU 네 개에 먼저 통과시킵니다. 240 mm carriage 두 개를 수평으로 놓고 SK12를 각 축의 상/하 위치에 체결합니다. carriage가 평행한 상태에서 SK12 구멍을 전사 가공합니다. collar는 아직 느슨하게 둡니다.",
        "상부 carriage를 손으로 100 mm 왕복했을 때 자중으로 부드럽게 움직이고, 축이 부싱에서 빠지지 않아야 합니다. 움직임 중 프레임이 벌어지면 다시 정렬합니다.",
    ),
    (
        "4. 중앙 Cardan 관절 조립",
        "04_cardan.png",
        "NVR-G02: 하부 yoke<br/>NVR-G03: 50x50x6 적층판 x6 + M8 trunnion x4<br/>NVR-G04: 상부 yoke<br/>NVR-G05: 각도 stop x4",
        "50x50x6 판 여섯 장을 겹쳐 36 mm 블록으로 체결합니다. 블록의 좌우 M8 축은 하부 yoke, 앞뒤 M8 축은 상부 yoke에 끼웁니다. 두 회전축 중심이 같은 점을 지나도록 스페이서로 간극을 조정합니다. yoke는 각각 carriage와 상부 중앙 프레임에 체결됩니다.",
        "Cardan은 pitch와 roll 방향으로 각각 +/-3도 이상 자유롭게 움직여야 하지만 X/Y/yaw 유격은 없어야 합니다. 네 angle stop은 최종 시운전 때 설정합니다.",
    ),
    (
        "5. 상부 4040 프레임 조립",
        "05_upper_frame.png",
        "NVR-U01: 840 x2, 660 x2, 560 x2, 420 x2<br/>NVR-P03: 상부 관절 spreader x3",
        "840/660 mm 프로파일로 외곽 사각을 만들고 560 mm 크로스멤버 두 개와 420 mm 중앙 십자 프레임을 조립합니다. 중앙 십자 프레임의 중심을 Cardan 상부 yoke에 체결합니다. 액추에이터 상부 관절 위치 세 곳에는 6 mm spreader를 4040에 직접 체결합니다.",
        "상부 프레임 중심이 하부 프레임 중심과 일치해야 합니다. 중립 위치에서 네 모서리 높이 차이는 2 mm 이하로 맞춥니다.",
    ),
    (
        "6. 액추에이터 3개 장착",
        "06_actuators.png",
        "M001: LA2000-125150 x3<br/>M002/M003: U/H bracket 각 6개<br/>핀, 스페이서, 풀림방지 너트",
        "액추에이터 하단은 반경 175 mm, 상단은 반경 400 mm의 같은 방사선 위에 둡니다. A1은 0도, A2는 120도, A3는 240도입니다. 한 개씩 하단 핀을 체결한 뒤 상단 핀을 연결합니다. 세 액추에이터를 같은 길이로 맞춘 후에만 상부 프레임을 지지대에서 내립니다.",
        "각 끝단이 두 축으로 자유롭게 회전해야 하며 rod에 옆힘이 걸리면 안 됩니다. 전 작업영역에서 몸체와 프레임 사이 최소 간격을 확인합니다.",
    ),
    (
        "7. 아크릴 상판 설치",
        "07_deck.png",
        "NVR-U02: 900 x800 x15 아크릴<br/>저두 볼트 + 넓은 와셔 + 압축 스페이서",
        "아크릴은 상부 4040 위에 올리고 저두 볼트로 고정합니다. 액추에이터와 latch 하중은 아크릴을 통하지 않고 반드시 하부 4040 또는 steel spreader로 전달되게 합니다. 볼트 주변에는 압축 스페이서와 넓은 와셔를 사용합니다.",
        "아크릴이 휘거나 모서리에 집중 응력이 없어야 합니다. 프레임 움직임과 볼트 체결로 균열이 생기지 않는지 확인합니다.",
    ),
    (
        "8. 카트 결합부 장착",
        "08_cart_coupling.png",
        "NVR-C01: 760 mm receiver rail x2<br/>NVR-C02: master/secondary locator<br/>NVR-C03: CR-3001 latch x4",
        "receiver rail 두 개는 카트 쪽 구조물에 평행하게 설치합니다. 원형 master locator를 먼저 맞추고, 반대편 secondary locator는 슬롯 방향으로 열어 과구속을 피합니다. 네 latch는 locator가 완전히 안착한 뒤 아래 방향으로 당기도록 keeper 위치를 전사합니다.",
        "locator만으로 반복 위치가 결정되고 latch는 들뜸만 제거해야 합니다. latch를 풀면 장치가 억지 없이 분리되어야 합니다. 전자석은 주 잠금장치로 사용하지 않습니다.",
    ),
)


def step_page(c, page, step):
    title, image, parts, actions, checks = step
    header(c, title, page)
    badge(c, page - 2, 46, 497)
    base.draw_image(c, IMAGE_DIR / image, 25, 52, 520, 458)
    info_box(c, title.split(". ", 1)[1], parts, actions, checks)
    c.showPage()


def final_check(c):
    width, height = SHEET
    header(c, "9. 체결을 끝내기 전 전체 확인", 11)
    base.draw_image(c, ROOT / "outputs" / "navimro_fabrication" / "renders" / "navimro_neutral_iso.png", 28, 60, 470, 445)
    rows = [
        ("확인 순서", "확인 내용", "합격 기준"),
        ("1", "하부 프레임", "평면, 대각선 차이 <=2 mm"),
        ("2", "가이드 축", "무전원 100 mm 왕복 시 걸림 없음"),
        ("3", "Cardan", "pitch/roll 자유, X/Y/yaw 유격 없음"),
        ("4", "액추에이터 관절", "모든 끝단 2축 회전, rod 옆힘 없음"),
        ("5", "Z/각도 stop", "전기 한계 밖, 기계 간섭 전 접촉"),
        ("6", "상판", "구조 하중이 4040/spreader로 전달"),
        ("7", "카트 결합", "locator 선접촉, latch 후체결"),
    ]
    base.draw_table(c, rows, 520, 500, [55, 135, 125], font_size=7.0, max_height=360)
    c.setFillColor(colors.HexColor("#FCE7E2"))
    c.roundRect(520, 78, 285, 105, 5, fill=1, stroke=0)
    base.draw_paragraph(c, "전원을 넣기 전에", 538, 164, 250, 24, "head")
    base.draw_paragraph(c, "상부 프레임을 별도 지지대로 받치고 세 액추에이터를 한 개씩 손으로 관절 점검합니다. vendor 치수가 확인되지 않은 구멍은 실물 전사 전까지 최종 가공하지 않습니다.", 538, 136, 250, 70, "small")
    c.showPage()


def quick_reference(c):
    width, height = SHEET
    header(c, "10. 현장용 한 장 조립 순서", 12)
    for index, step in enumerate(STEPS, start=1):
        row = (index - 1) // 4
        col = (index - 1) % 4
        x = 32 + col * 198
        y = 365 - row * 205
        c.setFillColor(LIGHT)
        c.roundRect(x, y, 178, 170, 5, fill=1, stroke=0)
        badge(c, index, x + 24, y + 142, ORANGE)
        c.setFillColor(NAVY)
        c.setFont("DocBold", 9)
        c.drawString(x + 47, y + 137, step[0].split(". ", 1)[1])
        base.draw_image(c, IMAGE_DIR / step[1], x + 10, y + 45, 158, 82)
        short = step[4].split(".")[0] + "."
        base.draw_paragraph(c, short, x + 12, y + 36, 154, 28, "tiny")
    c.showPage()


def main():
    base.register_fonts()
    base.S = base.styles()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=SHEET, pageCompression=1)
    cover(c)
    overview(c)
    for page, step in enumerate(STEPS, start=3):
        step_page(c, page, step)
    final_check(c)
    quick_reference(c)
    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    main()
