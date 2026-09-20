"""Shared parameters and engineering checks for Manual 3-RPS Rev M1.

All dimensions are millimetres unless noted otherwise.  This module is kept
free of Fusion imports so the same geometry can be audited independently.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from itertools import product
from math import acos, asin, cos, degrees, floor, pi, radians, sin, sqrt


@dataclass(frozen=True)
class Parameters:
    outer_length_mm: float = 700.0
    lower_profile_mm: float = 40.0
    upper_profile_mm: float = 30.0
    lower_cross_length_mm: float = 620.0
    upper_cross_length_mm: float = 640.0
    lower_support_radius_mm: float = 75.0
    upper_support_radius_mm: float = 250.0
    lower_pin_z_mm: float = 84.0
    upper_ring_z_collapsed_mm: float = 235.0
    upper_profile_bottom_z_collapsed_mm: float = 270.0
    upper_profile_top_z_collapsed_mm: float = 300.0
    lift_mm: float = 50.0
    angle_deg: float = 3.0

    adapter_length_x_mm: float = 120.0
    adapter_width_y_mm: float = 80.0
    adapter_thickness_mm: float = 8.0
    adapter_profile_hole_pitch_mm: float = 96.0

    outer_tube_od_mm: float = 32.0
    outer_tube_wall_mm: float = 2.0
    outer_tube_length_mm: float = 160.0
    outer_tube_s_start_mm: float = -16.0
    inner_tube_od_mm: float = 25.0
    inner_tube_wall_mm: float = 2.0
    inner_tube_length_mm: float = 150.0
    inner_tube_s_start_zero_mm: float = 8.0
    neutral_coarse_mm: float = 15.0

    coarse_pitch_mm: float = 15.0
    coarse_position_count: int = 6
    coarse_pin_s_mm: float = 115.0
    coarse_pin_diameter_mm: float = 8.0
    coarse_hole_diameter_max_mm: float = 8.1
    coarse_pin_grip_mm: float = 40.0

    bushing_id_mm: float = 25.0
    bushing_od_mm: float = 28.0
    bushing_flange_od_mm: float = 35.0
    bushing_length_mm: float = 21.0
    bushing_flange_thickness_mm: float = 1.5
    bushing_housing_min_mm: float = 28.000
    bushing_housing_max_mm: float = 28.021
    bushing_installed_id_min_mm: float = 25.040
    bushing_installed_id_max_mm: float = 25.124
    bushing_shaft_min_mm: float = 24.948
    bushing_shaft_max_mm: float = 25.000

    guide_ring_od_mm: float = 27.6
    guide_ring_id_mm: float = 25.10
    guide_ring_length_mm: float = 12.0

    threaded_plug_od_mm: float = 20.8
    threaded_plug_length_mm: float = 30.0
    threaded_plug_retainer_diameter_mm: float = 4.0
    threaded_plug_retainer_offset_mm: float = 22.5
    fine_stud_diameter_mm: float = 10.0
    fine_stud_pitch_mm: float = 1.5
    fine_stud_projection_mm: float = 33.0
    fine_stud_bottom_engagement_mm: float = 20.0

    phs_bore_mm: float = 10.0
    phs_outer_diameter_mm: float = 26.0
    phs_ring_width_mm: float = 14.0
    phs_holder_width_mm: float = 17.0
    phs_overall_length_mm: float = 56.0
    phs_center_to_thread_end_mm: float = 43.0
    phs_thread_depth_mm: float = 21.0
    phs_thread_engagement_min_mm: float = 6.0
    phs_thread_engagement_max_mm: float = 21.0
    phs_static_radial_capacity_n: float = 13200.0
    phs_min_permissible_tilt_deg: float = 8.0

    lower_clevis_gap_mm: float = 34.0
    lower_clevis_ear_thickness_mm: float = 6.0
    lower_clevis_base_length_mm: float = 60.0
    lower_clevis_base_width_mm: float = 50.0
    lower_clevis_base_thickness_mm: float = 8.0
    lower_pivot_diameter_mm: float = 8.0
    lower_pivot_grip_mm: float = 46.0

    upper_clevis_gap_mm: float = 20.0
    upper_clevis_ear_thickness_mm: float = 6.0
    upper_clevis_base_length_mm: float = 100.0
    upper_clevis_base_width_mm: float = 60.0
    upper_clevis_base_thickness_mm: float = 8.0
    upper_pivot_diameter_mm: float = 10.0
    upper_pivot_grip_mm: float = 32.0
    upper_side_shim_thickness_mm: float = 3.0

    design_leg_load_n: float = 600.0
    aluminium_elastic_modulus_mpa: float = 69000.0
    aluminium_6063_t5_yield_mpa: float = 145.0


P = Parameters()
SUPPORT_ANGLES_DEG = (90.0, 210.0, 330.0)
LOWER_CROSSBAR_Y_MM = (330.0, 75.0, -37.5, -330.0)
UPPER_CROSSBAR_Y_MM = (330.0, 250.0, -125.0, -330.0)

LOWER_PROFILE_CUTS = (
    ("LOWER_SIDE_L", "DNF4040", 700.0),
    ("LOWER_SIDE_R", "DNF4040", 700.0),
    ("LOWER_CROSS_FRONT", "DNF4040", 620.0),
    ("LOWER_CROSS_A1", "DNF4040", 620.0),
    ("LOWER_CROSS_A23", "DNF4040", 620.0),
    ("LOWER_CROSS_REAR", "DNF4040", 620.0),
)
UPPER_PROFILE_CUTS = (
    ("UPPER_SIDE_L", "DNF3030", 700.0),
    ("UPPER_SIDE_R", "DNF3030", 700.0),
    ("UPPER_CROSS_FRONT", "DNF3030", 640.0),
    ("UPPER_CROSS_A1", "DNF3030", 640.0),
    ("UPPER_CROSS_A23", "DNF3030", 640.0),
    ("UPPER_CROSS_REAR", "DNF3030", 640.0),
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


def lower_eye_points():
    return tuple(
        (x, y, P.lower_pin_z_mm)
        for x, y in support_points(P.lower_support_radius_mm)
    )


def upper_eye_local_points():
    return tuple(
        (x, y, 0.0)
        for x, y in support_points(P.upper_support_radius_mm)
    )


def adapter_rows():
    half_pitch = P.adapter_profile_hole_pitch_mm / 2.0
    rows = []
    for index, ((x, y), (radial, tangent)) in enumerate(
        zip(support_points(P.lower_support_radius_mm), support_basis()), start=1
    ):
        rows.append(
            {
                "id": f"A{index}",
                "center_mm": (x, y),
                "radial": radial,
                "tangent": tangent,
                "profile_mount_holes_mm": ((x - half_pitch, y), (x + half_pitch, y)),
                "clevis_mount_holes_mm": (
                    (x - 20.0 * radial[0], y - 20.0 * radial[1]),
                    (x + 20.0 * radial[0], y + 20.0 * radial[1]),
                ),
            }
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
            ratio = rows[row][pivot] / rows[pivot][pivot]
            for column in range(pivot, 4):
                rows[row][column] -= ratio * rows[pivot][column]
    result = [0.0, 0.0, 0.0]
    for row in range(2, -1, -1):
        result[row] = (
            rows[row][3]
            - sum(rows[row][column] * result[column] for column in range(row + 1, 3))
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
            columns.append(tuple((moved[row] - residual[row]) / step for row in range(3)))
        jacobian = tuple(
            tuple(columns[column][row] for column in range(3)) for row in range(3)
        )
        delta = _solve_linear_3x3(jacobian, tuple(-value for value in residual))
        values = [values[index] + delta[index] for index in range(3)]
    residual = _constraint_values(values, pitch_deg, roll_deg)
    return {
        "x_mm": values[0],
        "y_mm": values[1],
        "yaw_rad": values[2],
        "residual_mm": max(abs(value) for value in residual),
    }


def upper_world_points(lift_mm, pitch_deg, roll_deg):
    solved = solve_platform(pitch_deg, roll_deg)
    rotation = rotation_matrix(pitch_deg, roll_deg, solved["yaw_rad"])
    z_mm = P.upper_ring_z_collapsed_mm + lift_mm
    rows = []
    for local in upper_eye_local_points():
        moved = _matvec(rotation, local)
        rows.append(
            (
                moved[0] + solved["x_mm"],
                moved[1] + solved["y_mm"],
                moved[2] + z_mm,
            )
        )
    return tuple(rows)


def pin_lengths(lift_mm, pitch_deg, roll_deg):
    return tuple(
        sqrt(sum((upper[axis] - lower[axis]) ** 2 for axis in range(3)))
        for lower, upper in zip(
            lower_eye_points(), upper_world_points(lift_mm, pitch_deg, roll_deg)
        )
    )


def coarse_positions_mm():
    return tuple(P.coarse_pitch_mm * index for index in range(P.coarse_position_count))


def manual_pin_range_mm():
    inner_top_zero = P.inner_tube_s_start_zero_mm + P.inner_tube_length_mm
    minimum = (
        inner_top_zero
        + P.fine_stud_projection_mm
        - P.phs_thread_engagement_max_mm
        + P.phs_center_to_thread_end_mm
    )
    maximum = (
        inner_top_zero
        + coarse_positions_mm()[-1]
        + P.fine_stud_projection_mm
        - P.phs_thread_engagement_min_mm
        + P.phs_center_to_thread_end_mm
    )
    return minimum, maximum


def setting_for_length(length_mm):
    minimum, maximum = manual_pin_range_mm()
    if length_mm < minimum - 1e-9 or length_mm > maximum + 1e-9:
        raise ValueError(f"Length {length_mm:.3f} mm is outside manual range")
    coarse = min(
        coarse_positions_mm()[-1],
        max(0.0, P.coarse_pitch_mm * floor((length_mm - minimum) / P.coarse_pitch_mm)),
    )
    fine_extension = length_mm - (minimum + coarse)
    if fine_extension > P.coarse_pitch_mm + 1e-8:
        coarse += P.coarse_pitch_mm
        fine_extension = length_mm - (minimum + coarse)
    engagement = P.phs_thread_engagement_max_mm - fine_extension
    return {
        "coarse_mm": coarse,
        "fine_extension_mm": fine_extension,
        "phs_thread_engagement_mm": engagement,
        "turns_from_minimum": fine_extension / P.fine_stud_pitch_mm,
    }


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
                "manual_settings": tuple(setting_for_length(value) for value in lengths),
            }
        )
    minimum = min(min(row["pin_lengths_mm"]) for row in rows)
    maximum = max(max(row["pin_lengths_mm"]) for row in rows)
    manual_minimum, manual_maximum = manual_pin_range_mm()
    max_residual = max(row["residual_mm"] for row in rows)
    return {
        "pose_count": len(rows),
        "minimum_required_pin_mm": minimum,
        "maximum_required_pin_mm": maximum,
        "manual_minimum_pin_mm": manual_minimum,
        "manual_maximum_pin_mm": manual_maximum,
        "lower_margin_mm": minimum - manual_minimum,
        "upper_margin_mm": manual_maximum - maximum,
        "maximum_constraint_residual_mm": max_residual,
        "passes": minimum >= manual_minimum and maximum <= manual_maximum and max_residual < 1e-6,
        "rows": rows,
    }


def joint_axis_audit():
    rows = []
    for lift_mm, pitch_deg, roll_deg in product(
        (0.0, 25.0, 50.0), (-3.0, 0.0, 3.0), (-3.0, 0.0, 3.0)
    ):
        solved = solve_platform(pitch_deg, roll_deg)
        rotation = rotation_matrix(pitch_deg, roll_deg, solved["yaw_rad"])
        for index, (lower, upper, (_, tangent)) in enumerate(
            zip(lower_eye_points(), upper_world_points(lift_mm, pitch_deg, roll_deg), support_basis()),
            start=1,
        ):
            axis = tuple(upper[value] - lower[value] for value in range(3))
            axis_length = sqrt(_dot(axis, axis))
            axis = tuple(value / axis_length for value in axis)
            upper_pin_axis = _matvec(rotation, tangent)
            lower_perpendicular_error = degrees(asin(min(1.0, abs(_dot(axis, tangent)))))
            phs_articulation = degrees(
                acos(max(-1.0, min(1.0, abs(_dot(tangent, upper_pin_axis)))))
            )
            rows.append(
                {
                    "pose": (lift_mm, pitch_deg, roll_deg),
                    "strut": index,
                    "lower_axis_perpendicular_error_deg": lower_perpendicular_error,
                    "phs10_articulation_deg": phs_articulation,
                }
            )
    maximum_error = max(row["lower_axis_perpendicular_error_deg"] for row in rows)
    maximum_articulation = max(row["phs10_articulation_deg"] for row in rows)
    return {
        "maximum_lower_axis_perpendicular_error_deg": maximum_error,
        "maximum_phs10_articulation_deg": maximum_articulation,
        "published_phs10_allowance_deg": P.phs_min_permissible_tilt_deg,
        "passes": maximum_error < 1e-6 and maximum_articulation <= P.phs_min_permissible_tilt_deg,
        "rows": rows,
    }


def axial_stack_audit():
    outer_top = P.outer_tube_s_start_mm + P.outer_tube_length_mm
    bushing_bottom = outer_top - P.bushing_length_mm
    rows = []
    for coarse_mm in coarse_positions_mm():
        inner_bottom = P.inner_tube_s_start_zero_mm + coarse_mm
        inner_top = inner_bottom + P.inner_tube_length_mm
        overlap = outer_top - inner_bottom
        guide_top = inner_bottom + P.guide_ring_length_mm
        hole_offset = P.coarse_pin_s_mm - inner_bottom
        rows.append(
            {
                "coarse_mm": coarse_mm,
                "inner_bottom_s_mm": inner_bottom,
                "inner_top_s_mm": inner_top,
                "overlap_mm": overlap,
                "inner_hole_offset_mm": hole_offset,
                "guide_ring_top_s_mm": guide_top,
                "guide_to_bushing_clearance_mm": bushing_bottom - guide_top,
            }
        )
    hole_offsets = tuple(row["inner_hole_offset_mm"] for row in rows)
    hole_ligament = P.coarse_pitch_mm - P.coarse_pin_diameter_mm
    minimum_overlap = min(row["overlap_mm"] for row in rows)
    minimum_guide_clearance = min(row["guide_to_bushing_clearance_mm"] for row in rows)
    annular_wall = (P.outer_tube_od_mm - P.bushing_od_mm) / 2.0
    plug_retainer_to_stud_axial_clearance = (
        P.threaded_plug_retainer_offset_mm
        - P.fine_stud_bottom_engagement_mm
        - P.threaded_plug_retainer_diameter_mm / 2.0
    )
    return {
        "outer_top_s_mm": outer_top,
        "bushing_bottom_s_mm": bushing_bottom,
        "coarse_positions_mm": coarse_positions_mm(),
        "inner_hole_offsets_mm": hole_offsets,
        "hole_edge_ligament_mm": hole_ligament,
        "minimum_telescopic_overlap_mm": minimum_overlap,
        "minimum_guide_to_bushing_clearance_mm": minimum_guide_clearance,
        "outer_wall_after_28H7_ream_mm": annular_wall,
        "plug_retainer_to_stud_axial_clearance_mm": plug_retainer_to_stud_axial_clearance,
        "rows": rows,
        "passes": (
            hole_ligament >= 6.0
            and minimum_overlap >= 60.0
            and minimum_guide_clearance >= 5.0
            and annular_wall >= 1.9
            and plug_retainer_to_stud_axial_clearance >= 0.5
            and abs(hole_offsets[0] - 107.0) < 1e-9
            and abs(hole_offsets[-1] - 32.0) < 1e-9
        ),
    }


def clevis_stack_audit():
    lower_outer_width = P.lower_clevis_gap_mm + 2.0 * P.lower_clevis_ear_thickness_mm
    upper_outer_width = P.upper_clevis_gap_mm + 2.0 * P.upper_clevis_ear_thickness_mm
    return {
        "lower": {
            "outer_tube_od_mm": P.outer_tube_od_mm,
            "gap_mm": P.lower_clevis_gap_mm,
            "diametral_clearance_mm": P.lower_clevis_gap_mm - P.outer_tube_od_mm,
            "outer_width_mm": lower_outer_width,
            "pivot_grip_mm": P.lower_pivot_grip_mm,
            "axial_stack_clearance_mm": P.lower_pivot_grip_mm - lower_outer_width,
        },
        "upper": {
            "phs_ring_width_mm": P.phs_ring_width_mm,
            "phs_holder_width_mm": P.phs_holder_width_mm,
            "gap_mm": P.upper_clevis_gap_mm,
            "side_shim_total_mm": P.upper_clevis_gap_mm - P.phs_ring_width_mm,
            "holder_clearance_mm": P.upper_clevis_gap_mm - P.phs_holder_width_mm,
            "outer_width_mm": upper_outer_width,
            "pivot_grip_mm": P.upper_pivot_grip_mm,
            "axial_stack_clearance_mm": P.upper_pivot_grip_mm - upper_outer_width,
        },
        "passes": (
            P.lower_clevis_gap_mm - P.outer_tube_od_mm >= 1.0
            and abs(P.lower_pivot_grip_mm - lower_outer_width) < 1e-9
            and P.upper_clevis_gap_mm - P.phs_ring_width_mm >= 1.0
            and P.upper_clevis_gap_mm - P.phs_holder_width_mm >= 2.0
            and abs(
                P.upper_clevis_gap_mm
                - P.phs_ring_width_mm
                - 2.0 * P.upper_side_shim_thickness_mm
            )
            < 1e-9
            and abs(P.upper_pivot_grip_mm - upper_outer_width) < 1e-9
        ),
    }


def structural_screen():
    load = P.design_leg_load_n
    tube_bearing_area = 2.0 * P.outer_tube_wall_mm * P.coarse_pin_diameter_mm
    tube_bearing_stress = load / tube_bearing_area
    inner_id = P.inner_tube_od_mm - 2.0 * P.inner_tube_wall_mm
    second_moment = pi / 64.0 * (P.inner_tube_od_mm**4 - inner_id**4)
    euler_load = pi**2 * P.aluminium_elastic_modulus_mpa * second_moment / (303.0**2)
    m10_shear_area = pi * 8.376 * P.phs_thread_engagement_min_mm * 0.5
    conservative_thread_capacity = m10_shear_area * 100.0
    return {
        "design_leg_load_n": load,
        "outer_tube_hole_bearing_stress_mpa": tube_bearing_stress,
        "outer_tube_hole_bearing_yield_ratio": P.aluminium_6063_t5_yield_mpa / tube_bearing_stress,
        "inner_tube_second_moment_mm4": second_moment,
        "inner_tube_euler_load_n": euler_load,
        "inner_tube_euler_factor": euler_load / load,
        "phs10_static_capacity_n": P.phs_static_radial_capacity_n,
        "phs10_static_factor": P.phs_static_radial_capacity_n / load,
        "minimum_phs_thread_engagement_mm": P.phs_thread_engagement_min_mm,
        "conservative_m10_female_thread_capacity_n": conservative_thread_capacity,
        "conservative_m10_thread_factor": conservative_thread_capacity / load,
        "passes": (
            tube_bearing_stress <= P.aluminium_6063_t5_yield_mpa / 3.0
            and euler_load / load >= 5.0
            and P.phs_static_radial_capacity_n / load >= 5.0
            and conservative_thread_capacity / load >= 5.0
        ),
    }


def component_count_basis():
    return {
        "lower_dnf4040_profiles": 6,
        "upper_dnf3030_profiles": 6,
        "lower_4035_brackets": 8,
        "upper_dcb3025_brackets": 8,
        "lower_adapter_plates": 3,
        "lower_clevis_bases": 3,
        "lower_clevis_ears": 6,
        "outer_tubes": 3,
        "inner_tubes": 3,
        "jfm_2528_21_bushings": 3,
        "pom_guide_rings": 3,
        "threaded_plugs": 3,
        "m10_fine_studs": 3,
        "phs10_rod_ends": 3,
        "bj775_08040_sus_pins": 3,
        "upper_clevis_bases": 3,
        "upper_clevis_ears": 6,
        "lower_m8_pivot_bolts": 3,
        "upper_m10_pivot_bolts": 3,
        "upper_side_shims_3mm": 6,
        "fine_adjuster_thin_nuts_m10": 6,
    }


def full_audit():
    workspace = workspace_audit()
    joints = joint_axis_audit()
    axial = axial_stack_audit()
    clevises = clevis_stack_audit()
    structure = structural_screen()
    return {
        "revision": "M1",
        "status": "MANUAL_DETAILED_CAD_IN_PROGRESS_NOT_FOR_ORDER",
        "parameters": asdict(P),
        "support_azimuths_deg": SUPPORT_ANGLES_DEG,
        "lower_profile_cuts": LOWER_PROFILE_CUTS,
        "upper_profile_cuts": UPPER_PROFILE_CUTS,
        "workspace": workspace,
        "joint_axes": joints,
        "axial_stack": axial,
        "clevis_stacks": clevises,
        "structural_screen": structure,
        "component_count_basis": component_count_basis(),
        "collapsed_height_mm": P.upper_profile_top_z_collapsed_mm,
        "digital_layout_passes": (
            workspace["passes"]
            and joints["passes"]
            and axial["passes"]
            and clevises["passes"]
            and structure["passes"]
            and P.upper_profile_top_z_collapsed_mm <= 300.0
        ),
        "fabrication_release": False,
        "purchase_release": False,
    }
