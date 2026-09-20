"""Static self-standing and constraint audit for Manual 3-RPS Rev M2.

This module distinguishes a fully assembled, locked platform from an
incomplete assembly and from whole-unit resistance to external tipping.
The gravity calculation is a preliminary vertical-reaction screen, not an
FEA result or a certification claim.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import atan, cos, degrees, pi, radians, sin, sqrt

import numpy as np

from calculations.manual_turnbuckle_rev_m2_screen import (
    P,
    SUPPORT_ANGLES_DEG,
    lower_pin_points,
    pin_lengths,
    solve_platform,
    support_basis,
    upper_pin_local_points,
    upper_pin_points,
)


@dataclass(frozen=True)
class StabilityParameters:
    total_supported_mass_kg: float = 20.0
    gravity_m_s2: float = 9.80665
    cg_offset_radius_mm: float = 150.0
    pose_step_deg: float = 0.5
    load_direction_step_deg: float = 5.0
    jacobian_step_mm: float = 1e-4
    rank_tolerance: float = 1e-8
    # ISO metric basic pitch diameter: d2 = d - 0.64951905 * pitch.
    metric_pitch_diameter_factor: float = 0.64951905
    nominal_base_half_width_mm: float = 350.0
    illustrative_cg_height_mm: float = 300.0


S = StabilityParameters()


def _scan_values(limit_deg: float, step_deg: float):
    count = int(round(2.0 * limit_deg / step_deg))
    return tuple(-limit_deg + index * step_deg for index in range(count + 1))


def _rotation_radians(roll_rad: float, pitch_rad: float, yaw_rad: float):
    rx = np.array(
        (
            (1.0, 0.0, 0.0),
            (0.0, cos(roll_rad), -sin(roll_rad)),
            (0.0, sin(roll_rad), cos(roll_rad)),
        )
    )
    ry = np.array(
        (
            (cos(pitch_rad), 0.0, sin(pitch_rad)),
            (0.0, 1.0, 0.0),
            (-sin(pitch_rad), 0.0, cos(pitch_rad)),
        )
    )
    rz = np.array(
        (
            (cos(yaw_rad), -sin(yaw_rad), 0.0),
            (sin(yaw_rad), cos(yaw_rad), 0.0),
            (0.0, 0.0, 1.0),
        )
    )
    return rz @ ry @ rx


def _base_generalized_pose(pitch_deg: float, roll_deg: float):
    solved = solve_platform(pitch_deg, roll_deg)
    radius = P.upper_support_radius_mm
    return np.array(
        (
            solved["x_mm"],
            solved["y_mm"],
            P.upper_pin_z_mm,
            radians(roll_deg) * radius,
            radians(pitch_deg) * radius,
            solved["yaw_rad"] * radius,
        ),
        dtype=float,
    )


def _constraint_residual(generalized_pose, target_lengths_mm):
    radius = P.upper_support_radius_mm
    x_mm, y_mm, z_mm, roll_scaled, pitch_scaled, yaw_scaled = generalized_pose
    rotation = _rotation_radians(
        roll_scaled / radius,
        pitch_scaled / radius,
        yaw_scaled / radius,
    )
    translation = np.array((x_mm, y_mm, z_mm), dtype=float)
    lower_points = np.array(lower_pin_points(), dtype=float)
    local_points = np.array(upper_pin_local_points(), dtype=float)
    tangents = np.array([tangent for _, tangent in support_basis()], dtype=float)
    upper_points = np.array([translation + rotation @ point for point in local_points])
    link_vectors = upper_points - lower_points
    tangent_residuals = np.sum(link_vectors * tangents, axis=1)
    length_residuals = np.linalg.norm(link_vectors, axis=1) - np.asarray(target_lengths_mm)
    return np.concatenate((tangent_residuals, length_residuals))


def constraint_jacobian(pitch_deg: float, roll_deg: float):
    baseline = _base_generalized_pose(pitch_deg, roll_deg)
    target_lengths = pin_lengths(pitch_deg, roll_deg)
    step = S.jacobian_step_mm
    columns = []
    for axis in range(6):
        forward = baseline.copy()
        reverse = baseline.copy()
        forward[axis] += step
        reverse[axis] -= step
        columns.append(
            (
                _constraint_residual(forward, target_lengths)
                - _constraint_residual(reverse, target_lengths)
            )
            / (2.0 * step)
        )
    return np.column_stack(columns)


def constraint_rank_audit():
    rows = []
    minimum_singular_value = float("inf")
    maximum_condition_number = 0.0
    worst_pose = None
    minimum_rank = 6
    scan = _scan_values(P.angle_deg, S.pose_step_deg)
    for pitch_deg in scan:
        for roll_deg in scan:
            singular_values = np.linalg.svd(
                constraint_jacobian(pitch_deg, roll_deg), compute_uv=False
            )
            rank = int(np.sum(singular_values > S.rank_tolerance))
            condition = float(singular_values[0] / singular_values[-1])
            row = {
                "pitch_deg": pitch_deg,
                "roll_deg": roll_deg,
                "rank": rank,
                "minimum_singular_value": float(singular_values[-1]),
                "condition_number": condition,
            }
            rows.append(row)
            minimum_rank = min(minimum_rank, rank)
            if singular_values[-1] < minimum_singular_value:
                minimum_singular_value = float(singular_values[-1])
                worst_pose = dict(row)
            maximum_condition_number = max(maximum_condition_number, condition)

    neutral = constraint_jacobian(0.0, 0.0)
    two_leg_rows = neutral[[0, 1, 3, 4], :]
    spherical_both_ends_rows = neutral[[3, 4, 5], :]
    return {
        "pose_count": len(rows),
        "minimum_rank": minimum_rank,
        "required_rank": 6,
        "minimum_singular_value": minimum_singular_value,
        "maximum_condition_number": maximum_condition_number,
        "worst_pose": worst_pose,
        "neutral_three_locked_rps_rank": int(np.linalg.matrix_rank(neutral)),
        "neutral_two_rps_leg_rank": int(np.linalg.matrix_rank(two_leg_rows)),
        "neutral_three_sps_leg_rank": int(np.linalg.matrix_rank(spherical_both_ends_rows)),
        "passes": minimum_rank == 6 and minimum_singular_value > 0.35,
    }


def _point_to_segment_line_distance(point, first, second):
    edge = second - first
    offset = point - first
    cross_z = edge[0] * offset[1] - edge[1] * offset[0]
    return abs(float(cross_z)) / float(np.linalg.norm(edge))


def _projected_triangle_inradius(points_xy):
    center = np.mean(points_xy, axis=0)
    return min(
        _point_to_segment_line_distance(center, points_xy[index], points_xy[(index + 1) % 3])
        for index in range(3)
    )


def gravity_reaction_audit():
    weight_n = S.total_supported_mass_kg * S.gravity_m_s2
    lower_points = np.array(lower_pin_points(), dtype=float)
    minimum_reaction_n = float("inf")
    maximum_reaction_n = 0.0
    maximum_equivalent_axial_n = 0.0
    minimum_projected_inradius_mm = float("inf")
    minimum_case = None
    maximum_case = None
    axial_case = None
    pose_values = _scan_values(P.angle_deg, S.pose_step_deg)
    direction_values = tuple(
        index * S.load_direction_step_deg
        for index in range(int(round(360.0 / S.load_direction_step_deg)))
    )

    for pitch_deg in pose_values:
        for roll_deg in pose_values:
            upper_points = np.array(upper_pin_points(pitch_deg, roll_deg), dtype=float)
            points_xy = upper_points[:, :2]
            center_xy = np.mean(points_xy, axis=0)
            minimum_projected_inradius_mm = min(
                minimum_projected_inradius_mm,
                _projected_triangle_inradius(points_xy),
            )
            equilibrium = np.vstack((points_xy[:, 0], points_xy[:, 1], np.ones(3)))
            for direction_deg in direction_values:
                direction = radians(direction_deg)
                cg_xy = center_xy + S.cg_offset_radius_mm * np.array(
                    (cos(direction), sin(direction))
                )
                reactions = np.linalg.solve(
                    equilibrium,
                    np.array((weight_n * cg_xy[0], weight_n * cg_xy[1], weight_n)),
                )
                for leg_index, reaction_n in enumerate(reactions):
                    reaction_n = float(reaction_n)
                    case = {
                        "pitch_deg": pitch_deg,
                        "roll_deg": roll_deg,
                        "cg_direction_deg": direction_deg,
                        "leg_index": leg_index + 1,
                    }
                    if reaction_n < minimum_reaction_n:
                        minimum_reaction_n = reaction_n
                        minimum_case = {**case, "reaction_n": reaction_n}
                    if reaction_n > maximum_reaction_n:
                        maximum_reaction_n = reaction_n
                        maximum_case = {**case, "reaction_n": reaction_n}
                    link_vector = upper_points[leg_index] - lower_points[leg_index]
                    vertical_cosine = float(link_vector[2] / np.linalg.norm(link_vector))
                    equivalent_axial_n = reaction_n / vertical_cosine
                    if equivalent_axial_n > maximum_equivalent_axial_n:
                        maximum_equivalent_axial_n = equivalent_axial_n
                        axial_case = {
                            **case,
                            "reaction_n": reaction_n,
                            "link_vertical_cosine": vertical_cosine,
                            "equivalent_axial_n": equivalent_axial_n,
                        }

    return {
        "method": "vertical reaction distribution on projected upper support triangle",
        "pose_count": len(pose_values) ** 2,
        "load_direction_count_per_pose": len(direction_values),
        "case_count": len(pose_values) ** 2 * len(direction_values),
        "supported_mass_kg": S.total_supported_mass_kg,
        "weight_n": weight_n,
        "cg_offset_radius_mm": S.cg_offset_radius_mm,
        "nominal_support_triangle_inradius_mm": P.upper_support_radius_mm / 2.0,
        "minimum_projected_inradius_mm": minimum_projected_inradius_mm,
        "minimum_reaction_n": minimum_reaction_n,
        "minimum_reaction_case": minimum_case,
        "maximum_reaction_n": maximum_reaction_n,
        "maximum_reaction_case": maximum_case,
        "maximum_equivalent_axial_n": maximum_equivalent_axial_n,
        "maximum_equivalent_axial_case": axial_case,
        "design_leg_load_n": P.design_leg_load_n,
        "axial_load_factor": P.design_leg_load_n / maximum_equivalent_axial_n,
        "all_reactions_compressive": minimum_reaction_n > 0.0,
        "passes": (
            minimum_reaction_n > 0.0
            and S.cg_offset_radius_mm < minimum_projected_inradius_mm
            and maximum_equivalent_axial_n < P.design_leg_load_n
        ),
        "limitations": [
            "Vertical-reaction screen only; joint friction, frame flexibility, and dynamic shock are excluded.",
            "The 150 mm horizontal CG offset is an engineering assumption pending measured CG data.",
        ],
    }


def thread_lock_audit():
    pitch_diameter_mm = P.thread_nominal_mm - S.metric_pitch_diameter_factor * P.thread_pitch_mm
    lead_angle_rad = atan(P.thread_pitch_mm / (pi * pitch_diameter_mm))
    return {
        "thread": f"M{P.thread_nominal_mm:g}x{P.thread_pitch_mm:g}",
        "basic_pitch_diameter_mm": pitch_diameter_mm,
        "lead_angle_deg": degrees(lead_angle_rad),
        "minimum_friction_coefficient_for_ideal_self_lock": float(np.tan(lead_angle_rad)),
        "length_change_per_turn_mm": 2.0 * P.thread_pitch_mm,
        "supplier_self_lock_rating_published": False,
        "jam_nuts_required": True,
        "may_rely_on_thread_friction_alone": False,
        "stb_supplied_sjn_lock_nuts_per_leg": 2,
        "additional_external_jam_nuts_per_leg": 3,
        "total_lock_nuts_per_leg": 5,
        "external_interfaces": [
            "BJ761-to-coupling M12x1.75 RH",
            "coupling-to-STB M12x1.75 RH",
            "STB-to-PHS12L M12x1.75 LH",
        ],
        "catalog_configuration": "Retain both STB-supplied SJN lock nuts and add one jam nut at each external female-thread interface.",
        "passes_with_jam_nuts": True,
    }


def illustrative_tipover_audit():
    weight_n = S.total_supported_mass_kg * S.gravity_m_s2
    centered_force_n = (
        weight_n * S.nominal_base_half_width_mm / S.illustrative_cg_height_mm
    )
    offset_margin_mm = S.nominal_base_half_width_mm - S.cg_offset_radius_mm
    offset_force_n = weight_n * offset_margin_mm / S.illustrative_cg_height_mm
    return {
        "calculation_status": "illustrative_not_verified",
        "assumed_effective_half_base_mm": S.nominal_base_half_width_mm,
        "assumed_cg_height_mm": S.illustrative_cg_height_mm,
        "gravity_projection_margin_at_150mm_offset_mm": offset_margin_mm,
        "illustrative_centered_lateral_tip_force_n": centered_force_n,
        "illustrative_150mm_offset_lateral_tip_force_n": offset_force_n,
        "whole_unit_external_tip_resistance_verified": False,
        "open_inputs": [
            "actual lower contact or cart-coupling polygon",
            "measured complete-module mass and CG",
            "required lateral disturbance and dynamic load case",
        ],
    }


def self_standing_audit():
    constraint = constraint_rank_audit()
    gravity = gravity_reaction_audit()
    thread = thread_lock_audit()
    tipover = illustrative_tipover_audit()
    locked_static_pass = (
        constraint["passes"]
        and gravity["passes"]
        and thread["passes_with_jam_nuts"]
    )
    return {
        "parameters": asdict(S),
        "constraint": constraint,
        "gravity": gravity,
        "thread_lock": thread,
        "tipover": tipover,
        "fully_assembled_three_leg_platform_self_stands_under_screened_gravity": locked_static_pass,
        "central_post_required_after_all_three_links_are_locked": False,
        "temporary_support_required_during_assembly_or_loaded_adjustment": True,
        "two_leg_incomplete_assembly_self_standing": False,
        "whole_unanchored_unit_against_external_lateral_load_verified": False,
        "pass": locked_static_pass,
    }


if __name__ == "__main__":
    import json

    print(json.dumps(self_standing_audit(), ensure_ascii=False, indent=2))
