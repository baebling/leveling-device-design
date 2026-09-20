from pathlib import Path
from math import cos, sin, radians

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "renders"
OUT.mkdir(parents=True, exist_ok=True)

W, H, SCALE = 1600, 1000, 2
BG = "#F4F7FA"
INK = "#17212B"
MUTED = "#5F6B76"
GRID = "#CBD5DF"
NAVY = "#173F5F"
TEAL = "#2A9D8F"
CYAN = "#48B6C9"
ORANGE = "#F4A261"
RED = "#E76F51"
YELLOW = "#E9C46A"
GRAY = "#7B8794"
LIGHT = "#DCE5EC"
WHITE = "#FFFFFF"
GREEN = "#3D8B5F"


def font(size, bold=False, mono=False):
    candidates = []
    if mono:
        candidates = [r"C:\Windows\Fonts\consolab.ttf", r"C:\Windows\Fonts\consola.ttf"]
    elif bold:
        candidates = [r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf"]
    else:
        candidates = [r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, int(size * SCALE))
    return ImageFont.load_default()


def sc(v):
    return int(round(v * SCALE))


def pts(seq):
    return [(sc(x), sc(y)) for x, y in seq]


def canvas(title, subtitle):
    im = Image.new("RGB", (W * SCALE, H * SCALE), BG)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, sc(W), sc(112)], fill=WHITE)
    d.rectangle([0, 0, sc(18), sc(112)], fill=TEAL)
    d.text((sc(52), sc(24)), title, font=font(34, bold=True), fill=INK)
    d.text((sc(54), sc(72)), subtitle, font=font(17), fill=MUTED)
    return im, d


def finish(im, d, filename):
    d.rectangle([0, sc(944), sc(W), sc(H)], fill=INK)
    warning = "PRELIMINARY PoC DESIGN  |  NOT APPROVED FOR FABRICATION  |  REQUIRES MECHANICAL ENGINEERING REVIEW"
    d.text((sc(800), sc(971)), warning, anchor="mm", font=font(16, bold=True), fill=WHITE)
    im = im.resize((W, H), Image.Resampling.LANCZOS)
    im.save(OUT / filename, optimize=True)


def tag(d, x, y, text, color, width=None):
    f = font(16, bold=True)
    box = d.textbbox((0, 0), text, font=f)
    tw = (box[2] - box[0]) / SCALE
    w = width or tw + 28
    d.rounded_rectangle([sc(x), sc(y), sc(x + w), sc(y + 34)], radius=sc(8), fill=color)
    d.text((sc(x + w / 2), sc(y + 17)), text, anchor="mm", font=f, fill=WHITE if color != YELLOW else INK)


def callout(d, anchor, box_xy, title, body, color=TEAL, box_w=290):
    ax, ay = anchor
    bx, by = box_xy
    target_x = bx if bx > ax else bx + box_w
    target_y = by + 34
    d.line(pts([(ax, ay), ((ax + target_x) / 2, ay), (target_x, target_y)]), fill=color, width=sc(3))
    d.ellipse([sc(ax - 5), sc(ay - 5), sc(ax + 5), sc(ay + 5)], fill=color)
    d.rounded_rectangle([sc(bx), sc(by), sc(bx + box_w), sc(by + 74)], radius=sc(10), fill=WHITE, outline=color, width=sc(2))
    d.text((sc(bx + 16), sc(by + 13)), title, font=font(17, bold=True), fill=INK)
    d.text((sc(bx + 16), sc(by + 43)), body, font=font(14), fill=MUTED)


def arrow(d, a, b, color=INK, width=3, head=10):
    d.line(pts([a, b]), fill=color, width=sc(width))
    x1, y1 = a
    x2, y2 = b
    ang = __import__("math").atan2(y2 - y1, x2 - x1)
    for off in (2.55, -2.55):
        hx = x2 + head * cos(ang + off)
        hy = y2 + head * sin(ang + off)
        d.line(pts([(x2, y2), (hx, hy)]), fill=color, width=sc(width))


