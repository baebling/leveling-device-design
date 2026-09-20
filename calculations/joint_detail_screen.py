"""Preliminary joint packaging and torque screen.

This expands the Phase 0 joint candidate filter into first-order load-path
checks. It is intentionally conservative and still not a fabrication design.
"""

from math import pi, sqrt
from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("XDG_CACHE_HOME", str(ROOT / ".cache"))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplcache"))
for path in (ROOT,):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from cad.parameters import P
from calculations.joint_candidate_screen import ANGLE_MARGIN_DEG
from calculations.load_distribution import worst_case
from calculations.mobility_analysis import cardan_summary, joint_articulation_summary


ANGLE_CASES_DEG = (3.0, 5.0, 8.0)
DEFAULT_BRACKET_LUG_THICKNESS_MM = 8.0
DEFAULT_STUD_STANDOFF_MM = 10.0
PRELIM_ALLOWABLE_PIN_SHEAR_MPA = 100.0
PRELIM_ALLOWABLE_LUG_BEARING_MPA = 100.0
PRELIM_ALLOWABLE_STUD_BENDING_MPA = 150.0
CENTRAL_YAW_HORIZONTAL_ACCEL_G = 0.5
CENTRAL_YAW_DESIGN_FACTOR = 2.0
CENTRAL_YAW_TORQUE_SCREEN_FACTOR = 2.0
CENTRAL_YAW_CG_OFFSET_X_MM = 100.0
CENTRAL_YAW_CG_OFFSET_Y_MM = 100.0
CENTRAL_YAW_TOTAL_MASS_KG = 90.0
STEEL_SHEAR_MODULUS_MPA = 26000.0


ACTUATOR_JOINT_PACKAGES = (
    {
        "candidate": "Minebea_HRT8E_with_M8_pin",
        "source_id": "SRC-JNT-006",
        "catalog_axial_static_capacity_n": 5290.0,
        "catalog_radial_static_limit_n": 26770.0,
        "allowable_angle_deg": 14.0,
        "pin_diameter_mm": 8.0,
        "thread_root_diameter_mm": 6.5,
        "note": "Baseline +/-3 rod-end candidate; use axial, not radial, catalog limit and retain full 14 deg articulation after bracketing.",
    },
    {
        "candidate": "MISUMI_RBLD8_style_link_ball",
        "source_id": "SRC-JNT-004",
        "catalog_static_capacity_n": 12500.0,
        "allowable_angle_deg": 40.0,
        "pin_diameter_mm": 8.0,
        "thread_root_diameter_mm": 6.5,
        "note": "High-angle M8 link-ball candidate; exact SKU and holder geometry still open.",
    },
    {
        "candidate": "MISUMI_RBLD12_style_link_ball",
        "source_id": "SRC-JNT-004",
        "catalog_static_capacity_n": 26700.0,
        "allowable_angle_deg": 40.0,
        "pin_diameter_mm": 12.0,
        "thread_root_diameter_mm": 9.8,
        "note": "Upsized high-angle candidate if M8 stud/bearing package is too tight.",
    },
)


CENTRAL_CARDAN_PACKAGES = (
    {
        "candidate": "Ruland_MUS15_8_8_F",
        "source_id": "SRC-JNT-007",
        "rated_torque_nm": 15.3,
        "peak_torque_nm": None,
        "max_operating_angle_deg": 45.0,
        "note": "Small 8 mm bore U-joint; useful size reference but likely low torque.",
    },
    {
        "candidate": "Ruland_MUSSK22_12_12_F",
        "source_id": "SRC-JNT-008",
        "rated_torque_nm": 39.0,
        "peak_torque_nm": 197.0,
        "max_operating_angle_deg": 45.0,
        "note": "Keyed 12 mm U-joint; still torque-limited under conservative yaw screen.",
    },
)


def circular_area_mm2(diameter_mm):
    return pi * diameter_mm ** 2 / 4.0


def double_shear_stress_mpa(force_n, pin_diameter_mm):
    return force_n / (2.0 * circular_area_mm2(pin_diameter_mm))


def lug_bearing_stress_mpa(force_n, pin_diameter_mm, lug_thickness_mm):
    return force_n / (pin_diameter_mm * lug_thickness_mm)


def round_bar_bending_stress_mpa(force_n, standoff_mm, root_diameter_mm):
    # Cantilevered-thread screen only. A properly bracketed joint should avoid
    # this load path by keeping force through the ball center.
    moment_nmm = force_n * standoff_mm
    return 32.0 * moment_nmm / (pi * root_diameter_mm ** 3)


def allowable_standoff_mm(force_n, root_diameter_mm, allowable_bending_mpa=PRELIM_ALLOWABLE_STUD_BENDING_MPA):
    return allowable_bending_mpa * pi * root_diameter_mm ** 3 / (32.0 * force_n)


