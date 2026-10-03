"""Export and render the direct-M6 PHS6 upper-mount review package."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import cadquery as cq
import vtk


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cad.profile_radial_reve_actual_vendor import (  # noqa: E402
    Pose,
    group_shape,
    transform_upper_frame_shape,
)
from cad.profile_radial_revf_upper_pocket_review import local_review_geometry  # noqa: E402
from cad.revf_direct_phs6_mount import (  # noqa: E402
    audit_direct_mount_poses,
    build_direct_mount_plate,
    export_direct_mount_review,
    placed_direct_mount_plate,
)
from cad.revf_quote_package import build_upper_bracket  # noqa: E402
from cad.revf_split_keyhole_concept import (  # noqa: E402
    build_keyhole_support,
    build_mount_plate,
)
from cad.revf_upper_pocket_inputs import load_inputs  # noqa: E402


OUT = ROOT / "outputs" / "20261003_revf_direct_mount_review"


@dataclass(frozen=True)
class RenderPart:
    name: str
    shape: cq.Shape
    color: tuple[float, float, float]
    opacity: float = 1.0


COLORS = {
    "plate": (0.10, 0.40, 0.70),
    "housing": (0.58, 0.62, 0.66),
    "ball": (0.20, 0.23, 0.27),
    "fastener": (0.15, 0.17, 0.19),
    "profile": (0.72, 0.76, 0.80),
    "old": (0.48, 0.50, 0.53),
    "split": (0.92, 0.46, 0.08),
}


def _actor(part: RenderPart) -> vtk.vtkActor:
    vertices, triangles = part.shape.tessellate(0.35, 0.10)
    points = vtk.vtkPoints()
    for vertex in vertices:
        points.InsertNextPoint(vertex.x, vertex.y, vertex.z)
    cells = vtk.vtkCellArray()
    for triangle in triangles:
        cell = vtk.vtkTriangle()
        for index in range(3):
            cell.GetPointIds().SetId(index, triangle[index])
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
    actor.GetProperty().SetColor(*part.color)
    actor.GetProperty().SetOpacity(part.opacity)
    actor.GetProperty().SetRoughness(0.42)
    actor.GetProperty().SetMetallic(0.08)
    return actor


def _text(renderer, value, x, y, size, *, bold=False, color=(0.05, 0.10, 0.16)):
    actor = vtk.vtkTextActor()
    actor.SetInput(value)
    actor.SetPosition(x, y)
    prop = actor.GetTextProperty()
    prop.SetFontFamilyToArial()
    prop.SetFontSize(size)
    prop.SetColor(*color)
    prop.SetBold(bold)
    renderer.AddViewProp(actor)


def _render(parts, path, title, footer, camera, focal, scale):
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.97, 0.98, 0.99)
    renderer.SetBackground2(0.78, 0.86, 0.92)
    renderer.GradientBackgroundOn()
    for part in parts:
        renderer.AddActor(_actor(part))
    view = vtk.vtkCamera()
    view.SetPosition(*camera)
    view.SetFocalPoint(*focal)
    view.SetViewUp(0, 0, 1)
    view.ParallelProjectionOn()
    view.SetParallelScale(scale)
    renderer.SetActiveCamera(view)
    renderer.ResetCameraClippingRange()
    _text(renderer, title, 34, 820, 25, bold=True)
    _text(renderer, footer, 34, 28, 17, color=(0.15, 0.20, 0.25))
    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(True)
    window.SetSize(1500, 900)
    window.SetMultiSamples(8)
    window.AddRenderer(renderer)
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


def _cylinder(radius, length, start, direction=(0, 0, 1)):
    return cq.Solid.makeCylinder(radius, length, cq.Vector(*start), cq.Vector(*direction))


def closeup_parts(exploded=False):
    dz = 18 if exploded else 0
    geo = local_review_geometry(load_inputs(), 1)
    profile = cq.Workplane("XY").box(80, 30, 30).val().translate((0, 0, 54 + dz))
    plate = build_direct_mount_plate().translate((0, 0, dz))
    housing = geo["housing"]
    ball = geo["ball"]
    m6 = _cylinder(3.0, 12.0, (0, 0, 34.5 + dz), (0, 0, -1)).fuse(
        _cylinder(5.0, 4.0, (0, 0, 34.5 + dz))
    )
    mount_bolts = []
    for x in (-22, 22):
        mount_bolts.append(
            _cylinder(3.0, 18.0, (x, 0, 26 + dz)).fuse(
                _cylinder(5.0, 4.0, (x, 0, 26 + dz))
            )
        )
    return [
        RenderPart("profile", profile, COLORS["profile"], 0.28),
        RenderPart("plate", plate, COLORS["plate"]),
        RenderPart("housing", housing, COLORS["housing"]),
        RenderPart("ball", ball, COLORS["ball"]),
        RenderPart("fastener", m6, COLORS["fastener"]),
        *[RenderPart("fastener", item, COLORS["fastener"]) for item in mount_bolts],
    ]


def render_three_axis(path: Path):
    pose = Pose("raised_p3_r3", 50.0, 3.0, 3.0)
    frame = transform_upper_frame_shape(group_shape("upper_frame"), pose)
    parts = [RenderPart("profile", frame, COLORS["profile"], 0.30)]
    for axis in (1, 2, 3):
        parts.append(RenderPart("plate", placed_direct_mount_plate(axis, pose), COLORS["plate"]))
    _render(
        parts,
        path,
        "DIRECT-M6 UPPER PLATES | A1/A2/A3 | Z50 / PITCH+3 / ROLL+3",
        "The same 60x30x9 plate SKU is rotated during assembly; quantity 3.",
        (880, -960, 720),
        (0, 0, 290),
        430,
    )


def render_comparison(path: Path):
    old = build_upper_bracket(1).translate((-85, 0, 0))
    split_plate = build_mount_plate().translate((0, 0, 0))
    split_support = build_keyhole_support()
    direct = build_direct_mount_plate().translate((85, 0, 0))
    geo = local_review_geometry(load_inputs(), 1)
    parts = [
        RenderPart("old", old, COLORS["old"]),
        RenderPart("plate", split_plate, COLORS["plate"]),
        RenderPart("split", split_support, COLORS["split"]),
        RenderPart("housing", geo["housing"], COLORS["housing"]),
        RenderPart("plate", direct, COLORS["plate"]),
        RenderPart("housing", geo["housing"].translate((85, 0, 0)), COLORS["housing"]),
        RenderPart("ball", geo["ball"].translate((85, 0, 0)), COLORS["ball"]),
    ]
    _render(
        parts,
        path,
        "DFM OPTIONS | ONE-PIECE POCKET / SPLIT KEYHOLE / DIRECT M6",
        "RECOMMENDED: right-hand direct-M6 plate. One simple custom SKU, no housing clamp, nipple fully open.",
        (160, -235, 130),
        (0, 0, 15),
        120,
    )


def main() -> None:
    export_direct_mount_review(OUT)
    render_dir = OUT / "renders"
    _render(
        closeup_parts(False),
        render_dir / "01_direct_mount_assembled.png",
        "PHS6 DIRECT-M6 MOUNT | ASSEMBLED",
        "A6061 60x30x9 + CBS6-12. PHS6 body and grease nipple remain unclamped and open.",
        (110, -135, 92),
        (0, 0, 20),
        58,
    )
    _render(
        closeup_parts(True),
        render_dir / "02_direct_mount_exploded.png",
        "PHS6 DIRECT-M6 MOUNT | EXPLODED",
        "Preassemble PHS6 to plate, then attach plate to 3030 profile. Medium threadlocker + witness mark.",
        (120, -150, 112),
        (0, 0, 28),
        72,
    )
    render_three_axis(render_dir / "03_three_axis_same_sku.png")
    render_comparison(render_dir / "04_option_comparison.png")
    print(OUT)


if __name__ == "__main__":
    main()
