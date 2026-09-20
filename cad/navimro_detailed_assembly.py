"""Bolt-level mechanical digital mock-up for Fusion 360 review.

The model is intentionally explicit about provisional vendor interfaces. Yellow
parts must be replaced or re-parameterized after delivered-part measurement.
"""

from dataclasses import dataclass, replace
from math import acos, degrees, radians, sin, cos
from pathlib import Path

import cadquery as cq

from .common import centered_box, compound, cylinder_between
from .navimro_fabrication_parameters import N, NAVIMRO_POSES, transform_local_point


ALUMINIUM = (0.50, 0.56, 0.60, 1.0)
STEEL = (0.12, 0.25, 0.34, 1.0)
ACRYLIC = (0.45, 0.82, 0.88, 0.34)
PURCHASED = (0.86, 0.62, 0.20, 1.0)
FASTENER = (0.18, 0.19, 0.20, 1.0)
WASHER = (0.68, 0.71, 0.73, 1.0)
PROVISIONAL = (0.96, 0.76, 0.12, 1.0)
STOP = (0.77, 0.19, 0.13, 1.0)


@dataclass(frozen=True)
class DetailedComponent:
    name: str
    shape: object
    color: tuple
    material: str
    group: str
    bom_key: str
    status: str = "RELEASED"
    notes: str = ""


def _shape(value):
    return value.val() if hasattr(value, "val") else value


def _component(name, shape, color, material, group, bom_key, status="RELEASED", notes=""):
    return DetailedComponent(name, shape, color, material, group, bom_key, status, notes)


def _tslot_x(length, center):
    x, y, z = center
    profile = centered_box(length, 40.0, 40.0, center)
    cuts = [
        centered_box(length + 2.0, 8.0, 6.0, (x, y, z + 17.0)),
        centered_box(length + 2.0, 8.0, 6.0, (x, y, z - 17.0)),
        centered_box(length + 2.0, 6.0, 8.0, (x, y + 17.0, z)),
        centered_box(length + 2.0, 6.0, 8.0, (x, y - 17.0, z)),
        cylinder_between((x - length / 2.0 - 1.0, y, z), (x + length / 2.0 + 1.0, y, z), 3.5),
    ]
    for cut in cuts:
        profile = profile.cut(cut)
    return profile


def _tslot_y(length, center):
    x, y, z = center
    return _tslot_x(length, (0.0, 0.0, 0.0)).rotate((0, 0, 0), (0, 0, 1), 90).translate((x, y, z))


def _ring_z(x, y, z0, thickness, outer_radius, inner_radius):
    outer = cq.Workplane("XY").circle(outer_radius).extrude(thickness).translate((x, y, z0))
    inner = cq.Workplane("XY").circle(inner_radius).extrude(thickness + 2.0).translate((x, y, z0 - 1.0))
    return outer.cut(inner)


def _hex_z(x, y, z0, thickness, across_corners=13.0):
    return cq.Workplane("XY").polygon(6, across_corners).extrude(thickness).translate((x, y, z0))


def _vertical_fastener(parts, prefix, x, y, z_top, grip, group, size="M8", end="tnut", status="RELEASED"):
    diameter = {"M4": 4.0, "M5": 5.0, "M6": 6.0, "M8": 8.0}[size]
    head_radius = {"M4": 3.7, "M5": 4.5, "M6": 5.2, "M8": 6.5}[size]
    head_height = {"M4": 3.0, "M5": 3.5, "M6": 4.0, "M8": 5.0}[size]
    washer_r = {"M4": 4.5, "M5": 5.0, "M6": 6.0, "M8": 8.5}[size]
    screw = compound([
        cylinder_between((x, y, z_top - grip), (x, y, z_top + head_height), diameter / 2.0),
        cq.Workplane("XY").circle(head_radius).extrude(head_height).translate((x, y, z_top)),
    ])
    parts.append(_component(f"{prefix}_screw", screw, FASTENER, f"{size} socket screw", group, f"{size}_SOCKET_SCREW", status))
    parts.append(_component(f"{prefix}_washer", _ring_z(x, y, z_top - 1.0, 1.0, washer_r, diameter / 2.0 + 0.3), WASHER, f"{size} flat washer", group, f"{size}_WASHER", status))
    if end == "tnut":
        tnut = centered_box(18.0 if size == "M8" else 14.0, 10.0, 5.0, (x, y, z_top - grip - 2.5))
        parts.append(_component(f"{prefix}_tnut", tnut, FASTENER, f"{size} T-slot nut", group, f"{size}_TNUT", status))
    elif end == "nyloc":
        nut_across = {"M4": 7.5, "M5": 9.0, "M6": 10.0, "M8": 13.0}[size]
        nut = _hex_z(x, y, z_top - grip - 6.0, 6.0, nut_across)
        parts.append(_component(f"{prefix}_nyloc", nut, FASTENER, f"{size} nyloc nut", group, f"{size}_NYLOC", status))


def _vertical_fastener_up(parts, prefix, x, y, z_head, grip, group, size="M8", status="RELEASED"):
    """Model an underside screw that enters a T-slot above the plate."""
    diameter = {"M4": 4.0, "M5": 5.0, "M6": 6.0, "M8": 8.0}[size]
    head_radius = {"M4": 3.7, "M5": 4.5, "M6": 5.2, "M8": 6.5}[size]
    head_height = {"M4": 3.0, "M5": 3.5, "M6": 4.0, "M8": 5.0}[size]
    washer_r = {"M4": 4.5, "M5": 5.0, "M6": 6.0, "M8": 8.5}[size]
    screw = compound([
        cylinder_between((x, y, z_head), (x, y, z_head + grip), diameter / 2.0),
        cq.Workplane("XY").circle(head_radius).extrude(head_height).translate((x, y, z_head - head_height)),
    ])
    parts.append(_component(f"{prefix}_screw", screw, FASTENER, f"{size} socket screw", group, f"{size}_SOCKET_SCREW", status))
    parts.append(_component(
        f"{prefix}_washer",
        _ring_z(x, y, z_head, 1.0, washer_r, diameter / 2.0 + 0.3),
        WASHER,
        f"{size} flat washer",
        group,
        f"{size}_WASHER",
        status,
    ))
    tnut = centered_box(
        18.0 if size == "M8" else 14.0,
        10.0,
        5.0,
        (x, y, z_head + grip + 2.5),
    )
    parts.append(_component(f"{prefix}_tnut", tnut, FASTENER, f"{size} T-slot nut", group, f"{size}_TNUT", status))


