import cadquery as cq

from .common import COLORS, Component, centered_box, compound, rotate_translate, square_tube
from .parameters import P, Pose


def outer_component():
    tube = square_tube(
        P.guide_outer_size_mm,
        P.guide_outer_wall_mm,
        P.guide_outer_length_mm,
        P.guide_outer_z0_mm,
    )
    base_mount = square_tube(66.0, 8.0, 8.0, P.guide_outer_z0_mm)
    return Component(
        "keyed_guide_outer",
        compound([tube, base_mount]),
        COLORS["cyan"],
        "Compact 50x50x3 keyed aluminum guide with lower mounting collar",
        notes="Central guide is a secondary X/Y/yaw constraint, not the visual or lifting element",
    )


def inner_component(platform_z):
    z0 = platform_z - P.guide_inner_length_mm
    shape = square_tube(
        P.guide_inner_size_mm,
        P.guide_inner_wall_mm,
        P.guide_inner_length_mm,
        z0,
    )
    return Component(
        "keyed_guide_inner",
        shape,
        COLORS["clear"],
        "42x42x3 aluminum inner guide with replaceable UHMW yaw shims",
    )


def _pitch_shape(shape, pose: Pose, platform_z):
    return rotate_translate(shape, Pose(pitch_deg=pose.pitch_deg), platform_z)


def compact_cardan_components(pose: Pose, platform_z):
    """Compact Cardan package; the three radial actuators remain dominant."""
    pin_r = P.gimbal_pin_diameter_mm / 2.0

    lower_bridge = centered_box(60.0, 68.0, 8.0, (0.0, 0.0, -18.0))
    lower_lugs = [
        centered_box(24.0, 6.0, 30.0, (0.0, side * 31.0, -3.0))
        for side in (-1.0, 1.0)
    ]
    lower_socket = square_tube(60.0, 8.0, 12.0, -30.0)
    pitch_pin = (
        cq.Workplane("XZ")
        .circle(pin_r)
        .extrude(76.0)
        .translate((0.0, 38.0, 0.0))
    )
    lower = compound([lower_bridge, lower_socket, pitch_pin, *lower_lugs])

    cross_outer = centered_box(48.0, 48.0, 14.0)
    cross_inner = centered_box(30.0, 30.0, 18.0)
    cross = cross_outer.cut(cross_inner)
    roll_pin = (
        cq.Workplane("YZ")
        .circle(pin_r)
        .extrude(76.0)
        .translate((-38.0, 0.0, 0.0))
    )
    intermediate = compound([cross, roll_pin])

    upper_lugs = [
        centered_box(6.0, 24.0, 30.0, (side * 31.0, 0.0, 3.0))
        for side in (-1.0, 1.0)
    ]
    upper_mount = centered_box(120.0, 120.0, 6.0, (0.0, 0.0, 18.0))
    upper = compound([upper_mount, *upper_lugs])

    stop_tabs = compound([
        centered_box(10.0, 8.0, 10.0, (24.0, -27.0, 8.0)),
        centered_box(10.0, 8.0, 10.0, (-24.0, -27.0, 8.0)),
        centered_box(8.0, 10.0, 10.0, (-27.0, 24.0, 8.0)),
        centered_box(8.0, 10.0, 10.0, (-27.0, -24.0, 8.0)),
    ])

    return [
        Component(
            "compact_cardan_lower",
            lower.translate((0.0, 0.0, platform_z)),
            COLORS["yellow"],
            "Compact fixed +Y pitch clevis",
            notes="Keyed guide carries X/Y/yaw constraint",
        ),
        Component(
            "compact_cardan_cross",
            _pitch_shape(intermediate, pose, platform_z),
            COLORS["orange"],
            "Compact pitch-moving cross with local +X roll pin",
        ),
        Component(
            "compact_cardan_upper",
            rotate_translate(upper, pose, platform_z),
            COLORS["yellow"],
            "Compact platform-side Cardan mount",
        ),
        Component(
            "compact_cardan_angle_stops",
            _pitch_shape(stop_tabs, pose, platform_z),
            COLORS["red"],
            "Independent +/-7 degree pitch/roll stop-tab envelopes",
            notes="Exact adjustable screw contacts remain a hardware-detail task",
        ),
    ]


def overlap_mm(platform_z):
    outer_top = P.guide_outer_z0_mm + P.guide_outer_length_mm
    inner_bottom = platform_z - P.guide_inner_length_mm
    return max(0.0, outer_top - max(P.guide_outer_z0_mm, inner_bottom))
