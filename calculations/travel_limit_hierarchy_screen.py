"""Preliminary travel-limit hierarchy for the selected workspace candidate.

The result defines coordinate-free actuator-length windows.  CAD must later
convert them into separate switch and mechanical-stop contact geometry for all
permitted pitch/roll contact permutations.
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
from calculations.workspace_operating_window_screen import summary as workspace_summary


SOFT_END_RESERVE_MM = 15.0
ELECTRICAL_TO_STOP_ALLOWANCE_MM = 5.0
HARD_ENDPOINT_GUARD_MM = 5.0
ACTIVE_TOTAL_LIFTED_MASS_KG = 42.0
PRELIMINARY_STATIC_STOP_FACTOR = 2.0
LIFT_STOP_CONTACT_COUNT = 2


def length_hierarchy():
    retracted = P.actuator_retracted_mm
    extended = P.actuator_extended_mm
    hard_lower = retracted + HARD_ENDPOINT_GUARD_MM
    electrical_lower = hard_lower + ELECTRICAL_TO_STOP_ALLOWANCE_MM
    command_lower = retracted + SOFT_END_RESERVE_MM
    command_upper = extended - SOFT_END_RESERVE_MM
    electrical_upper = command_upper + ELECTRICAL_TO_STOP_ALLOWANCE_MM
    hard_upper = electrical_upper + ELECTRICAL_TO_STOP_ALLOWANCE_MM
    return {
        "catalogue_endpoint_range_mm": (retracted, extended),
        "hard_stop_guarded_range_mm": (hard_lower, hard_upper),
        "electrical_limit_target_range_mm": (electrical_lower, electrical_upper),
        "commanded_soft_range_mm": (command_lower, command_upper),
        "sequence_on_retraction": (
            f"command lower {command_lower:.0f} mm -> electrical lower {electrical_lower:.0f} mm "
            f"-> mechanical lower stop no closer than {hard_lower:.0f} mm -> catalogue end {retracted:.0f} mm"
        ),
        "sequence_on_extension": (
            f"command upper {command_upper:.0f} mm -> electrical upper {electrical_upper:.0f} mm "
            f"-> mechanical upper stop no farther than {hard_upper:.0f} mm -> catalogue end {extended:.0f} mm"
        ),
        "note": (
            "The electrical-to-stop allowance is a preliminary 5 mm motion budget. "
            "Actual switch repeatability, controller deceleration, backlash, and actuator "
            "end dimensions must be measured before freezing the values."
        ),
    }


def selected_workspace_limit_check():
    selected = workspace_summary()["recommended_candidate"]
    hierarchy = length_hierarchy()
    command_lower, command_upper = hierarchy["commanded_soft_range_mm"]
    rows = []
    for row in selected_workspace_rows(selected):
        rows.append({
            **row,
            "inside_commanded_soft_range": (
                row["minimum_actuator_length_mm"] >= command_lower
                and row["maximum_actuator_length_mm"] <= command_upper
            ),
        })
    worst = min(rows, key=lambda row: min(
        row["minimum_actuator_length_mm"] - command_lower,
        command_upper - row["maximum_actuator_length_mm"],
    ))
    return {
        "workspace_code": selected["code"],
        "selected_collapsed_height_mm": selected["collapsed_device_height_mm"],
        "all_grid_points_inside_commanded_soft_range": all(row["inside_commanded_soft_range"] for row in rows),
        "worst_grid_row": worst,
        "hard_stop_implementation_rule": (
            "A lower and an upper lift stop must be independent load-bearing physical contacts. "
            "They must be external collars/shoulders or equivalent geometry and may not block "
            "the keyed inner tube or depend on an actuator internal limit."
        ),
        "electrical_limit_rule": (
            "Each travel direction needs a separately mounted electrical limit/interlock that "
            "interrupts drive before its corresponding physical stop."
        ),
    }


def selected_workspace_rows(selected):
    # Re-evaluate via the candidate screen to keep the detailed nine-corner grid private to this module.
    candidate = next(
        row for row in workspace_summary()["candidate_rows"]
        if row["code"] == selected["code"]
    )
    raw_candidate = {
        key: candidate[key]
        for key in (
            "code", "collapsed_device_height_mm", "joint_height_offset_mm",
            "guide_outer_length_mm", "guide_inner_length_mm", "status", "note",
        )
    }

    # candidate_workspace_screen returns aggregate rows, so recreate the same grid locally.
    from itertools import product
    from calculations.workspace_operating_window_screen import (
        OPERATING_ANGLE_DEG, OPERATING_LIFT_MM, _offset_pose,
    )
    from calculations.actuator_geometry import actuator_lengths

    rows = []
    for lift_mm, pitch_deg, roll_deg in product(
        OPERATING_LIFT_MM,
        (-OPERATING_ANGLE_DEG, 0.0, OPERATING_ANGLE_DEG),
        (-OPERATING_ANGLE_DEG, 0.0, OPERATING_ANGLE_DEG),
    ):
        lengths = actuator_lengths(_offset_pose(
            lift_mm, pitch_deg, roll_deg, raw_candidate["joint_height_offset_mm"]
        ))
        rows.append({
            "lift_mm": lift_mm,
            "pitch_deg": pitch_deg,
            "roll_deg": roll_deg,
            "minimum_actuator_length_mm": min(lengths),
            "maximum_actuator_length_mm": max(lengths),
        })
    return rows


def preliminary_lift_stop_load_case():
    design_vertical_load = (
        ACTIVE_TOTAL_LIFTED_MASS_KG
        * P.gravity_m_s2
        * PRELIMINARY_STATIC_STOP_FACTOR
    )
    return {
        "total_lifted_mass_kg": ACTIVE_TOTAL_LIFTED_MASS_KG,
        "gravity_m_s2": P.gravity_m_s2,
        "preliminary_static_factor": PRELIMINARY_STATIC_STOP_FACTOR,
        "design_vertical_load_n": design_vertical_load,
        "assumed_parallel_lift_stop_contacts": LIFT_STOP_CONTACT_COUNT,
        "equal_share_reference_n_per_contact": design_vertical_load / LIFT_STOP_CONTACT_COUNT,
        "warning": (
            "This is a static reference only. It does not size a stop for impact, actuator speed, "
            "lost motion, misalignment, one-contact load concentration, fatigue, or a falling load."
        ),
    }


def summary():
    return {
        "length_hierarchy": length_hierarchy(),
        "selected_workspace_limit_check": selected_workspace_limit_check(),
        "preliminary_lift_stop_load_case": preliminary_lift_stop_load_case(),
        "phase_gate": "PHASE_1_PRELIMINARY_NOT_FOR_FABRICATION",
    }


def main():
    result = summary()
    print({"length_hierarchy": result["length_hierarchy"]})
    print({"selected_workspace_limit_check": result["selected_workspace_limit_check"]})
    print({"preliminary_lift_stop_load_case": result["preliminary_lift_stop_load_case"]})


if __name__ == "__main__":
    main()
