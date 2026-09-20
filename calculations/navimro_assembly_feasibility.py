"""Digital assembly-feasibility checks for the NAVIMRO Rev E mock-up."""

from __future__ import annotations

from functools import lru_cache

from cad.navimro_detailed_assembly import detailed_components
from cad.navimro_fabrication_parameters import N, NAVIMRO_POSES, NavimroPose


def shape_of(part):
    return part.shape.val() if hasattr(part.shape, "val") else part.shape


def _bbox_overlap(first, second, tolerance=1e-6):
    a = shape_of(first).BoundingBox()
    b = shape_of(second).BoundingBox()
    return (
        a.xmin < b.xmax - tolerance
        and a.xmax > b.xmin + tolerance
        and a.ymin < b.ymax - tolerance
        and a.ymax > b.ymin + tolerance
        and a.zmin < b.zmax - tolerance
        and a.zmax > b.zmin + tolerance
    )


def intersection_volume(first, second):
    if not _bbox_overlap(first, second):
        return 0.0
    return shape_of(first).intersect(shape_of(second)).Volume()


def distance(first, second):
    return shape_of(first).distance(shape_of(second))


def _cross_collisions(first, second, tolerance=0.01):
    collisions = []
    for a in first:
        for b in second:
            volume = intersection_volume(a, b)
            if volume > tolerance:
                collisions.append((a.name, b.name, volume))
    return collisions


def sampled_poses():
    poses = [NavimroPose(f"lift_{lift:03d}", float(lift)) for lift in range(0, 101, 10)]
    poses.extend(
        pose for name, pose in NAVIMRO_POSES.items()
        if name not in ("collapsed", "neutral", "raised")
    )
    return poses


@lru_cache(maxsize=32)
def _parts(label, lift_mm, pitch_deg, roll_deg):
    return tuple(detailed_components(NavimroPose(label, lift_mm, pitch_deg, roll_deg)))


def parts_for_pose(pose):
    if isinstance(pose, str):
        pose = NAVIMRO_POSES[pose]
    return _parts(pose.label, pose.lift_mm, pose.pitch_deg, pose.roll_deg)


def guide_motion_collisions():
    collisions = []
    for pose in sampled_poses():
        parts = parts_for_pose(pose)
        moving = [part for part in parts if part.group == "03_MOVING_GUIDE"]
        fixed = [part for part in parts if part.group == "02_FIXED_GUIDE"]
        lower = [part for part in parts if part.group == "01_LOWER_FRAME"]
        upper = [part for part in parts if part.group == "05_UPPER_FRAME"]
        for group_name, group_parts in (("fixed", fixed), ("lower", lower), ("upper", upper)):
            for first, second, volume in _cross_collisions(moving, group_parts):
                collisions.append((pose.label, group_name, first, second, volume))
    return collisions


def actuator_nonframe_collisions():
    collisions = []
    for pose in sampled_poses():
        parts = parts_for_pose(pose)
        actuators = [part for part in parts if part.name.startswith("LA2000_A2_PROVISIONAL_")]
        central = [
            part for part in parts
            if part.group in ("02_FIXED_GUIDE", "03_MOVING_GUIDE", "04_CARDAN")
        ]
        for first, second, volume in _cross_collisions(actuators, central):
            collisions.append((pose.label, first, second, volume))
    return collisions


def bore_interference_results():
    issues = []
    for pose_name in NAVIMRO_POSES:
        parts = parts_for_pose(pose_name)
        by_name = {part.name: part for part in parts}

        for index in (1, 2):
            shaft = by_name[f"NVR-S01_shaft_{index}"]
            mates = [
                by_name[f"LWR_cross_{index}"],
                by_name[f"LMF12UU_{index}_1"],
                by_name[f"LMF12UU_{index}_2"],
                by_name[f"SK12_{index}"],
                by_name[f"NVR-P13_moving_stop_pad_{index}_1_outer"],
            ]
            for mate in mates:
                volume = intersection_volume(shaft, mate)
                if volume > 0.01:
                    issues.append((pose_name, shaft.name, mate.name, volume))

        cardan_x = by_name["CARDAN_X_pin"]
        cardan_y = by_name["CARDAN_Y_pin"]
        if intersection_volume(cardan_x, cardan_y) > 0.01:
            issues.append((pose_name, cardan_x.name, cardan_y.name, intersection_volume(cardan_x, cardan_y)))
        for pin, tokens in (
            (cardan_x, ("upper_yoke", "cross_laminate")),
            (cardan_y, ("lower_yoke", "cross_laminate")),
        ):
            for mate in parts:
                if any(token in mate.name for token in tokens):
                    volume = intersection_volume(pin, mate)
                    if volume > 0.01:
                        issues.append((pose_name, pin.name, mate.name, volume))

        deck = by_name["NVR-U02_acrylic_deck"]
        for screw in (part for part in parts if part.name.startswith("DECK_") and part.name.endswith("_screw")):
            volume = intersection_volume(deck, screw)
            if volume > 0.01:
                issues.append((pose_name, deck.name, screw.name, volume))
            spacer = by_name[f"DECK_spacer_{screw.name.split('_')[1]}"]
            volume = intersection_volume(spacer, screw)
            if volume > 0.01:
                issues.append((pose_name, spacer.name, screw.name, volume))
        for part in (part for part in parts if part.name.startswith("DECK_") and part.name.endswith(("_washer", "_spacer"))):
            volume = intersection_volume(deck, part)
            if volume > 0.01:
                issues.append((pose_name, deck.name, part.name, volume))

        for index in (1, 2):
            sk = by_name[f"SK12_{index}"]
            for hole in (1, 2):
                screw = by_name[f"SK12_{index}_{hole}_screw"]
                volume = intersection_volume(sk, screw)
                if volume > 0.01:
                    issues.append((pose_name, sk.name, screw.name, volume))

        for index in (1, 2):
            for level in (1, 2):
                bushing = by_name[f"LMF12UU_{index}_{level}"]
                tab = by_name[f"NVR-P09_LMF_tab_{index}_{level}"]
                for hole in (1, 2, 3, 4):
                    screw = by_name[f"LMF_{index}_{level}_{hole}_screw"]
                    for mate in (bushing, tab):
                        volume = intersection_volume(mate, screw)
                        if volume > 0.01:
                            issues.append((pose_name, mate.name, screw.name, volume))
    return issues


