"""Compare preliminary central yaw-torque path concepts.

The goal is to select a Phase 0 direction, not to create fabrication geometry.
"""

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
from calculations.joint_detail_screen import square_tube_torsion_screen, yaw_torque_case
from calculations.mobility_analysis import cardan_summary
from calculations.user_confirmed_baseline import central_yaw_screen


ACTIVE_ANGLE_CASE_DEG = 3.0
CONSERVATIVE_ANGLE_CASE_DEG = 5.0
KEYED_SLIDE_COUPLE_SEPARATION_MM = P.guide_outer_size_mm
KEYED_SLIDE_CONTACT_WIDTH_MM = 10.0
KEYED_SLIDE_MIN_OVERLAP_MM = P.guide_min_overlap_mm
PRELIM_ALLOWABLE_KEY_CONTACT_MPA = 50.0
PRELIM_ALLOWABLE_TUBE_TORSION_MPA = 50.0
DUAL_GUIDE_SEPARATION_MM = P.support_radius_mm
HIWIN_MGN15H_DYNAMIC_LOAD_N = 6370.0
HIWIN_MGN15H_STATIC_LOAD_N = 9110.0
MISUMI_BSHS16_DYNAMIC_TORQUE_NM = 51.0
MISUMI_BSHS16_STATIC_TORQUE_NM = 93.0
RULAND_US32_RATED_TORQUE_NM = 485.8
RULAND_US32_PEAK_TORQUE_NM = 2429.2
RULAND_US32_MAX_ANGLE_DEG = 45.0


def required_central_path_case(angle_deg=ACTIVE_ANGLE_CASE_DEG):
    torque = central_yaw_screen()
    cardan = cardan_summary(angle_deg)
    required_angle = cardan["maximum_cardan_tilt_deg"] + ANGLE_MARGIN_DEG
    return {
        "angle_case_deg": angle_deg,
        "required_articulation_angle_deg": required_angle,
        "operating_yaw_torque_nm": torque["yaw_torque_nm"],
        "peak_or_design_yaw_torque_nm": torque["required_design_yaw_torque_nm"],
        "case_basis": "user-confirmed 10 kg payload, 10 kg cart, 22 kg moving structure, DF 1.5, 50/50 mm CG offset",
    }


def conservative_required_central_path_case(angle_deg=CONSERVATIVE_ANGLE_CASE_DEG):
    torque = yaw_torque_case()
    cardan = cardan_summary(angle_deg)
    required_angle = cardan["maximum_cardan_tilt_deg"] + ANGLE_MARGIN_DEG
    return {
        "angle_case_deg": angle_deg,
        "required_articulation_angle_deg": required_angle,
        "operating_yaw_torque_nm": torque["yaw_torque_nm"],
        "peak_or_design_yaw_torque_nm": torque["required_peak_or_design_torque_nm"],
        "case_basis": "archived conservative: 90 kg lifted mass, 0.5 g horizontal acceleration, DF 2.0, 100/100 mm CG offset",
    }


def margin(capacity, required):
    return capacity / required if required else None