def _axis_fastener(parts, prefix, center, axis, total_length, group, size="M8", status="PROVISIONAL"):
    cx, cy, cz = center
    ax, ay, az = axis
    half = total_length / 2.0
    start = (cx - ax * half, cy - ay * half, cz - az * half)
    end = (cx + ax * half, cy + ay * half, cz + az * half)
    diameter = {"M5": 5.0, "M6": 6.0, "M8": 8.0}[size]
    head_radius = {"M5": 4.5, "M6": 5.2, "M8": 6.5}[size]
    nut_radius = {"M5": 4.6, "M6": 5.4, "M8": 6.7}[size]
    washer_radius = {"M5": 5.0, "M6": 6.0, "M8": 8.5}[size]
    pin = cylinder_between(start, end, diameter / 2.0)
    head = cylinder_between(
        (start[0] - ax * 5.0, start[1] - ay * 5.0, start[2] - az * 5.0),
        start,
        head_radius,
    )
    nut = cylinder_between(end, (end[0] + ax * 6.0, end[1] + ay * 6.0, end[2] + az * 6.0), nut_radius)
    washer_a_end = (start[0] + ax, start[1] + ay, start[2] + az)
    washer_b_start = (end[0] - ax, end[1] - ay, end[2] - az)
    washer_a = cylinder_between(start, washer_a_end, washer_radius).cut(
        cylinder_between(
            (start[0] - ax, start[1] - ay, start[2] - az),
            (washer_a_end[0] + ax, washer_a_end[1] + ay, washer_a_end[2] + az),
            diameter / 2.0 + 0.3,
        )
    )
    washer_b = cylinder_between(washer_b_start, end, washer_radius).cut(
        cylinder_between(
            (washer_b_start[0] - ax, washer_b_start[1] - ay, washer_b_start[2] - az),
            (end[0] + ax, end[1] + ay, end[2] + az),
            diameter / 2.0 + 0.3,
        )
    )
    parts.extend([
        _component(f"{prefix}_pin", compound([pin, head]), FASTENER, f"{size} pivot bolt", group, f"{size}_PIVOT_BOLT", status),
        _component(f"{prefix}_washer_A", washer_a, WASHER, f"{size} flat washer", group, f"{size}_WASHER", status),
        _component(f"{prefix}_washer_B", washer_b, WASHER, f"{size} flat washer", group, f"{size}_WASHER", status),
        _component(f"{prefix}_nyloc", nut, FASTENER, f"{size} nyloc nut", group, f"{size}_NYLOC", status),
    ])


def _side_tslot_fastener(parts, prefix, x, z, side, surface_y, group, size="M4", status="PROVISIONAL"):
    """Model a screw through a side-mounted bracket into a profile side T-slot."""
    diameter = {"M4": 4.0, "M5": 5.0, "M6": 6.0}[size]
    head_radius = {"M4": 3.7, "M5": 4.5, "M6": 5.2}[size]
    washer_radius = {"M4": 4.5, "M5": 5.0, "M6": 6.0}[size]
    head_y = surface_y + side * 39.0
    tnut_y = surface_y - side * 3.0
    screw = compound([
        cylinder_between((x, tnut_y, z), (x, head_y, z), diameter / 2.0),
        cylinder_between((x, head_y, z), (x, head_y + side * 4.0, z), head_radius),
    ])
    washer = _ring_between_axis((x, head_y, z), (0, 1, 0), 1.0, washer_radius, diameter / 2.0 + 0.3)
    tnut = centered_box(14.0, 5.0, 10.0, (x, tnut_y, z))
    parts.extend([
        _component(f"{prefix}_screw", screw, FASTENER, f"{size} socket screw", group, f"{size}_SOCKET_SCREW", status),
        _component(f"{prefix}_washer", washer, WASHER, f"{size} flat washer", group, f"{size}_WASHER", status),
        _component(f"{prefix}_tnut", tnut, FASTENER, f"{size} T-slot nut", group, f"{size}_TNUT", status),
    ])


def _vertical_counterbored_fastener(parts, prefix, x, y, flange_bottom_z, group, status="PROVISIONAL"):
    """M4 screw recessed in an LMF12UU counterbore with washer/nut below."""
    shaft = cylinder_between((x, y, flange_bottom_z - 8.0), (x, y, flange_bottom_z + 3.0), 2.0)
    head = cylinder_between((x, y, flange_bottom_z + 3.0), (x, y, flange_bottom_z + 6.0), 3.7)
    washer = _ring_z(x, y, flange_bottom_z - 7.0, 1.0, 4.5, 2.3)
    nut = _hex_z(x, y, flange_bottom_z - 13.0, 6.0, 7.5)
    parts.extend([
        _component(f"{prefix}_screw", compound([shaft, head]), FASTENER, "M4 socket screw", group, "M4_SOCKET_SCREW", status),
        _component(f"{prefix}_washer", washer, WASHER, "M4 flat washer", group, "M4_WASHER", status),
        _component(f"{prefix}_nyloc", nut, FASTENER, "M4 nyloc nut", group, "M4_NYLOC", status),
    ])


def _joint_plate(x, y, z):
    plate = centered_box(42.0, 42.0, 4.0, (x, y, z))
    for dx, dy in ((-11.0, 11.0), (11.0, -11.0)):
        plate = plate.cut(cylinder_between((x + dx, y + dy, z - 3.0), (x + dx, y + dy, z + 3.0), 4.5))
    return plate


def _add_frame(parts, prefix, z, long_length, end_length, cross_xs, group, upper=False):
    y_long = (end_length + 40.0) / 2.0
    x_end = (long_length - 40.0) / 2.0
    rails = [
        (f"{prefix}_long_left", _tslot_x(long_length, (0.0, -y_long, z)), long_length),
        (f"{prefix}_long_right", _tslot_x(long_length, (0.0, y_long, z)), long_length),
        (f"{prefix}_end_front", _tslot_y(end_length, (x_end, 0.0, z)), end_length),
        (f"{prefix}_end_rear", _tslot_y(end_length, (-x_end, 0.0, z)), end_length),
    ]
    for index, x in enumerate(cross_xs, start=1):
        cross_length = (
            N.upper_crossmember_length_mm
            if upper
            else N.lower_crossmember_length_mm
        )
        rails.append((f"{prefix}_cross_{index}", _tslot_y(cross_length, (x, 0.0, z)), cross_length))
    if upper:
        rails.extend([
            (f"{prefix}_center_X_A", _tslot_x(N.upper_center_length_mm, (0.0, -50.0, z)), N.upper_center_length_mm),
            (f"{prefix}_center_X_B", _tslot_x(N.upper_center_length_mm, (0.0, 50.0, z)), N.upper_center_length_mm),
        ])
    for name, rail, length in rails:
        parts.append(_component(name, rail, ALUMINIUM, "6063-T5 4040 T-slot profile", group, f"PROFILE_4040_{int(length)}"))

    joints = [(sx * x_end, sy * y_long) for sx in (-1, 1) for sy in (-1, 1)]
    joints.extend((x, sy * y_long) for x in cross_xs for sy in (-1, 1))
    if upper:
        joints.extend(
            (sx * N.upper_center_length_mm / 2.0, y)
            for sx in (-1, 1)
            for y in (-50.0, 50.0)
        )
    for index, (x, y) in enumerate(joints, start=1):
        parts.append(_component(f"{prefix}_joint_plate_{index:02d}", _joint_plate(x, y, z + 22.0), STEEL, "profile joint angle/plate", group, "PROFILE_JOINT_PLATE"))
        _vertical_fastener(parts, f"{prefix}_J{index:02d}A", x - 11.0, y + 11.0, z + 25.0, 14.0, group)
        _vertical_fastener(parts, f"{prefix}_J{index:02d}B", x + 11.0, y - 11.0, z + 25.0, 14.0, group)


