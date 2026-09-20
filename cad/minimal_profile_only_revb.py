"""Dimension-corrected profile-only 3-RPS Rev B review assembly.

Rev B replaces the invalid tangent-rail/side-mounted LMB-10 arrangement with
an orthogonal lower grid.  All lower structural joints use 90 degree catalog
brackets.  Published LMB-10, PHS6, DNF4040, and DNF3030 dimensions are used.
The LM4075OE eye axial width remains a provisional 18 mm envelope because it
is not dimensioned in the public drawing and no matching STEP is available.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import asin, atan2, cos, degrees, radians, sin, sqrt

import cadquery as cq

from .common import centered_box, compound, cylinder_between


BLACK_PROFILE = (0.10, 0.12, 0.14, 1.0)
PROFILE_SLOT = (0.26, 0.29, 0.31, 1.0)
CAST_BRACKET = (0.42, 0.46, 0.49, 1.0)
STEEL = (0.63, 0.67, 0.70, 1.0)
FASTENER = (0.16, 0.17, 0.18, 1.0)
ACTUATOR_BODY = (0.20, 0.24, 0.27, 1.0)
ACTUATOR_ROD = (0.72, 0.76, 0.79, 1.0)
PROVISIONAL = (0.96, 0.70, 0.12, 1.0)
STOP_COLOR = (0.73, 0.17, 0.12, 1.0)


@dataclass(frozen=True)
class RevBParameters:
    outer_length_mm: float = 700.0
    outer_width_mm: float = 700.0
    lower_profile_mm: float = 40.0
    upper_profile_mm: float = 30.0
    mechanism_center_x_mm: float = 0.0
    mechanism_center_y_mm: float = -10.0
    upper_support_radius_mm: float = 250.0
    lower_support_radius_mm: float = 75.0
    lower_joint_z_mm: float = 76.0
    collapsed_ring_vertical_separation_mm: float = 155.0
    lift_mm: float = 50.0
    angle_deg: float = 3.0
    actuator_stroke_mm: float = 100.0
    actuator_min_pin_mm: float = 205.0
    actuator_max_pin_mm: float = 305.0
    upper_profile_center_local_z_mm: float = 50.0
    upper_profile_bottom_local_z_mm: float = 35.0
    phs_ring_to_thread_end_mm: float = 30.0
    phs_jam_nut_mm: float = 5.0
    phs_single_side_offset_mm: float = 14.5
    actuator_eye_width_mm: float = 18.0
    stop_slot_half_clearance_mm: float = 25.0
    stop_rod_radius_mm: float = 5.0


@dataclass(frozen=True)
class RevBPose:
    label: str
    lift_mm: float
    pitch_deg: float
    roll_deg: float


@dataclass(frozen=True)
class RevBComponent:
    name: str
    shape: object
    color: tuple
    material: str
    group: str
    bom_key: str
    status: str = "RELEASED"
    notes: str = ""


B = RevBParameters()

POSES = {
    "collapsed": RevBPose("collapsed", 0.0, 0.0, 0.0),
    "neutral": RevBPose("neutral", 25.0, 0.0, 0.0),
    "raised": RevBPose("raised", 50.0, 0.0, 0.0),
    "max_pitch": RevBPose("max_pitch", 25.0, 3.0, 0.0),
    "max_roll": RevBPose("max_roll", 25.0, 0.0, 3.0),
    "max_pitch_roll": RevBPose("max_pitch_roll", 25.0, 3.0, 3.0),
}


def _component(name, shape, color, material, group, bom_key, status="RELEASED", notes=""):
    return RevBComponent(name, shape, color, material, group, bom_key, status, notes)


def _shape(value):
    return value.val() if hasattr(value, "val") else value


def _profile_x(length, size, center=(0.0, 0.0, 0.0)):
    """Simplified extrusion using the published slot opening and depth."""
    x, y, z = center
    if size >= 40.0:
        slot_depth, slot_width, center_radius = 13.0, 8.3, 3.4
    else:
        slot_depth, slot_width, center_radius = 6.2, 6.3, 2.5
    offset = size / 2.0 - slot_depth / 2.0
    profile = centered_box(length, size, size, center)
    cuts = (
        centered_box(length + 2.0, slot_width, slot_depth, (x, y, z + offset)),
        centered_box(length + 2.0, slot_width, slot_depth, (x, y, z - offset)),
        centered_box(length + 2.0, slot_depth, slot_width, (x, y + offset, z)),
        centered_box(length + 2.0, slot_depth, slot_width, (x, y - offset, z)),
        cylinder_between(
            (x - length / 2.0 - 1.0, y, z),
            (x + length / 2.0 + 1.0, y, z),
            center_radius,
        ),
    )
    for cut in cuts:
        profile = profile.cut(cut)
    return profile


def _oriented_profile(length, size, center, angle_deg):
    x, y, z = center
    return _profile_x(length, size).rotate(
        (0, 0, 0), (0, 0, 1), angle_deg
    ).translate((x, y, z))


def _ring_between(center, axis, width, outer_radius, inner_radius):
    cx, cy, cz = center
    ax, ay, az = axis
    half = width / 2.0
    start = (cx - ax * half, cy - ay * half, cz - az * half)
    end = (cx + ax * half, cy + ay * half, cz + az * half)
    outer = cylinder_between(start, end, outer_radius)
    inner = cylinder_between(
        (start[0] - ax, start[1] - ay, start[2] - az),
        (end[0] + ax, end[1] + ay, end[2] + az),
        inner_radius,
    )
    return outer.cut(inner)


def _rotation_matrix(pitch_deg, roll_deg):
    pitch = radians(pitch_deg)
    roll = radians(roll_deg)
    cp, sp = cos(pitch), sin(pitch)
    cr, sr = cos(roll), sin(roll)
    return (
        (cp, sp * sr, sp * cr),
        (0.0, cr, -sr),
        (-sp, cp * sr, cp * cr),
    )


def _rotate_vector(vector, pose):
    matrix = _rotation_matrix(pose.pitch_deg, pose.roll_deg)
    x, y, z = vector
    return (
        matrix[0][0] * x + matrix[0][1] * y + matrix[0][2] * z,
        matrix[1][0] * x + matrix[1][1] * y + matrix[1][2] * z,
        matrix[2][0] * x + matrix[2][1] * y + matrix[2][2] * z,
    )


def _upper_origin_z(pose):
    return (
        B.lower_joint_z_mm
        + B.collapsed_ring_vertical_separation_mm
        + pose.lift_mm
    )


def _transform_point(point, pose):
    cx = B.mechanism_center_x_mm
    cy = B.mechanism_center_y_mm
    local = (point[0] - cx, point[1] - cy, point[2])
    x, y, z = _rotate_vector(local, pose)
    return (x + cx, y + cy, z + _upper_origin_z(pose))


def _transform_shape(shape, pose):
    cx = B.mechanism_center_x_mm
    cy = B.mechanism_center_y_mm
    result = shape.translate((-cx, -cy, 0.0))
    result = result.rotate((0, 0, 0), (1, 0, 0), pose.roll_deg)
    result = result.rotate((0, 0, 0), (0, 1, 0), pose.pitch_deg)
    return result.translate((cx, cy, _upper_origin_z(pose)))


def _radial_tangent_from_center(x, y):
    dx = x - B.mechanism_center_x_mm
    dy = y - B.mechanism_center_y_mm
    radius = sqrt(dx * dx + dy * dy)
    radial = (dx / radius, dy / radius, 0.0)
    tangent = (-radial[1], radial[0], 0.0)
    return radial, tangent


def upper_support_points():
    cx, cy = B.mechanism_center_x_mm, B.mechanism_center_y_mm
    radius = B.upper_support_radius_mm
    return (
        (cx, cy + radius),
        (cx - radius, cy),
        (cx + radius, cy),
    )


def lower_support_points():
    cx, cy = B.mechanism_center_x_mm, B.mechanism_center_y_mm
    radius = B.lower_support_radius_mm
    return (
        (cx, cy + radius),
        (cx - radius, cy),
        (cx + radius, cy),
    )


def _lower_frame_components():
    parts = []
    z = B.lower_profile_mm / 2.0
    for label, x in (("L", -330.0), ("R", 330.0)):
        parts.append(_component(
            f"lower_outer_side_{label}",
            _oriented_profile(700.0, 40.0, (x, 0.0, z), 90.0),
            BLACK_PROFILE, "DNF4040 black extrusion", "lower_frame", "4040_700",
        ))
    for label, y in (("F", 330.0), ("B", -330.0), ("CENTER", -10.0)):
        parts.append(_component(
            f"lower_cross_{label}",
            _profile_x(620.0, 40.0, (0.0, y, z)),
            BLACK_PROFILE, "DNF4040 black extrusion", "lower_frame", "4040_620",
        ))
    parts.append(_component(
        "lower_A1_radial_rail",
        _oriented_profile(300.0, 40.0, (0.0, 160.0, z), 90.0),
        BLACK_PROFILE, "DNF4040 black extrusion", "lower_frame", "4040_300",
        notes="Runs from Y=10 to Y=310 and meets both cross members at 90 degrees",
    ))
    return parts


def _vertical_fastener(center, diameter, top_z, bottom_z, tnut_size):
    x, y = center
    shaft = cylinder_between((x, y, bottom_z), (x, y, top_z), diameter / 2.0)
    head = cylinder_between((x, y, top_z), (x, y, top_z + 4.5), diameter * 0.82)
    tnut = centered_box(tnut_size[0], tnut_size[1], tnut_size[2], (x, y, bottom_z + 2.5))
    return compound([shaft, head, tnut])


def _catalog_4035(center, angle_deg, name):
    base = centered_box(40.0, 35.0, 6.0, (0.0, 0.0, 43.0))
    upright = centered_box(6.0, 35.0, 40.0, (-17.0, 0.0, 60.0))
    shape = base.union(upright).rotate((0, 0, 0), (0, 0, 1), angle_deg).translate(center)
    return _component(
        name, shape, CAST_BRACKET, "4035 aluminum die-cast 90 degree bracket",
        "lower_connectors", "K92782553_4035",
    )


def _lower_connector_components():
    parts = []
    joints = (
        (-310.0, 330.0, 0.0, "corner_FL"),
        (310.0, 330.0, 90.0, "corner_FR"),
        (-310.0, -330.0, 0.0, "corner_BL"),
        (310.0, -330.0, 90.0, "corner_BR"),
        (-310.0, -10.0, 0.0, "center_L"),
        (310.0, -10.0, 90.0, "center_R"),
        (0.0, 10.0, 0.0, "A1_inner"),
        (0.0, 310.0, 180.0, "A1_outer"),
    )
    for index, (x, y, angle, label) in enumerate(joints, start=1):
        parts.append(_catalog_4035((x, y, 0.0), angle, f"lower_4035_{index}_{label}"))
        fasteners = []
        a = radians(angle)
        for lx, ly in ((0.0, 10.0), (-10.0, 0.0)):
            px = x + lx * cos(a) - ly * sin(a)
            py = y + lx * sin(a) + ly * cos(a)
            fasteners.append(_vertical_fastener((px, py), 8.0, 49.0, 27.0, (23.0, 12.0, 6.0)))
        parts.append(_component(
            f"lower_4035_{index}_2x_M8x20_SP408",
            compound(fasteners), FASTENER,
            "2x M8x20 screw and SP408 spring nut", "lower_fasteners",
            "4035_M8_FASTENER_2SET",
        ))
    return parts


def _canonical_lmb_shape():
    base = centered_box(56.0, 26.0, 3.0, (18.0, 0.0, 41.5))
    outline = [
        (-10.0, 43.0), (46.0, 43.0), (46.0, 57.0),
        (8.0, 76.0), (6.0, 82.0), (0.0, 84.0),
        (-6.0, 82.0), (-8.0, 76.0), (-10.0, 70.0),
    ]
    plate = cq.Workplane("XZ").polyline(outline).close().extrude(3.0)
    plate_a = plate.translate((0.0, 10.0, 0.0))
    plate_b = plate.translate((0.0, -13.0, 0.0))
    shape = base.union(plate_a).union(plate_b)
    bore = cylinder_between((0.0, -16.0, 76.0), (0.0, 16.0, 76.0), 3.1)
    return shape.cut(bore)


def _lmb_components():
    parts = []
    canonical = _canonical_lmb_shape()
    for index, (x, y) in enumerate(lower_support_points(), start=1):
        radial, tangent = _radial_tangent_from_center(x, y)
        # Point the long tapered side plates inward.  The actuator body moves
        # outward toward the upper support and otherwise clips the bracket.
        angle = degrees(atan2(radial[1], radial[0])) + 180.0
        bracket = canonical.rotate((0, 0, 0), (0, 0, 1), angle).translate((x, y, 0.0))
        parts.append(_component(
            f"LMB10_A{index}", bracket, CAST_BRACKET,
            "LMB-10 56x26x44 clevis bracket", "lower_joints", "LMB10",
            notes="Top-mounted; long taper and second base feature point 36 mm inward",
        ))

        pin = cylinder_between(
            (x - tangent[0] * 16.0, y - tangent[1] * 16.0, B.lower_joint_z_mm),
            (x + tangent[0] * 16.0, y + tangent[1] * 16.0, B.lower_joint_z_mm),
            3.0,
        )
        parts.append(_component(
            f"LMB10_A{index}_included_pin", pin, FASTENER,
            "6 mm retained clevis pin", "lower_joints", "LMB10_INCLUDED_PIN",
            status="VENDOR_INCLUDED_CONFIRM_AT_ORDER",
        ))

        mounts = []
        for offset in (0.0, -36.0):
            mx = x + radial[0] * offset
            my = y + radial[1] * offset
            mounts.append(_vertical_fastener((mx, my), 8.0, 46.0, 27.0, (23.0, 12.0, 6.0)))
        parts.append(_component(
            f"LMB10_A{index}_2x_M8x16_SP408", compound(mounts), FASTENER,
            "2x M8x16 screw, washer and SP408 spring nut", "lower_fasteners",
            "LMB_M8X16_SP408_2SET",
        ))
    return parts


def _upper_frame_local_components():
    parts = []
    z = B.upper_profile_center_local_z_mm
    for label, x in (("L", -335.0), ("R", 335.0)):
        parts.append(_component(
            f"upper_outer_side_{label}",
            _oriented_profile(700.0, 30.0, (x, 0.0, z), 90.0),
            BLACK_PROFILE, "DNF3030-6 extrusion", "upper_frame", "3030_700",
        ))
    for label, y in (("F", 335.0), ("B", -335.0), ("A1", 240.0), ("A23", -10.0)):
        parts.append(_component(
            f"upper_cross_{label}", _profile_x(640.0, 30.0, (0.0, y, z)),
            BLACK_PROFILE, "DNF3030-6 extrusion", "upper_frame", "3030_640",
        ))
    return parts


def _catalog_dcb3025(center, angle_deg, name):
    base = centered_box(30.0, 25.0, 4.0, (0.0, 0.0, 37.0))
    upright = centered_box(4.0, 25.0, 30.0, (-13.0, 0.0, 50.0))
    shape = base.union(upright).rotate((0, 0, 0), (0, 0, 1), angle_deg).translate(center)
    return _component(
        name, shape, CAST_BRACKET, "DCB3025 aluminum 90 degree bracket",
        "upper_connectors", "K56842696_DCB3025",
    )


def _upper_connector_local_components():
    parts = []
    joint_rows = (335.0, -335.0, 240.0, -10.0)
    index = 0
    for y in joint_rows:
        for side, x in (("L", -320.0), ("R", 320.0)):
            index += 1
            angle = 0.0 if side == "L" else 180.0
            parts.append(_catalog_dcb3025((x, y, 0.0), angle, f"upper_DCB3025_{index}"))
            fasteners = []
            a = radians(angle)
            for lx, ly in ((0.0, 8.0), (-8.0, 0.0)):
                px = x + lx * cos(a) - ly * sin(a)
                py = y + lx * sin(a) + ly * cos(a)
                fasteners.append(_vertical_fastener((px, py), 6.0, 41.0, 28.0, (23.0, 10.0, 5.0)))
            parts.append(_component(
                f"upper_DCB3025_{index}_2x_M6x15_SP306", compound(fasteners), FASTENER,
                "2x M6x15 screw and SP306 spring nut", "upper_fasteners",
                "DCB_M6_FASTENER_2SET",
            ))
    return parts


def _phs_local_components():
    parts = []
    for index, (x, y) in enumerate(upper_support_points(), start=1):
        _, tangent = _radial_tangent_from_center(x, y)
        ring = _ring_between((x, y, 0.0), tangent, 9.0, 9.0, 3.0)
        neck = cylinder_between((x, y, 5.0), (x, y, 30.0), 5.5)
        jam_nut = cq.Workplane("XY").polygon(6, 11.5).extrude(5.0).translate((x, y, 30.0))
        parts.append(_component(
            f"PHS6_A{index}", compound([ring, neck, jam_nut]), STEEL,
            "THK PHS6 published envelope", "upper_joints", "PHS6",
            notes="D18, B1=9, M6x1, center-to-thread-end=30, jam nut=5",
        ))

        head_angle = degrees(atan2(tangent[1], tangent[0]))
        t_head = centered_box(10.0, 5.5, 4.5, (0.0, 0.0, 38.0)).rotate(
            (0, 0, 0), (0, 0, 1), head_angle
        ).translate((x, y, 0.0))
        shaft = cylinder_between((x, y, 17.5), (x, y, 40.0), 3.0)
        parts.append(_component(
            f"PHS6_A{index}_TB306_M6x20", compound([t_head, shaft]), FASTENER,
            "TB306 M6x20 T-bolt", "upper_fasteners", "K55868014_TB306_M6X20",
            notes="10 mm head fits the 10.2 mm DNF3030 cavity; nominal PHS engagement 12.5 mm",
        ))
    return parts


def _actuator_points(index, pose):
    lx, ly = lower_support_points()[index - 1]
    ux, uy = upper_support_points()[index - 1]
    _, lower_tangent = _radial_tangent_from_center(lx, ly)
    _, upper_tangent_local = _radial_tangent_from_center(ux, uy)
    phs_center = _transform_point((ux, uy, 0.0), pose)
    upper_tangent = _rotate_vector(upper_tangent_local, pose)
    upper_eye = (
        phs_center[0] - upper_tangent[0] * B.phs_single_side_offset_mm,
        phs_center[1] - upper_tangent[1] * B.phs_single_side_offset_mm,
        phs_center[2] - upper_tangent[2] * B.phs_single_side_offset_mm,
    )
    return (lx, ly, B.lower_joint_z_mm), upper_eye, phs_center, lower_tangent, upper_tangent


def _unit(start, end):
    vector = tuple(end[i] - start[i] for i in range(3))
    length = sqrt(sum(value * value for value in vector))
    return tuple(value / length for value in vector), length


def _point_along(start, unit, distance):
    return tuple(start[i] + unit[i] * distance for i in range(3))


def _oriented_motor_box(start, end, tangent, height=75.0, width=40.0):
    axis, length = _unit(start, end)
    midpoint = tuple((start[i] + end[i]) / 2.0 for i in range(3))
    plane = cq.Plane(origin=midpoint, xDir=axis, normal=tangent)
    return cq.Workplane(plane).box(length, height, width, centered=(True, True, True))


def _actuator_components(pose):
    parts = []
    for index in range(1, 4):
        lower, upper_eye, phs_center, lower_tangent, upper_tangent = _actuator_points(index, pose)
        axis, pin_length = _unit(lower, upper_eye)
        motor_start = _point_along(lower, axis, 9.0)
        motor_end = _point_along(lower, axis, 109.0)
        tube_start = _point_along(lower, axis, 85.0)
        tube_end = _point_along(lower, axis, min(174.0, pin_length - 31.0))
        rod_start = _point_along(lower, axis, 150.0)
        rod_end = _point_along(upper_eye, axis, -21.0)
        body = compound([
            _oriented_motor_box(motor_start, motor_end, lower_tangent),
            cylinder_between(tube_start, tube_end, 16.0),
        ])
        rod = cylinder_between(rod_start, rod_end, 10.0)
        lower_eye = _ring_between(lower, lower_tangent, B.actuator_eye_width_mm, 10.0, 3.2)
        upper_eye_ring = _ring_between(upper_eye, upper_tangent, B.actuator_eye_width_mm, 10.0, 3.2)
        parts.extend((
            _component(
                f"LM4075OE_A{index}_body", body, PROVISIONAL,
                "LM4075OE published 40x75x100 motor envelope", "actuators", "LM4075OE_100",
                "PROVISIONAL_VENDOR_STEP", f"Pin length {pin_length:.3f} mm",
            ),
            _component(
                f"LM4075OE_A{index}_rod", rod, ACTUATOR_ROD,
                "20 mm actuator rod envelope", "actuators", "LM4075OE_100",
                "PROVISIONAL_VENDOR_STEP",
            ),
            _component(
                f"LM4075OE_A{index}_lower_eye", lower_eye, PROVISIONAL,
                "provisional 18 mm eye", "actuator_eyes", "LM4075OE_100",
                "PROVISIONAL_EYE_WIDTH",
            ),
            _component(
                f"LM4075OE_A{index}_upper_eye", upper_eye_ring, PROVISIONAL,
                "provisional 18 mm eye", "actuator_eyes", "LM4075OE_100",
                "PROVISIONAL_EYE_WIDTH",
            ),
        ))

        bolt_start = _point_along(upper_eye, upper_tangent, -16.0)
        bolt_end = _point_along(phs_center, upper_tangent, 10.0)
        upper_bolt = compound([
            cylinder_between(bolt_start, bolt_end, 3.0),
            cylinder_between(_point_along(bolt_start, upper_tangent, -5.0), bolt_start, 5.0),
            cylinder_between(bolt_end, _point_along(bolt_end, upper_tangent, 6.0), 5.2),
        ])
        parts.append(_component(
            f"PHS6_A{index}_M6x50_joint_bolt", upper_bolt, FASTENER,
            "M6x50 ISO4014 bolt, washers, 2 mm shim and nyloc", "upper_fasteners",
            "M6X50_PARTIAL_STACK", "CONDITIONAL_EYE_WIDTH",
        ))
    return parts


def stop_local_points():
    cy = B.mechanism_center_y_mm
    return ((-280.0, cy), (0.0, cy), (280.0, cy))


def _stop_components(pose):
    parts = []
    for index, (x, y) in enumerate(stop_local_points(), start=1):
        local_rod = cylinder_between((x, y, -220.0), (x, y, 35.0), B.stop_rod_radius_mm)
        local_lower_collar = cylinder_between((x, y, -220.0), (x, y, -212.0), 15.0)
        local_upper_collar = cylinder_between((x, y, -165.0), (x, y, -157.0), 15.0)
        moving = _transform_shape(compound([local_rod, local_lower_collar, local_upper_collar]), pose)
        parts.append(_component(
            f"mechanical_stop_{index}_moving", moving, STOP_COLOR,
            "M10 threaded rod and two lock-collar stacks", "mechanical_stops", "M10_STOP_SET",
            "PROVISIONAL_CATALOG_COMBINATION",
        ))

        jaws = []
        for side in (-1.0, 1.0):
            jaws.append(centered_box(40.0, 8.0, 10.0, (x, y + side * 29.0, 70.0)))
        parts.append(_component(
            f"mechanical_stop_{index}_50mm_catch", compound(jaws), CAST_BRACKET,
            "profile-mounted 50 mm open stop catch", "mechanical_stops", "STOP_CATCH_PAIR",
            "PROVISIONAL_CATALOG_COMBINATION",
        ))
    return parts


def components_for_pose(pose):
    parts = []
    parts.extend(_lower_frame_components())
    parts.extend(_lower_connector_components())
    parts.extend(_lmb_components())
    local_upper = (
        _upper_frame_local_components()
        + _upper_connector_local_components()
        + _phs_local_components()
    )
    for component in local_upper:
        parts.append(RevBComponent(
            component.name,
            _transform_shape(component.shape, pose),
            component.color,
            component.material,
            component.group,
            component.bom_key,
            component.status,
            component.notes,
        ))
    parts.extend(_actuator_components(pose))
    parts.extend(_stop_components(pose))
    return parts


def as_assembly(pose, include_groups=None):
    assembly = cq.Assembly(name=f"minimal_profile_only_revb_{pose.label}")
    for component in components_for_pose(pose):
        if include_groups is not None and component.group not in include_groups:
            continue
        r, g, b, a = component.color
        assembly.add(_shape(component.shape), name=component.name, color=cq.Color(r, g, b, a))
    return assembly


def actuator_pin_lengths(pose):
    rows = []
    for index in range(1, 4):
        lower, upper_eye, _, _, _ = _actuator_points(index, pose)
        _, length = _unit(lower, upper_eye)
        rows.append(length)
    return tuple(rows)


def workspace_audit():
    rows = []
    for lift, pitch, roll in product((0.0, 25.0, 50.0), (-3.0, 0.0, 3.0), (-3.0, 0.0, 3.0)):
        pose = RevBPose(f"L{lift}_P{pitch}_R{roll}", lift, pitch, roll)
        rows.append({
            "lift_mm": lift,
            "pitch_deg": pitch,
            "roll_deg": roll,
            "pin_lengths_mm": actuator_pin_lengths(pose),
        })
    values = [value for row in rows for value in row["pin_lengths_mm"]]
    minimum, maximum = min(values), max(values)
    return {
        "pose_count": len(rows),
        "required_min_pin_mm": minimum,
        "required_max_pin_mm": maximum,
        "required_span_mm": maximum - minimum,
        "retract_margin_mm": minimum - B.actuator_min_pin_mm,
        "extend_margin_mm": B.actuator_max_pin_mm - maximum,
        "passes_stroke": minimum >= B.actuator_min_pin_mm and maximum <= B.actuator_max_pin_mm,
        "rows": rows,
    }


def profile_cut_list():
    return {
        "4040 x 700": 2,
        "4040 x 620": 3,
        "4040 x 300": 1,
        "3030 x 700": 2,
        "3030 x 640": 4,
    }


def assembly_bounds(pose):
    solids = [_shape(component.shape) for component in components_for_pose(pose)]
    box = compound(solids).BoundingBox()
    return {
        "xmin": box.xmin,
        "xmax": box.xmax,
        "ymin": box.ymin,
        "ymax": box.ymax,
        "zmin": box.zmin,
        "zmax": box.zmax,
        "xlen": box.xlen,
        "ylen": box.ylen,
        "zlen": box.zlen,
    }


def named_collision_volume(pose, moving_groups, fixed_groups):
    moving = compound([
        _shape(component.shape) for component in components_for_pose(pose)
        if component.group in moving_groups
    ])
    fixed = compound([
        _shape(component.shape) for component in components_for_pose(pose)
        if component.group in fixed_groups
    ])
    try:
        return moving.intersect(fixed).Volume()
    except Exception:
        return sum(
            moving.intersect(solid).Volume()
            for solid in fixed.Solids()
        )


def stop_sweep_audit():
    rows = []
    for pitch, roll in product((-3.0, 0.0, 3.0), repeat=2):
        pose = RevBPose(f"P{pitch}_R{roll}", 0.0, pitch, roll)
        for index, point in enumerate(stop_local_points(), start=1):
            moved = _transform_point((point[0], point[1], -161.0), pose)
            datum = _transform_point((point[0], point[1], -161.0), POSES["collapsed"])
            radial_move = sqrt((moved[0] - datum[0]) ** 2 + (moved[1] - datum[1]) ** 2)
            rows.append({"stop": index, "pitch_deg": pitch, "roll_deg": roll, "sweep_mm": radial_move})
    maximum = max(row["sweep_mm"] for row in rows)
    allowed = B.stop_slot_half_clearance_mm - B.stop_rod_radius_mm
    return {
        "maximum_horizontal_sweep_mm": maximum,
        "allowed_center_sweep_mm": allowed,
        "minimum_clearance_mm": allowed - maximum,
        "passes": maximum <= allowed,
        "rows": rows,
    }


def actuation_jacobian_audit():
    base = RevBPose("base", 25.0, 0.0, 0.0)
    base_lengths = actuator_pin_lengths(base)
    dz = 0.01
    da_deg = 0.001
    da_rad = radians(da_deg)
    z_lengths = actuator_pin_lengths(RevBPose("z", 25.0 + dz, 0.0, 0.0))
    pitch_lengths = actuator_pin_lengths(RevBPose("pitch", 25.0, da_deg, 0.0))
    roll_lengths = actuator_pin_lengths(RevBPose("roll", 25.0, 0.0, da_deg))
    matrix = []
    for index in range(3):
        matrix.append((
            (z_lengths[index] - base_lengths[index]) / dz,
            (pitch_lengths[index] - base_lengths[index]) / da_rad,
            (roll_lengths[index] - base_lengths[index]) / da_rad,
        ))
    a, b, c = matrix
    determinant = (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )
    return {
        "matrix": matrix,
        "determinant": determinant,
        "full_rank": abs(determinant) > 1.0,
    }


def support_azimuth_audit():
    """Check whether the three limbs are the requested 120 degree radial set."""
    rows = {}
    for label, points in (
        ("lower", lower_support_points()),
        ("upper", upper_support_points()),
    ):
        angles = sorted(
            (
                degrees(
                    atan2(
                        y - B.mechanism_center_y_mm,
                        x - B.mechanism_center_x_mm,
                    )
                )
                % 360.0
            )
            for x, y in points
        )
        gaps = tuple(
            (angles[(index + 1) % 3] - angles[index]) % 360.0
            for index in range(3)
        )
        rows[label] = {
            "azimuths_deg": tuple(angles),
            "circular_gaps_deg": gaps,
            "is_120_degree_radial": max(abs(gap - 120.0) for gap in gaps) < 1e-6,
        }
    return {
        "lower": rows["lower"],
        "upper": rows["upper"],
        "passes": rows["lower"]["is_120_degree_radial"]
        and rows["upper"]["is_120_degree_radial"],
    }


def joint_axis_alignment_audit():
    """Measure the modeled actuator-axis error against both joint pin axes."""
    rows = []
    for pose_name, pose in POSES.items():
        for index in range(1, 4):
            lower, upper_eye, _, lower_pin_axis, upper_pin_axis = _actuator_points(
                index, pose
            )
            actuator_axis, _ = _unit(lower, upper_eye)
            lower_dot = sum(
                actuator_axis[axis] * lower_pin_axis[axis] for axis in range(3)
            )
            upper_dot = sum(
                actuator_axis[axis] * upper_pin_axis[axis] for axis in range(3)
            )
            rows.append(
                {
                    "pose": pose_name,
                    "actuator": index,
                    "lower_perpendicular_error_deg": degrees(
                        asin(min(1.0, abs(lower_dot)))
                    ),
                    "upper_perpendicular_error_deg": degrees(
                        asin(min(1.0, abs(upper_dot)))
                    ),
                }
            )
    maximum = max(
        max(
            row["lower_perpendicular_error_deg"],
            row["upper_perpendicular_error_deg"],
        )
        for row in rows
    )
    neutral = [row for row in rows if row["pose"] == "collapsed"]
    neutral_maximum = max(
        max(
            row["lower_perpendicular_error_deg"],
            row["upper_perpendicular_error_deg"],
        )
        for row in neutral
    )
    return {
        "neutral_maximum_error_deg": neutral_maximum,
        "all_pose_maximum_error_deg": maximum,
        "tolerance_deg": 0.1,
        "passes": maximum <= 0.1,
        "rows": rows,
    }


def connector_fastener_axis_audit():
    """Record the Rev B connector-axis mismatch found in the visual re-audit."""
    return {
        "lower_4035": {
            "modeled_fastener_axes": ("vertical", "vertical"),
            "required_fastener_axes": ("horizontal_X", "horizontal_Y"),
            "passes": False,
        },
        "upper_DCB3025": {
            "modeled_fastener_axes": ("vertical", "vertical"),
            "required_fastener_axes": ("horizontal_X", "horizontal_Y"),
            "passes": False,
        },
        "passes": False,
    }
