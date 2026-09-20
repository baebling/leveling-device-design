"""Audit the vendor LM4075OE STEP without modifying the source file."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import cadquery as cq


def rounded_vector(value: cq.Vector) -> list[float]:
    return [round(value.x, 6), round(value.y, 6), round(value.z, 6)]


def edge_record(edge: cq.Edge) -> dict[str, object] | None:
    if edge.geomType() != "CIRCLE":
        return None
    record: dict[str, object] = {
        "radius_mm": round(edge.radius(), 6),
        "length_mm": round(edge.Length(), 6),
    }
    try:
        record["center_mm"] = rounded_vector(edge.arcCenter())
    except Exception:
        record["center_mm"] = rounded_vector(edge.Center())
    try:
        record["normal"] = rounded_vector(edge.normal())
    except Exception:
        record["normal"] = None
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("step", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    source = args.step.resolve()
    solids = list(cq.importers.importStep(str(source)).solids().vals())
    compound = cq.Compound.makeCompound(solids)
    overall = compound.BoundingBox()

    solid_records = []
    circle_records = []
    for solid_index, solid in enumerate(solids, start=1):
        box = solid.BoundingBox()
        circles = []
        for edge_index, edge in enumerate(solid.Edges(), start=1):
            record = edge_record(edge)
            if record is None:
                continue
            record.update({"solid": solid_index, "edge": edge_index})
            circles.append(record)
            circle_records.append(record)
        solid_records.append(
            {
                "solid": solid_index,
                "valid": solid.isValid(),
                "volume_mm3": round(solid.Volume(), 6),
                "center_of_mass_mm": rounded_vector(solid.Center()),
                "bounds_mm": {
                    "xmin": round(box.xmin, 6),
                    "xmax": round(box.xmax, 6),
                    "ymin": round(box.ymin, 6),
                    "ymax": round(box.ymax, 6),
                    "zmin": round(box.zmin, 6),
                    "zmax": round(box.zmax, 6),
                    "xlen": round(box.xlen, 6),
                    "ylen": round(box.ylen, 6),
                    "zlen": round(box.zlen, 6),
                },
                "circular_edges": circles,
            }
        )

    report = {
        "source": str(source),
        "sha256": hashlib.sha256(source.read_bytes()).hexdigest().upper(),
        "solid_count": len(solids),
        "all_solids_valid": all(item["valid"] for item in solid_records),
        "overall_bounds_mm": {
            "xmin": round(overall.xmin, 6),
            "xmax": round(overall.xmax, 6),
            "ymin": round(overall.ymin, 6),
            "ymax": round(overall.ymax, 6),
            "zmin": round(overall.zmin, 6),
            "zmax": round(overall.zmax, 6),
            "xlen": round(overall.xlen, 6),
            "ylen": round(overall.ylen, 6),
            "zlen": round(overall.zlen, 6),
        },
        "solids": solid_records,
        "all_circular_edges": circle_records,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
