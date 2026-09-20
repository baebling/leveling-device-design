"""NAVIMRO-oriented radial-three fabrication assembly.

This is a prototype fabrication model, not a certified lifting device. It keeps
unverified vendor hole patterns out of fabricated parts by using transfer-drill
plates at the LMF12UU, SK12 and DHLA2000 interfaces.
"""

from pathlib import Path

import cadquery as cq

from .common import COLORS, Component, centered_box, compound, cylinder_between
from .navimro_fabrication_parameters import N, NAVIMRO_POSES, transform_local_point


PROFILE = (0.62, 0.66, 0.69, 1.0)
STEEL = (0.12, 0.25, 0.34, 1.0)
ACTUATOR_BODY = (0.16, 0.17, 0.19, 1.0)
ACTUATOR_ROD = (0.72, 0.77, 0.80, 1.0)
PURCHASED = (0.91, 0.65, 0.22, 1.0)
STOP = (0.82, 0.21, 0.16, 1.0)


def _box_x(length, y, z, width=40.0, height=40.0):
    return centered_box(length, width, height, (0.0, y, z))


def _box_y(length, x, z, width=40.0, height=40.0):
    return centered_box(width, length, height, (x, 0.0, z))


def _local_to_world(shape, pose, platform_z):
    result = shape.rotate((0, 0, 0), (1, 0, 0), pose.roll_deg)
    result = result.rotate((0, 0, 0), (0, 1, 0), pose.pitch_deg)
    return result.translate((0.0, 0.0, platform_z))


def _component(name, shape, color, material, category="fabricated", notes=""):
    return Component(name, shape, color, material, category=category, notes=notes)


def _slotted_foot(length=120.0, width=50.0, thickness=6.0):
    plate = centered_box(length, width, thickness)
    for x in (-35.0, 35.0):
        slot = centered_box(24.0, 11.0, thickness + 2.0, (x, 0.0, 0.0))
        slot = slot.union(cylinder_between((x - 12.0, 0.0, -5.0), (x - 12.0, 0.0, 5.0), 5.5))
        slot = slot.union(cylinder_between((x + 12.0, 0.0, -5.0), (x + 12.0, 0.0, 5.0), 5.5))
        plate = plate.cut(slot)
    return plate


def lower_structure_components():
    p = N
    z = p.lower_frame_center_z_mm
    y_long = (p.lower_end_length_mm + p.profile_size_mm) / 2.0
    x_end = (p.lower_long_length_mm - p.profile_size_mm) / 2.0
    frame = compound([
        _box_x(p.lower_long_length_mm, -y_long, z),
        _box_x(p.lower_long_length_mm, y_long, z),
        _box_y(p.lower_end_length_mm, -x_end, z),
        _box_y(p.lower_end_length_mm, x_end, z),
        _box_y(p.crossmember_length_mm, -p.guide_shaft_x_mm, z),
        _box_y(p.crossmember_length_mm, p.guide_shaft_x_mm, z),
    ])
    components = [_component(
        "NVR-L01_lower_4040_frame", frame, PROFILE, "4040 aluminium profile",
        category="purchased_cut", notes="820x2, 640x2, 560x2",
    )]

    feet = []
    for x in (-350.0, 350.0):
        for y in (-310.0, 310.0):
            feet.append(_slotted_foot().translate((x, y, 3.0)))
    components.append(_component(
        "NVR-P01_universal_lower_mount_tabs", compound(feet), STEEL,
        "SS400 flat bar 50x6", notes="Slots accept an unknown cart/base hole pattern; clamp after fit-up",
    ))

    risers = []
    bushings = []
    stop_blocks = []
    for x in (-p.guide_shaft_x_mm, p.guide_shaft_x_mm):
        risers.append(centered_box(50.0, 6.0, 200.0, (x, 0.0, 125.0)))
        for zc in (p.fixed_bushing_lower_z_mm, p.fixed_bushing_upper_z_mm):
            outer = cylinder_between((x, 0.0, zc - 15.0), (x, 0.0, zc + 15.0), 21.0)
            inner = cylinder_between((x, 0.0, zc - 17.0), (x, 0.0, zc + 17.0), 6.1)
            bushings.append(outer.cut(inner))
        for zc in (70.0, 210.0):
            block = centered_box(50.0, 30.0, 6.0, (x, 0.0, zc)).cut(
                cylinder_between((x, 0.0, zc - 5.0), (x, 0.0, zc + 5.0), 6.5)
            )
            stop_blocks.append(block)
    components.extend([
        _component("NVR-P06_shaft_support_risers", compound(risers), STEEL, "SS400 flat bar 50x6"),
        _component(
            "NVR-B02_LMF12UU_fixed_transfer_fit_bushings", compound(bushings), PURCHASED,
            "LMF12UU linear flange bushings", category="purchased",
            notes="Four fixed units; flange holes transfer-drilled after receipt",
        ),
        _component(
            "NVR-G07_fixed_Z_stop_blocks", compound(stop_blocks), STOP,
            "SS400 flat-bar bumpers", notes="Independent hard contacts for the moving split collars",
        ),
    ])
    return components