def _slotted_plate(length, width, thickness, center, slot_centers=()):
    x, y, z = center
    plate = centered_box(length, width, thickness, center)
    for sx, sy, slot_length, slot_width in slot_centers:
        slot = centered_box(slot_length - slot_width, slot_width, thickness + 2.0, (x + sx, y + sy, z))
        slot = slot.union(cylinder_between((x + sx - (slot_length - slot_width) / 2.0, y + sy, z - thickness), (x + sx - (slot_length - slot_width) / 2.0, y + sy, z + thickness), slot_width / 2.0))
        slot = slot.union(cylinder_between((x + sx + (slot_length - slot_width) / 2.0, y + sy, z - thickness), (x + sx + (slot_length - slot_width) / 2.0, y + sy, z + thickness), slot_width / 2.0))
        plate = plate.cut(slot)
    return plate


def _add_lower_frame(parts):
    group = "01_LOWER_FRAME"
    _add_frame(parts, "LWR", N.lower_frame_center_z_mm, N.lower_long_length_mm, N.lower_end_length_mm, (-N.guide_shaft_x_mm, N.guide_shaft_x_mm), group)
    for cross_index, (shaft_x, shaft_y) in enumerate(N.guide_shaft_points_xy, start=1):
        part_index = next(
            i for i, part in enumerate(parts) if part.name == f"LWR_cross_{cross_index}"
        )
        clearance = cylinder_between(
            (shaft_x, shaft_y, N.lower_frame_center_z_mm - 24.0),
            (shaft_x, shaft_y, N.lower_frame_center_z_mm + 24.0),
            6.6,
        )
        parts[part_index] = replace(
            parts[part_index],
            shape=parts[part_index].shape.cut(clearance),
            notes="Rev E vertical guide-shaft clearance hole; deburr and sleeve edge if required",
        )
    actuator_cross_x = 175.0
    parts.append(_component(
        "LWR_actuator_cross",
        _tslot_y(N.lower_crossmember_length_mm, (actuator_cross_x, 0.0, N.lower_frame_center_z_mm)),
        ALUMINIUM,
        "6063-T5 4040 T-slot profile",
        group,
        f"PROFILE_4040_{int(N.lower_crossmember_length_mm)}",
    ))
    y_long = (N.lower_end_length_mm + 40.0) / 2.0
    for side, y in enumerate((-y_long, y_long), start=1):
        parts.append(_component(
            f"LWR_actuator_cross_joint_plate_{side}",
            _joint_plate(actuator_cross_x, y, N.lower_frame_center_z_mm + 22.0),
            STEEL,
            "profile joint angle/plate",
            group,
            "PROFILE_JOINT_PLATE",
        ))
        _vertical_fastener(parts, f"LWR_AX_J{side}A", actuator_cross_x - 11.0, y + 11.0, N.lower_frame_center_z_mm + 25.0, 14.0, group)
        _vertical_fastener(parts, f"LWR_AX_J{side}B", actuator_cross_x + 11.0, y - 11.0, N.lower_frame_center_z_mm + 25.0, 14.0, group)
    for index, (x, y) in enumerate(((-350, -310), (-350, 310), (350, -310), (350, 310)), start=1):
        plate = _slotted_plate(120, 50, 6, (x, y, 3), ((-35, 0, 24, 11), (35, 0, 24, 11)))
        parts.append(_component(f"NVR-P01_mount_tab_{index}", plate, STEEL, "SS400 50x6", group, "NVR-P01"))
        _vertical_fastener(parts, f"P01_{index}A", x - 35, y, 8, 18, group)
        _vertical_fastener(parts, f"P01_{index}B", x + 35, y, 8, 18, group)
    for index, (x, y) in enumerate(N.lower_points_xy, start=1):
        support_x = actuator_cross_x if index == 1 else -N.guide_shaft_x_mm
        radius = (x * x + y * y) ** 0.5
        angle_deg = degrees(__import__("math").atan2(y, x))
        plate_radius = radius - 50.0
        plate = centered_box(100, 50, 6, (plate_radius, 0.0, 5.0)).rotate(
            (0, 0, 0), (0, 0, 1), angle_deg
        )
        support_radius = support_x / (x / radius)
        support_y = y * support_radius / radius
        for dy in (-15.0, 15.0):
            plate = plate.cut(cylinder_between(
                (support_x, support_y + dy, 0.0),
                (support_x, support_y + dy, 10.0),
                4.25,
            ))
        parts.append(_component(
            f"NVR-P04_lower_spreader_{index}",
            plate,
            STEEL,
            "SS400 100x50x6 welded yoke base",
            group,
            "NVR-P04",
            notes="Underside mounted; two actuator-yoke lugs weld to its lower face",
        ))
        _vertical_fastener_up(parts, f"P04_{index}A", support_x, support_y - 15.0, 1.0, 14.0, group)
        _vertical_fastener_up(parts, f"P04_{index}B", support_x, support_y + 15.0, 1.0, 14.0, group)


def _lmf12uu(x, y, flange_bottom_z):
    """Common-standard LMF12UU envelope with four PCD32 mounting holes."""
    body = cq.Workplane("XY").circle(10.5).extrude(30).translate((x, y, flange_bottom_z - 30.0))
    flange = cq.Workplane("XY").circle(21.0).extrude(6.0).translate((x, y, flange_bottom_z))
    result = body.union(flange)
    result = result.cut(
        cq.Workplane("XY").circle(6.1).extrude(38.0).translate((x, y, flange_bottom_z - 31.0))
    )
    for dx, dy in ((16.0, 0.0), (-16.0, 0.0), (0.0, 16.0), (0.0, -16.0)):
        result = result.cut(cylinder_between(
            (x + dx, y + dy, flange_bottom_z - 1.0),
            (x + dx, y + dy, flange_bottom_z + 7.0),
            2.35,
        ))
        result = result.cut(cylinder_between(
            (x + dx, y + dy, flange_bottom_z + 1.8),
            (x + dx, y + dy, flange_bottom_z + 6.5),
            3.9,
        ))
    return result


