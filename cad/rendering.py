from pathlib import Path

import vtk

from .assembly import components_for_pose
from .parameters import POSES, Pose


CAMERAS = {
    "iso": ((1250, -1450, 1050), (0, 0, 250), (0, 0, 1)),
    "front": ((1250, -10, 430), (0, 0, 250), (0, 0, 1)),
    "side": ((10, -1350, 430), (0, 0, 250), (0, 0, 1)),
    "low_iso": ((1250, -1450, 430), (0, 0, 150), (0, 0, 1)),
    "center_detail": ((430, -520, 390), (0, 0, 245), (0, 0, 1)),
    "radial_detail": ((900, -1050, 1050), (0, 0, 165), (0, 0, 1)),
    "joint_detail": ((760, -620, 470), (250, 0, 175), (0, 0, 1)),
    "limit_detail": ((900, -300, 650), (255, 0, 175), (0, 0, 1)),
    "limit_end": ((850, -90, 780), (255, 0, 175), (0, 0, 1)),
    "ortho_front": ((1800, 0, 260), (0, 0, 180), (0, 0, 1)),
    "ortho_side": ((0, -1800, 260), (0, 0, 180), (0, 0, 1)),
    "ortho_top": ((0, 0, 1900), (0, 0, 130), (0, 1, 0)),
    "internal_iso": ((1150, -1350, 900), (0, 0, 155), (0, 0, 1)),
    "exploded_iso": ((1500, -1750, 1250), (0, 0, 320), (0, 0, 1)),
    "annotated_iso": ((1500, -1750, 1200), (0, 0, 220), (0, 0, 1)),
}


def _actor(component):
    shape = component.shape.val() if hasattr(component.shape, "val") else component.shape
    vertices, triangles = shape.tessellate(1.2, 0.25)
    points = vtk.vtkPoints()
    for vertex in vertices:
        points.InsertNextPoint(vertex.x, vertex.y, vertex.z)
    cells = vtk.vtkCellArray()
    for tri in triangles:
        cell = vtk.vtkTriangle()
        cell.GetPointIds().SetId(0, tri[0])
        cell.GetPointIds().SetId(1, tri[1])
        cell.GetPointIds().SetId(2, tri[2])
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
    r, g, b, a = component.color
    actor.GetProperty().SetColor(r, g, b)
    actor.GetProperty().SetOpacity(a)
    actor.GetProperty().SetRoughness(0.45)
    actor.GetProperty().SetMetallic(0.05)
    return actor


def _callout(renderer, camera, number, anchor, label_position):
    line = vtk.vtkLineSource()
    line.SetPoint1(*anchor)
    line.SetPoint2(*label_position)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(line.GetOutputPort())
    line_actor = vtk.vtkActor()
    line_actor.SetMapper(mapper)
    line_actor.GetProperty().SetColor(0.08, 0.18, 0.28)
    line_actor.GetProperty().SetLineWidth(2.0)
    renderer.AddActor(line_actor)

    marker = vtk.vtkSphereSource()
    marker.SetCenter(*label_position)
    marker.SetRadius(18.0)
    marker.SetThetaResolution(32)
    marker.SetPhiResolution(16)
    marker_mapper = vtk.vtkPolyDataMapper()
    marker_mapper.SetInputConnection(marker.GetOutputPort())
    marker_actor = vtk.vtkActor()
    marker_actor.SetMapper(marker_mapper)
    marker_actor.GetProperty().SetColor(0.07, 0.18, 0.28)
    renderer.AddActor(marker_actor)

    vector_text = vtk.vtkVectorText()
    vector_text.SetText(str(number))
    vector_text.Update()
    bounds = vector_text.GetOutput().GetBounds()
    transform = vtk.vtkTransform()
    transform.Translate(
        -(bounds[0] + bounds[1]) / 2.0,
        -(bounds[2] + bounds[3]) / 2.0,
        0.0,
    )
    centered = vtk.vtkTransformPolyDataFilter()
    centered.SetTransform(transform)
    centered.SetInputConnection(vector_text.GetOutputPort())
    text_mapper = vtk.vtkPolyDataMapper()
    text_mapper.SetInputConnection(centered.GetOutputPort())
    text = vtk.vtkFollower()
    text.SetMapper(text_mapper)
    direction = [
        camera.GetPosition()[i] - label_position[i]
        for i in range(3)
    ]
    length = sum(value * value for value in direction) ** 0.5
    text.SetPosition(*[
        label_position[i] + direction[i] / length * 18.5
        for i in range(3)
    ])
    text.SetScale(20.0, 20.0, 20.0)
    text.SetCamera(camera)
    text.GetProperty().SetColor(1.0, 1.0, 1.0)
    text.GetProperty().SetAmbient(1.0)
    text.GetProperty().SetDiffuse(0.0)
    renderer.AddActor(text)


