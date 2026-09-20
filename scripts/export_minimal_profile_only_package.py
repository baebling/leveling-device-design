"""Build the profile-only 3-RPS Fusion 360 review package."""

import csv
import hashlib
import json
import shutil
from collections import Counter
from pathlib import Path

import cadquery as cq
import vtk

from calculations.profile_only_vendor_interface_audit import build_audit
from cad.minimal_profile_only_assembly import (
    POSES,
    _shape,
    actuator_pin_lengths,
    assembly_bounds,
    components_for_pose,
    lower_tangent_rail_data,
    named_collision_volume,
    profile_cut_list,
    stop_sweep_audit,
    workspace_audit,
)


ROOT = Path(__file__).resolve().parents[1]
REVISION = "A"
OUTPUT = ROOT / "outputs" / "minimal_profile_only_revA"
STEP_DIR = OUTPUT / "step"
RENDER_DIR = OUTPUT / "renders"
TABLE_DIR = OUTPUT / "tables"
VERIFY_DIR = OUTPUT / "verification"
PACKAGE = ROOT / "output" / "Minimal_3RPS_ProfileOnly_Fusion360_revA.zip"

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
    "raised_iso": ((1120, -1320, 880), (0, 0, 170), (0, 0, 1), 520),
    "max_tilt_iso": ((1120, -1320, 880), (0, 0, 170), (0, 0, 1), 520),
    "top": ((0, 0, 1700), (0, 0, 150), (0, 1, 0), 450),
    "exploded": ((1350, -1500, 1220), (0, 0, 360), (0, 0, 1), 720),
    "actuator_joint": ((520, -620, 350), (0, 250, 125), (0, 0, 1), 225),
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

    detail_groups = (
        "lower_frame", "lower_joints", "lower_fasteners", "upper_frame",
        "upper_joints", "upper_fasteners", "actuators", "actuator_eyes",
    )
    detail = cq.Assembly(name="ACTUATOR_1_COMPLETE_JOINT_DETAIL")
    for part in components_for_pose(POSES["collapsed"]):
        if part.group not in detail_groups:
            continue
        if "A1" not in part.name and part.name not in {"upper_cross_A1", "lower_tangent_mount_rail_A1"}:
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
        parts = [
            part for part in parts
            if "A1" in part.name
            or part.name in {"upper_cross_A1", "lower_tangent_mount_rail_A1"}
        ]
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
        "BLACK = T-SLOT PROFILE | YELLOW = PROVISIONAL LM4075OE ENVELOPE"
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
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(("profile", "cut_length_mm", "quantity", "cut_tolerance_mm", "operation"))
        for key, quantity in profile_cut_list().items():
            profile, length = key.split(" x ")
            writer.writerow((profile, length, quantity, "+/-0.5", "square cut; deburr only"))
    return path


def write_bom():
    path = TABLE_DIR / "profile_only_mechanical_BOM.csv"
    rows = [
        ("P01", "4040 M8-slot extrusion, cut 700 mm", 2, "CUT", "lower outer sides"),
        ("P02", "4040 M8-slot extrusion, cut 620 mm", 3, "CUT", "lower front/back plus A1 tangent rail"),
        ("P03", "4040 M8-slot extrusion, CAD cut 296.696 mm", 2, "BLOCKED", "297 mm is not an orderable fixed length; 300 mm does not fit this geometry"),
        ("P04", "3030 M6-slot extrusion, cut 700 mm", 2, "CUT", "upper outer sides"),
        ("P05", "3030 M6-slot extrusion, cut 640 mm", 4, "CUT", "upper front/back and two joint rows"),
        ("J01", "LM4075OE-1075, 24 V, 100 mm stroke, 5 V encoder", 3, "PROVISIONAL_CAD", "replace yellow envelope with vendor STEP"),
        ("J02", "LMB-10 lower clevis bracket", 3, "BLOCKED", "current side mount cannot capture both 36 mm-spaced base features"),
        ("J03", "PHS6 spherical rod end", 3, "BLOCKED", "CAD profile-to-ring offset is 15 mm too short"),
        ("C01", "4040 catalog 4035 angle connector", 10, "BLOCKED", "four A2/A3 joints are 30/60 degrees, not 90 degrees"),
        ("C02", "3030 catalog internal/angle connector", 8, "CATALOG", "four outer corners plus four crossbar ends"),
        ("S01", "M10 adjustable two-collar mechanical stop set", 3, "PROVISIONAL", "independent of actuator electrical limits"),
        ("S02", "profile-mounted stop capture bracket pair", 3, "PROVISIONAL", "50 mm clear slot"),
    ]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(("item", "description", "quantity", "status", "installation"))
        writer.writerows(rows)
    return path


