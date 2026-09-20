from dataclasses import dataclass, replace
from math import cos, degrees, radians, sin

import cadquery as cq

from .parameters import P, Pose


COLORS = {
    "navy": (0.09, 0.25, 0.37, 1.0),
    "teal": (0.16, 0.62, 0.56, 0.62),
    "cyan": (0.28, 0.71, 0.79, 1.0),
    "orange": (0.96, 0.64, 0.38, 1.0),
    "red": (0.91, 0.44, 0.32, 1.0),
    "yellow": (0.91, 0.77, 0.42, 1.0),
    "gray": (0.48, 0.53, 0.58, 1.0),
    "darkgray": (0.24, 0.29, 0.34, 1.0),
    "green": (0.24, 0.55, 0.37, 1.0),
    "clear": (0.58, 0.88, 0.92, 0.40),
}


@dataclass
class Component:
    name: str
    shape: cq.Shape
    color: tuple
    material: str
    category: str = "fabricated"
    notes: str = ""


def centered_box(length, width, height, center=(0.0, 0.0, 0.0)):
    x, y, z = center
    return cq.Workplane("XY").box(length, width, height).translate((x, y, z))


def square_tube(size, wall, length, z0):
    outer = centered_box(size, size, length, (0.0, 0.0, z0 + length / 2.0))
    inner = centered_box(
        size - 2.0 * wall,
        size - 2.0 * wall,
        length + 2.0,
        (0.0, 0.0, z0 + length / 2.0),
    )
    return outer.cut(inner)


def compound(shapes):
    values = [shape.val() if isinstance(shape, cq.Workplane) else shape for shape in shapes]
    return cq.Compound.makeCompound(values)


def rotate_translate(shape, pose: Pose, z_translation):
    result = shape.rotate((0, 0, 0), (1, 0, 0), pose.roll_deg)
    result = result.rotate((0, 0, 0), (0, 1, 0), pose.pitch_deg)
    return result.translate((0.0, 0.0, z_translation))


def transform_point(point, pose: Pose, z_translation):
    # Same extrinsic X(roll), then Y(pitch) convention as rotate_translate.
    x, y, z = point
    cr, sr = cos(radians(pose.roll_deg)), sin(radians(pose.roll_deg))
    cp, sp = cos(radians(pose.pitch_deg)), sin(radians(pose.pitch_deg))
    y1, z1 = y * cr - z * sr, y * sr + z * cr
    x2, z2 = x * cp + z1 * sp, -x * sp + z1 * cp
    return cq.Vector(x2, y1, z2 + z_translation)


def cylinder_between(start, end, radius):
    start = cq.Vector(*start) if not isinstance(start, cq.Vector) else start
    end = cq.Vector(*end) if not isinstance(end, cq.Vector) else end
    direction = end - start
    length = direction.Length
    if length <= 1e-9:
        raise ValueError("Cylinder endpoints coincide")
    base = cq.Workplane("XY").circle(radius).extrude(length)
    z_axis = cq.Vector(0.0, 0.0, 1.0)
    unit = direction.normalized()
    axis = z_axis.cross(unit)
    dot = max(-1.0, min(1.0, z_axis.dot(unit)))
    angle = degrees(__import__("math").acos(dot))
    if axis.Length > 1e-9 and abs(angle) > 1e-9:
        base = base.rotate((0, 0, 0), axis.toTuple(), angle)
    elif dot < 0:
        base = base.rotate((0, 0, 0), (1, 0, 0), 180.0)
    return base.translate(start.toTuple())


def platform_center_z(pose: Pose):
    return P.platform_joint_z_collapsed_mm + pose.lift_mm


def with_world_shape(component: Component, pose: Pose):
    return replace(
        component,
        shape=rotate_translate(component.shape, pose, platform_center_z(pose)),
    )
