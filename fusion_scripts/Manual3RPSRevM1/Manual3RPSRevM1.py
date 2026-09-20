"""Fusion 360 native generator for the manual 3-RPS Rev M1 assembly."""

import json
import importlib.util
import math
import os
import sys
import time
import traceback

import adsk.core
import adsk.fusion


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

DATA_MODULE_NAME = "manual_3rps_rev_m1_data_runtime"
DATA_PATH = os.path.join(SCRIPT_DIR, "m1_data.py")
DATA_SPEC = importlib.util.spec_from_file_location(DATA_MODULE_NAME, DATA_PATH)
if DATA_SPEC is None or DATA_SPEC.loader is None:
    raise RuntimeError(f"Cannot load Rev M1 parameter module: {DATA_PATH}")
m1_data = importlib.util.module_from_spec(DATA_SPEC)
sys.modules[DATA_MODULE_NAME] = m1_data
DATA_SPEC.loader.exec_module(m1_data)

LOWER_CROSSBAR_Y_MM = m1_data.LOWER_CROSSBAR_Y_MM
LOWER_CONNECTOR_EDGE_OFFSET_MM = m1_data.P.lower_profile_mm / 2.0
P = m1_data.P
UPPER_CROSSBAR_Y_MM = m1_data.UPPER_CROSSBAR_Y_MM
UPPER_CONNECTOR_EDGE_OFFSET_MM = m1_data.P.upper_profile_mm / 2.0
adapter_rows = m1_data.adapter_rows
full_audit = m1_data.full_audit
lower_eye_points = m1_data.lower_eye_points
support_basis = m1_data.support_basis
upper_eye_local_points = m1_data.upper_eye_local_points
upper_support_points = lambda: m1_data.support_points(P.upper_support_radius_mm)


PROJECT_ROOT = r"C:\Users\gangm\OneDrive\2. 연구실\지원사업\BIZ-Lab 창업클럽\수평유지장치설계 프로젝트"
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "outputs", "manual_3rps_rev_m1_fusion_native")
F3D_PATH = os.path.join(OUTPUT_DIR, "Manual_3RPS_RevM1_NATIVE.f3d")
STEP_PATH = os.path.join(OUTPUT_DIR, "Manual_3RPS_RevM1_NEUTRAL.step")
IMAGE_PATH = os.path.join(OUTPUT_DIR, "Manual_3RPS_RevM1_Fusion.png")
IMAGE_TOP_PATH = os.path.join(OUTPUT_DIR, "Manual_3RPS_RevM1_TOP.png")
IMAGE_SIDE_PATH = os.path.join(OUTPUT_DIR, "Manual_3RPS_RevM1_SIDE.png")
IMAGE_A1_DETAIL_PATH = os.path.join(OUTPUT_DIR, "Manual_3RPS_RevM1_A1_DETAIL.png")
IMAGE_A1_SECTION_PATH = os.path.join(OUTPUT_DIR, "Manual_3RPS_RevM1_A1_SECTION.png")
VALIDATION_PATH = os.path.join(OUTPUT_DIR, "Manual_3RPS_RevM1_validation.json")
INTERFERENCE_PATH = os.path.join(OUTPUT_DIR, "Manual_3RPS_RevM1_fusion_interference.json")
ERROR_PATH = os.path.join(OUTPUT_DIR, "Manual3RPSRevM1_ERROR.txt")
GROUP_STEP_DIR = os.path.join(OUTPUT_DIR, "groups")


APP = None
DESIGN = None
ROOT = None
TBM = None
APPEARANCES = {}
COMPONENT_NAMES = []
GROUP_COMPONENTS = {}


def mm(value):
    return float(value) / 10.0


def point(value):
    return adsk.core.Point3D.create(mm(value[0]), mm(value[1]), mm(value[2]))


def vector(value):
    result = adsk.core.Vector3D.create(float(value[0]), float(value[1]), float(value[2]))
    if not result.normalize():
        raise ValueError("Zero-length direction vector")
    return result


def unit(value):
    length = math.sqrt(sum(item * item for item in value))
    if length <= 1e-12:
        raise ValueError("Zero-length vector")
    return tuple(item / length for item in value)


def add(a, b):
    return tuple(a[index] + b[index] for index in range(3))


def sub(a, b):
    return tuple(a[index] - b[index] for index in range(3))


def scale(value, amount):
    return tuple(item * amount for item in value)


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def midpoint(a, b):
    return tuple((a[index] + b[index]) / 2.0 for index in range(3))


def box(center, length, width, height, length_dir=(1.0, 0.0, 0.0), width_dir=(0.0, 1.0, 0.0)):
    bounds = adsk.core.OrientedBoundingBox3D.create(
        point(center),
        vector(length_dir),
        vector(width_dir),
        mm(length),
        mm(width),
        mm(height),
    )
    return TBM.createBox(bounds)


def cylinder(start, end, radius):
    return TBM.createCylinderOrCone(point(start), mm(radius), point(end), mm(radius))


def cut(target, tool, label):
    if not TBM.booleanOperation(
        target, tool, adsk.fusion.BooleanTypes.DifferenceBooleanType
    ):
        raise RuntimeError("Boolean cut failed: " + label)
    return target


def union(target, tool, label):
    if not TBM.booleanOperation(
        target, tool, adsk.fusion.BooleanTypes.UnionBooleanType
    ):
        raise RuntimeError("Boolean union failed: " + label)
    return target


def ring(center, axis, outer_radius, bore_radius, width):
    direction = unit(axis)
    first = add(center, scale(direction, -width / 2.0))
    second = add(center, scale(direction, width / 2.0))
    body = cylinder(first, second, outer_radius)
    cutter = cylinder(
        add(first, scale(direction, -1.0)),
        add(second, scale(direction, 1.0)),
        bore_radius,
    )
    return cut(body, cutter, "ring bore")


def identity():
    return adsk.core.Matrix3D.create()


def create_group(name):
    occurrence = ROOT.occurrences.addNewComponent(identity())
    occurrence.component.name = name
    return occurrence.component


def add_component(parent, name, bodies, appearance_name=None):
    occurrence = parent.occurrences.addNewComponent(identity())
    component = occurrence.component
    component.name = name
    COMPONENT_NAMES.append(name)
    if not isinstance(bodies, (list, tuple)):
        bodies = [bodies]
    for index, temporary in enumerate(bodies, start=1):
        persisted = component.bRepBodies.add(temporary)
        persisted.name = name + ("_BODY" if len(bodies) == 1 else f"_BODY_{index:02d}")
        appearance = APPEARANCES.get(appearance_name)
        if appearance:
            try:
                persisted.appearance = appearance
            except Exception:
                pass
    return occurrence


def create_appearance(name, rgb):
    try:
        existing = DESIGN.appearances.itemByName(name)
        if existing:
            return existing
        base = None
        for library_index in range(APP.materialLibraries.count):
            library = APP.materialLibraries.item(library_index)
            for appearance_index in range(library.appearances.count):
                candidate = library.appearances.item(appearance_index)
                if "Paint" in candidate.name or "Plastic" in candidate.name:
                    base = candidate
                    break
            if base:
                break
        if not base:
            for library_index in range(APP.materialLibraries.count):
                library = APP.materialLibraries.item(library_index)
                if library.appearances.count:
                    base = library.appearances.item(0)
                    break
        if not base:
            return None
        result = DESIGN.appearances.addByCopy(base, name)
        color = adsk.core.Color.create(rgb[0], rgb[1], rgb[2], 255)
        for property_id in ("generic_diffuse", "opaque_albedo"):
            try:
                prop = result.appearanceProperties.itemById(property_id)
                if prop:
                    prop.value = color
                    break
            except Exception:
                continue
        return result
    except Exception:
        return None