def keyed_square_slide_option():
    case = required_central_path_case()
    torsion = square_tube_torsion_screen(torque_nm=case["operating_yaw_torque_nm"])
    peak_torsion = square_tube_torsion_screen(torque_nm=case["peak_or_design_yaw_torque_nm"])
    couple_force_n = case["peak_or_design_yaw_torque_nm"] * 1000.0 / KEYED_SLIDE_COUPLE_SEPARATION_MM
    contact_area_mm2 = KEYED_SLIDE_CONTACT_WIDTH_MM * KEYED_SLIDE_MIN_OVERLAP_MM
    contact_pressure_mpa = couple_force_n / contact_area_mm2
    pass_screen = (
        peak_torsion["thin_wall_torsional_shear_mpa"] <= PRELIM_ALLOWABLE_TUBE_TORSION_MPA
        and contact_pressure_mpa <= PRELIM_ALLOWABLE_KEY_CONTACT_MPA
    )
    return {
        "concept_id": "YAW-A",
        "concept_name": "keyed_square_slide_with_two_axis_gimbal_torque_bypass",
        "source_ids": "cad.parameters; calculations/joint_detail_screen.py",
        "description": "Current central square telescoping guide carries yaw torque; top gimbal only allows pitch/roll and does not interrupt the yaw path.",
        "operating_torque_capacity_or_reference_nm": "calculated closed-section tube",
        "peak_torque_capacity_or_reference_nm": "calculated closed-section tube",
        "required_operating_torque_nm": case["operating_yaw_torque_nm"],
        "required_peak_or_design_torque_nm": case["peak_or_design_yaw_torque_nm"],
        "required_angle_deg": case["required_articulation_angle_deg"],
        "angle_capacity_deg": "depends on gimbal stops",
        "peak_tube_shear_mpa": peak_torsion["thin_wall_torsional_shear_mpa"],
        "peak_estimated_twist_deg": peak_torsion["estimated_twist_deg"],
        "key_couple_force_n": couple_force_n,
        "key_contact_pressure_mpa": contact_pressure_mpa,
        "load_screen_result": "PASS_PRELIM" if pass_screen else "FAIL_PRELIM",
        "phase0_rank": 1,
        "recommendation": "preferred concept direction if backlash, wear, and gimbal-axis implementation are solved",
        "main_risks": "sliding fit backlash, wear, side load, gimbal/yaw key connection, contamination, mock-up required",
    }


def oversized_direct_cardan_option():
    case = required_central_path_case()
    angle_ok = RULAND_US32_MAX_ANGLE_DEG >= case["required_articulation_angle_deg"]
    rated_ok = RULAND_US32_RATED_TORQUE_NM >= case["operating_yaw_torque_nm"]
    peak_ok = RULAND_US32_PEAK_TORQUE_NM >= case["peak_or_design_yaw_torque_nm"]
    return {
        "concept_id": "YAW-B",
        "concept_name": "oversized_direct_torque_universal_joint",
        "source_ids": "SRC-JNT-009",
        "description": "A large single Cardan directly transmits yaw torque while allowing pitch/roll articulation.",
        "operating_torque_capacity_or_reference_nm": RULAND_US32_RATED_TORQUE_NM,
        "peak_torque_capacity_or_reference_nm": RULAND_US32_PEAK_TORQUE_NM,
        "required_operating_torque_nm": case["operating_yaw_torque_nm"],
        "required_peak_or_design_torque_nm": case["peak_or_design_yaw_torque_nm"],
        "rated_torque_margin": margin(RULAND_US32_RATED_TORQUE_NM, case["operating_yaw_torque_nm"]),
        "peak_torque_margin": margin(RULAND_US32_PEAK_TORQUE_NM, case["peak_or_design_yaw_torque_nm"]),
        "required_angle_deg": case["required_articulation_angle_deg"],
        "angle_capacity_deg": RULAND_US32_MAX_ANGLE_DEG,
        "angle_margin_deg": RULAND_US32_MAX_ANGLE_DEG - case["required_articulation_angle_deg"],
        "load_screen_result": "PASS_TORQUE_ANGLE" if (angle_ok and rated_ok and peak_ok) else "FAIL",
        "phase0_rank": 4,
        "recommendation": "reserve torque-capable Cardan direction, but package/cost are likely heavy",
        "main_risks": "50.7 mm OD and 139.7 mm length are large for the central stack; shaft/key/clamp details and backlash still unresolved",
    }