def _add_fixed_guide(parts):
    group = "02_FIXED_GUIDE"
    for index, (x, shaft_y) in enumerate(N.guide_shaft_points_xy, start=1):
        outward = 1.0 if shaft_y > 0 else -1.0
        riser_y = shaft_y + outward * N.guide_riser_offset_from_shaft_mm
        riser_bottom = 54.0
        riser = centered_box(
            50.0,
            6.0,
            N.guide_riser_length_mm,
            (x, riser_y, riser_bottom + N.guide_riser_length_mm / 2.0),
        )
        parts.append(_component(
            f"NVR-P06_riser_{index}",
            riser,
            STEEL,
            "SS400 200x50x6",
            group,
            "NVR-P06",
            notes="Rev E side-offset riser; P09 tabs butt-weld to the inboard face",
        ))
        for foot_index, foot_y in enumerate((riser_y - 18.0, riser_y + 18.0), start=1):
            foot = centered_box(50.0, 30.0, 6.0, (x, foot_y, 51.0))
            foot = foot.cut(cylinder_between((x, shaft_y, 47.0), (x, shaft_y, 55.0), 6.6))
            for dx in (-15.0, 15.0):
                foot = foot.cut(cylinder_between((x + dx, foot_y, 47.0), (x + dx, foot_y, 55.0), 4.25))
            parts.append(_component(
                f"NVR-P17_riser_base_foot_{index}_{foot_index}",
                foot,
                STEEL,
                "SS400 50x30x6 welded foot",
                group,
                "NVR-P17",
                notes="Butt-weld to P06 after squaring on the lower-frame crossmember",
            ))
            _vertical_fastener(parts, f"RISER_{index}_{foot_index}A", x - 15.0, foot_y, 55.0, 8.0, group)
            _vertical_fastener(parts, f"RISER_{index}_{foot_index}B", x + 15.0, foot_y, 55.0, 8.0, group)
        for level, z in enumerate((N.fixed_bushing_lower_z_mm, N.fixed_bushing_upper_z_mm), start=1):
            tab_center_y = shaft_y + outward * 6.0
            tab = centered_box(50.0, 76.0, 6.0, (x, tab_center_y, z - 3.0))
            tab = tab.cut(cylinder_between((x, shaft_y, z - 7.0), (x, shaft_y, z + 7.0), 11.0))
            for dx, dy in ((16.0, 0.0), (-16.0, 0.0), (0.0, 16.0), (0.0, -16.0)):
                tab = tab.cut(cylinder_between((x + dx, shaft_y + dy, z - 7.0), (x + dx, shaft_y + dy, z + 1.0), 2.35))
            parts.append(_component(
                f"NVR-P09_LMF_tab_{index}_{level}",
                tab,
                STEEL,
                "SS400 50x76x6",
                group,
                "NVR-P09",
                "PROVISIONAL",
                "Common PCD32 four-hole pattern modeled; 76 mm tab reaches the offset riser; transfer-check against delivered LMF12UU",
            ))
            parts.append(_component(
                f"LMF12UU_{index}_{level}",
                _lmf12uu(x, shaft_y, z),
                PURCHASED,
                "LMF12UU linear bushing",
                group,
                "LMF12UU",
                "PROVISIONAL",
            ))
            for hole, (dx, dy) in enumerate(((16.0, 0.0), (-16.0, 0.0), (0.0, 16.0), (0.0, -16.0)), start=1):
                _vertical_counterbored_fastener(
                    parts,
                    f"LMF_{index}_{level}_{hole}",
                    x + dx,
                    shaft_y + dy,
                    z,
                    group,
                    status="PROVISIONAL",
                )
        for level, z in enumerate((126.0, 242.0), start=1):
            stop = centered_box(50.0, 18.0, 6.0, (x, shaft_y + outward * 32.0, z))
            parts.append(_component(
                f"NVR-P13_fixed_carriage_stop_{index}_{level}",
                stop,
                STOP,
                "SS400 50x18x6 welded Z stop",
                group,
                "NVR-P13",
                notes="Position from measured carriage envelope; 2 mm nominal overtravel beyond commanded stroke",
            ))


def _sk12_vertical(x, shaft_y, z, side):
    """Common SK12 envelope rotated 90 degrees for a vertical moving shaft."""
    profile_face_y = side * 20.0
    block_center_y = profile_face_y + side * 19.0
    block = centered_box(42.0, 38.0, 14.0, (x, block_center_y, z))
    block = block.cut(cylinder_between((x, shaft_y, z - 8.0), (x, shaft_y, z + 8.0), 6.1))
    for dx in (-16.0, 16.0):
        block = block.cut(cylinder_between(
            (x + dx, profile_face_y - side, z),
            (x + dx, profile_face_y + side * 39.0, z),
            2.75,
        ))
    return block


def _add_moving_guide(parts, platform_z):
    group = "03_MOVING_GUIDE"
    z = platform_z + N.carriage_center_offset_mm
    parts.append(_component(
        "NVR-G01_carriage",
        _tslot_x(N.carriage_length_mm, (0.0, 0.0, z)),
        ALUMINIUM,
        "6063-T5 4040 T-slot profile",
        group,
        "PROFILE_4040_240",
    ))
    for index, (x, shaft_y) in enumerate(N.guide_shaft_points_xy, start=1):
        side = 1.0 if shaft_y > 0 else -1.0
        parts.append(_component(
            f"SK12_{index}",
            _sk12_vertical(x, shaft_y, z, side),
            PURCHASED,
            "SK12 shaft support rotated for vertical shaft",
            group,
            "SK12",
            "PROVISIONAL",
            "Common SK12 42x38x14 envelope with 32 mm mounting-hole spacing; confirm delivered part",
        ))
        for hole, dx in enumerate((-16.0, 16.0), start=1):
            _side_tslot_fastener(
                parts,
                f"SK12_{index}_{hole}",
                x + dx,
                z,
                side,
                side * 20.0,
                group,
                size="M4",
                status="PROVISIONAL",
            )
        shaft_top_z = platform_z + N.guide_shaft_top_offset_mm
        shaft = cylinder_between(
            (x, shaft_y, shaft_top_z - N.guide_shaft_length_mm),
            (x, shaft_y, shaft_top_z),
            N.guide_shaft_diameter_mm / 2.0,
        )
        parts.append(_component(f"NVR-S01_shaft_{index}", shaft, WASHER, "SUJ2 ground shaft 12x230", group, "NVR-S01"))
        for stop_index, stop_z in enumerate((z - 23.0,), start=1):
            inner_pad = centered_box(50.0, 32.0, 6.0, (x, side * 16.0, stop_z))
            for dx in (-15.0, 15.0):
                inner_pad = inner_pad.cut(cylinder_between(
                    (x + dx, side * 8.0, stop_z - 4.0),
                    (x + dx, side * 8.0, stop_z + 4.0),
                    4.25,
                ))
            parts.append(_component(
                f"NVR-P13_moving_stop_pad_{index}_{stop_index}_inner",
                inner_pad,
                STOP,
                "SS400 50x32x6 moving Z-stop inner strip",
                group,
                "NVR-P13",
                notes="Bolted to carriage slot, then edge-welded to the outer strip after dry-run stop setting",
            ))
            outer_pad = centered_box(50.0, 40.0, 6.0, (x, side * 52.0, stop_z))
            outer_pad = outer_pad.cut(cylinder_between(
                (x, shaft_y, stop_z - 4.0),
                (x, shaft_y, stop_z + 4.0),
                6.6,
            ))
            parts.append(_component(
                f"NVR-P13_moving_stop_pad_{index}_{stop_index}_outer",
                outer_pad,
                STOP,
                "SS400 50x40x6 moving Z-stop outer strip",
                group,
                "NVR-P13",
                notes="Edge-weld to the inner strip; shaft clearance is transfer-checked after guide alignment",
            ))
            for hole, dx in enumerate((-15.0, 15.0), start=1):
                _vertical_fastener_up(
                    parts,
                    f"MOVING_STOP_{index}_{stop_index}_{hole}",
                    x + dx,
                    side * 8.0,
                    stop_z - 3.0,
                    6.0,
                    group,
                )