def moving_guide_components(pose, platform_z):
    p = N
    carriage_shapes = []
    clamp_shapes = []
    for zoff in (p.carriage_lower_offset_mm, p.carriage_upper_offset_mm):
        carriage_shapes.append(_box_x(p.carriage_length_mm, 0.0, platform_z + zoff))
        for x in (-p.guide_shaft_x_mm, p.guide_shaft_x_mm):
            clamp_shapes.append(centered_box(42.0, 36.0, 18.0, (x, 0.0, platform_z + zoff)))
    shafts = [
        cylinder_between(
            (x, 0.0, platform_z - p.guide_shaft_length_mm),
            (x, 0.0, platform_z),
            p.guide_shaft_diameter_mm / 2.0,
        )
        for x in (-p.guide_shaft_x_mm, p.guide_shaft_x_mm)
    ]
    collars = []
    for x in (-p.guide_shaft_x_mm, p.guide_shaft_x_mm):
        for zoff in (-165.0, -125.0):
            collar = cylinder_between(
                (x, 0.0, platform_z + zoff - 5.5),
                (x, 0.0, platform_z + zoff + 5.5),
                14.0,
            ).cut(cylinder_between(
                (x, 0.0, platform_z + zoff - 7.0),
                (x, 0.0, platform_z + zoff + 7.0),
                6.1,
            ))
            collars.append(collar)
    components = [
        _component(
            "NVR-G01_vertical_carriage_4040", compound(carriage_shapes), PROFILE,
            "4040 aluminium profile", category="purchased_cut", notes="240x2; translates only in Z",
        ),
        _component(
            "NVR-B01_SK12_moving_transfer_fit_clamps", compound(clamp_shapes), PURCHASED,
            "SK12 shaft supports", category="purchased",
            notes="Four moving clamps; mounting holes transfer-drilled after receipt",
        ),
        _component("NVR-S01_moving_twin_12mm_guide_shafts", compound(shafts), ACTUATOR_ROD, "12 mm linear shaft", category="purchased_cut"),
        _component(
            "NVR-G06_independent_Z_stop_collars", compound(collars), STOP,
            "12 mm split shaft collars", category="purchased",
            notes="Two collars per shaft; set against fixed lower/upper stop blocks during commissioning",
        ),
    ]

    lower_lugs = compound([
        centered_box(50.0, 6.0, 70.0, (0.0, -28.0, platform_z - 5.0)),
        centered_box(50.0, 6.0, 70.0, (0.0, 28.0, platform_z - 5.0)),
    ])
    cross = compound([
        centered_box(50.0, 50.0, 36.0, (0.0, 0.0, platform_z)),
        cylinder_between((-34.0, 0.0, platform_z), (-23.0, 0.0, platform_z), 4.0),
        cylinder_between((23.0, 0.0, platform_z), (34.0, 0.0, platform_z), 4.0),
        cylinder_between((0.0, -34.0, platform_z), (0.0, -23.0, platform_z), 4.0),
        cylinder_between((0.0, 23.0, platform_z), (0.0, 34.0, platform_z), 4.0),
    ])
    upper_lugs_local = compound([
        centered_box(6.0, 50.0, 70.0, (-28.0, 0.0, -5.0)),
        centered_box(6.0, 50.0, 70.0, (28.0, 0.0, -5.0)),
    ])
    stops = compound([
        centered_box(18.0, 18.0, 24.0, (x, y, platform_z - 18.0))
        for x, y in ((-42.0, -42.0), (-42.0, 42.0), (42.0, -42.0), (42.0, 42.0))
    ])
    components.extend([
        _component("NVR-G02_cardan_lower_yoke", lower_lugs, STEEL, "SS400 flat bar 50x6"),
        _component(
            "NVR-G03_cardan_laminated_cross", cross, COLORS["cyan"],
            "Six 50x50x6 plates plus four opposed M8 trunnions",
            notes="Bolt six plates into a 36 mm block, then transfer-drill/tap trunnion faces in one setup",
        ),
        _component("NVR-G04_cardan_upper_yoke", _local_to_world(upper_lugs_local, pose, platform_z), STEEL, "SS400 flat bar 50x6"),
        _component(
            "NVR-G05_independent_angle_stops", stops, STOP, "M8 adjustable stop screws",
            category="purchased", notes="Set during commissioning to stop before shaft/bushing bind",
        ),
    ])
    return components


