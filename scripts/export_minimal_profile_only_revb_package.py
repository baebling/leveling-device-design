"""Build the dimension-corrected profile-only 3-RPS Rev B package."""

import csv
import hashlib
import json
import shutil
from pathlib import Path

import cadquery as cq
import vtk

from cad.minimal_profile_only_revb import (
    B,
    POSES,
    _shape,
    actuation_jacobian_audit,
    actuator_pin_lengths,
    assembly_bounds,
    components_for_pose,
    connector_fastener_axis_audit,
    joint_axis_alignment_audit,
    named_collision_volume,
    profile_cut_list,
    stop_sweep_audit,
    support_azimuth_audit,
    workspace_audit,
)


ROOT = Path(__file__).resolve().parents[1]
REVISION = "B"
OUTPUT = ROOT / "outputs" / "minimal_profile_only_revB"
STEP_DIR = OUTPUT / "step"
RENDER_DIR = OUTPUT / "renders"
TABLE_DIR = OUTPUT / "tables"
VERIFY_DIR = OUTPUT / "verification"
DOCUMENT_DIR = OUTPUT / "documents"
PACKAGE = ROOT / "output" / "Minimal_3RPS_ProfileOnly_Fusion360_revB.zip"

GROUPS = (
    "lower_frame",
    "lower_connectors",
    "lower_joints",
    "lower_fasteners",
    "upper_frame",
    "upper_connectors",
    "upper_joints",
    "upper_fasteners",
    "actuators",
    "actuator_eyes",
    "mechanical_stops",
)

EXPLODED_OFFSETS = {
    "lower_frame": 0.0,
    "lower_connectors": 25.0,
    "lower_joints": 80.0,
    "lower_fasteners": 45.0,
    "actuators": 170.0,
    "actuator_eyes": 170.0,
    "mechanical_stops": 90.0,
    "upper_joints": 290.0,
    "upper_fasteners": 330.0,
    "upper_frame": 390.0,
    "upper_connectors": 420.0,
}