def _add_cardan(parts, pose, platform_z):
    group = "04_CARDAN"
    lower_axis_z = platform_z + N.cardan_lower_axis_offset_mm
    upper_axis_local_z = N.cardan_upper_axis_offset_mm
    yoke_offset = N.cardan_yoke_offset_mm

    lower_bridge_z = platform_z + N.cardan_lower_bridge_offset_mm
    lower_bridge = centered_box(100.0, 50.0, 6.0, (0.0, 0.0, lower_bridge_z))
    for x, y in ((-30.0, -14.0), (-30.0, 14.0), (30.0, -14.0), (30.0, 14.0)):
        lower_bridge = lower_bridge.cut(cylinder_between(
            (x, y, lower_bridge_z - 4.0), (x, y, lower_bridge_z + 4.0), 4.25
        ))
    parts.append(_component(
        "NVR-P08_lower_cardan_bridge",
        lower_bridge,
        STEEL,
        "SS400 100x50x6",
        group,
        "NVR-P08",
    ))
    for index, (x, y) in enumerate(((-30.0, -14.0), (-30.0, 14.0), (30.0, -14.0), (30.0, 14.0)), start=1):
        _vertical_fastener(parts, f"CARDAN_lower_{index}", x, y, lower_bridge_z + 4.0, 8.0, group)

    for index, y in enumerate((-yoke_offset, yoke_offset), start=1):
        lug = centered_box(50.0, 6.0, 22.0, (0.0, y, platform_z - 41.0))
        lug = lug.cut(cylinder_between(
            (0.0, y - 4.0, lower_axis_z),
            (0.0, y + 4.0, lower_axis_z),
            4.1,
        ))
        parts.append(_component(
            f"NVR-P07_lower_yoke_{index}",
            lug,
            STEEL,
            "SS400 50x22x6",
            group,
            "NVR-P07",
        ))

    cross_center_z = platform_z + (
        N.cardan_upper_axis_offset_mm + N.cardan_lower_axis_offset_mm
    ) / 2.0
    for index in range(4):
        z = cross_center_z - N.cardan_cross_height_mm / 2.0 + 3.0 + index * 6.0
        plate = centered_box(N.cardan_cross_size_mm, N.cardan_cross_size_mm, 6.0, (0.0, 0.0, z))
        plate = plate.cut(cylinder_between(
            (-31.0, 0.0, platform_z + N.cardan_upper_axis_offset_mm),
            (31.0, 0.0, platform_z + N.cardan_upper_axis_offset_mm),
            4.1,
        ))
        plate = plate.cut(cylinder_between(
            (0.0, -31.0, platform_z + N.cardan_lower_axis_offset_mm),
            (0.0, 31.0, platform_z + N.cardan_lower_axis_offset_mm),
            4.1,
        ))
        plate = plate.rotate(
            (0.0, 0.0, lower_axis_z),
            (0.0, 1.0, lower_axis_z),
            pose.pitch_deg,
        )
        parts.append(_component(
            f"NVR-P14_cross_laminate_{index+1}",
            plate,
            PURCHASED,
            "SS400 50x50x6 perimeter-welded and line-drilled",
            group,
            "NVR-P14",
            notes="Four plates form a 24 mm block; weld first, then line-drill both offset pivot bores",
        ))

    lower_axis = (0.0, 1.0, 0.0)
    _axis_fastener(
        parts,
        "CARDAN_Y",
        (0.0, 0.0, lower_axis_z),
        lower_axis,
        70.0,
        group,
        status="PROVISIONAL",
    )

    upper_start = len(parts)
    for index, x in enumerate((-yoke_offset, yoke_offset), start=1):
        lug = centered_box(6.0, 50.0, 24.0, (x, 0.0, -38.0))
        lug = lug.cut(cylinder_between(
            (x - 4.0, 0.0, upper_axis_local_z),
            (x + 4.0, 0.0, upper_axis_local_z),
            4.1,
        ))
        parts.append(_component(
            f"NVR-P07_upper_yoke_{index}",
            lug,
            STEEL,
            "SS400 50x24x6",
            group,
            "NVR-P07",
        ))
    for segment, y in enumerate((-50.0, 0.0, 50.0), start=1):
        bridge = centered_box(100.0, 50.0, 6.0, (0.0, y, N.cardan_upper_bridge_offset_mm))
        parts.append(_component(
            f"NVR-P08_upper_cardan_bridge_{segment}",
            bridge,
            STEEL,
            "SS400 100x50x6 welded bridge segment",
            group,
            "NVR-P08",
            notes="Three edge-welded strips form the 100x150 upper bridge",
        ))
    for index, (x, y) in enumerate(((-30.0, -50.0), (30.0, -50.0), (-30.0, 50.0), (30.0, 50.0)), start=1):
        _vertical_fastener_up(
            parts,
            f"CARDAN_upper_{index}",
            x,
            y,
            N.cardan_upper_bridge_offset_mm - 3.0,
            6.0,
            group,
        )
    for item_index in range(upper_start, len(parts)):
        parts[item_index] = replace(
            parts[item_index],
            shape=_upper_local_shape(parts[item_index].shape, pose, platform_z),
        )

    upper_center = transform_local_point(
        (0.0, 0.0, N.cardan_upper_axis_offset_mm), pose, platform_z
    )
    upper_axis = _upper_local_vector((1.0, 0.0, 0.0), pose)
    _axis_fastener(
        parts,
        "CARDAN_X",
        upper_center,
        upper_axis.toTuple(),
        70.0,
        group,
        status="PROVISIONAL",
    )

    for index, (x, y) in enumerate(((-42.0, -62.0), (-42.0, 62.0), (42.0, -62.0), (42.0, 62.0)), start=1):
        stop = centered_box(18.0, 18.0, 24.0, (x, y, N.cardan_upper_bridge_offset_mm - 15.0))
        stop = _upper_local_shape(stop, pose, platform_z)
        parts.append(_component(
            f"CARDAN_angle_stop_{index}",
            stop,
            STOP,
            "M8 adjustable stop block welded under upper bridge",
            group,
            "CARDAN_ANGLE_STOP",
            "PROVISIONAL",
            "Set beyond +/-3 degree command range during dry assembly",
        ))


def _add_upper_frame(parts, pose, platform_z):
    group = "05_UPPER_FRAME"
    start_index = len(parts)
    _add_frame(parts, "UPR", 0.0, N.upper_long_length_mm, N.upper_end_length_mm, (-200.0, 200.0), group, upper=True)
    for index, (x, y) in enumerate(N.upper_points_xy, start=1):
        support_x = 400.0 if index == 1 else -200.0
        plate = centered_box(100, 50, 6, (x, y, -23.0))
        for dy in (-15.0, 15.0):
            plate = plate.cut(cylinder_between(
                (support_x, y + dy, -28.0),
                (support_x, y + dy, -18.0),
                4.25,
            ))
        parts.append(_component(
            f"NVR-P03_upper_spreader_{index}",
            plate,
            STEEL,
            "SS400 100x50x6 welded yoke base",
            group,
            "NVR-P03",
            notes="Underside mounted; two actuator-yoke lugs weld to its lower face",
        ))
        _vertical_fastener_up(parts, f"P03_{index}A", support_x, y - 15.0, -27.0, 14.0, group)
        _vertical_fastener_up(parts, f"P03_{index}B", support_x, y + 15.0, -27.0, 14.0, group)
    for item_index in range(start_index, len(parts)):
        parts[item_index] = replace(
            parts[item_index],
            shape=_upper_local_shape(parts[item_index].shape, pose, platform_z),
        )


