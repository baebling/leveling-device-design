"""Generate Rev M2 STEP, DXF, CSV, audit inputs, and review renders."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import cadquery as cq
import ezdxf
import vtk

from cad.manual_turnbuckle_rev_m2 import COLORS, Component, components_for_pose, grouped_components
from calculations import manual_turnbuckle_rev_m2_screen as data


OUT = ROOT / "outputs" / "manual_turnbuckle_rev_m2"
STEP_DIR = OUT / "step"
GROUP_DIR = OUT / "groups"
FAB_DIR = OUT / "fabrication"
RENDER_DIR = OUT / "renders"

POSES = {
    "NEUTRAL": (0.0, 0.0),
    "PITCH_P3": (3.0, 0.0),
    "PITCH_M3": (-3.0, 0.0),
    "ROLL_P3": (0.0, 3.0),
    "ROLL_M3": (0.0, -3.0),
    "P3_R3": (3.0, 3.0),
    "P3_RM3": (3.0, -3.0),
    "PM3_R3": (-3.0, 3.0),
    "PM3_RM3": (-3.0, -3.0),
}


def export_step_files():
    for directory in (STEP_DIR, GROUP_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    for name, (pitch, roll) in POSES.items():
        components = components_for_pose(pitch, roll)
        compound = cq.Compound.makeCompound([component.shape for component in components])
        cq.exporters.export(compound, str(STEP_DIR / f"Manual_3RPS_RevM2_{name}.step"))
    for group, components in grouped_components().items():
        compound = cq.Compound.makeCompound([component.shape for component in components])
        cq.exporters.export(compound, str(GROUP_DIR / f"{group}.step"))


def _new_dxf():
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 4
    for name, color in (("OUTLINE", 7), ("M8_CLEARANCE", 1), ("SUPPORT_CLEARANCE", 3), ("CENTER", 6), ("NOTES", 7)):
        doc.layers.add(name=name, color=color)
    return doc


def _export_plate_dxf(name, center_diameter, quantity):
    doc = _new_dxf()
    msp = doc.modelspace()
    length = data.P.adapter_length_mm
    width = data.P.adapter_width_mm
    msp.add_lwpolyline(
        [(-length / 2, -width / 2), (length / 2, -width / 2), (length / 2, width / 2), (-length / 2, width / 2)],
        close=True,
        dxfattribs={"layer": "OUTLINE"},
    )
    for x in (-data.P.adapter_hole_pitch_mm / 2, data.P.adapter_hole_pitch_mm / 2):
        msp.add_circle((x, 0), 4.5, dxfattribs={"layer": "M8_CLEARANCE"})
    msp.add_circle((0, 0), center_diameter / 2, dxfattribs={"layer": "SUPPORT_CLEARANCE"})
    msp.add_line((-50, 0), (50, 0), dxfattribs={"layer": "CENTER"})
    msp.add_line((0, -30), (0, 30), dxfattribs={"layer": "CENTER"})
    msp.add_text(
        f"{name} QTY {quantity} | A6061-T6 100x60x5 | PRELIMINARY",
        height=3.0,
        dxfattribs={"layer": "NOTES"},
    ).set_placement((-50, -38))
    doc.saveas(FAB_DIR / f"{name}.dxf")


def export_fabrication_files():
    FAB_DIR.mkdir(parents=True, exist_ok=True)
    _export_plate_dxf("M2_LOWER_ADAPTER_D13_5", 13.5, 3)
    _export_plate_dxf("M2_UPPER_ADAPTER_D21_5", 21.5, 3)
    with (FAB_DIR / "M2_profile_cut_list.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow(("frame", "profile", "length_mm", "quantity", "end_cut"))
        writer.writerow(("lower", "DNF4040", 700, 2, "90 deg"))
        writer.writerow(("lower", "DNF4040", 620, 4, "90 deg"))
        writer.writerow(("upper", "DNF3030", 700, 2, "90 deg"))
        writer.writerow(("upper", "DNF3030", 640, 3, "90 deg"))
    with (FAB_DIR / "M2_support_hole_table.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow(("part", "feature", "x_mm", "y_mm", "diameter_mm", "quantity"))
        for part, diameter in (("LOWER_ADAPTER", 13.5), ("UPPER_ADAPTER", 21.5)):
            writer.writerow((part, "support clearance", 0, 0, diameter, 3))
            writer.writerow((part, "M8 clearance", -35, 0, 9.0, 3))
            writer.writerow((part, "M8 clearance", 35, 0, 9.0, 3))
        for index, (x, y) in enumerate(data.support_points(data.P.lower_support_radius_mm), 1):
            writer.writerow((f"LOWER_PROFILE_A{index}", "stud relief in adjacent profile wall", x, y, 13.5, 1))
        for index, (x, y) in enumerate(data.support_points(data.P.upper_support_radius_mm), 1):
            writer.writerow((f"UPPER_PROFILE_A{index}", "stud relief in adjacent profile wall", x, y, 21.5, 1))


def export_bom():
    rows = [
        ("S01", "DNF4040 profile", "700 mm", 2, "cut"),
        ("S02", "DNF4040 profile", "620 mm", 4, "cut"),
        ("S03", "DNF3030 profile", "700 mm", 2, "cut"),
        ("S04", "DNF3030 profile", "640 mm", 3, "cut"),
        ("S05", "4035 inside profile bracket", "4040 / M8", 8, "buy"),
        ("S06", "DCB3025 inside profile bracket", "3030 / M6", 6, "buy"),
        ("M01", "NBK STB-M12 turnbuckle", "M12x1.75 RH/LH; min tip span 171; supplied SJN lock nuts retained", 3, "vendor confirmation"),
        ("M02", "PHS12L female rod end", "M12x1.75 LH; bore12; width16; h50", 3, "source exact LH item"),
        ("M03", "IMAO BJ761-12011N hinge eye", "M12; bore12; eye width14; H50; L30", 3, "buy"),
        ("M04", "DIN6334 coupling nut", "M12x36 RH", 3, "buy"),
        ("M05", "IMAO BJ762-12001 hinge support", "pin12; gap14; M12 mount", 3, "buy"),
        ("M06", "IMAO BJ762-20001 hinge support", "original pin20; gap22; M20 mount", 3, "buy"),
        ("M07", "flanged reducing bush", "ID12.1 / OD20 / L11", 6, "exact stock item required"),
        ("M08", "upper pivot bolt", "M12x65 class 8.8 + washer + nyloc", 3, "buy"),
        ("F01", "lower adapter plate", "A6061-T6 100x60x5; D13.5 + 2xD9", 3, "laser/waterjet"),
        ("F02", "upper adapter plate", "A6061-T6 100x60x5; D21.5 + 2xD9", 3, "laser/waterjet"),
        ("F03", "lower round standoff", "OD16 / ID8.5 / L15", 6, "buy"),
        ("F04", "upper round standoff", "OD16 / ID8.5 / L20", 6, "buy"),
        ("F05", "lower adapter fastener", "M8x35 socket bolt + washer + T-nut", 6, "buy"),
        ("F06", "upper adapter fastener", "M8x40 socket bolt + washer + T-nut", 6, "buy"),
        ("F07", "BJ762-12001 mount nut", "M12 washer + nut", 3, "buy"),
        ("F08", "BJ762-20001 mount nut", "M20 washer + nut", 3, "buy"),
        ("F09", "BJ761 to coupling jam nut", "M12x1.75 RH thin jam nut", 3, "buy"),
        ("F10", "profile bracket fastener set", "as specified for S05/S06", 14, "buy"),
        ("F11", "coupling to STB jam nut", "M12x1.75 RH thin jam nut", 3, "buy"),
        ("F12", "STB to PHS12L jam nut", "M12x1.75 LH thin jam nut", 3, "source exact LH item"),
    ]
    path = OUT / "Manual_3RPS_RevM2_BOM.csv"
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow(("line_id", "item", "exact_specification", "quantity", "status"))
        writer.writerows(rows)


def _actor(component: Component):
    vertices, triangles = component.shape.tessellate(0.7, 0.2)
    points = vtk.vtkPoints()
    for vertex in vertices:
        points.InsertNextPoint(vertex.x, vertex.y, vertex.z)
    polys = vtk.vtkCellArray()
    for triangle in triangles:
        cell = vtk.vtkTriangle()
        for index, value in enumerate(triangle):
            cell.GetPointIds().SetId(index, value)
        polys.InsertNextCell(cell)
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    polydata.SetPolys(polys)
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputData(polydata)
    normals.ComputePointNormalsOn()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(normals.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(*component.color)
    actor.GetProperty().SetRoughness(0.55)
    return actor


def render_pose(name, pitch, roll):
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.96, 0.97, 0.98)
    renderer.SetBackground2(0.78, 0.84, 0.88)
    renderer.GradientBackgroundOn()
    for component in components_for_pose(pitch, roll):
        renderer.AddActor(_actor(component))
    title = vtk.vtkTextActor()
    title.SetInput(f"MANUAL 3-RPS REV M2 | {name}\nPITCH {pitch:+.1f} deg | ROLL {roll:+.1f} deg | TILT-ONLY")
    title.SetPosition(28, 820)
    title.GetTextProperty().SetFontSize(23)
    title.GetTextProperty().SetColor(0.06, 0.13, 0.19)
    title.GetTextProperty().SetBold(True)
    renderer.AddActor2D(title)
    footer = vtk.vtkTextActor()
    footer.SetInput("PRELIMINARY | PURCHASE RELEASE FALSE | NOT FOR FABRICATION")
    footer.SetPosition(28, 24)
    footer.GetTextProperty().SetFontSize(16)
    footer.GetTextProperty().SetColor(0.65, 0.12, 0.08)
    renderer.AddActor2D(footer)
    camera = vtk.vtkCamera()
    camera.SetPosition(760, -920, 610)
    camera.SetFocalPoint(0, 0, 145)
    camera.SetViewUp(0, 0, 1)
    camera.SetViewAngle(33)
    renderer.SetActiveCamera(camera)
    renderer.ResetCameraClippingRange()
    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(True)
    window.SetMultiSamples(8)
    window.SetSize(1400, 900)
    window.AddRenderer(renderer)
    window.Render()
    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.SetInputBufferTypeToRGB()
    capture.ReadFrontBufferOff()
    capture.Update()
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(RENDER_DIR / f"Manual_3RPS_RevM2_{name}.png"))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()
    window.Finalize()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    export_step_files()
    export_fabrication_files()
    export_bom()
    workspace = data.workspace_audit()
    strength = data.strength_audit()
    (OUT / "RevM2_calculation_audit.json").write_text(
        json.dumps({"workspace": workspace, "strength": strength}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    render_pose("NEUTRAL", 0.0, 0.0)
    render_pose("P3_R3", 3.0, 3.0)
    print(json.dumps({"output": str(OUT), "poses": len(POSES), "workspace_pass": workspace["passes"], "strength_pass": strength["passes_preliminary_screen"]}, indent=2))


if __name__ == "__main__":
    main()
