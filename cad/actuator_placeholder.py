import cadquery as cq

from .common import COLORS, Component, centered_box, compound, cylinder_between
from .parameters import P


def make_actuator(base, top, name, base_pin_axis=None, top_pin_axis=None):
    base = cq.Vector(*base) if not isinstance(base, cq.Vector) else base
    top = cq.Vector(*top) if not isinstance(top, cq.Vector) else top
    axis = (top - base).normalized()
    length = (top - base).Length
    body_length = min(P.actuator_body_length_mm, length - 45.0)
    joint_offset = P.actuator_rod_end_outer_diameter_mm / 2.0 + 16.5
    body_start = base + axis.multiply(joint_offset)
    body_end = base + axis.multiply(body_length)
    rod_start = base + axis.multiply(max(0.0, body_length - 18.0))
    rod_end = top - axis.multiply(joint_offset)
    body = cylinder_between(body_start, body_end, P.actuator_body_radius_mm)
    rod = cylinder_between(rod_start, rod_end, P.actuator_rod_radius_mm)
    lower_adapter = cylinder_between(
        base + axis.multiply(P.actuator_rod_end_outer_diameter_mm / 2.0),
        body_start,
        6.5,
    )
    upper_adapter = cylinder_between(
        rod_end,
        top - axis.multiply(P.actuator_rod_end_outer_diameter_mm / 2.0),
        6.5,
    )
    tangent = cq.Vector(-axis.y, axis.x, 0.0)
    if tangent.Length <= 1e-9:
        tangent = cq.Vector(0.0, 1.0, 0.0)
    tangent = tangent.normalized()
    base_pin_axis = (
        cq.Vector(*base_pin_axis) if base_pin_axis is not None and not isinstance(base_pin_axis, cq.Vector)
        else base_pin_axis
    ) or tangent
    top_pin_axis = (
        cq.Vector(*top_pin_axis) if top_pin_axis is not None and not isinstance(top_pin_axis, cq.Vector)
        else top_pin_axis
    ) or tangent
    base_pin_axis = base_pin_axis.normalized()
    top_pin_axis = top_pin_axis.normalized()
    eye_half = P.actuator_rod_end_eye_width_mm / 2.0
    joint0 = cylinder_between(
        base - base_pin_axis.multiply(eye_half),
        base + base_pin_axis.multiply(eye_half),
        P.actuator_rod_end_outer_diameter_mm / 2.0,
    ).cut(
        cylinder_between(
            base - base_pin_axis.multiply(eye_half + 1.0),
            base + base_pin_axis.multiply(eye_half + 1.0),
            P.actuator_clevis_hole_mm / 2.0,
        )
    )
    joint1 = cylinder_between(
        top - top_pin_axis.multiply(eye_half),
        top + top_pin_axis.multiply(eye_half),
        P.actuator_rod_end_outer_diameter_mm / 2.0,
    ).cut(
        cylinder_between(
            top - top_pin_axis.multiply(eye_half + 1.0),
            top + top_pin_axis.multiply(eye_half + 1.0),
            P.actuator_clevis_hole_mm / 2.0,
        )
    )
    # Keep the simplified motor envelope clear of the joint package. The
    # final offset must be replaced by the vendor STEP mounting datum.
    motor_center = base + axis.multiply(105.0)
    motor_normal = axis.cross(base_pin_axis)
    motor = cq.Workplane(cq.Plane(
        origin=motor_center,
        xDir=axis,
        normal=motor_normal,
    )).box(
        P.actuator_motor_box_x_mm,
        P.actuator_motor_box_y_mm,
        P.actuator_motor_box_z_mm,
    )
    shape = compound([body, rod, lower_adapter, upper_adapter, joint0, joint1, motor])
    return Component(
        name,
        shape,
        COLORS["orange"],
        P.actuator_model,
        category="purchased",
        notes="Parametric actuator envelope with official HRT8E 23x11x8 mm eye envelopes; exact threaded actuator adapter remains preliminary",
    )


def make_radial_limit_components(base, top, name):
    """Build the detailed LS-01 package while preserving the old API."""
    from .actuator_limit_package import components

    return components(base, top, name)


def vendor_step_path():
    return (
        __import__("pathlib").Path(__file__).resolve().parents[1]
        / "references"
        / "vendor"
        / "firgelli"
        / "F-SD-H-450-12v-8in.stp"
    )
