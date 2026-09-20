"""CadQuery model for the simplified manual 3-RPS Rev M2 candidate."""

from __future__ import annotations

from dataclasses import dataclass
from math import degrees, sqrt

import cadquery as cq

from calculations import manual_turnbuckle_rev_m2_screen as data


P = data.P


@dataclass(frozen=True)
class Component:
    name: str
    group: str
    shape: cq.Shape
    color: tuple[float, float, float]
    material: str


COLORS = {
    "profile": (0.72, 0.75, 0.78),
    "plate": (0.20, 0.48, 0.66),
    "support": (0.12, 0.14, 0.16),
    "link": (0.16, 0.18, 0.20),
    "rod_end": (0.76, 0.48, 0.14),
    "fastener": (0.34, 0.37, 0.40),
    "spacer": (0.72, 0.45, 0.17),
}


def _box(length, width, height, center):
    return cq.Workplane("XY").box(length, width, height).translate(center).val()


def _cylinder_between(start, end, radius):
    start = cq.Vector(*start) if not isinstance(start, cq.Vector) else start
    end = cq.Vector(*end) if not isinstance(end, cq.Vector) else end
    direction = end - start
    if direction.Length <= 1e-9:
        raise ValueError("Cylinder endpoints coincide")
    shape = cq.Workplane("XY").circle(radius).extrude(direction.Length).val()
    z_axis = cq.Vector(0.0, 0.0, 1.0)
    unit = direction.normalized()
    axis = z_axis.cross(unit)
    dot = max(-1.0, min(1.0, z_axis.dot(unit)))
    angle = degrees(__import__("math").acos(dot))
    if axis.Length > 1e-9 and abs(angle) > 1e-9:
        shape = shape.rotate((0, 0, 0), axis.toTuple(), angle)
    elif dot < 0:
        shape = shape.rotate((0, 0, 0), (1, 0, 0), 180.0)
    return shape.translate(start.toTuple())


def _ring(center, axis, outer_diameter, inner_diameter, width, x_dir):
    plane = cq.Plane(origin=center, xDir=x_dir, normal=axis)
    return (
        cq.Workplane(plane)
        .circle(outer_diameter / 2.0)
        .circle(inner_diameter / 2.0)
        .extrude(width / 2.0, both=True)
        .val()
    )


def _hex_prism_between(start, end, across_corners):
    start_v = cq.Vector(*start) if not isinstance(start, cq.Vector) else start
    end_v = cq.Vector(*end) if not isinstance(end, cq.Vector) else end
    axis = (end_v - start_v).normalized()
    helper = cq.Vector(0, 0, 1)
    if abs(axis.dot(helper)) > 0.95:
        helper = cq.Vector(1, 0, 0)
    x_dir = helper.cross(axis).normalized()
    plane = cq.Plane(origin=start_v.toTuple(), xDir=x_dir.toTuple(), normal=axis.toTuple())
    return (
        cq.Workplane(plane)
        .polygon(6, across_corners)
        .extrude((end_v - start_v).Length)
        .val()
    )


def _point(start, unit, distance):
    return cq.Vector(*start) + unit.multiply(distance)


def _transform_shape(shape, pitch_deg, roll_deg, yaw_rad, translation):
    transformed = shape.rotate((0, 0, 0), (1, 0, 0), roll_deg)
    transformed = transformed.rotate((0, 0, 0), (0, 1, 0), pitch_deg)
    transformed = transformed.rotate((0, 0, 0), (0, 0, 1), degrees(yaw_rad))
    return transformed.translate(translation)


def _transform_vector(vector, rotation):
    return cq.Vector(*data._matvec(rotation, vector))


