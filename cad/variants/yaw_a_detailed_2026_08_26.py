import cadquery as cq

from math import atan2, degrees, hypot

from .common import COLORS, Component, centered_box, compound, rotate_translate, square_tube
from .parameters import P, Pose


def outer_component():
    tube = square_tube(
        P.guide_outer_size_mm,
        P.guide_outer_wall_mm,
        P.guide_outer_length_mm,
        P.guide_outer_z0_mm,
    )
    base_collar = square_tube(70.0, 10.0, 8.0, P.guide_outer_z0_mm)
    mouth_z0 = P.guide_outer_z0_mm + P.guide_outer_length_mm - 8.0
    mouth_collar = square_tube(70.0, 10.0, 8.0, mouth_z0)
    return Component(
        "keyed_guide_outer",
        compound([tube, base_collar, mouth_collar]),
        COLORS["cyan"],
        "50x50x3 aluminum square tube with external collars; bore remains open",
        notes="Yaw clearance is set with replaceable UHMW wear shims, not by tube nominal clearance alone",
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
        "42x42x3 aluminum square tube + replaceable UHMW yaw shims",
    )


def _translated(shape, z):
    return shape.translate((0.0, 0.0, z))


def _pitch_moving(shape, pose: Pose, platform_z):
    pitch_pose = Pose(pitch_deg=pose.pitch_deg)
    return rotate_translate(shape, pitch_pose, platform_z)


def _platform_moving(shape, pose: Pose, platform_z):
    return rotate_translate(shape, pose, platform_z)


def gimbal_components(pose: Pose, platform_z):
    """Return fixed, pitch-moving, and platform-moving gimbal bodies."""
    span = P.gimbal_yoke_span_mm
    lug = P.gimbal_lug_thickness_mm
    pin_r = P.gimbal_pin_diameter_mm / 2.0

    lower_bridge = centered_box(70.0, span, 10.0, (0.0, 0.0, -24.0))
    lower_lugs = [
        centered_box(70.0, lug, 38.0, (0.0, side * (span - lug) / 2.0, -1.0))
        for side in (-1.0, 1.0)
    ]
    lower_socket = square_tube(64.0, 9.0, 14.0, -30.0)
    # XZ workplane extrudes along -Y in CadQuery, so translate toward +Y to
    # center the pin on the joint origin.
    pitch_pin = cq.Workplane("XZ").circle(pin_r).extrude(span + 12.0).translate((0.0, (span + 12.0) / 2.0, 0.0))
    pitch_stop_blocks = [
        centered_box(16.0, 12.0, 12.0, (side * 27.0, -(span / 2.0 + 7.0), 15.0))
        for side in (-1.0, 1.0)
    ]
    fixed = compound([lower_bridge, lower_socket, pitch_pin, *lower_lugs, *pitch_stop_blocks])

    ring_outer = centered_box(76.0, 76.0, 18.0)
    ring_inner = centered_box(48.0, 48.0, 22.0)
    ring = ring_outer.cut(ring_inner)
    roll_pin = cq.Workplane("YZ").circle(pin_r).extrude(span + 12.0).translate((-(span + 12.0) / 2.0, 0.0, 0.0))
    pitch_tangs = [
        centered_box(12.0, 10.0, 14.0, (side * 27.0, -39.0, 9.0))
        for side in (-1.0, 1.0)
    ]
    roll_stop_blocks = [
        centered_box(12.0, 16.0, 12.0, (-(span / 2.0 + 7.0), side * 27.0, 15.0))
        for side in (-1.0, 1.0)
    ]
    intermediate = compound([ring, roll_pin, *pitch_tangs, *roll_stop_blocks])

    # The bridge reaches the two inner X-side HFS8 rails. It is the explicit
    # structural connection between the gimbal and upper frame.
    upper_bridge = centered_box(360.0, 70.0, 8.0, (0.0, 0.0, 16.0))
    upper_lugs = [
        centered_box(lug, 70.0, 34.0, (side * (span - lug) / 2.0, 0.0, 1.0))
        for side in (-1.0, 1.0)
    ]
    roll_tangs = [
        centered_box(10.0, 12.0, 14.0, (-39.0, side * 27.0, 9.0))
        for side in (-1.0, 1.0)
    ]
    upper = compound([upper_bridge, *upper_lugs, *roll_tangs])

    return [
        Component(
            "gimbal_lower_pitch_yoke",
            _translated(fixed, platform_z),
            COLORS["yellow"],
            "Fabricated steel lower yoke; fixed +Y pitch axis",
            notes="Carries yaw through the keyed guide and provides independent pitch-stop seats",
        ),
        Component(
            "gimbal_intermediate_ring",
            _pitch_moving(intermediate, pose, platform_z),
            COLORS["orange"],
            "Fabricated steel intermediate ring; pitch moving / local +X roll axis",
            notes=f"Nominal independent pin stops: +/-{P.gimbal_pin_stop_angle_deg:.0f} deg per axis",
        ),
        Component(
            "gimbal_upper_roll_yoke",
            _platform_moving(upper, pose, platform_z),
            COLORS["yellow"],
            "Fabricated steel upper yoke; follows pitch and roll",
            notes="No third azimuth joint is permitted",
        ),
    ]


