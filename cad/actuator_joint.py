"""Detailed preliminary JNT-BR-01 actuator joint packages.

The shapes capture an assembly-ready topology without releasing tolerances or
specific fastener part numbers. Each joint uses a centered double-shear yoke,
replaceable lug bushings, an 8 mm shoulder-pin envelope, compact misalignment
spacers and retained hardware.
"""

from math import atan2, cos, degrees, radians, sin

import cadquery as cq

from .common import COLORS, Component, centered_box, compound, cylinder_between, with_world_shape
from .parameters import P, Pose


def projected_eye_width_mm(angle_deg=P.actuator_rod_end_allowable_angle_deg):
    """Conservative tangential envelope of the tilted HRT8E eye body."""
    angle = radians(angle_deg)
    return (
        P.actuator_rod_end_eye_width_mm * cos(angle)
        + P.actuator_rod_end_outer_diameter_mm * sin(angle)
    )


def articulation_clearance_mm(angle_deg=P.actuator_rod_end_allowable_angle_deg):
    return P.actuator_yoke_inner_gap_mm - projected_eye_width_mm(angle_deg)


def _rotated(shape, angle_deg):
    return shape.rotate((0, 0, 0), (0, 0, 1), angle_deg)


def _ring_between(start, end, outer_radius, inner_radius):
    return cylinder_between(start, end, outer_radius).cut(
        cylinder_between(start, end, inner_radius)
    )


def _single_package(radius, pin_z, angle_deg, root_sign):
    """Build one package in radial/tangential/vertical local coordinates."""
    gap = P.actuator_yoke_inner_gap_mm
    lug_t = P.actuator_yoke_lug_thickness_mm
    bushing_od = P.actuator_lug_bushing_outer_diameter_mm
    pin_bore = P.actuator_lug_bushing_bore_mm
    lug_y = gap / 2.0 + lug_t / 2.0

    # The cross plate sits toward the supporting frame: inward at the lower
    # joint and outward at the upper joint. Four holes reserve a bolted load
    # path into a local frame/load-spreader plate.
    root_x = radius + root_sign * 34.0
    plate = centered_box(
        P.actuator_bracket_mount_plate_thickness_mm,
        60.0,
        60.0,
        (root_x, 0.0, pin_z),
    )
    for y in (-18.0, 18.0):
        for z in (pin_z - 16.0, pin_z + 16.0):
            hole = cylinder_between(
                (root_x - 6.0, y, z),
                (root_x + 6.0, y, z),
                P.actuator_bracket_mount_hole_mm / 2.0,
            )
            plate = plate.cut(hole)

    lug_center_x = radius + root_sign * 11.0
    lug_shapes = []
    bushing_shapes = []
    for y in (-lug_y, lug_y):
        lug = centered_box(44.0, lug_t, 52.0, (lug_center_x, y, pin_z))
        lug_hole = cylinder_between(
            (radius, y - lug_t / 2.0 - 1.0, pin_z),
            (radius, y + lug_t / 2.0 + 1.0, pin_z),
            bushing_od / 2.0 + 0.05,
        )
        lug_shapes.append(lug.cut(lug_hole))
        bushing_shapes.append(_ring_between(
            (radius, y - lug_t / 2.0, pin_z),
            (radius, y + lug_t / 2.0, pin_z),
            bushing_od / 2.0,
            pin_bore / 2.0,
        ))

    # Compact spacer envelopes contact the spherical insert, not the outer
    # HRT8E body. Their exact purchased/turned detail remains a V-01 item.
    eye_half = P.actuator_rod_end_eye_width_mm / 2.0
    spacer_w = P.actuator_misalignment_spacer_width_mm
    spacer_od = P.actuator_misalignment_spacer_outer_diameter_mm
    spacers = [
        _ring_between(
            (radius, -gap / 2.0, pin_z),
            (radius, -eye_half, pin_z),
            spacer_od / 2.0,
            pin_bore / 2.0,
        ),
        _ring_between(
            (radius, eye_half, pin_z),
            (radius, gap / 2.0, pin_z),
            spacer_od / 2.0,
            pin_bore / 2.0,
        ),
    ]
    assert abs((gap - P.actuator_rod_end_eye_width_mm) / 2.0 - spacer_w) < 1e-9

    stack_half = gap / 2.0 + lug_t
    pin = cylinder_between(
        (radius, -stack_half, pin_z),
        (radius, stack_half + 1.5, pin_z),
        P.actuator_yoke_pin_diameter_mm / 2.0,
    )
    head = cylinder_between(
        (radius, -stack_half - P.actuator_pin_head_thickness_mm, pin_z),
        (radius, -stack_half, pin_z),
        P.actuator_pin_head_diameter_mm / 2.0,
    )
    washer = _ring_between(
        (radius, stack_half, pin_z),
        (radius, stack_half + 1.5, pin_z),
        8.0,
        pin_bore / 2.0,
    )
    retainer = cylinder_between(
        (radius, stack_half + 1.5, pin_z),
        (radius, stack_half + 1.5 + P.actuator_pin_retainer_thickness_mm, pin_z),
        P.actuator_pin_retainer_diameter_mm / 2.0,
    )

    return tuple(_rotated(shape, angle_deg) for shape in (
        compound([plate, *lug_shapes]),
        compound(bushing_shapes),
        compound(spacers),
        compound([pin, head, washer, retainer]),
    ))


