"""Render exploded and cumulative assembly views for the NAVIMRO guide."""

from dataclasses import replace
from pathlib import Path

import vtk

from cad.navimro_fabrication_assembly import components_for_pose
from cad.navimro_fabrication_parameters import NAVIMRO_POSES


STAGES = (
    ("01_lower_frame", ("NVR-L01", "NVR-P01")),
    ("02_fixed_tower", ("NVR-P06", "NVR-B02", "NVR-G07")),
    ("03_moving_guide", ("NVR-G01", "NVR-B01", "NVR-S01", "NVR-G06")),
    ("04_cardan", ("NVR-G02", "NVR-G03", "NVR-G04", "NVR-G05")),
    ("05_upper_frame", ("NVR-U01", "NVR-P03")),
    ("06_actuators", ("NVR-A",)),
    ("07_deck", ("NVR-U02",)),
    ("08_cart_coupling", ("NVR-C",)),
)

STAGE_TITLES = {
    "01_lower_frame": "STEP 1  LOWER 4040 FRAME + MOUNT TABS",
    "02_fixed_tower": "STEP 2  FIXED GUIDE TOWER + LMF12UU",
    "03_moving_guide": "STEP 3  MOVING SHAFTS + CARRIAGE",
    "04_cardan": "STEP 4  CENTRAL CARDAN JOINT",
    "05_upper_frame": "STEP 5  UPPER 4040 FRAME",
    "06_actuators": "STEP 6  THREE RADIAL ACTUATORS",
    "07_deck": "STEP 7  ACRYLIC COVER DECK",
    "08_cart_coupling": "STEP 8  CART-SIDE RECEIVERS + LATCHES",
}

GROUP_COLORS = (
    (0.43, 0.47, 0.50),
    (0.18, 0.48, 0.67),
    (0.13, 0.66, 0.60),
    (0.10, 0.76, 0.86),
    (0.83, 0.64, 0.18),
    (0.20, 0.22, 0.24),
    (0.43, 0.77, 0.83),
    (0.55, 0.36, 0.68),
)


def _group_index(name):
    for index, (_, prefixes) in enumerate(STAGES):
        if any(name.startswith(prefix) for prefix in prefixes):
            return index
    raise ValueError(f"Unmapped assembly component: {name}")


def _actor(component, color=None, opacity=None, translate=(0.0, 0.0, 0.0)):
    shape = component.shape.translate(translate) if any(translate) else component.shape
    shape = shape.val() if hasattr(shape, "val") else shape
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
    actor.GetProperty().SetColor(*(color or component.color[:3]))
    actor.GetProperty().SetOpacity(component.color[3] if opacity is None else opacity)
    actor.GetProperty().SetEdgeVisibility(False)
    return actor


def _finish(renderer, output_path, title, footer, camera_position, focal, parallel_scale):
    renderer.SetBackground(0.98, 0.985, 0.99)
    renderer.SetBackground2(0.79, 0.87, 0.91)
    renderer.GradientBackgroundOn()

    heading = vtk.vtkTextActor()
    heading.SetInput(title)
    heading.SetPosition(32, 915)
    heading.GetTextProperty().SetFontSize(24)
    heading.GetTextProperty().SetBold(True)
    heading.GetTextProperty().SetColor(0.05, 0.14, 0.22)
    renderer.AddActor2D(heading)

    note = vtk.vtkTextActor()
    note.SetInput(footer)
    note.SetPosition(32, 25)
    note.GetTextProperty().SetFontSize(16)
    note.GetTextProperty().SetColor(0.70, 0.24, 0.05)
    renderer.AddActor2D(note)

    camera = vtk.vtkCamera()
    camera.SetPosition(*camera_position)
    camera.SetFocalPoint(*focal)
    camera.SetViewUp(0, 0, 1)
    camera.ParallelProjectionOn()
    camera.SetParallelScale(parallel_scale)
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


def render_stage(stage_index, output_path):
    components = components_for_pose(NAVIMRO_POSES["neutral"])
    renderer = vtk.vtkRenderer()
    for component in components:
        group = _group_index(component.name)
        if group > stage_index:
            continue
        if group == stage_index:
            renderer.AddActor(_actor(component, color=(0.94, 0.43, 0.08), opacity=1.0))
        else:
            renderer.AddActor(_actor(component, color=(0.56, 0.60, 0.62), opacity=0.34))

    stage_name = STAGES[stage_index][0]
    if stage_index in (1, 2):
        camera = (730, -850, 500)
        focal = (0, 0, 155)
        scale = 300
    elif stage_index == 3:
        camera = (630, -720, 430)
        focal = (0, 0, 245)
        scale = 220
    else:
        camera = (1250, -1450, 850)
        focal = (0, 0, 180)
        scale = 520
    return _finish(
        renderer,
        output_path,
        STAGE_TITLES[stage_name],
        "ORANGE = INSTALL NOW   |   GRAY = ALREADY ASSEMBLED",
        camera,
        focal,
        scale,
    )


def render_exploded(output_path):
    components = components_for_pose(NAVIMRO_POSES["neutral"])
    offsets = (0, 60, 145, 220, 340, 185, 455, 520)
    renderer = vtk.vtkRenderer()
    for component in components:
        group = _group_index(component.name)
        renderer.AddActor(_actor(
            replace(component, color=(*GROUP_COLORS[group], 1.0)),
            translate=(0.0, 0.0, offsets[group]),
        ))
    return _finish(
        renderer,
        output_path,
        "EXPLODED ASSEMBLY - BOTTOM TO TOP",
        "ASSEMBLE IN NUMBER ORDER 1 -> 8   |   COLORS MATCH THE MANUAL",
        (1500, -1750, 1120),
        (0, 0, 380),
        700,
    )


def render_all(root):
    output_dir = Path(root) / "outputs" / "navimro_fabrication" / "assembly_guide"
    outputs = [render_exploded(output_dir / "00_exploded.png")]
    for index, (name, _) in enumerate(STAGES):
        outputs.append(render_stage(index, output_dir / f"{name}.png"))
    return outputs


if __name__ == "__main__":
    render_all(Path(__file__).resolve().parents[1])
