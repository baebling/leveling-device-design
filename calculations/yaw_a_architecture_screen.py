"""Preliminary YAW-A architecture screen.

YAW-A means the keyed square telescoping guide carries yaw torque while a
two-axis gimbal/yoke permits pitch and roll. This file turns that direction
into candidate Phase 0 parameters without creating fabrication geometry.
"""

from math import atan, degrees, pi
from pathlib import Path
import os
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("XDG_CACHE_HOME", str(ROOT / ".cache"))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplcache"))
for path in (ROOT,):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from cad.parameters import P
from calculations.joint_candidate_screen import ANGLE_MARGIN_DEG
from calculations.mobility_analysis import ANGLE_CASES_DEG, cardan_summary
from calculations.user_confirmed_baseline import central_yaw_screen


YAW_A_GIMBAL_DESIGN_ANGLE_DEG = 8.0
YAW_A_GIMBAL_HARD_STOP_DEG = 10.0
YAW_A_BACKLASH_TARGET_DEG = 0.25
YAW_A_BACKLASH_MAX_DEG = 0.50
YAW_A_TOTAL_CLEARANCE_TARGET_MM = 0.2
YAW_A_TOTAL_CLEARANCE_MAX_MM = 0.3
YAW_A_CONTACT_WIDTH_MM = 10.0
YAW_A_CONTACT_OVERLAP_MIN_MM = P.guide_min_overlap_mm
YAW_A_CONTACT_OVERLAP_PREFERRED_MM = 100.0
YAW_A_COUPLE_SEPARATION_MM = P.guide_outer_size_mm
YAW_A_YOKE_COUPLE_ARM_MM = 50.0
YAW_A_YOKE_PIN_DIAMETER_MM = 10.0
YAW_A_YOKE_LUG_THICKNESS_MM = 8.0
PRELIM_ALLOWABLE_PIN_SHEAR_MPA = 100.0
PRELIM_ALLOWABLE_LUG_BEARING_MPA = 100.0


def constraint_rank_summary():
    # Platform twist variables: tx, ty, tz, rx, ry, rz.
    yaw_a = np.array([
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],  # tx = 0
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0],  # ty = 0
        [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],  # yaw rz = 0
    ])
    rigid_no_gimbal = np.array([
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
    ])
    loose_spherical_no_yaw_lock = np.array([
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
    ])

    def row(matrix, allowed_motion, result):
        rank = int(np.linalg.matrix_rank(matrix))
        return {
            "constraint_rank": rank,
            "passive_platform_dof": 6 - rank,
            "allowed_motion": allowed_motion,
            "screen_result": result,
        }

    return {
        "YAW_A_keyed_slide_with_two_axis_gimbal": row(yaw_a, "tz, rx, ry", "PASS_MOBILITY"),
        "rigid_keyed_slide_without_gimbal": row(rigid_no_gimbal, "tz only", "FAIL_BINDS_PITCH_ROLL"),
        "loose_spherical_joint_without_yaw_lock": row(loose_spherical_no_yaw_lock, "tz, rx, ry, rz", "FAIL_YAW_UNCONSTRAINED"),
    }


def gimbal_angle_screen():
    rows = []
    for angle in ANGLE_CASES_DEG:
        cardan = cardan_summary(angle)
        required_angle = cardan["maximum_cardan_tilt_deg"] + ANGLE_MARGIN_DEG
        rows.append({
            "pitch_roll_case_deg": angle,
            "maximum_combined_tilt_deg": cardan["maximum_cardan_tilt_deg"],
            "required_angle_with_margin_deg": required_angle,
            "candidate_design_angle_deg": YAW_A_GIMBAL_DESIGN_ANGLE_DEG,
            "candidate_hard_stop_angle_deg": YAW_A_GIMBAL_HARD_STOP_DEG,
            "passes_design_angle": required_angle <= YAW_A_GIMBAL_DESIGN_ANGLE_DEG,
            "passes_hard_stop_angle": required_angle <= YAW_A_GIMBAL_HARD_STOP_DEG,
        })
    return rows


def yaw_backlash_deg(total_clearance_mm, couple_separation_mm=YAW_A_COUPLE_SEPARATION_MM):
    return degrees(atan(total_clearance_mm / couple_separation_mm))


def backlash_screen():
    rows = []
    for clearance in (0.1, 0.2, 0.3, 0.5):
        backlash = yaw_backlash_deg(clearance)
        rows.append({
            "total_clearance_mm": clearance,
            "couple_separation_mm": YAW_A_COUPLE_SEPARATION_MM,
            "estimated_yaw_freeplay_deg": backlash,
            "meets_preferred_target": backlash <= YAW_A_BACKLASH_TARGET_DEG,
            "meets_maximum_limit": backlash <= YAW_A_BACKLASH_MAX_DEG,
        })
    return rows