def stop_clearances():
    result = {}
    for pose_name, fixed_level in (("collapsed", 1), ("raised", 2)):
        by_name = {part.name: part for part in parts_for_pose(pose_name)}
        values = []
        for index in (1, 2):
            fixed = by_name[f"NVR-P13_fixed_carriage_stop_{index}_{fixed_level}"]
            moving = by_name[f"NVR-P13_moving_stop_pad_{index}_1_outer"]
            values.append(distance(fixed, moving))
        result[pose_name] = tuple(values)
    return result


def neutral_connectivity():
    by_name = {part.name: part for part in parts_for_pose("neutral")}
    return {
        "lower_bridge_to_carriage_mm": distance(
            by_name["NVR-P08_lower_cardan_bridge"], by_name["NVR-G01_carriage"]
        ),
        "upper_bridge_to_rail_a_mm": distance(
            by_name["NVR-P08_upper_cardan_bridge_1"], by_name["UPR_center_X_A"]
        ),
        "upper_bridge_to_rail_b_mm": distance(
            by_name["NVR-P08_upper_cardan_bridge_3"], by_name["UPR_center_X_B"]
        ),
        "upper_center_rail_separation_mm": distance(
            by_name["UPR_center_X_A"], by_name["UPR_center_X_B"]
        ),
        "cardan_pin_separation_mm": distance(
            by_name["CARDAN_X_pin"], by_name["CARDAN_Y_pin"]
        ),
    }


def module_envelope(pose_name="collapsed"):
    parts = [
        part for part in parts_for_pose(pose_name)
        if part.group != "08_CART_COUPLING"
    ]
    boxes = [shape_of(part).BoundingBox() for part in parts]
    return {
        "x_mm": max(box.xmax for box in boxes) - min(box.xmin for box in boxes),
        "y_mm": max(box.ymax for box in boxes) - min(box.ymin for box in boxes),
        "z_mm": max(box.zmax for box in boxes) - min(box.zmin for box in boxes),
    }


def cart_reference_check():
    result = {}
    cart_boxes = None
    for pose_name in ("collapsed", "raised"):
        parts = parts_for_pose(pose_name)
        cart = [shape_of(part).BoundingBox() for part in parts if part.group == "08_CART_COUPLING"]
        module = [shape_of(part).BoundingBox() for part in parts if part.group != "08_CART_COUPLING"]
        current = (
            min(box.xmin for box in cart), max(box.xmax for box in cart),
            min(box.ymin for box in cart), max(box.ymax for box in cart),
            min(box.zmin for box in cart), max(box.zmax for box in cart),
        )
        if cart_boxes is None:
            cart_boxes = current
        result[f"{pose_name}_cart_bbox_mm"] = current
        result[f"{pose_name}_vertical_gap_mm"] = min(box.zmin for box in module) - max(box.zmax for box in cart)
    result["static_reference"] = result["collapsed_cart_bbox_mm"] == result["raised_cart_bbox_mm"]
    return result


def audit_summary():
    guide = guide_motion_collisions()
    actuator = actuator_nonframe_collisions()
    bores = bore_interference_results()
    stops = stop_clearances()
    connectivity = neutral_connectivity()
    envelope = module_envelope()
    cart_reference = cart_reference_check()
    stop_pass = all(1.5 <= value <= 3.0 for values in stops.values() for value in values)
    connectivity_pass = (
        connectivity["lower_bridge_to_carriage_mm"] <= 0.01
        and connectivity["upper_bridge_to_rail_a_mm"] <= 0.01
        and connectivity["upper_bridge_to_rail_b_mm"] <= 0.01
        and connectivity["upper_center_rail_separation_mm"] > 0.1
        and connectivity["cardan_pin_separation_mm"] > 0.1
    )
    envelope_pass = 250.0 <= envelope["z_mm"] <= 300.0
    return {
        "revision": "E",
        "parameters": {
            "actuator_stroke_mm": N.actuator_vendor_stroke_mm,
            "guide_shaft_length_mm": N.guide_shaft_length_mm,
            "guide_shaft_points_xy": N.guide_shaft_points_xy,
            "cardan_axis_offset_mm": (
                N.cardan_upper_axis_offset_mm - N.cardan_lower_axis_offset_mm
            ),
        },
        "sample_count": len(sampled_poses()),
        "guide_motion_collisions": guide,
        "actuator_central_collisions": actuator,
        "bore_interference": bores,
        "stop_clearance_mm": stops,
        "connectivity_mm": connectivity,
        "module_envelope_mm": envelope,
        "cart_reference_check": cart_reference,
        "stop_clearance_pass": stop_pass,
        "connectivity_pass": connectivity_pass,
        "module_height_pass": envelope_pass,
        "cart_coupling_status": "PROVISIONAL_SEPARATED_REFERENCE_NOT_INCLUDED_IN_PASS_CART_INTERFACE_UNFROZEN",
        "digital_assembly_pass": (
            not guide
            and not actuator
            and not bores
            and stop_pass
            and connectivity_pass
            and envelope_pass
        ),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(audit_summary(), indent=2))
