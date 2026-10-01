"""Rev E radial 3-RPS model using the supplied LM4075OE STEP geometry.

The detailed profile and frame-bracket groups come from the Fusion-native
Rev D export.  The provisional actuator envelopes are replaced
with the six named solids from the vendor STEP.  LMB-10 and the selected MISUMI
TRUSCO PHS6 are rebuilt as conservative supplier-interface envelopes from the
published dimensions.  These joint solids are for assembly/interference review,
not for manufacturing.  The upper frame is raised relative to the unchanged
actuator pin geometry to clear the full-length PHS6 body.  The legacy mixed
stop/fastener groups are invalid after this revision.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from math import sqrt
from pathlib import Path

import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.gp import gp_Trsf

from fusion_scripts.ProfileRadialRevD import revd_data
from scripts.render_lm4075oe_vendor_step import read_named_shapes


ROOT = Path(__file__).resolve().parents[1]
REVD_GROUP_DIR = ROOT / "outputs" / "profile_radial_revD_fusion_native" / "groups"
VENDOR_STEP = ROOT / "references" / "vendor_cad" / "LM4075OE-1075-100mm.stp"

VENDOR_REAR_PIN_MM = (11.409449, -228.951419, -5.366741)
VENDOR_FRONT_PIN_MM = (-193.590551, -228.951419, -5.366741)
VENDOR_COLLAPSED_PIN_MM = 205.0
VENDOR_MOVING_PART = "NEIGUAN"
VENDOR_PART_COLORS = {
    "UP": (0.18, 0.36, 0.55, 1.0),
    "END": (0.10, 0.16, 0.22, 1.0),
    "MOTER": (0.62, 0.66, 0.69, 1.0),
    "WAIKE": (0.20, 0.48, 0.70, 1.0),
    "FENGTOU": (0.88, 0.55, 0.12, 1.0),
    "NEIGUAN": (0.82, 0.84, 0.86, 1.0),
}
GROUP_COLORS = {
    "lower_frame": (0.12, 0.14, 0.16, 1.0),
    "lower_brackets": (0.45, 0.48, 0.51, 1.0),
    "lower_adapters": (0.12, 0.42, 0.68, 1.0),
    "lower_joints": (0.58, 0.61, 0.64, 1.0),
    "upper_frame": (0.12, 0.14, 0.16, 1.0),
    "upper_brackets": (0.45, 0.48, 0.51, 1.0),
    "upper_joints": (0.66, 0.69, 0.72, 1.0),
    "mechanical_stops": (0.72, 0.14, 0.10, 1.0),
    "fasteners": (0.20, 0.21, 0.23, 1.0),
}

# Rev E correction; the legacy Rev D STEP groups remain historical geometry.
UPPER_FRAME_RISE_MM = 15.0
UPPER_PHS_FASTENER_STACK = {
    "stud_length_mm": 25.0,
    "phs_thread_engagement_mm": 10.0,
    "slot_nut_thread_engagement_mm": 6.0,
    "jam_nut_thickness_mm": 5.0,
    "exposed_stud_gap_mm": 4.0,
}
LOWER_LMB_FASTENER_STACK = {
    "bolt_length_mm": 12.0,
    "bracket_base_mm": 3.0,
    "flat_washer_count_per_bolt": 3,
    "flat_washer_thickness_mm": 1.0,
    "adapter_plate_mm": 8.0,
    "thread_engagement_mm": 6.0,
    "nominal_tip_recess_mm": 2.0,
}

LMB10_DIMENSIONS = {
    "base_length_mm": 56.0,
    "outside_width_mm": 26.0,
    "inside_width_mm": 20.0,
    "sheet_thickness_mm": 3.0,
    "mount_hole_diameter_mm": 8.0,
    "mount_hole_pitch_mm": 36.0,
    "pivot_hole_diameter_mm": 6.2,
    "pivot_axis_height_mm": 36.0,
    "rear_height_mm": 17.0,
    "pivot_radius_mm": 8.0,
}

TRUSCO_PHS6_DIMENSIONS = {
    "order_code": "PHS6",
    "misumi_order_code": "280-7599",
    "bore_mm": 6.0,
    "female_thread": "M6",
    "allowable_angle_deg": 13.0,
    "overall_width_mm": 20.0,
    "center_distance_mm": 30.0,
    "overall_height_mm": 40.0,
    # Axial bearing width is not listed on the MISUMI result page.  A 10 mm
    # conservative envelope is used for clash checking and is not a drawing.
    "axial_envelope_mm": 10.0,
    "stem_envelope_diameter_mm": 10.0,
    # Keep the rod-end stud on the 3030 slot centerline.  The upper actuator
    # clevis, not this rod end, is shifted 1.5 mm along the pivot pin with
    # three 0.5 mm shims (see revd_data.upper_joint_side_offset_mm).
    "assembly_tangent_offset_mm": 0.0,
}

STATIC_GROUPS = ("lower_frame", "lower_brackets", "lower_adapters")
MOVING_GROUPS = ("upper_frame", "upper_brackets")
COLLAPSED_ONLY_GROUPS = ("mechanical_stops", "fasteners")
STRUCTURAL_STATIC_GROUPS = ("lower_frame", "lower_brackets", "lower_adapters")
STRUCTURAL_MOVING_GROUPS = ("upper_frame", "upper_brackets")


@dataclass(frozen=True)
class Pose:
    label: str
    lift_mm: float
    pitch_deg: float
    roll_deg: float


@dataclass(frozen=True)
class Part:
    name: str
    shape: cq.Shape
    color: tuple[float, float, float, float]
    group: str


POSES = {
    "collapsed": Pose("collapsed", 0.0, 0.0, 0.0),
    "neutral": Pose("neutral", 25.0, 0.0, 0.0),
    "raised": Pose("raised", 50.0, 0.0, 0.0),
    "pitch_p3": Pose("pitch_p3", 25.0, 3.0, 0.0),
    "pitch_m3": Pose("pitch_m3", 25.0, -3.0, 0.0),
    "roll_p3": Pose("roll_p3", 25.0, 0.0, 3.0),
    "roll_m3": Pose("roll_m3", 25.0, 0.0, -3.0),
    "p3_r3": Pose("p3_r3", 25.0, 3.0, 3.0),
    "p3_rm3": Pose("p3_rm3", 25.0, 3.0, -3.0),
    "pm3_r3": Pose("pm3_r3", 25.0, -3.0, 3.0),
    "pm3_rm3": Pose("pm3_rm3", 25.0, -3.0, -3.0),
}


def _shape(value) -> cq.Shape:
    if isinstance(value, cq.Shape):
        return value
    if hasattr(value, "val"):
        return value.val()
    return cq.Shape.cast(value)


def _dot(a, b):
    return sum(a[index] * b[index] for index in range(3))


def _sub(a, b):
    return tuple(a[index] - b[index] for index in range(3))


def _add(a, b):
    return tuple(a[index] + b[index] for index in range(3))


def _scale(a, amount):
    return tuple(value * amount for value in a)


def _cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _unit(value):
    length = sqrt(_dot(value, value))
    if length <= 1e-12:
        raise ValueError("Zero-length vector")
    return tuple(item / length for item in value)


def _matvec(matrix, vector):
    return tuple(_dot(row, vector) for row in matrix)


def _rigid_transform(shape, matrix, translation):
    transform = gp_Trsf()
    transform.SetValues(
        matrix[0][0], matrix[0][1], matrix[0][2], translation[0],
        matrix[1][0], matrix[1][1], matrix[1][2], translation[1],
        matrix[2][0], matrix[2][1], matrix[2][2], translation[2],
    )
    transformed = BRepBuilderAPI_Transform(_shape(shape).wrapped, transform, True).Shape()
    return cq.Shape.cast(transformed)


@lru_cache(maxsize=None)
def group_shape(name: str) -> cq.Shape:
    path = REVD_GROUP_DIR / f"{name}.step"
    if not path.exists():
        raise FileNotFoundError(path)
    solids = list(cq.importers.importStep(str(path)).solids().vals())
    return cq.Compound.makeCompound(solids)


@lru_cache(maxsize=1)
def vendor_shapes() -> tuple[tuple[str, cq.Shape], ...]:
    if not VENDOR_STEP.exists():
        raise FileNotFoundError(VENDOR_STEP)
    return tuple((name, cq.Shape.cast(shape)) for name, shape in read_named_shapes(VENDOR_STEP))


def platform_transform(pose: Pose):
    solved = revd_data.solve_platform(pose.pitch_deg, pose.roll_deg)
    rotation = revd_data.rotation_matrix(
        pose.pitch_deg, pose.roll_deg, solved["yaw_rad"]
    )
    source_origin = (0.0, 0.0, revd_data.P.upper_ring_z_collapsed_mm)
    target_origin = (
        solved["x_mm"],
        solved["y_mm"],
        revd_data.P.upper_ring_z_collapsed_mm + pose.lift_mm,
    )
    translation = _sub(target_origin, _matvec(rotation, source_origin))
    return rotation, translation, solved


def transform_upper_shape(shape, pose: Pose):
    rotation, translation, _ = platform_transform(pose)
    return _rigid_transform(shape, rotation, translation)


def transform_upper_frame_shape(shape, pose: Pose):
    shifted = _shape(shape).translate((0.0, 0.0, UPPER_FRAME_RISE_MM))
    return transform_upper_shape(shifted, pose)


def _local_lmb10_shape() -> cq.Shape:
    """Conservative LMB-10 envelope in radial/tangent/Z local coordinates."""

    d = LMB10_DIMENSIONS
    base = (
        cq.Workplane("XY")
        .box(d["base_length_mm"], d["outside_width_mm"], d["sheet_thickness_mm"], centered=(True, True, False))
    )
    for x_value in (-d["mount_hole_pitch_mm"] / 2.0, d["mount_hole_pitch_mm"] / 2.0):
        base = base.faces(">Z").workplane().pushPoints([(x_value, 0.0)]).hole(d["mount_hole_diameter_mm"])

    # Side-view boundary follows the supplier drawing's critical envelope:
    # 44 mm total, R8 around the pin, 17 mm rear, and a sloped web.
    side_profile = (
        (-28.0, d["sheet_thickness_mm"]),
        (-28.0, d["rear_height_mm"]),
        (10.0, 38.0),
        (10.0, 44.0),
        (18.0, 44.0),
        (26.0, d["pivot_axis_height_mm"]),
        (26.0, d["sheet_thickness_mm"]),
    )
    plane = cq.Plane(origin=(0.0, d["outside_width_mm"] / 2.0, 0.0), xDir=(1.0, 0.0, 0.0), normal=(0.0, -1.0, 0.0))
    ear = cq.Workplane(plane).polyline(side_profile).close().extrude(d["sheet_thickness_mm"])
    pivot_axis_start = (18.0, d["outside_width_mm"] / 2.0, d["pivot_axis_height_mm"])
    pivot_axis_end = (18.0, d["inside_width_mm"] / 2.0, d["pivot_axis_height_mm"])
    pivot = cq.Solid.makeCylinder(
        d["pivot_radius_mm"],
        d["sheet_thickness_mm"],
        cq.Vector(*pivot_axis_start),
        cq.Vector(0.0, -1.0, 0.0),
    )
    bore = cq.Solid.makeCylinder(
        d["pivot_hole_diameter_mm"] / 2.0,
        d["sheet_thickness_mm"] + 0.2,
        cq.Vector(pivot_axis_start[0], pivot_axis_start[1] + 0.1, pivot_axis_start[2]),
        cq.Vector(0.0, -1.0, 0.0),
    )
    right_ear = _shape(ear).fuse(pivot).cut(bore)
    left_ear = right_ear.translate((0.0, -23.0, 0.0))
    return cq.Compound.makeCompound([_shape(base), right_ear, left_ear])


@lru_cache(maxsize=1)
def lower_joint_shapes() -> tuple[cq.Shape, ...]:
    local = _local_lmb10_shape()
    rows = []
    for row in revd_data.adapter_rows():
        radial = row["radial"]
        tangent = row["tangent"]
        matrix = (
            (radial[0], tangent[0], 0.0),
            (radial[1], tangent[1], 0.0),
            (0.0, 0.0, 1.0),
        )
        lmb_x, lmb_y = row["lmb_center_mm"]
        rows.append(_rigid_transform(local, matrix, (lmb_x, lmb_y, 48.0)))
    return tuple(rows)


def _local_phs6_shape() -> cq.Shape:
    """MISUMI TRUSCO PHS6 supplier envelope centered on its pivot."""

    d = TRUSCO_PHS6_DIMENSIONS
    outer_radius = d["overall_width_mm"] / 2.0
    axial = d["axial_envelope_mm"]
    ring = cq.Solid.makeCylinder(
        outer_radius,
        axial,
        cq.Vector(0.0, -axial / 2.0, 0.0),
        cq.Vector(0.0, 1.0, 0.0),
    )
    bore = cq.Solid.makeCylinder(
        d["bore_mm"] / 2.0,
        axial + 0.2,
        cq.Vector(0.0, -axial / 2.0 - 0.1, 0.0),
        cq.Vector(0.0, 1.0, 0.0),
    )
    ring = ring.cut(bore)
    stem_start = outer_radius * 0.55
    stem_length = d["center_distance_mm"] - stem_start
    stem = cq.Solid.makeCylinder(
        d["stem_envelope_diameter_mm"] / 2.0,
        stem_length,
        cq.Vector(0.0, 0.0, stem_start),
        cq.Vector(0.0, 0.0, 1.0),
    )
    return ring.fuse(stem)


@lru_cache(maxsize=1)
def upper_joint_local_shapes() -> tuple[cq.Shape, ...]:
    local = _local_phs6_shape()
    rows = []
    for support, (_, tangent) in zip(revd_data.upper_support_points(), revd_data.support_basis()):
        radial = (tangent[1], -tangent[0], 0.0)
        matrix = (
            (radial[0], tangent[0], 0.0),
            (radial[1], tangent[1], 0.0),
            (0.0, 0.0, 1.0),
        )
        rows.append(
            _rigid_transform(
                local,
                matrix,
                (
                    support[0] + tangent[0] * TRUSCO_PHS6_DIMENSIONS["assembly_tangent_offset_mm"],
                    support[1] + tangent[1] * TRUSCO_PHS6_DIMENSIONS["assembly_tangent_offset_mm"],
                    revd_data.P.upper_ring_z_collapsed_mm,
                ),
            )
        )
    return tuple(rows)


def supplier_joint_parts(pose: Pose) -> list[Part]:
    rows = []
    for index, shape in enumerate(lower_joint_shapes(), start=1):
        rows.append(Part(f"A{index}_LMB10_SUPPLIER_ENVELOPE", shape, GROUP_COLORS["lower_joints"], "lower_joints"))
    for index, shape in enumerate(upper_joint_local_shapes(), start=1):
        rows.append(
            Part(
                f"A{index}_TRUSCO_PHS6_280-7599_SUPPLIER_ENVELOPE",
                transform_upper_shape(shape, pose),
                GROUP_COLORS["upper_joints"],
                "upper_joints",
            )
        )
    return rows


@lru_cache(maxsize=1)
def lower_lmb_bolt_shapes() -> tuple[cq.Shape, ...]:
    """Six M8x12 shanks and three 1 mm flat washers per bolt."""

    rows = []
    tip_z = 40.0 + LOWER_LMB_FASTENER_STACK["nominal_tip_recess_mm"]
    bearing_z = tip_z + LOWER_LMB_FASTENER_STACK["bolt_length_mm"]
    for adapter in revd_data.adapter_rows():
        for x, y in adapter["lmb_tapped_holes_mm"]:
            shank = cq.Solid.makeCylinder(4.0, bearing_z - tip_z, cq.Vector(x, y, tip_z))
            washers = cq.Solid.makeCylinder(8.5, 3.0, cq.Vector(x, y, 51.0)).cut(
                cq.Solid.makeCylinder(4.25, 3.0, cq.Vector(x, y, 51.0))
            )
            head = cq.Solid.makeCylinder(6.5, 8.0, cq.Vector(x, y, bearing_z))
            rows.append(cq.Compound.makeCompound((shank, washers, head)))
    return tuple(rows)


@lru_cache(maxsize=1)
def upper_phs_fastener_local_shapes() -> tuple[cq.Shape, ...]:
    """M6x25 stud with a jam nut against each PHS6 shank end."""

    rows = []
    for support, (_, tangent) in zip(revd_data.upper_support_points(), revd_data.support_basis()):
        x = support[0] + tangent[0] * TRUSCO_PHS6_DIMENSIONS["assembly_tangent_offset_mm"]
        y = support[1] + tangent[1] * TRUSCO_PHS6_DIMENSIONS["assembly_tangent_offset_mm"]
        z = revd_data.P.upper_ring_z_collapsed_mm
        stud = cq.Solid.makeCylinder(3.0, 25.0, cq.Vector(x, y, z + 20.0))
        nut = cq.Solid.makeCylinder(5.5, 5.0, cq.Vector(x, y, z + 30.0)).cut(
            cq.Solid.makeCylinder(3.0, 5.0, cq.Vector(x, y, z + 30.0))
        )
        rows.append(cq.Compound.makeCompound((stud, nut)))
    return tuple(rows)


def upper_eye_points(pose: Pose):
    return revd_data._upper_world_points(
        pose.lift_mm, pose.pitch_deg, pose.roll_deg
    )


def actuator_pin_lengths(pose: Pose):
    return tuple(
        sqrt(_dot(_sub(upper, lower), _sub(upper, lower)))
        for lower, upper in zip(revd_data.lower_eye_points(), upper_eye_points(pose))
    )


def actuator_parts(index: int, pose: Pose) -> list[Part]:
    lower = revd_data.lower_eye_points()[index - 1]
    upper = upper_eye_points(pose)[index - 1]
    tangent = revd_data.support_basis()[index - 1][1]
    actuator_axis = _unit(_sub(upper, lower))
    pin_length = sqrt(_dot(_sub(upper, lower), _sub(upper, lower)))
    extension = pin_length - VENDOR_COLLAPSED_PIN_MM

    # Source longitudinal basis is rear-to-front = -X and source pin axis = +Y.
    source_to_target = (
        (-actuator_axis[0], tangent[0], -_cross(actuator_axis, tangent)[0]),
        (-actuator_axis[1], tangent[1], -_cross(actuator_axis, tangent)[1]),
        (-actuator_axis[2], tangent[2], -_cross(actuator_axis, tangent)[2]),
    )
    translation = _sub(lower, _matvec(source_to_target, VENDOR_REAR_PIN_MM))
    rows = []
    for name, source_shape in vendor_shapes():
        shifted = source_shape
        if name == VENDOR_MOVING_PART:
            shifted = shifted.translate((-extension, 0.0, 0.0))
        transformed = _rigid_transform(shifted, source_to_target, translation)
        rows.append(
            Part(
                f"A{index}_LM4075OE_{name}_PIN_{pin_length:.3f}mm",
                transformed,
                VENDOR_PART_COLORS[name],
                "actuators",
            )
        )
    return rows


def components_for_pose(pose: Pose, include_collapsed_hardware=False) -> list[Part]:
    rows = []
    for name in STATIC_GROUPS:
        rows.append(Part(name.upper(), group_shape(name), GROUP_COLORS[name], name))
    for name in MOVING_GROUPS:
        rows.append(
            Part(
                name.upper(),
                transform_upper_frame_shape(group_shape(name), pose),
                GROUP_COLORS[name],
                name,
            )
        )
    rows.extend(supplier_joint_parts(pose))
    for index, shape in enumerate(lower_lmb_bolt_shapes(), start=1):
        rows.append(Part(f"LMB_M8x12_{index}", shape, GROUP_COLORS["fasteners"], "lower_fasteners"))
    for index, shape in enumerate(upper_phs_fastener_local_shapes(), start=1):
        rows.append(Part(f"PHS_M6x25_{index}", transform_upper_shape(shape, pose), GROUP_COLORS["fasteners"], "upper_fasteners"))
    for index in range(1, 4):
        rows.extend(actuator_parts(index, pose))
    if include_collapsed_hardware:
        raise ValueError("Legacy Rev D stop/fastener groups are invalid after the Rev E frame raise")
    return rows


def assembly_for_pose(pose: Pose, include_collapsed_hardware=False):
    assembly = cq.Assembly(name=f"PROFILE_RADIAL_3RPS_REVE_{pose.label.upper()}")
    for part in components_for_pose(pose, include_collapsed_hardware):
        assembly.add(part.shape, name=part.name, color=cq.Color(*part.color))
    return assembly


def _compound(shapes):
    return cq.Compound.makeCompound([_shape(shape) for shape in shapes])


def _intersection_volume(first, second):
    try:
        return _shape(first).intersect(_shape(second)).Volume()
    except Exception:
        return sum(
            _shape(first).intersect(solid).Volume() for solid in _shape(second).Solids()
        )


def _bounding_boxes_overlap(first, second, tolerance=1e-6):
    first_box = _shape(first).BoundingBox()
    second_box = _shape(second).BoundingBox()
    return not (
        first_box.xmax < second_box.xmin - tolerance
        or second_box.xmax < first_box.xmin - tolerance
        or first_box.ymax < second_box.ymin - tolerance
        or second_box.ymax < first_box.ymin - tolerance
        or first_box.zmax < second_box.zmin - tolerance
        or second_box.zmax < first_box.zmin - tolerance
    )


def _screened_intersection_volume(first, second):
    if not _bounding_boxes_overlap(first, second):
        return 0.0
    return _intersection_volume(first, second)


def collision_audit(pose: Pose):
    static_structure = _compound(group_shape(name) for name in STRUCTURAL_STATIC_GROUPS)
    moving_structure = _compound(
        transform_upper_frame_shape(group_shape(name), pose)
        for name in STRUCTURAL_MOVING_GROUPS
    )
    lower_joint_rows = list(lower_joint_shapes())
    upper_joint_rows = [
        transform_upper_shape(shape, pose) for shape in upper_joint_local_shapes()
    ]
    lower_joints = _compound(lower_joint_rows)
    upper_joints = _compound(upper_joint_rows)
    upper_phs_fasteners = _compound(
        transform_upper_shape(shape, pose) for shape in upper_phs_fastener_local_shapes()
    )
    lower_assembly = _compound((static_structure, lower_joints))
    upper_assembly = _compound((moving_structure, upper_joints))
    actuators = [
        _compound(part.shape for part in actuator_parts(index, pose))
        for index in range(1, 4)
    ]
    rows = [
        {
            "pair": "lower_structure__upper_structure",
            "volume_mm3": _intersection_volume(static_structure, moving_structure),
        },
        {
            "pair": "lower_joints__upper_assembly",
            "volume_mm3": _intersection_volume(lower_joints, upper_assembly),
        },
        {
            "pair": "upper_joints__upper_structure",
            "volume_mm3": _intersection_volume(upper_joints, moving_structure),
        },
        {
            "pair": "upper_phs_fasteners__upper_structure",
            "volume_mm3": _intersection_volume(upper_phs_fasteners, moving_structure),
        },
        {
            "pair": "lower_lmb_bolts__lower_frame",
            "volume_mm3": _intersection_volume(
                _compound(lower_lmb_bolt_shapes()), group_shape("lower_frame")
            ),
        },
        {
            "pair": "upper_joints__lower_assembly",
            "volume_mm3": _intersection_volume(upper_joints, lower_assembly),
        },
        {
            "pair": "lower_joints__upper_joints",
            "volume_mm3": _intersection_volume(lower_joints, upper_joints),
        },
    ]
    for index, actuator in enumerate(actuators, start=1):
        rows.extend(
            (
                {
                    "pair": f"actuator_{index}__lower_structure",
                    "volume_mm3": _intersection_volume(actuator, static_structure),
                },
                {
                    "pair": f"actuator_{index}__upper_structure",
                    "volume_mm3": _intersection_volume(actuator, moving_structure),
                },
            )
        )
        for joint_index, joint in enumerate(lower_joint_rows, start=1):
            rows.append(
                {
                    "pair": f"actuator_{index}__lower_joint_{joint_index}",
                    "volume_mm3": _screened_intersection_volume(actuator, joint),
                }
            )
        for joint_index, joint in enumerate(upper_joint_rows, start=1):
            rows.append(
                {
                    "pair": f"actuator_{index}__upper_joint_{joint_index}",
                    "volume_mm3": _screened_intersection_volume(actuator, joint),
                }
            )
    for first in range(3):
        for second in range(first + 1, 3):
            rows.append(
                {
                    "pair": f"actuator_{first + 1}__actuator_{second + 1}",
                    "volume_mm3": _intersection_volume(actuators[first], actuators[second]),
                }
            )
    for row in rows:
        row["volume_mm3"] = round(row["volume_mm3"], 6)
    maximum = max(row["volume_mm3"] for row in rows)
    return {"pose": pose.label, "maximum_volume_mm3": maximum, "passes": maximum < 0.1, "pairs": rows}


def full_pose_audit():
    rows = []
    for lift, pitch, roll in product(
        (0.0, 25.0, 50.0), (-3.0, 0.0, 3.0), (-3.0, 0.0, 3.0)
    ):
        pose = Pose(f"L{lift:g}_P{pitch:g}_R{roll:g}", lift, pitch, roll)
        lengths = actuator_pin_lengths(pose)
        collision = collision_audit(pose)
        rows.append(
            {
                "pose": pose.label,
                "lift_mm": lift,
                "pitch_deg": pitch,
                "roll_deg": roll,
                "pin_lengths_mm": [round(value, 6) for value in lengths],
                "minimum_retract_margin_mm": round(min(lengths) - 205.0, 6),
                "minimum_extend_margin_mm": round(305.0 - max(lengths), 6),
                "collision": collision,
            }
        )
    max_collision = max(row["collision"]["maximum_volume_mm3"] for row in rows)
    return {
        "revision": "E_ACTUAL_VENDOR_STEP_SUPPLIER_INTERFACES",
        "pose_count": len(rows),
        "vendor_step": str(VENDOR_STEP),
        "vendor_part_count": len(vendor_shapes()),
        "lower_joint_model": "LMB-10",
        "upper_joint_model": "TRUSCO PHS6 / 280-7599",
        "upper_frame_rise_mm": UPPER_FRAME_RISE_MM,
        "collapsed_upper_frame_top_mm": revd_data.P.upper_profile_top_z_collapsed_mm + UPPER_FRAME_RISE_MM,
        "lower_lmb_fastener_stack": LOWER_LMB_FASTENER_STACK,
        "upper_phs_fastener_stack": UPPER_PHS_FASTENER_STACK,
        "upper_clevis_shim_count_per_axis": 3,
        "upper_clevis_shim_thickness_mm": 0.5,
        "supplier_joint_envelopes_in_collision_audit": True,
        "joint_model_note": (
            "Supplier-interface envelopes from public dimensions; not fabrication drawings. "
            "TRUSCO PHS6 axial width is a conservative 10 mm envelope because MISUMI does not publish it on the order page."
        ),
        "collapsed_pin_center_mm": VENDOR_COLLAPSED_PIN_MM,
        "minimum_pin_mm": min(min(row["pin_lengths_mm"]) for row in rows),
        "maximum_pin_mm": max(max(row["pin_lengths_mm"]) for row in rows),
        "maximum_unintended_collision_volume_mm3": max_collision,
        "passes": all(
            row["minimum_retract_margin_mm"] >= 0.0
            and row["minimum_extend_margin_mm"] >= 0.0
            and row["collision"]["passes"]
            for row in rows
        ),
        "rows": rows,
    }