def write_fastener_schedule():
    path = TABLE_DIR / "profile_only_fastener_schedule.csv"
    rows = [
        ("F01", "M8 profile connector screw", 20, "two per 4035 connector; DO NOT ORDER before Rev B"),
        ("F02", "40-series M8 T-nut", 20, "two per 4035 connector; DO NOT ORDER before Rev B"),
        ("F03", "M6 profile connector screw", 16, "two per DCB3025 connector; DO NOT ORDER before Rev B"),
        ("F04", "30-series M6 T-nut", 16, "two per DCB3025 connector; DO NOT ORDER before Rev B"),
        ("F05", "M8 screw for LMB-10", 6, "two per lower bracket; final length after receipt"),
        ("F06", "40-series M8 T-nut for LMB-10", 6, "two per lower bracket"),
        ("F07", "6 mm clevis pin with positive retainer", 3, "one per lower bracket"),
        ("F08", "M6x50 partially threaded upper pivot bolt", 3, "one per actuator"),
        ("F09", "M6 flat washer", 6, "two per upper pivot"),
        ("F10", "M6 nyloc nut", 3, "one per upper pivot"),
        ("F11", "30-series M6 hammer-head/T-bolt for PHS6", 3, "male stud points down into PHS6 female thread"),
        ("F12", "M8 screw for stop capture bracket", 6, "two per stop"),
        ("F13", "40-series M8 T-nut for stop capture bracket", 6, "two per stop"),
    ]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(("item", "description", "quantity", "installation"))
        writer.writerows(rows)
    return path


def write_assembly_guide(parts):
    audit = workspace_audit()
    rails = lower_tangent_rail_data()
    text = f"""# Profile-only 3-RPS review guide Rev {REVISION}

## FABRICATION HOLD — 2026-08-31

Do not assemble or order structure from this package. Vendor-image audit found that the LMB-10 base cannot be mounted as modeled, four oblique lower joints cannot use the 90-degree 4035 connector, the PHS6 stack is 15 mm too short, and the 297 mm profile is not an orderable fixed length. See `verification/vendor_interface_audit_2026-08-31.json` and `web_research/vendor_dimension_interface_audit_2026-08-31.md` in the project.

## Recommended Fusion 360 file

Import `step/MINIMAL_3RPS_profile_only_collapsed_rev{REVISION}.step` with Fusion 360 Upload or File > Open. The assembly contains {len(parts)} named positioned components. Use the exploded STEP for order and `ACTUATOR_1_complete_joint_detail_rev{REVISION}.step` for the clevis/PHS6 stack.

## Coordinate system and envelope

- Origin: center of the lower 700 x 700 mm frame at its underside.
- +X: right, +Y: rear/A1 direction, +Z: upward.
- Collapsed envelope: 700 x 700 x 299 mm.
- Raised frame-top height: 345 mm at 50 mm nominal common lift.
- Upper motion: Z 0-50 mm, pitch +/-3 deg, roll +/-3 deg. X, Y and yaw are constrained by the three RPS limbs.
- Required actuator pin-center range: {audit['required_min_pin_mm']:.3f}-{audit['required_max_pin_mm']:.3f} mm.
- LM4075OE theoretical range: 205-305 mm; margins {audit['retract_margin_mm']:.3f}/{audit['extend_margin_mm']:.3f} mm.

## Former intended assembly order — review only

1. Build the lower 4040 outer square from two 700 mm sides and two 620 mm cross members. Square diagonals before final torque.
2. Install the three lower tangent rails. A1 is 620 mm at Y=295 mm. A2/A3 are {rails[1]['length_mm']:.3f} mm at {rails[1]['angle_deg']:.3f}/{rails[2]['angle_deg']:.3f} deg.
3. Side-mount three LMB-10 brackets at support points (0,250), (-216.5,-125), and (216.5,-125) mm. Their pin axes are tangent to the 250 mm support circle.
4. Insert each LM4075OE lower eye into its LMB-10 and fit the 6 mm retained pin.
5. Build the upper 3030 frame from two 700 mm sides and four 640 mm cross members. The two joint rows are Y=250 and Y=-125 mm in upper local coordinates.
6. Capture one M6 hammer-head/T-bolt in each lower 3030 slot and screw the downward male thread into PHS6 with a jam nut. Fit each actuator upper eye to the single side of PHS6 with an M6x50 partial-thread bolt, two washers and a nyloc nut.
7. Install the three compact M10 two-collar stop rods and lower capture-jaw pairs. Set the collars only after the electrical limits have been tested at low speed.
8. Move one actuator at a time, then perform synchronized Z motion, then pitch/roll. Stop immediately if encoder direction, current, or physical clearance differs from the audit.

## Former fabrication concept — withdrawn

- No full-size structural plate, plywood, acrylic deck, welding, drilling or tapping is used in this Rev A structure.
- The former plan assumed profile square cutting and deburring only. That claim is withdrawn until Rev B connection hardware is verified.
- Small catalog connectors, stop brackets, T-nuts and fasteners remain necessary; "profile-only" means the load-carrying frames contain extrusion rather than sheet.

## Release restrictions

- Yellow actuator bodies are planning envelopes reconstructed from retained LM4075OE 100 mm STEP inspection notes. Replace them with the vendor STEP or measured delivered parts.
- Verify LMB-10, PHS6, profile slot standards, actuator eye width/bore, cable exit and M6 single-side articulation on one physical axis before ordering all structure.
- The stop hardware is a compact preliminary arrangement. Confirm collar contact and bracket stiffness in a supervised low-speed bench test.
- This is a PoC digital mock-up, not a certification or a people-carrying design.
"""
    path = OUTPUT / "FUSION360_IMPORT_AND_ASSEMBLY_GUIDE.md"
    path.write_text(text, encoding="utf-8")
    return path


