"""Independent B-rep audit for Fusion-exported Profile Radial Rev D STEP files."""

from __future__ import annotations

import json
from pathlib import Path

import cadquery as cq


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "profile_radial_revD_fusion_native"
GROUP_DIR = OUTPUT_DIR / "groups"
MAIN_STEP = OUTPUT_DIR / "Profile_Radial_3RPS_RevD_COLLAPSED.step"
AUDIT_PATH = OUTPUT_DIR / "Profile_Radial_3RPS_RevD_step_audit.json"
VOLUME_TOLERANCE_MM3 = 0.01

GROUP_NAMES = (
    "lower_frame",
    "lower_brackets",
    "lower_adapters",
    "lower_joints",
    "actuators",
    "upper_frame",
    "upper_brackets",
    "upper_joints",
    "mechanical_stops",
    "fasteners",
)


def load_solids(path: Path) -> list[cq.Shape]:
    return list(cq.importers.importStep(str(path)).solids().vals())


def bounds(solids: list[cq.Shape]) -> dict[str, float]:
    compound = cq.Compound.makeCompound(solids)
    box = compound.BoundingBox()
    return {
        "xmin": box.xmin,
        "xmax": box.xmax,
        "ymin": box.ymin,
        "ymax": box.ymax,
        "zmin": box.zmin,
        "zmax": box.zmax,
        "xlen": box.xlen,
        "ylen": box.ylen,
        "zlen": box.zlen,
    }


def intersection_report(
    first_name: str,
    first: list[cq.Shape],
    second_name: str,
    second: list[cq.Shape],
) -> dict[str, object]:
    collisions = []
    total_volume = 0.0
    max_volume = 0.0
    for first_index, first_solid in enumerate(first, start=1):
        for second_index, second_solid in enumerate(second, start=1):
            volume = first_solid.intersect(second_solid).Volume()
            total_volume += volume
            max_volume = max(max_volume, volume)
            if volume > VOLUME_TOLERANCE_MM3:
                collisions.append(
                    {
                        "first_solid": first_index,
                        "second_solid": second_index,
                        "volume_mm3": volume,
                    }
                )
    return {
        "pair": f"{first_name}::{second_name}",
        "total_intersection_volume_mm3": total_volume,
        "max_pair_intersection_volume_mm3": max_volume,
        "collision_count": len(collisions),
        "collisions": collisions,
        "pass": not collisions,
    }


def almost_equal(value: float, target: float, tolerance: float = 0.01) -> bool:
    return abs(value - target) <= tolerance


def main() -> int:
    groups = {
        name: load_solids(GROUP_DIR / f"{name}.step") for name in GROUP_NAMES
    }
    main_solids = load_solids(MAIN_STEP)
    main_bounds = bounds(main_solids)
    group_summary = {
        name: {"solid_count": len(solids), "bounds_mm": bounds(solids)}
        for name, solids in groups.items()
    }

    collision_pairs = (
        ("lower_frame", "lower_brackets"),
        ("upper_frame", "upper_brackets"),
        ("lower_adapters", "lower_joints"),
        ("lower_joints", "actuators"),
        ("actuators", "upper_joints"),
        ("actuators", "lower_frame"),
        ("actuators", "lower_brackets"),
        ("actuators", "upper_frame"),
        ("actuators", "upper_brackets"),
        ("actuators", "mechanical_stops"),
        ("mechanical_stops", "lower_frame"),
        ("mechanical_stops", "upper_frame"),
        ("upper_joints", "mechanical_stops"),
        ("upper_joints", "upper_frame"),
    )
    intersections = [
        intersection_report(first, groups[first], second, groups[second])
        for first, second in collision_pairs
    ]

    dimensions_pass = all(
        (
            almost_equal(main_bounds["xlen"], 700.0),
            almost_equal(main_bounds["ylen"], 700.0),
            almost_equal(main_bounds["zmin"], 0.0),
            almost_equal(main_bounds["zmax"], 300.0),
        )
    )
    collisions_pass = all(item["pass"] for item in intersections)
    audit = {
        "source": str(MAIN_STEP),
        "main_step_solid_count": len(main_solids),
        "main_bounds_mm": main_bounds,
        "group_summary": group_summary,
        "intersection_tolerance_mm3": VOLUME_TOLERANCE_MM3,
        "intersections": intersections,
        "checks": {
            "700x700x300_envelope": dimensions_pass,
            "audited_non_mating_pairs_have_no_positive_volume_overlap": collisions_pass,
        },
        "pass": dimensions_pass and collisions_pass,
    }
    AUDIT_PATH.write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(audit, ensure_ascii=False, indent=2))
    return 0 if audit["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