def double_arrow(d, a, b, text, color=NAVY, text_offset=(0, -18)):
    arrow(d, a, b, color=color, width=2, head=9)
    arrow(d, b, a, color=color, width=2, head=9)
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    d.rounded_rectangle([sc(mx - 54), sc(my - 14 + text_offset[1]), sc(mx + 54), sc(my + 14 + text_offset[1])], radius=sc(6), fill=WHITE)
    d.text((sc(mx + text_offset[0]), sc(my + text_offset[1])), text, anchor="mm", font=font(15, bold=True), fill=color)


def iso(x, y, z, ox=800, oy=665, k=0.55, kz=0.90):
    return ox + (x - y) * k, oy + (x + y) * 0.23 - z * kz


def iso_box(d, x0, x1, y0, y1, z0, z1, top, side=None, ox=800, oy=665, k=0.55, outline=INK, kz=0.90):
    side = side or top
    b = [iso(x0, y0, z0, ox, oy, k, kz), iso(x1, y0, z0, ox, oy, k, kz), iso(x1, y1, z0, ox, oy, k, kz), iso(x0, y1, z0, ox, oy, k, kz)]
    t = [iso(x0, y0, z1, ox, oy, k, kz), iso(x1, y0, z1, ox, oy, k, kz), iso(x1, y1, z1, ox, oy, k, kz), iso(x0, y1, z1, ox, oy, k, kz)]
    d.polygon(pts([b[0], b[1], t[1], t[0]]), fill=side, outline=outline, width=sc(2))
    d.polygon(pts([b[1], b[2], t[2], t[1]]), fill=side, outline=outline, width=sc(2))
    d.polygon(pts(t), fill=top, outline=outline, width=sc(2))


def draw_isometric():
    im, d = canvas(
        "RECOMMENDED CONCEPT / ISOMETRIC",
        "Three-point independent lift + keyed telescopic guide + Cardan joint / nominal envelope 900 x 800 mm",
    )
    tag(d, 1220, 30, "3 DOF CONTROL", TEAL)
    tag(d, 1390, 30, "PHASE 1", NAVY)

    # Lower universal plate and base frame.
    iso_box(d, -450, 450, -400, 400, 0, 28, NAVY, "#0F2F48")
    iso_box(d, -370, 370, -320, -275, 30, 76, "#294F6D")
    iso_box(d, -370, 370, 275, 320, 30, 76, "#294F6D")
    iso_box(d, -370, -325, -275, 275, 30, 76, "#294F6D")
    iso_box(d, 325, 370, -275, 275, 30, 76, "#294F6D")

    # Actuators and joints.
    supports = [(300, 0), (-280, 250), (-280, -250)]
    for x, y in supports:
        p0 = iso(x, y, 58)
        p1 = iso(x, y, 250)
        d.line(pts([p0, p1]), fill=INK, width=sc(25))
        d.line(pts([p0, p1]), fill=ORANGE, width=sc(16))
        for px, py in (p0, p1):
            d.ellipse([sc(px - 11), sc(py - 11), sc(px + 11), sc(py + 11)], fill=YELLOW, outline=INK, width=sc(2))

    # Central guide / Cardan.
    iso_box(d, -52, 52, -52, 52, 55, 220, CYAN, "#2D8598")
    iso_box(d, -38, 38, -38, 38, 190, 260, "#8DD7E3", CYAN)
    cx, cy = iso(0, 0, 258)
    d.ellipse([sc(cx - 24), sc(cy - 16), sc(cx + 24), sc(cy + 16)], fill=YELLOW, outline=INK, width=sc(2))

    # Upper moving frame and plate.
    iso_box(d, -420, 420, -370, 370, 260, 300, TEAL, "#20796F")
    iso_box(d, -360, 360, -260, -205, 302, 337, GRAY, "#5A6672")
    iso_box(d, -360, 360, 205, 260, 302, 337, GRAY, "#5A6672")

    # Parametric locating and latching features.
    for x, y in [(-300, -285), (-300, 285), (300, -285), (300, 285)]:
        iso_box(d, x - 26, x + 26, y - 26, y + 26, 300, 342, YELLOW, "#B9953F")
    for x, y in [(0, -365), (0, 365), (-405, 0), (405, 0)]:
        a = iso(x, y, 318)
        d.rounded_rectangle([sc(a[0] - 15), sc(a[1] - 10), sc(a[0] + 15), sc(a[1] + 10)], radius=sc(5), fill=RED, outline=INK, width=sc(2))

    callout(d, iso(0, 0, 220), (95, 170), "CONSTRAINT GUIDE", "Keyed Z slide + 2-axis Cardan", CYAN, 340)
    callout(d, iso(-280, -250, 155), (90, 690), "3 x ACTUATOR", "Spherical ends / self-locking", ORANGE, 320)
    callout(d, iso(320, 250, 330), (1175, 175), "CART INTERFACE", "Adjustable rails + locators", TEAL, 335)
    callout(d, iso(405, 0, 318), (1240, 700), "MECHANICAL LOCK", "Over-center latch + safety clip", RED, 300)

    # Motion triad.
    ox, oy = 1275, 500
    arrow(d, (ox, oy), (ox, oy - 105), GREEN, 4, 12)
    d.text((sc(ox + 14), sc(oy - 100)), "Z / LIFT", font=font(16, bold=True), fill=GREEN)
    d.arc([sc(ox - 95), sc(oy - 70), sc(ox + 95), sc(oy + 70)], start=195, end=345, fill=NAVY, width=sc(4))
    d.text((sc(ox), sc(oy + 65)), "PITCH + ROLL", anchor="mm", font=font(16, bold=True), fill=NAVY)
    d.text((sc(800), sc(900)), "X / Y / YAW ARE MECHANICALLY CONSTRAINED", anchor="mm", font=font(19, bold=True), fill=INK)
    finish(im, d, "concept_isometric.png")