CAMERAS = {
    "collapsed_iso": ((1120, -1320, 820), (0, 0, 145), (0, 0, 1), 510),
    "raised_iso": ((1120, -1320, 900), (0, 0, 170), (0, 0, 1), 520),
    "max_tilt_iso": ((1120, -1320, 900), (0, 0, 170), (0, 0, 1), 520),
    "top": ((0, 0, 1700), (0, 0, 150), (0, 1, 0), 450),
    "exploded": ((1350, -1500, 1220), (0, 0, 360), (0, 0, 1), 720),
    "actuator_joint": ((620, -720, 430), (0, 160, 150), (0, 0, 1), 285),
}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def hierarchical_assembly(pose_name, exploded=False, groups=None):
    selected = tuple(groups) if groups is not None else GROUPS
    root = cq.Assembly(name=f"MINIMAL_PROFILE_ONLY_{pose_name.upper()}_REV{REVISION}")
    for group in selected:
        sub = cq.Assembly(name=group.upper())
        for part in (item for item in components_for_pose(POSES[pose_name]) if item.group == group):
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
        path = STEP_DIR / f"MINIMAL_3RPS_profile_only_{pose_name}_rev{REVISION}.step"
        hierarchical_assembly(pose_name).save(str(path), exportType="STEP", mode="default")
        outputs.append(path)

    exploded = STEP_DIR / f"MINIMAL_3RPS_profile_only_exploded_rev{REVISION}.step"
    hierarchical_assembly("neutral", exploded=True).save(
        str(exploded), exportType="STEP", mode="default"
    )
    outputs.append(exploded)

    subassemblies = {
        "SUB_01_LOWER_PROFILE_FRAME": (
            "lower_frame", "lower_connectors", "lower_joints", "lower_fasteners"
        ),
        "SUB_02_UPPER_PROFILE_FRAME": (
            "upper_frame", "upper_connectors", "upper_joints", "upper_fasteners"
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

    detail = cq.Assembly(name="ACTUATOR_1_COMPLETE_JOINT_DETAIL")
    keep_names = {"upper_cross_A1", "lower_A1_radial_rail"}
    for part in components_for_pose(POSES["collapsed"]):
        if "A1" not in part.name and part.name not in keep_names:
            continue
        r, g, b, a = part.color
        detail.add(part.shape, name=part.name, color=cq.Color(r, g, b, a))
    detail_path = STEP_DIR / f"ACTUATOR_1_complete_joint_detail_rev{REVISION}.step"
    detail.save(str(detail_path), exportType="STEP", mode="default")
    outputs.append(detail_path)
    return outputs


def actor_for(part, offset=0.0):
    shape = part.shape.translate((0.0, 0.0, offset)) if offset else part.shape
    shape = _shape(shape)
    vertices, triangles = shape.tessellate(1.8, 0.35)
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


def render_view(filename, camera_name, pose_name="collapsed", exploded=False, detail=False):
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.96, 0.97, 0.98)
    parts = components_for_pose(POSES[pose_name])
    if detail:
        keep_names = {"upper_cross_A1", "lower_A1_radial_rail"}
        parts = [part for part in parts if "A1" in part.name or part.name in keep_names]
    for part in parts:
        offset = EXPLODED_OFFSETS[part.group] if exploded else 0.0
        renderer.AddActor(actor_for(part, offset))

    title = vtk.vtkTextActor()
    title.SetInput(
        f"PROFILE-ONLY 3-RPS REV {REVISION} | {pose_name.upper()}"
        f" | {len(parts)} MODELED COMPONENTS"
    )
    title.SetPosition(28, 842)
    title.GetTextProperty().SetFontSize(21)
    title.GetTextProperty().SetBold(True)
    title.GetTextProperty().SetColor(0.05, 0.09, 0.13)
    title.GetTextProperty().SetBackgroundColor(0.96, 0.97, 0.98)
    title.GetTextProperty().SetBackgroundOpacity(0.92)
    renderer.AddViewProp(title)

    footer = vtk.vtkTextActor()
    footer.SetInput(
        "BLACK = T-SLOT PROFILE | YELLOW = ACTUATOR ENVELOPE"
        " | RED = INDEPENDENT MECHANICAL STOP"
    )
    footer.SetPosition(28, 22)
    footer.GetTextProperty().SetFontSize(14)
    footer.GetTextProperty().SetColor(0.35, 0.08, 0.04)
    footer.GetTextProperty().SetBackgroundColor(0.96, 0.97, 0.98)
    footer.GetTextProperty().SetBackgroundOpacity(0.92)
    renderer.AddViewProp(footer)

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
    window.AddRenderer(renderer)
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
        render_view(RENDER_DIR / "03_max_pitch_roll_iso.png", "max_tilt_iso", "max_pitch_roll"),
        render_view(RENDER_DIR / "04_top.png", "top"),
        render_view(RENDER_DIR / "05_exploded.png", "exploded", "neutral", exploded=True),
        render_view(RENDER_DIR / "06_actuator_1_joint_detail.png", "actuator_joint", detail=True),
    ]


def write_component_manifest(parts):
    path = TABLE_DIR / "profile_only_component_manifest.csv"
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(("component_name", "group", "bom_key", "material", "status", "notes"))
        for part in parts:
            writer.writerow((part.name, part.group, part.bom_key, part.material, part.status, part.notes))
    return path


def write_cut_list():
    path = TABLE_DIR / "profile_cut_list.csv"
    sku = {
        "4040 x 700": "K92787708",
        "4040 x 620": "K92787705",
        "4040 x 300": "K92787692",
        "3030 x 700": "K42296106",
        "3030 x 640": "K42296071",
    }
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(("profile", "cut_length_mm", "quantity", "navimro_sku", "operation"))
        for key, quantity in profile_cut_list().items():
            profile, length = key.split(" x ")
            writer.writerow((profile, length, quantity, sku[key], "factory square cut; deburr"))
    return path


