"""Export the corrected 120-degree radial 3-RPS Rev C review package."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from pathlib import Path

import cadquery as cq
import ezdxf
import vtk

from cad.minimal_radial_revc import (
    C,
    POSES,
    _shape,
    actuator_joint_points,
    actuator_pin_lengths,
    assembly_bounds,
    components_for_pose,
    connector_axis_audit,
    hub_mount_points,
    joint_axis_audit,
    lmb_tap_points,
    named_collision_volume,
    profile_cut_list,
    stop_sweep_audit,
    support_azimuth_audit,
    workspace_audit,
)


ROOT = Path(__file__).resolve().parents[1]
REVISION = "C"
OUTPUT = ROOT / "outputs" / "minimal_radial_revC"
STEP_DIR = OUTPUT / "step"
RENDER_DIR = OUTPUT / "renders"
TABLE_DIR = OUTPUT / "tables"
VERIFY_DIR = OUTPUT / "verification"
DOCUMENT_DIR = OUTPUT / "documents"
FAB_DIR = OUTPUT / "fabrication"
PACKAGE = ROOT / "output" / "Minimal_3RPS_Radial_RevC_Fusion360.zip"

GROUPS = (
    "lower_frame",
    "lower_connectors",
    "lower_fasteners",
    "lower_hub",
    "lower_joints",
    "upper_frame",
    "upper_connectors",
    "upper_fasteners",
    "upper_joints",
    "actuators",
    "actuator_eyes",
    "mechanical_stops",
)

EXPLODED_OFFSETS = {
    "lower_frame": 0.0,
    "lower_connectors": 10.0,
    "lower_fasteners": 25.0,
    "lower_hub": 80.0,
    "lower_joints": 125.0,
    "actuators": 205.0,
    "actuator_eyes": 205.0,
    "mechanical_stops": 125.0,
    "upper_joints": 330.0,
    "upper_fasteners": 360.0,
    "upper_frame": 410.0,
    "upper_connectors": 410.0,
}

CAMERAS = {
    "collapsed_iso": ((1120, -1320, 820), (0, 0, 145), (0, 0, 1), 590),
    "raised_iso": ((1120, -1320, 900), (0, 0, 170), (0, 0, 1), 600),
    "tilt_iso": ((1120, -1320, 900), (0, 0, 170), (0, 0, 1), 600),
    "top": ((0, 0, 1700), (0, 0, 150), (0, 1, 0), 450),
    "front": ((0, -1500, 260), (0, 0, 145), (0, 0, 1), 410),
    "exploded": ((1400, -1550, 1320), (0, 0, 400), (0, 0, 1), 750),
    "joint": ((520, -630, 380), (10, 105, 145), (0, 0, 1), 265),
    "connector": ((360, -430, 260), (-290, 300, 20), (0, 0, 1), 120),
    "hub": ((0, 0, 900), (0, 0, 55), (0, 1, 0), 190),
}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _selected_parts(pose_name, detail=None):
    parts = components_for_pose(POSES[pose_name])
    if detail == "joint":
        keep = {"upper_cross_A1", "lower_hub_plate_280x220x10"}
        parts = [
            part
            for part in parts
            if "A1" in part.name or part.name in keep
        ]
    elif detail == "connector":
        prefixes = (
            "lower_outer_side_L",
            "lower_cross_F",
            "lower_4035_1_L",
        )
        parts = [part for part in parts if part.name.startswith(prefixes)]
    elif detail == "hub":
        parts = [
            part
            for part in parts
            if part.group in {"lower_hub", "lower_joints"}
            or (part.group == "lower_fasteners" and "LMB10" in part.name)
        ]
    return parts


def hierarchical_assembly(pose_name, exploded=False, groups=None, detail=None):
    parts = _selected_parts(pose_name, detail)
    selected = tuple(groups) if groups is not None else GROUPS
    root = cq.Assembly(name=f"MINIMAL_RADIAL_{pose_name.upper()}_REV{REVISION}")
    for group in selected:
        sub = cq.Assembly(name=group.upper())
        for part in (item for item in parts if item.group == group):
            shape = part.shape
            if exploded:
                shape = shape.translate((0.0, 0.0, EXPLODED_OFFSETS[group]))
            r, g, b, a = part.color
            sub.add(shape, name=part.name, color=cq.Color(r, g, b, a))
        root.add(sub, name=group.upper())
    return root


def export_steps():
    STEP_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    for pose_name in POSES:
        path = STEP_DIR / f"MINIMAL_3RPS_radial_{pose_name}_rev{REVISION}.step"
        hierarchical_assembly(pose_name).save(str(path), exportType="STEP", mode="default")
        outputs.append(path)

    exploded = STEP_DIR / f"MINIMAL_3RPS_radial_exploded_rev{REVISION}.step"
    hierarchical_assembly("neutral", exploded=True).save(
        str(exploded), exportType="STEP", mode="default"
    )
    outputs.append(exploded)

    subassemblies = {
        "SUB_01_LOWER_FRAME_HUB": (
            "lower_frame",
            "lower_connectors",
            "lower_fasteners",
            "lower_hub",
            "lower_joints",
        ),
        "SUB_02_UPPER_PROFILE_FRAME": (
            "upper_frame",
            "upper_connectors",
            "upper_fasteners",
            "upper_joints",
        ),
        "SUB_03_THREE_ACTUATORS": ("actuators", "actuator_eyes"),
        "SUB_04_MECHANICAL_STOPS": ("mechanical_stops",),
    }
    for name, groups in subassemblies.items():
        path = STEP_DIR / f"{name}_collapsed_rev{REVISION}.step"
        hierarchical_assembly("collapsed", groups=groups).save(
            str(path), exportType="STEP", mode="default"
        )
        outputs.append(path)

    for label, detail in (
        ("DETAIL_A1_COMPLETE_JOINT", "joint"),
        ("DETAIL_4035_COPLANAR_CORNER", "connector"),
        ("DETAIL_LOWER_HUB_AND_LMB", "hub"),
    ):
        path = STEP_DIR / f"{label}_rev{REVISION}.step"
        hierarchical_assembly("collapsed", detail=detail).save(
            str(path), exportType="STEP", mode="default"
        )
        outputs.append(path)
    return outputs


def actor_for(part, offset=0.0):
    shape = part.shape.translate((0.0, 0.0, offset)) if offset else part.shape
    vertices, triangles = _shape(shape).tessellate(1.8, 0.35)
    points = vtk.vtkPoints()
    for vertex in vertices:
        points.InsertNextPoint(vertex.x, vertex.y, vertex.z)
    cells = vtk.vtkCellArray()
    for triangle in triangles:
        cell = vtk.vtkTriangle()
        for index, point_id in enumerate(triangle):
            cell.GetPointIds().SetId(index, point_id)
        cells.InsertNextCell(cell)
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    polydata.SetPolys(cells)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(polydata)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(*part.color[:3])
    actor.GetProperty().SetOpacity(part.color[3])
    actor.GetProperty().SetInterpolationToPhong()
    return actor


def render_view(filename, camera_name, pose_name="collapsed", exploded=False, detail=None):
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.96, 0.97, 0.98)
    parts = _selected_parts(pose_name, detail)
    for part in parts:
        offset = EXPLODED_OFFSETS[part.group] if exploded else 0.0
        renderer.AddActor(actor_for(part, offset))

    view_label = "EXPLODED" if exploded else pose_name.upper()
    title = vtk.vtkTextActor()
    title.SetInput(
        f"120-DEG RADIAL 3-RPS REV {REVISION} | {view_label}"
        f" | {len(parts)} COMPONENTS"
    )
    title.SetPosition(28, 842)
    title.GetTextProperty().SetFontSize(21)
    title.GetTextProperty().SetBold(True)
    title.GetTextProperty().SetColor(0.05, 0.09, 0.13)
    title.GetTextProperty().SetBackgroundColor(0.96, 0.97, 0.98)
    title.GetTextProperty().SetBackgroundOpacity(0.92)

    footer = vtk.vtkTextActor()
    footer.SetInput(
        "PRELIMINARY - NOT FOR FABRICATION | BLACK=PROFILE | SILVER=HUB/JOINT | YELLOW=ACTUATOR"
    )
    footer.SetPosition(28, 22)
    footer.GetTextProperty().SetFontSize(14)
    footer.GetTextProperty().SetColor(0.35, 0.08, 0.04)
    footer.GetTextProperty().SetBackgroundColor(0.96, 0.97, 0.98)
    footer.GetTextProperty().SetBackgroundOpacity(0.92)
    overlay = vtk.vtkRenderer()
    overlay.SetLayer(1)
    overlay.SetInteractive(False)
    overlay.SetBackgroundAlpha(0.0)
    overlay.AddViewProp(title)
    overlay.AddViewProp(footer)

    position, focal, up, scale = CAMERAS[camera_name]
    camera = vtk.vtkCamera()
    camera.SetPosition(*position)
    camera.SetFocalPoint(*focal)
    camera.SetViewUp(*up)
    camera.ParallelProjectionOn()
    camera.SetParallelScale(scale)
    renderer.SetActiveCamera(camera)
    renderer.ResetCameraClippingRange()

    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(True)
    window.SetSize(1400, 900)
    window.SetNumberOfLayers(2)
    renderer.SetLayer(0)
    window.AddRenderer(renderer)
    window.AddRenderer(overlay)
    window.Render()
    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.SetInputBufferTypeToRGB()
    capture.ReadFrontBufferOff()
    capture.Update()
    filename.parent.mkdir(parents=True, exist_ok=True)
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(filename))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()
    window.Finalize()
    return filename


def render_all():
    return [
        render_view(RENDER_DIR / "01_collapsed_iso.png", "collapsed_iso"),
        render_view(RENDER_DIR / "02_raised_iso.png", "raised_iso", "raised"),
        render_view(RENDER_DIR / "03_max_pitch_roll_iso.png", "tilt_iso", "max_pitch_roll"),
        render_view(RENDER_DIR / "04_top_120deg_layout.png", "top"),
        render_view(RENDER_DIR / "05_front.png", "front"),
        render_view(RENDER_DIR / "06_exploded.png", "exploded", "neutral", exploded=True),
        render_view(RENDER_DIR / "07_A1_joint_detail.png", "joint", detail="joint"),
        render_view(RENDER_DIR / "08_4035_connector_detail.png", "connector", detail="connector"),
        render_view(RENDER_DIR / "09_lower_hub_detail.png", "hub", detail="hub"),
    ]


def write_hub_dxf_and_table():
    FAB_DIR.mkdir(parents=True, exist_ok=True)
    dxf_path = FAB_DIR / "LOWER_HUB_280x220x10_revC.dxf"
    doc = ezdxf.new("R2010")
    doc.layers.add("OUTLINE", color=7)
    doc.layers.add("M8_CLEARANCE_D9", color=3)
    doc.layers.add("M8_TAP_DRILL_D6_8", color=1)
    model = doc.modelspace()
    half_x = C.lower_hub_length_mm / 2.0
    half_y = C.lower_hub_width_mm / 2.0
    model.add_lwpolyline(
        [(-half_x, -half_y), (half_x, -half_y), (half_x, half_y), (-half_x, half_y)],
        close=True,
        dxfattribs={"layer": "OUTLINE"},
    )
    for point in hub_mount_points():
        model.add_circle(point, 4.5, dxfattribs={"layer": "M8_CLEARANCE_D9"})
    for point in lmb_tap_points():
        model.add_circle(point, 3.4, dxfattribs={"layer": "M8_TAP_DRILL_D6_8"})
    doc.saveas(dxf_path)

    table_path = TABLE_DIR / "lower_hub_hole_table.csv"
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    with table_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(("hole_id", "x_mm", "y_mm", "operation", "quantity_group"))
        for index, (x, y) in enumerate(hub_mount_points(), start=1):
            writer.writerow((f"HC{index:02d}", f"{x:.3f}", f"{y:.3f}", "THRU DIA9", "hub-to-4040"))
        for index, (x, y) in enumerate(lmb_tap_points(), start=1):
            writer.writerow((f"HT{index:02d}", f"{x:.3f}", f"{y:.3f}", "DRILL DIA6.8 THEN TAP M8x1.25", "LMB-to-hub"))
    return dxf_path, table_path


def write_tables(parts):
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    manifest = TABLE_DIR / "component_manifest.csv"
    with manifest.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(("component_name", "group", "bom_key", "material", "status", "notes"))
        for part in parts:
            writer.writerow((part.name, part.group, part.bom_key, part.material, part.status, part.notes))

    cut = TABLE_DIR / "profile_cut_list.csv"
    sku = {
        "4040 x 700": "K92787708",
        "4040 x 620": "K92787705",
        "3030 x 700": "K42296106",
        "3030 x 640": "K42296071",
    }
    with cut.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(("profile", "length_mm", "quantity", "navimro_sku", "operation"))
        for key, quantity in profile_cut_list().items():
            profile, length = key.split(" x ")
            writer.writerow((profile, length, quantity, sku[key], "square cut and deburr"))

    bom = TABLE_DIR / "mechanical_BOM.csv"
    rows = [
        ("P01", "DNF4040 M8-slot extrusion 700 mm", 2, "K92787708", "CORE_GEOMETRY_PASS"),
        ("P02", "DNF4040 M8-slot extrusion 620 mm", 4, "K92787705", "CORE_GEOMETRY_PASS"),
        ("P03", "DNF3030-6 M6-slot extrusion 700 mm", 2, "K42296106", "CORE_GEOMETRY_PASS"),
        ("P04", "DNF3030-6 M6-slot extrusion 640 mm", 4, "K42296071", "CORE_GEOMETRY_PASS"),
        ("C01", "4035 40-series bracket", 8, "K92782553", "TWO_HORIZONTAL_AXES_MODELED"),
        ("C02", "DCB3025 30-series bracket", 8, "K56842696", "TWO_HORIZONTAL_AXES_MODELED"),
        ("H01", "A6061-T6 lower hub 280x220x10", 1, "CUSTOM", "FIRST_ARTICLE_REQUIRED"),
        ("J01", "LM4075OE-1075 24 V 100 mm encoder", 3, "MOTIONGEARON", "EYE_WIDTH_OPEN"),
        ("J02", "LMB-10 lower clevis", 3, "MOTORBANK", "PIN_INCLUSION_CONFIRM"),
        ("J03", "THK PHS6 female rod end", 3, "THK", "PUBLISHED_DIMENSION_PASS"),
        ("S01", "M10 independent mechanical stop set", 3, "CUSTOM/CATALOG", "MOUNT_DETAIL_OPEN"),
    ]
    with bom.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(("item", "description", "quantity", "supplier_or_sku", "status"))
        writer.writerows(rows)

    fasteners = TABLE_DIR / "fastener_schedule.csv"
    fastener_rows = [
        ("F01", "M8x20 bolt", 24, "K53672490", "4035 16 + hub 8"),
        ("F02", "SP408 M8 spring nut", 24, "K14671419", "lower profiles"),
        ("F03", "M6x15 button socket bolt", 16, "K14333089", "DCB3025"),
        ("F04", "SP306 M6 spring nut", 16, "K14671215", "upper profiles"),
        ("F05", "M8x16 screw plus flat/spring washer", 6, "K53672478 family", "LMB to tapped hub"),
        ("F06", "TB306 M6x20 T-bolt", 3, "K55868014", "PHS6 to 3030"),
        ("F07", "M6x50 partial-thread bolt", 3, "K53672105", "upper eye joint"),
        ("F08", "M6 washer", 6, "K14530259", "upper eye joint"),
        ("F09", "M6 prevailing nut and ID6 shim", 3, "SKU_OPEN", "after one-axis fit"),
    ]
    with fasteners.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(("item", "description", "used_quantity", "sku", "note"))
        writer.writerows(fastener_rows)
    return manifest, cut, bom, fasteners


def write_assembly_guide(parts):
    workspace = workspace_audit()
    axis = joint_axis_audit()
    bounds = assembly_bounds(POSES["collapsed"])
    text = f"""# Fusion 360 가져오기 및 조립 검토 가이드 - Rev {REVISION}

