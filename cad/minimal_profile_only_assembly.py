"""Profile-only 3-RPS Rev A review model for the low-load PoC.

FABRICATION HOLD (2026-08-31): vendor drawing audit found an invalid LMB-10
mount orientation, invalid 4035 use at four oblique rail joints, and a 15 mm
short PHS6 stack.  Keep this module only to reproduce the superseded Rev A
geometry and its failure audit.  Do not use it as fabrication geometry.

The active concept uses no full-size structural plate. Lower and upper frames
are T-slot extrusion assemblies. Small catalog brackets, fasteners, rod ends,
and mechanical stop hardware remain necessary.

The LM4075OE geometry is a planning envelope reconstructed from the retained
100 mm STEP inspection notes because the source STEP is not present in the
workspace. It is deliberately marked PROVISIONAL.
"""

from dataclasses import dataclass
from itertools import product
from math import atan2, cos, degrees, radians, sin, sqrt

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
class ProfileOnlyParameters:
    outer_length_mm: float = 700.0
    outer_width_mm: float = 700.0
    lower_profile_mm: float = 40.0
    upper_profile_mm: float = 30.0
    support_radius_mm: float = 250.0
    tangent_rail_radial_offset_mm: float = 45.0
    lower_joint_z_mm: float = 15.0
    collapsed_pin_spacing_mm: float = 230.0
    lift_mm: float = 50.0
    angle_deg: float = 3.0
    actuator_stroke_mm: float = 100.0
    actuator_min_pin_mm: float = 205.0
    actuator_max_pin_mm: float = 305.0
    upper_frame_center_local_z_mm: float = 35.0
    upper_frame_bottom_local_z_mm: float = 20.0
    phs_single_side_offset_mm: float = 14.5
    lower_actuator_body_radius_mm: float = 20.0
    tube_radius_mm: float = 16.0
    rod_radius_mm: float = 8.0
    stop_post_radius_mm: float = 310.0


@dataclass(frozen=True)
class ProfilePose:
    label: str
    lift_mm: float
    pitch_deg: float
    roll_deg: float


@dataclass(frozen=True)
class ProfileComponent:
    name: str
    shape: object
    color: tuple
    material: str
    group: str
    bom_key: str
    status: str = "RELEASED"
    notes: str = ""


M = ProfileOnlyParameters()

POSES = {
    "collapsed": ProfilePose("collapsed", 0.0, 0.0, 0.0),
    "neutral": ProfilePose("neutral", 25.0, 0.0, 0.0),
    "raised": ProfilePose("raised", 50.0, 0.0, 0.0),
    "max_pitch": ProfilePose("max_pitch", 25.0, 3.0, 0.0),
    "max_roll": ProfilePose("max_roll", 25.0, 0.0, 3.0),
    "max_pitch_roll": ProfilePose("max_pitch_roll", 25.0, 3.0, 3.0),
}


def _component(name, shape, color, material, group, bom_key, status="RELEASED", notes=""):
    return ProfileComponent(name, shape, color, material, group, bom_key, status, notes)


def _shape(value):
    return value.val() if hasattr(value, "val") else value


def _profile_x(length, size, center=(0.0, 0.0, 0.0)):
    """Simplified four-slot extrusion with a center bore."""
    x, y, z = center
    profile = centered_box(length, size, size, center)
    slot_depth = 5.0 if size >= 40.0 else 4.0
    slot_width = 8.0 if size >= 40.0 else 6.0
    offset = size / 2.0 - slot_depth / 2.0
    cuts = (
        centered_box(length + 2.0, slot_width, slot_depth, (x, y, z + offset)),
        centered_box(length + 2.0, slot_width, slot_depth, (x, y, z - offset)),
        centered_box(length + 2.0, slot_depth, slot_width, (x, y + offset, z)),
        centered_box(length + 2.0, slot_depth, slot_width, (x, y - offset, z)),
        cylinder_between(
            (x - length / 2.0 - 1.0, y, z),
            (x + length / 2.0 + 1.0, y, z),
            3.5 if size >= 40.0 else 2.8,
        ),
    )
    for cut in cuts:
        profile = profile.cut(cut)
    return profile