def write_bom():
    path = TABLE_DIR / "profile_only_mechanical_BOM.csv"
    rows = [
        ("P01", "DNF4040 M8-slot extrusion 700 mm", 2, "K92787708", "HOLD_REDESIGN"),
        ("P02", "DNF4040 M8-slot extrusion 620 mm", 3, "K92787705", "HOLD_REDESIGN"),
        ("P03", "DNF4040 M8-slot extrusion 300 mm", 1, "K92787692", "HOLD_REDESIGN"),
        ("P04", "DNF3030-6 M6-slot extrusion 700 mm", 2, "K42296106", "HOLD_REDESIGN"),
        ("P05", "DNF3030-6 M6-slot extrusion 640 mm", 4, "K42296071", "HOLD_REDESIGN"),
        ("C01", "4035 4040 90-degree bracket", 8, "K92782553", "REJECTED_FASTENER_AXIS"),
        ("C02", "DCB3025 3030 90-degree bracket", 8, "K56842696", "REJECTED_FASTENER_AXIS"),
        ("J01", "LM4075OE-1075 24 V, 100 mm, 5 V encoder", 3, "MOTIONGEARON", "EYE_WIDTH_OPEN"),
        ("J02", "LMB-10 single lower clevis", 3, "MOTORBANK", "PIN_INCLUSION_CONFIRM"),
        ("J03", "THK PHS6 female rod end", 3, "THK/SPEEDMALL", "RELEASED_DIMENSION"),
        ("S01", "M10 independent mechanical stop set", 3, "SUPPLIER_OPEN", "CATALOG_COMBINATION_OPEN"),
    ]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(("item", "description", "quantity", "supplier_or_sku", "status"))
        writer.writerows(rows)
    return path


def write_fastener_schedule():
    path = TABLE_DIR / "profile_only_fastener_schedule.csv"
    rows = [
        ("F01", "M8x20 full-thread hex bolt", 16, "K53672490", "3 packs of 6; 4035 brackets"),
        ("F02", "SP408 40-series M8 spring nut", 22, "K14671419", "16 bracket + 6 LMB; one 100 pack"),
        ("F03", "M6x15 SCM435 button socket bolt", 16, "K14333089", "DCB3025; one 100 pack"),
        ("F04", "SP306 30-series M6 spring nut", 16, "K14671215", "DCB3025; one 100 pack"),
        ("F05", "M8x16 full-thread hex bolt", 6, "K53672478", "LMB-10; one pack of 7"),
        ("F06", "LMB-10 included 6 mm pin and retainer", 3, "WITH_J02", "confirm included contents before order"),
        ("F07", "M6x50 half-thread hex bolt, thread length 18", 3, "K53672105", "upper pivot; one pack of 10"),
        ("F08", "M6 flat washer ID6.4 OD12.5 t1.5", 6, "K14530259", "upper pivot; one 100 pack"),
        ("F09", "M6 prevailing-torque nut", 3, "SKU_OPEN", "must not loosen; select after one-axis fit"),
        ("F10", "M6 ID shim 0.5/1.0 mm", 12, "SKU_OPEN", "final quantity after eye-width measurement"),
        ("F11", "TB306 M6x20 T-bolt", 3, "K55868014", "PHS6-to-3030, 12.5 mm nominal engagement"),
        ("F12", "medium-strength threadlocker", 1, "NAVIMRO_OPEN", "PHS6 stud/jam nut and stop hardware"),
    ]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(("item", "description", "used_quantity", "navimro_sku", "purchase_note"))
        writer.writerows(rows)
    return path