def setup_appearances():
    palette = {
        "PROFILE": (32, 38, 44),
        "BRACKET": (155, 165, 173),
        "ADAPTER": (36, 112, 168),
        "ACTUATOR": (220, 158, 20),
        "ROD": (195, 202, 207),
        "JOINT": (174, 181, 187),
        "FASTENER": (45, 48, 52),
        "STOP": (172, 48, 40),
        "BUSHING": (232, 202, 62),
        "POM": (240, 240, 232),
        "STUD": (106, 110, 116),
    }
    for name, rgb in palette.items():
        APPEARANCES[name] = create_appearance("RevM1_" + name, rgb)


def profile_body(axis, center, length, section, slot_width, slot_depth, center_bore):
    cavity_width = 18.5 if section == 40.0 else 15.5
    cavity_depth = 5.4 if section == 40.0 else 4.4
    cavity_offset = section / 2.0 - slot_depth - cavity_depth / 2.0
    if axis == "X":
        body = box(center, length, section, section)
        body = cut(
            body,
            box(
                (center[0], center[1], center[2] + section / 2.0 - slot_depth / 2.0 + 0.1),
                length + 2.0,
                slot_width,
                slot_depth + 0.2,
            ),
            "profile top slot",
        )
        body = cut(
            body,
            box(
                (center[0], center[1], center[2] - section / 2.0 + slot_depth / 2.0 - 0.1),
                length + 2.0,
                slot_width,
                slot_depth + 0.2,
            ),
            "profile bottom slot",
        )
        body = cut(
            body,
            box(
                (center[0], center[1] + section / 2.0 - slot_depth / 2.0 + 0.1, center[2]),
                length + 2.0,
                slot_depth + 0.2,
                slot_width,
            ),
            "profile side slot positive",
        )
        body = cut(
            body,
            box(
                (center[0], center[1] - section / 2.0 + slot_depth / 2.0 - 0.1, center[2]),
                length + 2.0,
                slot_depth + 0.2,
                slot_width,
            ),
            "profile side slot negative",
        )
        for sign, label in ((1.0, "positive"), (-1.0, "negative")):
            body = cut(
                body,
                box(
                    (center[0], center[1], center[2] + sign * cavity_offset),
                    length + 2.0,
                    cavity_width,
                    cavity_depth,
                ),
                "profile top/bottom undercut " + label,
            )
            body = cut(
                body,
                box(
                    (center[0], center[1] + sign * cavity_offset, center[2]),
                    length + 2.0,
                    cavity_depth,
                    cavity_width,
                ),
                "profile side undercut " + label,
            )
        body = cut(
            body,
            cylinder(
                (center[0] - length / 2.0 - 1.0, center[1], center[2]),
                (center[0] + length / 2.0 + 1.0, center[1], center[2]),
                center_bore / 2.0,
            ),
            "profile center bore",
        )
        return body

    body = box(center, section, length, section)
    body = cut(
        body,
        box(
            (center[0], center[1], center[2] + section / 2.0 - slot_depth / 2.0 + 0.1),
            slot_width,
            length + 2.0,
            slot_depth + 0.2,
        ),
        "profile top slot",
    )
    body = cut(
        body,
        box(
            (center[0], center[1], center[2] - section / 2.0 + slot_depth / 2.0 - 0.1),
            slot_width,
            length + 2.0,
            slot_depth + 0.2,
        ),
        "profile bottom slot",
    )
    body = cut(
        body,
        box(
            (center[0] + section / 2.0 - slot_depth / 2.0 + 0.1, center[1], center[2]),
            slot_depth + 0.2,
            length + 2.0,
            slot_width,
        ),
        "profile side slot positive",
    )
    body = cut(
        body,
        box(
            (center[0] - section / 2.0 + slot_depth / 2.0 - 0.1, center[1], center[2]),
            slot_depth + 0.2,
            length + 2.0,
            slot_width,
        ),
        "profile side slot negative",
    )
    for sign, label in ((1.0, "positive"), (-1.0, "negative")):
        body = cut(
            body,
            box(
                (center[0], center[1], center[2] + sign * cavity_offset),
                cavity_width,
                length + 2.0,
                cavity_depth,
            ),
            "profile top/bottom undercut " + label,
        )
        body = cut(
            body,
            box(
                (center[0] + sign * cavity_offset, center[1], center[2]),
                cavity_depth,
                length + 2.0,
                cavity_width,
            ),
            "profile side undercut " + label,
        )
    body = cut(
        body,
        cylinder(
            (center[0], center[1] - length / 2.0 - 1.0, center[2]),
            (center[0], center[1] + length / 2.0 + 1.0, center[2]),
            center_bore / 2.0,
        ),
        "profile center bore",
    )
    return body


def add_profile(parent, name, axis, center, length, section):
    if section == 40.0:
        body = profile_body(axis, center, length, section, 8.3, 4.5, 6.8)
    else:
        body = profile_body(axis, center, length, section, 6.3, 2.5, 6.0)
    return add_component(parent, name, body, "PROFILE")


def add_bolt_component(
    parent,
    name,
    start,
    end,
    diameter,
    head_radius,
    head_length,
    nut_size=None,
    thread_start=None,
    thread_core_diameter=None,
):
    direction = unit(sub(end, start))
    if thread_start is not None and thread_core_diameter is not None:
        shaft = cylinder(start, thread_start, diameter / 2.0)
        core_start = add(thread_start, scale(direction, -0.1))
        core = cylinder(core_start, end, thread_core_diameter / 2.0)
        bodies = [union(shaft, core, name + " thread core")]
    else:
        bodies = [cylinder(start, end, diameter / 2.0)]
    head_start = add(start, scale(direction, -head_length))
    bodies.append(cylinder(head_start, start, head_radius))
    if nut_size:
        nut_center = add(end, scale(direction, nut_size[2] / 2.0))
        reference = (0.0, 0.0, 1.0)
        if abs(direction[2]) > 0.8:
            reference = (0.0, 1.0, 0.0)
        length_dir = unit(cross(reference, direction))
        width_dir = unit(cross(direction, length_dir))
        bodies.append(
            box(
                nut_center,
                nut_size[0],
                nut_size[1],
                nut_size[2],
                length_dir,
                width_dir,
            )
        )
    return add_component(parent, name, bodies, "FASTENER")


def add_inside_corner(parent_brackets, parent_fasteners, name, corner, sx, sy, leg, thickness, height, z_center, bolt_diameter):
    x, y = corner
    first_leg = box(
        (x + sx * leg / 2.0, y + sy * thickness / 2.0, z_center),
        leg,
        thickness,
        height,
    )
    second_leg = box(
        (x + sx * thickness / 2.0, y + sy * leg / 2.0, z_center),
        thickness,
        leg,
        height,
    )
    bracket = union(first_leg, second_leg, name + " L bracket")
    clearance_radius = bolt_diameter / 2.0 + 0.3
    bracket = cut(
        bracket,
        cylinder(
            (x - sx * 15.0, y + sy * leg / 2.0, z_center),
            (x + sx * (thickness + 15.0), y + sy * leg / 2.0, z_center),
            clearance_radius,
        ),
        name + " X clearance hole",
    )
    bracket = cut(
        bracket,
        cylinder(
            (x + sx * leg / 2.0, y - sy * 15.0, z_center),
            (x + sx * leg / 2.0, y + sy * (thickness + 15.0), z_center),
            clearance_radius,
        ),
        name + " Y clearance hole",
    )
    add_component(parent_brackets, name, bracket, "BRACKET")
    z = z_center
    slot_depth = 4.5 if bolt_diameter >= 7.0 else 2.5
    nut_size = (18.0, 12.0, 5.0) if bolt_diameter >= 7.0 else (15.0, 10.0, 4.0)
    add_bolt_component(
        parent_fasteners,
        name + "_BOLT_X",
        (x + sx * thickness, y + sy * leg / 2.0, z),
        (x - sx * slot_depth, y + sy * leg / 2.0, z),
        bolt_diameter,
        bolt_diameter * 0.85,
        4.0,
        nut_size,
    )
    add_bolt_component(
        parent_fasteners,
        name + "_BOLT_Y",
        (x + sx * leg / 2.0, y + sy * thickness, z),
        (x + sx * leg / 2.0, y - sy * slot_depth, z),
        bolt_diameter,
        bolt_diameter * 0.85,
        4.0,
        nut_size,
    )