def actuator_package_screen(angle_deg, lug_thickness_mm=DEFAULT_BRACKET_LUG_THICKNESS_MM,
                            stud_standoff_mm=DEFAULT_STUD_STANDOFF_MM):
    articulation = joint_articulation_summary(angle_deg)
    force = worst_case(angle_deg=angle_deg, design_factor=2.0, max_eccentricity_mm=100.0)
    required_angle_deg = max(
        articulation["maximum_lower_joint_deviation_deg"],
        articulation["maximum_upper_joint_deviation_deg"],
    ) + ANGLE_MARGIN_DEG
    required_axial_force_n = force["max_axial_force_n"]
    required_static_capacity_n = 2.0 * required_axial_force_n

    rows = []
    for candidate in ACTUATOR_JOINT_PACKAGES:
        pin_shear = double_shear_stress_mpa(required_axial_force_n, candidate["pin_diameter_mm"])
        lug_bearing = lug_bearing_stress_mpa(
            required_axial_force_n,
            candidate["pin_diameter_mm"],
            lug_thickness_mm,
        )
        stud_bending = round_bar_bending_stress_mpa(
            required_axial_force_n,
            stud_standoff_mm,
            candidate["thread_root_diameter_mm"],
        )
        max_standoff = allowable_standoff_mm(required_axial_force_n, candidate["thread_root_diameter_mm"])
        angle_ok = candidate["allowable_angle_deg"] >= required_angle_deg
        axial_capacity = candidate.get("catalog_axial_static_capacity_n", candidate.get("catalog_static_capacity_n"))
        capacity_ok = axial_capacity >= required_static_capacity_n
        pin_shear_ok = pin_shear <= PRELIM_ALLOWABLE_PIN_SHEAR_MPA
        lug_bearing_ok = lug_bearing <= PRELIM_ALLOWABLE_LUG_BEARING_MPA
        stud_bending_ok = stud_bending <= PRELIM_ALLOWABLE_STUD_BENDING_MPA
        rows.append({
            "angle_case_deg": angle_deg,
            "candidate": candidate["candidate"],
            "source_id": candidate["source_id"],
            "required_angle_with_margin_deg": required_angle_deg,
            "required_axial_force_n": required_axial_force_n,
            "required_static_capacity_n": required_static_capacity_n,
            "allowable_angle_deg": candidate["allowable_angle_deg"],
            "catalog_axial_static_capacity_n": axial_capacity,
            "catalog_radial_static_limit_n": candidate.get("catalog_radial_static_limit_n"),
            "pin_diameter_mm": candidate["pin_diameter_mm"],
            "lug_thickness_mm": lug_thickness_mm,
            "stud_standoff_mm": stud_standoff_mm,
            "thread_root_diameter_mm": candidate["thread_root_diameter_mm"],
            "pin_double_shear_stress_mpa": pin_shear,
            "lug_bearing_stress_mpa": lug_bearing,
            "cantilevered_stud_bending_stress_mpa": stud_bending,
            "max_cantilever_standoff_for_allowable_bending_mm": max_standoff,
            "angle_ok": angle_ok,
            "catalog_capacity_ok": capacity_ok,
            "pin_shear_ok": pin_shear_ok,
            "lug_bearing_ok": lug_bearing_ok,
            "cantilevered_stud_bending_ok": stud_bending_ok,
            "screen_result": "PASS_PACKAGING_SCREEN" if (
                angle_ok and capacity_ok and pin_shear_ok and lug_bearing_ok and stud_bending_ok
            ) else "REQUIRES_REDESIGN_OR_UPSIZE",
            "note": candidate["note"],
        })
    return rows


def yaw_torque_case(total_mass_kg=CENTRAL_YAW_TOTAL_MASS_KG,
                    cg_x_mm=CENTRAL_YAW_CG_OFFSET_X_MM,
                    cg_y_mm=CENTRAL_YAW_CG_OFFSET_Y_MM,
                    horizontal_accel_g=CENTRAL_YAW_HORIZONTAL_ACCEL_G,
                    design_factor=CENTRAL_YAW_DESIGN_FACTOR):
    cg_radius_m = sqrt(cg_x_mm ** 2 + cg_y_mm ** 2) / 1000.0
    horizontal_force_n = total_mass_kg * P.gravity_m_s2 * horizontal_accel_g * design_factor
    torque_nm = horizontal_force_n * cg_radius_m
    return {
        "total_mass_kg": total_mass_kg,
        "cg_x_mm": cg_x_mm,
        "cg_y_mm": cg_y_mm,
        "cg_radius_mm": cg_radius_m * 1000.0,
        "horizontal_accel_g": horizontal_accel_g,
        "design_factor": design_factor,
        "horizontal_force_n": horizontal_force_n,
        "yaw_torque_nm": torque_nm,
        "torque_screen_factor": CENTRAL_YAW_TORQUE_SCREEN_FACTOR,
        "required_peak_or_design_torque_nm": torque_nm * CENTRAL_YAW_TORQUE_SCREEN_FACTOR,
    }


