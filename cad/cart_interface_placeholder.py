import cadquery as cq

from .common import COLORS, Component, centered_box, compound
from .parameters import P, Pose


def _cart_receiver(offset_y):
    z = -38.0
    l, w, m = P.cart_interface_length_mm, P.cart_interface_width_mm, P.cart_frame_member_width_mm
    beams = [
        centered_box(l, m, m, (0, offset_y + (w - m) / 2, z)),
        centered_box(l, m, m, (0, offset_y - (w - m) / 2, z)),
        centered_box(m, w - 2 * m, m, ((l - m) / 2, offset_y, z)),
        centered_box(m, w - 2 * m, m, (-(l - m) / 2, offset_y, z)),
    ]
    return compound(beams)


def _guide_receivers(offset_y):
    items = []
    for x in (-P.guide_pin_spacing_x_mm / 2, P.guide_pin_spacing_x_mm / 2):
        for y in (-P.guide_pin_spacing_y_mm / 2, P.guide_pin_spacing_y_mm / 2):
            cone = cq.Workplane("XY").circle(15).workplane(offset=18).circle(8).loft(combine=True)
            items.append(cone.translate((x, y + offset_y, -8)))
    return compound(items)


def components(pose: Pose):
    # The cart is intentionally only a parameterized coupling-interface dummy.
    # No cart body, wheel, drive or navigation geometry is modeled.
    offset_y = 0.0 if pose.cart_coupled else -P.cart_disengaged_gap_mm
    return [
        Component("cart_receiver_dummy", _cart_receiver(offset_y), COLORS["gray"], "PARAMETRIC CART-SIDE RECEIVER (dimensions TBD)", category="interface_dummy", notes="Not a cart design and not derived from reference images"),
        Component("cart_guide_receivers", _guide_receivers(offset_y), COLORS["yellow"], "Steel conical receiver cups", category="interface_dummy"),
    ]