def lift_stop_components(platform_z):
    """External passive stop cartridges and their moving contact bar."""
    post_x = P.lift_stop_post_x_offset_mm
    post_y = P.lift_stop_post_spacing_mm / 2.0
    bar_z = platform_z - P.lift_stop_bar_offset_below_joint_mm
    bar_half = P.lift_stop_bar_thickness_mm / 2.0
    cartridge_z0 = 52.0
    cartridge_z1 = 200.0
    cartridge_length = cartridge_z1 - cartridge_z0
    moving_rod_length = 160.0

    fixed_parts = []
    moving_rods = []
    post_points = ((post_x, -post_y), (post_x, post_y))
    for x, y in post_points:
        body = cq.Workplane("XY").circle(P.lift_stop_nut_diameter_mm / 2.0).circle((P.lift_stop_post_diameter_mm + 2.0) / 2.0).extrude(cartridge_length).translate((x, y, cartridge_z0))
        fixed_parts.append(body)
        fixed_parts.append(centered_box(34.0, 34.0, 8.0, (x, y, cartridge_z0 + 4.0)))
        moving_rods.append(
            cq.Workplane("XY")
            .circle(P.lift_stop_post_diameter_mm / 2.0)
            .extrude(moving_rod_length)
            .translate((x, y, bar_z - moving_rod_length))
        )

    moving_parts = []
    for x, y in post_points:
        length = hypot(x, y)
        angle = degrees(atan2(y, x))
        arm = centered_box(length, 20.0, P.lift_stop_bar_thickness_mm, (length / 2.0, 0.0, bar_z))
        arm = arm.rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), angle)
        hole = cq.Workplane("XY").center(x, y).circle((P.lift_stop_post_diameter_mm + 4.0) / 2.0).extrude(P.lift_stop_bar_thickness_mm + 2.0).translate((0.0, 0.0, bar_z - bar_half - 1.0))
        moving_parts.append(arm.cut(hole))
    collar = square_tube(56.0, 7.0, P.lift_stop_bar_thickness_mm, bar_z - bar_half)

    switch_x = post_x + 40.0
    switches = compound([
        centered_box(24.0, 18.0, 12.0, (switch_x, post_y, 85.0)),
        centered_box(24.0, 18.0, 12.0, (switch_x, post_y, 175.0)),
    ])

    return [
        Component(
            "guide_external_mechanical_stops",
            compound(fixed_parts),
            COLORS["red"],
            "Two passive telescopic stop cartridges with captured end shoulders",
            notes="Mechanical contacts are outside the guide bore, below the load deck, and independent of actuator/electrical limits",
        ),
        Component(
            "guide_moving_stop_bar",
            compound([*moving_parts, *moving_rods, collar]),
            COLORS["yellow"],
            "Moving split collar, contact arms, and cartridge rods",
        ),
        Component(
            "guide_electrical_limit_switches",
            switches,
            COLORS["green"],
            "Separate lower and upper limit-switch envelopes",
            category="purchased",
            notes="Switch bodies are deliberately separate from the captured mechanical shoulders; exact cams and overrun remain bench-test inputs",
        ),
    ]


def overlap_mm(platform_z):
    outer_top = P.guide_outer_z0_mm + P.guide_outer_length_mm
    inner_bottom = platform_z - P.guide_inner_length_mm
    return max(0.0, outer_top - max(P.guide_outer_z0_mm, inner_bottom))