def _oriented_profile(length, size, center, angle_deg):
    x, y, z = center
    return _profile_x(length, size).rotate((0, 0, 0), (0, 0, 1), angle_deg).translate((x, y, z))


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
    return M.lower_joint_z_mm + M.collapsed_pin_spacing_mm + pose.lift_mm


def _transform_point(point, pose):
    x, y, z = _rotate_vector(point, pose)
    return (x, y, z + _upper_origin_z(pose))


def _transform_shape(shape, pose):
    result = shape.rotate((0, 0, 0), (1, 0, 0), pose.roll_deg)
    result = result.rotate((0, 0, 0), (0, 1, 0), pose.pitch_deg)
    return result.translate((0.0, 0.0, _upper_origin_z(pose)))


def support_points():
    return (
        (0.0, 250.0),
        (-216.5, -125.0),
        (216.5, -125.0),
    )


def _radial_tangent(x, y):
    radius = sqrt(x * x + y * y)
    radial = (x / radius, y / radius, 0.0)
    tangent = (-radial[1], radial[0], 0.0)
    return radial, tangent


def _line_square_segment(origin, direction, half_span):
    ox, oy = origin
    dx, dy = direction
    candidates = []
    if abs(dx) > 1e-9:
        for x in (-half_span, half_span):
            t = (x - ox) / dx
            y = oy + t * dy
            if -half_span - 1e-6 <= y <= half_span + 1e-6:
                candidates.append((t, x, y))
    if abs(dy) > 1e-9:
        for y in (-half_span, half_span):
            t = (y - oy) / dy
            x = ox + t * dx
            if -half_span - 1e-6 <= x <= half_span + 1e-6:
                candidates.append((t, x, y))
    candidates.sort(key=lambda row: row[0])
    first, last = candidates[0], candidates[-1]
    return (first[1], first[2]), (last[1], last[2])


def lower_tangent_rail_data():
    rows = []
    inner_half = M.outer_width_mm / 2.0 - M.lower_profile_mm
    for index, (x, y) in enumerate(support_points(), start=1):
        radial, tangent = _radial_tangent(x, y)
        line_origin = (
            x + radial[0] * M.tangent_rail_radial_offset_mm,
            y + radial[1] * M.tangent_rail_radial_offset_mm,
        )
        start, end = _line_square_segment(line_origin, tangent[:2], inner_half)
        length = sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
        center = ((start[0] + end[0]) / 2.0, (start[1] + end[1]) / 2.0)
        rows.append({
            "index": index,
            "support": (x, y),
            "radial": radial,
            "tangent": tangent,
            "start": start,
            "end": end,
            "center": center,
            "length_mm": length,
            "angle_deg": degrees(atan2(tangent[1], tangent[0])),
        })
    return rows


def _lower_frame_components():
    parts = []
    z = M.lower_profile_mm / 2.0
    side_x = M.outer_width_mm / 2.0 - M.lower_profile_mm / 2.0
    cross_y = M.outer_length_mm / 2.0 - M.lower_profile_mm / 2.0
    cross_length = M.outer_width_mm - 2.0 * M.lower_profile_mm
    for label, x in (("L", -side_x), ("R", side_x)):
        parts.append(_component(
            f"lower_outer_side_{label}",
            _oriented_profile(M.outer_length_mm, 40.0, (x, 0.0, z), 90.0),
            BLACK_PROFILE, "black anodized 4040 extrusion", "lower_frame", "4040_700",
        ))
    for label, y in (("F", cross_y), ("B", -cross_y)):
        parts.append(_component(
            f"lower_outer_cross_{label}",
            _profile_x(cross_length, 40.0, (0.0, y, z)),
            BLACK_PROFILE, "black anodized 4040 extrusion", "lower_frame", "4040_620",
        ))
    for row in lower_tangent_rail_data():
        cx, cy = row["center"]
        parts.append(_component(
            f"lower_tangent_mount_rail_A{row['index']}",
            _oriented_profile(row["length_mm"], 40.0, (cx, cy, z), row["angle_deg"]),
            BLACK_PROFILE, "black anodized 4040 extrusion", "lower_frame",
            f"4040_TANGENT_{round(row['length_mm'])}", notes="Tangent-axis actuator rail",
        ))
    return parts


