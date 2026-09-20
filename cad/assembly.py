from pathlib import Path

import cadquery as cq

from . import actuator_joint, actuator_placeholder, cart_interface_placeholder, guide_mechanism, latch, lower_interface, sensor_brackets, upper_interface
from .common import Component, platform_center_z, transform_point
from .parameters import P, POSES, Pose, ROOT


def components_for_pose(pose: Pose):
    components = []
    components.extend(lower_interface.components())
    components.extend(actuator_joint.lower_components())
    components.extend(cart_interface_placeholder.components(pose))
    components.extend(latch.components(pose))
    components.append(guide_mechanism.outer_component())

    platform_z = platform_center_z(pose)
    components.append(guide_mechanism.inner_component(platform_z))
    components.extend(guide_mechanism.compact_cardan_components(pose, platform_z))
    components.extend(upper_interface.components(pose))
    components.extend(actuator_joint.upper_components(pose))
    components.extend(sensor_brackets.components(pose))

    for idx, ((x, y), (bx, by)) in enumerate(zip(P.support_points_xy, P.base_points_xy), start=1):
        base = (bx, by, P.base_joint_z_mm)
        top = transform_point((x, y, 0.0), pose, platform_z)
        base_pin_axis = cq.Vector(-by, bx, 0.0).normalized()
        local_top_pin_axis = cq.Vector(-y, x, 0.0).normalized()
        top_pin_axis = transform_point(local_top_pin_axis.toTuple(), pose, 0.0)
        name = f"actuator_A{idx}"
        components.append(actuator_placeholder.make_actuator(
            base,
            top,
            name,
            base_pin_axis=base_pin_axis,
            top_pin_axis=top_pin_axis,
        ))
        components.extend(actuator_placeholder.make_radial_limit_components(base, top, name))
    return components


def as_cq_assembly(pose: Pose):
    assembly = cq.Assembly(name=f"leveling_module_{pose.label}")
    for component in components_for_pose(pose):
        color = component.color
        assembly.add(
            component.shape,
            name=component.name,
            color=cq.Color(color[0], color[1], color[2], color[3]),
        )
    return assembly


def actuator_lengths(pose: Pose):
    platform_z = platform_center_z(pose)
    lengths = []
    for (x, y), (bx, by) in zip(P.support_points_xy, P.base_points_xy):
        top = transform_point((x, y, 0.0), pose, platform_z)
        bottom = cq.Vector(bx, by, P.base_joint_z_mm)
        lengths.append((top - bottom).Length)
    return tuple(lengths)


def export_step_states(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    exported = []
    for name in ("collapsed", "neutral", "raised", "max_pitch", "max_roll", "max_pitch_roll", "cart_disengaged"):
        path = output_dir / f"leveling_module_{name}.step"
        as_cq_assembly(POSES[name]).save(str(path), exportType="STEP", mode="default")
        exported.append(path)
    return exported


if __name__ == "__main__":
    export_step_states(ROOT / "outputs" / "cad" / "step")