def _profile_frames():
    lower = []
    for name, x in (("LOWER_SIDE_L", -330.0), ("LOWER_SIDE_R", 330.0)):
        lower.append(Component(name, "lower_frame", _box(40, 700, 40, (x, 0, 20)), COLORS["profile"], "DNF4040"))
    lower_holes = {75.0: [0.0], -37.5: [-64.951905, 64.951905]}
    for index, y in enumerate(data.LOWER_CROSSBAR_Y_MM):
        shape = _box(620, 40, 40, (0, y, 20))
        for x in lower_holes.get(y, []):
            shape = shape.cut(_cylinder_between((x, y, -1), (x, y, 41), 6.75))
        lower.append(Component(f"LOWER_CROSS_{index + 1}", "lower_frame", shape, COLORS["profile"], "DNF4040"))

    upper_local = []
    frame_center_local_z = 285.0 - P.upper_pin_z_mm
    for name, x in (("UPPER_SIDE_L", -335.0), ("UPPER_SIDE_R", 335.0)):
        upper_local.append(Component(name, "upper_frame", _box(30, 700, 30, (x, 0, frame_center_local_z)), COLORS["profile"], "DNF3030"))
    upper_points = data.support_points(P.upper_support_radius_mm)
    upper_holes = {315.0: [upper_points[0][0]], -157.5: [upper_points[1][0], upper_points[2][0]]}
    for index, y in enumerate(data.UPPER_CROSSBAR_Y_MM):
        shape = _box(640, 30, 30, (0, y, frame_center_local_z))
        for x in upper_holes.get(y, []):
            shape = shape.cut(_cylinder_between((x, y, frame_center_local_z - 16), (x, y, frame_center_local_z + 16), 10.75))
        upper_local.append(Component(f"UPPER_CROSS_{index + 1}", "upper_frame", shape, COLORS["profile"], "DNF3030"))
    lower.extend(_frame_brackets(data.LOWER_CROSSBAR_Y_MM, 310.0, 40.0, 40.0, 6.0, 35.0, 20.0, "L4035"))
    upper_local.extend(_frame_brackets(data.UPPER_CROSSBAR_Y_MM, 320.0, 30.0, 30.0, 5.0, 25.0, frame_center_local_z, "UDCB3025"))
    return lower, upper_local


def _frame_brackets(crossbar_y_values, inner_x, section, leg, thickness, height, z_center, prefix):
    components = []
    for row_index, y in enumerate(crossbar_y_values, start=1):
        if y >= 200.0:
            sy = -1.0
        elif y <= -200.0:
            sy = 1.0
        elif y > 0.0:
            sy = 1.0
        else:
            sy = -1.0
        surface_y = y + sy * section / 2.0
        for side_name, x, sx in (("L", -inner_x, 1.0), ("R", inner_x, -1.0)):
            first = _box(leg, thickness, height, (x + sx * leg / 2.0, surface_y + sy * thickness / 2.0, z_center))
            second = _box(thickness, leg, height, (x + sx * thickness / 2.0, surface_y + sy * leg / 2.0, z_center))
            bracket = first.fuse(second)
            components.append(Component(f"{prefix}_{row_index}_{side_name}", "frame_brackets", bracket, COLORS["fastener"], "standard profile inside bracket"))
    return components


def _plate(center, central_diameter):
    x, y, z = center
    shape = _box(P.adapter_length_mm, P.adapter_width_mm, P.adapter_thickness_mm, center)
    for hole_x in (-P.adapter_hole_pitch_mm / 2.0, P.adapter_hole_pitch_mm / 2.0):
        shape = shape.cut(_cylinder_between((x + hole_x, y, z - 4), (x + hole_x, y, z + 4), 4.5))
    shape = shape.cut(_cylinder_between((x, y, z - 4), (x, y, z + 4), central_diameter / 2.0))
    return shape


def _tube_spacer(center, length):
    x, y, z = center
    outer = _cylinder_between((x, y, z - length / 2), (x, y, z + length / 2), 8.0)
    inner = _cylinder_between((x, y, z - length / 2 - 1), (x, y, z + length / 2 + 1), 4.25)
    return outer.cut(inner)


def _vertical_hollow_hex(center, height, across_corners, hole_diameter):
    x, y, z = center
    outer = cq.Workplane("XY").polygon(6, across_corners).extrude(height).translate((x, y, z - height / 2)).val()
    hole = _cylinder_between((x, y, z - height), (x, y, z + height), hole_diameter / 2.0)
    return outer.cut(hole)


def _bj762_support(origin_xy, mount_z, angle_deg, size, inverted=False):
    if size == 12:
        pin_d, gap, stud_d, stud_l, body_d, h1, h, ear = 12.0, 14.2, 12.0, 30.0, 30.0, 34.0, 21.0, 7.4
    elif size == 20:
        pin_d, gap, stud_d, stud_l, body_d, h1, h, ear = 12.2, 22.2, 20.0, 50.0, 50.0, 52.0, 32.0, 11.0
    else:
        raise ValueError(size)
    direction = -1.0 if inverted else 1.0
    x, y = origin_xy
    parts = []
    total = gap + 2.0 * ear
    for side in (-1.0, 1.0):
        y_offset = side * (gap / 2.0 + ear / 2.0)
        center_z = mount_z + direction * h1 / 2.0
        ear_shape = _box(body_d, ear, h1, (x, y + y_offset, center_z))
        hole = _cylinder_between(
            (x, y - total, mount_z + direction * h),
            (x, y + total, mount_z + direction * h),
            pin_d / 2.0,
        )
        parts.append(ear_shape.cut(hole))
    bridge_center_z = mount_z + direction * 4.0
    parts.append(_box(body_d, total, 8.0, (x, y, bridge_center_z)))
    parts.append(
        _cylinder_between(
            (x, y, mount_z),
            (x, y, mount_z - direction * stud_l),
            stud_d / 2.0,
        )
    )
    shape = cq.Compound.makeCompound(parts)
    return shape.rotate((x, y, mount_z), (x, y, mount_z + 1), angle_deg)