def single_ball_spline_option():
    case = required_central_path_case()
    dynamic_ok = MISUMI_BSHS16_DYNAMIC_TORQUE_NM >= case["operating_yaw_torque_nm"]
    static_ok = MISUMI_BSHS16_STATIC_TORQUE_NM >= case["peak_or_design_yaw_torque_nm"]
    return {
        "concept_id": "YAW-C",
        "concept_name": "single_16mm_commercial_ball_spline",
        "source_ids": "SRC-JNT-010",
        "description": "Commercial ball spline carries Z translation and yaw torque in one component.",
        "operating_torque_capacity_or_reference_nm": MISUMI_BSHS16_DYNAMIC_TORQUE_NM,
        "peak_torque_capacity_or_reference_nm": MISUMI_BSHS16_STATIC_TORQUE_NM,
        "required_operating_torque_nm": case["operating_yaw_torque_nm"],
        "required_peak_or_design_torque_nm": case["peak_or_design_yaw_torque_nm"],
        "dynamic_torque_margin": margin(MISUMI_BSHS16_DYNAMIC_TORQUE_NM, case["operating_yaw_torque_nm"]),
        "static_torque_margin": margin(MISUMI_BSHS16_STATIC_TORQUE_NM, case["peak_or_design_yaw_torque_nm"]),
        "required_angle_deg": case["required_articulation_angle_deg"],
        "angle_capacity_deg": "requires separate top gimbal",
        "load_screen_result": "PASS_TORQUE_ONLY" if (dynamic_ok and static_ok) else "FAIL_TORQUE_CAPACITY",
        "phase0_rank": 3,
        "recommendation": "reserve only; torque is plausible in the low-load screen but package/procurement and pitch-roll isolation remain unattractive",
        "main_risks": "Pitch/roll still needs gimbal isolation; procurement, package height, cost, and overconstraint risk remain higher than YAW-A",
    }


def dual_parallel_guides_option():
    case = required_central_path_case()
    operating_pair_force_n = case["operating_yaw_torque_nm"] * 1000.0 / DUAL_GUIDE_SEPARATION_MM
    peak_pair_force_n = case["peak_or_design_yaw_torque_nm"] * 1000.0 / DUAL_GUIDE_SEPARATION_MM
    load_ok = (
        operating_pair_force_n <= HIWIN_MGN15H_DYNAMIC_LOAD_N
        and peak_pair_force_n <= HIWIN_MGN15H_STATIC_LOAD_N
    )
    return {
        "concept_id": "YAW-D",
        "concept_name": "dual_parallel_anti_yaw_guides_with_top_compliance",
        "source_ids": "SRC-GDE-002",
        "description": "Two separated guide paths create a yaw-resisting couple while a top gimbal/compliance prevents pitch/roll binding.",
        "operating_torque_capacity_or_reference_nm": f"force couple over {DUAL_GUIDE_SEPARATION_MM:.0f} mm",
        "peak_torque_capacity_or_reference_nm": f"force couple over {DUAL_GUIDE_SEPARATION_MM:.0f} mm",
        "required_operating_torque_nm": case["operating_yaw_torque_nm"],
        "required_peak_or_design_torque_nm": case["peak_or_design_yaw_torque_nm"],
        "operating_pair_force_n": operating_pair_force_n,
        "peak_pair_force_n": peak_pair_force_n,
        "guide_dynamic_rating_n": HIWIN_MGN15H_DYNAMIC_LOAD_N,
        "guide_static_rating_n": HIWIN_MGN15H_STATIC_LOAD_N,
        "required_angle_deg": case["required_articulation_angle_deg"],
        "angle_capacity_deg": "requires top compliance/gimbal",
        "load_screen_result": "PASS_LOAD_ONLY" if load_ok else "FAIL_LOAD",
        "phase0_rank": 2,
        "recommendation": "reserve concept if central guide backlash is unacceptable",
        "main_risks": "wide package, extra parts, alignment sensitivity, high overconstraint risk unless pitch/roll compliance is explicit",
    }


def comparison_rows():
    return [
        keyed_square_slide_option(),
        oversized_direct_cardan_option(),
        dual_parallel_guides_option(),
        single_ball_spline_option(),
    ]


def summary():
    return {
        "required_case": required_central_path_case(),
        "archived_conservative_case": conservative_required_central_path_case(),
        "comparison_rows": comparison_rows(),
        "preferred_direction": "YAW-A keyed square slide with explicit yaw torque bypass through the guide tube, keeping ball spline and oversized U-joint as reserves",
        "approval_gate": "preliminary only; not approved for fabrication",
    }


def main():
    result = summary()
    print({"required_case": result["required_case"]})
    print({"archived_conservative_case": result["archived_conservative_case"]})
    print({"comparison_rows": result["comparison_rows"]})
    print({"preferred_direction": result["preferred_direction"]})
    print({"approval_gate": result["approval_gate"]})


if __name__ == "__main__":
    main()