def run_validation(step_paths):
    moving = {"actuators", "actuator_eyes"}
    fixed = {"lower_frame", "lower_connectors", "upper_frame", "upper_connectors"}
    collisions = {
        name: named_collision_volume(pose, moving, fixed)
        for name, pose in POSES.items()
    }
    selected = STEP_DIR / f"MINIMAL_3RPS_profile_only_collapsed_rev{REVISION}.step"
    imported = cq.importers.importStep(str(selected))
    imported_shape = imported.val()
    vendor_audit = build_audit()
    result = {
        "revision": REVISION,
        "status": "FABRICATION_BLOCKED_VENDOR_INTERFACE_MISMATCH",
        "fabrication_release": False,
        "component_count": len(components_for_pose(POSES["collapsed"])),
        "structural_plate_count": 0,
        "welding_required": False,
        "drilling_or_tapping_required": False,
        "profile_square_cutting_required": True,
        "workspace": workspace_audit(),
        "mechanical_stop_sweep": stop_sweep_audit(),
        "bounds": {name: assembly_bounds(pose) for name, pose in POSES.items()},
        "actuator_to_profile_collision_volume_mm3": collisions,
        "step_reverse_import": {
            "file": str(selected.relative_to(ROOT)).replace("\\", "/"),
            "solid_count": len(imported_shape.Solids()),
            "volume_mm3": imported_shape.Volume(),
            "passes": len(imported_shape.Solids()) > 0 and imported_shape.Volume() > 0.0,
        },
        "step_file_count": len(step_paths),
        "collapsed_actuator_pin_lengths_mm": actuator_pin_lengths(POSES["collapsed"]),
        "vendor_interface_audit": vendor_audit,
    }
    VERIFY_DIR.mkdir(parents=True, exist_ok=True)
    vendor_path = VERIFY_DIR / "vendor_interface_audit_2026-08-31.json"
    vendor_path.write_text(
        json.dumps(vendor_audit, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
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
    print("[5/6] run geometry and STEP reverse-import validation")
    _, validation = run_validation(step_paths)
    print("[6/6] write hashes and zip package")
    write_manifest(validation)
    package_zip()
    print(PACKAGE)


if __name__ == "__main__":
    main()
