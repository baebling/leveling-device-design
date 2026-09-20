from itertools import product
from math import radians, tan

from cad.parameters import P


PAYLOAD_SWEEP_KG = (5.0, 10.0)
CART_MASS_SWEEP_KG = (10.0,)
MOVING_STRUCTURE_MASS_SWEEP_KG = (15.0, 22.0)
CG_OFFSET_SWEEP_MM = (0.0, 50.0, 100.0)
PAYLOAD_CG_HEIGHT_SWEEP_MM = (0.0, 300.0, 600.0)
ANGLE_SWEEP_DEG = (3.0,)
DESIGN_FACTOR_SWEEP = (1.5, 2.0)

ARCHIVED_PAYLOAD_SWEEP_KG = (5.0, 10.0, 20.0)
ARCHIVED_CART_MASS_SWEEP_KG = (10.0, 20.0, 30.0)
ARCHIVED_MOVING_STRUCTURE_MASS_SWEEP_KG = (22.0, 30.0, 40.0)
ARCHIVED_ANGLE_SWEEP_DEG = (3.0, 5.0, 8.0)
ARCHIVED_DESIGN_FACTOR_SWEEP = (2.0, 2.5)


def interface_loads(payload_kg=10.0, cart_mass_kg=10.0, upper_structure_mass_kg=22.0,
                    cg_x_mm=50.0, cg_y_mm=50.0, cg_height_mm=None, tilt_deg=3.0, design_factor=1.5):
    """Preliminary lower interface load transfer. Does not certify overturning stability."""
    if cg_height_mm is None:
        cg_height_mm = 0.0
    total_mass_kg = payload_kg + cart_mass_kg + upper_structure_mass_kg
    design_weight_n = total_mass_kg * P.gravity_m_s2 * design_factor
    pitch_moment_nm = design_weight_n * (cg_x_mm + cg_height_mm * tan(radians(tilt_deg))) / 1000.0
    roll_moment_nm = design_weight_n * (cg_y_mm + cg_height_mm * tan(radians(tilt_deg))) / 1000.0
    return {
        "material_payload_kg": payload_kg,
        "cart_mass_kg": cart_mass_kg,
        "upper_structure_mass_kg": upper_structure_mass_kg,
        "total_mass_kg": total_mass_kg,
        "design_factor": design_factor,
        "cg_x_mm": cg_x_mm,
        "cg_y_mm": cg_y_mm,
        "cg_height_mm": cg_height_mm,
        "tilt_deg": tilt_deg,
        "maximum_vertical_interface_load_n": design_weight_n,
        "maximum_pitch_interface_moment_nm": pitch_moment_nm,
        "maximum_roll_interface_moment_nm": roll_moment_nm,
        "support_polygon_note": "TBD after lower mobile-base support polygon is provided; do not infer it from images.",
    }


def worst_case(payload_cases_kg=PAYLOAD_SWEEP_KG,
               cart_mass_cases_kg=CART_MASS_SWEEP_KG,
               moving_structure_mass_cases_kg=MOVING_STRUCTURE_MASS_SWEEP_KG,
               angle_cases_deg=ANGLE_SWEEP_DEG,
               design_factor_cases=DESIGN_FACTOR_SWEEP):
    rows = []
    for payload, cart, moving_structure, cg_x, cg_y, cg_height, tilt, factor in product(
        payload_cases_kg,
        cart_mass_cases_kg,
        moving_structure_mass_cases_kg,
        CG_OFFSET_SWEEP_MM,
        CG_OFFSET_SWEEP_MM,
        PAYLOAD_CG_HEIGHT_SWEEP_MM,
        angle_cases_deg,
        design_factor_cases,
    ):
        rows.append(interface_loads(payload, cart, moving_structure, cg_x, cg_y, cg_height, tilt, factor))
    return max(rows, key=lambda row: max(abs(row["maximum_pitch_interface_moment_nm"]),
                                        abs(row["maximum_roll_interface_moment_nm"])))


def archived_heavy_worst_case():
    return worst_case(
        payload_cases_kg=ARCHIVED_PAYLOAD_SWEEP_KG,
        cart_mass_cases_kg=ARCHIVED_CART_MASS_SWEEP_KG,
        moving_structure_mass_cases_kg=ARCHIVED_MOVING_STRUCTURE_MASS_SWEEP_KG,
        angle_cases_deg=ARCHIVED_ANGLE_SWEEP_DEG,
        design_factor_cases=ARCHIVED_DESIGN_FACTOR_SWEEP,
    )


if __name__ == "__main__":
    print({"basis": "active low-load user-confirmed interface case"})
    print(interface_loads())
    print({"basis": "active low-load worst interface moment"})
    print(worst_case())
    print({"basis": "archived heavy sensitivity worst interface moment"})
    print(archived_heavy_worst_case())