def draw_front():
    im, d = canvas(
        "RECOMMENDED CONCEPT / FRONT VIEW",
        "View along X axis / width direction shown / neutral position with ±3° roll envelope",
    )
    # Ground and neutral structure.
    d.line(pts([(220, 810), (1380, 810)]), fill=GRID, width=sc(3))
    d.rectangle([sc(330), sc(750), sc(1270), sc(790)], fill=NAVY, outline=INK, width=sc(3))
    d.rectangle([sc(410), sc(710), sc(1190), sc(750)], fill="#294F6D", outline=INK, width=sc(3))
    d.rectangle([sc(745), sc(500), sc(855), sc(710)], fill=CYAN, outline=INK, width=sc(3))
    d.rectangle([sc(770), sc(455), sc(830), sc(530)], fill="#8DD7E3", outline=INK, width=sc(3))

    for x in (520, 1080):
        d.line(pts([(x, 720), (x, 495)]), fill=INK, width=sc(28))
        d.line(pts([(x, 720), (x, 495)]), fill=ORANGE, width=sc(18))
        for y in (720, 495):
            d.ellipse([sc(x - 13), sc(y - 13), sc(x + 13), sc(y + 13)], fill=YELLOW, outline=INK, width=sc(2))

    d.rectangle([sc(300), sc(450), sc(1300), sc(500)], fill=TEAL, outline=INK, width=sc(3))
    d.rectangle([sc(410), sc(405), sc(1190), sc(450)], fill=GRAY, outline=INK, width=sc(3))
    # Tilt envelope.
    angle = radians(3)
    half = 500
    dy = half * sin(angle)
    d.line(pts([(800 - half, 475 + dy), (800 + half, 475 - dy)]), fill=RED, width=sc(4))
    d.line(pts([(800 - half, 475 - dy), (800 + half, 475 + dy)]), fill=RED, width=sc(4))
    d.text((sc(1330), sc(438)), "+/-3 deg ROLL", font=font(16, bold=True), fill=RED)

    double_arrow(d, (300, 858), (1300, 858), "800 mm NOMINAL", NAVY)
    d.line(pts([(300, 810), (300, 875)]), fill=NAVY, width=sc(2))
    d.line(pts([(1300, 810), (1300, 875)]), fill=NAVY, width=sc(2))
    double_arrow(d, (230, 790), (230, 450), "~270 mm", NAVY, (-5, 0))
    d.text((sc(125), sc(620)), "COLLAPSED\nESTIMATE", anchor="mm", font=font(15, bold=True), fill=MUTED)

    callout(d, (800, 515), (1040, 170), "CARDAN HEAD", "Allows pitch and roll", CYAN, 300)
    callout(d, (520, 610), (140, 190), "REAR SUPPORT PAIR", "Actuator A2 / A3", ORANGE, 300)
    callout(d, (1120, 428), (1110, 600), "ADAPTER RAIL", "Cart geometry remains parametric", GRAY, 350)

    d.rounded_rectangle([sc(520), sc(880), sc(1080), sc(925)], radius=sc(8), fill=WHITE, outline=TEAL, width=sc(2))
    d.text((sc(800), sc(902)), "Allowed: Z + Roll + Pitch   |   Blocked: X + Y + Yaw", anchor="mm", font=font(17, bold=True), fill=INK)
    finish(im, d, "concept_front.png")


