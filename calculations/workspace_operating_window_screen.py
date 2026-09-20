"""Select a preliminary full Z/pitch/roll operating window before CAD.

This screen considers the user-confirmed +/-3 deg grid, a 15 mm candidate
actuator soft-end reserve, and central-guide overlap.  It selects a geometry
candidate for the CAD gate but does not place fabrication geometry or final
mechanical stops.
"""

from itertools import product
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
from calculations.actuator_geometry import actuator_lengths


OPERATING_LIFT_MM = (0.0, 50.0, 75.0, 100.0)
OPERATING_ANGLE_DEG = 3.0
ACTUATOR_SOFT_END_RESERVE_MM = 15.0
MIN_GUIDE_OVERLAP_MM = P.guide_min_overlap_mm

WORKSPACE_CANDIDATES = (
    {
        "code": "WS-01-H0",
        "collapsed_device_height_mm": 250.0,
        "joint_height_offset_mm": -20.0,
        "guide_outer_length_mm": 190.0,
        "guide_inner_length_mm": 200.0,
        "status": "comparison_only",
        "note": "Existing 250 mm preliminary geometry; compare only because the lower operating reserve is tight.",
    },
    {
        "code": "WS-01-H20",
        "collapsed_device_height_mm": 270.0,
        "joint_height_offset_mm": 0.0,
        "guide_outer_length_mm": 195.0,
        "guide_inner_length_mm": 220.0,
        "status": "recommended_pre_cad_candidate",
        "note": "270 mm collapsed-height candidate inside the user-confirmed 250 to 300 mm envelope; adds lower-stroke reserve while retaining guide overlap.",
    },
)


def _offset_pose(lift_mm, pitch_deg, roll_deg, joint_height_offset_mm):
    return Pose(
        lift_mm + joint_height_offset_mm,
        pitch_deg,
        roll_deg,
        True,
        "workspace_operating_window",
    )


def guide_overlap_mm(lift_mm, joint_height_offset_mm, outer_length_mm, inner_length_mm):
    platform_z = P.platform_joint_z_collapsed_mm + joint_height_offset_mm + lift_mm
    outer_top = P.guide_outer_z0_mm + outer_length_mm
    inner_bottom = platform_z - inner_length_mm
    return max(0.0, outer_top - max(P.guide_outer_z0_mm, inner_bottom))


def candidate_workspace_screen(candidate):
    rows = []
    for lift_mm, pitch_deg, roll_deg in product(
        OPERATING_LIFT_MM,
        (-OPERATING_ANGLE_DEG, 0.0, OPERATING_ANGLE_DEG),
        (-OPERATING_ANGLE_DEG, 0.0, OPERATING_ANGLE_DEG),
    ):
        pose = _offset_pose(lift_mm, pitch_deg, roll_deg, candidate["joint_height_offset_mm"])
        lengths = actuator_lengths(pose)
        retracted_reserve = min(lengths) - (P.actuator_retracted_mm + ACTUATOR_SOFT_END_RESERVE_MM)
        extended_reserve = (P.actuator_extended_mm - ACTUATOR_SOFT_END_RESERVE_MM) - max(lengths)
        overlap = guide_overlap_mm(
            lift_mm,
            candidate["joint_height_offset_mm"],
            candidate["guide_outer_length_mm"],
            candidate["guide_inner_length_mm"],
        )
        rows.append({
            "lift_mm": lift_mm,
            "pitch_deg": pitch_deg,
            "roll_deg": roll_deg,
            "minimum_actuator_length_mm": min(lengths),
            "maximum_actuator_length_mm": max(lengths),
            "retracted_soft_reserve_mm": retracted_reserve,
            "extended_soft_reserve_mm": extended_reserve,
            "minimum_soft_reserve_mm": min(retracted_reserve, extended_reserve),
            "guide_overlap_mm": overlap,
            "guide_overlap_reserve_mm": overlap - MIN_GUIDE_OVERLAP_MM,
        })

    worst_actuator = min(rows, key=lambda row: row["minimum_soft_reserve_mm"])
    worst_overlap = min(rows, key=lambda row: row["guide_overlap_reserve_mm"])
    return {
        **candidate,
        "coordinate_system": "O lower-platform center; +X length, +Y width, +Z vertical; pitch about +Y; roll about +X",
        "equation": "Li = ||Ry(pitch) Rx(roll) ui + [0,0,z] - bi||",
        "actuator_soft_range_mm": (
            P.actuator_retracted_mm + ACTUATOR_SOFT_END_RESERVE_MM,
            P.actuator_extended_mm - ACTUATOR_SOFT_END_RESERVE_MM,
        ),
        "soft_end_reserve_basis": (
            "15 mm preliminary operating keep-out for catalog-end uncertainty, position-feedback/"
            "deceleration allowance, and assembly tolerance; it is not a final mechanical-stop position"
        ),
        "worst_actuator_row": worst_actuator,
        "worst_guide_row": worst_overlap,
        "full_operating_grid_passes": (
            worst_actuator["minimum_soft_reserve_mm"] >= 0.0
            and worst_overlap["guide_overlap_reserve_mm"] >= 0.0
        ),
        "cad_readiness_result": (
            "RECOMMENDED_FOR_PRE_CAD_PARAMETER_REVIEW"
            if candidate["status"] == "recommended_pre_cad_candidate"
            and worst_actuator["minimum_soft_reserve_mm"] >= 10.0
            and worst_overlap["guide_overlap_reserve_mm"] >= 5.0
            else "PASS_BUT_NOT_RECOMMENDED_FOR_CAD_BASELINE"
            if worst_actuator["minimum_soft_reserve_mm"] >= 0.0
            and worst_overlap["guide_overlap_reserve_mm"] >= 0.0
            else "FAIL"
        ),
        "remaining_requirement": (
            "CAD must locate independent lift stops and electrical limit switches so all actuator "
            "lengths stay inside the physical catalog endpoints under every permitted contact permutation."
        ),
    }


def summary():
    rows = [candidate_workspace_screen(candidate) for candidate in WORKSPACE_CANDIDATES]
    recommended = next(row for row in rows if row["status"] == "recommended_pre_cad_candidate")
    return {
        "screen_basis": {
            "payload": "10 kg user-confirmed material payload; workspace itself is geometry-only",
            "pitch_roll_grid_deg": "+/-3",
            "lift_grid_mm": OPERATING_LIFT_MM,
            "actuator_soft_end_reserve_mm": ACTUATOR_SOFT_END_RESERVE_MM,
            "minimum_guide_overlap_mm": MIN_GUIDE_OVERLAP_MM,
            "fabrication_status": "Phase 2 detailed CAD approved; not approved for fabrication",
        },
        "candidate_rows": rows,
        "recommended_candidate": recommended,
        "phase_gate": "PHASE_2_DETAILED_CAD_APPROVED_NOT_FOR_FABRICATION",
    }


def main():
    for row in summary()["candidate_rows"]:
        print({
            "code": row["code"],
            "collapsed_device_height_mm": row["collapsed_device_height_mm"],
            "worst_actuator_row": row["worst_actuator_row"],
            "worst_guide_row": row["worst_guide_row"],
            "cad_readiness_result": row["cad_readiness_result"],
        })


if __name__ == "__main__":
    main()