def add_frame_connectors(bracket_group, fastener_group, crossbar_y_values, inner_x, upper=False):
    edge_offset = (
        UPPER_CONNECTOR_EDGE_OFFSET_MM if upper else LOWER_CONNECTOR_EDGE_OFFSET_MM
    )
    for row_index, y in enumerate(crossbar_y_values, start=1):
        if y >= 200.0:
            sy = -1.0
        elif y <= -200.0:
            sy = 1.0
        elif y > 0.0:
            sy = 1.0
        else:
            sy = -1.0
        for side_name, x, sx in (("L", -inner_x, 1.0), ("R", inner_x, -1.0)):
            if upper:
                add_inside_corner(
                    bracket_group,
                    fastener_group,
                    f"DCB3025_{row_index}_{side_name}",
                    (x, y + sy * edge_offset),
                    sx,
                    sy,
                    30.0,
                    5.0,
                    25.0,
                    285.0,
                    6.0,
                )
            else:
                add_inside_corner(
                    bracket_group,
                    fastener_group,
                    f"BRACKET4035_{row_index}_{side_name}",
                    (x, y + sy * edge_offset),
                    sx,
                    sy,
                    40.0,
                    6.0,
                    35.0,
                    20.0,
                    8.0,
                )


def add_adapter_and_lmb(adapter_group, joint_group, fastener_group, row):
    cx, cy = row["center_mm"]
    plate = box((cx, cy, 44.0), P.adapter_length_x_mm, P.adapter_width_y_mm, P.adapter_thickness_mm)
    for hole_index, (hx, hy) in enumerate(row["profile_mount_holes_mm"], start=1):
        plate = cut(
            plate,
            cylinder((hx, hy, 38.0), (hx, hy, 50.0), 4.5),
            row["id"] + f" profile hole {hole_index}",
        )
    for hole_index, (hx, hy) in enumerate(row["lmb_tapped_holes_mm"], start=1):
        plate = cut(
            plate,
            cylinder((hx, hy, 38.0), (hx, hy, 50.0), 3.4),
            row["id"] + f" LMB tap {hole_index}",
        )
    add_component(adapter_group, row["id"] + "_LMB_RADIAL_ADAPTER_120x70x8", plate, "ADAPTER")

    for hole_index, (hx, hy) in enumerate(row["profile_mount_holes_mm"], start=1):
        add_bolt_component(
            fastener_group,
            row["id"] + f"_ADAPTER_M8x20_{hole_index}",
            (hx, hy, 52.0),
            (hx, hy, 35.5),
            8.0,
            7.0,
            4.0,
            (18.0, 10.0, 5.0),
        )

    radial = row["radial"]
    tangent = row["tangent"]
    lmb_x, lmb_y = row["lmb_center_mm"]
    base = box(
        (lmb_x, lmb_y, 49.5),
        56.0,
        26.0,
        3.0,
        radial,
        tangent,
    )
    for hole_index, (hx, hy) in enumerate(row["lmb_tapped_holes_mm"], start=1):
        base = cut(
            base,
            cylinder((hx, hy, 46.0), (hx, hy, 53.0), 4.2),
            row["id"] + f" LMB base clearance {hole_index}",
        )
    ear_bodies = []
    for sign in (-1.0, 1.0):
        ear_center = (
            lmb_x + tangent[0] * sign * 11.5,
            lmb_y + tangent[1] * sign * 11.5,
            71.5,
        )
        ear = box(ear_center, 32.0, 3.0, 41.0, radial, tangent)
        ear = cut(
            ear,
            cylinder(
                (
                    lmb_x - tangent[0] * 18.0,
                    lmb_y - tangent[1] * 18.0,
                    P.lower_pin_z_mm,
                ),
                (
                    lmb_x + tangent[0] * 18.0,
                    lmb_y + tangent[1] * 18.0,
                    P.lower_pin_z_mm,
                ),
                3.1,
            ),
            row["id"] + " LMB pivot bore",
        )
        ear_bodies.append(ear)
    add_component(joint_group, row["id"] + "_LMB10", [base] + ear_bodies, "BRACKET")

    for hole_index, (hx, hy) in enumerate(row["lmb_tapped_holes_mm"], start=1):
        add_bolt_component(
            fastener_group,
            row["id"] + f"_LMB_M8x16_{hole_index}",
            (hx, hy, 55.0),
            (hx, hy, 41.0),
            8.0,
            7.0,
            4.0,
            thread_start=(hx, hy, 48.1),
            thread_core_diameter=6.6,
        )

    pin_start = (
        lmb_x - tangent[0] * 18.0,
        lmb_y - tangent[1] * 18.0,
        P.lower_pin_z_mm,
    )
    pin_end = (
        lmb_x + tangent[0] * 18.0,
        lmb_y + tangent[1] * 18.0,
        P.lower_pin_z_mm,
    )
    add_bolt_component(
        fastener_group,
        row["id"] + "_LMB_PIVOT_PIN_M6",
        pin_start,
        pin_end,
        6.0,
        5.0,
        3.0,
        (10.0, 10.0, 4.0),
    )


def add_actuator(actuator_group, index, lower, upper, tangent):
    axis = unit(sub(upper, lower))
    pin_length = math.sqrt(sum((upper[i] - lower[i]) ** 2 for i in range(3)))
    motor_start = add(lower, scale(axis, 19.0))
    motor_end = add(lower, scale(axis, 119.0))
    tube_start = add(lower, scale(axis, 85.0))
    tube_end = add(lower, scale(axis, min(174.0, pin_length - 31.0)))
    rod_start = add(lower, scale(axis, 150.0))
    rod_end = add(
        upper,
        scale(axis, -(P.actuator_eye_outer_radius_mm - P.upper_rod_eye_overlap_mm)),
    )
    lower_eye = ring(lower, tangent, P.actuator_eye_outer_radius_mm, 3.2, 18.0)
    upper_eye = ring(upper, tangent, P.actuator_eye_outer_radius_mm, 3.2, 18.0)
    motor_body = box(midpoint(motor_start, motor_end), 100.0, 40.0, 75.0, axis, tangent)
    tube = cylinder(tube_start, tube_end, 16.0)
    tube = cut(
        tube,
        cylinder(
            add(tube_start, scale(axis, -1.0)),
            add(tube_end, scale(axis, 1.0)),
            11.0,
        ),
        f"A{index} actuator tube bore",
    )
    neck = cylinder(
        add(lower, scale(axis, 6.0)),
        add(lower, scale(axis, 90.0)),
        7.0,
    )
    motor_body = union(motor_body, tube, f"A{index} motor and tube")
    motor_body = union(motor_body, neck, f"A{index} body neck")
    motor_body = union(motor_body, lower_eye, f"A{index} lower eye")
    add_component(
        actuator_group,
        f"A{index}_LM4075OE_BODY_PINLEN_{pin_length:.2f}mm",
        motor_body,
        "ACTUATOR",
    )
    moving_rod = cylinder(rod_start, rod_end, 10.0)
    moving_rod = union(moving_rod, upper_eye, f"A{index} upper eye")
    add_component(
        actuator_group,
        f"A{index}_LM4075OE_ROD",
        moving_rod,
        "ROD",
    )


