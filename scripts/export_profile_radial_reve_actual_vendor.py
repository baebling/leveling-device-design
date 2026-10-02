"""Export the Rev E actual-vendor STEP pose package and validation record."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cadquery as cq
import vtk

from cad.profile_radial_reve_actual_vendor import (
    POSES,
    Pose,
    VENDOR_COLLAPSED_PIN_MM,
    VENDOR_FRONT_PIN_MM,
    VENDOR_REAR_PIN_MM,
    VENDOR_STEP,
    actuator_parts,
    assembly_for_pose,
    components_for_pose,
    full_pose_audit,
    supplier_joint_parts,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "profile_radial_revE_pin_axis_corrected_2026-10-02"
STEP_DIR = OUTPUT / "step"
RENDER_DIR = OUTPUT / "renders"
AUDIT_PATH = OUTPUT / "Profile_Radial_3RPS_RevE_supplier_interface_validation.json"
MANIFEST_PATH = OUTPUT / "artifact_manifest.json"

EXPORT_POSES = {
    "collapsed": POSES["collapsed"],
    "neutral": POSES["neutral"],
    "raised": POSES["raised"],
    "p3_r3": POSES["p3_r3"],
    "p3_rm3": POSES["p3_rm3"],
}

CAMERAS = {
    "iso": ((1050, -1250, 780), (0, 0, 155), (0, 0, 1), 520),
    "top": ((0, 0, 1500), (0, 0, 150), (0, 1, 0), 420),
    "side": ((1200, 0, 220), (0, 0, 150), (0, 0, 1), 390),
    "underside": ((980, -1180, -360), (0, 0, 185), (0, 0, 1), 500),
    "joint": ((430, -410, 335), (14.5, 155, 165), (0, 0, 1), 205),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def actor_for(part):
    vertices, triangles = part.shape.tessellate(1.2, 0.25)
    points = vtk.vtkPoints()
    for vertex in vertices:
        points.InsertNextPoint(vertex.x, vertex.y, vertex.z)
    cells = vtk.vtkCellArray()
    for triangle in triangles:
        cell = vtk.vtkTriangle()
        for index, point_id in enumerate(triangle):
            cell.GetPointIds().SetId(index, point_id)
        cells.InsertNextCell(cell)
    mesh = vtk.vtkPolyData()
    mesh.SetPoints(points)
    mesh.SetPolys(cells)
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputData(mesh)
    normals.ComputePointNormalsOn()
    normals.SplittingOff()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(normals.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(*part.color[:3])
    actor.GetProperty().SetOpacity(part.color[3])
    actor.GetProperty().SetInterpolationToPhong()
    actor.GetProperty().SetRoughness(0.4)
    return actor


def render_pose(pose: Pose, path: Path, view="iso", detail=False, overlay=True):
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.96, 0.97, 0.98)
    renderer.SetBackground2(0.80, 0.86, 0.90)
    renderer.GradientBackgroundOn()
    parts = components_for_pose(
        pose,
        include_collapsed_hardware=False,
    )
    if detail:
        parts = [
            part for part in parts
            if part.name.startswith("A1_") or part.name in ("LMB_M8x12_1", "LMB_M8x12_2", "PHS_M6x25_1")
        ]
    for part in parts:
        renderer.AddActor(actor_for(part))

    position, focal, up, scale = CAMERAS[view]
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
    window.SetSize(1500, 960)
    window.SetMultiSamples(8)
    window.SetNumberOfLayers(2 if overlay else 1)
    renderer.SetLayer(0)
    window.AddRenderer(renderer)
    if overlay:
        text_layer = vtk.vtkRenderer()
        text_layer.SetLayer(1)
        text_layer.SetInteractive(False)
        text_layer.SetBackgroundAlpha(0.0)
        title = vtk.vtkTextActor()
        title.SetInput(
            "REV E CORRECTED | 315 mm COLLAPSED | LM4075OE + LMB-10 + PHS6\n"
            f"Z={pose.lift_mm:.0f} mm | PITCH={pose.pitch_deg:+.1f} deg | ROLL={pose.roll_deg:+.1f} deg"
        )
        title.SetPosition(28, 870)
        title.GetTextProperty().SetFontSize(22)
        title.GetTextProperty().SetBold(True)
        title.GetTextProperty().SetColor(0.04, 0.08, 0.12)
        text_layer.AddActor2D(title)
        footer = vtk.vtkTextActor()
        footer.SetInput("CAD REVIEW | NOT RELEASED FOR ORDER OR FABRICATION")
        footer.SetPosition(28, 24)
        footer.GetTextProperty().SetFontSize(15)
        footer.GetTextProperty().SetColor(0.62, 0.10, 0.07)
        text_layer.AddActor2D(footer)
        window.AddRenderer(text_layer)
    window.Render()
    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.SetInputBufferTypeToRGB()
    capture.ReadFrontBufferOff()
    capture.Update()
    path.parent.mkdir(parents=True, exist_ok=True)
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(path))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()
    window.Finalize()
    return path


def export_steps():
    STEP_DIR.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, pose in EXPORT_POSES.items():
        path = STEP_DIR / f"Profile_Radial_3RPS_RevE_SUPPLIER_{name.upper()}.step"
        assembly_for_pose(
            pose, include_collapsed_hardware=False
        ).save(str(path), exportType="STEP", mode="default")
        paths.append(path)
    return paths


def export_joint_detail():
    """Export one complete A1 interface stack for practical CAD review."""

    pose = POSES["collapsed"]
    detail = cq.Assembly(name="A1_LM4075OE_LMB10_TRUSCO_PHS6_INTERFACE")
    parts = [
        part for part in components_for_pose(pose)
        if part.name.startswith("A1_") or part.name in ("LMB_M8x12_1", "LMB_M8x12_2", "PHS_M6x25_1")
    ]
    for part in parts:
        detail.add(part.shape, name=part.name, color=cq.Color(*part.color))
    path = STEP_DIR / "A1_LM4075OE_LMB10_TRUSCO_PHS6_INTERFACE_DETAIL.step"
    detail.save(str(path), exportType="STEP", mode="default")
    return path


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    step_paths = export_steps()
    joint_detail = export_joint_detail()
    render_paths = [
        render_pose(POSES["collapsed"], RENDER_DIR / "01_COLLAPSED_SUPPLIER.png"),
        render_pose(POSES["neutral"], RENDER_DIR / "02_NEUTRAL_SUPPLIER.png"),
        render_pose(POSES["raised"], RENDER_DIR / "03_RAISED_SUPPLIER.png"),
        render_pose(POSES["p3_r3"], RENDER_DIR / "04_PITCH3_ROLL3_SUPPLIER.png"),
        render_pose(POSES["p3_rm3"], RENDER_DIR / "05_PITCH3_ROLLM3_SUPPLIER.png"),
        render_pose(POSES["collapsed"], RENDER_DIR / "06_SIDE_SUPPLIER.png", view="side"),
        render_pose(POSES["collapsed"], RENDER_DIR / "07_UNDERSIDE_SUPPLIER.png", view="underside"),
        render_pose(POSES["collapsed"], RENDER_DIR / "08_A1_JOINT_SUPPLIER.png", view="joint", detail=True),
    ]
    audit = full_pose_audit()
    audit.update(
        {
            "vendor_step_sha256": sha256(VENDOR_STEP),
            "vendor_rear_pin_center_mm": VENDOR_REAR_PIN_MM,
            "vendor_front_pin_center_mm": VENDOR_FRONT_PIN_MM,
            "vendor_collapsed_pin_center_distance_mm": VENDOR_COLLAPSED_PIN_MM,
            "note": (
                "Pose models use the actual LM4075OE STEP plus public-dimension LMB-10 and "
                "TRUSCO PHS6 supplier envelopes. Rev E upper eye centers and platform X/Y/yaw "
                "are corrected for world-fixed lower hinge pin axes. Actual upper pivot pins, "
                "independent mechanical stops, moving cables, and enclosure are not modeled; "
                "this package does not establish final assembly or purchase readiness. "
                "The stale mixed Rev D fastener group is replaced with the corrected six LMB bolts "
                "and three PHS studs. Upper frame rises 15 mm; upper actuator eyes shift 1.5 mm "
                "on three existing 0.5 mm shims per axis so PHS studs stay in the 3030 slot center. "
                "Supplier envelopes are not fabrication drawings. Electrical parts are not modeled."
            ),
            "purchase_release": False,
            "fabrication_release": False,
        }
    )
    AUDIT_PATH.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    artifacts = step_paths + [joint_detail] + render_paths + [AUDIT_PATH]
    manifest = {
        "revision": "E_ACTUAL_VENDOR_PIN_AXIS_CORRECTED_2026_10_02",
        "artifact_count": len(artifacts),
        "artifacts": [
            {"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in artifacts
        ],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"audit": str(AUDIT_PATH), "passes": audit["passes"], "artifacts": len(artifacts)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
