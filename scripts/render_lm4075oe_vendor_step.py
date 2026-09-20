"""Render the named LM4075OE vendor STEP parts for interface review."""

from __future__ import annotations

import argparse
from pathlib import Path

import cadquery as cq
import vtk
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDataStd import TDataStd_Name
from OCP.TDF import TDF_Label, TDF_LabelSequence
from OCP.TDocStd import TDocStd_Document
from OCP.XCAFApp import XCAFApp_Application
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ShapeTool


COLORS = {
    "UP": (0.18, 0.36, 0.55),
    "END": (0.10, 0.16, 0.22),
    "MOTER": (0.62, 0.66, 0.69),
    "WAIKE": (0.20, 0.48, 0.70),
    "FENGTOU": (0.88, 0.55, 0.12),
    "NEIGUAN": (0.82, 0.84, 0.86),
}


def name_of(label: TDF_Label) -> str:
    attribute = TDataStd_Name()
    if label.FindAttribute(TDataStd_Name.GetID_s(), attribute):
        return attribute.Get().ToExtString()
    referred = TDF_Label()
    if XCAFDoc_ShapeTool.GetReferredShape_s(label, referred):
        if referred.FindAttribute(TDataStd_Name.GetID_s(), attribute):
            return attribute.Get().ToExtString()
    return "UNNAMED"


def actor_for(shape, color):
    wrapped = cq.Shape.cast(shape)
    vertices, triangles = wrapped.tessellate(0.25, 0.08)
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
    actor.GetProperty().SetColor(*color)
    actor.GetProperty().SetRoughness(0.4)
    actor.GetProperty().SetMetallic(0.15)
    return actor


def read_named_shapes(path: Path):
    XCAFApp_Application.GetApplication_s()
    document = TDocStd_Document(TCollection_ExtendedString("MDTV-XCAF"))
    reader = STEPCAFControl_Reader()
    reader.SetNameMode(True)
    if reader.ReadFile(str(path.resolve())) != 1 or not reader.Transfer(document):
        raise RuntimeError("STEP import failed")
    shape_tool = XCAFDoc_DocumentTool.ShapeTool_s(document.Main())
    roots = TDF_LabelSequence()
    shape_tool.GetFreeShapes(roots)
    components = TDF_LabelSequence()
    XCAFDoc_ShapeTool.GetComponents_s(roots.Value(1), components, False)
    return [
        (name_of(components.Value(index)), XCAFDoc_ShapeTool.GetShape_s(components.Value(index)))
        for index in range(1, components.Length() + 1)
    ]


def render(named_shapes, output: Path, camera_position, view_up, title_text):
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.96, 0.97, 0.98)
    renderer.SetBackground2(0.80, 0.86, 0.90)
    renderer.GradientBackgroundOn()
    for name, shape in named_shapes:
        renderer.AddActor(actor_for(shape, COLORS.get(name, (0.55, 0.55, 0.55))))

    camera = vtk.vtkCamera()
    camera.SetPosition(*camera_position)
    camera.SetFocalPoint(-91.0, -229.0, -22.0)
    camera.SetViewUp(*view_up)
    camera.SetViewAngle(30.0)
    renderer.SetActiveCamera(camera)
    renderer.ResetCameraClippingRange()

    title = vtk.vtkTextActor()
    title.SetInput(title_text)
    title.SetPosition(36, 740)
    title.GetTextProperty().SetFontSize(25)
    title.GetTextProperty().SetColor(0.04, 0.10, 0.16)
    title.GetTextProperty().SetBold(True)
    renderer.AddActor2D(title)

    legend = vtk.vtkTextActor()
    legend.SetInput("FIXED CANDIDATES: UP / END / MOTER / WAIKE / FENGTOU\nMOVING CANDIDATE: NEIGUAN\nVENDOR STEP: accessories not included")
    legend.SetPosition(36, 35)
    legend.GetTextProperty().SetFontSize(19)
    legend.GetTextProperty().SetColor(0.04, 0.10, 0.16)
    renderer.AddActor2D(legend)

    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(True)
    window.SetSize(1400, 820)
    window.SetMultiSamples(8)
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("step", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    named = read_named_shapes(args.step)
    render(
        named,
        args.output_dir / "LM4075OE_VENDOR_ISO.png",
        (380.0, -620.0, 300.0),
        (0.0, 0.0, 1.0),
        "LM4075OE-1075 100 mm | SUPPLIER STEP | ISO",
    )
    render(
        named,
        args.output_dir / "LM4075OE_VENDOR_SIDE.png",
        (-91.0, -720.0, -22.0),
        (0.0, 0.0, 1.0),
        "LM4075OE-1075 100 mm | SUPPLIER STEP | SIDE",
    )
    print("Rendered", len(named), "named components")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
