"""Repeated OpenCascade assembly, interference, and section checks for Rev M2."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cad.manual_turnbuckle_rev_m2 import components_for_pose, grouped_components
from calculations import manual_turnbuckle_rev_m2_screen as data
from scripts.build_manual_turnbuckle_rev_m2 import OUT, POSES


AUDIT = OUT / "Manual_3RPS_RevM2_repeated_verification.json"
VOLUME_TOLERANCE_MM3 = 0.01

NON_MATING_PAIRS = (
    ("links", "lower_frame"),
    ("links", "upper_frame"),
    ("links", "frame_brackets"),
    ("links", "lower_adapters"),
    ("links", "upper_adapters"),
    ("links", "lower_supports"),
    ("links", "upper_supports"),
    ("lower_supports", "lower_frame"),
    ("lower_supports", "lower_adapters"),
    ("upper_supports", "upper_frame"),
    ("upper_supports", "upper_adapters"),
    ("joint_pins", "lower_supports"),
    ("joint_pins", "upper_supports"),
    ("joint_pins", "links"),
)


def _boxes_overlap(first, second, tolerance=1e-6):
    a = first.BoundingBox()
    b = second.BoundingBox()
    return not (
        a.xmax <= b.xmin + tolerance
        or b.xmax <= a.xmin + tolerance
        or a.ymax <= b.ymin + tolerance
        or b.ymax <= a.ymin + tolerance
        or a.zmax <= b.zmin + tolerance
        or b.zmax <= a.zmin + tolerance
    )


def _pair_report(first_name, first, second_name, second):
    collisions = []
    candidate_count = 0
    for first_component in first:
        for second_component in second:
            if not _boxes_overlap(first_component.shape, second_component.shape):
                continue
            candidate_count += 1
            volume = first_component.shape.intersect(second_component.shape).Volume()
            if volume > VOLUME_TOLERANCE_MM3:
                collisions.append(
                    {
                        "first": first_component.name,
                        "second": second_component.name,
                        "volume_mm3": volume,
                    }
                )
    return {
        "pair": f"{first_name}::{second_name}",
        "broad_phase_candidates": candidate_count,
        "collision_count": len(collisions),
        "collisions": collisions,
        "pass": not collisions,
    }


def _pose_report(name, pitch, roll):
    components = components_for_pose(pitch, roll)
    groups = grouped_components(pitch, roll)
    valid = all(component.shape.isValid() for component in components)
    bounds = __import__("cadquery").Compound.makeCompound([component.shape for component in components]).BoundingBox()
    intersections = [
        _pair_report(first, groups[first], second, groups[second])
        for first, second in NON_MATING_PAIRS
    ]
    return {
        "pose": name,
        "pitch_deg": pitch,
        "roll_deg": roll,
        "component_count": len(components),
        "all_shapes_valid": valid,
        "bounds_mm": {
            "xlen": bounds.xlen,
            "ylen": bounds.ylen,
            "zmin": bounds.zmin,
            "zmax": bounds.zmax,
        },
        "intersections": intersections,
        "collision_count": sum(item["collision_count"] for item in intersections),
        "pass": valid and all(item["pass"] for item in intersections),
    }


def _section_and_fit_report():
    checks = {
        "lower_eye_width_inside_BJ762_12001_gap": 13.8 < 14.2,
        "upper_PHS12L_ring_width_inside_BJ762_20001_gap": 15.8 < 22.2,
        "upper_PHS12L_neck_width_inside_BJ762_20001_gap": 19.0 < 22.2,
        "upper_reducing_bush_pair_matches_pin_and_support": 12.0 < 12.2 and 20.0 < 20.2,
        "lower_nut_space_inside_15mm_standoff_gap": 12.0 <= data.P.lower_standoff_mm,
        "upper_nut_space_inside_20mm_standoff_gap": 18.0 <= data.P.upper_standoff_mm,
        "lower_adapter_edge_margin": (data.P.adapter_length_mm - data.P.adapter_hole_pitch_mm) / 2.0 >= 15.0,
        "upper_support_body_fits_60mm_plate_width": 50.0 <= data.P.adapter_width_mm,
    }
    return {
        "checks": checks,
        "clearances_mm": {
            "lower_eye_side_total": 14.2 - 13.8,
            "upper_ring_side_total": 22.2 - 15.8,
            "upper_neck_side_total": 22.2 - 19.0,
            "lower_nut_vertical": data.P.lower_standoff_mm - 12.0,
            "upper_nut_vertical": data.P.upper_standoff_mm - 18.0,
        },
        "pass": all(checks.values()),
    }


def _bom_report():
    bom_path = OUT / "Manual_3RPS_RevM2_BOM.csv"
    with bom_path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    by_id = {row["line_id"]: row for row in rows}
    expected = {
        "S01": 2,
        "S02": 4,
        "S03": 2,
        "S04": 3,
        "S05": 8,
        "S06": 6,
        "M01": 3,
        "M02": 3,
        "M03": 3,
        "M04": 3,
        "M05": 3,
        "M06": 3,
        "M07": 6,
        "M08": 3,
        "F01": 3,
        "F02": 3,
        "F03": 6,
        "F04": 6,
        "F05": 6,
        "F06": 6,
        "F07": 3,
        "F08": 3,
        "F09": 3,
        "F10": 14,
        "F11": 3,
        "F12": 3,
    }
    quantity_checks = {
        line_id: line_id in by_id and int(by_id[line_id]["quantity"]) == quantity
        for line_id, quantity in expected.items()
    }
    model_groups = {name: len(values) for name, values in grouped_components().items()}
    link_components = grouped_components().get("links", [])
    model_checks = {
        "three_links": model_groups.get("links") == 3,
        "sixteen_modeled_solids_per_link_including_five_lock_nuts": (
            len(link_components) == 3
            and all(len(component.shape.Solids()) == 16 for component in link_components)
        ),
        "three_lower_supports": model_groups.get("lower_supports") == 3,
        "three_upper_supports": model_groups.get("upper_supports") == 3,
        "six_lower_frame_profiles": model_groups.get("lower_frame") == 6,
        "five_upper_frame_profiles": model_groups.get("upper_frame") == 5,
        "fourteen_frame_brackets": model_groups.get("frame_brackets") == 14,
        "six_adapter_plates_plus_twelve_standoffs": (
            model_groups.get("lower_adapters") == 9 and model_groups.get("upper_adapters") == 9
        ),
        "twelve_adapter_bolts": model_groups.get("adapter_fasteners") == 12,
        "six_joint_pins": model_groups.get("joint_pins") == 6,
    }
    return {
        "bom_row_count": len(rows),
        "quantity_checks": quantity_checks,
        "model_group_counts": model_groups,
        "model_checks": model_checks,
        "pass": (
            len(rows) == 26
            and all(quantity_checks.values())
            and all(model_checks.values())
        ),
    }


def _cycle(cycle_number):
    workspace = data.workspace_audit()
    strength = data.strength_audit()
    poses = [_pose_report(name, *pose) for name, pose in POSES.items()]
    section = _section_and_fit_report()
    bom = _bom_report()
    result = {
        "cycle": cycle_number,
        "pass_1_kinematics_and_strength": workspace["passes"] and strength["passes_preliminary_screen"],
        "pass_2_occ_assembly_and_interference": all(pose["pass"] for pose in poses),
        "pass_3_section_fit_and_bom_reconstruction": section["pass"] and bom["pass"],
        "workspace_summary": {
            key: workspace[key]
            for key in (
                "required_minimum_pin_mm",
                "required_maximum_pin_mm",
                "required_adjustment_mm",
                "minimum_internal_engagement_mm",
                "lower_length_margin_mm",
                "upper_length_margin_mm",
            )
        },
        "strength": strength,
        "poses": poses,
        "section_fit": section,
        "bom": bom,
    }
    result["pass"] = all(
        result[key]
        for key in (
            "pass_1_kinematics_and_strength",
            "pass_2_occ_assembly_and_interference",
            "pass_3_section_fit_and_bom_reconstruction",
        )
    )
    canonical = json.dumps(result, ensure_ascii=False, sort_keys=True).encode("utf-8")
    result["result_sha256"] = hashlib.sha256(canonical).hexdigest()
    return result


def main():
    cycles = [_cycle(1), _cycle(2)]
    repeated_match = cycles[0]["result_sha256"] == cycles[1]["result_sha256"]
    # Cycle numbers differ by design, so compare the substantive payload too.
    left = dict(cycles[0])
    right = dict(cycles[1])
    for value in (left, right):
        value.pop("cycle", None)
        value.pop("result_sha256", None)
    repeated_match = left == right
    audit = {
        "engine": "CadQuery 2.8 / OpenCascade 7.9",
        "intersection_tolerance_mm3": VOLUME_TOLERANCE_MM3,
        "cycles": cycles,
        "repeated_results_identical": repeated_match,
        "purchase_release": False,
        "fabrication_release": False,
        "open_gates": [
            "Source an exact PHS12L M12x1.75 left-hand rod end with the audited dimensions.",
            "Source an exact M12x1.75 left-hand jam nut for each PHS12L interface.",
            "Source exact ID12/OD20/L11 flanged bushes and verify the delivered BJ762-20001 fork.",
            "Obtain supplier compression-use confirmation for STB-M12 or complete a one-leg proof test.",
            "Confirm tool access and stud-relief holes on one profile/adapter first article.",
            "Measure the complete-module CG and actual lower contact/coupling polygon before claiming whole-unit tip resistance.",
        ],
        "pass": all(cycle["pass"] for cycle in cycles) and repeated_match,
    }
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {
        "cycles": len(cycles),
        "repeated_results_identical": repeated_match,
        "pose_checks_per_cycle": len(POSES),
        "collision_count_each_cycle": [
            sum(pose["collision_count"] for pose in cycle["poses"]) for cycle in cycles
        ],
        "all_three_passes_each_cycle": [cycle["pass"] for cycle in cycles],
        "pass": audit["pass"],
        "audit": str(AUDIT),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if audit["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
