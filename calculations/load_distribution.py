from itertools import product

import numpy as np

from cad.assembly import actuator_lengths
from cad.common import platform_center_z, transform_point
from cad.parameters import P, Pose


PAYLOAD_SWEEP_KG = (5.0, 10.0)
CART_MASS_SWEEP_KG = (10.0,)
MOVING_STRUCTURE_MASS_SWEEP_KG = (15.0, 22.0)
DESIGN_FACTOR_SWEEP = (1.5, 2.0)
ECCENTRICITY_SWEEP_MM = (0.0, 50.0, 100.0)

ARCHIVED_PAYLOAD_SWEEP_KG = (5.0, 10.0, 20.0)
ARCHIVED_CART_MASS_SWEEP_KG = (10.0, 20.0, 30.0)
ARCHIVED_MOVING_STRUCTURE_MASS_SWEEP_KG = (22.0, 30.0, 40.0)
ARCHIVED_DESIGN_FACTOR_SWEEP = (1.5, 2.0, 2.5)


def support_reactions(total_mass_kg, cg_x_mm, cg_y_mm, design_factor):
    matrix = np.array([
        [1.0, 1.0, 1.0],
        [point[0] for point in P.support_points_xy],
        [point[1] for point in P.support_points_xy],
    ])
    design_weight = total_mass_kg * P.gravity_m_s2 * design_factor
    rhs = np.array([design_weight, design_weight * cg_x_mm, design_weight * cg_y_mm])
    return np.linalg.solve(matrix, rhs)


def actuator_vertical_cosines(pose):
    platform_z = platform_center_z(pose)
    lengths = actuator_lengths(pose)
    cosines = []
    for (top_x, top_y), (_, _), length in zip(P.support_points_xy, P.base_points_xy, lengths):
        top = transform_point((top_x, top_y, 0.0), pose, platform_z)
        cosines.append(abs((top.z - P.base_joint_z_mm) / length))
    return cosines


def worst_case(angle_deg=3.0,
               design_factor=2.0,
               max_eccentricity_mm=50.0,
               payload_cases_kg=PAYLOAD_SWEEP_KG,
               cart_mass_cases_kg=CART_MASS_SWEEP_KG,
               moving_structure_mass_cases_kg=MOVING_STRUCTURE_MASS_SWEEP_KG):
    poses = [
        Pose(lift, pitch, roll, True, "sweep")
        for lift, pitch, roll in product((0.0, 50.0, 75.0, 100.0), (-angle_deg, 0.0, angle_deg), (-angle_deg, 0.0, angle_deg))
    ]
    eccentricities = (0.0, max_eccentricity_mm)
    worst = None
    for payload, cart, moving_structure, cg_x, cg_y, pose in product(
        payload_cases_kg,
        cart_mass_cases_kg,
        moving_structure_mass_cases_kg,
        eccentricities,
        eccentricities,
        poses,
    ):
        total_mass = payload + cart + moving_structure
        reactions = support_reactions(total_mass, cg_x, cg_y, design_factor)
        cosines = actuator_vertical_cosines(pose)
        axial_forces = [reaction / cosine for reaction, cosine in zip(reactions, cosines)]
        row = {
            "max_axial_force_n": float(max(axial_forces)),
            "min_vertical_reaction_n": float(min(reactions)),
            "material_payload_kg": payload,
            "cart_mass_kg": cart,
            "moving_structure_mass_kg": moving_structure,
            "total_moving_mass_kg": total_mass,
            "design_factor": design_factor,
            "cg_x_mm": cg_x,
            "cg_y_mm": cg_y,
            "lift_mm": pose.lift_mm,
            "pitch_deg": pose.pitch_deg,
            "roll_deg": pose.roll_deg,
            "minimum_vertical_cosine": float(min(cosines)),
            "passes_firgelli_450_lbf": float(max(axial_forces)) <= P.actuator_dynamic_force_n,
        }
        if worst is None or row["max_axial_force_n"] > worst["max_axial_force_n"]:
            worst = row
    return worst


def archived_heavy_worst_case(angle_deg=3.0, design_factor=2.0, max_eccentricity_mm=50.0):
    return worst_case(
        angle_deg=angle_deg,
        design_factor=design_factor,
        max_eccentricity_mm=max_eccentricity_mm,
        payload_cases_kg=ARCHIVED_PAYLOAD_SWEEP_KG,
        cart_mass_cases_kg=ARCHIVED_CART_MASS_SWEEP_KG,
        moving_structure_mass_cases_kg=ARCHIVED_MOVING_STRUCTURE_MASS_SWEEP_KG,
    )


def design_sweep_summary():
    rows = []
    for angle, factor, ecc in product((3.0, 5.0, 8.0), DESIGN_FACTOR_SWEEP, (50.0, 100.0)):
        rows.append(worst_case(angle, factor, ecc))
    return rows


def archived_heavy_design_sweep_summary():
    rows = []
    for angle, factor, ecc in product((3.0, 5.0, 8.0), ARCHIVED_DESIGN_FACTOR_SWEEP, (50.0, 100.0)):
        rows.append(archived_heavy_worst_case(angle, factor, ecc))
    return rows


def main():
    print({"basis": "active low-load user-confirmed sweep"})
    for row in design_sweep_summary():
        print(row)
    print({"basis": "archived heavy sensitivity sweep", "worst_rows_only": True})
    for row in archived_heavy_design_sweep_summary():
        print(row)


if __name__ == "__main__":
    main()
