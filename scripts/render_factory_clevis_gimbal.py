"""Render the JNT-CG-01 measured-mockup seed."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("XDG_CACHE_HOME", str(ROOT / ".cache"))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplcache"))
for path in (ROOT,):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import vtk

from cad.factory_clevis_gimbal import components
from cad.rendering import _actor


def render_factory_clevis_gimbal():
    output = ROOT / "outputs" / "renders" / "jnt_cg01_factory_clevis_gimbal.png"
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.965, 0.972, 0.982)
    renderer.SetBackground2(0.78, 0.86, 0.91)
    renderer.GradientBackgroundOn()
    for component in components():
        renderer.AddActor(_actor(component))

    for text, position, size, color in (
        ("JNT-CG-01 | FACTORY-EYE NESTED GIMBAL", (40, 920), 28, (0.05, 0.15, 0.24)),
        ("ORANGE  FACTORY EYE\nYELLOW  INNER CRADLE\nNAVY    OUTER YOKE\nCYAN    OPPOSED TRUNNIONS", (1060, 690), 19, (0.05, 0.15, 0.24)),
        ("MEASURED MOCK-UP SEED | NOT FOR FABRICATION", (40, 25), 17, (0.65, 0.16, 0.12)),
    ):
        actor = vtk.vtkTextActor()
        actor.SetInput(text)
        actor.SetPosition(*position)
        actor.GetTextProperty().SetFontSize(size)
        actor.GetTextProperty().SetColor(*color)
        actor.GetTextProperty().SetBold(True)
        renderer.AddActor2D(actor)

    camera = vtk.vtkCamera()
    camera.SetPosition(178.0, -215.0, 155.0)
    camera.SetFocalPoint(4.0, 0.0, 0.0)
    camera.SetViewUp(0.0, 0.0, 1.0)
    camera.SetViewAngle(28.0)
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
    output.parent.mkdir(parents=True, exist_ok=True)
    writer.SetFileName(str(output))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()
    window.Finalize()
    return [output]


if __name__ == "__main__":
    render_factory_clevis_gimbal()
