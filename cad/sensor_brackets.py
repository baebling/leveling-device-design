import cadquery as cq

from .common import COLORS, Component
from .parameters import P, Pose


def _imu_bracket_local():
    plate = cq.Workplane("XY").box(70, 55, 4)
    plate = plate.faces(">Z").workplane().pushPoints([(-25, -18), (-25, 18), (25, -18), (25, 18)]).hole(3.4)
    return plate.translate((0, -170, P.module_top_above_joint_mm - 2.0))


def _cable_guide():
    ring = cq.Workplane("XY").circle(18).circle(12).extrude(8)
    tab = cq.Workplane("XY").box(40, 12, 8).translate((18, 0, 4))
    return ring.union(tab).translate((-70, 0, 145))


def components(pose: Pose):
    from .common import with_world_shape
    imu = Component("imu_bracket", _imu_bracket_local().val(), COLORS["green"], "PETG/PA12 printed bracket", category="printable")
    guide = Component("cable_guide", _cable_guide().val(), COLORS["green"], "PETG/PA12 printed cable guide", category="printable")
    return [with_world_shape(imu, pose), guide]