def render_pose(
    pose: Pose,
    path: Path,
    view="iso",
    size=(1600, 1000),
    include_names=None,
    exclude_names=None,
    component_offsets=None,
    annotations=None,
    legend_lines=None,
    state_text=None,
    show_floor=True,
    parallel_scale=None,
):
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.965, 0.972, 0.982)
    renderer.SetBackground2(0.78, 0.86, 0.91)
    renderer.GradientBackgroundOn()
    renderer.SetUseDepthPeeling(True)
    renderer.SetMaximumNumberOfPeels(20)
    for component in components_for_pose(pose):
        if include_names is not None and component.name not in include_names:
            continue
        if exclude_names is not None and component.name in exclude_names:
            continue
        actor = _actor(component)
        if component_offsets and component.name in component_offsets:
            actor.SetPosition(*component_offsets[component.name])
        renderer.AddActor(actor)

    # Floor is a visual datum only, not cart geometry.
    if show_floor:
        plane = vtk.vtkPlaneSource()
        plane.SetOrigin(-650, -600, -70)
        plane.SetPoint1(650, -600, -70)
        plane.SetPoint2(-650, 600, -70)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(plane.GetOutputPort())
        floor = vtk.vtkActor()
        floor.SetMapper(mapper)
        floor.GetProperty().SetColor(0.84, 0.86, 0.88)
        floor.GetProperty().SetOpacity(0.55)
        renderer.AddActor(floor)

    title = vtk.vtkTextActor()
    display_label = {
        "cart_disengaged": "CART RELEASED",
        "max_pitch_roll": "PITCH + ROLL LIMIT",
        "max_pitch": "PITCH LIMIT",
        "max_roll": "ROLL LIMIT",
    }.get(pose.label, pose.label.upper())
    title.SetInput(f"PHASE 2\nZ={pose.lift_mm:.0f} mm  PITCH={pose.pitch_deg:.1f} deg  ROLL={pose.roll_deg:.1f} deg")
    title.SetPosition(40, size[1] - 95)
    title.GetTextProperty().SetFontSize(25)
    title.GetTextProperty().SetColor(0.05, 0.15, 0.24)
    title.GetTextProperty().SetBold(True)
    renderer.AddActor2D(title)
    state = vtk.vtkTextActor()
    state.SetInput(state_text or f"RADIAL 3 | {display_label}")
    state.SetPosition(610, size[1] - 70)
    state.GetTextProperty().SetFontSize(25)
    state.GetTextProperty().SetColor(0.05, 0.15, 0.24)
    state.GetTextProperty().SetBold(True)
    renderer.AddActor2D(state)
    if legend_lines:
        legend = vtk.vtkTextActor()
        legend.SetInput("\n".join(legend_lines))
        legend.SetPosition(size[0] - 480, size[1] - 360)
        legend.GetTextProperty().SetFontSize(20)
        legend.GetTextProperty().SetColor(0.05, 0.15, 0.24)
        legend.GetTextProperty().SetBold(True)
        legend.GetTextProperty().SetLineSpacing(1.25)
        renderer.AddActor2D(legend)
    footer = vtk.vtkTextActor()
    footer.SetInput("PRELIMINARY | NOT FOR FABRICATION | CART INTERFACE PLACEHOLDER")
    footer.SetPosition(40, 25)
    footer.GetTextProperty().SetFontSize(16)
    footer.GetTextProperty().SetColor(0.65, 0.16, 0.12)
    renderer.AddActor2D(footer)

    camera = vtk.vtkCamera()
    position, focal, up = CAMERAS[view]
    camera.SetPosition(*position)
    camera.SetFocalPoint(*focal)
    camera.SetViewUp(*up)
    camera.SetViewAngle(34)
    if parallel_scale is not None:
        camera.ParallelProjectionOn()
        camera.SetParallelScale(parallel_scale)
    renderer.SetActiveCamera(camera)
    for number, anchor, label_position in annotations or ():
        _callout(renderer, camera, number, anchor, label_position)
    renderer.ResetCameraClippingRange()

    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(True)
    window.SetAlphaBitPlanes(True)
    window.SetMultiSamples(8)
    window.SetSize(*size)
    window.AddRenderer(renderer)
    window.Render()
    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.SetScale(1)
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


