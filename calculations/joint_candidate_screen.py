"""Preliminary joint candidate screen for the Phase 0 design basis.

This is not a final bearing or joint selection. It only checks whether common
joint families are worth carrying into the next approval package.
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
from calculations.load_distribution import worst_case
from calculations.mobility_analysis import cardan_summary, joint_articulation_summary


ANGLE_CASES_DEG = (3.0, 5.0, 8.0)
ANGLE_MARGIN_DEG = 2.0
STATIC_LOAD_SCREEN_FACTOR = 2.0


ACTUATOR_JOINT_CANDIDATES = (
    {
        "candidate": "single_axis_clevis",
        "source_id": "concept_screen",
        "allowable_angle_deg": None,
        "static_load_capacity_n": None,
        "notes": "Rejected unless a planar motion path is proven; current lower joint motion is spatial.",
    },
    {
        "candidate": "MISUMI_PHSOSM8",
        "source_id": "SRC-JNT-001",
        "allowable_angle_deg": 12.0,
        "static_load_capacity_n": 2690.0,
        "notes": "Compact oil-free rod end; low static capacity margin in the current worst cases.",
    },
    {
        "candidate": "Minebea_HRT8E",
        "source_id": "SRC-JNT-006",
        "allowable_angle_deg": 14.0,
        "static_load_capacity_n": 5290.0,
        "radial_static_limit_n": 26770.0,
        "load_capacity_basis": "catalog axial static limit",
        "notes": "Use the 5.29 kN axial static limit for actuator-axis screening; 26.77 kN radial value is retained only as catalog context.",
    },
    {
        "candidate": "MISUMI_RBLD8_link_ball_style",
        "source_id": "SRC-JNT-004",
        "allowable_angle_deg": 40.0,
        "static_load_capacity_n": 12500.0,
        "notes": "High-angle link-ball style candidate; exact SKU/package must be verified.",
    },
)


CENTRAL_CARDAN_CANDIDATES = (
    {
        "candidate": "current_placeholder_design_angle",
        "source_id": "cad.parameters",
        "allowable_angle_deg": P.cardan_design_angle_deg,
        "notes": "Current CAD planning value; not a purchased joint rating.",
    },
    {
        "candidate": "current_placeholder_hard_stop",
        "source_id": "cad.parameters",
        "allowable_angle_deg": P.cardan_hard_stop_angle_deg,
        "notes": "Current CAD hard-stop planning value; needs independent stop geometry.",
    },
    {
        "candidate": "Ruland_single_u_joint_family",
        "source_id": "SRC-JNT-005",
        "allowable_angle_deg": 45.0,
        "notes": "Yaw-transmitting Cardan/u-joint family reference; torque, backlash and mounting TBD.",
    },
)


def actuator_joint_screen(angle_deg):
    articulation = joint_articulation_summary(angle_deg)
    force = worst_case(angle_deg=angle_deg, design_factor=2.0, max_eccentricity_mm=100.0)
    required_lower_angle = articulation["maximum_lower_joint_deviation_deg"]
    required_upper_angle = articulation["maximum_upper_joint_deviation_deg"]
    required_angle = max(required_lower_angle, required_upper_angle) + ANGLE_MARGIN_DEG
    required_static_load = force["max_axial_force_n"] * STATIC_LOAD_SCREEN_FACTOR

    rows = []
    for candidate in ACTUATOR_JOINT_CANDIDATES:
        angle_capacity = candidate["allowable_angle_deg"]
        load_capacity = candidate["static_load_capacity_n"]
        dof_ok = candidate["candidate"] != "single_axis_clevis"
        angle_ok = angle_capacity is not None and angle_capacity >= required_angle
        load_ok = load_capacity is not None and load_capacity >= required_static_load
        rows.append({
            "angle_case_deg": angle_deg,
            "candidate": candidate["candidate"],
            "source_id": candidate["source_id"],
            "required_angle_with_margin_deg": required_angle,
            "required_static_load_screen_n": required_static_load,
            "allowable_angle_deg": angle_capacity,
            "static_load_capacity_n": load_capacity,
            "load_capacity_basis": candidate.get("load_capacity_basis", "catalog value as recorded"),
            "radial_static_limit_n": candidate.get("radial_static_limit_n"),
            "angle_margin_remaining_deg": None if angle_capacity is None else angle_capacity - required_angle,
            "static_load_capacity_ratio_to_required_axial": None if load_capacity is None else load_capacity / force["max_axial_force_n"],
            "dof_ok": dof_ok,
            "angle_ok": angle_ok,
            "load_ok": load_ok,
            "screen_result": "PASS" if (dof_ok and angle_ok and load_ok) else "FAIL",
            "notes": candidate["notes"],
        })
    return rows


def central_cardan_screen(angle_deg):
    cardan = cardan_summary(angle_deg)
    required_angle = cardan["maximum_cardan_tilt_deg"] + ANGLE_MARGIN_DEG
    rows = []
    for candidate in CENTRAL_CARDAN_CANDIDATES:
        angle_capacity = candidate["allowable_angle_deg"]
        angle_ok = angle_capacity >= required_angle
        rows.append({
            "angle_case_deg": angle_deg,
            "candidate": candidate["candidate"],
            "source_id": candidate["source_id"],
            "required_angle_with_margin_deg": required_angle,
            "allowable_angle_deg": angle_capacity,
            "angle_margin_remaining_deg": angle_capacity - required_angle,
            "screen_result": "PASS_ANGLE_ONLY" if angle_ok else "FAIL",
            "notes": candidate["notes"],
        })
    return rows


def summary():
    actuator_rows = []
    cardan_rows = []
    for angle in ANGLE_CASES_DEG:
        actuator_rows.extend(actuator_joint_screen(angle))
        cardan_rows.extend(central_cardan_screen(angle))
    return {
        "screening_assumptions": {
            "angle_margin_deg": ANGLE_MARGIN_DEG,
            "static_load_screen_factor": STATIC_LOAD_SCREEN_FACTOR,
            "force_case": "load_distribution.worst_case(angle, design_factor=2.0, max_eccentricity_mm=100)",
            "fabrication_status": "preliminary; not approved for fabrication",
        },
        "actuator_joint_rows": actuator_rows,
        "central_cardan_rows": cardan_rows,
    }


def main():
    result = summary()
    print({"screening_assumptions": result["screening_assumptions"]})
    print({"actuator_joint_screen": result["actuator_joint_rows"]})
    print({"central_cardan_screen": result["central_cardan_rows"]})


if __name__ == "__main__":
    main()
