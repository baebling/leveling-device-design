"""CAD-independent actuator geometry for Phase 1 engineering checks.

The render/export modules use CadQuery vectors.  Stroke, workspace, and load
screens need the same kinematics but must remain runnable without importing a
CAD kernel, so this module deliberately uses only scalar math.
"""

from math import cos, radians, sin, sqrt

from cad.parameters import P, Pose


def platform_center_z(pose: Pose):
    return P.platform_joint_z_collapsed_mm + pose.lift_mm


def transform_point(point, pose: Pose, z_translation):
    """Apply the project convention: world-X roll then world-Y pitch."""
    x, y, z = point
    cr, sr = cos(radians(pose.roll_deg)), sin(radians(pose.roll_deg))
    cp, sp = cos(radians(pose.pitch_deg)), sin(radians(pose.pitch_deg))
    y1, z1 = y * cr - z * sr, y * sr + z * cr
    x2, z2 = x * cp + z1 * sp, -x * sp + z1 * cp
    return (x2, y1, z2 + z_translation)


def actuator_lengths(pose: Pose):
    z_center = platform_center_z(pose)
    lengths = []
    for (x, y), (base_x, base_y) in zip(P.support_points_xy, P.base_points_xy):
        top_x, top_y, top_z = transform_point((x, y, 0.0), pose, z_center)
        dx = top_x - base_x
        dy = top_y - base_y
        dz = top_z - P.base_joint_z_mm
        lengths.append(sqrt(dx * dx + dy * dy + dz * dz))
    return tuple(lengths)