## 현재 상태

Rev C는 Rev B의 체결축·핀축·120도 배치 오류를 수정한 예비 디지털 조립이다. 핵심 프레임, 소형 허브, 3-RPS 운동학과 대표 자세 간섭은 통과했지만, LM4075OE 실제 아이 폭과 독립 스토퍼 장착 스탠드오프가 남아 있어 제작 릴리스는 아니다.

## Fusion 360 권장 파일

`step/MINIMAL_3RPS_radial_collapsed_revC.step`를 업로드한다. {len(parts)}개 위치 부품이 이름별로 들어 있다. `DETAIL_A1_COMPLETE_JOINT_revC.step`, `DETAIL_4035_COPLANAR_CORNER_revC.step`, `DETAIL_LOWER_HUB_AND_LMB_revC.step`를 함께 열어 체결 방향을 확인한다.

## 기준값

- 접힘 포락체: {bounds['xlen']:.0f} x {bounds['ylen']:.0f} x {bounds['zlen']:.0f} mm.
- Z 0~50 mm, pitch/roll 각각 +/-3 deg.
- 지지점: 90/210/330 deg, 간격 120/120/120 deg.
- 요구 핀 중심거리: {workspace['required_min_pin_mm']:.3f}~{workspace['required_max_pin_mm']:.3f} mm.
- PHS6 최대 구면 꺾임: {axis['maximum_phs_articulation_deg']:.3f} deg.

