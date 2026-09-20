import cadquery as cq

from .common import COLORS, Component, centered_box, compound, with_world_shape
from .parameters import P, Pose


def _upper_frame_local():
    s = P.frame_size_mm
    lx = P.platform_length_mm - 60.0
    ly = P.platform_width_mm - 60.0
    # The actuator pivot passes through the frame mid-plane. This recovers
    # 20 mm of package height versus placing the pivot below the extrusion.
    z = 0.0
    beams = [
        centered_box(lx, s, s, (0, +(ly - s) / 2, z)),
        centered_box(lx, s, s, (0, -(ly - s) / 2, z)),
        centered_box(s, ly - 2 * s, s, (+(lx - s) / 2, 0, z)),
        centered_box(s, ly - 2 * s, s, (-(lx - s) / 2, 0, z)),
        centered_box(s, 420, s, (-160, 0, z)),
        centered_box(s, 420, s, (160, 0, z)),
        centered_box(560, s, s, (-20, 120, z)),
        centered_box(560, s, s, (-20, -120, z)),
    ]
    return compound(beams)


def _panel_local():
    z0 = P.upper_frame_half_height_mm
    panel = cq.Workplane("XY").box(
        P.platform_length_mm,
        P.platform_width_mm,
        P.upper_panel_thickness_mm,
        centered=(True, True, False),
    ).translate((0, 0, z0))
    # Parameterized M8 accessory grid; corner radius/hole spacing must be
    # finalized from the user's payload fixture before fabrication.
    points = [(x, y) for x in (-350, -175, 0, 175, 350) for y in (-300, -150, 0, 150, 300)]
    return panel.faces(">Z").workplane().pushPoints(points).hole(8.5)


def _load_spreaders_local():
    plates = []
    for x, y in P.support_points_xy:
        plates.append(centered_box(110, 90, 6, (x, y, -3)))
    plates.append(centered_box(180, 180, 6, (0, 0, -3)))
    return compound(plates)


def components(pose: Pose):
    locals_ = [
        Component("upper_HFS8_frame", _upper_frame_local(), COLORS["darkgray"], "MISUMI HFS8-4040 equivalent", category="purchased_cut"),
        Component("upper_acrylic_panel", _panel_local().val(), COLORS["teal"], "15 mm cast PMMA (PLEXIGLAS GS equivalent)", notes="Non-primary panel; use metal spreaders at every concentrated attachment"),
        Component("upper_load_spreaders", _load_spreaders_local(), COLORS["navy"], "6061-T6 aluminum 6 mm"),
    ]
    return [with_world_shape(c, pose) for c in locals_]
