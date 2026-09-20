"""Independent kinematic and strength screen for Manual 3-RPS Rev M2.

Rev M2 removes the drilled telescoping struts used by Rev M1.  Each leg is
assembled from a commercial M12 RH/LH turnbuckle, a rigid lower hinge eye,
and a left-hand female spherical rod end.  Only the tilt-only workspace is
screened; common Z lift is deliberately excluded.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from itertools import product
from math import cos, pi, radians, sin, sqrt


@dataclass(frozen=True)
class Parameters:
    outer_length_mm: float = 700.0
    lower_profile_mm: float = 40.0
    upper_profile_mm: float = 30.0
    lower_cross_length_mm: float = 620.0
    upper_cross_length_mm: float = 640.0
    lower_support_radius_mm: float = 75.0
    upper_support_radius_mm: float = 315.0
    lower_pin_z_mm: float = 81.0
    upper_pin_z_mm: float = 213.0
    upper_profile_bottom_z_mm: float = 270.0
    upper_profile_top_z_mm: float = 300.0
    angle_deg: float = 3.0

    adapter_length_mm: float = 100.0
    adapter_width_mm: float = 60.0
    adapter_thickness_mm: float = 5.0
    adapter_hole_pitch_mm: float = 70.0
    lower_standoff_mm: float = 15.0
    upper_standoff_mm: float = 20.0

    # NBK STB-M12 / SJN-M12 catalogue dimensions.
    thread_nominal_mm: float = 12.0
    thread_pitch_mm: float = 1.75
    stb_min_tip_span_mm: float = 171.0
    sjn_thread_length_each_end_mm: float = 38.0
    required_internal_engagement_mm: float = 18.0

    # Lower end: DIN 6334 M12x36 coupling nut, BJ761-12011N eye bolt.
    coupling_nut_length_mm: float = 36.0
    lower_stb_external_engagement_mm: float = 12.0
    lower_eye_external_engagement_mm: float = 22.0
    lower_coupling_internal_gap_mm: float = 2.0
    bj761_eye_center_to_thread_tip_mm: float = 50.0

    # Upper end: PHS12L female rod end, 50 mm centre-to-thread-end.
    upper_rod_end_center_to_thread_end_mm: float = 50.0
    upper_stb_external_engagement_mm: float = 13.0

    design_leg_load_n: float = 600.0
    steel_elastic_modulus_mpa: float = 205000.0
    m12_conservative_minor_diameter_mm: float = 9.85
    m12_tensile_stress_area_mm2: float = 84.3
    aluminium_6061_t6_yield_mpa: float = 276.0


P = Parameters()
SUPPORT_ANGLES_DEG = (90.0, 210.0, 330.0)
LOWER_CROSSBAR_Y_MM = (330.0, 75.0, -37.5, -330.0)
# The front perimeter crossbar is omitted because the A1 support crossbar is
# already close to the front edge and serves as the structural front member.
UPPER_CROSSBAR_Y_MM = (315.0, -157.5, -330.0)


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


def lower_pin_points():
    return tuple((x, y, P.lower_pin_z_mm) for x, y in support_points(P.lower_support_radius_mm))


def upper_pin_local_points():
    return tuple((x, y, 0.0) for x, y in support_points(P.upper_support_radius_mm))


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
        lower_pin_points(), upper_pin_local_points(), support_basis()
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
        jacobian = tuple(tuple(columns[col][row] for col in range(3)) for row in range(3))
        delta = _solve_linear_3x3(jacobian, tuple(-value for value in residual))
        values = [values[index] + delta[index] for index in range(3)]
    residual = _constraint_values(values, pitch_deg, roll_deg)
    return {
        "x_mm": values[0],
        "y_mm": values[1],
        "yaw_rad": values[2],
        "residual_mm": max(abs(value) for value in residual),
    }


def upper_pin_points(pitch_deg, roll_deg):
    solved = solve_platform(pitch_deg, roll_deg)
    rotation = rotation_matrix(pitch_deg, roll_deg, solved["yaw_rad"])
    rows = []
    for local in upper_pin_local_points():
        moved = _matvec(rotation, local)
        rows.append(
            (
                moved[0] + solved["x_mm"],
                moved[1] + solved["y_mm"],
                moved[2] + P.upper_pin_z_mm,
            )
        )
    return tuple(rows)


def pin_lengths(pitch_deg, roll_deg):
    return tuple(
        sqrt(sum((upper[axis] - lower[axis]) ** 2 for axis in range(3)))
        for lower, upper in zip(lower_pin_points(), upper_pin_points(pitch_deg, roll_deg))
    )


def fixed_end_allowance_mm():
    lower = P.bj761_eye_center_to_thread_tip_mm + P.lower_coupling_internal_gap_mm
    upper = P.upper_rod_end_center_to_thread_end_mm - P.upper_stb_external_engagement_mm
    return lower + upper


def adjustable_pin_range_mm():
    minimum = P.stb_min_tip_span_mm + fixed_end_allowance_mm()
    maximum = minimum + 2.0 * (
        P.sjn_thread_length_each_end_mm - P.required_internal_engagement_mm
    )
    return minimum, maximum


def setting_for_length(length_mm):
    minimum, maximum = adjustable_pin_range_mm()
    if length_mm < minimum - 1e-9 or length_mm > maximum + 1e-9:
        raise ValueError(f"Length {length_mm:.3f} mm is outside Rev M2 range")
    tip_span = length_mm - fixed_end_allowance_mm()
    total_extension = tip_span - P.stb_min_tip_span_mm
    return {
        "turnbuckle_tip_span_mm": tip_span,
        "internal_engagement_each_end_mm": (
            P.sjn_thread_length_each_end_mm - total_extension / 2.0
        ),
        "turns_from_stb_minimum": total_extension / (2.0 * P.thread_pitch_mm),
    }


def workspace_audit():
    rows = []
    for pitch_deg, roll_deg in product(
        (-P.angle_deg, 0.0, P.angle_deg), repeat=2
    ):
        solved = solve_platform(pitch_deg, roll_deg)
        lengths = pin_lengths(pitch_deg, roll_deg)
        rows.append(
            {
                "pitch_deg": pitch_deg,
                "roll_deg": roll_deg,
                **solved,
                "pin_lengths_mm": lengths,
                "settings": tuple(setting_for_length(value) for value in lengths),
            }
        )
    required_minimum = min(min(row["pin_lengths_mm"]) for row in rows)
    required_maximum = max(max(row["pin_lengths_mm"]) for row in rows)
    available_minimum, available_maximum = adjustable_pin_range_mm()
    minimum_engagement = min(
        setting["internal_engagement_each_end_mm"]
        for row in rows
        for setting in row["settings"]
    )
    return {
        "parameters": asdict(P),
        "pose_count": len(rows),
        "required_minimum_pin_mm": required_minimum,
        "required_maximum_pin_mm": required_maximum,
        "required_adjustment_mm": required_maximum - required_minimum,
        "available_minimum_pin_mm": available_minimum,
        "available_maximum_pin_mm": available_maximum,
        "lower_length_margin_mm": required_minimum - available_minimum,
        "upper_length_margin_mm": available_maximum - required_maximum,
        "minimum_internal_engagement_mm": minimum_engagement,
        "maximum_constraint_residual_mm": max(row["residual_mm"] for row in rows),
        "passes": (
            required_minimum >= available_minimum
            and required_maximum <= available_maximum
            and minimum_engagement >= P.required_internal_engagement_mm
        ),
        "rows": rows,
    }


def strength_audit():
    diameter = P.m12_conservative_minor_diameter_mm
    area_moment_mm4 = pi * diameter**4 / 64.0
    critical_buckling_n = (
        pi**2
        * P.steel_elastic_modulus_mpa
        * area_moment_mm4
        / workspace_audit()["required_maximum_pin_mm"] ** 2
    )
    thread_stress_mpa = P.design_leg_load_n / P.m12_tensile_stress_area_mm2
    plate_span_mm = P.adapter_hole_pitch_mm
    plate_section_modulus_mm3 = (
        P.adapter_width_mm * P.adapter_thickness_mm**2 / 6.0
    )
    plate_stress_mpa = (
        P.design_leg_load_n * plate_span_mm / 4.0 / plate_section_modulus_mm3
    )
    return {
        "design_leg_load_n": P.design_leg_load_n,
        "conservative_m12_euler_buckling_n": critical_buckling_n,
        "buckling_factor": critical_buckling_n / P.design_leg_load_n,
        "m12_direct_thread_stress_mpa": thread_stress_mpa,
        "five_mm_adapter_plate_bending_stress_mpa": plate_stress_mpa,
        "adapter_plate_yield_factor": P.aluminium_6061_t6_yield_mpa / plate_stress_mpa,
        "passes_preliminary_screen": (
            critical_buckling_n / P.design_leg_load_n >= 3.0
            and P.aluminium_6061_t6_yield_mpa / plate_stress_mpa >= 3.0
        ),
        "limitations": (
            "Turnbuckle and hinge-support compression capacity is not published; "
            "supplier confirmation and a one-leg proof test remain mandatory."
        ),
    }


if __name__ == "__main__":
    import json

    print(json.dumps({"workspace": workspace_audit(), "strength": strength_audit()}, indent=2))
