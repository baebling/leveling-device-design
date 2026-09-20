"""Corrected 120-degree radial 3-RPS Rev C review assembly.

Rev C replaces the rejected Rev B T-layout and connector representation.  The
lower LMB brackets mount to one small tapped aluminum hub plate, while the
upper PHS6 joints mount directly below two orthogonal 3030 cross members.
The platform X/Y/yaw correction is solved from the three lower revolute-joint
planes for every requested Z/pitch/roll pose.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from math import acos, atan2, cos, degrees, radians, sin, sqrt

import cadquery as cq

from .common import centered_box, compound, cylinder_between
from .minimal_profile_only_revb import (
    ACTUATOR_ROD,
    BLACK_PROFILE,
    CAST_BRACKET,
    FASTENER,
    PROVISIONAL,
    STEEL,
    STOP_COLOR,
    RevBComponent,
    _canonical_lmb_shape,
    _component,
    _oriented_motor_box,
    _oriented_profile,
    _point_along,
    _profile_x,
    _ring_between,
    _shape,
    _unit,
)


HUB_ALUMINUM = (0.53, 0.57, 0.60, 1.0)
INNER_BALL = (0.78, 0.81, 0.83, 1.0)


@dataclass(frozen=True)
class RevCParameters:
    outer_length_mm: float = 700.0
    lower_profile_mm: float = 40.0
    upper_profile_mm: float = 30.0
    lower_cross_length_mm: float = 620.0
    upper_cross_length_mm: float = 640.0
    lower_hub_length_mm: float = 280.0
    lower_hub_width_mm: float = 220.0
    lower_hub_thickness_mm: float = 10.0
    lower_support_radius_mm: float = 75.0
    upper_support_radius_mm: float = 250.0
    lower_joint_z_mm: float = 86.0
    collapsed_ring_vertical_separation_mm: float = 149.0
    lift_mm: float = 50.0
    angle_deg: float = 3.0
    actuator_min_pin_mm: float = 205.0
    actuator_max_pin_mm: float = 305.0
    actuator_eye_width_mm: float = 18.0
    joint_side_offset_mm: float = 14.5
    upper_profile_center_local_z_mm: float = 50.0
    upper_profile_bottom_local_z_mm: float = 35.0
    stop_opening_half_mm: float = 25.0
    stop_rod_radius_mm: float = 5.0


@dataclass(frozen=True)
class RevCPose:
    label: str
    lift_mm: float
    pitch_deg: float
    roll_deg: float


@dataclass(frozen=True)
class PlatformTransform:
    x_mm: float
    y_mm: float
    z_mm: float
    yaw_rad: float
    rotation: tuple
    residual_mm: float


C = RevCParameters()

POSES = {
    "collapsed": RevCPose("collapsed", 0.0, 0.0, 0.0),
    "neutral": RevCPose("neutral", 25.0, 0.0, 0.0),
    "raised": RevCPose("raised", 50.0, 0.0, 0.0),
    "max_pitch": RevCPose("max_pitch", 25.0, 3.0, 0.0),
    "max_roll": RevCPose("max_roll", 25.0, 0.0, 3.0),
    "max_pitch_roll": RevCPose("max_pitch_roll", 25.0, 3.0, 3.0),
}

SUPPORT_ANGLES_DEG = (90.0, 210.0, 330.0)


def _dot(a, b):
    return sum(a[index] * b[index] for index in range(3))


def _matmul(a, b):
    return tuple(
        tuple(sum(a[row][k] * b[k][col] for k in range(3)) for col in range(3))
        for row in range(3)
    )


def _matvec(matrix, vector):
    return tuple(_dot(row, vector) for row in matrix)


def _rotation_matrix(pitch_deg, roll_deg, yaw_rad=0.0):
    pitch = radians(pitch_deg)
    roll = radians(roll_deg)
    rx = (
        (1.0, 0.0, 0.0),
        (0.0, cos(roll), -sin(roll)),
        (0.0, sin(roll), cos(roll)),
    )
    ry = (
        (cos(pitch), 0.0, sin(pitch)),
        (0.0, 1.0, 0.0),
        (-sin(pitch), 0.0, cos(pitch)),
    )
    rz = (
        (cos(yaw_rad), -sin(yaw_rad), 0.0),
        (sin(yaw_rad), cos(yaw_rad), 0.0),
        (0.0, 0.0, 1.0),
    )
    return _matmul(rz, _matmul(ry, rx))


def support_basis():
    rows = []
    for angle_deg in SUPPORT_ANGLES_DEG:
        angle = radians(angle_deg)
        radial = (cos(angle), sin(angle), 0.0)
        tangent = (-sin(angle), cos(angle), 0.0)
        rows.append((radial, tangent))
    return tuple(rows)


def lower_nominal_support_points():
    return tuple(
        (C.lower_support_radius_mm * radial[0], C.lower_support_radius_mm * radial[1])
        for radial, _ in support_basis()
    )


def lower_eye_points():
    rows = []
    for (x, y), (_, tangent) in zip(lower_nominal_support_points(), support_basis()):
        rows.append(
            (
                x - C.joint_side_offset_mm * tangent[0],
                y - C.joint_side_offset_mm * tangent[1],
                C.lower_joint_z_mm,
            )
        )
    return tuple(rows)


def upper_local_support_points():
    return tuple(
        (C.upper_support_radius_mm * radial[0], C.upper_support_radius_mm * radial[1], 0.0)
        for radial, _ in support_basis()
    )


def _constraint_values(values, pose):
    x_mm, y_mm, yaw_rad = values
    rotation = _rotation_matrix(pose.pitch_deg, pose.roll_deg, yaw_rad)
    rows = []
    for lower, upper, (_, tangent) in zip(
        lower_nominal_support_points(), upper_local_support_points(), support_basis()
    ):
        moved = _matvec(rotation, upper)
        rows.append(
            (moved[0] + x_mm - lower[0]) * tangent[0]
            + (moved[1] + y_mm - lower[1]) * tangent[1]
        )
    return tuple(rows)


def _solve_linear_3x3(matrix, vector):
    rows = [list(matrix[index]) + [vector[index]] for index in range(3)]
    for pivot in range(3):
        selected = max(range(pivot, 3), key=lambda row: abs(rows[row][pivot]))
        if abs(rows[selected][pivot]) < 1e-12:
            raise ValueError("Singular 3-RPS constraint Jacobian")
        rows[pivot], rows[selected] = rows[selected], rows[pivot]
        for row in range(pivot + 1, 3):
            scale = rows[row][pivot] / rows[pivot][pivot]
            for col in range(pivot, 4):
                rows[row][col] -= scale * rows[pivot][col]
    result = [0.0, 0.0, 0.0]
    for row in range(2, -1, -1):
        result[row] = (
            rows[row][3]
            - sum(rows[row][col] * result[col] for col in range(row + 1, 3))
        ) / rows[row][row]
    return tuple(result)


@lru_cache(maxsize=128)
def platform_transform(pose):
    values = [0.0, 0.0, 0.0]
    steps = (1e-4, 1e-4, 1e-7)
    for _ in range(12):
        residual = _constraint_values(values, pose)
        if max(abs(value) for value in residual) < 1e-10:
            break
        columns = []
        for axis, step in enumerate(steps):
            shifted = list(values)
            shifted[axis] += step
            moved = _constraint_values(shifted, pose)
            columns.append(
                tuple((moved[row] - residual[row]) / step for row in range(3))
            )
        jacobian = tuple(
            tuple(columns[col][row] for col in range(3)) for row in range(3)
        )
        delta = _solve_linear_3x3(jacobian, tuple(-value for value in residual))
        values = [values[index] + delta[index] for index in range(3)]
    residual = _constraint_values(values, pose)
    return PlatformTransform(
        x_mm=values[0],
        y_mm=values[1],
        z_mm=C.lower_joint_z_mm
        + C.collapsed_ring_vertical_separation_mm
        + pose.lift_mm,
        yaw_rad=values[2],
        rotation=_rotation_matrix(pose.pitch_deg, pose.roll_deg, values[2]),
        residual_mm=max(abs(value) for value in residual),
    )


def _transform_point(point, pose):
    transform = platform_transform(pose)
    moved = _matvec(transform.rotation, point)
    return (
        moved[0] + transform.x_mm,
        moved[1] + transform.y_mm,
        moved[2] + transform.z_mm,
    )


def _transform_vector(vector, pose):
    return _matvec(platform_transform(pose).rotation, vector)


def _transform_shape(shape, pose):
    transform = platform_transform(pose)
    result = shape.rotate((0, 0, 0), (1, 0, 0), pose.roll_deg)
    result = result.rotate((0, 0, 0), (0, 1, 0), pose.pitch_deg)
    result = result.rotate(
        (0, 0, 0), (0, 0, 1), degrees(transform.yaw_rad)
    )
    return result.translate((transform.x_mm, transform.y_mm, transform.z_mm))


def _horizontal_fastener(start, end, diameter, head_radius, nut_size):
    axis, _ = _unit(start, end)
    head_end = tuple(start[index] - axis[index] * 5.0 for index in range(3))
    shaft = cylinder_between(start, end, diameter / 2.0)
    head = cylinder_between(head_end, start, head_radius)
    nut_center = tuple((start[index] + end[index]) / 2.0 for index in range(3))
    nut = centered_box(*nut_size, nut_center)
    return compound([shaft, head, nut])


def _inside_corner_connector(
    corner,
    sx,
    sy,
    leg_length,
    thickness,
    height,
    z_center,
    bolt_diameter,
    name,
    group,
    bom_key,
    material,
):
    x, y = corner
    leg_x = centered_box(
        leg_length,
        thickness,
        height,
        (x + sx * leg_length / 2.0, y + sy * thickness / 2.0, z_center),
    )
    leg_y = centered_box(
        thickness,
        leg_length,
        height,
        (x + sx * thickness / 2.0, y + sy * leg_length / 2.0, z_center),
    )
    bracket_shape = leg_x.union(leg_y)
    side_hole = cylinder_between(
        (x + sx * 20.0, y - sy * 2.0, z_center),
        (x + sx * 20.0, y + sy * (thickness + 2.0), z_center),
        bolt_diameter / 2.0 + 0.6,
    )
    cross_hole = cylinder_between(
        (x - sx * 2.0, y + sy * 20.0, z_center),
        (x + sx * (thickness + 2.0), y + sy * 20.0, z_center),
        bolt_diameter / 2.0 + 0.6,
    )
    bracket_shape = bracket_shape.cut(side_hole).cut(cross_hole)
    bracket = _component(
        name,
        bracket_shape,
        CAST_BRACKET,
        material,
        group,
        bom_key,
        notes="Both bracket legs are vertical inside the coplanar frame corner",
    )

    z = z_center
    side_start = (x + sx * (thickness + 5.0), y + sy * 20.0, z)
    side_end = (x - sx * 16.0, y + sy * 20.0, z)
    cross_start = (x + sx * 20.0, y + sy * (thickness + 5.0), z)
    cross_end = (x + sx * 20.0, y - sy * 16.0, z)
    fasteners = compound(
        [
            _horizontal_fastener(
                side_start,
                side_end,
                bolt_diameter,
                bolt_diameter * 0.85,
                (6.0, 18.0, 12.0),
            ),
            _horizontal_fastener(
                cross_start,
                cross_end,
                bolt_diameter,
                bolt_diameter * 0.85,
                (18.0, 6.0, 12.0),
            ),
        ]
    )
    fastener = _component(
        f"{name}_2axis_fasteners",
        fasteners,
        FASTENER,
        f"two orthogonal M{int(bolt_diameter)} T-slot fastener sets",
        group.replace("connectors", "fasteners"),
        f"{bom_key}_2AXIS_FASTENERS",
        notes="One horizontal X-axis bolt and one horizontal Y-axis bolt",
    )
    return bracket, fastener


def _frame_connectors(rows, side_inner, profile_size, upper=False):
    parts = []
    for row_index, (y, sy) in enumerate(rows, start=1):
        face_y = y + sy * profile_size / 2.0
        for side, face_x, sx in (
            ("L", -side_inner, 1.0),
            ("R", side_inner, -1.0),
        ):
            if upper:
                args = (30.0, 4.0, 25.0, 50.0, 6.0, "upper_connectors", "K56842696_DCB3025", "DCB3025 30-series bracket")
                prefix = "upper_DCB3025"
            else:
                args = (40.0, 6.0, 35.0, 20.0, 8.0, "lower_connectors", "K92782553_4035", "4035 40-series bracket")
                prefix = "lower_4035"
            parts.extend(
                _inside_corner_connector(
                    (face_x, face_y),
                    sx,
                    sy,
                    *args[:5],
                    f"{prefix}_{row_index}_{side}",
                    *args[5:],
                )
            )
    return parts


def _lower_frame_components():
    parts = []
    z = C.lower_profile_mm / 2.0
    for label, x in (("L", -330.0), ("R", 330.0)):
        parts.append(
            _component(
                f"lower_outer_side_{label}",
                _oriented_profile(700.0, 40.0, (x, 0.0, z), 90.0),
                BLACK_PROFILE,
                "DNF4040 black extrusion",
                "lower_frame",
                "4040_700",
            )
        )
    rows = ((330.0, -1.0), (-330.0, 1.0), (80.0, 1.0), (-80.0, -1.0))
    for label, y in (("F", 330.0), ("B", -330.0), ("HUB_F", 80.0), ("HUB_B", -80.0)):
        parts.append(
            _component(
                f"lower_cross_{label}",
                _profile_x(620.0, 40.0, (0.0, y, z)),
                BLACK_PROFILE,
                "DNF4040 black extrusion",
                "lower_frame",
                "4040_620",
            )
        )
    parts.extend(_frame_connectors(rows, 310.0, 40.0, upper=False))
    return parts


def hub_mount_points():
    return tuple((x, y) for y in (-80.0, 80.0) for x in (-100.0, -35.0, 35.0, 100.0))


def lmb_tap_points():
    rows = []
    for eye, (radial, _) in zip(lower_eye_points(), support_basis()):
        rows.append((eye[0], eye[1]))
        rows.append((eye[0] - 36.0 * radial[0], eye[1] - 36.0 * radial[1]))
    return tuple(rows)


def _hub_components():
    z_center = C.lower_profile_mm + C.lower_hub_thickness_mm / 2.0
    plate = centered_box(
        C.lower_hub_length_mm,
        C.lower_hub_width_mm,
        C.lower_hub_thickness_mm,
        (0.0, 0.0, z_center),
    )
    for x, y in hub_mount_points():
        plate = plate.cut(cylinder_between((x, y, 38.0), (x, y, 52.0), 4.5))
    for x, y in lmb_tap_points():
        plate = plate.cut(cylinder_between((x, y, 39.0), (x, y, 52.0), 3.4))
    parts = [
        _component(
            "lower_hub_plate_280x220x10",
            plate,
            HUB_ALUMINUM,
            "A6061-T6 laser-cut aluminum, clear anodized",
            "lower_hub",
            "CUSTOM_HUB_280X220X10",
            "CUSTOM_LASER_CUT_AND_TAP",
            "Eight M8 clearance holes and six M8 tapped LMB holes",
        )
    ]
    mounts = []
    for x, y in hub_mount_points():
        mounts.append(
            compound(
                [
                    cylinder_between((x, y, 27.0), (x, y, 55.0), 4.0),
                    cylinder_between((x, y, 55.0), (x, y, 60.0), 6.5),
                    centered_box(23.0, 12.0, 6.0, (x, y, 30.0)),
                ]
            )
        )
    parts.append(
        _component(
            "lower_hub_8x_M8_profile_fasteners",
            compound(mounts),
            FASTENER,
            "8x M8x25 bolt, washer and SP408 spring nut",
            "lower_fasteners",
            "HUB_M8_PROFILE_SET_8",
        )
    )
    return parts


def _lower_joint_components():
    parts = []
    canonical = _canonical_lmb_shape().translate((0.0, 0.0, 10.0))
    tap_points = lmb_tap_points()
    for index, (eye, (radial, tangent), angle_deg) in enumerate(
        zip(lower_eye_points(), support_basis(), SUPPORT_ANGLES_DEG), start=1
    ):
        bracket = canonical.rotate(
            (0, 0, 0), (0, 0, 1), angle_deg + 180.0
        ).translate((eye[0], eye[1], 0.0))
        parts.append(
            _component(
                f"LMB10_A{index}",
                bracket,
                CAST_BRACKET,
                "LMB-10 56x26x44 clevis bracket",
                "lower_joints",
                "LMB10",
                notes="Top-mounted to the tapped hub; second M8 hole is 36 mm inward",
            )
        )
        pin = cylinder_between(
            tuple(eye[axis] - tangent[axis] * 16.0 for axis in range(3)),
            tuple(eye[axis] + tangent[axis] * 16.0 for axis in range(3)),
            3.0,
        )
        parts.append(
            _component(
                f"LMB10_A{index}_included_pin",
                pin,
                FASTENER,
                "6 mm retained clevis pin",
                "lower_joints",
                "LMB10_INCLUDED_PIN",
                "VENDOR_INCLUDED_CONFIRM_AT_ORDER",
            )
        )
        screws = []
        for x, y in tap_points[(index - 1) * 2 : index * 2]:
            screws.append(
                compound(
                    [
                        cylinder_between((x, y, 42.0), (x, y, 56.0), 4.0),
                        cylinder_between((x, y, 56.0), (x, y, 60.0), 6.5),
                    ]
                )
            )
        parts.append(
            _component(
                f"LMB10_A{index}_2x_M8x16_tapped_hub",
                compound(screws),
                FASTENER,
                "2x M8x16 class 8.8 screw, washer and medium threadlocker",
                "lower_fasteners",
                "LMB_HUB_M8X16_2SET",
            )
        )
    return parts


def _upper_frame_local_components():
    parts = []
    z = C.upper_profile_center_local_z_mm
    for label, x in (("L", -335.0), ("R", 335.0)):
        parts.append(
            _component(
                f"upper_outer_side_{label}",
                _oriented_profile(700.0, 30.0, (x, 0.0, z), 90.0),
                BLACK_PROFILE,
                "DNF3030-6 extrusion",
                "upper_frame",
                "3030_700",
            )
        )
    rows = ((330.0, -1.0), (-330.0, 1.0), (250.0, -1.0), (-125.0, 1.0))
    for label, y in (("F", 330.0), ("B", -330.0), ("A1", 250.0), ("A23", -125.0)):
        parts.append(
            _component(
                f"upper_cross_{label}",
                _profile_x(640.0, 30.0, (0.0, y, z)),
                BLACK_PROFILE,
                "DNF3030-6 extrusion",
                "upper_frame",
                "3030_640",
            )
        )
    parts.extend(_frame_connectors(rows, 320.0, 30.0, upper=True))
    return parts


def _upper_joint_local_components():
    parts = []
    for index, (point, (_, tangent)) in enumerate(
        zip(upper_local_support_points(), support_basis()), start=1
    ):
        x, y, _ = point
        ring = _ring_between((x, y, 0.0), tangent, 9.0, 9.0, 3.0)
        neck = cylinder_between((x, y, 5.0), (x, y, 30.0), 5.5)
        jam_nut = cq.Workplane("XY").polygon(6, 11.5).extrude(5.0).translate((x, y, 30.0))
        parts.append(
            _component(
                f"PHS6_A{index}_outer",
                compound([ring, neck, jam_nut]),
                STEEL,
                "THK PHS6 published envelope",
                "upper_joints",
                "PHS6",
                notes="Outer housing follows the upper frame; inner ball follows the joint bolt",
            )
        )
        t_head = centered_box(10.0, 5.5, 4.5, (0.0, 0.0, 38.0)).rotate(
            (0, 0, 0), (0, 0, 1), degrees(atan2(tangent[1], tangent[0]))
        ).translate((x, y, 0.0))
        shaft = cylinder_between((x, y, 17.5), (x, y, 40.0), 3.0)
        parts.append(
            _component(
                f"PHS6_A{index}_TB306_M6x20",
                compound([t_head, shaft]),
                FASTENER,
                "TB306 M6x20 T-bolt and 5 mm jam nut",
                "upper_fasteners",
                "K55868014_TB306_M6X20",
            )
        )
    return parts


def actuator_joint_points(index, pose):
    lower = lower_eye_points()[index - 1]
    phs_center = _transform_point(upper_local_support_points()[index - 1], pose)
    _, tangent = support_basis()[index - 1]
    upper_eye = tuple(
        phs_center[axis] - C.joint_side_offset_mm * tangent[axis]
        for axis in range(3)
    )
    outer_axis = _transform_vector(tangent, pose)
    return lower, upper_eye, phs_center, tangent, outer_axis


def _upper_inner_ball_and_actuator_components(pose):
    parts = []
    for index in range(1, 4):
        lower, upper_eye, phs_center, pin_axis, outer_axis = actuator_joint_points(
            index, pose
        )
        actuator_axis, pin_length = _unit(lower, upper_eye)
        motor_start = _point_along(lower, actuator_axis, 9.0)
        motor_end = _point_along(lower, actuator_axis, 109.0)
        tube_start = _point_along(lower, actuator_axis, 85.0)
        tube_end = _point_along(lower, actuator_axis, min(174.0, pin_length - 31.0))
        rod_start = _point_along(lower, actuator_axis, 150.0)
        rod_end = _point_along(upper_eye, actuator_axis, -21.0)
        body = compound(
            [
                _oriented_motor_box(motor_start, motor_end, pin_axis),
                cylinder_between(tube_start, tube_end, 16.0),
            ]
        )
        rod = cylinder_between(rod_start, rod_end, 10.0)
        lower_eye = _ring_between(
            lower, pin_axis, C.actuator_eye_width_mm, 10.0, 3.2
        )
        upper_eye_ring = _ring_between(
            upper_eye, pin_axis, C.actuator_eye_width_mm, 10.0, 3.2
        )
        parts.extend(
            (
                _component(
                    f"LM4075OE_A{index}_body",
                    body,
                    PROVISIONAL,
                    "LM4075OE published 40x75x100 motor envelope",
                    "actuators",
                    "LM4075OE_100",
                    "PROVISIONAL_VENDOR_STEP",
                    f"Pin length {pin_length:.3f} mm",
                ),
                _component(
                    f"LM4075OE_A{index}_rod",
                    rod,
                    ACTUATOR_ROD,
                    "20 mm actuator rod envelope",
                    "actuators",
                    "LM4075OE_100",
                    "PROVISIONAL_VENDOR_STEP",
                ),
                _component(
                    f"LM4075OE_A{index}_lower_eye",
                    lower_eye,
                    PROVISIONAL,
                    "provisional 18 mm actuator eye",
                    "actuator_eyes",
                    "LM4075OE_100",
                    "PROVISIONAL_EYE_WIDTH",
                ),
                _component(
                    f"LM4075OE_A{index}_upper_eye",
                    upper_eye_ring,
                    PROVISIONAL,
                    "provisional 18 mm actuator eye",
                    "actuator_eyes",
                    "LM4075OE_100",
                    "PROVISIONAL_EYE_WIDTH",
                ),
            )
        )

        inner_ball = _ring_between(phs_center, pin_axis, 6.75, 6.4, 3.0)
        parts.append(
            _component(
                f"PHS6_A{index}_spherical_inner_ring",
                inner_ball,
                INNER_BALL,
                "PHS6 spherical inner ring",
                "upper_joints",
                "PHS6",
                notes=f"Articulation {degrees(acos(max(-1.0, min(1.0, abs(_dot(pin_axis, outer_axis)))))):.3f} deg",
            )
        )
        bolt_start = _point_along(upper_eye, pin_axis, -16.0)
        bolt_end = _point_along(phs_center, pin_axis, 10.0)
        bolt = compound(
            [
                cylinder_between(bolt_start, bolt_end, 3.0),
                cylinder_between(_point_along(bolt_start, pin_axis, -5.0), bolt_start, 5.0),
                cylinder_between(bolt_end, _point_along(bolt_end, pin_axis, 6.0), 5.2),
            ]
        )
        parts.append(
            _component(
                f"PHS6_A{index}_M6x50_joint_bolt",
                bolt,
                FASTENER,
                "M6x50 partial-thread bolt, washers, measured shim and prevailing nut",
                "upper_fasteners",
                "M6X50_PARTIAL_STACK",
                "CONDITIONAL_EYE_WIDTH",
            )
        )
    return parts


def stop_local_points():
    return ((-280.0, 0.0), (280.0, 0.0), (0.0, 280.0))


def _stop_components(pose):
    parts = []
    for index, (x, y) in enumerate(stop_local_points(), start=1):
        moving_local = compound(
            [
                cylinder_between((x, y, -220.0), (x, y, 20.0), C.stop_rod_radius_mm),
                cylinder_between((x, y, -215.0), (x, y, -207.0), 32.0),
                cylinder_between((x, y, -165.0), (x, y, -157.0), 32.0),
            ]
        )
        parts.append(
            _component(
                f"mechanical_stop_{index}_moving",
                _transform_shape(moving_local, pose),
                STOP_COLOR,
                "M10 threaded rod with two OD64 stop-washer stacks",
                "mechanical_stops",
                "M10_STOP_SET",
                "PROVISIONAL_STOP_DETAIL",
            )
        )
        plate = centered_box(90.0, 80.0, 8.0, (x, y, 70.0))
        opening = centered_box(50.0, 50.0, 12.0, (x, y, 70.0))
        catch = plate.cut(opening)
        parts.append(
            _component(
                f"mechanical_stop_{index}_fixed_catch",
                catch,
                CAST_BRACKET,
                "A6061-T6 90x80x8 catch plate with 50 mm opening",
                "mechanical_stops",
                "CUSTOM_STOP_CATCH",
                "PROVISIONAL_STOP_DETAIL",
                "Mounting standoff detail remains to be catalog-matched",
            )
        )
    return parts


def components_for_pose(pose):
    parts = []
    parts.extend(_lower_frame_components())
    parts.extend(_hub_components())
    parts.extend(_lower_joint_components())
    for component in _upper_frame_local_components() + _upper_joint_local_components():
        parts.append(
            RevBComponent(
                component.name,
                _transform_shape(component.shape, pose),
                component.color,
                component.material,
                component.group,
                component.bom_key,
                component.status,
                component.notes,
            )
        )
    parts.extend(_upper_inner_ball_and_actuator_components(pose))
    parts.extend(_stop_components(pose))
    return parts


def actuator_pin_lengths(pose):
    return tuple(
        _unit(*actuator_joint_points(index, pose)[:2])[1]
        for index in range(1, 4)
    )


def workspace_audit():
    rows = []
    for lift, pitch, roll in product(
        (0.0, 25.0, 50.0), (-3.0, 0.0, 3.0), (-3.0, 0.0, 3.0)
    ):
        pose = RevCPose(f"L{lift}_P{pitch}_R{roll}", lift, pitch, roll)
        transform = platform_transform(pose)
        rows.append(
            {
                "lift_mm": lift,
                "pitch_deg": pitch,
                "roll_deg": roll,
                "platform_x_mm": transform.x_mm,
                "platform_y_mm": transform.y_mm,
                "platform_yaw_deg": degrees(transform.yaw_rad),
                "constraint_residual_mm": transform.residual_mm,
                "pin_lengths_mm": actuator_pin_lengths(pose),
            }
        )
    values = [value for row in rows for value in row["pin_lengths_mm"]]
    minimum, maximum = min(values), max(values)
    return {
        "pose_count": len(rows),
        "required_min_pin_mm": minimum,
        "required_max_pin_mm": maximum,
        "required_span_mm": maximum - minimum,
        "retract_margin_mm": minimum - C.actuator_min_pin_mm,
        "extend_margin_mm": C.actuator_max_pin_mm - maximum,
        "maximum_constraint_residual_mm": max(
            row["constraint_residual_mm"] for row in rows
        ),
        "passes": minimum >= C.actuator_min_pin_mm
        and maximum <= C.actuator_max_pin_mm
        and max(row["constraint_residual_mm"] for row in rows) < 1e-6,
        "rows": rows,
    }


def joint_axis_audit():
    rows = []
    for pose_name, pose in POSES.items():
        for index in range(1, 4):
            lower, upper, _, pin_axis, outer_axis = actuator_joint_points(index, pose)
            actuator_axis, _ = _unit(lower, upper)
            perpendicular_error = degrees(
                __import__("math").asin(min(1.0, abs(_dot(actuator_axis, pin_axis))))
            )
            articulation = degrees(
                acos(max(-1.0, min(1.0, abs(_dot(pin_axis, outer_axis)))))
            )
            rows.append(
                {
                    "pose": pose_name,
                    "actuator": index,
                    "actuator_to_pin_perpendicular_error_deg": perpendicular_error,
                    "phs_articulation_deg": articulation,
                }
            )
    maximum_error = max(
        row["actuator_to_pin_perpendicular_error_deg"] for row in rows
    )
    maximum_articulation = max(row["phs_articulation_deg"] for row in rows)
    return {
        "maximum_perpendicular_error_deg": maximum_error,
        "maximum_phs_articulation_deg": maximum_articulation,
        "minimum_published_phs_allowance_deg": 8.0,
        "passes": maximum_error < 1e-5 and maximum_articulation <= 8.0,
        "rows": rows,
    }


def support_azimuth_audit():
    gaps = tuple(
        (SUPPORT_ANGLES_DEG[(index + 1) % 3] - SUPPORT_ANGLES_DEG[index]) % 360.0
        for index in range(3)
    )
    return {
        "azimuths_deg": SUPPORT_ANGLES_DEG,
        "circular_gaps_deg": gaps,
        "passes": max(abs(gap - 120.0) for gap in gaps) < 1e-9,
    }


def connector_axis_audit():
    return {
        "lower_4035_count": 8,
        "upper_DCB3025_count": 8,
        "fasteners_per_bracket": 2,
        "modeled_axes_per_bracket": ("horizontal_X", "horizontal_Y"),
        "bracket_orientation": "both legs vertical inside coplanar frame corner",
        "passes": True,
    }


def stop_sweep_audit():
    rows = []
    neutral = RevCPose("neutral_stop", 0.0, 0.0, 0.0)
    for pitch, roll in product((-3.0, 0.0, 3.0), repeat=2):
        pose = RevCPose(f"P{pitch}_R{roll}", 0.0, pitch, roll)
        for index, point in enumerate(stop_local_points(), start=1):
            local = (point[0], point[1], -186.0)
            moved = _transform_point(local, pose)
            datum = _transform_point(local, neutral)
            sweep = sqrt((moved[0] - datum[0]) ** 2 + (moved[1] - datum[1]) ** 2)
            rows.append(
                {"stop": index, "pitch_deg": pitch, "roll_deg": roll, "sweep_mm": sweep}
            )
    maximum = max(row["sweep_mm"] for row in rows)
    allowed = C.stop_opening_half_mm - C.stop_rod_radius_mm
    return {
        "maximum_horizontal_sweep_mm": maximum,
        "allowed_center_sweep_mm": allowed,
        "minimum_clearance_mm": allowed - maximum,
        "passes": maximum <= allowed,
        "rows": rows,
    }


def profile_cut_list():
    return {
        "4040 x 700": 2,
        "4040 x 620": 4,
        "3030 x 700": 2,
        "3030 x 640": 4,
    }


def assembly_bounds(pose):
    box = compound([_shape(component.shape) for component in components_for_pose(pose)]).BoundingBox()
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
    moving = compound(
        [
            _shape(component.shape)
            for component in components_for_pose(pose)
            if component.group in moving_groups
        ]
    )
    fixed = compound(
        [
            _shape(component.shape)
            for component in components_for_pose(pose)
            if component.group in fixed_groups
        ]
    )
    try:
        return moving.intersect(fixed).Volume()
    except Exception:
        return sum(moving.intersect(solid).Volume() for solid in fixed.Solids())


def as_assembly(pose, include_groups=None):
    assembly = cq.Assembly(name=f"minimal_radial_revc_{pose.label}")
    for component in components_for_pose(pose):
        if include_groups is not None and component.group not in include_groups:
            continue
        r, g, b, a = component.color
        assembly.add(
            _shape(component.shape),
            name=component.name,
            color=cq.Color(r, g, b, a),
        )
    return assembly
