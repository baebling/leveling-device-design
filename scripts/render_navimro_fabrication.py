"""Render verification views of the NAVIMRO fabrication assembly."""

from pathlib import Path

import vtk

from cad.navimro_fabrication_assembly import components_for_pose
from cad.navimro_fabrication_parameters import NAVIMRO_POSES


CAMERAS = {
    "iso": ((1250, -1450, 900), (0, 0, 210), (0, 0, 1)),
    "front": ((1600, 0, 300), (0, 0, 210), (0, 0, 1)),
    "side": ((0, -1600, 300), (0, 0, 210), (0, 0, 1)),
    "top": ((0, 0, 1850), (0, 0, 170), (0, 1, 0)),
    "guide": ((500, -650, 420), (0, 0, 220), (0, 0, 1)),
}


def _actor(component):
    shape = component.shape.val() if hasattr(component.shape, "val") else component.shape
    vertices, triangles = shape.tessellate(1.5, 0.3)
    points = vtk.vtkPoints()
    for vertex in vertices:
        points.InsertNextPoint(vertex.x, vertex.y, vertex.z)
    cells = vtk.vtkCellArray()
    for tri in triangles:
        cell = vtk.vtkTriangle()
        for i, point_id in enumerate(tri):
            cell.GetPointIds().SetId(i, point_id)
        cells.InsertNextCell(cell)
    poly = vtk.vtkPolyData()
    poly.SetPoints(points)
    poly.SetPolys(cells)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(poly)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    r, g, b, a = component.color
    actor.GetProperty().SetColor(r, g, b)
    actor.GetProperty().SetOpacity(a)
    return actor


def render(pose_name, output_path, view="iso", include_prefixes=None, parallel=False):
    pose = NAVIMRO_POSES[pose_name]
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.97, 0.98, 0.985)
    renderer.SetBackground2(0.78, 0.86, 0.90)
    renderer.GradientBackgroundOn()
    for component in components_for_pose(pose):
        if include_prefixes and not any(component.name.startswith(prefix) for prefix in include_prefixes):
            continue
        renderer.AddActor(_actor(component))

    title = vtk.vtkTextActor()
    title.SetInput(f"NAVIMRO RADIAL-3 FABRICATION BASELINE | {pose_name.upper()}\nZ {pose.lift_mm:.0f} mm | PITCH {pose.pitch_deg:.1f} deg | ROLL {pose.roll_deg:.1f} deg")
    title.SetPosition(32, 925)
    title.GetTextProperty().SetFontSize(22)
    title.GetTextProperty().SetBold(True)
    title.GetTextProperty().SetColor(0.05, 0.14, 0.22)
    renderer.AddActor2D(title)
    footer = vtk.vtkTextActor()
    footer.SetInput("PROTOTYPE FABRICATION SET | VERIFY VENDOR TRANSFER-HOLES BEFORE DRILLING")
    footer.SetPosition(32, 24)
    footer.GetTextProperty().SetFontSize(15)
    footer.GetTextProperty().SetColor(0.65, 0.12, 0.08)
    renderer.AddActor2D(footer)

    camera = vtk.vtkCamera()
    position, focal, up = CAMERAS[view]
    camera.SetPosition(*position)
    camera.SetFocalPoint(*focal)
    camera.SetViewUp(*up)
    if parallel:
        camera.ParallelProjectionOn()
        camera.SetParallelScale(520.0 if view == "top" else 370.0)
    renderer.SetActiveCamera(camera)
    renderer.ResetCameraClippingRange()

    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(True)
    window.SetSize(1600, 1000)
    window.AddRenderer(renderer)
    window.Render()
    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.SetInputBufferTypeToRGB()
    capture.ReadFrontBufferOff()
    capture.Update()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(output_path))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()
    window.Finalize()
    return output_path


def render_all(root):
    output_dir = Path(root) / "outputs" / "navimro_fabrication" / "renders"
    outputs = [
        render("collapsed", output_dir / "navimro_collapsed_iso.png"),
        render("neutral", output_dir / "navimro_neutral_iso.png"),
        render("raised", output_dir / "navimro_raised_iso.png"),
        render("max_pitch_roll", output_dir / "navimro_max_pitch_roll_iso.png"),
        render("neutral", output_dir / "navimro_front.png", view="front", parallel=True),
        render("neutral", output_dir / "navimro_side.png", view="side", parallel=True),
        render("neutral", output_dir / "navimro_top.png", view="top", parallel=True),
        render(
            "neutral", output_dir / "navimro_guide_detail.png", view="guide",
            include_prefixes=("NVR-G", "NVR-B", "NVR-S", "NVR-P06"),
        ),
    ]
    return outputs

