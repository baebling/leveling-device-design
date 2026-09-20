"""Render the archived Firgelli STEP with fixed and moving solids separated."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("XDG_CACHE_HOME", str(ROOT / ".cache"))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplcache"))
for path in (ROOT,):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import cadquery as cq
import vtk

from cad.common import COLORS, Component
from cad.rendering import _actor


ACTUATOR_STEP = ROOT / "references" / "vendor" / "firgelli" / "F-SD-H-450-12v-8in.stp"


def vendor_components():
    solids = list(cq.importers.importStep(str(ACTUATOR_STEP)).val().Solids())
    components = []
    for index, solid in enumerate(solids):
        if index == 3:
            color = COLORS["navy"]
            material = "fixed actuator body and motor"
        elif index == 6:
            color = COLORS["yellow"]
            material = "moving rod and front clevis"
        elif index == 7:
            color = COLORS["cyan"]
            material = "moving front shoulder component"
        else:
            color = COLORS["gray"]
            material = "fixed accessory or cable solid"
        components.append(Component(
            f"vendor_solid_{index}",
            solid,
            color,
            material,
            category="vendor_reference",
        ))
    return components


def _axis_actor(start, end, color):
    source = vtk.vtkLineSource()
    source.SetPoint1(*start)
    source.SetPoint2(*end)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(source.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(*color)
    actor.GetProperty().SetLineWidth(4.0)
    return actor


def render(path, camera_position, focal_point, state_text):
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.965, 0.972, 0.982)
    renderer.SetBackground2(0.78, 0.86, 0.91)
    renderer.GradientBackgroundOn()
    for component in vendor_components():
        renderer.AddActor(_actor(component))

    origin = (42.05, 38.5, 0.0)
    renderer.AddActor(_axis_actor(origin, (142.05, 38.5, 0.0), (0.85, 0.18, 0.18)))
    renderer.AddActor(_axis_actor(origin, (42.05, -320.0, 0.0), (0.18, 0.62, 0.28)))
    renderer.AddActor(_axis_actor(origin, (42.05, 38.5, 100.0), (0.18, 0.32, 0.85)))

    title = vtk.vtkTextActor()
    title.SetInput("FIRGELLI SOURCE STEP DIAGNOSTIC")
    title.SetPosition(40, 920)
    title.GetTextProperty().SetFontSize(26)
    title.GetTextProperty().SetColor(0.05, 0.15, 0.24)
    title.GetTextProperty().SetBold(True)
    renderer.AddActor2D(title)

    state = vtk.vtkTextActor()
    state.SetInput(state_text)
    state.SetPosition(520, 920)
    state.GetTextProperty().SetFontSize(24)
    state.GetTextProperty().SetColor(0.05, 0.15, 0.24)
    state.GetTextProperty().SetBold(True)
    renderer.AddActor2D(state)

    legend = vtk.vtkTextActor()
    legend.SetInput(
        "NAVY    FIXED BODY / MOTOR\n"
        "YELLOW  MOVING ROD / FRONT CLEVIS\n"
        "CYAN    MOVING FRONT SHOULDER\n"
        "GRAY    FIXED ACCESSORY SOLIDS\n"
        "RGB     STEP X / Y / Z AXES"
    )
    legend.SetPosition(980, 690)
    legend.GetTextProperty().SetFontSize(20)
    legend.GetTextProperty().SetColor(0.05, 0.15, 0.24)
    legend.GetTextProperty().SetBold(True)
    renderer.AddActor2D(legend)

    footer = vtk.vtkTextActor()
    footer.SetInput("VENDOR REFERENCE ONLY | ORIGINAL STEP TOPOLOGY IS NOT VALID FOR FABRICATION EXPORT")
    footer.SetPosition(40, 25)
    footer.GetTextProperty().SetFontSize(16)
    footer.GetTextProperty().SetColor(0.65, 0.16, 0.12)
    renderer.AddActor2D(footer)

    camera = vtk.vtkCamera()
    camera.SetPosition(*camera_position)
    camera.SetFocalPoint(*focal_point)
    camera.SetViewUp(0.0, 0.0, 1.0)
    camera.SetViewAngle(32.0)
    renderer.SetActiveCamera(camera)
    renderer.ResetCameraClippingRange()

    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(True)
    window.SetMultiSamples(8)
    window.SetSize(1500, 1000)
    window.AddRenderer(renderer)
    window.Render()
    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.SetInputBufferTypeToRGB()
    capture.ReadFrontBufferOff()
    capture.Update()
    writer = vtk.vtkPNGWriter()
    path.parent.mkdir(parents=True, exist_ok=True)
    writer.SetFileName(str(path))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()
    window.Finalize()
    return path


def render_vendor_diagnostics():
    output = ROOT / "outputs" / "renders"
    paths = [render(
        output / "vendor_firgelli_step_side.png",
        (520.0, -105.0, 300.0),
        (20.0, -105.0, 0.0),
        "SIDE VIEW | STEP AXIS +Y REAR / -Y FRONT",
    )]
    paths.append(render(
        output / "vendor_firgelli_step_front.png",
        (42.05, -650.0, 15.0),
        (42.05, -250.0, 0.0),
        "FRONT CLEVIS VIEW",
    ))
    return paths


def main():
    render_vendor_diagnostics()
    print("vendor actuator diagnostic renders complete")


if __name__ == "__main__":
    main()