def write_assembly_guide(parts):
    audit = workspace_audit()
    text = f"""# Fusion 360 import and rejected-assembly review guide - Rev {REVISION}

## Current release state

**REJECTED - DO NOT FABRICATE OR PURCHASE FROM THIS PACKAGE.** A later assembly-axis audit found that both 4035/DCB connector fasteners were modeled vertically, the one-sided PHS6 offset produces a 3.549 degree actuator/pin-axis error at zero tilt, and the support azimuth gaps are 90/90/180 degrees instead of the requested 120/120/120 degrees. STEP files are retained only to reproduce and inspect the failure.

## Recommended Fusion 360 file

For failure review only, import `step/MINIMAL_3RPS_profile_only_collapsed_rev{REVISION}.step`. It contains {len(parts)} named positioned components. Do not treat the exploded STEP as a valid assembly sequence.

## Coordinate system and envelope

- Origin: lower 700 x 700 mm frame center at its underside.
- +X: right, +Y: A1/rear direction, +Z: upward.
- Collapsed envelope: 700 x 700 x {assembly_bounds(POSES['collapsed'])['zlen']:.0f} mm.
- Upper motion: common Z lift 0-50 mm, pitch +/-3 deg, roll +/-3 deg.
- Actuator pin-center demand: {audit['required_min_pin_mm']:.3f}-{audit['required_max_pin_mm']:.3f} mm.
- LM4075OE nominal range: 205-305 mm; margins {audit['retract_margin_mm']:.3f}/{audit['extend_margin_mm']:.3f} mm.

## Rejected assembly sequence

1. Build the lower orthogonal 4040 grid: two 700 mm sides, three 620 mm cross members at Y=330/-330/-10, and the 300 mm A1 rail from Y=10 to 310. Use eight 4035 brackets and two M8 fasteners per bracket.
2. Top-mount each LMB-10. Put its pin center at A1=(0,65), A2=(-75,-10), A3=(75,-10) mm and its second base feature 36 mm inward. Both M8 fasteners share one profile slot.
3. Place each actuator lower eye in the 20 mm LMB opening. Fit the included 6 mm pin only after checking that the delivered eye width is at most 20 mm and the retainer is included.
4. Build the upper 3030 grid: two 700 mm sides and four 640 mm cross members at local Y=335/-335/240/-10. Use eight DCB3025 brackets and two M6 fasteners per bracket.
5. Capture one TB306 M6x20 head in each lower 3030 slot. Use a 5 mm jam nut and screw PHS6 onto the remaining 12.5 mm nominal thread engagement. Lock the jam nut with medium-strength threadlocker.
6. Put the PHS6 ring on one side of the actuator upper eye. Fit the M6x50 half-thread bolt, two flat washers and measured shims so the 32 mm plain shank spans both bearing surfaces. Use a prevailing-torque nut without clamping the PHS6 inner ring against its outer body.
7. Install three mechanically independent stop rods/catches only after the selected catalog arrangement reproduces the CAD clear opening. Electrical limit switches do not replace these stops.
8. With no payload, move one actuator at a time at low speed. Then test common Z, pitch and roll while checking current, encoder direction, cable clearance, pin retention and stop contact.

## Fabrication operations

- No full-size plate, plywood, acrylic structural deck, welding, drilling or tapping is required by the Rev B profile frame.
- Profiles are fixed-length NAVIMRO cuts. Only square cutting and deburring are required at the supplier.
- The stop capture remains a catalog-combination placeholder and cannot be ordered from this package yet.

## Open receipt checks

- LM4075OE eye axial width, bore, cable-exit envelope and actual 205/305 mm pin-center lengths.
- LMB-10 included pin diameter, usable grip length and positive retainer.
- M6x50 upper pivot washer/shim stack and prevailing-torque nut SKU.
- Final M10 stop rod, collars, catch brackets and profile fasteners.

This is a rejected fixed indoor low-speed 10 kg PoC digital mockup, not a fabrication release, certification, or people-carrying design.
"""
    path = OUTPUT / "FUSION360_IMPORT_AND_ASSEMBLY_GUIDE.md"
    path.write_text(text, encoding="utf-8")
    return path


def copy_supporting_documents():
    DOCUMENT_DIR.mkdir(parents=True, exist_ok=True)
    sources = (
        ROOT / "design_basis" / "minimal_profile_only_revB_2026-08-31.md",
        ROOT / "procurement" / "profile_only_revB_structural_bom_2026-08-31.md",
        ROOT / "web_research" / "vendor_dimension_interface_audit_2026-08-31.md",
        ROOT / "procurement" / "electrical_control_completeness_2026-08-28.md",
    )
    outputs = []
    for source in sources:
        target = DOCUMENT_DIR / source.name
        shutil.copy2(source, target)
        outputs.append(target)
    return outputs