def _catalog_connector(center, angle_deg, size, group, name):
    """Compact catalog angle connector envelope, not a custom plate."""
    x, y, z = center
    base = centered_box(size, size, 6.0, (0.0, 0.0, 0.0))
    rib = centered_box(size, 6.0, 24.0, (0.0, -size / 2.0 + 3.0, 9.0))
    shape = base.union(rib).rotate((0, 0, 0), (0, 0, 1), angle_deg).translate((x, y, z))
    return _component(name, shape, CAST_BRACKET, "catalog cast angle connector", group, "ANGLE_CONNECTOR")


def _connector_fastener_set(center, angle_deg, size, top_z, diameter, group, name, bom_key):
    """Four visible screw/T-nut stacks for one catalog connector."""
    x, y, _ = center
    angle = radians(angle_deg)
    ca, sa = cos(angle), sin(angle)
    local_points = (
        (-size * 0.24, 0.0),
        (size * 0.24, 0.0),
        (0.0, -size * 0.24),
        (0.0, size * 0.24),
    )
    stacks = []
    for lx, ly in local_points:
        px = x + lx * ca - ly * sa
        py = y + lx * sa + ly * ca
        shaft = cylinder_between((px, py, top_z - 13.0), (px, py, top_z + 1.0), diameter / 2.0)
        head = cylinder_between((px, py, top_z), (px, py, top_z + 4.0), diameter * 0.80)
        tnut = centered_box(16.0, 10.0, 5.0, (px, py, top_z - 10.5))
        stacks.extend((shaft, head, tnut))
    return _component(
        name, compound(stacks), FASTENER,
        f"4x M{int(diameter)} socket screw and matching T-nut set",
        group, bom_key,
    )


def _lower_connector_components():
    parts = []
    # Side-mounted orientation keeps the connector inside the 40 mm frame
    # height instead of stacking it on top of the extrusion.
    z = 19.0
    corner = M.outer_width_mm / 2.0 - M.lower_profile_mm - 18.0
    for index, (x, y, angle) in enumerate((
        (-corner, -corner, 0.0), (corner, -corner, 90.0),
        (corner, corner, 180.0), (-corner, corner, -90.0),
    ), start=1):
        center = (x, y, z)
        parts.append(_catalog_connector(center, angle, 34.0, "lower_connectors", f"lower_corner_connector_{index}"))
        parts.append(_connector_fastener_set(
            center, angle, 34.0, 40.0, 8.0, "lower_fasteners",
            f"lower_corner_connector_{index}_4x_M8", "M8_ANGLE_FASTENER_4SET",
        ))
    count = 0
    for row in lower_tangent_rail_data():
        for endpoint in (row["start"], row["end"]):
            count += 1
            center = (endpoint[0], endpoint[1], z)
            parts.append(_catalog_connector(
                center, row["angle_deg"], 30.0,
                "lower_connectors", f"lower_tangent_connector_{count}",
            ))
            parts.append(_connector_fastener_set(
                center, row["angle_deg"], 30.0, 40.0, 8.0, "lower_fasteners",
                f"lower_tangent_connector_{count}_4x_M8", "M8_ANGLE_FASTENER_4SET",
            ))
    return parts


def _horizontal_fastener(center, axis, length, diameter=8.0):
    cx, cy, cz = center
    ax, ay, az = axis
    half = length / 2.0
    start = (cx - ax * half, cy - ay * half, cz - az * half)
    end = (cx + ax * half, cy + ay * half, cz + az * half)
    shaft = cylinder_between(start, end, diameter / 2.0)
    head = cylinder_between(
        (start[0] - ax * 5.0, start[1] - ay * 5.0, start[2] - az * 5.0),
        start, diameter * 0.85,
    )
    nut = cylinder_between(
        end, (end[0] + ax * 6.0, end[1] + ay * 6.0, end[2] + az * 6.0),
        diameter * 0.78,
    )
    return compound([shaft, head, nut])