def draw_side():
    im, d = canvas(
        "RECOMMENDED CONCEPT / SIDE VIEW",
        "View along Y axis / 900 mm length / lift and pitch motion envelope",
    )
    d.line(pts([(170, 820), (1430, 820)]), fill=GRID, width=sc(3))
    d.rectangle([sc(270), sc(760), sc(1330), sc(800)], fill=NAVY, outline=INK, width=sc(3))
    d.rectangle([sc(340), sc(720), sc(1260), sc(760)], fill="#294F6D", outline=INK, width=sc(3))
    d.rectangle([sc(750), sc(510), sc(850), sc(720)], fill=CYAN, outline=INK, width=sc(3))
    d.rectangle([sc(775), sc(465), sc(825), sc(535)], fill="#8DD7E3", outline=INK, width=sc(3))

    for x in (480, 1120):
        d.line(pts([(x, 725), (x, 505)]), fill=INK, width=sc(28))
        d.line(pts([(x, 725), (x, 505)]), fill=ORANGE, width=sc(18))
        for y in (725, 505):
            d.ellipse([sc(x - 13), sc(y - 13), sc(x + 13), sc(y + 13)], fill=YELLOW, outline=INK, width=sc(2))

    d.rectangle([sc(250), sc(460), sc(1350), sc(510)], fill=TEAL, outline=INK, width=sc(3))
    d.rectangle([sc(360), sc(415), sc(1240), sc(460)], fill=GRAY, outline=INK, width=sc(3))

    # 100 mm raised envelope and pitch lines.
    d.rectangle([sc(250), sc(330), sc(1350), sc(380)], fill=None, outline=GREEN, width=sc(4))
    d.line(pts([(250, 355), (1350, 355)]), fill=GREEN, width=sc(2))
    angle = radians(3)
    half = 550
    dy = half * sin(angle)
    d.line(pts([(800 - half, 485 + dy), (800 + half, 485 - dy)]), fill=RED, width=sc(4))
    d.line(pts([(800 - half, 485 - dy), (800 + half, 485 + dy)]), fill=RED, width=sc(4))
    d.text((sc(1370), sc(420)), "+/-3 deg\nPITCH", font=font(16, bold=True), fill=RED)

    double_arrow(d, (250, 870), (1350, 870), "900 mm NOMINAL", NAVY)
    d.line(pts([(250, 820), (250, 888)]), fill=NAVY, width=sc(2))
    d.line(pts([(1350, 820), (1350, 888)]), fill=NAVY, width=sc(2))
    double_arrow(d, (1410, 460), (1410, 330), "100 mm LIFT", GREEN, (-8, 0))

    callout(d, (800, 530), (90, 170), "KEYED Z SLIDE", "Blocks X / Y / Yaw", CYAN, 310)
    callout(d, (1120, 590), (1180, 640), "FRONT ACTUATOR", "A1 at X = +300 mm", ORANGE, 300)
    callout(d, (480, 590), (90, 650), "REAR ACTUATORS", "A2 / A3 share rear station", ORANGE, 330)
    d.text((sc(800), sc(920)), "CENTER HEIGHT: ~270 mm COLLAPSED / ~320 mm NEUTRAL / ~370 mm FULL LIFT", anchor="mm", font=font(18, bold=True), fill=INK)
    finish(im, d, "concept_side.png")