def add_phs_and_upper_fastener(joint_group, fastener_group, index, support, upper_eye, tangent):
    sx, sy = support
    phs_center = (sx, sy, P.upper_ring_z_collapsed_mm)
    phs_stem = cylinder((sx, sy, 244.0), (sx, sy, 265.0), 4.5)
    phs_stem = cut(
        phs_stem,
        cylinder((sx, sy, 256.0), (sx, sy, 266.0), 2.5),
        f"A{index} PHS6 M6 tap core",
    )
    jam_nut = cylinder((sx, sy, 265.0), (sx, sy, 270.0), 7.0)
    jam_nut = cut(
        jam_nut,
        cylinder((sx, sy, 264.0), (sx, sy, 271.0), 3.2),
        f"A{index} PHS6 jam nut clearance",
    )
    phs_bodies = [
        ring(phs_center, tangent, 9.0, 3.0, 9.0),
        phs_stem,
        jam_nut,
    ]
    add_component(joint_group, f"A{index}_PHS6_AND_JAM_NUT", phs_bodies, "JOINT")

    bolt_center = upper_eye
    first = add(bolt_center, scale(tangent, -25.0))
    second = add(bolt_center, scale(tangent, 25.0))
    add_bolt_component(
        fastener_group,
        f"A{index}_UPPER_M6x50_PART_THREAD_PIVOT",
        first,
        second,
        6.0,
        5.0,
        4.0,
        (10.0, 10.0, 5.0),
    )
    # Place the washers against the modeled 18 mm actuator eye and 9 mm PHS ring.
    for washer_index, offset in enumerate((-9.75, 19.75), start=1):
        washer_center = add(bolt_center, scale(tangent, offset))
        add_component(
            fastener_group,
            f"A{index}_UPPER_M6_WASHER_{washer_index}",
            ring(washer_center, tangent, 6.25, 3.2, 1.5),
            "FASTENER",
        )

    shim_center = add(bolt_center, scale(tangent, 9.5))
    add_component(
        fastener_group,
        f"A{index}_UPPER_ID6_SHIM_1MM_PROVISIONAL",
        ring(shim_center, tangent, 6.25, 3.2, 1.0),
        "FASTENER",
    )

    add_bolt_component(
        fastener_group,
        f"A{index}_TB306_M6x20",
        (sx, sy, 273.2),
        (sx, sy, 258.0),
        6.0,
        7.5,
        3.5,
        thread_start=(sx, sy, 265.1),
        thread_core_diameter=4.8,
    )


def add_mechanical_stops(stop_group, fastener_group):
    rod_y = 330.0 - P.stop_rod_offset_from_crossbar_mm
    stop_positions = (
        (0.0, 330.0, rod_y),
        (-240.0, -330.0, -rod_y),
        (240.0, -330.0, -rod_y),
    )
    for index, (x, crossbar_y, rod_y) in enumerate(stop_positions, start=1):
        direction = 1.0 if crossbar_y > 0.0 else -1.0
        catch_y = direction * 287.5
        anchor_width_y = 85.0
        anchor_y = direction * (350.0 - anchor_width_y / 2.0)
        catch = box(
            (x, catch_y, P.stop_catch_center_z_mm), 90.0, 125.0, 8.0
        )
        catch = cut(
            catch,
            cylinder(
                (x, rod_y, P.stop_catch_center_z_mm - 6.0),
                (x, rod_y, P.stop_catch_center_z_mm + 6.0),
                P.stop_opening_radius_mm,
            ),
            f"stop {index} opening",
        )
        for hx in (x - 32.0, x + 32.0):
            catch = cut(
                catch,
                cylinder(
                    (hx, crossbar_y, P.stop_catch_center_z_mm - 6.0),
                    (hx, crossbar_y, P.stop_catch_center_z_mm + 6.0),
                    4.5,
                ),
                f"stop {index} lower mount",
            )
        add_component(stop_group, f"STOP_{index}_LOWER_CATCH_90x125x8_D50", catch, "STOP")
        add_component(
            stop_group,
            f"STOP_{index}_2x_M8x28_STANDOFF",
            [
                ring((hx, crossbar_y, 54.0), (0.0, 0.0, 1.0), 8.0, 4.2, 28.0)
                for hx in (x - 32.0, x + 32.0)
            ],
            "BRACKET",
        )

        anchor = box((x, anchor_y, 267.0), 80.0, anchor_width_y, 6.0)
        anchor = cut(
            anchor,
            cylinder((x, rod_y, 260.0), (x, rod_y, 272.0), 5.25),
            f"stop {index} anchor rod",
        )
        for hx in (x - 25.0, x + 25.0):
            anchor = cut(
                anchor,
                cylinder((hx, crossbar_y, 260.0), (hx, crossbar_y, 272.0), 3.4),
                f"stop {index} upper mount",
            )
        add_component(stop_group, f"STOP_{index}_UPPER_UNDERSLOT_ANCHOR_80x85x6", anchor, "STOP")
        add_component(
            stop_group,
            f"STOP_{index}_M10_ROD",
            cylinder((x, rod_y, 0.0), (x, rod_y, 270.0), 5.0),
            "STOP",
        )
        contact_bars = []
        for z_center in (
            P.stop_upper_washer_center_z_mm,
            P.stop_lower_washer_center_z_mm,
        ):
            contact_bar = box(
                (x, rod_y, z_center),
                P.stop_contact_bar_length_mm,
                P.stop_contact_bar_width_mm,
                4.0,
            )
            contact_bar = cut(
                contact_bar,
                cylinder(
                    (x, rod_y, z_center - 3.0),
                    (x, rod_y, z_center + 3.0),
                    5.25,
                ),
                f"stop {index} contact bar bore",
            )
            contact_bars.append(contact_bar)
        add_component(
            stop_group,
            f"STOP_{index}_2x_CONTACT_BAR_70x20x4",
            contact_bars,
            "STOP",
        )
        contact_bar_nuts = []
        for nut_number, z_center in enumerate((7.0, 21.0, 73.0, 87.0), start=1):
            nut = box((x, rod_y, z_center), 17.0, 17.0, 8.0)
            nut = cut(
                nut,
                cylinder((x, rod_y, z_center - 5.0), (x, rod_y, z_center + 5.0), 5.1),
                f"stop {index} contact nut bore {nut_number}",
            )
            contact_bar_nuts.append(nut)
        add_component(
            stop_group,
            f"STOP_{index}_4x_M10_CONTACT_BAR_JAM_NUTS",
            contact_bar_nuts,
            "FASTENER",
        )
        anchor_nuts = []
        for nut_number, z_center in enumerate((256.0, 274.0), start=1):
            nut = box((x, rod_y, z_center), 17.0, 17.0, 8.0)
            nut = cut(
                nut,
                cylinder((x, rod_y, z_center - 5.0), (x, rod_y, z_center + 5.0), 5.1),
                f"stop {index} anchor nut bore {nut_number}",
            )
            anchor_nuts.append(nut)
        add_component(
            stop_group,
            f"STOP_{index}_M10_ANCHOR_NUTS",
            anchor_nuts,
            "FASTENER",
        )
        for hole_index, hx in enumerate((x - 32.0, x + 32.0), start=1):
            add_bolt_component(
                fastener_group,
                f"STOP_{index}_LOWER_M8_{hole_index}",
                (hx, crossbar_y, 76.0),
                (hx, crossbar_y, 35.5),
                8.0,
                7.0,
                4.0,
                (18.0, 10.0, 5.0),
            )
        for hole_index, hx in enumerate((x - 25.0, x + 25.0), start=1):
            add_bolt_component(
                fastener_group,
                f"STOP_{index}_UPPER_M6_{hole_index}",
                (hx, crossbar_y, 263.0),
                (hx, crossbar_y, 272.9),
                6.0,
                5.0,
                3.0,
                (15.0, 10.0, 4.0),
            )


