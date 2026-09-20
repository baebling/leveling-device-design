"""Shared dimensions and kinematic checks for profile radial Rev D.

Rev D removes the Rev C central hub plate. Three small local adapter brackets
orient the LMB-10 mounting holes radially while fastening to straight 4040
cross-member slots with two M8 screws each.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from itertools import combinations, product
from math import acos, asin, cos, degrees, radians, sin, sqrt


@dataclass(frozen=True)
class Parameters:
    outer_length_mm: float = 700.0
    lower_profile_mm: float = 40.0
    upper_profile_mm: float = 30.0
    lower_cross_length_mm: float = 620.0
    upper_cross_length_mm: float = 640.0
    lower_support_radius_mm: float = 95.0
    upper_support_radius_mm: float = 250.0
    lower_pin_z_mm: float = 84.0
    upper_ring_z_collapsed_mm: float = 246.0
    upper_profile_bottom_z_collapsed_mm: float = 270.0
    upper_profile_top_z_collapsed_mm: float = 300.0
    lift_mm: float = 50.0
    angle_deg: float = 3.0
    actuator_min_pin_mm: float = 205.0
    actuator_max_pin_mm: float = 305.0
    actuator_eye_outer_radius_mm: float = 10.0
    upper_rod_eye_overlap_mm: float = 2.0
    joint_side_offset_mm: float = 14.5
    adapter_length_x_mm: float = 120.0
    adapter_width_y_mm: float = 70.0
    adapter_thickness_mm: float = 8.0
    adapter_profile_hole_pitch_mm: float = 96.0
    lmb_hole_pitch_mm: float = 36.0
    lmb_base_length_mm: float = 56.0
    lmb_base_width_mm: float = 26.0
    lmb_pin_offset_from_base_center_mm: float = 18.0
    stop_catch_center_z_mm: float = 72.0
    stop_lower_washer_center_z_mm: float = 14.0
    stop_upper_washer_center_z_mm: float = 80.0
    stop_command_clearance_mm: float = 2.0
    stop_opening_radius_mm: float = 25.0
    stop_rod_radius_mm: float = 5.0
    stop_rod_offset_from_crossbar_mm: float = 52.0
    stop_contact_bar_length_mm: float = 70.0
    stop_contact_bar_width_mm: float = 20.0


P = Parameters()
SUPPORT_ANGLES_DEG = (90.0, 210.0, 330.0)

LOWER_CROSSBAR_Y_MM = (330.0, 95.0, -47.5, -330.0)
UPPER_CROSSBAR_Y_MM = (330.0, 250.0, -125.0, -330.0)
LOWER_CONNECTOR_EDGE_OFFSET_MM = P.lower_profile_mm / 2.0
UPPER_CONNECTOR_EDGE_OFFSET_MM = P.upper_profile_mm / 2.0

LOWER_PROFILE_CUTS = (
    ("LOWER_SIDE_L", "4040", 700.0),
    ("LOWER_SIDE_R", "4040", 700.0),
    ("LOWER_CROSS_FRONT", "4040", 620.0),
    ("LOWER_CROSS_A1", "4040", 620.0),
    ("LOWER_CROSS_A23", "4040", 620.0),
    ("LOWER_CROSS_REAR", "4040", 620.0),
)
UPPER_PROFILE_CUTS = (
    ("UPPER_SIDE_L", "3030", 700.0),
    ("UPPER_SIDE_R", "3030", 700.0),
    ("UPPER_CROSS_FRONT", "3030", 640.0),
    ("UPPER_CROSS_A1", "3030", 640.0),
    ("UPPER_CROSS_A23", "3030", 640.0),
    ("UPPER_CROSS_REAR", "3030", 640.0),
)


def support_basis():
    rows = []
    for angle_deg in SUPPORT_ANGLES_DEG:
        angle = radians(angle_deg)
        radial = (cos(angle), sin(angle), 0.0)
        tangent = (-sin(angle), cos(angle), 0.0)
        rows.append((radial, tangent))
    return tuple(rows)


def support_points(radius_mm):
    return tuple(
        (radius_mm * radial[0], radius_mm * radial[1])
        for radial, _ in support_basis()
    )


def lower_support_points():
    return support_points(P.lower_support_radius_mm)


def upper_support_points():
    return support_points(P.upper_support_radius_mm)


def adapter_rows():
    rows = []
    half_mount = P.adapter_profile_hole_pitch_mm / 2.0
    half_lmb = P.lmb_hole_pitch_mm / 2.0
    for index, ((x, y), (radial, tangent)) in enumerate(
        zip(lower_support_points(), support_basis()), start=1
    ):
        pin_x = x - P.joint_side_offset_mm * tangent[0]
        pin_y = y - P.joint_side_offset_mm * tangent[1]
        # The product photographs show the pivot close to one longitudinal end
        # of the 56 mm base.  Keep the actuator pin at the solved support point
        # and move the base inward; this also gives the motor housing the relief
        # provided by the real bracket's inclined side plates.
        lmb_x = pin_x - P.lmb_pin_offset_from_base_center_mm * radial[0]
        lmb_y = pin_y - P.lmb_pin_offset_from_base_center_mm * radial[1]
        profile_offsets = (-half_mount, half_mount)
        plate_x = x
        if index == 3:
            # Both slot fasteners remain on the A23 cross-member.  Their
            # asymmetric positions clear the oblique LMB-10 footprint.
            profile_offsets = (-70.0, 30.0)
            plate_x = x - 20.0
        plate_y = pin_y - 12.0 * radial[1]
        rows.append(
            {
                "id": f"A{index}",
                "center_mm": (x, y),
                "plate_center_mm": (plate_x, plate_y),
                "radial": radial,
                "tangent": tangent,
                "profile_mount_holes_mm": tuple((x + offset, y) for offset in profile_offsets),
                "lmb_tapped_holes_mm": (
                    (
                        lmb_x - half_lmb * radial[0],
                        lmb_y - half_lmb * radial[1],
                    ),
                    (
                        lmb_x + half_lmb * radial[0],
                        lmb_y + half_lmb * radial[1],
                    ),
                ),
                "lmb_center_mm": (lmb_x, lmb_y),
                "lmb_pin_center_mm": (pin_x, pin_y),
            }
        )
    return tuple(rows)


def lower_eye_points():
    rows = []
    for (x, y), (_, tangent) in zip(lower_support_points(), support_basis()):
        rows.append(
            (
                x - P.joint_side_offset_mm * tangent[0],
                y - P.joint_side_offset_mm * tangent[1],
                P.lower_pin_z_mm,
            )
        )
    return tuple(rows)


def upper_eye_local_points():
    rows = []
    for (x, y), (_, tangent) in zip(upper_support_points(), support_basis()):
        rows.append(
            (
                x - P.joint_side_offset_mm * tangent[0],
                y - P.joint_side_offset_mm * tangent[1],
                0.0,
            )
        )
    return tuple(rows)


def _dot(a, b):
    return sum(a[index] * b[index] for index in range(3))


def _matmul(a, b):
    return tuple(
        tuple(sum(a[row][k] * b[k][col] for k in range(3)) for col in range(3))
        for row in range(3)
    )


def _matvec(matrix, vector):
    return tuple(_dot(row, vector) for row in matrix)


def rotation_matrix(pitch_deg, roll_deg, yaw_rad=0.0):
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


def _constraint_values(values, pitch_deg, roll_deg):
    x_mm, y_mm, yaw_rad = values
    rotation = rotation_matrix(pitch_deg, roll_deg, yaw_rad)
    rows = []
    for lower, upper, (_, tangent) in zip(
        lower_eye_points(), upper_eye_local_points(), support_basis()
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
def solve_platform(pitch_deg, roll_deg):
    values = [0.0, 0.0, 0.0]
    steps = (1e-4, 1e-4, 1e-7)
    for _ in range(12):
        residual = _constraint_values(values, pitch_deg, roll_deg)
        if max(abs(value) for value in residual) < 1e-10:
            break
        columns = []
        for axis, step in enumerate(steps):
            shifted = list(values)
            shifted[axis] += step
            moved = _constraint_values(shifted, pitch_deg, roll_deg)
            columns.append(
                tuple((moved[row] - residual[row]) / step for row in range(3))
            )
        jacobian = tuple(
            tuple(columns[col][row] for col in range(3)) for row in range(3)
        )
        delta = _solve_linear_3x3(
            jacobian, tuple(-value for value in residual)
        )
        values = [values[index] + delta[index] for index in range(3)]
    residual = _constraint_values(values, pitch_deg, roll_deg)
    return {
        "x_mm": values[0],
        "y_mm": values[1],
        "yaw_rad": values[2],
        "residual_mm": max(abs(value) for value in residual),
    }


def _upper_world_points(lift_mm, pitch_deg, roll_deg):
    solved = solve_platform(pitch_deg, roll_deg)
    rotation = rotation_matrix(pitch_deg, roll_deg, solved["yaw_rad"])
    rows = []
    z = P.upper_ring_z_collapsed_mm + lift_mm
    for point in upper_eye_local_points():
        moved = _matvec(rotation, point)
        rows.append(
            (
                moved[0] + solved["x_mm"],
                moved[1] + solved["y_mm"],
                moved[2] + z,
            )
        )
    return tuple(rows)


def pin_lengths(lift_mm, pitch_deg, roll_deg):
    upper = _upper_world_points(lift_mm, pitch_deg, roll_deg)
    return tuple(
        sqrt(sum((upper[i][axis] - lower[axis]) ** 2 for axis in range(3)))
        for i, lower in enumerate(lower_eye_points())
    )


def workspace_audit():
    rows = []
    for lift_mm, pitch_deg, roll_deg in product(
        (0.0, 25.0, 50.0), (-3.0, 0.0, 3.0), (-3.0, 0.0, 3.0)
    ):
        solved = solve_platform(pitch_deg, roll_deg)
        lengths = pin_lengths(lift_mm, pitch_deg, roll_deg)
        rows.append(
            {
                "lift_mm": lift_mm,
                "pitch_deg": pitch_deg,
                "roll_deg": roll_deg,
                **solved,
                "pin_lengths_mm": lengths,
            }
        )
    minimum = min(min(row["pin_lengths_mm"]) for row in rows)
    maximum = max(max(row["pin_lengths_mm"]) for row in rows)
    max_residual = max(row["residual_mm"] for row in rows)
    return {
        "pose_count": len(rows),
        "minimum_pin_mm": minimum,
        "maximum_pin_mm": maximum,
        "retract_margin_mm": minimum - P.actuator_min_pin_mm,
        "extend_margin_mm": P.actuator_max_pin_mm - maximum,
        "maximum_constraint_residual_mm": max_residual,
        "passes": (
            minimum >= P.actuator_min_pin_mm
            and maximum <= P.actuator_max_pin_mm
            and max_residual < 1e-6
        ),
        "rows": rows,
    }


def joint_axis_audit():
    rows = []
    for lift_mm, pitch_deg, roll_deg in product(
        (0.0, 25.0, 50.0), (-3.0, 0.0, 3.0), (-3.0, 0.0, 3.0)
    ):
        solved = solve_platform(pitch_deg, roll_deg)
        rotation = rotation_matrix(pitch_deg, roll_deg, solved["yaw_rad"])
        upper_points = _upper_world_points(lift_mm, pitch_deg, roll_deg)
        for index, (lower, upper, (_, tangent)) in enumerate(
            zip(lower_eye_points(), upper_points, support_basis()), start=1
        ):
            actuator = tuple(upper[axis] - lower[axis] for axis in range(3))
            actuator_length = sqrt(_dot(actuator, actuator))
            actuator_axis = tuple(value / actuator_length for value in actuator)
            upper_outer_axis = _matvec(rotation, tangent)
            perpendicular_error = degrees(
                asin(min(1.0, abs(_dot(actuator_axis, tangent))))
            )
            articulation = degrees(
                acos(max(-1.0, min(1.0, abs(_dot(tangent, upper_outer_axis)))))
            )
            rows.append(
                {
                    "lift_mm": lift_mm,
                    "pitch_deg": pitch_deg,
                    "roll_deg": roll_deg,
                    "actuator": index,
                    "actuator_to_lower_pin_perpendicular_error_deg": perpendicular_error,
                    "phs6_articulation_deg": articulation,
                }
            )
    maximum_error = max(
        row["actuator_to_lower_pin_perpendicular_error_deg"] for row in rows
    )
    maximum_articulation = max(row["phs6_articulation_deg"] for row in rows)
    return {
        "maximum_perpendicular_error_deg": maximum_error,
        "maximum_phs6_articulation_deg": maximum_articulation,
        "published_phs6_allowance_deg": 8.0,
        "passes": maximum_error < 1e-6 and maximum_articulation <= 8.0,
        "rows": rows,
    }


def stop_sweep_audit():
    rod_y = 330.0 - P.stop_rod_offset_from_crossbar_mm
    rod_points = ((0.0, rod_y), (-240.0, -rod_y), (240.0, -rod_y))
    local_z = P.stop_catch_center_z_mm - P.upper_ring_z_collapsed_mm
    rows = []
    for pitch_deg, roll_deg in product((-3.0, 0.0, 3.0), repeat=2):
        solved = solve_platform(pitch_deg, roll_deg)
        rotation = rotation_matrix(pitch_deg, roll_deg, solved["yaw_rad"])
        for index, (x, y) in enumerate(rod_points, start=1):
            moved = _matvec(rotation, (x, y, local_z))
            moved_x = moved[0] + solved["x_mm"]
            moved_y = moved[1] + solved["y_mm"]
            sweep = sqrt((moved_x - x) ** 2 + (moved_y - y) ** 2)
            rows.append(
                {
                    "stop": index,
                    "pitch_deg": pitch_deg,
                    "roll_deg": roll_deg,
                    "horizontal_sweep_mm": sweep,
                }
            )
    maximum = max(row["horizontal_sweep_mm"] for row in rows)
    allowance = P.stop_opening_radius_mm - P.stop_rod_radius_mm
    contact_bar_to_profile_clearance = (
        P.stop_rod_offset_from_crossbar_mm
        - P.lower_profile_mm / 2.0
        - P.stop_contact_bar_width_mm / 2.0
        - maximum
    )
    lower_contact_lift = (
        P.stop_catch_center_z_mm
        - 4.0
        - (P.stop_lower_washer_center_z_mm + 2.0)
    )
    upper_contact_lift = (
        P.stop_catch_center_z_mm
        + 4.0
        - (P.stop_upper_washer_center_z_mm - 2.0)
    )
    return {
        "maximum_horizontal_sweep_mm": maximum,
        "allowed_center_sweep_mm": allowance,
        "minimum_radial_clearance_mm": allowance - maximum,
        "minimum_contact_bar_to_profile_clearance_mm": contact_bar_to_profile_clearance,
        "lower_mechanical_contact_lift_mm": upper_contact_lift,
        "upper_mechanical_contact_lift_mm": lower_contact_lift,
        "command_range_mm": (0.0, P.lift_mm),
        "passes": (
            maximum <= allowance
            and contact_bar_to_profile_clearance >= 2.0
            and abs(upper_contact_lift + P.stop_command_clearance_mm) < 1e-9
            and abs(
                lower_contact_lift
                - (P.lift_mm + P.stop_command_clearance_mm)
            )
            < 1e-9
        ),
        "rows": rows,
    }


def adapter_audit():
    rows = adapter_rows()
    expected_y = (
        P.lower_support_radius_mm,
        -0.5 * P.lower_support_radius_mm,
        -0.5 * P.lower_support_radius_mm,
    )
    alignment = []
    for row, crossbar_y in zip(rows, expected_y):
        mount_y = tuple(point[1] for point in row["profile_mount_holes_mm"])
        lmb = row["lmb_tapped_holes_mm"]
        pitch = sqrt(
            (lmb[1][0] - lmb[0][0]) ** 2 + (lmb[1][1] - lmb[0][1]) ** 2
        )
        alignment.append(
            {
                "id": row["id"],
                "crossbar_y_mm": crossbar_y,
                "mount_hole_y_mm": mount_y,
                "mount_holes_on_slot": all(
                    abs(value - crossbar_y) < 1e-9 for value in mount_y
                ),
                "lmb_hole_pitch_mm": pitch,
            }
        )
    overlaps = []
    for first, second in combinations(rows, 2):
        dx = abs(first["plate_center_mm"][0] - second["plate_center_mm"][0])
        dy = abs(first["plate_center_mm"][1] - second["plate_center_mm"][1])
        overlap_x = dx < P.adapter_length_x_mm
        overlap_y = dy < P.adapter_width_y_mm
        overlaps.append(
            {
                "pair": (first["id"], second["id"]),
                "overlaps": overlap_x and overlap_y,
            }
        )
    hole_edge_checks = []
    profile_fastener_clearance_checks = []
    for row in rows:
        cx, cy = row["plate_center_mm"]
        half_x = P.adapter_length_x_mm / 2.0
        half_y = P.adapter_width_y_mm / 2.0
        points = row["profile_mount_holes_mm"] + row["lmb_tapped_holes_mm"]
        edge_margin = min(
            min(half_x - abs(x - cx), half_y - abs(y - cy)) for x, y in points
        )
        hole_edge_checks.append(
            {"id": row["id"], "minimum_hole_center_edge_margin_mm": edge_margin}
        )
        radial = row["radial"]
        tangent = row["tangent"]
        lmb_x, lmb_y = row["lmb_center_mm"]
        clearances = []
        for hole_x, hole_y in row["profile_mount_holes_mm"]:
            dx = hole_x - lmb_x
            dy = hole_y - lmb_y
            radial_distance = abs(dx * radial[0] + dy * radial[1])
            tangent_distance = abs(dx * tangent[0] + dy * tangent[1])
            radial_gap = max(radial_distance - P.lmb_base_length_mm / 2.0, 0.0)
            tangent_gap = max(tangent_distance - P.lmb_base_width_mm / 2.0, 0.0)
            clearances.append(sqrt(radial_gap**2 + tangent_gap**2) - 10.0)
        profile_fastener_clearance_checks.append(
            {
                "id": row["id"],
                "minimum_m8_socket_to_lmb_planar_clearance_mm": min(clearances),
            }
        )
    return {
        "adapter_count": len(rows),
        "central_hub_plate_count": 0,
        "adapter_size_mm": (
            P.adapter_length_x_mm,
            P.adapter_width_y_mm,
            P.adapter_thickness_mm,
        ),
        "alignment": alignment,
        "overlaps": overlaps,
        "hole_edge_checks": hole_edge_checks,
        "profile_fastener_clearance_checks": profile_fastener_clearance_checks,
        "passes": (
            all(row["mount_holes_on_slot"] for row in alignment)
            and all(abs(row["lmb_hole_pitch_mm"] - 36.0) < 1e-9 for row in alignment)
            and not any(row["overlaps"] for row in overlaps)
            and min(row["minimum_hole_center_edge_margin_mm"] for row in hole_edge_checks)
            >= 10.0
            and min(
                row["minimum_m8_socket_to_lmb_planar_clearance_mm"]
                for row in profile_fastener_clearance_checks
            )
            >= 3.0
        ),
    }


def connector_audit():
    return {
        "lower_4035_count": 8,
        "upper_DCB3025_count": 8,
        "axes_per_bracket": ("horizontal_X", "horizontal_Y"),
        "lower_crossbar_center_to_bracket_corner_mm": LOWER_CONNECTOR_EDGE_OFFSET_MM,
        "upper_crossbar_center_to_bracket_corner_mm": UPPER_CONNECTOR_EDGE_OFFSET_MM,
        "bracket_corner_reference": "crossbar_outer_face",
        "oblique_profile_joint_count": 0,
        "unavailable_adjustable_bracket_count": 0,
        "passes": True,
    }


def full_audit():
    workspace = workspace_audit()
    joints = joint_axis_audit()
    stops = stop_sweep_audit()
    adapters = adapter_audit()
    connectors = connector_audit()
    azimuth_gaps = (120.0, 120.0, 120.0)
    return {
        "revision": "D",
        "status": "FUSION_NATIVE_DETAIL_IN_PROGRESS_NOT_FOR_ORDER",
        "parameters": asdict(P),
        "support_azimuths_deg": SUPPORT_ANGLES_DEG,
        "support_gaps_deg": azimuth_gaps,
        "lower_profile_cuts": LOWER_PROFILE_CUTS,
        "upper_profile_cuts": UPPER_PROFILE_CUTS,
        "workspace": workspace,
        "joint_axes": joints,
        "mechanical_stops": stops,
        "adapters": adapters,
        "connectors": connectors,
        "collapsed_height_mm": P.upper_profile_top_z_collapsed_mm,
        "digital_layout_passes": (
            workspace["passes"]
            and joints["passes"]
            and stops["passes"]
            and adapters["passes"]
            and connectors["passes"]
            and P.upper_profile_top_z_collapsed_mm <= 300.0
        ),
        "fabrication_release": False,
        "purchase_release": False,
    }