def _aggregate(points, pin_z, root_sign):
    groups = [[], [], [], []]
    for x, y in points:
        angle = degrees(atan2(y, x))
        package = _single_package((x * x + y * y) ** 0.5, pin_z, angle, root_sign)
        for group, shape in zip(groups, package):
            group.append(shape)
    return tuple(compound(group) for group in groups)


def lower_components():
    structure, bushings, spacers, pins = _aggregate(
        P.base_points_xy, P.base_joint_z_mm, root_sign=-1.0
    )
    return [
        Component(
            "lower_actuator_brackets",
            structure,
            COLORS["yellow"],
            "JNT-BR-01 8 mm steel boxed double-shear yokes",
            notes="Four M8 attachment-hole envelopes per yoke; final plate joint and torque remain open",
        ),
        Component(
            "lower_actuator_bushings",
            bushings,
            COLORS["cyan"],
            "Replaceable 12x8.2x8 mm lug-bushing envelopes",
            category="fabricated_or_purchased",
        ),
        Component(
            "lower_actuator_misalignment_spacers",
            spacers,
            COLORS["gray"],
            "HRT8E misalignment-spacer envelopes, 3.5 mm each side",
            category="fabricated_or_purchased",
        ),
        Component(
            "lower_actuator_pins_retention",
            pins,
            COLORS["darkgray"],
            "M8 shoulder-pin/head/washer/locking-retainer envelopes",
            category="purchased",
            notes="Exact grade, shoulder length and locking method remain open",
        ),
    ]


def upper_components(pose: Pose):
    structure, bushings, spacers, pins = _aggregate(
        P.support_points_xy, 0.0, root_sign=1.0
    )
    local_components = [
        Component(
            "upper_radial_clevises",
            structure,
            COLORS["yellow"],
            "JNT-BR-01 8 mm steel boxed double-shear yokes",
            notes="Four M8 attachment-hole envelopes per yoke; load-spreader attachment remains preliminary",
        ),
        Component(
            "upper_actuator_bushings",
            bushings,
            COLORS["cyan"],
            "Replaceable 12x8.2x8 mm lug-bushing envelopes",
            category="fabricated_or_purchased",
        ),
        Component(
            "upper_actuator_misalignment_spacers",
            spacers,
            COLORS["gray"],
            "HRT8E misalignment-spacer envelopes, 3.5 mm each side",
            category="fabricated_or_purchased",
        ),
        Component(
            "upper_actuator_pins_retention",
            pins,
            COLORS["darkgray"],
            "M8 shoulder-pin/head/washer/locking-retainer envelopes",
            category="purchased",
            notes="Exact grade, shoulder length and locking method remain open",
        ),
    ]
    return [with_world_shape(component, pose) for component in local_components]
