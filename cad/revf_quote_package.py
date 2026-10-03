"""Rev F quotation/fabrication-review geometry for six custom metal parts.

The package is intentionally small: three drilled/tapped A6061 plates and
three supplier-finished S45C upper pockets.  The authoritative lower STEP
files contain a geometric M8 x 1.25 internal-thread representation.  A second
set with D6.8 tap-drill cylinders is exported for quotation systems that do
not accept detailed helical threads; drawings and the hole table control the
manufacturing callout in both cases.
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
    "material": "A6061-T6 or A6061P-T651",
    "length_mm": 120.0,
    "width_mm": 70.0,
    "thickness_mm": 8.0,
    "profile_hole_diameter_mm": 9.0,
    "tap_drill_diameter_mm": 6.8,
    "thread_nominal_diameter_mm": 8.0,
    "thread_pitch_mm": 1.25,
    "thread": "M8x1.25 THROUGH",
    "minimum_required_thread_engagement_mm": 6.0,
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
    "counterbore_entry_face": "TOP",
    "overall_height_from_ball_center_mm": 39.0,
    "channel_width_mm": 18.5,
}


def _cylinder(radius: float, length: float, start, direction=(0, 0, 1)) -> cq.Shape:
    return cq.Solid.makeCylinder(radius, length, cq.Vector(*start), cq.Vector(*direction))


def _box(x: float, y: float, z: float, center) -> cq.Shape:
    return cq.Workplane("XY").box(x, y, z).val().translate(center)


def _m8_internal_thread_cutter() -> cq.Shape:
    """Return a visual/manufacturing M8x1.25 through-thread cutting solid.

    The pilot bore remains D6.8.  The swept 60-degree V groove reaches the
    nominal D8 major diameter and is extended 1 mm beyond both plate faces so
    the resulting STEP has an unambiguous through-thread representation.
    Drawings remain authoritative for tolerance and thread class.
    """
    pitch = LOWER_PLATE_SPEC["thread_pitch_mm"]
    pilot_radius = LOWER_PLATE_SPEC["tap_drill_diameter_mm"] / 2
    major_radius = LOWER_PLATE_SPEC["thread_nominal_diameter_mm"] / 2
    z_start = -1.0
    height = LOWER_PLATE_SPEC["thickness_mm"] + 2.0
    helix = cq.Wire.makeHelix(pitch, height, pilot_radius, center=(0, 0, z_start))
    half_width = (major_radius - (pilot_radius - 0.05)) / (3**0.5)
    profile = (
        cq.Workplane("XZ", origin=(0, 0, z_start))
        .moveTo(pilot_radius - 0.05, -half_width)
        .lineTo(major_radius, 0)
        .lineTo(pilot_radius - 0.05, half_width)
        .close()
    )
    return profile.sweep(helix, isFrenet=False, combine=False).val()


def build_lower_plate(part_id: str, *, model_threads: bool = True) -> cq.Shape:
    """Return one A6061 plate with detailed or quote-safe M8 tap geometry."""
    if part_id not in LOWER_PLATE_SPECS:
        raise ValueError(f"Unknown lower plate {part_id!r}")
    spec = LOWER_PLATE_SPECS[part_id]
    solid = _box(120, 70, 8, (0, 0, 4))
    for x, y in spec["profile_through"]:
        solid = solid.cut(_cylinder(4.5, 10, (x, y, -1)))
    for x, y in spec["lmb_tap_m8"]:
        solid = solid.cut(_cylinder(3.4, 10, (x, y, -1)))
        if model_threads:
            solid = solid.cut(_m8_internal_thread_cutter().translate((x, y, 0)))
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
            (f"UP-A{axis}", "C1", 0.0, 0.0, "D6.6 THRU + CB D11 x 6 FROM TOP", "PHS6 M6 retainer"),
        ])
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow(("part_id", "hole_id", "x_mm", "y_mm", "callout", "note"))
        writer.writerows(rows)


def _write_readme(path: Path) -> None:
    path.write_text(
        """# Rev F 맞춤부품 STEP·가공도 사용 안내

이 폴더에는 감독하 실내 자중 시연용 맞춤 금속부품 6개의 발주 자료가 들어 있다. 카트·적재물·사람 탑승 용도가 아니다.

## STEP 파일 구분

- `step/`: 가공사항을 형상에 반영한 기준 STEP 6개. 하부판은 M8×1.25 실제 나사산 형상을 포함한다.
- `step_quote_simplified/`: 상세 나사산 STEP을 읽지 못하는 견적 사이트용 하부판 STEP 3개. 나사 위치는 Ø6.8 밑구멍으로 단순화했지만 **M8×1.25 관통 탭 가공 지시는 그대로 유효**하다.
- 상부 포켓의 3차원 형상은 `step/UP_*.step`이 우선하며, 상부 DXF는 장착면 참고용이다.