def _adapter_components():
    lower = []
    upper_local = []
    for index, ((lx, ly), (ux, uy), (radial, _)) in enumerate(
        zip(
            data.support_points(P.lower_support_radius_mm),
            data.support_points(P.upper_support_radius_mm),
            data.support_basis(),
        ),
        start=1,
    ):
        angle = data.SUPPORT_ANGLES_DEG[index - 1]
        lower.append(Component(f"L{index}_ADAPTER", "lower_adapters", _plate((lx, ly, 57.5), 13.5), COLORS["plate"], "A6061-T6 5t"))
        for side in (-1.0, 1.0):
            lower.append(Component(f"L{index}_SPACER_{side:+.0f}", "lower_adapters", _tube_spacer((lx + side * 35.0, ly, 47.5), 15.0), COLORS["spacer"], "A6061 OD16 ID8.5 L15"))
            lower.append(Component(f"L{index}_M8_BOLT_{side:+.0f}", "adapter_fasteners", _cylinder_between((lx + side * 35.0, ly, 40.0), (lx + side * 35.0, ly, 64.0), 3.9), COLORS["fastener"], "M8x35 socket bolt + T-nut"))
        lower.append(Component(f"L{index}_BJ762_12001", "lower_supports", _bj762_support((lx, ly), 60.0, angle, 12, False), COLORS["support"], "SCM435"))
        lower.append(Component(f"L{index}_M12_NUT", "fasteners", _vertical_hollow_hex((lx, ly, 50.0), 10.0, 21.0, 12.3), COLORS["fastener"], "M12 nut"))

        upper_plate_center_z = 247.5 - P.upper_pin_z_mm
        upper_spacer_center_z = 260.0 - P.upper_pin_z_mm
        upper_mount_z = 245.0 - P.upper_pin_z_mm
        upper_local.append(Component(f"U{index}_ADAPTER", "upper_adapters", _plate((ux, uy, upper_plate_center_z), 21.5), COLORS["plate"], "A6061-T6 5t"))
        for side in (-1.0, 1.0):
            upper_local.append(Component(f"U{index}_SPACER_{side:+.0f}", "upper_adapters", _tube_spacer((ux + side * 35.0, uy, upper_spacer_center_z), 20.0), COLORS["spacer"], "A6061 OD16 ID8.5 L20"))
            upper_local.append(Component(f"U{index}_M8_BOLT_{side:+.0f}", "adapter_fasteners", _cylinder_between((ux + side * 35.0, uy, upper_plate_center_z - 8.0), (ux + side * 35.0, uy, upper_spacer_center_z + 10.0), 3.9), COLORS["fastener"], "M8x40 socket bolt + T-nut"))
        upper_local.append(Component(f"U{index}_BJ762_20001", "upper_supports", _bj762_support((ux, uy), upper_mount_z, angle, 20, True), COLORS["support"], "SCM435 with 12x20 bushes"))
        upper_local.append(Component(f"U{index}_M20_NUT", "fasteners", _vertical_hollow_hex((ux, uy, upper_mount_z + 13.0), 16.0, 34.6, 20.3), COLORS["fastener"], "M20 nut"))
    return lower, upper_local