def annulus(start, end, outer_radius, inner_radius, label):
    body = cylinder(start, end, outer_radius)
    direction = unit(sub(end, start))
    return cut(
        body,
        cylinder(
            add(start, scale(direction, -1.0)),
            add(end, scale(direction, 1.0)),
            inner_radius,
        ),
        label + " bore",
    )


def axis_point(origin, axis, distance):
    return add(origin, scale(axis, distance))


def oriented_thin_nut(center, axis, tangent, across_flats=17.0, thickness=5.0):
    width_direction = unit(cross(axis, tangent))
    body = box(
        center,
        across_flats,
        across_flats,
        thickness,
        tangent,
        width_direction,
    )
    return cut(
        body,
        cylinder(
            axis_point(center, axis, -thickness),
            axis_point(center, axis, thickness),
            5.1,
        ),
        "M10 thin-nut clearance",
    )


def add_ball_lock_pin(parent, name, center, tangent):
    start = add(center, scale(tangent, -P.coarse_pin_grip_mm / 2.0))
    end = add(center, scale(tangent, P.coarse_pin_grip_mm / 2.0))
    shaft = cylinder(start, end, P.coarse_pin_diameter_mm / 2.0)
    head_end = add(start, scale(tangent, -8.0))
    head = cylinder(head_end, start, 5.5)
    pull_ring_center = add(head_end, scale(tangent, -4.0))
    pull_ring = ring(pull_ring_center, tangent, 14.0, 10.0, 3.0)
    return add_component(parent, name, [shaft, head, pull_ring], "FASTENER")


def add_manual_lower_mount(adapter_group, lower_joint_group, fastener_group, row):
    cx, cy = row["center_mm"]
    radial = row["radial"]
    tangent = row["tangent"]

    adapter = box(
        (cx, cy, 44.0),
        P.adapter_length_x_mm,
        P.adapter_width_y_mm,
        P.adapter_thickness_mm,
    )
    for hole_index, (hx, hy) in enumerate(row["profile_mount_holes_mm"], start=1):
        adapter = cut(
            adapter,
            cylinder((hx, hy, 38.0), (hx, hy, 50.0), 4.5),
            row["id"] + f" adapter profile hole {hole_index}",
        )
    for hole_index, (hx, hy) in enumerate(row["clevis_mount_holes_mm"], start=1):
        adapter = cut(
            adapter,
            cylinder((hx, hy, 38.0), (hx, hy, 50.0), 3.4),
            row["id"] + f" adapter M8 tapped core {hole_index}",
        )
    add_component(
        adapter_group,
        row["id"] + "_LOWER_ADAPTER_A6061_120x80x8",
        adapter,
        "ADAPTER",
    )

    for hole_index, (hx, hy) in enumerate(row["profile_mount_holes_mm"], start=1):
        add_bolt_component(
            fastener_group,
            row["id"] + f"_ADAPTER_TO_PROFILE_M8x20_{hole_index}",
            (hx, hy, 52.0),
            (hx, hy, 35.5),
            8.0,
            7.0,
            4.0,
            (18.0, 10.0, 5.0),
        )

    base = box(
        (cx, cy, 52.0),
        P.lower_clevis_base_length_mm,
        P.lower_clevis_base_width_mm,
        P.lower_clevis_base_thickness_mm,
        radial,
        tangent,
    )
    for hole_index, (hx, hy) in enumerate(row["clevis_mount_holes_mm"], start=1):
        base = cut(
            base,
            cylinder((hx, hy, 46.0), (hx, hy, 62.0), 4.3),
            row["id"] + f" lower clevis base clearance {hole_index}",
        )
    clevis = base
    ear_offset = P.lower_clevis_gap_mm / 2.0 + P.lower_clevis_ear_thickness_mm / 2.0
    for sign in (-1.0, 1.0):
        ear_center = (
            cx + tangent[0] * sign * ear_offset,
            cy + tangent[1] * sign * ear_offset,
            81.5,
        )
        ear = box(
            ear_center,
            50.0,
            P.lower_clevis_ear_thickness_mm,
            53.0,
            radial,
            tangent,
        )
        clevis = union(clevis, ear, row["id"] + " lower clevis one-piece union")
    clevis = cut(
        clevis,
        cylinder(
            add((cx, cy, P.lower_pin_z_mm), scale(tangent, -30.0)),
            add((cx, cy, P.lower_pin_z_mm), scale(tangent, 30.0)),
            4.1,
        ),
        row["id"] + " lower M8 pivot bore",
    )
    add_component(
        lower_joint_group,
        row["id"] + "_LOWER_ONE_PIECE_CLEVIS_A6061",
        clevis,
        "BRACKET",
    )

    for hole_index, (hx, hy) in enumerate(row["clevis_mount_holes_mm"], start=1):
        add_bolt_component(
            fastener_group,
            row["id"] + f"_CLEVIS_TO_ADAPTER_M8x16_{hole_index}",
            (hx, hy, 60.0),
            (hx, hy, 47.0),
            8.0,
            7.0,
            4.0,
            thread_start=(hx, hy, 48.0),
            thread_core_diameter=6.6,
        )


def add_manual_upper_clevis(upper_joint_group, fastener_group, index, upper, tangent, radial):
    ux, uy, uz = upper
    base = box(
        (ux, uy, 266.0),
        P.upper_clevis_base_length_mm,
        P.upper_clevis_base_width_mm,
        P.upper_clevis_base_thickness_mm,
    )
    mount_holes = ((ux - 42.0, uy), (ux + 42.0, uy))
    for hole_index, (hx, hy) in enumerate(mount_holes, start=1):
        base = cut(
            base,
            cylinder((hx, hy, 258.0), (hx, hy, 274.0), 3.3),
            f"A{index} upper clevis M6 clearance {hole_index}",
        )
    clevis = base
    ear_offset = P.upper_clevis_gap_mm / 2.0 + P.upper_clevis_ear_thickness_mm / 2.0
    for sign in (-1.0, 1.0):
        ear_center = (
            ux + tangent[0] * sign * ear_offset,
            uy + tangent[1] * sign * ear_offset,
            244.5,
        )
        ear = box(
            ear_center,
            50.0,
            P.upper_clevis_ear_thickness_mm,
            37.0,
            radial,
            tangent,
        )
        clevis = union(clevis, ear, f"A{index} upper clevis one-piece union")
    clevis = cut(
        clevis,
        cylinder(
            add(upper, scale(tangent, -20.0)),
            add(upper, scale(tangent, 20.0)),
            5.1,
        ),
        f"A{index} upper M10 pivot bore",
    )
    add_component(
        upper_joint_group,
        f"A{index}_UPPER_ONE_PIECE_CLEVIS_A6061",
        clevis,
        "BRACKET",
    )
    for hole_index, (hx, hy) in enumerate(mount_holes, start=1):
        add_bolt_component(
            fastener_group,
            f"A{index}_UPPER_CLEVIS_TO_PROFILE_M6x15_{hole_index}",
            (hx, hy, 262.0),
            (hx, hy, 272.5),
            6.0,
            5.0,
            4.0,
            (15.0, 10.0, 4.0),
        )