def central_cardan_torque_screen(angle_deg=5.0):
    cardan = cardan_summary(angle_deg)
    torque = yaw_torque_case()
    required_angle = cardan["maximum_cardan_tilt_deg"] + ANGLE_MARGIN_DEG
    rows = []
    for candidate in CENTRAL_CARDAN_PACKAGES:
        angle_ok = candidate["max_operating_angle_deg"] >= required_angle
        rated_ok = candidate["rated_torque_nm"] >= torque["yaw_torque_nm"]
        peak = candidate["peak_torque_nm"]
        peak_ok = False if peak is None else peak >= torque["required_peak_or_design_torque_nm"]
        rows.append({
            "angle_case_deg": angle_deg,
            "candidate": candidate["candidate"],
            "source_id": candidate["source_id"],
            "required_angle_with_margin_deg": required_angle,
            "max_operating_angle_deg": candidate["max_operating_angle_deg"],
            "yaw_torque_nm": torque["yaw_torque_nm"],
            "required_peak_or_design_torque_nm": torque["required_peak_or_design_torque_nm"],
            "rated_torque_nm": candidate["rated_torque_nm"],
            "peak_torque_nm": peak,
            "angle_ok": angle_ok,
            "rated_torque_ok": rated_ok,
            "peak_or_design_torque_ok": peak_ok,
            "screen_result": "PASS" if (angle_ok and rated_ok and peak_ok) else "FAIL_TORQUE_SCREEN",
            "note": candidate["note"],
        })
    return rows


def square_tube_torsion_screen(torque_nm=None, outer_size_mm=None, wall_mm=None, length_mm=None):
    if torque_nm is None:
        torque_nm = yaw_torque_case()["yaw_torque_nm"]
    if outer_size_mm is None:
        outer_size_mm = P.guide_outer_size_mm
    if wall_mm is None:
        wall_mm = P.guide_outer_wall_mm
    if length_mm is None:
        length_mm = P.guide_outer_length_mm
    mean_size_mm = outer_size_mm - wall_mm
    enclosed_area_mm2 = mean_size_mm ** 2
    perimeter_mm = 4.0 * mean_size_mm
    torque_nmm = torque_nm * 1000.0
    shear_flow_n_per_mm = torque_nmm / (2.0 * enclosed_area_mm2)
    shear_stress_mpa = shear_flow_n_per_mm / wall_mm
    torsion_constant_mm4 = 4.0 * enclosed_area_mm2 ** 2 / (perimeter_mm / wall_mm)
    twist_rad = torque_nmm * length_mm / (STEEL_SHEAR_MODULUS_MPA * torsion_constant_mm4)
    return {
        "torque_nm": torque_nm,
        "outer_size_mm": outer_size_mm,
        "wall_mm": wall_mm,
        "length_mm": length_mm,
        "mean_size_mm": mean_size_mm,
        "thin_wall_torsional_shear_mpa": shear_stress_mpa,
        "estimated_twist_deg": twist_rad * 180.0 / pi,
        "note": "Thin-wall closed-section estimate for yaw torque path comparison only.",
    }


def summary():
    actuator_rows = []
    for angle in ANGLE_CASES_DEG:
        actuator_rows.extend(actuator_package_screen(angle))
    return {
        "screening_assumptions": {
            "lug_thickness_mm": DEFAULT_BRACKET_LUG_THICKNESS_MM,
            "stud_standoff_mm": DEFAULT_STUD_STANDOFF_MM,
            "prelim_allowable_pin_shear_mpa": PRELIM_ALLOWABLE_PIN_SHEAR_MPA,
            "prelim_allowable_lug_bearing_mpa": PRELIM_ALLOWABLE_LUG_BEARING_MPA,
            "prelim_allowable_stud_bending_mpa": PRELIM_ALLOWABLE_STUD_BENDING_MPA,
            "fabrication_status": "preliminary; not approved for fabrication",
        },
        "actuator_package_rows": actuator_rows,
        "central_cardan_torque_rows": central_cardan_torque_screen(5.0),
        "central_yaw_torque_case": yaw_torque_case(),
        "square_tube_torsion_reference": square_tube_torsion_screen(),
    }


def main():
    result = summary()
    print({"screening_assumptions": result["screening_assumptions"]})
    print({"actuator_package_screen": result["actuator_package_rows"]})
    print({"central_yaw_torque_case": result["central_yaw_torque_case"]})
    print({"central_cardan_torque_screen": result["central_cardan_torque_rows"]})
    print({"square_tube_torsion_reference": result["square_tube_torsion_reference"]})


if __name__ == "__main__":
    main()