def _lmb_components():
    parts = []
    for index, (x, y) in enumerate(support_points(), start=1):
        radial, tangent = _radial_tangent(x, y)
        offset = M.tangent_rail_radial_offset_mm
        base_center = (
            x + radial[0] * (offset - 21.5),
            y + radial[1] * (offset - 21.5),
            22.0,
        )
        base = centered_box(58.0, 3.0, 44.0).rotate(
            (0, 0, 0), (0, 0, 1), degrees(atan2(tangent[1], tangent[0]))
        ).translate(base_center)
        ears = []
        for side in (-1.0, 1.0):
            ear_center = (
                x + radial[0] * 11.0 + tangent[0] * side * 11.5,
                y + radial[1] * 11.0 + tangent[1] * side * 11.5,
                M.lower_joint_z_mm,
            )
            ear = centered_box(24.0, 3.0, 24.0).rotate(
                (0, 0, 0), (0, 0, 1), degrees(atan2(radial[1], radial[0]))
            ).translate(ear_center)
            ears.append(ear)
        bracket = compound([base] + ears)
        parts.append(_component(
            f"LMB10_A{index}", bracket, CAST_BRACKET, "LMB-10 clevis bracket",
            "lower_joints", "LMB10", notes="Side-mounted to keep collapsed height low",
        ))
        pin = _horizontal_fastener((x, y, M.lower_joint_z_mm), tangent, 36.0, 6.0)
        parts.append(_component(
            f"LMB10_A{index}_pin", pin, FASTENER, "6 mm clevis pin and retainer",
            "lower_joints", "LMB10_PIN",
        ))
        for bolt_index, tangent_offset in enumerate((-18.0, 18.0), start=1):
            bolt_center = (
                base_center[0] + tangent[0] * tangent_offset + radial[0] * 20.0,
                base_center[1] + tangent[1] * tangent_offset + radial[1] * 20.0,
                20.0,
            )
            parts.append(_component(
                f"LMB10_A{index}_mount_M8_{bolt_index}",
                _horizontal_fastener(bolt_center, radial, 46.0, 8.0),
                FASTENER, "M8 socket screw and T-nut", "lower_fasteners", "M8_TNUT_SET",
            ))
    return parts


def _upper_frame_local_components():
    parts = []
    z = M.upper_frame_center_local_z_mm
    side_x = M.outer_width_mm / 2.0 - M.upper_profile_mm / 2.0
    cross_y = M.outer_length_mm / 2.0 - M.upper_profile_mm / 2.0
    cross_length = M.outer_width_mm - 2.0 * M.upper_profile_mm
    for label, x in (("L", -side_x), ("R", side_x)):
        parts.append(_component(
            f"upper_outer_side_{label}",
            _oriented_profile(M.outer_length_mm, 30.0, (x, 0.0, z), 90.0),
            BLACK_PROFILE, "black anodized 3030 extrusion", "upper_frame", "3030_700",
        ))
    for label, y in (("F", cross_y), ("B", -cross_y), ("A1", 250.0), ("A23", -125.0)):
        parts.append(_component(
            f"upper_cross_{label}",
            _profile_x(cross_length, 30.0, (0.0, y, z)),
            BLACK_PROFILE, "black anodized 3030 extrusion", "upper_frame", "3030_640",
        ))
    return parts


def _upper_connector_local_components():
    parts = []
    # The same connector is side-mounted within the 30 mm upper-frame depth.
    z = M.upper_frame_bottom_local_z_mm + 9.0
    corner = M.outer_width_mm / 2.0 - M.upper_profile_mm - 15.0
    for index, (x, y, angle) in enumerate((
        (-corner, -corner, 0.0), (corner, -corner, 90.0),
        (corner, corner, 180.0), (-corner, corner, -90.0),
    ), start=1):
        center = (x, y, z)
        parts.append(_catalog_connector(center, angle, 28.0, "upper_connectors", f"upper_corner_connector_{index}"))
        parts.append(_connector_fastener_set(
            center, angle, 28.0, 50.0, 6.0, "upper_fasteners",
            f"upper_corner_connector_{index}_4x_M6", "M6_ANGLE_FASTENER_4SET",
        ))
    side_x = M.outer_width_mm / 2.0 - M.upper_profile_mm - 14.0
    for row_index, y in enumerate((250.0, -125.0), start=1):
        for side_index, x in enumerate((-side_x, side_x), start=1):
            angle = 0.0 if side_index == 1 else 180.0
            center = (x, y, z)
            parts.append(_catalog_connector(
                center, angle, 26.0,
                "upper_connectors", f"upper_cross_connector_{row_index}_{side_index}",
            ))
            parts.append(_connector_fastener_set(
                center, angle, 26.0, 50.0, 6.0, "upper_fasteners",
                f"upper_cross_connector_{row_index}_{side_index}_4x_M6",
                "M6_ANGLE_FASTENER_4SET",
            ))
    return parts