def add_manual_strut(strut_group, joint_group, fastener_group, index, lower, upper, tangent):
    axis = unit(sub(upper, lower))
    radial = unit((axis[0], axis[1], 0.0))
    pin_length = math.sqrt(sum((upper[value] - lower[value]) ** 2 for value in range(3)))
    neutral_setting = m1_data.setting_for_length(pin_length)
    coarse_mm = neutral_setting["coarse_mm"]
    inner_start_s = P.inner_tube_s_start_zero_mm + coarse_mm
    inner_end_s = inner_start_s + P.inner_tube_length_mm
    outer_end_s = P.outer_tube_s_start_mm + P.outer_tube_length_mm

    outer = annulus(
        axis_point(lower, axis, P.outer_tube_s_start_mm),
        axis_point(lower, axis, outer_end_s),
        P.outer_tube_od_mm / 2.0,
        (P.outer_tube_od_mm - 2.0 * P.outer_tube_wall_mm) / 2.0,
        f"A{index} outer tube",
    )
    for s_value, label, bore_radius in (
        (0.0, "lower pivot", 4.1),
        (P.coarse_pin_s_mm, "coarse pin", P.coarse_hole_diameter_max_mm / 2.0),
    ):
        center = axis_point(lower, axis, s_value)
        outer = cut(
            outer,
            cylinder(
                add(center, scale(tangent, -25.0)),
                add(center, scale(tangent, 25.0)),
                bore_radius,
            ),
            f"A{index} outer tube {label} bore",
        )
    add_component(
        strut_group,
        f"A{index}_OUTER_TUBE_OD32x2_L160_REAM28H7",
        outer,
        "ACTUATOR",
    )

    inner = annulus(
        axis_point(lower, axis, inner_start_s),
        axis_point(lower, axis, inner_end_s),
        P.inner_tube_od_mm / 2.0,
        (P.inner_tube_od_mm - 2.0 * P.inner_tube_wall_mm) / 2.0,
        f"A{index} inner tube",
    )
    for hole_index, offset in enumerate((107.0, 92.0, 77.0, 62.0, 47.0, 32.0), start=1):
        center = axis_point(lower, axis, inner_start_s + offset)
        inner = cut(
            inner,
            cylinder(
                add(center, scale(tangent, -20.0)),
                add(center, scale(tangent, 20.0)),
                P.coarse_hole_diameter_max_mm / 2.0,
            ),
            f"A{index} inner coarse hole {hole_index}",
        )
    retainer_s = inner_end_s - P.threaded_plug_retainer_offset_mm
    retainer_center = axis_point(lower, axis, retainer_s)
    inner = cut(
        inner,
        cylinder(
            add(retainer_center, scale(tangent, -18.0)),
            add(retainer_center, scale(tangent, 18.0)),
            2.1,
        ),
        f"A{index} plug retainer bore",
    )
    add_component(
        strut_group,
        f"A{index}_INNER_TUBE_OD25x2_L150_6POS",
        inner,
        "ROD",
    )

    bushing_start_s = outer_end_s - P.bushing_length_mm
    bushing_main = annulus(
        axis_point(lower, axis, bushing_start_s),
        axis_point(lower, axis, outer_end_s),
        P.bushing_od_mm / 2.0,
        P.bushing_id_mm / 2.0,
        f"A{index} JFM bushing",
    )
    bushing_flange = annulus(
        axis_point(lower, axis, outer_end_s),
        axis_point(lower, axis, outer_end_s + P.bushing_flange_thickness_mm),
        P.bushing_flange_od_mm / 2.0,
        P.bushing_id_mm / 2.0,
        f"A{index} JFM flange",
    )
    add_component(
        strut_group,
        f"A{index}_IGUS_JFM_2528_21",
        [bushing_main, bushing_flange],
        "BUSHING",
    )

    guide = annulus(
        axis_point(lower, axis, inner_start_s),
        axis_point(lower, axis, inner_start_s + P.guide_ring_length_mm),
        P.guide_ring_od_mm / 2.0,
        P.guide_ring_id_mm / 2.0,
        f"A{index} POM guide",
    )
    add_component(strut_group, f"A{index}_POM_LOWER_GUIDE_RING", guide, "POM")

    plug_start_s = inner_end_s - P.threaded_plug_length_mm
    plug = cylinder(
        axis_point(lower, axis, plug_start_s),
        axis_point(lower, axis, inner_end_s),
        P.threaded_plug_od_mm / 2.0,
    )
    plug = cut(
        plug,
        cylinder(
            axis_point(lower, axis, inner_end_s - 22.0),
            axis_point(lower, axis, inner_end_s + 1.0),
            5.1,
        ),
        f"A{index} plug M10 thread representation",
    )
    plug = cut(
        plug,
        cylinder(
            add(retainer_center, scale(tangent, -18.0)),
            add(retainer_center, scale(tangent, 18.0)),
            2.1,
        ),
        f"A{index} plug retainer clearance",
    )
    add_component(strut_group, f"A{index}_A6061_M10_THREADED_PLUG", plug, "ADAPTER")

    stud_start_s = inner_end_s - P.fine_stud_bottom_engagement_mm
    stud_end_s = inner_end_s + P.fine_stud_projection_mm
    add_component(
        strut_group,
        f"A{index}_M10x1p5_FINE_STUD_L53",
        cylinder(axis_point(lower, axis, stud_start_s), axis_point(lower, axis, stud_end_s), 5.0),
        "STUD",
    )
    lower_nut_center = axis_point(lower, axis, inner_end_s + 2.5)
    thread_end = axis_point(upper, axis, -P.phs_center_to_thread_end_mm)
    upper_nut_center = axis_point(thread_end, axis, -2.5)
    add_component(
        fastener_group,
        f"A{index}_2x_M10_DIN439_THIN_JAM_NUTS",
        [
            oriented_thin_nut(lower_nut_center, axis, tangent),
            oriented_thin_nut(upper_nut_center, axis, tangent),
        ],
        "FASTENER",
    )

    phs_ring = ring(upper, tangent, P.phs_outer_diameter_mm / 2.0, P.phs_bore_mm / 2.0, P.phs_ring_width_mm)
    stem_end = axis_point(upper, axis, -12.0)
    phs = cylinder(thread_end, stem_end, 8.5)
    phs = union(phs, phs_ring, f"A{index} PHS10 holder and ring")
    phs = cut(
        phs,
        cylinder(axis_point(thread_end, axis, -1.0), axis_point(thread_end, axis, 22.0), 5.1),
        f"A{index} PHS10 female thread representation",
    )
    add_component(joint_group, f"A{index}_THK_PHS10_RH", phs, "JOINT")

    for shim_index, tangent_offset in enumerate((-8.5, 8.5), start=1):
        shim_center = add(upper, scale(tangent, tangent_offset))
        add_component(
            fastener_group,
            f"A{index}_UPPER_ID10_OD18_SHIM_3MM_{shim_index}",
            ring(shim_center, tangent, 9.0, 5.1, P.upper_side_shim_thickness_mm),
            "FASTENER",
        )

    add_bolt_component(
        fastener_group,
        f"A{index}_UPPER_M10_SHOULDER_BOLT_GRIP32",
        add(upper, scale(tangent, -16.0)),
        add(upper, scale(tangent, 16.0)),
        9.98,
        8.0,
        5.0,
        (17.0, 17.0, 8.0),
    )
    add_bolt_component(
        fastener_group,
        f"A{index}_LOWER_M8_SHOULDER_BOLT_GRIP46",
        add(lower, scale(tangent, -23.0)),
        add(lower, scale(tangent, 23.0)),
        7.98,
        7.0,
        5.0,
        (13.0, 13.0, 6.5),
    )
    coarse_center = axis_point(lower, axis, P.coarse_pin_s_mm)
    add_ball_lock_pin(
        fastener_group,
        f"A{index}_IMAO_BJ775_08040_SUS_COARSE_PIN",
        coarse_center,
        tangent,
    )
    add_bolt_component(
        fastener_group,
        f"A{index}_PLUG_RETAINER_M4_GRIP32",
        add(retainer_center, scale(tangent, -16.0)),
        add(retainer_center, scale(tangent, 16.0)),
        3.98,
        3.5,
        3.0,
        (7.0, 7.0, 4.0),
    )