def _upper_local_shape(shape, pose, platform_z):
    result = shape.rotate(
        (0.0, 0.0, N.cardan_upper_axis_offset_mm),
        (1.0, 0.0, N.cardan_upper_axis_offset_mm),
        pose.roll_deg,
    )
    result = result.rotate(
        (0.0, 0.0, N.cardan_lower_axis_offset_mm),
        (0.0, 1.0, N.cardan_lower_axis_offset_mm),
        pose.pitch_deg,
    )
    return result.translate((0.0, 0.0, platform_z))


def _upper_local_vector(vector, pose):
    x, y, z = vector
    cr, sr = cos(radians(pose.roll_deg)), sin(radians(pose.roll_deg))
    cp, sp = cos(radians(pose.pitch_deg)), sin(radians(pose.pitch_deg))
    y1, z1 = y * cr - z * sr, y * sr + z * cr
    return cq.Vector(x * cp + z1 * sp, y1, -x * sp + z1 * cp).normalized()


def _yoke_lug(radius, pin_z, angle_deg, side, root_sign):
    gap = N.actuator_yoke_inner_gap_mm
    thickness = N.actuator_yoke_lug_thickness_mm
    lug_y = side * (gap / 2.0 + thickness / 2.0)
    root_face_z = pin_z + N.actuator_yoke_pin_drop_mm - 3.0
    bottom_z = pin_z - 14.0
    lug_height = root_face_z - bottom_z
    lug = centered_box(
        50.0,
        thickness,
        lug_height,
        (radius + root_sign * 10.0, lug_y, (root_face_z + bottom_z) / 2.0),
    )
    bore = cylinder_between(
        (radius, lug_y - thickness / 2.0 - 1.0, pin_z),
        (radius, lug_y + thickness / 2.0 + 1.0, pin_z),
        N.actuator_yoke_pin_hole_mm / 2.0,
    )
    return lug.cut(bore).rotate((0, 0, 0), (0, 0, 1), angle_deg)


def _ring_between_axis(center, axis, width, outer_radius, inner_radius):
    center_v = cq.Vector(*center) if not isinstance(center, cq.Vector) else center
    axis_v = cq.Vector(*axis) if not isinstance(axis, cq.Vector) else axis
    axis_v = axis_v.normalized()
    half = axis_v.multiply(width / 2.0)
    return cylinder_between(center_v - half, center_v + half, outer_radius).cut(
        cylinder_between(center_v - half.multiply(1.2), center_v + half.multiply(1.2), inner_radius)
    )


def _jft8_rod_end(center, pin_axis, body_axis):
    center_v = cq.Vector(*center) if not isinstance(center, cq.Vector) else center
    pin_axis_v = cq.Vector(*pin_axis) if not isinstance(pin_axis, cq.Vector) else pin_axis
    body_axis_v = cq.Vector(*body_axis) if not isinstance(body_axis, cq.Vector) else body_axis
    pin_axis_v = pin_axis_v.normalized()
    body_axis_v = body_axis_v.normalized()

    housing = _ring_between_axis(
        center_v,
        pin_axis_v,
        N.rod_end_housing_width_mm,
        N.rod_end_outer_diameter_mm / 2.0,
        6.2,
    )
    ball = _ring_between_axis(
        center_v,
        pin_axis_v,
        N.rod_end_ball_width_mm,
        6.0,
        N.rod_end_bore_mm / 2.0 + 0.1,
    )
    neck_start = center_v + body_axis_v.multiply(8.0)
    neck_end = center_v + body_axis_v.multiply(N.rod_end_center_to_end_mm)
    thread_start = neck_end - body_axis_v.multiply(N.rod_end_thread_depth_mm)
    thread_end = neck_end + body_axis_v.multiply(1.0)
    thread_bore = cylinder_between(thread_start, thread_end, 4.1)
    neck = cylinder_between(neck_start, neck_end, 6.5).cut(thread_bore)
    collar = cylinder_between(
        center_v + body_axis_v.multiply(26.0),
        neck_end,
        8.0,
    ).cut(thread_bore)
    return compound([housing, ball, neck, collar])


def _joint_spacers(center, pin_axis):
    center_v = cq.Vector(*center) if not isinstance(center, cq.Vector) else center
    axis_v = cq.Vector(*pin_axis) if not isinstance(pin_axis, cq.Vector) else pin_axis
    axis_v = axis_v.normalized()
    gap_half = N.actuator_yoke_inner_gap_mm / 2.0
    ball_half = N.rod_end_ball_width_mm / 2.0
    shapes = []
    for start, end in ((-gap_half, -ball_half), (ball_half, gap_half)):
        shapes.append(cylinder_between(
            center_v + axis_v.multiply(start),
            center_v + axis_v.multiply(end),
            6.0,
        ).cut(cylinder_between(
            center_v + axis_v.multiply(start - 0.5),
            center_v + axis_v.multiply(end + 0.5),
            N.actuator_yoke_pin_hole_mm / 2.0,
        )))
    return compound(shapes)


def _m8_interface_stud(center, body_axis):
    center_v = cq.Vector(*center) if not isinstance(center, cq.Vector) else center
    axis_v = cq.Vector(*body_axis) if not isinstance(body_axis, cq.Vector) else body_axis
    axis_v = axis_v.normalized()
    start = center_v + axis_v.multiply(
        N.rod_end_center_to_end_mm - N.rod_end_thread_depth_mm
    )
    end = center_v + axis_v.multiply(42.0)
    stud = cylinder_between(start, end, 3.8)
    locknut = cylinder_between(
        center_v + axis_v.multiply(36.0),
        center_v + axis_v.multiply(41.0),
        7.4,
    ).cut(cylinder_between(
        center_v + axis_v.multiply(35.0),
        center_v + axis_v.multiply(42.0),
        4.1,
    ))
    return compound([stud, locknut])


def _actuator_body(base, top, tangent):
    base_v, top_v = cq.Vector(*base), cq.Vector(*top)
    direction = top_v - base_v
    length = direction.Length
    unit = direction.normalized()
    tangent_v = cq.Vector(*tangent) if not isinstance(tangent, cq.Vector) else tangent
    tangent_v = tangent_v.normalized()
    side = tangent_v.cross(unit).normalized()

    body_start = base_v + unit.multiply(42.0)
    body_end = base_v + unit.multiply(min(172.0, length - 80.0))
    rod_start = body_end - unit.multiply(22.0)
    rod_end = top_v - unit.multiply(42.0)
    body = cylinder_between(body_start, body_end, 22.5)
    rod = cylinder_between(rod_start, rod_end, 9.0)

    gearbox_center = base_v + unit.multiply(72.0) + side.multiply(20.0)
    gearbox = cq.Workplane(cq.Plane(
        origin=gearbox_center,
        xDir=unit,
        normal=tangent_v,
    )).box(55.0, 44.0, 42.0)
    motor_center = base_v + unit.multiply(78.0) + side.multiply(46.0)
    motor = cylinder_between(
        motor_center - tangent_v.multiply(42.0),
        motor_center + tangent_v.multiply(28.0),
        27.0,
    )
    return compound([body, rod, gearbox, motor])


