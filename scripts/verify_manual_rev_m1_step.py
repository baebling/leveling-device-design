"""Independent B-rep audit for Fusion-exported Manual 3-RPS Rev M1 STEP files."""

from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

import cadquery as cq


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "manual_3rps_rev_m1_fusion_native"
GROUP_DIR = OUTPUT_DIR / "groups"
MAIN_STEP = OUTPUT_DIR / "Manual_3RPS_RevM1_NEUTRAL.step"
AUDIT_PATH = OUTPUT_DIR / "Manual_3RPS_RevM1_step_audit.json"
VOLUME_TOLERANCE_MM3 = 0.01

GROUP_NAMES = (
    "lower_frame",
    "lower_brackets",
    "lower_adapters",
    "lower_joints",
    "manual_struts",
    "upper_frame",
    "upper_brackets",
    "upper_joints",
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


def positive_intersection(first: cq.Shape, second: cq.Shape) -> float:
    return first.intersect(second).Volume()


def cross_group_report(
    first_name: str,
    first: list[cq.Shape],
    second_name: str,
    second: list[cq.Shape],
) -> dict[str, object]:
    collisions = []
    total_volume = 0.0
    maximum = 0.0
    for first_index, first_solid in enumerate(first, start=1):
        for second_index, second_solid in enumerate(second, start=1):
            volume = positive_intersection(first_solid, second_solid)
            total_volume += volume
            maximum = max(maximum, volume)
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
        "checked_pairs": len(first) * len(second),
        "total_intersection_volume_mm3": total_volume,
        "max_pair_intersection_volume_mm3": maximum,
        "collision_count": len(collisions),
        "collisions": collisions,
        "pass": not collisions,
    }


def self_group_report(name: str, solids: list[cq.Shape]) -> dict[str, object]:
    collisions = []
    checked_pairs = 0
    for (first_index, first_solid), (second_index, second_solid) in combinations(
        enumerate(solids, start=1), 2
    ):
        checked_pairs += 1
        volume = positive_intersection(first_solid, second_solid)
        if volume > VOLUME_TOLERANCE_MM3:
            collisions.append(
                {
                    "first_solid": first_index,
                    "second_solid": second_index,
                    "volume_mm3": volume,
                }
            )
    return {
        "group": name,
        "checked_pairs": checked_pairs,
        "collision_count": len(collisions),
        "collisions": collisions,
        "pass": not collisions,
    }


def almost_equal(value: float, target: float, tolerance: float = 0.01) -> bool:
    return abs(value - target) <= tolerance


def main() -> int:
    groups = {name: load_solids(GROUP_DIR / f"{name}.step") for name in GROUP_NAMES}
    main_solids = load_solids(MAIN_STEP)
    main_bounds = bounds(main_solids)
    group_summary = {
        name: {"solid_count": len(solids), "bounds_mm": bounds(solids)}
        for name, solids in groups.items()
    }

    cross_reports = [
        cross_group_report(first, groups[first], second, groups[second])
        for first, second in combinations(GROUP_NAMES, 2)
    ]
    self_reports = [self_group_report(name, groups[name]) for name in GROUP_NAMES]

    dimensions_pass = all(
        (
            almost_equal(main_bounds["xlen"], 700.0),
            almost_equal(main_bounds["ylen"], 700.0),
            almost_equal(main_bounds["zmin"], 0.0),
            almost_equal(main_bounds["zmax"], 300.0),
        )
    )
    cross_pass = all(item["pass"] for item in cross_reports)
    self_pass = all(item["pass"] for item in self_reports)
    audit = {
        "source": str(MAIN_STEP),
        "main_step_solid_count": len(main_solids),
        "main_bounds_mm": main_bounds,
        "group_summary": group_summary,
        "intersection_tolerance_mm3": VOLUME_TOLERANCE_MM3,
        "cross_group_reports": cross_reports,
        "self_group_reports": self_reports,
        "checks": {
            "700x700x300_envelope": dimensions_pass,
            "all_36_cross_group_pairs_have_no_positive_volume_overlap": cross_pass,
            "all_9_group_internal_pairs_have_no_positive_volume_overlap": self_pass,
        },
        "pass": dimensions_pass and cross_pass and self_pass,
    }
    AUDIT_PATH.write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "main_step_solid_count": audit["main_step_solid_count"],
                "main_bounds_mm": audit["main_bounds_mm"],
                "checks": audit["checks"],
                "cross_collisions": sum(item["collision_count"] for item in cross_reports),
                "internal_collisions": sum(item["collision_count"] for item in self_reports),
                "pass": audit["pass"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if audit["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