def add_parameters():
    values = {
        "outerLength": (P.outer_length_mm, "mm", "Overall profile frame length"),
        "lowerSupportRadius": (P.lower_support_radius_mm, "mm", "Lower R-joint support radius"),
        "upperSupportRadius": (P.upper_support_radius_mm, "mm", "Upper spherical-joint support radius"),
        "liftTarget": (P.lift_mm, "mm", "Common Z lift target"),
        "pitchRollTarget": (P.angle_deg, "deg", "Pitch and roll target"),
        "adapterLength": (P.adapter_length_x_mm, "mm", "Local lower adapter length"),
        "adapterWidth": (P.adapter_width_y_mm, "mm", "Local lower adapter width"),
        "adapterThickness": (P.adapter_thickness_mm, "mm", "Local lower adapter thickness"),
        "outerTubeOD": (P.outer_tube_od_mm, "mm", "Manual strut outer tube OD"),
        "innerTubeOD": (P.inner_tube_od_mm, "mm", "Manual strut inner tube OD"),
        "coarsePitch": (P.coarse_pitch_mm, "mm", "Manual coarse-hole pitch"),
        "manualMinPin": (m1_data.manual_pin_range_mm()[0], "mm", "Minimum pin-centre length"),
        "manualMaxPin": (m1_data.manual_pin_range_mm()[1], "mm", "Maximum pin-centre length"),
    }
    for name, (value, units, comment) in values.items():
        ROOT.attributes.add(
            "REV_M1_PARAMETER",
            name,
            f"{value} {units} | {comment}",
        )


def create_assembly():
    global GROUP_COMPONENTS
    lower_frame = create_group("01_LOWER_4040_FRAME")
    lower_brackets = create_group("02_LOWER_4035_BRACKETS")
    adapters = create_group("03_LOWER_LOCAL_ADAPTERS")
    lower_joints = create_group("04_LOWER_ONE_PIECE_CLEVISES")
    struts = create_group("05_THREE_MANUAL_TELESCOPIC_STRUTS")
    upper_frame = create_group("06_UPPER_3030_FRAME")
    upper_brackets = create_group("07_UPPER_DCB3025_BRACKETS")
    upper_joints = create_group("08_UPPER_CLEVISES_AND_PHS10")
    fasteners = create_group("09_ALL_POSITIONED_FASTENERS")

    add_profile(lower_frame, "LOWER_SIDE_L_DNF4040_700", "Y", (-330.0, 0.0, 20.0), 700.0, 40.0)
    add_profile(lower_frame, "LOWER_SIDE_R_DNF4040_700", "Y", (330.0, 0.0, 20.0), 700.0, 40.0)
    lower_names = ("FRONT", "A1", "A23", "REAR")
    for name, y in zip(lower_names, LOWER_CROSSBAR_Y_MM):
        add_profile(lower_frame, f"LOWER_CROSS_{name}_DNF4040_620", "X", (0.0, y, 20.0), 620.0, 40.0)
    add_frame_connectors(lower_brackets, fasteners, LOWER_CROSSBAR_Y_MM, 310.0, upper=False)

    rows = adapter_rows()
    for row in rows:
        add_manual_lower_mount(adapters, lower_joints, fasteners, row)

    add_profile(upper_frame, "UPPER_SIDE_L_DNF3030_700", "Y", (-335.0, 0.0, 285.0), 700.0, 30.0)
    add_profile(upper_frame, "UPPER_SIDE_R_DNF3030_700", "Y", (335.0, 0.0, 285.0), 700.0, 30.0)
    upper_names = ("FRONT", "A1", "A23", "REAR")
    for name, y in zip(upper_names, UPPER_CROSSBAR_Y_MM):
        add_profile(upper_frame, f"UPPER_CROSS_{name}_DNF3030_640", "X", (0.0, y, 285.0), 640.0, 30.0)
    add_frame_connectors(upper_brackets, fasteners, UPPER_CROSSBAR_Y_MM, 320.0, upper=True)

    lower_eyes = lower_eye_points()
    upper_eyes = tuple(
        (point_value[0], point_value[1], P.upper_ring_z_collapsed_mm)
        for point_value in upper_eye_local_points()
    )
    for index, (lower, upper, basis, support) in enumerate(
        zip(lower_eyes, upper_eyes, support_basis(), upper_support_points()), start=1
    ):
        radial, tangent = basis
        add_manual_upper_clevis(
            upper_joints, fasteners, index, upper, tangent, radial
        )
        add_manual_strut(
            struts, upper_joints, fasteners, index, lower, upper, tangent
        )

    GROUP_COMPONENTS = {
        "lower_frame": lower_frame,
        "lower_brackets": lower_brackets,
        "lower_adapters": adapters,
        "manual_struts": struts,
        "upper_frame": upper_frame,
        "upper_brackets": upper_brackets,
        "lower_joints": lower_joints,
        "upper_joints": upper_joints,
        "fasteners": fasteners,
    }


def save_camera_image(path_value, eye_mm, target_mm, up_direction):
    viewport = APP.activeViewport
    camera = viewport.camera
    camera.isSmoothTransition = False
    camera.eye = point(eye_mm)
    camera.target = point(target_mm)
    camera.upVector = vector(up_direction)
    viewport.camera = camera
    adsk.doEvents()
    time.sleep(0.35)
    viewport.fit()
    adsk.doEvents()
    time.sleep(0.35)
    viewport.fit()
    adsk.doEvents()
    if not viewport.saveAsImageFile(path_value, 1800, 1200):
        raise RuntimeError("Fusion viewport image export failed: " + path_value)


def set_a1_detail_visibility(enabled):
    if not enabled:
        for top_occurrence in ROOT.occurrences:
            top_occurrence.isLightBulbOn = True
            for child_occurrence in top_occurrence.component.occurrences:
                child_occurrence.isLightBulbOn = True
        return

    visible_children = {
        "01_LOWER_4040_FRAME": lambda name: name.startswith("LOWER_CROSS_A1_"),
        "03_LOWER_LOCAL_ADAPTERS": lambda name: name.startswith("A1_"),
        "04_LOWER_ONE_PIECE_CLEVISES": lambda name: name.startswith("A1_"),
        "05_THREE_MANUAL_TELESCOPIC_STRUTS": lambda name: name.startswith("A1_"),
        "06_UPPER_3030_FRAME": lambda name: name.startswith("UPPER_CROSS_A1_"),
        "08_UPPER_CLEVISES_AND_PHS10": lambda name: name.startswith("A1_"),
        "09_ALL_POSITIONED_FASTENERS": lambda name: name.startswith("A1_"),
    }
    for top_occurrence in ROOT.occurrences:
        group_name = top_occurrence.component.name
        predicate = visible_children.get(group_name)
        top_occurrence.isLightBulbOn = predicate is not None
        if predicate is not None:
            for child_occurrence in top_occurrence.component.occurrences:
                child_occurrence.isLightBulbOn = predicate(child_occurrence.component.name)


def interference_entity_name(entity):
    try:
        if entity.component:
            return entity.component.name
    except Exception:
        pass
    try:
        return entity.name
    except Exception:
        return str(entity)


