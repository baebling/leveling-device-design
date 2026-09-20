"""One-axis assembly study for M2R2F2.

The complete A1 assembly is extracted from the verified M2R2F1 model.
The exploded lower/upper joint models use catalogue interface dimensions.
Cosmetic blends, threads and several proprietary internal details are schematic.
"""
from math import sqrt
import cadquery as cq
from cad import manual_turnbuckle_rev_m2 as base
from cad import manual_turnbuckle_rev_m2r1 as m2r1
from cad import manual_turnbuckle_rev_m2r2f1 as m

C = base.Component
SILVER, BLACK, BLUE = m2r1.SILVER, m2r1.STEEL, m2r1.BLUE
ORANGE = (0.82, 0.42, 0.08)
LOWER_CENTER = cq.Vector(0, 0, 63)
UPPER_CENTER = cq.Vector(0, 175, 281)
LINK_UNIT = (UPPER_CENTER - LOWER_CENTER).normalized()


def part(name, group, shape, color=SILVER, material="catalogue interface envelope"):
    return C(name, group, shape, color, material)


def _locate_a1(shape, center):
    """Rotate local SHAT shaft-Y model to A1 shaft-X, then translate."""
    return shape.rotate((0, 0, 0), (0, 0, 1), -90).translate(center.toTuple())


def profile_segment(upper=False):
    shape = m.profile(180, 80).rotate((0, 0, 0), (0, 0, 1), 90)
    if upper:
        shape = shape.translate((0, 175, 304))  # profile spans z=304..344; joint foot touches underside
    return part("UPPER_HFS8_4080" if upper else "LOWER_HFS8_4080", "profile", shape,
                SILVER, "HFS8-4080 cut segment; joint interface section exact, internal cavity simplified")


def bj761_eye():
    """BJ761-12011N: d12(+0.2/0), W14(0/-0.2), D25, H50, thread L30."""
    axis = cq.Vector(1, 0, 0)
    ring = base._ring(LOWER_CENTER.toTuple(), axis.toTuple(), 25, 12, 14, LINK_UNIT.toTuple())
    stem = base._cylinder_between(LOWER_CENTER + LINK_UNIT.multiply(9),
                                  LOWER_CENTER + LINK_UNIT.multiply(22), 6)
    thread = base._cylinder_between(LOWER_CENTER + LINK_UNIT.multiply(20),
                                    LOWER_CENTER + LINK_UNIT.multiply(50), 6)
    return part("BJ761_12011N", "joint_member", cq.Compound.makeCompound([ring, stem, thread]),
                ORANGE, "IMAO BJ761-12011N; thread helix and eye blend schematic")


def phs12l_parts():
    """THK PHS12L holder and spherical inner ring as separate components."""
    c = UPPER_CENTER
    axis = cq.Vector(1, 0, 0)
    # Holder: D30, axial width B12; neck/hex follows D1=17.5, D2=22, W=19.
    holder_ring = base._ring(c.toTuple(), axis.toTuple(), 30, 22.275, 12, (-LINK_UNIT).toTuple())
    neck_start = c - LINK_UNIT.multiply(13)
    neck_end = c - LINK_UNIT.multiply(44)
    neck = base._cylinder_between(neck_start, neck_end, 17.5 / 2)
    hex_end = c - LINK_UNIT.multiply(50)
    hex_body = base._hex_prism_between(neck_end, hex_end, 22)
    holder = cq.Compound.makeCompound([holder_ring, neck, hex_body])

    rad, half = 22.225 / 2, 16 / 2
    edge = sqrt(rad * rad - half * half)
    ball_local = (cq.Workplane("XY").moveTo(6, -half).lineTo(edge, -half)
                  .threePointArc((rad, 0), (edge, half)).lineTo(6, half)
                  .close().revolve(360, (0, 0, 0), (0, 1, 0)).val())
    # local revolution axis Y -> global X
    ball = ball_local.rotate((0, 0, 0), (0, 0, 1), -90).translate(c.toTuple())
    return [
        part("PHS12L_HOLDER", "joint_member", holder, ORANGE,
             "THK PHS12L; outer catalogue dimensions, grease nipple/thread helix omitted"),
        part("PHS12L_INNER_RING", "joint_member", ball, SILVER,
             "THK PHS12L; d12 H7, ball22.225, width16")]