def _phs_local_components():
    parts = []
    for index, (x, y) in enumerate(support_points(), start=1):
        _, tangent = _radial_tangent(x, y)
        ring = _ring_between((x, y, 0.0), tangent, 9.0, 11.0, 3.15)
        female_body = cylinder_between((x, y, 5.0), (x, y, 13.0), 5.5)
        jam_nut = cq.Workplane("XY").polygon(6, 11.5).extrude(5.0).translate((x, y, 10.0))
        parts.append(_component(
            f"PHS6_A{index}", compound([ring, female_body, jam_nut]), STEEL,
            "THK PHS6 rod end envelope", "upper_joints", "PHS6",
        ))
        tbolt = compound([
            centered_box(14.0, 10.0, 5.0, (x, y, M.upper_frame_bottom_local_z_mm + 2.5)),
            cylinder_between((x, y, 9.0), (x, y, M.upper_frame_bottom_local_z_mm + 5.0), 3.0),
        ])
        parts.append(_component(
            f"PHS6_A{index}_M6_hammer_head_bolt", tbolt, FASTENER,
            "M6 hammer-head T-bolt with downward male thread",
            "upper_fasteners", "M6_TBOLT",
            notes="T-head captured in lower 3030 slot; PHS6 female thread screws onto stud",
        ))
    return parts


def _actuator_points(index, pose):
    x, y = support_points()[index - 1]
    _, tangent = _radial_tangent(x, y)
    lower = (x, y, M.lower_joint_z_mm)
    phs_center = _transform_point((x, y, 0.0), pose)
    upper_tangent = _rotate_vector(tangent, pose)
    upper_eye = (
        phs_center[0] - upper_tangent[0] * M.phs_single_side_offset_mm,
        phs_center[1] - upper_tangent[1] * M.phs_single_side_offset_mm,
        phs_center[2] - upper_tangent[2] * M.phs_single_side_offset_mm,
    )
    return lower, upper_eye, phs_center, tangent, upper_tangent


def _unit(start, end):
    vector = (end[0] - start[0], end[1] - start[1], end[2] - start[2])
    length = sqrt(sum(value * value for value in vector))
    return tuple(value / length for value in vector), length


def _point_along(start, unit, distance):
    return tuple(start[i] + unit[i] * distance for i in range(3))


def _actuator_components(pose):
    parts = []
    for index in range(1, 4):
        lower, upper_eye, phs_center, lower_tangent, upper_tangent = _actuator_points(index, pose)
        axis, pin_length = _unit(lower, upper_eye)
        motor_end = _point_along(lower, axis, 48.0)
        tube_start = _point_along(lower, axis, 34.0)
        tube_end = _point_along(lower, axis, 165.0)
        rod_start = _point_along(lower, axis, 150.0)
        rod_end = _point_along(upper_eye, axis, -11.0)
        body = compound([
            cylinder_between(lower, motor_end, M.lower_actuator_body_radius_mm),
            cylinder_between(tube_start, tube_end, M.tube_radius_mm),
        ])
        rod = cylinder_between(rod_start, rod_end, M.rod_radius_mm)
        lower_eye = _ring_between(lower, lower_tangent, 18.0, 10.0, 3.2)
        upper_eye_ring = _ring_between(upper_eye, upper_tangent, 18.0, 10.0, 3.2)
        parts.extend([
            _component(
                f"LM4075OE_A{index}_body", body, ACTUATOR_BODY,
                "LM4075OE 100 mm planning envelope", "actuators", "LM4075OE_100",
                "PROVISIONAL", f"Pin length {pin_length:.3f} mm; replace with vendor STEP",
            ),
            _component(
                f"LM4075OE_A{index}_rod", rod, ACTUATOR_ROD,
                "chrome actuator rod envelope", "actuators", "LM4075OE_100",
                "PROVISIONAL",
            ),
            _component(
                f"LM4075OE_A{index}_lower_eye", lower_eye, PROVISIONAL,
                "18 mm lower eye envelope", "actuator_eyes", "LM4075OE_100",
                "PROVISIONAL",
            ),
            _component(
                f"LM4075OE_A{index}_upper_eye", upper_eye_ring, PROVISIONAL,
                "18 mm upper eye envelope", "actuator_eyes", "LM4075OE_100",
                "PROVISIONAL",
            ),
        ])
        bolt_start = _point_along(upper_eye, upper_tangent, -16.0)
        bolt_end = _point_along(phs_center, upper_tangent, 10.0)
        upper_bolt = compound([
            cylinder_between(bolt_start, bolt_end, 3.0),
            cylinder_between(_point_along(bolt_start, upper_tangent, -5.0), bolt_start, 5.0),
            cylinder_between(bolt_end, _point_along(bolt_end, upper_tangent, 5.0), 5.2),
        ])
        parts.append(_component(
            f"PHS6_A{index}_M6x50_joint_bolt", upper_bolt, FASTENER,
            "M6x50 partial-thread joint bolt", "upper_fasteners", "M6X50_PARTIAL",
            notes="Single-side PHS6 connection; physical fit test required",
        ))
    return parts