def draw_top():
    im, d = canvas(
        "RECOMMENDED CONCEPT / TOP VIEW",
        "Support geometry, central constraint guide and parametric cart-interface rails / dimensions in mm",
    )
    cx, cy, unit = 700, 500, 0.80

    def plan(x, y):
        return cx + x * unit, cy - y * unit

    # Universal lower plate and mounting-face parameter.
    p0 = plan(-450, 400)
    p1 = plan(450, -400)
    d.rounded_rectangle([sc(p0[0]), sc(p0[1]), sc(p1[0]), sc(p1[1])], radius=sc(14), fill="#D8EFEA", outline=TEAL, width=sc(4))
    m0 = plan(-350, 300)
    m1 = plan(350, -300)
    d.rounded_rectangle([sc(m0[0]), sc(m0[1]), sc(m1[0]), sc(m1[1])], radius=sc(10), fill=None, outline=NAVY, width=sc(3))
    for dash_x in range(int(m0[0]), int(m1[0]), 28):
        d.line(pts([(dash_x, m0[1]), (min(dash_x + 15, m1[0]), m0[1])]), fill=NAVY, width=sc(2))
        d.line(pts([(dash_x, m1[1]), (min(dash_x + 15, m1[0]), m1[1])]), fill=NAVY, width=sc(2))
    for dash_y in range(int(m0[1]), int(m1[1]), 28):
        d.line(pts([(m0[0], dash_y), (m0[0], min(dash_y + 15, m1[1]))]), fill=NAVY, width=sc(2))
        d.line(pts([(m1[0], dash_y), (m1[0], min(dash_y + 15, m1[1]))]), fill=NAVY, width=sc(2))

    # Support polygon.
    supports = {"A1": (300, 0), "A2": (-280, 250), "A3": (-280, -250)}
    tri = [plan(*supports[name]) for name in ("A1", "A2", "A3")]
    d.polygon(pts(tri), fill="#F4E5B3", outline=ORANGE, width=sc(5))
    d.text((sc(640), sc(485)), "NOMINAL SUPPORT\nPOLYGON", anchor="mm", font=font(19, bold=True), fill="#6B541D")

    # Cart adapter rails remain parametric.
    for y in (-220, 220):
        a = plan(-360, y + 34)
        b = plan(360, y - 34)
        d.rounded_rectangle([sc(a[0]), sc(a[1]), sc(b[0]), sc(b[1])], radius=sc(7), fill=GRAY, outline=INK, width=sc(3))
        for x in (-250, -80, 90, 260):
            s = plan(x - 35, y + 10)
            e = plan(x + 35, y - 10)
            d.rounded_rectangle([sc(s[0]), sc(s[1]), sc(e[0]), sc(e[1])], radius=sc(8), fill=LIGHT, outline=INK, width=sc(2))

    # Actuator points and central guide.
    for name, (x, y) in supports.items():
        px, py = plan(x, y)
        d.ellipse([sc(px - 23), sc(py - 23), sc(px + 23), sc(py + 23)], fill=ORANGE, outline=INK, width=sc(3))
        d.text((sc(px), sc(py)), name, anchor="mm", font=font(15, bold=True), fill=INK)
    gcx, gcy = plan(0, 0)
    d.rounded_rectangle([sc(gcx - 32), sc(gcy - 32), sc(gcx + 32), sc(gcy + 32)], radius=sc(8), fill=CYAN, outline=INK, width=sc(3))
    d.text((sc(gcx), sc(gcy)), "G", anchor="mm", font=font(18, bold=True), fill=INK)

    # Locators and latches.
    for x, y in [(-320, -300), (-320, 300), (320, -300), (320, 300)]:
        px, py = plan(x, y)
        d.polygon(pts([(px, py - 16), (px + 16, py), (px, py + 16), (px - 16, py)]), fill=YELLOW, outline=INK, width=sc(2))
    for x, y in [(0, -375), (0, 375), (-425, 0), (425, 0)]:
        px, py = plan(x, y)
        d.rounded_rectangle([sc(px - 22), sc(py - 14), sc(px + 22), sc(py + 14)], radius=sc(5), fill=RED, outline=INK, width=sc(2))

    # Dimensions and axes.
    double_arrow(d, plan(-450, -455), plan(450, -455), "900", NAVY)
    d.line(pts([plan(-450, -400), plan(-450, -470)]), fill=NAVY, width=sc(2))
    d.line(pts([plan(450, -400), plan(450, -470)]), fill=NAVY, width=sc(2))
    double_arrow(d, plan(-515, -400), plan(-515, 400), "800", NAVY, (0, 0))
    arrow(d, (1160, 700), (1270, 700), RED, 4, 12)
    d.text((sc(1284), sc(700)), "+X", anchor="lm", font=font(16, bold=True), fill=RED)
    arrow(d, (1160, 700), (1160, 590), GREEN, 4, 12)
    d.text((sc(1160), sc(570)), "+Y", anchor="mm", font=font(16, bold=True), fill=GREEN)

    callout(d, plan(0, 0), (1120, 175), "G / CONSTRAINT MAST", "Z slide + Cardan / blocks yaw", CYAN, 360)
    callout(d, plan(300, 0), (1130, 320), "A1 / FRONT", "Single front support", ORANGE, 310)
    callout(d, plan(-280, 250), (55, 165), "A2 + A3 / REAR", "Pair defines the rear edge", ORANGE, 315)
    d.rounded_rectangle([sc(1110), sc(780), sc(1510), sc(910)], radius=sc(12), fill=WHITE, outline=RED, width=sc(2))
    d.text((sc(1135), sc(802)), "LOAD-CENTRE CAUTION", font=font(17, bold=True), fill=RED)
    d.text((sc(1135), sc(837)), "CG outside the triangle can create", font=font(14), fill=MUTED)
    d.text((sc(1135), sc(862)), "tension/uplift at one actuator.", font=font(14), fill=MUTED)
    d.text((sc(1135), sc(887)), "Use bidirectional joints + cart latches.", font=font(14, bold=True), fill=INK)
    d.text((sc(700), sc(900)), "DASHED NAVY = PRELIMINARY 700 x 600 LOWER MOUNTING FACE", anchor="mm", font=font(16, bold=True), fill=NAVY)
    finish(im, d, "concept_top.png")