def _add_actuators(parts, pose, platform_z):
    group = "06_ACTUATORS"
    for index, ((ux, uy), (lx, ly)) in enumerate(zip(N.upper_points_xy, N.lower_points_xy), start=1):
        top = transform_local_point(
            (ux, uy, N.upper_joint_offset_mm), pose, platform_z
        )
        base = (lx, ly, N.base_joint_z_mm)
        base_v, top_v = cq.Vector(*base), cq.Vector(*top)
        actuator_axis = (top_v - base_v).normalized()

        radial = (lx * lx + ly * ly) ** 0.5
        angle_deg = degrees(__import__("math").atan2(ly, lx))
        lower_tangent = cq.Vector(-ly / radial, lx / radial, 0.0)
        upper_radius = (ux * ux + uy * uy) ** 0.5
        upper_tangent_local = (-uy / upper_radius, ux / upper_radius, 0.0)
        upper_tangent = _upper_local_vector(upper_tangent_local, pose)

        parts.append(_component(
            f"LA2000_A2_PROVISIONAL_{index}",
            _actuator_body(base, top, lower_tangent),
            PROVISIONAL,
            "DIHOOL LA2000-125150 A2 conservative envelope",
            group,
            "LA2000_125150",
            "PROVISIONAL",
            "Replace with supplier STEP; pin-centre and motor/cable envelope remain vendor confirmation items",
        ))

        for end_name, center, pin_axis, body_axis in (
            ("LOWER", base_v, lower_tangent, actuator_axis),
            ("UPPER", top_v, upper_tangent, actuator_axis.multiply(-1.0)),
        ):
            parts.append(_component(
                f"ACT{index}_{end_name}_JFT8R",
                _jft8_rod_end(center, pin_axis, body_axis),
                PURCHASED,
                "JMC JFT-8R M8 female spherical rod end",
                group,
                "JFT8R",
                "CATALOG_VERIFIED",
                "NAVIMRO K02020097; 8 bore, 24 OD, 9/12 width, 36 center-to-end, 13 degree articulation",
            ))
            parts.append(_component(
                f"ACT{index}_{end_name}_M8_A2_ADAPTER_PROVISIONAL",
                _m8_interface_stud(center, body_axis),
                PROVISIONAL,
                "M8x1.25 threaded interface and jam-nut envelope",
                group,
                "A2_M8_INTERFACE",
                "PROVISIONAL",
                "Confirm whether delivered A2 end is male or female and set full thread engagement with no exposed bending standoff",
            ))
            parts.append(_component(
                f"ACT{index}_{end_name}_spacer_pair",
                _joint_spacers(center, pin_axis),
                WASHER,
                "4 mm misalignment spacer pair",
                group,
                "JFT8_SPACER_PAIR",
                "PROVISIONAL",
                "Turn or select after measuring the delivered rod-end ball width",
            ))
            _axis_fastener(
                parts,
                f"ACT{index}_{end_name}",
                center.toTuple(),
                pin_axis.toTuple(),
                36.0,
                group,
                size="M8",
                status="PROVISIONAL",
            )

        for side in (-1, 1):
            lower_lug = _yoke_lug(
                radial,
                N.base_joint_z_mm,
                angle_deg,
                side,
                root_sign=-1.0,
            )
            parts.append(_component(
                f"ACT{index}_LOWER_yoke_lug_{'A' if side < 0 else 'B'}",
                lower_lug,
                STEEL,
                "SS400 50x6 welded lug with 8.2 mm bore",
                group,
                "NVR-P16",
                notes="Weld to NVR-P04 underside using a simple pin-alignment jig",
            ))

            upper_lug_local = _yoke_lug(
                upper_radius,
                N.upper_joint_offset_mm,
                degrees(__import__("math").atan2(uy, ux)),
                side,
                root_sign=1.0,
            )
            upper_lug = _upper_local_shape(upper_lug_local, pose, platform_z)
            parts.append(_component(
                f"ACT{index}_UPPER_yoke_lug_{'A' if side < 0 else 'B'}",
                upper_lug,
                STEEL,
                "SS400 50x6 welded lug with 8.2 mm bore",
                group,
                "NVR-P16",
                notes="Weld to NVR-P03 underside using a simple pin-alignment jig",
            ))


def _add_deck(parts, pose, platform_z):
    group = "07_DECK"
    start_index = len(parts)
    deck_z = 27.5
    holes = set()
    for x in (-400, -200, 0, 200, 400):
        holes.add((x, -350)); holes.add((x, 350))
    for y in (-175, 0, 175):
        holes.add((-400, y)); holes.add((400, y))
    deck = centered_box(N.platform_length_mm, N.platform_width_mm, N.acrylic_thickness_mm, (0, 0, deck_z))
    for x, y in holes:
        deck = deck.cut(cylinder_between((x, y, 18.0), (x, y, 37.0), 9.1))
    parts.append(_component("NVR-U02_acrylic_deck", deck, ACRYLIC, "clear PMMA 900x800x15", group, "NVR-U02"))
    for index, (x, y) in enumerate(sorted(holes), start=1):
        spacer = cq.Workplane("XY").circle(9).extrude(15).translate((x, y, 20))
        spacer = spacer.cut(cq.Workplane("XY").circle(4.3).extrude(17).translate((x, y, 19)))
        parts.append(_component(
            f"DECK_spacer_{index:02d}",
            spacer,
            WASHER,
            "aluminium compression sleeve ID8.6 OD18 L15",
            group,
            "DECK_SPACER",
            "PROVISIONAL",
            "Machine from tube or select exact NAVIMRO spacer after deck receipt",
        ))
        _vertical_fastener(parts, f"DECK_{index:02d}", x, y, 36, 26, group)
    for item_index in range(start_index, len(parts)):
        parts[item_index] = replace(
            parts[item_index],
            shape=_upper_local_shape(parts[item_index].shape, pose, platform_z),
        )