## 조립 순서

1. 하부 4040 프레임을 700 mm 측면 2개와 620 mm 가로 4개로 놓는다. 4035는 프레임 위가 아니라 각 접합부 안쪽 모서리에 세우고, 한 볼트는 X축, 다른 볼트는 Y축으로 측면 슬롯에 체결한다.
2. 280x220x10 허브판을 Y=+/-80 mm 가로 프로파일 위에 놓고 Ø9 홀 8개를 M8x20+SP408로 체결한다.
3. LMB-10 세 개를 허브의 M8 탭에 축당 두 개씩 체결한다. 각 두 번째 탭은 핀 중심에서 반경 안쪽 36 mm다.
4. 하부 액추에이터 아이를 LMB 내폭 20 mm 안에 넣고 실제 공급 핀·리테이너로 고정한다. 아이 폭을 먼저 측정한다.
5. 상부 3030 프레임을 700 mm 측면 2개와 640 mm 가로 4개로 조립한다. DCB3025도 안쪽 수직 코너에 두고 수평 X/Y축 M6 체결을 사용한다.
6. PHS6을 A1=(0,250), A2=(-216.506,-125), A3=(216.506,-125) mm에서 TB306 M6x20과 잼너트로 하부 슬롯에 고정한다.
7. PHS6 내륜과 액추에이터 상부 아이를 M6x50 부분나사 볼트로 단측 연결한다. 실제 아이 폭에 맞춰 와셔·심을 정하고 내륜을 압착하지 않는 풀림방지너트를 사용한다.
8. 독립 M10 스토퍼는 장착 스탠드오프가 확정된 뒤 설치한다. 전기 종단 리미트는 이 기계 스토퍼를 대체하지 않는다.
9. 무부하·저속으로 축별 구동, 공통 Z, pitch, roll 순서로 시험하며 전류·엔코더 방향·핀 유지·케이블과 스토퍼 접촉을 확인한다.

