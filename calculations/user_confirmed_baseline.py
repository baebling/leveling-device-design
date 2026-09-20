"""User-confirmed low-load Phase 0 baseline screen.

This script reflects the 2026-08-25 user decision:
- carried material payload: 10 kg
- expected empty cart mass: about 10 kg, and the cart can be designed around
  the leveling device
- required leveling: +/-3 deg pitch/roll only
- disconnected leveling-device height envelope: 250 to 300 mm
- prioritize simple fabrication, assembly, and PoC demonstration

It does not replace the older conservative sensitivity screens; it adds a
lighter review baseline for deciding the next concept direction.
"""

from itertools import product
from math import hypot
from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("XDG_CACHE_HOME", str(ROOT / ".cache"))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplcache"))
for path in (ROOT,):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from cad.parameters import P, Pose
from calculations.load_distribution import actuator_vertical_cosines, support_reactions


USER_CONFIRMED_PAYLOAD_KG = 10.0
USER_CONFIRMED_EMPTY_CART_MASS_KG = 10.0
USER_CONFIRMED_ANGLE_DEG = 3.0
USER_CONFIRMED_DEVICE_HEIGHT_MIN_MM = 250.0
USER_CONFIRMED_DEVICE_HEIGHT_MAX_MM = 300.0
POC_BASELINE_DESIGN_FACTOR = 1.5
POC_SENSITIVITY_DESIGN_FACTOR = 2.0
POC_BASELINE_ECCENTRICITY_MM = 50.0
POC_SENSITIVITY_ECCENTRICITY_MM = 100.0
POC_BASELINE_HORIZONTAL_ACCEL_G = 0.25
POC_SENSITIVITY_HORIZONTAL_ACCEL_G = 0.5
POC_BASELINE_TORQUE_SCREEN_FACTOR = 1.5
POC_SENSITIVITY_TORQUE_SCREEN_FACTOR = 2.0


def _poses(angle_deg=USER_CONFIRMED_ANGLE_DEG):
    return [
        Pose(lift, pitch, roll, True, "user_confirmed_baseline")
        for lift, pitch, roll in product(
            (0.0, 50.0, 100.0),
            (-angle_deg, 0.0, angle_deg),
            (-angle_deg, 0.0, angle_deg),
        )
    ]


def actuator_force_screen(design_factor=POC_BASELINE_DESIGN_FACTOR,
                          max_eccentricity_mm=POC_BASELINE_ECCENTRICITY_MM,
                          payload_kg=USER_CONFIRMED_PAYLOAD_KG,
                          angle_deg=USER_CONFIRMED_ANGLE_DEG,
                          cart_mass_cases_kg=(USER_CONFIRMED_EMPTY_CART_MASS_KG,)):
    eccentricities = (0.0, max_eccentricity_mm)
    worst = None
    for cart, moving_structure, cg_x, cg_y, pose in product(
        cart_mass_cases_kg,
        P.moving_structure_mass_range_kg,
        eccentricities,
        eccentricities,
        _poses(angle_deg),
    ):
        total_mass = payload_kg + cart + moving_structure
        reactions = support_reactions(total_mass, cg_x, cg_y, design_factor)
        cosines = actuator_vertical_cosines(pose)
        axial_forces = [reaction / cosine for reaction, cosine in zip(reactions, cosines)]
        row = {
            "material_payload_kg": payload_kg,
            "cart_mass_kg": cart,
            "moving_structure_mass_kg": moving_structure,
            "total_lifted_mass_kg": total_mass,
            "angle_deg": angle_deg,
            "design_factor": design_factor,
            "max_eccentricity_mm": max_eccentricity_mm,
            "cg_x_mm": cg_x,
            "cg_y_mm": cg_y,
            "lift_mm": pose.lift_mm,
            "pitch_deg": pose.pitch_deg,
            "roll_deg": pose.roll_deg,
            "max_axial_force_n": float(max(axial_forces)),
            "min_vertical_reaction_n": float(min(reactions)),
            "minimum_vertical_cosine": float(min(cosines)),
            "actuator_dynamic_force_n": P.actuator_dynamic_force_n,
            "force_margin_to_firgelli": P.actuator_dynamic_force_n / float(max(axial_forces)),
            "passes_firgelli_450_lbf": float(max(axial_forces)) <= P.actuator_dynamic_force_n,
        }
        if worst is None or row["max_axial_force_n"] > worst["max_axial_force_n"]:
            worst = row
    return worst


