import cadquery as cq

from .common import COLORS, Component, centered_box, compound
from .parameters import P


def make_lower_plate():
    plate = cq.Workplane("XY").box(
        P.platform_length_mm,
        P.platform_width_mm,
        P.lower_plate_thickness_mm,
        centered=(True, True, False),
    )
    # Universal bolt pattern and four longitudinal adjustment slots.
    hole_points = [
        (-350, -300), (-350, 300), (350, -300), (350, 300),
        (-250, -200), (-250, 200), (250, -200), (250, 200),
    ]
    plate = plate.faces(">Z").workplane().pushPoints(hole_points).hole(11.0)
    for x, y in [(-350, 0), (350, 0), (0, -300), (0, 300)]:
        slot = (
            cq.Workplane("XY")
            .center(x, y)
            .slot2D(70.0, 14.0, 0.0 if y == 0 else 90.0)
            .extrude(P.lower_plate_thickness_mm + 2.0)
            .translate((0, 0, -1.0))
        )
        plate = plate.cut(slot)
    return plate


def make_lower_frame():
    z = P.lower_frame_center_z_mm
    s = P.frame_size_mm
    lx = P.platform_length_mm - 80.0
    ly = P.platform_width_mm - 80.0
    beams = [
        centered_box(lx, s, s, (0, +(ly - s) / 2.0, z)),
        centered_box(lx, s, s, (0, -(ly - s) / 2.0, z)),
        centered_box(s, ly - 2 * s, s, (+(lx - s) / 2.0, 0, z)),
        centered_box(s, ly - 2 * s, s, (-(lx - s) / 2.0, 0, z)),
        centered_box(560.0, s, s, (0, 140.0, z)),
        centered_box(560.0, s, s, (0, -140.0, z)),
        centered_box(s, 240.0, s, (140.0, 0, z)),
        centered_box(s, 240.0, s, (-140.0, 0, z)),
    ]
    return compound(beams)


def components():
    return [
        Component("lower_interface_plate", make_lower_plate().val(), COLORS["navy"], "6061-T6 aluminum 8 mm", notes="Acrylic not recommended for this primary load-transfer plate"),
        Component("lower_HFS8_frame", make_lower_frame(), COLORS["darkgray"], "MISUMI HFS8-4040 equivalent", category="purchased_cut"),
    ]