def _add_cart_coupling(parts, pose, platform_z):
    group = "08_CART_COUPLING"
    start_index = len(parts)
    for index, y in enumerate((-N.cart_rail_y_mm, N.cart_rail_y_mm), start=1):
        parts.append(_component(f"NVR-C01_receiver_rail_{index}", _tslot_x(N.cart_receiver_length_mm, (0, y, 55)), ALUMINIUM, "6063-T5 4040 T-slot profile", group, "PROFILE_4040_760"))
    locator_z = 55
    for index, (x, radius, name) in enumerate(((-N.locator_x_mm, 10, "master"), (N.locator_x_mm, 9, "secondary")), start=1):
        locator_plate = centered_box(120, 50, 6, (x, 0, locator_z - 3))
        locator_plate = locator_plate.cut(cylinder_between((x, 0, locator_z - 7), (x, 0, locator_z + 1), 4.3))
        parts.append(_component(f"NVR-P10_{name}_locator_plate", locator_plate, STEEL, "SS400 120x50x6", group, "NVR-P10", "PROVISIONAL"))
        pin = cq.Workplane("XY").circle(radius).extrude(25).translate((x, 0, locator_z))
        pin = pin.cut(cylinder_between((x, 0, locator_z - 1), (x, 0, locator_z + 27), 4.3))
        parts.append(_component(f"NVR-C02_{name}_locator_PROVISIONAL", pin, PROVISIONAL, "turned steel locator pin", group, f"LOCATOR_{name.upper()}", "PROVISIONAL"))
        _vertical_fastener(parts, f"LOCATOR_{index}", x, 0, locator_z + 30, 35, group, end="nyloc", status="PROVISIONAL")
    for index, (x, y) in enumerate(((x, y) for x in (-N.latch_x_mm, N.latch_x_mm) for y in (-N.latch_y_mm, N.latch_y_mm)), start=1):
        spreader = centered_box(100, 50, 6, (x, y, 18))
        latch = centered_box(85, 34, 44, (x, y, 38))
        keeper = centered_box(70, 20, 6, (x, y - (22 if y > 0 else -22), 60))
        for dx in (-25.0, 25.0):
            spreader = spreader.cut(cylinder_between((x + dx, y, 14.0), (x + dx, y, 22.0), 3.25))
            latch = latch.cut(cylinder_between((x + dx, y, 14.0), (x + dx, y, 66.0), 3.25))
        parts.append(_component(f"NVR-P11_latch_spreader_{index}", spreader, STEEL, "SS400 100x50x6", group, "NVR-P11", "PROVISIONAL"))
        parts.append(_component(f"CR3001_latch_{index}_PROVISIONAL", latch, PROVISIONAL, "CR-3001 latch", group, "CR3001", "PROVISIONAL"))
        parts.append(_component(f"NVR-P12_CR3001_keeper_{index}_PROVISIONAL", keeper, PROVISIONAL, "SS400 keeper fitted to CR-3001", group, "NVR-P12", "PROVISIONAL"))
        for hole, dx in enumerate((-25, 25), start=1):
            _vertical_fastener(parts, f"LATCH_{index}_{hole}", x + dx, y, 64, 24, group, size="M6", end="tnut", status="PROVISIONAL")
    for item_index in range(start_index, len(parts)):
        original = parts[item_index]
        parts[item_index] = replace(
            original,
            shape=original.shape.translate((0.0, 0.0, -170.0)),
            status="PROVISIONAL",
            notes=(original.notes + "; " if original.notes else "")
            + "Rev E cart-side reference is shown separated below the module; do not fabricate before cart dimensions are frozen",
        )


def detailed_components(pose_name="neutral"):
    pose = NAVIMRO_POSES[pose_name] if isinstance(pose_name, str) else pose_name
    platform_z = N.collapsed_joint_z_mm + pose.lift_mm
    parts = []
    _add_lower_frame(parts)
    _add_fixed_guide(parts)
    _add_moving_guide(parts, platform_z)
    _add_cardan(parts, pose, platform_z)
    _add_upper_frame(parts, pose, platform_z)
    _add_actuators(parts, pose, platform_z)
    _add_deck(parts, pose, platform_z)
    _add_cart_coupling(parts, pose, platform_z)
    return parts


GROUP_OFFSETS = {
    "01_LOWER_FRAME": 0.0,
    "02_FIXED_GUIDE": 70.0,
    "03_MOVING_GUIDE": 150.0,
    "04_CARDAN": 230.0,
    "05_UPPER_FRAME": 350.0,
    "06_ACTUATORS": 190.0,
    "07_DECK": 480.0,
    "08_CART_COUPLING": 0.0,
}


def as_hierarchical_assembly(pose_name="neutral", exploded=False):
    root = cq.Assembly(name=f"NAVIMRO_DETAILED_{pose_name.upper()}")
    components = detailed_components(pose_name)
    for group in GROUP_OFFSETS:
        sub = cq.Assembly(name=group)
        for part in (item for item in components if item.group == group):
            shape = part.shape.translate((0, 0, GROUP_OFFSETS[group])) if exploded else part.shape
            r, g, b, a = part.color
            sub.add(shape, name=part.name, color=cq.Color(r, g, b, a))
        root.add(sub, name=group)
    return root


def export_fusion_steps(output_dir, revision="D"):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for pose_name in NAVIMRO_POSES:
        path = output_dir / f"NAVIMRO_detailed_{pose_name}_rev{revision}.step"
        as_hierarchical_assembly(pose_name).save(str(path), exportType="STEP", mode="default")
        outputs.append(path)
    exploded = output_dir / f"NAVIMRO_detailed_exploded_rev{revision}.step"
    as_hierarchical_assembly("neutral", exploded=True).save(str(exploded), exportType="STEP", mode="default")
    outputs.append(exploded)
    module_only = cq.Assembly(name="NAVIMRO_MODULE_ONLY_COLLAPSED")
    collapsed_parts = detailed_components("collapsed")
    for group in GROUP_OFFSETS:
        if group == "08_CART_COUPLING":
            continue
        sub = cq.Assembly(name=group)
        for part in (item for item in collapsed_parts if item.group == group):
            r, g, b, a = part.color
            sub.add(part.shape, name=part.name, color=cq.Color(r, g, b, a))
        module_only.add(sub, name=group)
    module_only_path = output_dir / f"NAVIMRO_module_only_collapsed_rev{revision}.step"
    module_only.save(str(module_only_path), exportType="STEP", mode="default")
    outputs.append(module_only_path)
    neutral_parts = detailed_components("neutral")
    for group in GROUP_OFFSETS:
        assembly = cq.Assembly(name=group)
        for part in (item for item in neutral_parts if item.group == group):
            r, g, b, a = part.color
            assembly.add(part.shape, name=part.name, color=cq.Color(r, g, b, a))
        path = output_dir / f"SUB_{group}_rev{revision}.step"
        assembly.save(str(path), exportType="STEP", mode="default")
        outputs.append(path)

    cassette_names = {
        "LWR_actuator_cross",
        "NVR-P04_lower_spreader_1",
        "UPR_end_front",
        "NVR-P03_upper_spreader_1",
    }
    cassette = cq.Assembly(name="ACT1_COMPLETE_MOUNTING_CASSETTE")
    for part in neutral_parts:
        if part.name in cassette_names or part.name.startswith("ACT1_") or part.name == "LA2000_A2_PROVISIONAL_1":
            r, g, b, a = part.color
            cassette.add(part.shape, name=part.name, color=cq.Color(r, g, b, a))
    cassette_path = output_dir / f"ACT1_complete_mounting_cassette_neutral_rev{revision}.step"
    cassette.save(str(cassette_path), exportType="STEP", mode="default")
    outputs.append(cassette_path)
    return outputs