def _link_shape(lower, upper, lower_tangent, upper_tangent):
    lower_v = cq.Vector(*lower)
    upper_v = cq.Vector(*upper)
    delta = upper_v - lower_v
    length = delta.Length
    unit = delta.normalized()
    lower_t = cq.Vector(*lower_tangent).normalized()
    upper_t = cq.Vector(*upper_tangent).normalized()

    parts = []
    parts.append(_ring(lower, lower_t.toTuple(), 25.0, 12.15, 13.8, unit.toTuple()))
    parts.append(_cylinder_between(_point(lower, unit, 9), _point(lower, unit, 29), 6.0))
    parts.append(_cylinder_between(_point(lower, unit, 20), _point(lower, unit, 52), 6.0))
    parts.append(_hex_prism_between(_point(lower, unit, 21), _point(lower, unit, 28), 22.0))
    parts.append(_hex_prism_between(_point(lower, unit, 28), _point(lower, unit, 64), 22.0))
    parts.append(_cylinder_between(_point(lower, unit, 52), _point(lower, unit, 80), 6.0))
    parts.append(_hex_prism_between(_point(lower, unit, 64), _point(lower, unit, 71), 22.0))

    stb_lower_shoulder = 72.0
    stb_upper_shoulder = length - 57.0
    midpoint = (stb_lower_shoulder + stb_upper_shoulder) / 2.0
    central_start = midpoint - 40.5
    central_end = midpoint + 40.5
    parts.append(_cylinder_between(_point(lower, unit, stb_lower_shoulder), _point(lower, unit, central_start + 1), 6.0))
    parts.append(_hex_prism_between(_point(lower, unit, central_start - 7), _point(lower, unit, central_start), 22.0))
    parts.append(_hex_prism_between(_point(lower, unit, central_start), _point(lower, unit, central_end), 22.0))
    parts.append(_hex_prism_between(_point(lower, unit, central_end), _point(lower, unit, central_end + 7), 22.0))
    parts.append(_cylinder_between(_point(lower, unit, central_end - 1), _point(lower, unit, stb_upper_shoulder), 6.0))
    parts.append(_cylinder_between(_point(lower, unit, length - 57), _point(lower, unit, length - 37), 6.0))
    parts.append(_hex_prism_between(_point(lower, unit, length - 57), _point(lower, unit, length - 50), 22.0))

    parts.append(_cylinder_between(_point(lower, unit, length - 50), _point(lower, unit, length - 10), 9.5))
    parts.append(_ring(upper, upper_t.toTuple(), 30.0, 12.15, 15.8, unit.toTuple()))
    return cq.Compound.makeCompound(parts)


def _joint_pins(lower_points, upper_points, upper_tangents):
    parts = []
    for index, (lower, upper, (_, lower_tangent), upper_tangent) in enumerate(
        zip(lower_points, upper_points, data.support_basis(), upper_tangents), start=1
    ):
        l = cq.Vector(*lower)
        lt = cq.Vector(*lower_tangent).normalized()
        lower_pin = _cylinder_between(l - lt.multiply(18.0), l + lt.multiply(18.0), 5.9)
        parts.append(Component(f"L{index}_SUPPLIED_PIN", "joint_pins", lower_pin, COLORS["fastener"], "BJ762 supplied pin D12"))
        u = cq.Vector(*upper)
        ut = cq.Vector(*upper_tangent).normalized()
        upper_pin = _cylinder_between(u - ut.multiply(25.0), u + ut.multiply(25.0), 5.9)
        parts.append(Component(f"U{index}_M12_PIN_BOLT", "joint_pins", upper_pin, COLORS["fastener"], "M12x65 bolt and nut"))
    return parts


def components_for_pose(pitch_deg=0.0, roll_deg=0.0):
    lower_frame, upper_frame_local = _profile_frames()
    lower_parts, upper_parts_local = _adapter_components()
    solved = data.solve_platform(pitch_deg, roll_deg)
    rotation = data.rotation_matrix(pitch_deg, roll_deg, solved["yaw_rad"])
    translation = (solved["x_mm"], solved["y_mm"], P.upper_pin_z_mm)

    upper_components = []
    for component in upper_frame_local + upper_parts_local:
        upper_components.append(
            Component(
                component.name,
                component.group,
                _transform_shape(component.shape, pitch_deg, roll_deg, solved["yaw_rad"], translation),
                component.color,
                component.material,
            )
        )

    lower_points = data.lower_pin_points()
    upper_points = data.upper_pin_points(pitch_deg, roll_deg)
    upper_tangents = tuple(
        _transform_vector(tangent, rotation).toTuple()
        for _, tangent in data.support_basis()
    )
    links = []
    for index, (lower, upper, (_, lower_tangent), upper_tangent) in enumerate(
        zip(lower_points, upper_points, data.support_basis(), upper_tangents), start=1
    ):
        links.append(
            Component(
                f"LEG_{index}_STB_M12_LINK",
                "links",
                _link_shape(lower, upper, lower_tangent, upper_tangent),
                COLORS["link"],
                "STB-M12 + BJ761-12011N + PHS12L",
            )
        )
    return lower_frame + lower_parts + upper_components + links + _joint_pins(lower_points, upper_points, upper_tangents)


def grouped_components(pitch_deg=0.0, roll_deg=0.0):
    groups = {}
    for component in components_for_pose(pitch_deg, roll_deg):
        groups.setdefault(component.group, []).append(component)
    return groups


def compound_for_pose(pitch_deg=0.0, roll_deg=0.0):
    return cq.Compound.makeCompound([component.shape for component in components_for_pose(pitch_deg, roll_deg)])
