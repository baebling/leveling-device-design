from pathlib import Path

import cadquery as cq
import ezdxf

from .assembly import as_cq_assembly, components_for_pose, export_step_states
from .common import platform_center_z
from .guide_mechanism import compact_cardan_components, inner_component, outer_component
from .lower_interface import make_lower_plate
from .parameters import P, POSES
from .sensor_brackets import _cable_guide, _imu_bracket_local
from .upper_interface import _panel_local
from .factory_clevis_gimbal import assembly as factory_clevis_gimbal_assembly
from .navimro_pin_lug_gimbal import assembly as navimro_pin_lug_gimbal_assembly


def _export_dxf_profiles(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for filename, length, width, holes in (
        ("lower_interface_plate_profile.dxf", P.platform_length_mm, P.platform_width_mm,
         [(-350, -300), (-350, 300), (350, -300), (350, 300), (-250, -200), (-250, 200), (250, -200), (250, 200)]),
        ("upper_acrylic_panel_profile.dxf", P.platform_length_mm, P.platform_width_mm,
         [(x, y) for x in (-350, -175, 0, 175, 350) for y in (-300, -150, 0, 150, 300)]),
    ):
        doc = ezdxf.new("R2010")
        doc.header["$INSUNITS"] = 4  # millimetres
        msp = doc.modelspace()
        x0, y0 = -length / 2, -width / 2
        msp.add_lwpolyline([(x0, y0), (-x0, y0), (-x0, -y0), (x0, -y0)], close=True, dxfattribs={"layer": "CUT_OUTER"})
        diameter = 11.0 if filename.startswith("lower") else 8.5
        for point in holes:
            if filename.startswith("upper"):
                if (
                    abs(point[0]) < P.upper_service_opening_x_mm / 2.0
                    and abs(point[1]) < P.upper_service_opening_y_mm / 2.0
                ):
                    continue
            msp.add_circle(point, diameter / 2, dxfattribs={"layer": "CUT_HOLES"})
        if filename.startswith("upper") and P.upper_service_opening_x_mm > 0.0:
            hx = P.upper_service_opening_x_mm / 2.0
            hy = P.upper_service_opening_y_mm / 2.0
            msp.add_lwpolyline(
                [(-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy)],
                close=True,
                dxfattribs={"layer": "CUT_INNER"},
            )
        msp.add_text("PRELIMINARY - NOT APPROVED FOR FABRICATION", height=12, dxfattribs={"layer": "NOTES"}).set_placement((x0 + 20, y0 + 20))
        path = output_dir / filename
        doc.saveas(path)
        outputs.append(path)
    return outputs


def _export_guide_gimbal_states(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for pose_name in ("neutral", "max_pitch_roll"):
        pose = POSES[pose_name]
        platform_z = platform_center_z(pose)
        components = [outer_component(), inner_component(platform_z)]
        components.extend(compact_cardan_components(pose, platform_z))
        assembly = cq.Assembly(name=f"guide_gimbal_{pose_name}")
        for component in components:
            r, g, b, a = component.color
            assembly.add(component.shape, name=component.name, color=cq.Color(r, g, b, a))
        path = output_dir / f"guide_gimbal_{pose_name}.step"
        assembly.save(str(path), exportType="STEP", mode="default")
        outputs.append(path)
    return outputs


def _export_actuator_joint_packages(output_dir: Path):
    names = {
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
    }
    assembly = cq.Assembly(name="radial_actuator_joint_packages_neutral")
    for component in components_for_pose(POSES["neutral"]):
        if component.name not in names:
            continue
        r, g, b, a = component.color
        assembly.add(component.shape, name=component.name, color=cq.Color(r, g, b, a))
    path = output_dir / "radial_actuator_joint_packages_neutral.step"
    assembly.save(str(path), exportType="STEP", mode="default")
    return [path]


def _export_actuator_limit_package(output_dir: Path):
    names = {
        "actuator_A1",
        "actuator_A1_limit_fixed_carrier",
        "actuator_A1_limit_guide_bushings",
        "actuator_A1_limit_moving_striker",
        "actuator_A1_external_mechanical_stops",
        "actuator_A1_electrical_trip_cams",
        "actuator_A1_electrical_limit_brackets",
        "actuator_A1_electrical_limits",
    }
    assembly = cq.Assembly(name="ls01_actuator_limit_package_neutral")
    for component in components_for_pose(POSES["neutral"]):
        if component.name not in names:
            continue
        r, g, b, a = component.color
        assembly.add(component.shape, name=component.name, color=cq.Color(r, g, b, a))
    path = output_dir / "ls01_actuator_limit_package_neutral.step"
    assembly.save(str(path), exportType="STEP", mode="default")
    return [path]


def _export_factory_clevis_gimbal(output_dir: Path):
    path = output_dir / "jnt_cg01_factory_clevis_gimbal_seed.step"
    factory_clevis_gimbal_assembly().save(str(path), exportType="STEP", mode="default")
    return [path]


def _export_navimro_pin_lug_gimbal(output_dir: Path):
    path = output_dir / "navimro_pin_lug_gimbal_assumption.step"
    navimro_pin_lug_gimbal_assembly().save(str(path), exportType="STEP", mode="default")
    return [path]


def export_all(root: Path):
    cad_root = root / "outputs" / "cad"
    step_paths = export_step_states(cad_root / "step")
    step_paths += _export_guide_gimbal_states(cad_root / "step")
    step_paths += _export_actuator_joint_packages(cad_root / "step")
    step_paths += _export_actuator_limit_package(cad_root / "step")
    step_paths += _export_factory_clevis_gimbal(cad_root / "step")
    step_paths += _export_navimro_pin_lug_gimbal(cad_root / "step")
    stl_dir = cad_root / "stl"
    stl_dir.mkdir(parents=True, exist_ok=True)
    stl_paths = [stl_dir / "imu_bracket.stl", stl_dir / "cable_guide.stl"]
    cq.exporters.export(_imu_bracket_local().val(), str(stl_paths[0]), exportType="STL", tolerance=0.05, angularTolerance=0.1)
    cq.exporters.export(_cable_guide().val(), str(stl_paths[1]), exportType="STL", tolerance=0.05, angularTolerance=0.1)
    dxf_paths = _export_dxf_profiles(cad_root / "dxf")
    glb_dir = cad_root / "glb"
    glb_dir.mkdir(parents=True, exist_ok=True)
    glb_path = glb_dir / "leveling_module_neutral.glb"
    as_cq_assembly(POSES["neutral"]).save(str(glb_path), exportType="GLTF")
    return step_paths + stl_paths + dxf_paths + [glb_path]
