import cadquery as cq

from .common import COLORS, Component, centered_box, compound
from .parameters import P, Pose


def components(pose: Pose):
    # Simplified envelope of four DESTACO 323-R pull-action latches. The latch
    # provides clamping only; the conical pins/receivers locate X/Y/yaw.
    offset_y = 0.0 if pose.cart_coupled else -P.cart_disengaged_gap_mm
    shapes = []
    for x, y in [(-350, -285), (-350, 285), (350, -285), (350, 285)]:
        base = centered_box(75, 30, 8, (x, y, -6))
        handle = centered_box(25, 18, 70, (x, y, 24))
        hook = cq.Workplane("XZ").circle(4).extrude(36).translate((x, y - 18, -15))
        target = centered_box(35, 12, 28, (x, y + offset_y, -18))
        shapes.extend([base, handle, hook, target])
    return [Component("four_mechanical_latches", compound(shapes), COLORS["red"], "4x DESTACO 323-R + fabricated keeper", category="purchased", notes="Primary retention is mechanical; no electromagnet used")]