## 허브 제작

`fabrication/LOWER_HUB_280x220x10_revC.dxf`와 `tables/lower_hub_hole_table.csv`를 사용한다. 외형 직사각 절단, Ø9 관통홀 8개, Ø6.8 탭드릴 후 M8x1.25 탭 6개다. 탭 유효깊이는 9 mm 이상으로 요구한다.

이 설계는 고정식 실내 저속 10 kg PoC 검토안이며 사람 운반이나 인증 적합성을 의미하지 않는다.
"""
    path = OUTPUT / "FUSION360_IMPORT_AND_ASSEMBLY_GUIDE.md"
    path.write_text(text, encoding="utf-8")
    return path


def copy_supporting_documents():
    DOCUMENT_DIR.mkdir(parents=True, exist_ok=True)
    sources = (
        ROOT / "design_basis" / "minimal_radial_revC_2026-08-31.md",
        ROOT / "procurement" / "minimal_radial_revC_structural_bom_2026-08-31.md",
        ROOT / "design_basis" / "revB_assembly_reaudit_2026-08-31.md",
        ROOT / "procurement" / "electrical_control_completeness_2026-08-28.md",
    )
    outputs = []
    for source in sources:
        target = DOCUMENT_DIR / source.name
        shutil.copy2(source, target)
        outputs.append(target)
    return outputs


def run_validation(step_paths):
    fixed = {
        "lower_frame",
        "lower_connectors",
        "lower_hub",
        "lower_joints",
        "upper_frame",
        "upper_connectors",
    }
    body_collisions = {
        name: named_collision_volume(pose, {"actuators"}, fixed)
        for name, pose in POSES.items()
    }
    eye_collisions = {
        name: named_collision_volume(
            pose,
            {"actuator_eyes"},
            {"lower_frame", "lower_hub", "upper_frame"},
        )
        for name, pose in POSES.items()
    }
    workspace = workspace_audit()
    joints = joint_axis_audit()
    supports = support_azimuth_audit()
    connectors = connector_axis_audit()
    stops = stop_sweep_audit()
    collisions_pass = max(body_collisions.values()) < 0.001 and max(eye_collisions.values()) < 0.001
    selected = STEP_DIR / f"MINIMAL_3RPS_radial_collapsed_rev{REVISION}.step"
    imported = cq.importers.importStep(str(selected)).val()
    core_pass = (
        workspace["passes"]
        and joints["passes"]
        and supports["passes"]
        and connectors["passes"]
        and stops["passes"]
        and collisions_pass
    )
    result = {
        "revision": REVISION,
        "status": "DIGITAL_CORE_ASSEMBLY_PASS_EYE_WIDTH_AND_STOP_MOUNT_OPEN" if core_pass else "DIGITAL_CHECK_FAILED",
        "fabrication_release": False,
        "purchase_release": False,
        "component_count": len(components_for_pose(POSES["collapsed"])),
        "structural_full_size_plate_count": 0,
        "small_custom_hub_plate_count": 1,
        "welding_required": False,
        "workspace": workspace,
        "joint_axis_alignment": joints,
        "support_azimuth": supports,
        "connector_axes": connectors,
        "mechanical_stop_sweep": stops,
        "bounds": {name: assembly_bounds(pose) for name, pose in POSES.items()},
        "actuator_body_collision_volume_mm3": body_collisions,
        "actuator_eye_collision_volume_mm3": eye_collisions,
        "digital_core_checks_pass": core_pass,
        "step_reverse_import": {
            "file": str(selected.relative_to(ROOT)).replace("\\", "/"),
            "solid_count": len(imported.Solids()),
            "volume_mm3": imported.Volume(),
            "passes": len(imported.Solids()) > 0 and imported.Volume() > 0.0,
        },
        "step_file_count": len(step_paths),
        "collapsed_pin_lengths_mm": actuator_pin_lengths(POSES["collapsed"]),
        "open_items": [
            "LM4075OE delivered eye axial width and vendor STEP",
            "LMB-10 included pin and positive retainer",
            "M6x50 upper joint measured washer/shim stack",
            "independent stop catch mounting standoff and exact SKU",
            "one lower hub first-article hole/tap and wrench-access check",
        ],
    }
    VERIFY_DIR.mkdir(parents=True, exist_ok=True)
    path = VERIFY_DIR / "minimal_radial_revC_validation.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path, result


def write_manifest(validation):
    rows = []
    for path in sorted(OUTPUT.rglob("*")):
        if path.is_file() and path.name != "artifact_manifest.json":
            rows.append(
                {
                    "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )
    path = OUTPUT / "artifact_manifest.json"
    path.write_text(
        json.dumps(
            {
                "revision": REVISION,
                "status": validation["status"],
                "artifact_count": len(rows),
                "component_count": validation["component_count"],
                "artifacts": rows,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def package_zip():
    PACKAGE.parent.mkdir(parents=True, exist_ok=True)
    if PACKAGE.exists():
        PACKAGE.unlink()
    shutil.make_archive(str(PACKAGE.with_suffix("")), "zip", OUTPUT)
    return PACKAGE


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    parts = components_for_pose(POSES["collapsed"])
    print(f"[1/7] export STEP assemblies ({len(parts)} modeled components)")
    step_paths = export_steps()
    print("[2/7] render review set")
    render_all()
    print("[3/7] write hub DXF and hole table")
    write_hub_dxf_and_table()
    print("[4/7] write BOM, cut list and component tables")
    write_tables(parts)
    print("[5/7] write guide and supporting documents")
    write_assembly_guide(parts)
    copy_supporting_documents()
    print("[6/7] run geometry and STEP validation")
    _, validation = run_validation(step_paths)
    print("[7/7] write manifest and Fusion 360 zip")
    write_manifest(validation)
    package_zip()
    print(PACKAGE)


if __name__ == "__main__":
    main()
