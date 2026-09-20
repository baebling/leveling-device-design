import itertools

import numpy as np

from cad.assembly import actuator_lengths
from cad.common import platform_center_z, transform_point
from cad.parameters import P, Pose
from calculations.kinematics import pose_grid


def vertical_reactions(total_mass_kg, cg_x_mm=0.0, cg_y_mm=0.0, dynamic_factor=1.0, safety_factor=1.0):
    points = P.support_points_xy
    matrix = np.array([
        [1.0, 1.0, 1.0],
        [p[0] for p in points],
        [p[1] for p in points],
    ])
    weight = total_mass_kg * P.gravity_m_s2 * dynamic_factor * safety_factor
    rhs = np.array([weight, weight * cg_x_mm, weight * cg_y_mm])
    return tuple(float(v) for v in np.linalg.solve(matrix, rhs))


def design_cases():
    rows = []
    for payload, structure in itertools.product(
        P.payload_cases_kg,
        P.moving_structure_mass_range_kg,
    ):
        reactions = vertical_reactions(payload + structure, 0.0, 0.0, dynamic_factor=1.5, safety_factor=P.preliminary_safety_factor)
        for pose in pose_grid(P.recommended_angle_deg):
            lengths = actuator_lengths(pose)
            platform_z = platform_center_z(pose)
            cosines = []
            for ((x, y), (bx, by), length) in zip(P.support_points_xy, P.base_points_xy, lengths):
                top = transform_point((x, y, 0.0), pose, platform_z)
                cosines.append(abs((top.z - P.base_joint_z_mm) / length))
            axial = tuple(reaction / cosine for reaction, cosine in zip(reactions, cosines))
            rows.append({
                "payload_kg": payload, "structure_kg": structure, "cg_x_mm": 0.0, "cg_y_mm": 0.0,
                "lift_mm": pose.lift_mm, "pitch_deg": pose.pitch_deg, "roll_deg": pose.roll_deg,
                "a1_n": axial[0], "a2_n": axial[1], "a3_n": axial[2],
                "max_compression_n": max(axial), "min_reaction_n": min(axial),
                "minimum_vertical_direction_cosine": min(cosines),
            })
    return rows


def eccentricity_sensitivity(total_mass_kg=32.0):
    rows = []
    for eccentricity in P.eccentricity_sensitivity_mm:
        points = ((0.0, 0.0),) if eccentricity == 0 else (
            (eccentricity, 0.0), (0.0, eccentricity), (eccentricity, eccentricity)
        )
        for x, y in points:
            reactions = vertical_reactions(total_mass_kg, x, y, dynamic_factor=1.5, safety_factor=P.preliminary_safety_factor)
            level_cosine = P.actuator_vertical_separation_collapsed_mm / P.actuator_level_length_at_lift0_mm
            rows.append({
                "cg_x_mm": x, "cg_y_mm": y,
                "vertical_reactions_n": reactions,
                "estimated_axial_forces_n": tuple(v / level_cosine for v in reactions),
            })
    return rows


def summary():
    rows = design_cases()
    worst = max(rows, key=lambda row: row["max_compression_n"])
    minimum = min(rows, key=lambda row: row["min_reaction_n"])
    return {
        "worst_case": worst,
        "minimum_reaction_case": minimum,
        "selected_dynamic_rating_n": P.actuator_dynamic_force_n,
        "rating_margin_n": P.actuator_dynamic_force_n - worst["max_compression_n"],
        "maximum_required_tension_n": abs(min(0.0, minimum["min_reaction_n"])),
        "passes_preliminary_force_check": worst["max_compression_n"] <= P.actuator_dynamic_force_n,
        "eccentricity_sensitivity": eccentricity_sensitivity(),
        "note": "Inclination is included through each actuator's vertical direction cosine. The central keyed guide reacts the balanced lateral components. Pin, bracket, buckling and transient FEA remain required before fabrication.",
    }
