"""Create review STEP, CAD renders and measured B-rep audit for M2R1.
No machining DXF or fabrication release is produced.
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import json
import hashlib
from itertools import combinations
import cadquery as cq
import vtk
from cad import manual_turnbuckle_rev_m2r1 as model
from calculations import manual_turnbuckle_rev_m2_screen as kinematics

OUT = ROOT / "outputs/manual_turnbuckle_rev_m2r1"
POSES = {"NEUTRAL": (0, 0), "PITCH_P3": (3, 0), "PITCH_M3": (-3, 0),
         "ROLL_P3": (0, 3), "ROLL_M3": (0, -3), "P3_R3": (3, 3),
         "P3_RM3": (3, -3), "PM3_R3": (-3, 3), "PM3_RM3": (-3, -3)}


def bbox_overlap(a, b, tol=1e-6):
    return all(min(getattr(a, k+'max'), getattr(b, k+'max')) -
               max(getattr(a, k+'min'), getattr(b, k+'min')) > tol for k in 'xyz')


def check_pose(parts):
    boxes = {c.name: c.shape.BoundingBox() for c in parts}
    collisions, checked = [], 0
    for a, b in combinations(parts, 2):
        if not bbox_overlap(boxes[a.name], boxes[b.name]):
            continue
        checked += 1
        volume = a.shape.intersect(b.shape).Volume()
        if volume > 0.01:
            collisions.append({"a": a.name, "b": b.name, "volume_mm3": volume})
    joint_checks = []
    lookup = {c.name: c for c in parts}
    for i in range(1, 4):
        fork = lookup[f"U{i}_FORK"].shape
        bush = lookup[f"U{i}_BUSH_L"].shape
        pin = lookup[f"U{i}_PIN_M12X80"].shape
        ball = lookup[f"U{i}_INNER_BEARING"].shape
        spacer = lookup[f"U{i}_INNER_SPACER_L"].shape
        joint_checks.append({"axis": i, "bush_fork_distance_mm": fork.distance(bush),
            "bush_pin_distance_mm": bush.distance(pin),
            "bearing_spacer_distance_mm": ball.distance(spacer),
            "bearing_pin_distance_mm": ball.distance(pin)})
    return {"component_count": len(parts), "pair_count": len(parts)*(len(parts)-1)//2,
            "broad_phase_candidates": checked,
            "invalid_shapes": [c.name for c in parts if not c.shape.isValid()],
            "unexpected_collisions": collisions, "joint_distances": joint_checks,
            "pass": not collisions and all(c.shape.isValid() for c in parts),
            "scope": "all distinct component pairs; internal modeled threads within each compound link not checked"}


def export(parts, path):
    assembly = cq.Assembly(name="M2R1_PRELIMINARY_NOT_FOR_FABRICATION")
    for c in parts:
        assembly.add(c.shape, name=c.name, color=cq.Color(*c.color))
    assembly.export(str(path))
    return assembly


def actor(c):
    vertices, triangles = c.shape.tessellate(0.25, 0.12)
    pts = vtk.vtkPoints()
    for p in vertices:
        pts.InsertNextPoint(p.x, p.y, p.z)
    cells = vtk.vtkCellArray()
    for face in triangles:
        cells.InsertNextCell(3)
        for index in face:
            cells.InsertCellPoint(index)
    mesh = vtk.vtkPolyData()
    mesh.SetPoints(pts)
    mesh.SetPolys(cells)
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputData(mesh)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(normals.GetOutputPort())
    obj = vtk.vtkActor()
    obj.SetMapper(mapper)
    obj.GetProperty().SetColor(*c.color)
    obj.GetProperty().SetSpecular(0.25)
    obj.GetProperty().SetSpecularPower(25)
    return obj


def render(parts, name, camera_direction=(1, -1.4, 0.7), subtitle=""):
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.94, 0.96, 0.98)
    for c in parts:
        renderer.AddActor(actor(c))
    camera = renderer.GetActiveCamera()
    camera.SetPosition(*camera_direction)
    camera.SetFocalPoint(0, 0, 0)
    camera.SetViewUp(0, 1, 0) if abs(camera_direction[2]) > 0.95 and abs(camera_direction[0]) < 0.1 else camera.SetViewUp(0, 0, 1)
    camera.ParallelProjectionOn()
    renderer.ResetCamera()
    camera.SetParallelScale(camera.GetParallelScale()*(0.86 if name in POSES or name == 'STRUCTURE_EXPOSED' else 1.1))
    for content, y, size, color in [
        ("MANUAL 3-RPS / M2R1   " + name, 850, 25, (0.06, 0.12, 0.18)),
        (subtitle, 817, 18, (0.15, 0.22, 0.3)),
        ("PRELIMINARY CAD - NOT FOR FABRICATION - SUPPLIER FITS UNCONFIRMED", 22, 16, (0.7, 0.13, 0.08))]:
        label = vtk.vtkTextActor()
        label.SetInput(content)
        label.SetPosition(25, y)
        label.GetTextProperty().SetFontSize(size)
        label.GetTextProperty().SetFontFamilyToCourier()
        label.GetTextProperty().SetColor(*color)
        renderer.AddViewProp(label)
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
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(OUT / "renders" / (name + ".png")))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()
    window.Finalize()


def local_joint_views():
    J = model.J
    parts = list(model.joint_local_parts())
    # Show the representative spherical housing/inner ring from actual pose model,
    # brought back from axis A1 into its local coordinate system.
    neutral = model.components_for_pose(0, 0, False)
    center = kinematics.upper_pin_points(0, 0)[0]
    def local(shape):
        return shape.translate(tuple(-v for v in center)).rotate((0,0,0),(0,0,1), -90)
    ball = next(c for c in neutral if c.name == "U1_INNER_BEARING")
    link = next(c for c in neutral if c.name == "LEG_1_STB_M12_LINK")
    parts.append(model.comp("INNER_BEARING", "upper_bearings", local(ball.shape), model.SILVER))
    parts.append(model.comp("ROD_END_HOUSING", "rod_end_housing", local(link.shape.Solids()[-1]), model.STEEL))
    export(parts, OUT / "step" / "M2R1_UPPER_JOINT_REVIEW.step")
    render(parts, "UPPER_JOINT", (1.2,-1.5,0.7), "Separate bushes, spherical inner bearing, side spacers and retained pin")
    section_box = model.base._box(100, 250, 180, (50, 0, 10))
    section = []
    for c in parts:
        shape = c.shape.intersect(section_box)
        if shape.Volume() > 1e-8:
            section.append(model.comp(c.name,c.group,shape,c.color,c.material))
    render(section, "UPPER_JOINT_SECTION", (1,-0.13,0.05), "x=0 section through pin axis; nominal fit study only")
    exploded = []
    for c in parts:
        offset = 0
        if c.name.startswith("BUSH_"):
            offset = -35 if c.name.endswith("L") else 35
        elif c.name.startswith("INNER_SPACER_"):
            offset = -15 if c.name.endswith("L") else 15
        elif c.name.startswith("WASHER_"):
            offset = -55 if c.name.endswith("L") else 55
        elif c.name.startswith("PIN_"):
            offset = -135
        elif c.name == "LOCK_NUT":
            offset = 80
        dz = -50 if c.name == "ROD_END_HOUSING" else 0
        exploded.append(model.comp(c.name,c.group,c.shape.translate((0,offset,dz)),c.color,c.material))
    export(exploded, OUT / "step" / "M2R1_UPPER_JOINT_EXPLODED_REVIEW.step")
    render(exploded, "UPPER_JOINT_EXPLODED", (1,-0.3,0.55), "Exploded review; offsets are for visibility, not assembly dimensions")


def main():
    for folder in (OUT, OUT/'step', OUT/'renders'):
        folder.mkdir(parents=True, exist_ok=True)
    reports = {}
    for name, (pitch, roll) in POSES.items():
        parts = model.components_for_pose(pitch, roll)
        report = check_pose(parts)
        reports[name] = report
        print(name, 'PASS' if report['pass'] else 'FAIL',
              len(report['unexpected_collisions']), 'collisions', flush=True)
        if not report['pass']:
            print(json.dumps(report['unexpected_collisions'], indent=2), flush=True)
        if name in ('NEUTRAL', 'P3_R3', 'PM3_RM3'):
            export(parts, OUT/'step'/f'M2R1_{name}_REVIEW.step')
            render(parts,name,subtitle=f'Pitch {pitch:+} deg / Roll {roll:+} deg | original M2 support coordinates')
        if name == 'NEUTRAL':
            render(parts,'FRONT', (0,-1,0.05), 'Orthographic front view')
            render(parts,'TOP', (0.01,-0.01,1), 'Orthographic top view')
            render([c for c in parts if c.group not in ('upper_frame','frame_brackets')],
                   'STRUCTURE_EXPOSED', subtitle='Frame members hidden for internal review only')
    local_joint_views()
    reread = cq.importers.importStep(str(OUT/'step/M2R1_NEUTRAL_REVIEW.step')).val()
    expected = cq.Compound.makeCompound([c.shape for c in model.components_for_pose()])
    volume_delta = abs(reread.Volume()-expected.Volume())
    workspace = kinematics.workspace_audit()
    readback_valid = reread.isValid() and all(s.isValid() for s in reread.Solids())
    audit = {'revision':'M2R1', 'pose_reports':reports, 'assumptions':model.assumptions(),
             'workspace':workspace,
             'step_readback': {'valid':readback_valid, 'volume_delta_mm3':volume_delta,
                               'solid_count':len(reread.Solids())},
             'digital_pass':all(r['pass'] for r in reports.values()) and readback_valid and volume_delta<0.1 and workspace['passes'],
             'purchase_release':False,'fabrication_release':False, 'physical_test_executed':False}
    (OUT/'M2R1_CAD_AUDIT.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
    manifest = []
    for p in sorted((OUT/'step').glob('*.step')):
        manifest.append({'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    (OUT/'STEP_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    (OUT/'COMPONENT_REGISTER.json').write_text(json.dumps([
        {'name':c.name,'group':c.group,'material_or_assumption':c.material}
        for c in model.components_for_pose()],indent=2),encoding='utf-8')
    print('DIGITAL_PASS', audit['digital_pass'], 'STEP_VOLUME_DELTA', volume_delta, flush=True)
    return 0 if audit['digital_pass'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
