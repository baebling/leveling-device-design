"""Rev F quotation/fabrication-review geometry for six custom metal parts.

The package is intentionally small: three drilled/tapped A6061 plates and
three supplier-finished S45C upper pockets.  Threads are represented by their
tap-drill diameter; drawings and the hole table carry the thread callout.
"""

from __future__ import annotations

import csv
import json
from math import atan2, degrees
from pathlib import Path

import cadquery as cq
import ezdxf

from fusion_scripts.ProfileRadialRevD import revd_data


LOWER_PLATE_SPECS = {
    "A1": {
        "profile_through": ((-48.0, 12.0), (48.0, 12.0)),
        "lmb_tap_m8": ((14.5, -24.0), (14.5, 12.0)),
    },
    "A2": {
        "profile_through": ((-48.0, -18.557), (48.0, -18.557)),
        "lmb_tap_m8": ((23.927, 12.0), (-7.25, -6.0)),
    },
    "A3": {
        "profile_through": ((-50.0, 6.557), (50.0, 6.557)),
        "lmb_tap_m8": ((-18.427, 12.0), (12.75, -6.0)),
    },
}

LOWER_PLATE_SPEC = {
    "material": "A6061-T6",
    "length_mm": 120.0,
    "width_mm": 70.0,
    "thickness_mm": 8.0,
    "profile_hole_diameter_mm": 9.0,
    "tap_drill_diameter_mm": 6.8,
    "thread": "M8x1.25 THROUGH",
}

UPPER_BRACKET_SPEC = {
    "material": "S45C, untreated",
    "base_length_mm": 60.0,
    "base_width_mm": 30.0,
    "base_thickness_mm": 9.0,
    "mount_pitch_mm": 44.0,
    "mount_hole_diameter_mm": 6.6,
    "saddle_diameter_mm": 20.2,
    "saddle_width_mm": 6.75,
    "saddle_outer_diameter_mm": 28.0,
    "center_through_diameter_mm": 6.6,
    "counterbore_diameter_mm": 11.0,
    "counterbore_depth_mm": 6.0,
    "overall_height_from_ball_center_mm": 39.0,
    "channel_width_mm": 18.5,
}


def _cylinder(radius: float, length: float, start, direction=(0, 0, 1)) -> cq.Shape:
    return cq.Solid.makeCylinder(radius, length, cq.Vector(*start), cq.Vector(*direction))


def _box(x: float, y: float, z: float, center) -> cq.Shape:
    return cq.Workplane("XY").box(x, y, z).val().translate(center)


def build_lower_plate(part_id: str) -> cq.Shape:
    """Return one A6061 plate; M8 threads are modelled as D6.8 tap holes."""
    if part_id not in LOWER_PLATE_SPECS:
        raise ValueError(f"Unknown lower plate {part_id!r}")
    spec = LOWER_PLATE_SPECS[part_id]
    solid = _box(120, 70, 8, (0, 0, 4))
    for x, y in spec["profile_through"]:
        solid = solid.cut(_cylinder(4.5, 10, (x, y, -1)))
    for x, y in spec["lmb_tap_m8"]:
        solid = solid.cut(_cylinder(3.4, 10, (x, y, -1)))
    return solid.clean()


def _mount_rotation_deg(axis_index: int) -> float:
    if axis_index not in (1, 2, 3):
        raise ValueError("axis_index must be 1, 2, or 3")
    _, tangent = revd_data.support_basis()[axis_index - 1]
    radial = (tangent[1], -tangent[0])
    return degrees(atan2(radial[1], radial[0]))