def run_validation(step_paths):
    actuator_body_collisions = {
        name: named_collision_volume(
            pose,
            {"actuators"},
            {"lower_frame", "lower_connectors", "lower_joints", "upper_frame", "upper_connectors"},
        )
        for name, pose in POSES.items()
    }
    eye_collisions = {
        name: named_collision_volume(
            pose,
            {"actuator_eyes"},
            {"lower_frame", "lower_connectors", "upper_frame", "upper_connectors"},
        )
        for name, pose in POSES.items()
    }
    selected = STEP_DIR / f"MINIMAL_3RPS_profile_only_collapsed_rev{REVISION}.step"
    imported_shape = cq.importers.importStep(str(selected)).val()
    workspace = workspace_audit()
    stops = stop_sweep_audit()
    jacobian = actuation_jacobian_audit()
    joints = joint_axis_alignment_audit()
    supports = support_azimuth_audit()
    connectors = connector_fastener_axis_audit()
    collisions_pass = max(actuator_body_collisions.values()) < 0.001 and max(eye_collisions.values()) < 0.001
    result = {
        "revision": REVISION,
        "status": "REJECTED_ASSEMBLY_GEOMETRY_REDESIGN_REQUIRED",
        "fabrication_release": False,
        "component_count": len(components_for_pose(POSES["collapsed"])),
        "structural_plate_count": 0,
        "welding_required": False,
        "drilling_or_tapping_required": False,
        "profile_square_cutting_required": True,
        "workspace": workspace,
        "mechanical_stop_sweep": stops,
        "actuation_jacobian": jacobian,
        "joint_axis_alignment": joints,
        "support_azimuth": supports,
        "connector_fastener_axes": connectors,
        "bounds": {name: assembly_bounds(pose) for name, pose in POSES.items()},
        "actuator_body_collision_volume_mm3": actuator_body_collisions,
        "actuator_eye_collision_volume_mm3": eye_collisions,
        "digital_checks_pass": False,
        "step_reverse_import": {
            "file": str(selected.relative_to(ROOT)).replace("\\", "/"),
            "solid_count": len(imported_shape.Solids()),
            "volume_mm3": imported_shape.Volume(),
            "passes": len(imported_shape.Solids()) > 0 and imported_shape.Volume() > 0.0,
        },
        "step_file_count": len(step_paths),
        "collapsed_actuator_pin_lengths_mm": actuator_pin_lengths(POSES["collapsed"]),
        "open_items": [
            "REDESIGN: 4035/DCB connector second-leg fastener axes",
            "REDESIGN: actuator eye/pin-axis alignment",
            "REDESIGN: requested 120-degree radial support layout",
            "LM4075OE eye axial width and matching vendor STEP",
            "LMB-10 pin and positive retainer inclusion",
            "M6 prevailing-torque nut and shim thickness after one-axis fit",
            "independent M10 mechanical stop catalog combination",
        ],
    }
    VERIFY_DIR.mkdir(parents=True, exist_ok=True)
    path = VERIFY_DIR / "profile_only_validation.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path, result


def write_manifest(validation):
    files = [path for path in OUTPUT.rglob("*") if path.is_file() and path.name != "artifact_manifest.json"]
    rows = [
        {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in sorted(files)
    ]
    path = OUTPUT / "artifact_manifest.json"
    path.write_text(json.dumps({
        "revision": REVISION,
        "status": validation["status"],
        "artifact_count": len(rows),
        "component_count": validation["component_count"],
        "artifacts": rows,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
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
    print(f"[1/6] export STEP assemblies ({len(parts)} modeled components)")
    step_paths = export_steps()
    print("[2/6] render visual review set")
    render_all()
    print("[3/6] write component, cut, BOM and fastener tables")
    write_component_manifest(parts)
    write_cut_list()
    write_bom()
    write_fastener_schedule()
    print("[4/6] write Fusion 360 and assembly guide")
    write_assembly_guide(parts)
    copy_supporting_documents()
    print("[5/6] run geometry and STEP reverse-import validation")
    _, validation = run_validation(step_paths)
    print("[6/6] write hashes and zip package")
    write_manifest(validation)
    package_zip()
    print(PACKAGE)


if __name__ == "__main__":
    main()
