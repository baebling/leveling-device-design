"""Export and render the Rev F two-piece PHS6 upper-bracket concept."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import cadquery as cq
import vtk


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cad.revf_quote_package import build_upper_bracket  # noqa: E402
from cad.revf_split_keyhole_concept import (  # noqa: E402
    assembled_components,
    build_fastener_proxies,
    build_keyhole_support,
    build_mount_plate,
    build_phs6_proxy,
    export_split_keyhole_concept,
)


OUT = ROOT / "outputs" / "20261003_revf_split_keyhole_concept"


@dataclass(frozen=True)
class RenderPart:
    name: str
    shape: cq.Shape
    color: tuple[float, float, float]
    opacity: float = 1.0


COLORS = {
    "mount_plate": (0.12, 0.40, 0.68),
    "keyhole_support": (0.94, 0.48, 0.10),
    "housing": (0.58, 0.62, 0.66),
    "ball": (0.22, 0.26, 0.30),
    "grease_nipple_unknown": (0.88, 0.12, 0.12),
    "m6_retainer": (0.18, 0.20, 0.22),
    "m5_left": (0.18, 0.20, 0.22),
    "m5_right": (0.18, 0.20, 0.22),
    "profile_proxy": (0.76, 0.79, 0.82),
    "old_monolithic": (0.48, 0.52, 0.56),
}


def _actor(part: RenderPart) -> vtk.vtkActor:
    vertices, triangles = part.shape.tessellate(0.30, 0.10)
    points = vtk.vtkPoints()
    for vertex in vertices:
        points.InsertNextPoint(vertex.x, vertex.y, vertex.z)
    cells = vtk.vtkCellArray()
    for triangle in triangles:
        cell = vtk.vtkTriangle()
        for index in range(3):
            cell.GetPointIds().SetId(index, triangle[index])
        cells.InsertNextCell(cell)
    poly = vtk.vtkPolyData()
    poly.SetPoints(points)
    poly.SetPolys(cells)
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputData(poly)
    normals.ComputePointNormalsOn()
    normals.SplittingOff()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(normals.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(*part.color)
    actor.GetProperty().SetOpacity(part.opacity)
    actor.GetProperty().SetRoughness(0.42)
    actor.GetProperty().SetMetallic(0.10)
    return actor


def _text(renderer, value: str, x: int, y: int, size: int, color=(0.05, 0.10, 0.16), bold=False):
    actor = vtk.vtkTextActor()
    actor.SetInput(value)
    actor.SetPosition(x, y)
    prop = actor.GetTextProperty()
    prop.SetFontFamilyToArial()
    prop.SetFontSize(size)
    prop.SetColor(*color)
    prop.SetBold(bold)
    renderer.AddActor2D(actor)


def _render(parts, path: Path, *, title: str, footer: str, camera=(105, -125, 88), focal=(0, 0, 15)):
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.97, 0.98, 0.99)
    renderer.SetBackground2(0.78, 0.86, 0.92)
    renderer.GradientBackgroundOn()
    for part in parts:
        renderer.AddActor(_actor(part))
    camera_object = vtk.vtkCamera()
    camera_object.SetPosition(*camera)
    camera_object.SetFocalPoint(*focal)
    camera_object.SetViewUp(0, 0, 1)
    camera_object.ParallelProjectionOn()
    camera_object.SetParallelScale(58)
    renderer.SetActiveCamera(camera_object)
    renderer.ResetCameraClippingRange()
    _text(renderer, title, 32, 820, 25, bold=True)
    _text(renderer, footer, 32, 28, 17, color=(0.16, 0.21, 0.26))
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


def _normal_parts(*, exploded=False):
    components = assembled_components(exploded=exploded)
    parts = []
    for name, shape in components.items():
        opacity = 0.32 if name == "grease_nipple_unknown" else 1.0
        parts.append(RenderPart(name, shape, COLORS[name], opacity))
    profile = cq.Workplane("XY").box(80, 30, 30).val().translate((0, 0, 55 if not exploded else 73))
    parts.append(RenderPart("profile_proxy", profile, COLORS["profile_proxy"], 0.30))
    return parts


def render_comparison(path: Path):
    old = build_upper_bracket(1).translate((-48, 0, 0))
    parts = [RenderPart("old_monolithic", old, COLORS["old_monolithic"])]
    for name, shape in {
        "mount_plate": build_mount_plate().translate((48, 0, 0)),
        "keyhole_support": build_keyhole_support().translate((48, 0, 0)),
        **{name: shape.translate((48, 0, 0)) for name, shape in build_phs6_proxy().items()},
        **{name: shape.translate((48, 0, 0)) for name, shape in build_fastener_proxies().items()},
    }.items():
        parts.append(RenderPart(name, shape, COLORS[name], 0.30 if name == "grease_nipple_unknown" else 1.0))
    _render(
        parts,
        path,
        title="UPPER BRACKET DFM COMPARISON | LEFT: ONE-PIECE | RIGHT: TWO-PIECE",
        footer="RIGHT: straight plate + groove + drilling. Red envelope = PHS6 grease-nipple direction NOT VERIFIED.",
        camera=(125, -175, 105),
        focal=(0, 0, 15),
    )


def main() -> None:
    export_split_keyhole_concept(OUT)
    render_dir = OUT / "renders"
    _render(
        _normal_parts(exploded=False),
        render_dir / "01_two_piece_assembled.png",
        title="REV F TWO-PIECE PHS6 UPPER BRACKET | ASSEMBLED CONCEPT",
        footer="Blue: mounting plate | Orange: 8T keyhole backup | Red: unverified grease-nipple envelope",
    )
    _render(
        _normal_parts(exploded=True),
        render_dir / "02_two_piece_exploded.png",
        title="REV F TWO-PIECE PHS6 UPPER BRACKET | EXPLODED CONCEPT",
        footer="2 custom parts per axis; M6 centre retainer + 2 x M5 edge screws. NOT FOR FABRICATION.",
        camera=(120, -150, 110),
        focal=(0, 0, 25),
    )
    render_comparison(render_dir / "03_dfm_comparison.png")
    print(OUT)


if __name__ == "__main__":
    main()