def run_fusion_interference_checks(pass_count=3):
    entities = adsk.core.ObjectCollection.create()
    for occurrence in ROOT.allOccurrences:
        if occurrence.component.bRepBodies.count > 0:
            entities.add(occurrence)
    passes = []
    for pass_index in range(1, pass_count + 1):
        interference_input = DESIGN.createInterferenceInput(entities)
        interference_input.areCoincidentFacesIncluded = False
        results = DESIGN.analyzeInterference(interference_input)
        rows = []
        for result_index in range(results.count):
            result = results.item(result_index)
            volume_mm3 = None
            try:
                volume_mm3 = result.interferenceBody.volume * 1000.0
            except Exception:
                pass
            rows.append(
                {
                    "entity_one": interference_entity_name(result.entityOne),
                    "entity_two": interference_entity_name(result.entityTwo),
                    "volume_mm3": volume_mm3,
                }
            )
        signature = tuple(
            sorted(
                (
                    row["entity_one"],
                    row["entity_two"],
                    None if row["volume_mm3"] is None else round(row["volume_mm3"], 6),
                )
                for row in rows
            )
        )
        passes.append(
            {
                "pass": pass_index,
                "checked_leaf_occurrences": entities.count,
                "interference_count": results.count,
                "signature": signature,
                "rows": rows,
                "passes": results.count == 0,
            }
        )
    report = {
        "method": "Fusion Design.analyzeInterference; coincident faces excluded",
        "pass_count": pass_count,
        "repeatable": all(row["signature"] == passes[0]["signature"] for row in passes),
        "all_zero": all(row["passes"] for row in passes),
        "passes": passes,
    }
    with open(INTERFERENCE_PATH, "w", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    return report


def save_section_checks():
    paths = []
    section_analyses = DESIGN.analyses.sectionAnalyses
    for pass_index, offset_mm in enumerate((0.0, 3.0, -3.0), start=1):
        section_input = section_analyses.createInput(ROOT.yZConstructionPlane, mm(offset_mm))
        analysis = section_analyses.add(section_input)
        analysis.name = f"REV_M1_A1_SECTION_PASS_{pass_index}_X_{offset_mm:+.1f}mm"
        analysis.isHatchShown = True
        analysis.isLightBulbOn = True
        path_value = os.path.join(
            OUTPUT_DIR, f"Manual_3RPS_RevM1_A1_SECTION_PASS_{pass_index}.png"
        )
        save_camera_image(
            path_value,
            (500.0, 165.0, 190.0),
            (0.0, 165.0, 165.0),
            (0.0, 0.0, 1.0),
        )
        paths.append({"pass": pass_index, "x_offset_mm": offset_mm, "image": path_value})
        analysis.isLightBulbOn = False
        try:
            analysis.deleteMe()
        except Exception:
            pass
    return paths


def export_results():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(GROUP_STEP_DIR, exist_ok=True)
    audit = full_audit()
    audit["fusion_native_component_count"] = len(COMPONENT_NAMES)
    audit["fusion_component_names"] = tuple(COMPONENT_NAMES)
    audit["fusion_document_name"] = APP.activeDocument.name
    audit["fusion_f3d_path"] = F3D_PATH
    audit["fusion_step_path"] = STEP_PATH
    audit["manual_strut_basis"] = (
        "OD32x2 outer and OD25x2 inner aluminium tubes; neutral coarse position "
        "15 mm; JFM-2528-21 guide; PHS10 upper rod end"
    )
    audit["manual_positive_limits"] = (
        "Six discrete coarse holes plus PHS10 thread engagement marks; adjustment "
        "only while the upper frame is independently supported"
    )
    interference = run_fusion_interference_checks(3)
    audit["fusion_interference_checks"] = interference
    audit["digital_layout_passes"] = audit["digital_layout_passes"] and interference["all_zero"]
    with open(VALIDATION_PATH, "w", encoding="utf-8") as stream:
        json.dump(audit, stream, ensure_ascii=False, indent=2)
        stream.write("\n")

    manager = DESIGN.exportManager
    archive_options = manager.createFusionArchiveExportOptions(F3D_PATH, ROOT)
    if not manager.execute(archive_options):
        raise RuntimeError("Fusion archive export failed")
    step_options = manager.createSTEPExportOptions(STEP_PATH, ROOT)
    if not manager.execute(step_options):
        raise RuntimeError("STEP export failed")

    group_paths = {}
    for name, component in GROUP_COMPONENTS.items():
        path_value = os.path.join(GROUP_STEP_DIR, name + ".step")
        options = manager.createSTEPExportOptions(path_value, component)
        if not manager.execute(options):
            raise RuntimeError("Group STEP export failed: " + name)
        group_paths[name] = path_value
    audit["fusion_group_step_paths"] = group_paths
    with open(VALIDATION_PATH, "w", encoding="utf-8") as stream:
        json.dump(audit, stream, ensure_ascii=False, indent=2)
        stream.write("\n")

    target = (0.0, 0.0, 150.0)
    save_camera_image(IMAGE_PATH, (900.0, -1100.0, 750.0), target, (0.0, 0.0, 1.0))
    save_camera_image(IMAGE_TOP_PATH, (0.0, 0.0, 1200.0), target, (0.0, 1.0, 0.0))
    save_camera_image(IMAGE_SIDE_PATH, (1200.0, 0.0, 150.0), target, (0.0, 0.0, 1.0))
    set_a1_detail_visibility(True)
    save_camera_image(
        IMAGE_A1_DETAIL_PATH,
        (520.0, -260.0, 380.0),
        (0.0, 165.0, 155.0),
        (0.0, 0.0, 1.0),
    )
    audit["fusion_section_checks"] = save_section_checks()
    set_a1_detail_visibility(False)
    save_camera_image(IMAGE_PATH, (900.0, -1100.0, 750.0), target, (0.0, 0.0, 1.0))
    with open(VALIDATION_PATH, "w", encoding="utf-8") as stream:
        json.dump(audit, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    if os.path.exists(ERROR_PATH):
        os.remove(ERROR_PATH)


def run(context):
    global APP, DESIGN, ROOT, TBM
    ui = None
    try:
        APP = adsk.core.Application.get()
        ui = APP.userInterface
        document = APP.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        document.name = "Manual_3RPS_RevM1_NATIVE"
        DESIGN = adsk.fusion.Design.cast(APP.activeProduct)
        DESIGN.designType = adsk.fusion.DesignTypes.DirectDesignType
        ROOT = DESIGN.rootComponent
        TBM = adsk.fusion.TemporaryBRepManager.get()

        add_parameters()
        setup_appearances()
        ROOT.attributes.add("REV_M1", "STATUS", "MANUAL_DETAIL_REVIEW_NOT_FOR_ORDER")
        ROOT.attributes.add("REV_M1", "CENTRAL_HUB_PLATE_COUNT", "0")
        ROOT.attributes.add("REV_M1", "SUPPORT_AZIMUTHS_DEG", "90,210,330")
        ROOT.attributes.add("REV_M1", "POWERED_COMPONENT_COUNT", "0")
        create_assembly()
        export_results()
        ui.messageBox(
            "Manual Rev M1 native assembly created.\n\n"
            "Central hub plate: removed\n"
            "Manual telescopic struts: 3\n"
            "Fusion interference passes: 3\n"
            "Fusion section passes: 3\n"
            f"Native components: {len(COMPONENT_NAMES)}\n"
            f"F3D: {F3D_PATH}\n\n"
            "Status: detailed review, not released for order."
        )
    except Exception:
        message = "Manual3RPSRevM1 failed:\n" + traceback.format_exc()
        if ui:
            ui.messageBox(message)
        try:
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            with open(ERROR_PATH, "w", encoding="utf-8") as stream:
                stream.write(message)
        except Exception:
            pass