def anti_yaw_contact_screen(contact_width_mm=YAW_A_CONTACT_WIDTH_MM,
                            overlap_mm=YAW_A_CONTACT_OVERLAP_MIN_MM):
    case = central_yaw_screen()
    design_torque_nm = case["required_design_yaw_torque_nm"]
    couple_force_n = design_torque_nm * 1000.0 / YAW_A_COUPLE_SEPARATION_MM
    contact_pressure_mpa = couple_force_n / (contact_width_mm * overlap_mm)
    return {
        "peak_or_design_yaw_torque_nm": design_torque_nm,
        "load_basis": "user-confirmed 10 kg payload, +/-3 deg PoC baseline",
        "couple_separation_mm": YAW_A_COUPLE_SEPARATION_MM,
        "couple_force_n": couple_force_n,
        "contact_width_mm": contact_width_mm,
        "overlap_mm": overlap_mm,
        "contact_pressure_mpa": contact_pressure_mpa,
        "preferred_overlap_mm": YAW_A_CONTACT_OVERLAP_PREFERRED_MM,
        "note": "Contact pressure is preliminary. Wear pad material, lubrication, preload and contamination are unresolved.",
    }


def circular_area_mm2(diameter_mm):
    return pi * diameter_mm ** 2 / 4.0


def yoke_pin_screen(pin_diameter_mm=YAW_A_YOKE_PIN_DIAMETER_MM,
                    lug_thickness_mm=YAW_A_YOKE_LUG_THICKNESS_MM,
                    couple_arm_mm=YAW_A_YOKE_COUPLE_ARM_MM):
    case = central_yaw_screen()
    design_torque_nm = case["required_design_yaw_torque_nm"]
    pin_force_n = design_torque_nm * 1000.0 / couple_arm_mm
    double_shear_mpa = pin_force_n / (2.0 * circular_area_mm2(pin_diameter_mm))
    lug_bearing_mpa = pin_force_n / (pin_diameter_mm * lug_thickness_mm)
    return {
        "peak_or_design_yaw_torque_nm": design_torque_nm,
        "load_basis": "user-confirmed 10 kg payload, +/-3 deg PoC baseline",
        "couple_arm_mm": couple_arm_mm,
        "pin_force_n": pin_force_n,
        "pin_diameter_mm": pin_diameter_mm,
        "lug_thickness_mm": lug_thickness_mm,
        "pin_double_shear_mpa": double_shear_mpa,
        "lug_bearing_mpa": lug_bearing_mpa,
        "pin_shear_ok": double_shear_mpa <= PRELIM_ALLOWABLE_PIN_SHEAR_MPA,
        "lug_bearing_ok": lug_bearing_mpa <= PRELIM_ALLOWABLE_LUG_BEARING_MPA,
        "note": "Yaw-torque pin screen only. Pitch/roll bearing life, fatigue and fastener details are not approved.",
    }


def candidate_parameter_summary():
    return {
        "gimbal_design_angle_deg": YAW_A_GIMBAL_DESIGN_ANGLE_DEG,
        "gimbal_hard_stop_angle_deg": YAW_A_GIMBAL_HARD_STOP_DEG,
        "total_yaw_clearance_target_mm": YAW_A_TOTAL_CLEARANCE_TARGET_MM,
        "total_yaw_clearance_max_mm": YAW_A_TOTAL_CLEARANCE_MAX_MM,
        "estimated_target_yaw_freeplay_deg": yaw_backlash_deg(YAW_A_TOTAL_CLEARANCE_TARGET_MM),
        "estimated_max_yaw_freeplay_deg": yaw_backlash_deg(YAW_A_TOTAL_CLEARANCE_MAX_MM),
        "anti_yaw_contact_width_mm": YAW_A_CONTACT_WIDTH_MM,
        "anti_yaw_min_overlap_mm": YAW_A_CONTACT_OVERLAP_MIN_MM,
        "anti_yaw_preferred_overlap_mm": YAW_A_CONTACT_OVERLAP_PREFERRED_MM,
        "gimbal_yaw_couple_arm_mm": YAW_A_YOKE_COUPLE_ARM_MM,
        "gimbal_yoke_pin_diameter_mm": YAW_A_YOKE_PIN_DIAMETER_MM,
        "gimbal_yoke_lug_thickness_mm": YAW_A_YOKE_LUG_THICKNESS_MM,
        "load_basis": "user-confirmed 10 kg payload, +/-3 deg PoC baseline",
        "fabrication_status": "preliminary; not approved for fabrication",
    }


def summary():
    return {
        "constraint_rank_summary": constraint_rank_summary(),
        "gimbal_angle_screen": gimbal_angle_screen(),
        "backlash_screen": backlash_screen(),
        "anti_yaw_contact_screen": anti_yaw_contact_screen(),
        "preferred_overlap_contact_screen": anti_yaw_contact_screen(overlap_mm=YAW_A_CONTACT_OVERLAP_PREFERRED_MM),
        "yoke_pin_screen": yoke_pin_screen(),
        "candidate_parameters": candidate_parameter_summary(),
    }


def main():
    result = summary()
    print({"constraint_rank_summary": result["constraint_rank_summary"]})
    print({"gimbal_angle_screen": result["gimbal_angle_screen"]})
    print({"backlash_screen": result["backlash_screen"]})
    print({"anti_yaw_contact_screen": result["anti_yaw_contact_screen"]})
    print({"preferred_overlap_contact_screen": result["preferred_overlap_contact_screen"]})
    print({"yoke_pin_screen": result["yoke_pin_screen"]})
    print({"candidate_parameters": result["candidate_parameters"]})


if __name__ == "__main__":
    main()