def draw_exploded():
    im, d = canvas(
        "RECOMMENDED CONCEPT / EXPLODED ARCHITECTURE",
        "Concept-level layer separation / components are placeholders, not fabrication geometry",
    )
    ox, oy, k, kz = 660, 735, 0.46, 0.65
    # Lower plate.
    iso_box(d, -450, 450, -400, 400, 0, 25, NAVY, "#0F2F48", ox, oy, k, kz=kz)
    # Base frame elevated.
    iso_box(d, -370, 370, -320, -275, 130, 175, "#294F6D", "#173F5F", ox, oy, k, kz=kz)
    iso_box(d, -370, 370, 275, 320, 130, 175, "#294F6D", "#173F5F", ox, oy, k, kz=kz)
    iso_box(d, -370, -325, -275, 275, 130, 175, "#294F6D", "#173F5F", ox, oy, k, kz=kz)
    iso_box(d, 325, 370, -275, 275, 130, 175, "#294F6D", "#173F5F", ox, oy, k, kz=kz)
    # Actuator layer.
    for x, y in [(300, 0), (-280, 250), (-280, -250)]:
        p0 = iso(x, y, 250, ox, oy, k, kz)
        p1 = iso(x, y, 430, ox, oy, k, kz)
        d.line(pts([p0, p1]), fill=INK, width=sc(24))
        d.line(pts([p0, p1]), fill=ORANGE, width=sc(15))
        d.ellipse([sc(p0[0] - 10), sc(p0[1] - 10), sc(p0[0] + 10), sc(p0[1] + 10)], fill=YELLOW, outline=INK, width=sc(2))
        d.ellipse([sc(p1[0] - 10), sc(p1[1] - 10), sc(p1[0] + 10), sc(p1[1] + 10)], fill=YELLOW, outline=INK, width=sc(2))
    iso_box(d, -55, 55, -55, 55, 230, 425, CYAN, "#2D8598", ox, oy, k, kz=kz)
    # Upper frame and cart interface.
    iso_box(d, -420, 420, -370, 370, 520, 560, TEAL, "#20796F", ox, oy, k, kz=kz)
    iso_box(d, -360, 360, -260, -205, 665, 705, GRAY, "#5A6672", ox, oy, k, kz=kz)
    iso_box(d, -360, 360, 205, 260, 665, 705, GRAY, "#5A6672", ox, oy, k, kz=kz)
    for x, y in [(-300, -285), (-300, 285), (300, -285), (300, 285)]:
        iso_box(d, x - 26, x + 26, y - 26, y + 26, 705, 748, YELLOW, "#B9953F", ox, oy, k, kz=kz)

    # Assembly axes.
    for x, y in [(0, 0), (300, 0), (-280, 250), (-280, -250)]:
        a = iso(x, y, 40, ox, oy, k, kz)
        b = iso(x, y, 700, ox, oy, k, kz)
        d.line(pts([a, b]), fill=GRID, width=sc(2))

    callout(d, iso(0, 0, 10, ox, oy, k, kz), (60, 740), "1 / LOWER INTERFACE", "Replaceable bolt-on plate", NAVY, 300)
    callout(d, iso(-350, -300, 150, ox, oy, k, kz), (60, 565), "2 / BASE FRAME", "Profile + folded steel brackets", NAVY, 310)
    callout(d, iso(-280, -250, 330, ox, oy, k, kz), (65, 340), "3 / MOTION SET", "3 actuators + constraint mast", ORANGE, 315)
    callout(d, iso(350, 300, 545, ox, oy, k, kz), (1180, 350), "4 / MOVING FRAME", "900 x 800 nominal envelope", TEAL, 330)
    callout(d, iso(300, 250, 720, ox, oy, k, kz), (1195, 165), "5 / CART COUPLING", "Rails, locators, latches, sensors", GRAY, 330)
    d.rounded_rectangle([sc(1080), sc(745), sc(1510), sc(900)], radius=sc(12), fill=WHITE, outline=RED, width=sc(2))
    d.text((sc(1105), sc(770)), "INDEPENDENT SAFETY LAYERS", font=font(17, bold=True), fill=INK)
    for i, s in enumerate(["Electrical travel limits", "Mechanical Z / angle stops", "Self-locking or brake", "Latch secondary safety clip"]):
        d.ellipse([sc(1105), sc(803 + i * 22), sc(1117), sc(815 + i * 22)], fill=RED)
        d.text((sc(1128), sc(807 + i * 22)), s, font=font(14), fill=MUTED)
    finish(im, d, "concept_exploded.png")