def render_all(output_dir: Path):
    outputs = []
    for name in ("collapsed", "neutral", "raised", "max_pitch", "max_roll", "max_pitch_roll", "cart_disengaged"):
        outputs.append(render_pose(POSES[name], output_dir / f"phase2_{name}.png"))
    outputs.append(render_pose(POSES["neutral"], output_dir / "phase2_cart_engaged.png", view="front"))
    outputs.append(render_pose(POSES["neutral"], output_dir / "phase2_diagonal_layout.png", view="low_iso"))
    guide_names = {
        "keyed_guide_outer",
        "keyed_guide_inner",
        "compact_cardan_lower",
        "compact_cardan_cross",
        "compact_cardan_upper",
        "compact_cardan_angle_stops",
    }
    outputs.append(render_pose(
        POSES["neutral"],
        output_dir / "phase2_gimbal_detail.png",
        view="center_detail",
        size=(1400, 1000),
        include_names=guide_names,
    ))
    outputs.append(render_pose(
        POSES["max_pitch_roll"],
        output_dir / "phase2_gimbal_limit.png",
        view="center_detail",
        size=(1400, 1000),
        include_names=guide_names,
    ))
    radial_names = {
        "keyed_guide_outer",
        "keyed_guide_inner",
        "compact_cardan_lower",
        "compact_cardan_cross",
        "compact_cardan_upper",
        "compact_cardan_angle_stops",
        "lower_actuator_brackets",
        "lower_actuator_bushings",
        "lower_actuator_misalignment_spacers",
        "lower_actuator_pins_retention",
        "upper_radial_clevises",
        "upper_actuator_bushings",
        "upper_actuator_misalignment_spacers",
        "upper_actuator_pins_retention",
        "actuator_A1",
        "actuator_A2",
        "actuator_A3",
        "actuator_A1_external_mechanical_stops",
        "actuator_A2_external_mechanical_stops",
        "actuator_A3_external_mechanical_stops",
        "actuator_A1_electrical_limits",
        "actuator_A2_electrical_limits",
        "actuator_A3_electrical_limits",
    }
    for index in (1, 2, 3):
        radial_names.update({
            f"actuator_A{index}_limit_fixed_carrier",
            f"actuator_A{index}_limit_guide_bushings",
            f"actuator_A{index}_limit_moving_striker",
            f"actuator_A{index}_electrical_trip_cams",
            f"actuator_A{index}_electrical_limit_brackets",
        })
    outputs.append(render_pose(
        POSES["neutral"],
        output_dir / "phase2_radial_tripod_detail.png",
        view="radial_detail",
        size=(1400, 1000),
        include_names=radial_names,
    ))
    joint_names = {
        "lower_actuator_brackets",
        "lower_actuator_bushings",
        "lower_actuator_misalignment_spacers",
        "lower_actuator_pins_retention",
        "upper_radial_clevises",
        "upper_actuator_bushings",
        "upper_actuator_misalignment_spacers",
        "upper_actuator_pins_retention",
        "actuator_A1",
    }
    outputs.append(render_pose(
        POSES["neutral"],
        output_dir / "phase2_actuator_joint_detail.png",
        view="joint_detail",
        size=(1400, 1000),
        include_names=joint_names,
    ))
    limit_names = {
        "actuator_A1",
        "actuator_A1_limit_fixed_carrier",
        "actuator_A1_limit_guide_bushings",
        "actuator_A1_limit_moving_striker",
        "actuator_A1_external_mechanical_stops",
        "actuator_A1_electrical_trip_cams",
        "actuator_A1_electrical_limit_brackets",
        "actuator_A1_electrical_limits",
    }
    outputs.append(render_pose(
        POSES["neutral"],
        output_dir / "phase2_actuator_limit_detail.png",
        view="limit_detail",
        size=(1500, 1000),
        include_names=limit_names,
        state_text="LS-01M | STATIC-BENCH MECHANICAL STOPS",
        show_floor=False,
        legend_lines=[
            "YELLOW  MOVING RODS / CROSSHEAD",
            "RED     MECHANICAL STOP COLLARS",
            "DARK    MB21-DERIVED FIXED CARRIER",
        ],
    ))
    outputs.append(render_pose(
        POSES["neutral"],
        output_dir / "phase2_actuator_limit_end_view.png",
        view="limit_end",
        size=(1500, 1000),
        include_names=limit_names,
        state_text="LS-01 | END VIEW",
        show_floor=False,
    ))
    outputs.append(render_pose(
        POSES["neutral"],
        output_dir / "phase2_internal_top_off.png",
        view="internal_iso",
        size=(1600, 1000),
        exclude_names={"upper_acrylic_panel"},
        state_text="RADIAL 3 | INTERNAL TOP-OFF",
    ))
    outputs.append(render_pose(
        POSES["neutral"],
        output_dir / "phase2_assembly_front.png",
        view="ortho_front",
        size=(1600, 1000),
        state_text="RADIAL 3 | FRONT ORTHOGRAPHIC",
        show_floor=False,
        parallel_scale=360.0,
    ))
    outputs.append(render_pose(
        POSES["neutral"],
        output_dir / "phase2_assembly_side.png",
        view="ortho_side",
        size=(1600, 1000),
        state_text="RADIAL 3 | SIDE ORTHOGRAPHIC",
        show_floor=False,
        parallel_scale=360.0,
    ))
    outputs.append(render_pose(
        POSES["neutral"],
        output_dir / "phase2_assembly_top.png",
        view="ortho_top",
        size=(1600, 1000),
        exclude_names={"upper_acrylic_panel"},
        state_text="RADIAL 3 | TOP ORTHOGRAPHIC",
        show_floor=False,
        parallel_scale=560.0,
    ))

    exploded_offsets = {}
    for name in {"lower_interface_plate"}:
        exploded_offsets[name] = (0.0, 0.0, 60.0)
    for name in {"lower_HFS8_frame"}:
        exploded_offsets[name] = (0.0, 0.0, 105.0)
    for name in {
        "lower_actuator_brackets",
        "lower_actuator_bushings",
        "lower_actuator_misalignment_spacers",
        "lower_actuator_pins_retention",
    }:
        exploded_offsets[name] = (0.0, 0.0, 135.0)
    for name in {
        "actuator_A1", "actuator_A2", "actuator_A3",
        "actuator_A1_external_mechanical_stops",
        "actuator_A2_external_mechanical_stops",
        "actuator_A3_external_mechanical_stops",
        "actuator_A1_electrical_limits",
        "actuator_A2_electrical_limits",
        "actuator_A3_electrical_limits",
    }:
        exploded_offsets[name] = (0.0, 0.0, 190.0)
    for index in (1, 2, 3):
        for suffix in (
            "limit_fixed_carrier",
            "limit_guide_bushings",
            "limit_moving_striker",
            "electrical_trip_cams",
            "electrical_limit_brackets",
        ):
            exploded_offsets[f"actuator_A{index}_{suffix}"] = (0.0, 0.0, 190.0)
    for name in {"keyed_guide_outer", "cable_guide"}:
        exploded_offsets[name] = (0.0, 0.0, 145.0)
    for name in {"keyed_guide_inner"}:
        exploded_offsets[name] = (0.0, 0.0, 205.0)
    for name in {
        "compact_cardan_lower",
        "compact_cardan_cross",
        "compact_cardan_upper",
        "compact_cardan_angle_stops",
    }:
        exploded_offsets[name] = (0.0, 0.0, 245.0)
    for name in {
        "upper_radial_clevises",
        "upper_actuator_bushings",
        "upper_actuator_misalignment_spacers",
        "upper_actuator_pins_retention",
    }:
        exploded_offsets[name] = (0.0, 0.0, 275.0)
    for name in {"upper_HFS8_frame", "upper_load_spreaders", "imu_bracket"}:
        exploded_offsets[name] = (0.0, 0.0, 315.0)
    exploded_offsets["upper_acrylic_panel"] = (0.0, 0.0, 365.0)
    outputs.append(render_pose(
        POSES["neutral"],
        output_dir / "phase2_exploded.png",
        view="exploded_iso",
        size=(1600, 1100),
        component_offsets=exploded_offsets,
        state_text="RADIAL 3 | LAYERED EXPLODED VIEW",
        show_floor=False,
    ))

    annotations = [
        (1, (-320.0, 260.0, 315.0), (-520.0, 420.0, 500.0)),
        (2, (400.0, 0.0, 285.0), (575.0, 40.0, 420.0)),
        (3, (245.0, -40.0, 170.0), (520.0, -250.0, 255.0)),
        (4, (0.0, 0.0, 185.0), (-190.0, -135.0, 355.0)),
        (5, (90.0, 0.0, 50.0), (265.0, 160.0, 100.0)),
        (6, (-300.0, -285.0, 28.0), (-525.0, -420.0, 145.0)),
        (7, (0.0, -350.0, 4.0), (-40.0, -560.0, 65.0)),
        (8, (300.0, 250.0, -20.0), (520.0, 360.0, 70.0)),
    ]
    legend_lines = [
        "1  UPPER DECK / FRAME",
        "2  UPPER JOINT PACKAGE",
        "3  RADIAL ACTUATORS A1-A3",
        "4  KEYED GUIDE + CARDAN",
        "5  LOWER JOINT PACKAGE",
        "6  LOWER STRUCTURAL FRAME",
        "7  UNIVERSAL LOWER PLATE",
        "8  CART RECEIVER / LATCH",
    ]
    outputs.append(render_pose(
        POSES["neutral"],
        output_dir / "phase2_annotated_assembly.png",
        view="annotated_iso",
        size=(1800, 1100),
        annotations=annotations,
        legend_lines=legend_lines,
        state_text="RADIAL 3 | NUMBERED ASSEMBLY",
        show_floor=False,
    ))
    return outputs