def build_upper_bracket(axis_index: int) -> cq.Shape:
    """Return the axis-specific supplier-finished PHS6 pocket bracket."""
    d = UPPER_BRACKET_SPEC
    angle = _mount_rotation_deg(axis_index)

    def rotate_z(shape: cq.Shape) -> cq.Shape:
        return shape.rotate((0, 0, 0), (0, 0, 1), angle)

    width = d["saddle_width_mm"]
    saddle = _cylinder(d["saddle_outer_diameter_mm"] / 2, width, (0, -width / 2, 0), (0, 1, 0))
    saddle = saddle.cut(
        _cylinder(d["saddle_diameter_mm"] / 2, width + 2, (0, -width / 2 - 1, 0), (0, 1, 0))
    )
    rails = _box(4, width, 34, (-12, 0, 17)).fuse(_box(4, width, 34, (12, 0, 17)))
    base = rotate_z(_box(60, 30, 9, (0, 0, 34.5)))
    bracket = saddle.fuse(rails).fuse(base)
    # Re-cut after fusing the rails so their inner corners cannot re-enter the
    # nominal D20.2 housing-clearance cylinder.
    bracket = bracket.cut(
        _cylinder(d["saddle_diameter_mm"] / 2, width + 2, (0, -width / 2 - 1, 0), (0, 1, 0))
    )
    # Side-open insertion route for the PHS6 housing and grease nipple.
    bracket = bracket.cut(_box(d["channel_width_mm"], 70, 24, (0, 25, 18)))
    # Central M6 clearance hole plus D11 x 6 counterbore from the top face.
    bracket = bracket.cut(_cylinder(d["center_through_diameter_mm"] / 2, 11, (0, 0, 29)))
    bracket = bracket.cut(_cylinder(d["counterbore_diameter_mm"] / 2, 6, (0, 0, 33)))
    for x in (-d["mount_pitch_mm"] / 2, d["mount_pitch_mm"] / 2):
        hole = rotate_z(_cylinder(d["mount_hole_diameter_mm"] / 2, 11, (x, 0, 29)))
        bracket = bracket.cut(hole)
    return bracket.clean()


def _write_lower_dxf(path: Path, part_id: str) -> None:
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 4
    for layer in ("CUT_OUTER", "DRILL_D9", "TAP_M8X1_25", "CENTER", "NOTES"):
        doc.layers.add(layer)
    msp = doc.modelspace()
    msp.add_lwpolyline([(-60, -35), (60, -35), (60, 35), (-60, 35)], close=True,
                       dxfattribs={"layer": "CUT_OUTER"})
    for point in LOWER_PLATE_SPECS[part_id]["profile_through"]:
        msp.add_circle(point, 4.5, dxfattribs={"layer": "DRILL_D9"})
    for point in LOWER_PLATE_SPECS[part_id]["lmb_tap_m8"]:
        msp.add_circle(point, 3.4, dxfattribs={"layer": "TAP_M8X1_25"})
    msp.add_line((-60, 0), (60, 0), dxfattribs={"layer": "CENTER"})
    msp.add_line((0, -35), (0, 35), dxfattribs={"layer": "CENTER"})
    msp.add_text(f"{part_id}: 120x70x8 A6061-T6; D9 THRU; M8x1.25 THRU (D6.8 PILOT)",
                 height=3, dxfattribs={"layer": "NOTES"}).set_placement((-58, -31))
    doc.saveas(path)


def _write_upper_dxf(path: Path, axis_index: int) -> None:
    """Mount-face DXF only; STEP controls the 3D saddle/pocket surfaces."""
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 4
    for layer in ("BASE_OUTLINE", "DRILL_D6_6", "COUNTERBORE_D11", "CENTER", "NOTES"):
        doc.layers.add(layer)
    msp = doc.modelspace()
    angle = _mount_rotation_deg(axis_index)
    rad = angle * 3.141592653589793 / 180
    c, s = __import__("math").cos(rad), __import__("math").sin(rad)

    def rot(point):
        x, y = point
        return (c * x - s * y, s * x + c * y)

    msp.add_lwpolyline([rot(p) for p in ((-30, -15), (30, -15), (30, 15), (-30, 15))],
                       close=True, dxfattribs={"layer": "BASE_OUTLINE"})
    for x in (-22, 22):
        msp.add_circle(rot((x, 0)), 3.3, dxfattribs={"layer": "DRILL_D6_6"})
    msp.add_circle((0, 0), 3.3, dxfattribs={"layer": "DRILL_D6_6"})
    msp.add_circle((0, 0), 5.5, dxfattribs={"layer": "COUNTERBORE_D11"})
    msp.add_line(rot((-30, 0)), rot((30, 0)), dxfattribs={"layer": "CENTER"})
    msp.add_text(
        f"UP-A{axis_index}: MOUNT FACE ONLY. STEP CONTROLS D20.2 SADDLE/POCKET. D6.6 x3; CB D11 DEPTH6.",
        height=2.5, dxfattribs={"layer": "NOTES"},
    ).set_placement((-34, -34))
    doc.saveas(path)