def joint_hardware(prefix, upper=False):
    items = []
    for c in m.joint(prefix, upper):
        # Center lower at local origin; upper foot mounts below a profile whose underside is z=241.
        center = UPPER_CENTER if upper else LOWER_CENTER
        items.append(part(c.name, c.group, _locate_a1(c.shape, center), c.color, c.material))
    return items


def assembled_lower():
    return [profile_segment(False), bj761_eye()] + joint_hardware("L1", False)


def assembled_upper():
    return [profile_segment(True)] + phs12l_parts() + joint_hardware("U1", True)


def one_axis_complete():
    full = m.components_for_pose(0, 0)
    keep = []
    for c in full:
        if c.name in ("LOWER_FRONT_RAIL", "UPPER_FRONT_RAIL") or c.name.startswith(("L1_", "U1_", "A1_")):
            keep.append(c)
    return keep


def _explode(parts, prefix, upper=False):
    """Explode along shaft X and fastener Z without changing part geometry."""
    out = []
    for c in parts:
        dx = dz = 0
        sgn = -1 if c.shape.Center().x < 0 else 1
        if "SHAT12_" in c.name: dx = 45 * sgn
        elif "SHIM_STACK_" in c.name: dx = 22 * sgn
        elif "MCL12F_" in c.name: dx = 65 * sgn
        elif "SHAFT12X100" in c.name: dx = -125
        elif "PHS12L_INNER" in c.name: dx = 0
        elif c.name.startswith(prefix + "_L_M5") or c.name.startswith(prefix + "_R_M5"): dx=45*sgn; dz = 38 if not upper else -38
        elif c.name.startswith(prefix + "_L_W5") or c.name.startswith(prefix + "_R_W5"): dx=45*sgn; dz = 20 if not upper else -20
        elif "HNTT8_5" in c.name: dx=45*sgn; dz = -18 if not upper else 18
        elif "SHAT_CLAMP_HEAD_" in c.name: dx = 105 * sgn
        out.append(part(c.name, c.group, c.shape.translate((dx, 0, dz)), c.color, c.material))
    return out


def lower_exploded():
    return _explode(assembled_lower(), "L1", False)


def upper_exploded():
    return _explode(assembled_upper(), "U1", True)


DIMENSION_STATUS = {
    "confirmed_catalogue_interfaces": {
        "SHAT12_mm": {"bore": 12, "axis_height": 23, "foot_length": 42, "axis_width": 14,
                       "mount_pitch": 32, "mount_hole": 5.5, "foot_thickness": 6, "clamp_screw": "M4"},
        "HFS8_4080_mm": {"face": [40, 80], "slot_width": 10, "slot_pitch": 40,
                         "slot_lip_depth": 5.5, "slot_floor_depth": 12.5},
        "HNTT8_mm": {"plan": [17, 17], "overall_height": 9, "boss_height": 3,
                      "threads": ["M5", "M8"]},
        "BJ761_12011N_mm": {"bore": "12 +0.2/0", "width": "14 0/-0.2", "eye_od": 25,
                             "eye_center_to_tip": 50, "thread": "M12x1.75", "thread_length": 30},
        "PHS12L_mm": {"bore": "12 H7", "inner_width": 16, "holder_width": 12,
                       "holder_od": 30, "ball_od": 22.225, "thread": "M12x1.75 LH"},
        "MCL12F_mm": {"bore": "12 +0.050/+0.012", "od": 28, "width": "11 +0.076/-0.254",
                       "clamp_screw": "M4x12", "screw_location": 10.01, "tool": "3 mm hex"},
        "axis_stack_mm": {"support_inner_gap": 26, "upper": "5 + 16 + 5",
                           "lower_nominal": "5.9 + 14 + 5.9 + 0.2 clearance", "shaft_length": 100}
    },
    "schematic_or_unconfirmed": [
        "SHAT12 casting fillets, draft and proprietary clamp slit details",
        "HFS8 internal cavities away from the mounting face",
        "HNTT8 underside taper and exact thread lead-in",
        "BJ761 eye-to-stem blend and thread helix",
        "PHS12L grease nipple, copper bush/socket detail and thread helix",
        "MCL-12-F slit and clamp screw are not yet represented in the complete-axis CAD",
        "actual delivered widths and the final DIN988 shim combination",
        "supplier-approved compression, slot-lip bending, clamp holding and slip ratings"
    ]
}