def draw_latch():
    im, d = canvas(
        "CART COUPLING / PARAMETRIC CONCEPT",
        "Dummy lower-frame interface only / actual cart dimensions, material and hole positions are not inferred from images",
    )
    # Main plan view.
    x0, y0, x1, y1 = 120, 190, 1050, 830
    d.rounded_rectangle([sc(x0), sc(y0), sc(x1), sc(y1)], radius=sc(18), fill="#D8EFEA", outline=TEAL, width=sc(4))
    d.text((sc(585), sc(214)), "UPPER MOUNTING PLATE / 900 x 800 NOMINAL", anchor="mm", font=font(16, bold=True), fill=INK)

    # Slots and adjustable adapter rails.
    for ry in (365, 650):
        d.rounded_rectangle([sc(250), sc(ry), sc(920), sc(ry + 70)], radius=sc(8), fill=GRAY, outline=INK, width=sc(3))
        for sx in range(300, 900, 120):
            d.rounded_rectangle([sc(sx), sc(ry + 24), sc(sx + 62), sc(ry + 46)], radius=sc(10), fill=LIGHT, outline=INK, width=sc(2))
    # Dummy cart member outlines.
    for ry in (384, 669):
        d.rounded_rectangle([sc(295), sc(ry), sc(880), sc(ry + 32)], radius=sc(4), fill=None, outline=WHITE, width=sc(4))
    d.text((sc(585), sc(535)), "DASHED/WHITE = PARAMETRIC CART-SIDE ADAPTER", anchor="mm", font=font(15, bold=True), fill=MUTED)

    # Four guide blocks.
    guides = [(235, 330), (935, 330), (235, 720), (935, 720)]
    for gx, gy in guides:
        d.polygon(pts([(gx, gy - 27), (gx + 27, gy), (gx, gy + 27), (gx - 27, gy)]), fill=YELLOW, outline=INK, width=sc(3))
    # Round + diamond locators.
    d.ellipse([sc(350 - 24), sc(330 - 24), sc(350 + 24), sc(330 + 24)], fill=CYAN, outline=INK, width=sc(3))
    d.text((sc(350), sc(330)), "R", anchor="mm", font=font(15, bold=True), fill=INK)
    d.polygon(pts([(820, 300), (850, 330), (820, 360), (790, 330)]), fill=CYAN, outline=INK, width=sc(3))
    d.text((sc(820), sc(330)), "D", anchor="mm", font=font(15, bold=True), fill=INK)

    # Latches and sensor flags.
    latch_pts = [(190, 500), (980, 500), (380, 780), (790, 780)]
    for lx, ly in latch_pts:
        d.rounded_rectangle([sc(lx - 34), sc(ly - 20), sc(lx + 34), sc(ly + 20)], radius=sc(7), fill=RED, outline=INK, width=sc(3))
        d.line(pts([(lx - 12, ly), (lx + 20, ly - 28)]), fill=WHITE, width=sc(5))
        d.ellipse([sc(lx + 36), sc(ly - 7), sc(lx + 50), sc(ly + 7)], fill=GREEN, outline=INK, width=sc(2))

    # Labels.
    callout(d, (350, 330), (80, 120), "ROUND LOCATOR", "Fixes X and Y datum", CYAN, 275)
    callout(d, (820, 330), (750, 120), "DIAMOND LOCATOR", "Fixes one axis; avoids bind", CYAN, 315)
    callout(d, (235, 720), (80, 840), "4 x TAPER GUIDE", "Coarse entry + landing pads", YELLOW, 290)
    callout(d, (790, 780), (735, 840), "4 x DRAW LATCH", "Uplift lock + safety clip", RED, 305)

    # Section inset.
    d.rounded_rectangle([sc(1100), sc(190), sc(1510), sc(830)], radius=sc(16), fill=WHITE, outline=GRID, width=sc(3))
    d.text((sc(1305), sc(224)), "SECTION / ENGAGED", anchor="mm", font=font(20, bold=True), fill=INK)
    # Plate, pad, adapter rail.
    d.rectangle([sc(1160), sc(650), sc(1450), sc(700)], fill=TEAL, outline=INK, width=sc(3))
    d.rectangle([sc(1210), sc(610), sc(1400), sc(650)], fill=YELLOW, outline=INK, width=sc(3))
    d.rectangle([sc(1200), sc(535), sc(1410), sc(610)], fill=GRAY, outline=INK, width=sc(3))
    d.text((sc(1305), sc(570)), "CART-SIDE\nADAPTER", anchor="mm", font=font(16, bold=True), fill=WHITE)
    # Latch body and hook.
    d.rounded_rectangle([sc(1125), sc(625), sc(1190), sc(725)], radius=sc(8), fill=RED, outline=INK, width=sc(3))
    d.line(pts([(1160, 635), (1180, 540), (1215, 540)]), fill=RED, width=sc(10))
    d.ellipse([sc(1142), sc(665), sc(1174), sc(697)], fill=YELLOW, outline=INK, width=sc(2))
    d.text((sc(1305), sc(745)), "METAL LATCH CARRIES UPLIFT\nPAD CARRIES VERTICAL LOAD", anchor="mm", font=font(15, bold=True), fill=INK)

    # Sensor/interlock chain.
    d.rounded_rectangle([sc(1140), sc(300), sc(1470), sc(445)], radius=sc(12), fill="#EEF5F8", outline=GREEN, width=sc(2))
    d.text((sc(1305), sc(327)), "COUPLING INTERLOCK", anchor="mm", font=font(17, bold=True), fill=GREEN)
    for i, line in enumerate(["Latch closes", "Sensor confirms", "AUTO motion enabled"]):
        y = 365 + i * 31
        d.ellipse([sc(1170), sc(y - 7), sc(1184), sc(y + 7)], fill=GREEN)
        d.text((sc(1200), sc(y)), line, anchor="lm", font=font(15), fill=INK)
        if i < 2:
            arrow(d, (1430, y), (1430, y + 22), GREEN, 2, 7)

    d.text((sc(1305), sc(875)), "All spacings remain parameters until the real cart is measured.", anchor="mm", font=font(16, bold=True), fill=MUTED)
    finish(im, d, "cart_latch_concept.png")


if __name__ == "__main__":
    draw_isometric()
    draw_front()
    draw_side()
    draw_top()
    draw_exploded()
    draw_latch()
    for path in sorted(OUT.glob("*.png")):
        print(f"{path.name}: {path.stat().st_size} bytes")