def _write_hole_table(path: Path) -> None:
    rows = []
    for part_id, spec in LOWER_PLATE_SPECS.items():
        for index, (x, y) in enumerate(spec["profile_through"], 1):
            rows.append((part_id, f"P{index}", x, y, "D9 THRU", "profile fastening"))
        for index, (x, y) in enumerate(spec["lmb_tap_m8"], 1):
            rows.append((part_id, f"T{index}", x, y, "M8x1.25 THRU; drill D6.8", "LMB-10 fastening"))
    for axis in (1, 2, 3):
        angle = _mount_rotation_deg(axis)
        rows.extend([
            (f"UP-A{axis}", "M1", -22.0, 0.0, "D6.6 THRU", f"rotate mount face {angle:.3f} deg in STEP"),
            (f"UP-A{axis}", "M2", 22.0, 0.0, "D6.6 THRU", f"rotate mount face {angle:.3f} deg in STEP"),
            (f"UP-A{axis}", "C1", 0.0, 0.0, "D6.6 THRU + CB D11 x 6", "PHS6 M6 retainer"),
        ])
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow(("part_id", "hole_id", "x_mm", "y_mm", "callout", "note"))
        writer.writerows(rows)


def export_quote_package(output_dir: Path, include_pdf: bool = True) -> dict:
    """Export six STEP/DXF files, coordinates and a machine-readable manifest."""
    output_dir.mkdir(parents=True, exist_ok=True)
    step_dir, dxf_dir = output_dir / "step", output_dir / "dxf"
    step_dir.mkdir(exist_ok=True)
    dxf_dir.mkdir(exist_ok=True)
    step_files, dxf_files = [], []
    for part_id in LOWER_PLATE_SPECS:
        step = step_dir / f"{part_id}_LOWER_LMB_ADAPTER_120x70x8.step"
        dxf = dxf_dir / f"{part_id}_LOWER_LMB_ADAPTER_120x70x8.dxf"
        cq.exporters.export(build_lower_plate(part_id), str(step), exportType="STEP")
        _write_lower_dxf(dxf, part_id)
        step_files.append(step)
        dxf_files.append(dxf)
    for axis in (1, 2, 3):
        step = step_dir / f"UP_A{axis}_PHS6_POCKET_BRACKET.step"
        dxf = dxf_dir / f"UP_A{axis}_PHS6_POCKET_MOUNT_FACE.dxf"
        cq.exporters.export(build_upper_bracket(axis), str(step), exportType="STEP")
        _write_upper_dxf(dxf, axis)
        step_files.append(step)
        dxf_files.append(dxf)
    hole_table = output_dir / "RevF_hole_coordinate_table.csv"
    _write_hole_table(hole_table)
    manifest = {
        "package": "Rev F quotation candidate",
        "scope": "supervised indoor self-weight PoC; no cart, payload, or person",
        "step_files": step_files,
        "dxf_files": dxf_files,
        "hole_table": hole_table,
        "upper_bracket_spec": UPPER_BRACKET_SPEC,
        "lower_plate_spec": LOWER_PLATE_SPEC,
        "warnings": [
            "PRELIMINARY POC DESIGN - vendor DFM review required",
            "DXF for upper brackets is mounting-face reference only; STEP controls the 3D pocket",
            "M8 threads are modelled as D6.8 tap holes",
            "No claim of certification, human carrying, or field safety",
        ],
    }
    json_path = output_dir / "manifest.json"
    serializable = dict(manifest)
    serializable.update(
        step_files=[str(p.relative_to(output_dir)) for p in step_files],
        dxf_files=[str(p.relative_to(output_dir)) for p in dxf_files],
        hole_table=str(hole_table.relative_to(output_dir)),
    )
    json_path.write_text(json.dumps(serializable, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest["manifest"] = json_path
    if include_pdf:
        from scripts.build_revf_quote_package import build_drawing_pdf

        manifest["drawing_pdf"] = build_drawing_pdf(output_dir)
    return manifest
