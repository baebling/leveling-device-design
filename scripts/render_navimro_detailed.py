"""Render the bolt-level Rev E digital mock-up for visual verification."""

from pathlib import Path

import vtk

from cad.navimro_detailed_assembly import GROUP_OFFSETS, detailed_components


CAMERAS = {
    "iso": ((1450, -1700, 1050), (0, 0, 200), (0, 0, 1), 560),
    "top": ((0, 0, 1900), (0, 0, 180), (0, 1, 0), 540),
    "underside": ((1350, -1600, -500), (0, 0, 180), (0, 0, 1), 560),
    "exploded": ((1750, -2000, 1350), (0, 0, 450), (0, 0, 1), 760),
    "joint": ((880, -780, 430), (285, 0, 120), (0, 0, 1), 270),
}


def _actor(part, translate=(0.0, 0.0, 0.0)):
    shape = part.shape.translate(translate) if any(translate) else part.shape
    shape = shape.val() if hasattr(shape, "val") else shape
    vertices, triangles = shape.tessellate(1.8, 0.35)
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
    actor.GetProperty().SetColor(*part.color[:3])
    actor.GetProperty().SetOpacity(part.color[3])
    return actor


def render(output_path, view="iso", exploded=False):
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.98, 0.985, 0.99)
    renderer.SetBackground2(0.78, 0.86, 0.90)
    renderer.GradientBackgroundOn()
    parts = detailed_components("neutral")
    if view == "joint":
        fixed_names = {
            "LWR_actuator_cross",
            "NVR-P04_lower_spreader_1",
            "UPR_end_front",
            "NVR-P03_upper_spreader_1",
        }
        parts = [
            part
            for part in parts
            if part.name in fixed_names
            or part.name.startswith("ACT1_")
            or part.name == "LA2000_A2_PROVISIONAL_1"
        ]
    for part in parts:
        offset = (0.0, 0.0, GROUP_OFFSETS[part.group]) if exploded else (0.0, 0.0, 0.0)
        renderer.AddActor(_actor(part, offset))

    title = vtk.vtkTextActor()
    title.SetInput(f"NAVIMRO DETAILED DIGITAL MOCK-UP REV E\n{len(parts)} POSITIONED COMPONENTS | ASSEMBLY-AUDITED GUIDE + CARDAN | YELLOW = PROVISIONAL")
    title.SetPosition(30, 915)
    title.GetTextProperty().SetFontSize(22)
    title.GetTextProperty().SetBold(True)
    title.GetTextProperty().SetColor(0.05, 0.14, 0.22)
    renderer.AddViewProp(title)
    footer = vtk.vtkTextActor()
    footer.SetInput("FUSION 360 STEP REVIEW SET | NOT RELEASED FOR FABRICATION UNTIL YELLOW PARTS ARE VERIFIED")
    footer.SetPosition(30, 22)
    footer.GetTextProperty().SetFontSize(14)
    footer.GetTextProperty().SetColor(0.68, 0.16, 0.08)
    renderer.AddViewProp(footer)

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
    output = Path(root) / "outputs" / "navimro_fusion360_revE" / "renders"
    return [
        render(output / "detailed_iso.png", "iso"),
        render(output / "detailed_top.png", "top"),
        render(output / "detailed_underside.png", "underside"),
        render(output / "detailed_exploded.png", "exploded", exploded=True),
        render(output / "actuator_joint_closeup.png", "joint"),
    ]


if __name__ == "__main__":
    render_all(Path(__file__).resolve().parents[1])