def upper_structure_components(pose, platform_z):
    p = N
    y_long = (p.upper_end_length_mm + p.profile_size_mm) / 2.0
    x_end = (p.upper_long_length_mm - p.profile_size_mm) / 2.0
    local_frame = compound([
        _box_x(p.upper_long_length_mm, -y_long, 0.0),
        _box_x(p.upper_long_length_mm, y_long, 0.0),
        _box_y(p.upper_end_length_mm, -x_end, 0.0),
        _box_y(p.upper_end_length_mm, x_end, 0.0),
        _box_y(p.crossmember_length_mm, -200.0, 0.0),
        _box_y(p.crossmember_length_mm, 200.0, 0.0),
        _box_x(p.upper_center_length_mm, 0.0, 0.0),
        _box_y(p.upper_center_length_mm, 0.0, 0.0),
    ])
    local_panel = centered_box(
        p.platform_length_mm, p.platform_width_mm, p.acrylic_thickness_mm,
        (0.0, 0.0, p.profile_size_mm / 2.0 + p.acrylic_thickness_mm / 2.0),
    )
    local_spreaders = compound([
        centered_box(100.0, 50.0, 6.0, (x, y, 23.0))
        for x, y in p.upper_points_xy
    ])
    components = [
        _component(
            "NVR-U01_upper_4040_frame", _local_to_world(local_frame, pose, platform_z), PROFILE,
            "4040 aluminium profile", category="purchased_cut", notes="840x2, 660x2, 560x2, 420x2",
        ),
        _component(
            "NVR-U02_acrylic_work_deck", _local_to_world(local_panel, pose, platform_z), COLORS["clear"],
            "15 mm clear acrylic", category="purchased_cut",
            notes="Non-primary structural cover; profile frame carries actuator and cart-interface loads",
        ),
        _component("NVR-P03_upper_joint_spreaders", _local_to_world(local_spreaders, pose, platform_z), STEEL, "SS400 flat bar 50x6"),
    ]
    return components