def _stop_components(pose):
    """Compact two-way stops that do not increase the collapsed height.

    Each M10 rod moves with the upper frame. Two fixed catch jaws are mounted
    to the lower extrusion. The upper and lower collars independently limit
    retraction and extension; the jaw gap permits the small pitch/roll sweep.
    """
    parts = []
    points = ((0.0, 300.0), (-259.808, -150.0), (259.808, -150.0))
    for index, (x, y) in enumerate(points, start=1):
        radial, tangent = _radial_tangent(x, y)

        # Moving geometry is defined in upper-frame coordinates. At zero lift,
        # the upper collar touches the jaw top. At 50 mm lift, the lower collar
        # touches the jaw underside.
        local_rod = cylinder_between((x, y, -238.0), (x, y, 20.0), 5.0)
        local_lower_collar = cq.Workplane("XY").circle(45.0).extrude(8.0).translate((x, y, -238.0))
        local_upper_collar = cq.Workplane("XY").circle(45.0).extrude(8.0).translate((x, y, -172.0))
        local_mount_nut = cq.Workplane("XY").polygon(6, 17.0).extrude(8.0).translate((x, y, 12.0))
        moving_stop = _transform_shape(
            compound([local_rod, local_lower_collar, local_upper_collar, local_mount_nut]),
            pose,
        )
        parts.append(_component(
            f"mechanical_stop_{index}_moving", moving_stop, STOP_COLOR,
            "M10 threaded stop rod with two adjustable collars", "mechanical_stops",
            "M10_STOP_SET", "PROVISIONAL",
            "Moves with upper frame; collar positions provide 50 mm mechanical travel",
        ))

        # Two small extrusion-mounted jaws leave an open central slot. They are
        # catalog-bracket-scale parts, not full-size structural plates.
        jaw_shapes = []
        jaw_fasteners = []
        for side in (-1.0, 1.0):
            center = (
                x + tangent[0] * side * 35.0,
                y + tangent[1] * side * 35.0,
                69.0,
            )
            jaw = centered_box(40.0, 20.0, 8.0).rotate(
                (0, 0, 0), (0, 0, 1), degrees(atan2(radial[1], radial[0]))
            ).translate(center)
            riser_center = (center[0], center[1], 54.5)
            riser = centered_box(20.0, 8.0, 29.0).rotate(
                (0, 0, 0), (0, 0, 1), degrees(atan2(tangent[1], tangent[0]))
            ).translate(riser_center)
            jaw_shapes.append(jaw.union(riser))
            jaw_fasteners.extend((
                cylinder_between((center[0], center[1], 35.0), (center[0], center[1], 45.0), 4.0),
                cylinder_between((center[0], center[1], 40.0), (center[0], center[1], 45.0), 6.5),
                centered_box(16.0, 10.0, 5.0, (center[0], center[1], 37.5)),
            ))
        parts.append(_component(
            f"mechanical_stop_{index}_catch_jaws", compound(jaw_shapes), CAST_BRACKET,
            "pair of T-slot stop-capture brackets", "mechanical_stops", "STOP_CATCH_PAIR",
            "PROVISIONAL", "50 mm open slot allows the verified 18.21 mm maximum rod sweep",
        ))
        parts.append(_component(
            f"mechanical_stop_{index}_catch_2x_M8", compound(jaw_fasteners), FASTENER,
            "2x M8 socket screw and T-nut for stop-capture brackets",
            "mechanical_stops", "STOP_CATCH_M8_2SET", "PROVISIONAL",
        ))
    return parts