## 하부 A1~A3 어댑터판

- 재질: A6061-T6 또는 A6061P-T651
- 외형: 120×70×8 mm
- 각 판: 프로파일 체결 Ø9 관통 2개
- 각 판: LMB-10 체결 Ø6.8 밑구멍 후 M8×1.25 관통 탭 2개
- 각 축의 홀 좌표가 다르므로 `RevF_hole_coordinate_table.csv` 또는 개별 DXF를 따른다.
- 나사산 공차·탭 등급은 STEP 나사산 형상이 아니라 가공도 지시가 우선한다.

## 상부 A1~A3 포켓 브래킷

- 재질: S45C/SM45C, 열처리·도금 없음
- 베이스 60×30×9 mm, 장착 Ø6.6 관통 2개/피치 44 mm
- PHS6 안장 Ø20.2×폭 6.75 mm, 외측 Ø28 mm, 삽입 채널 폭 18.5 mm
- 중앙 Ø6.6 관통 후 **상면에서 Ø11×깊이 6 mm 카운터보어**
- STEP 전체 형상 가공 후 디버링, 일반공차 우선 ±0.2 mm

## 조립 전 확인

하부 M8 볼트는 LMB-10 바닥과 와셔를 지난 뒤 판에 6~8 mm 물리고 판 아래로 돌출되지 않는 길이를 사용한다. 실제 LMB-10 바닥 두께를 측정한 뒤 볼트 길이를 결정한다. 이 자료는 시제품 견적·조립용이며 강도 인증이나 사람 탑승 적합성을 의미하지 않는다.
""",
        encoding="utf-8",
    )


def export_quote_package(output_dir: Path, include_pdf: bool = True) -> dict:
    """Export six STEP/DXF files, coordinates and a machine-readable manifest."""
    output_dir.mkdir(parents=True, exist_ok=True)
    step_dir = output_dir / "step"
    quote_simplified_step_dir = output_dir / "step_quote_simplified"
    dxf_dir = output_dir / "dxf"
    step_dir.mkdir(exist_ok=True)
    quote_simplified_step_dir.mkdir(exist_ok=True)
    dxf_dir.mkdir(exist_ok=True)
    step_files, quote_simplified_step_files, dxf_files = [], [], []
    for part_id in LOWER_PLATE_SPECS:
        step = step_dir / f"{part_id}_LOWER_LMB_ADAPTER_120x70x8.step"
        quote_simplified_step = (
            quote_simplified_step_dir
            / f"{part_id}_LOWER_LMB_ADAPTER_120x70x8_D6.8_PILOT_M8_TAP_CALLOUT.step"
        )
        dxf = dxf_dir / f"{part_id}_LOWER_LMB_ADAPTER_120x70x8.dxf"
        cq.exporters.export(build_lower_plate(part_id, model_threads=True), str(step), exportType="STEP")
        cq.exporters.export(
            build_lower_plate(part_id, model_threads=False),
            str(quote_simplified_step),
            exportType="STEP",
        )
        _write_lower_dxf(dxf, part_id)
        step_files.append(step)
        quote_simplified_step_files.append(quote_simplified_step)
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
    readme = output_dir / "README_견적업로드.md"
    _write_readme(readme)
    manifest = {
        "package": "Rev F quotation candidate",
        "scope": "supervised indoor self-weight PoC; no cart, payload, or person",
        "step_files": step_files,
        "quote_simplified_step_files": quote_simplified_step_files,
        "dxf_files": dxf_files,
        "hole_table": hole_table,
        "readme": readme,
        "upper_bracket_spec": UPPER_BRACKET_SPEC,
        "lower_plate_spec": LOWER_PLATE_SPEC,
        "warnings": [
            "PRELIMINARY POC DESIGN - vendor DFM review required",
            "DXF for upper brackets is mounting-face reference only; STEP controls the 3D pocket",
            "Authoritative lower STEP files contain modeled M8x1.25 threads; drawings control thread class",
            "Quote-simplified lower STEP files show D6.8 pilot holes and still require M8x1.25 through tapping",
            "No claim of certification, human carrying, or field safety",
        ],
    }
    json_path = output_dir / "manifest.json"
    serializable = dict(manifest)
    serializable.update(
        step_files=[str(p.relative_to(output_dir)) for p in step_files],
        quote_simplified_step_files=[str(p.relative_to(output_dir)) for p in quote_simplified_step_files],
        dxf_files=[str(p.relative_to(output_dir)) for p in dxf_files],
        hole_table=str(hole_table.relative_to(output_dir)),
        readme=str(readme.relative_to(output_dir)),
    )
    json_path.write_text(json.dumps(serializable, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest["manifest"] = json_path
    if include_pdf:
        from scripts.build_revf_quote_package import build_drawing_pdf

        manifest["drawing_pdf"] = build_drawing_pdf(output_dir)
    return manifest