def _actuator_components(base, top, index):
    base_v = cq.Vector(*base)
    top_v = cq.Vector(*top)
    direction = top_v - base_v
    length = direction.Length
    unit = direction.normalized()
    body_end = base_v + unit.multiply(min(150.0, length * 0.58))
    rod_start = base_v + unit.multiply(min(125.0, length * 0.48))
    body = cylinder_between(base_v, body_end, 25.0)
    rod = cylinder_between(rod_start, top_v, 10.0)
    joints = compound([
        cq.Workplane("XY").sphere(15.0).translate(base_v.toTuple()),
        cq.Workplane("XY").sphere(15.0).translate(top_v.toTuple()),
    ])
    return [
        _component(
            f"NVR-A{index}_LA2000_pin_lug_planning_envelope", compound([body, rod]), ACTUATOR_BODY,
            "LA2000-125150 pin/lug planning envelope", category="purchased",
            notes=f"Pin-centre length {length:.1f} mm; body envelope is conservative",
        ),
        _component(
            f"NVR-A{index}_pin_lug_joint_envelopes", joints, PURCHASED,
            "6 mm U/H bracket plus assumed M8 eye adapter", category="purchased_reference",
            notes="Final pins, spacers and transfer holes require delivered actuator inspection",
        ),
    ]


def actuator_components(pose, platform_z):
    components = []
    for index, ((ux, uy), (lx, ly)) in enumerate(zip(N.upper_points_xy, N.lower_points_xy), start=1):
        top = transform_local_point((ux, uy, 0.0), pose, platform_z)
        components.extend(_actuator_components((lx, ly, N.base_joint_z_mm), top, index))
    return components


def cart_coupling_components(pose, platform_z):
    p = N
    rails_local = compound([
        _box_x(p.cart_receiver_length_mm, -p.cart_rail_y_mm, 55.0),
        _box_x(p.cart_receiver_length_mm, p.cart_rail_y_mm, 55.0),
    ])
    locator_local = compound([
        cq.Workplane("XY").circle(10.0).extrude(25.0).translate((-p.locator_x_mm, 0.0, 35.0)),
        cq.Workplane("XY").circle(9.0).extrude(25.0).translate((p.locator_x_mm, 0.0, 35.0)),
    ])
    latches_local = compound([
        centered_box(85.0, 34.0, 44.0, (x, y, 38.0))
        for x in (-p.latch_x_mm, p.latch_x_mm)
        for y in (-p.latch_y_mm, p.latch_y_mm)
    ])
    return [
        _component(
            "NVR-C01_cart_side_receiver_rails", _local_to_world(rails_local, pose, platform_z), PROFILE,
            "4040 aluminium profile", category="cart_side_interface",
            notes="760x2 loose cart-side interface pieces; not a cart-body design",
        ),
        _component(
            "NVR-C02_master_and_secondary_locators", _local_to_world(locator_local, pose, platform_z), COLORS["cyan"],
            "Steel locator pins", notes="Round master and relieved/slotted secondary prevent over-constraint",
        ),
        _component(
            "NVR-C03_CR3001_latches", _local_to_world(latches_local, pose, platform_z), PURCHASED,
            "CR-3001 toggle clamps", category="purchased",
            notes="Four mechanical latches; electromagnets are not used as primary locks",
        ),
    ]


def components_for_pose(pose):
    platform_z = N.collapsed_joint_z_mm + pose.lift_mm
    components = []
    components.extend(lower_structure_components())
    components.extend(moving_guide_components(pose, platform_z))
    components.extend(upper_structure_components(pose, platform_z))
    components.extend(actuator_components(pose, platform_z))
    components.extend(cart_coupling_components(pose, platform_z))
    return components


def as_assembly(pose):
    assembly = cq.Assembly(name=f"navimro_radial3_{pose.label}")
    for component in components_for_pose(pose):
        r, g, b, a = component.color
        assembly.add(component.shape, name=component.name, color=cq.Color(r, g, b, a))
    return assembly


def export_step_states(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for name, pose in NAVIMRO_POSES.items():
        path = output_dir / f"navimro_radial3_{name}.step"
        as_assembly(pose).save(str(path), exportType="STEP", mode="default")
        outputs.append(path)
    return outputs