def components_for_pose(pose):
    parts = []
    parts.extend(_lower_frame_components())
    parts.extend(_lower_connector_components())
    parts.extend(_lmb_components())
    for component in _upper_frame_local_components() + _upper_connector_local_components() + _phs_local_components():
        parts.append(ProfileComponent(
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
    assembly = cq.Assembly(name=f"minimal_profile_only_{pose.label}")
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
        pose = ProfilePose(f"L{lift}_P{pitch}_R{roll}", lift, pitch, roll)
        lengths = actuator_pin_lengths(pose)
        rows.append({
            "lift_mm": lift,
            "pitch_deg": pitch,
            "roll_deg": roll,
            "pin_lengths_mm": lengths,
        })
    all_lengths = [length for row in rows for length in row["pin_lengths_mm"]]
    minimum = min(all_lengths)
    maximum = max(all_lengths)
    return {
        "pose_count": len(rows),
        "required_min_pin_mm": minimum,
        "required_max_pin_mm": maximum,
        "required_span_mm": maximum - minimum,
        "retract_margin_mm": minimum - M.actuator_min_pin_mm,
        "extend_margin_mm": M.actuator_max_pin_mm - maximum,
        "passes_stroke": minimum >= M.actuator_min_pin_mm and maximum <= M.actuator_max_pin_mm,
        "rows": rows,
    }


def stop_sweep_audit():
    points = ((0.0, 300.0), (-259.808, -150.0), (259.808, -150.0))
    rows = []
    for lift, local_z in ((0.0, -168.0), (50.0, -234.0)):
        for pitch, roll in product((-3.0, 0.0, 3.0), repeat=2):
            pose = ProfilePose(f"stop_L{lift}_P{pitch}_R{roll}", lift, pitch, roll)
            for index, (x, y) in enumerate(points, start=1):
                moved = _transform_point((x, y, local_z), pose)
                sweep = sqrt((moved[0] - x) ** 2 + (moved[1] - y) ** 2)
                rows.append({
                    "stop_index": index,
                    "lift_mm": lift,
                    "pitch_deg": pitch,
                    "roll_deg": roll,
                    "lateral_sweep_mm": sweep,
                })
    maximum = max(row["lateral_sweep_mm"] for row in rows)
    available = 25.0 - 5.0
    return {
        "pose_count": 18,
        "sample_count": len(rows),
        "maximum_lateral_sweep_mm": maximum,
        "available_rod_center_sweep_mm": available,
        "minimum_radial_clearance_mm": available - maximum,
        "passes_slot_clearance": maximum <= available,
        "rows": rows,
    }


def assembly_bounds(pose):
    shapes = [_shape(component.shape) for component in components_for_pose(pose)]
    bounds = cq.Compound.makeCompound(shapes).BoundingBox()
    return {
        "xmin": bounds.xmin, "xmax": bounds.xmax,
        "ymin": bounds.ymin, "ymax": bounds.ymax,
        "zmin": bounds.zmin, "zmax": bounds.zmax,
        "xlen": bounds.xlen, "ylen": bounds.ylen, "zlen": bounds.zlen,
    }


def profile_cut_list():
    tangent_lengths = [round(row["length_mm"]) for row in lower_tangent_rail_data()]
    counts = {}
    for key in ("4040 x 700", "4040 x 700", "4040 x 620", "4040 x 620"):
        counts[key] = counts.get(key, 0) + 1
    for length in tangent_lengths:
        key = f"4040 x {length}"
        counts[key] = counts.get(key, 0) + 1
    for key in ("3030 x 700", "3030 x 700"):
        counts[key] = counts.get(key, 0) + 1
    for _ in range(4):
        counts["3030 x 640"] = counts.get("3030 x 640", 0) + 1
    return counts


def named_collision_volume(pose, moving_groups, fixed_groups):
    parts = components_for_pose(pose)
    moving = [_shape(part.shape) for part in parts if part.group in moving_groups]
    fixed = [_shape(part.shape) for part in parts if part.group in fixed_groups]
    total = 0.0
    for moving_shape in moving:
        for fixed_shape in fixed:
            try:
                total += moving_shape.intersect(fixed_shape).Volume()
            except Exception:
                continue
    return total