def central_yaw_screen(design_factor=POC_BASELINE_DESIGN_FACTOR,
                       max_eccentricity_mm=POC_BASELINE_ECCENTRICITY_MM,
                       horizontal_accel_g=POC_BASELINE_HORIZONTAL_ACCEL_G,
                       torque_screen_factor=POC_BASELINE_TORQUE_SCREEN_FACTOR,
                       payload_kg=USER_CONFIRMED_PAYLOAD_KG,
                       cart_mass_kg=USER_CONFIRMED_EMPTY_CART_MASS_KG):
    total_mass = payload_kg + cart_mass_kg + max(P.moving_structure_mass_range_kg)
    cg_radius_m = hypot(max_eccentricity_mm, max_eccentricity_mm) / 1000.0
    yaw_torque_nm = (
        total_mass
        * P.gravity_m_s2
        * horizontal_accel_g
        * design_factor
        * cg_radius_m
    )
    return {
        "material_payload_kg": payload_kg,
        "cart_mass_kg": cart_mass_kg,
        "moving_structure_mass_kg": max(P.moving_structure_mass_range_kg),
        "total_lifted_mass_kg": total_mass,
        "horizontal_accel_g": horizontal_accel_g,
        "design_factor": design_factor,
        "cg_x_mm": max_eccentricity_mm,
        "cg_y_mm": max_eccentricity_mm,
        "yaw_torque_nm": yaw_torque_nm,
        "torque_screen_factor": torque_screen_factor,
        "required_design_yaw_torque_nm": yaw_torque_nm * torque_screen_factor,
    }


def summary():
    return {
        "user_decision": {
            "material_payload_kg": USER_CONFIRMED_PAYLOAD_KG,
            "empty_cart_mass_kg": USER_CONFIRMED_EMPTY_CART_MASS_KG,
            "pitch_roll_required_deg": USER_CONFIRMED_ANGLE_DEG,
            "disconnected_device_height_range_mm": (
                USER_CONFIRMED_DEVICE_HEIGHT_MIN_MM,
                USER_CONFIRMED_DEVICE_HEIGHT_MAX_MM,
            ),
            "cart_design_basis": "cart can be designed around the leveling device",
            "fabrication_priority": "simple machining, fabrication and assembly",
            "status": "user confirmed on 2026-08-25",
        },
        "baseline_actuator_force": actuator_force_screen(),
        "df2_actuator_force_sensitivity": actuator_force_screen(
            design_factor=POC_SENSITIVITY_DESIGN_FACTOR,
            max_eccentricity_mm=POC_BASELINE_ECCENTRICITY_MM,
        ),
        "ecc100_actuator_force_sensitivity": actuator_force_screen(
            design_factor=POC_BASELINE_DESIGN_FACTOR,
            max_eccentricity_mm=POC_SENSITIVITY_ECCENTRICITY_MM,
        ),
        "heavy_cart_actuator_force_sensitivity": actuator_force_screen(
            cart_mass_cases_kg=P.cart_mass_cases_kg,
        ),
        "baseline_yaw_torque": central_yaw_screen(),
        "conservative_yaw_torque_sensitivity": central_yaw_screen(
            design_factor=POC_SENSITIVITY_DESIGN_FACTOR,
            max_eccentricity_mm=POC_SENSITIVITY_ECCENTRICITY_MM,
            horizontal_accel_g=POC_SENSITIVITY_HORIZONTAL_ACCEL_G,
            torque_screen_factor=POC_SENSITIVITY_TORQUE_SCREEN_FACTOR,
            cart_mass_kg=max(P.cart_mass_cases_kg),
        ),
        "heavy_cart_yaw_torque_sensitivity": central_yaw_screen(
            cart_mass_kg=max(P.cart_mass_cases_kg),
        ),
        "approval_note": "Preliminary PoC sizing screen only; not approved for fabrication.",
    }


def main():
    for key, value in summary().items():
        print({key: value})


if __name__ == "__main__":
    main()
