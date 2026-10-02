"""Rev F REVIEW candidate, NOT APPROVED FOR FABRICATION or purchase.

Coordinates: local x radial, y tangent (pin), z up, origin at PHS ball.
World origin and 3-RPS solution are unchanged from Rev E. Only Z/pitch/roll
are commanded; solved X/Y/yaw are dependent closure coordinates.
All new bracket dimensions below are DESIGN ASSUMPTIONS, not delivered
tolerances. PHS spherical race, neck, pin transitions and tools are envelopes.
These envelopes cannot establish assembly feasibility or bearing capacity.
No exports, release flags, independent stops or fixed actuator-eye ears.
Self-weight-only supervised indoor PoC, no cart/payload/person.
Load review: +/-750 N per actuator, target static ratio 1.5, not stall proof;
see calculations.revf_upper_pocket_load_screen for equations and open checks.
"""
from functools import lru_cache
from math import atan2, degrees, isfinite
import cadquery as cq
from cad.revf_upper_pocket_inputs import PocketInputs, load_inputs
from cad.profile_radial_reve_actual_vendor import (
    Part, Pose, platform_transform, upper_eye_points, actuator_parts,
    _rigid_transform, group_shape, transform_upper_frame_shape,
    lower_joint_shapes, lower_lmb_bolt_shapes,
)
from fusion_scripts.ProfileRadialRevD import revd_data


REVIEW_ASSUMPTIONS = {
    "material": "S45C/SM45C candidate; delivered grade/strength unverified",
    "race_sphere_radius_mm": 7.0,
    "ball_keepout_radius_mm": 7.5,
    "neck_radius_mm": 5.0,
    "neck_end_z_mm": 30.0,
    "bracket_outer_radius_mm": 14.0,
    "mount_face_z_mm": 39.0,
    "base_length_mm": 60.0,
    "base_width_mm": 30.0,
    "mount_pitch_mm": 44.0,
    "mount_hole_mm": 6.6,
    "nominal_shoulder_length_mm": 35.0,
    "tool_envelope_radius_mm": 9.0,
}
COLOR = (0.50, 0.55, 0.62, 1.0)


def _cylinder(radius, length, start, direction=(0, 0, 1)):
    return cq.Solid.makeCylinder(radius, length, cq.Vector(*start), cq.Vector(*direction))


def _box(x, y, z, center):
    return cq.Workplane("XY").box(x, y, z).val().translate(center)


def _validate(inputs):
    values = (inputs.phs_outer_d_mm, inputs.phs_outer_width_mm, inputs.phs_ball_width_mm)
    if (inputs.bracket_count != 3 or inputs.eye_offset_mm != 16.0
            or any(not isfinite(v) or v <= 0 for v in values)
            or inputs.phs_outer_d_mm <= 15 or inputs.phs_outer_d_mm >= 28
            or inputs.phs_ball_width_mm >= 14):
        raise ValueError("Review geometry requires three brackets, unchanged 16 mm offset and valid bearing envelopes")


@lru_cache(maxsize=16)
def local_review_geometry(inputs: PocketInputs, axis_index: int = 1) -> dict[str, cq.Shape]:
    """Axis-specific base in radial/tangent coordinates; joint core unchanged."""
    _validate(inputs)
    basis = _basis(axis_index)
    angle = degrees(atan2(basis[0][1], basis[0][0]))
    def mount_orientation(shape):
        return shape.rotate((0, 0, 0), (0, 0, 1), angle)
    d = REVIEW_ASSUMPTIONS
    radius, width = inputs.phs_outer_d_mm / 2, inputs.phs_outer_width_mm
    race = cq.Solid.makeSphere(d["race_sphere_radius_mm"], angleDegrees1=-90)
    ball = race.intersect(_box(20, inputs.phs_ball_width_mm, 20, (0, 0, 0)))
    ball = ball.cut(_cylinder(3, 30, (0, -15, 0), (0, 1, 0)))
    ring = _cylinder(radius, width, (0, -width / 2, 0), (0, 1, 0))
    neck = _cylinder(d["neck_radius_mm"], 24, (0, 0, 6))
    housing = ring.fuse(neck).cut(race).cut(_cylinder(3, 10, (0, 0, 20)))
    # Axially open annular saddle, radial support around OD, no pin support ear.
    saddle = _cylinder(d["bracket_outer_radius_mm"], width, (0, -width / 2, 0), (0, 1, 0))
    saddle = saddle.cut(_cylinder(radius, width + 2, (0, -width / 2 - 1, 0), (0, 1, 0)))
    rails = _box(4, width, 34, (-12, 0, 17)).fuse(_box(4, width, 34, (12, 0, 17)))
    base = mount_orientation(_box(d["base_length_mm"], d["base_width_mm"], 9, (0, 0, 34.5)))
    bracket = saddle.fuse(rails).fuse(base)
    # Open neck insertion channel; housing slides from +local Y before M6.
    bracket = bracket.cut(_box(10, 60, 24, (0, 25, 18)))
    bracket = bracket.cut(_cylinder(3.3, 9, (0, 0, 30)))
    bracket = bracket.cut(_cylinder(5.5, 6, (0, 0, 33)))
    for x in (-d["mount_pitch_mm"] / 2, d["mount_pitch_mm"] / 2):
        bracket = bracket.cut(mount_orientation(_cylinder(d["mount_hole_mm"] / 2, 12, (x, 0, 29))))
    shoulder_start = -(20 + 1.5 + inputs.phs_ball_width_mm / 2)
    shoulder_end = shoulder_start + d["nominal_shoulder_length_mm"]
    ball_end = inputs.phs_ball_width_mm / 2
    pin = _cylinder(3, 35, (0, shoulder_start, 0), (0, 1, 0))
    head = _cylinder(5, 6, (0, shoulder_start - 6, 0), (0, 1, 0))
    thread = _cylinder(2.5, 10, (0, shoulder_end, 0), (0, 1, 0))
    def washer(start, length, radius=5):
        return _cylinder(radius, length, (0, start, 0), (0, 1, 0)).cut(
            _cylinder(3.1, length, (0, start, 0), (0, 1, 0)))
    geometry = {
        "bracket": bracket.clean(), "housing": housing, "ball": ball,
        "ball_window": cq.Solid.makeSphere(d["ball_keepout_radius_mm"], angleDegrees1=-90),
        "eye_envelope": _cylinder(10, 20, (0, shoulder_start, 0), (0, 1, 0)).cut(
            _cylinder(3, 20, (0, shoulder_start, 0), (0, 1, 0))),
        "pin_shoulder": pin, "pin_head": head, "pin_m5_thread_envelope": thread,
        "shim": washer(-ball_end - 1.5, 1.5),
        "spacer": washer(ball_end, shoulder_end - ball_end),
        "m5_nut_envelope": _cylinder(4.7, 5, (0, shoulder_end, 0), (0, 1, 0)).cut(thread),
        "m6_retainer_envelope": _cylinder(3, 13, (0, 0, 20)).fuse(_cylinder(5, 6, (0, 0, 33))),
        "pin_transition_unknown_keepout": _cylinder(4, 1, (0, shoulder_start, 0), (0, 1, 0)).fuse(
            _cylinder(4, 1, (0, shoulder_end - 1, 0), (0, 1, 0))),
        "m6_tool_envelope": _cylinder(3, 40, (0, 0, 39)),
        "m5_tool_envelope": _cylinder(9, 35, (0, shoulder_end + 5, 0), (0, 1, 0)),
    }
    for index, x in enumerate((-22, 22), 1):
        geometry[f"mount_bolt_{index}_envelope"] = mount_orientation(_cylinder(3, 16.5, (x, 0, 30)).fuse(_cylinder(5, 6, (x, 0, 24))))
        geometry[f"tnut_{index}_UNVERIFIED_SLOT"] = mount_orientation(_box(23, 10, 5, (x, 0, 44)).cut(_cylinder(3, 6, (x, 0, 41))))
        # Straight hex-driver shaft only; handle sweep is an unresolved check.
        geometry[f"mount_tool_{index}_envelope"] = mount_orientation(_cylinder(3, 40, (x, 0, -16)))
    return geometry


def _basis(axis_index):
    if type(axis_index) is not int or axis_index not in (1, 2, 3):
        raise ValueError("Axis index must be 1, 2 or 3")
    _, tangent = revd_data.support_basis()[axis_index - 1]
    radial = (tangent[1], -tangent[0], 0)
    return ((radial[0], tangent[0], 0), (radial[1], tangent[1], 0), (0, 0, 1))


def joint_reference(axis_index: int, pose: Pose):
    _basis(axis_index)
    tangent = revd_data.support_basis()[axis_index - 1][1]
    eye = upper_eye_points(pose)[axis_index - 1]
    return {"ball_center": tuple(eye[i] + 16 * tangent[i] for i in range(3)), "pin_axis": tangent}


def _place(shape, axis, pose, follows_platform=True):
    basis = _basis(axis)
    ref = joint_reference(axis, pose)
    if follows_platform:
        rotation, _, _ = platform_transform(pose)
        basis = tuple(tuple(sum(rotation[i][k] * basis[k][j] for k in range(3)) for j in range(3)) for i in range(3))
    return _rigid_transform(shape, basis, ref["ball_center"])


def pocket_brackets(inputs: PocketInputs) -> tuple[Part, Part, Part]:
    """Three axis-specific candidates in collapsed frame, NOT supplier SKUs."""
    return tuple(Part(f"A{i}_REVF_POCKET_REVIEW_NOT_FOR_FABRICATION", _place(local_review_geometry(inputs, i)["bracket"], i, Pose("collapsed", 0, 0, 0)), COLOR, "upper_pockets") for i in (1, 2, 3))


def phs_components(axis_index: int, pose: Pose) -> dict[str, cq.Shape]:
    """Default-input bearing/hardware. Housing follows frame; ball/pin do not."""
    return _joint_components(axis_index, pose, load_inputs())


def _joint_components(axis, pose, inputs):
    geo = local_review_geometry(inputs, axis)
    keys = ("housing", "ball", "pin_shoulder", "pin_head", "pin_m5_thread_envelope", "shim", "spacer", "m5_nut_envelope", "m6_retainer_envelope")
    return {key: _place(geo[key], axis, pose, key in ("housing", "m6_retainer_envelope")) for key in keys}


def revf_components_for_pose(pose: Pose, inputs: PocketInputs) -> list[Part]:
    """Use unchanged source structure/lower R and actual six-solid actuators."""
    rows = [Part(name.upper(), group_shape(name), COLOR, name) for name in ("lower_frame", "lower_brackets", "lower_adapters")]
    rows += [Part(name.upper(), transform_upper_frame_shape(group_shape(name), pose), COLOR, name) for name in ("upper_frame", "upper_brackets")]
    rows += [Part(f"A{i}_LMB10", shape, COLOR, "lower_joints") for i, shape in enumerate(lower_joint_shapes(), 1)]
    rows += [Part(f"LOWER_BOLT_{i}", shape, COLOR, "lower_fasteners") for i, shape in enumerate(lower_lmb_bolt_shapes(), 1)]
    for axis in (1, 2, 3):
        geo = local_review_geometry(inputs, axis)
        rows.append(Part(f"A{axis}_REVF_POCKET_REVIEW_NOT_FOR_FABRICATION", _place(geo["bracket"], axis, pose), COLOR, "upper_pockets"))
        rows += [Part(f"A{axis}_REVF_{key}", shape, COLOR, "upper_joints") for key, shape in _joint_components(axis, pose, inputs).items()]
        rows += [Part(f"A{axis}_REVF_{key}", _place(shape, axis, pose), COLOR, "upper_fasteners") for key, shape in geo.items() if key.startswith(("mount_bolt", "tnut"))]
        rows.extend(actuator_parts(axis, pose))
    return rows


def _path_measurements(geometry, keys, direction, obstacles, travel):
    """Pairwise samples retain invalid results; no finite path proves assembly."""
    measurements = []
    for step in range(9):
        for key in keys:
            for obstacle in obstacles:
                offset = travel * step / 8
                row = {"moving": key, "obstacle": obstacle, "offset_mm": offset}
                try:
                    moving = geometry[key].translate(tuple(a * offset for a in direction))
                    common = moving.intersect(geometry[obstacle])
                    volume = common.Volume()
                    valid = moving.isValid() and geometry[obstacle].isValid() and common.isValid() and isfinite(volume) and volume >= -1e-8
                    row.update(volume_mm3=volume if isfinite(volume) else None, boolean_valid=bool(valid))
                except Exception as error:
                    row.update(volume_mm3=None, boolean_valid=False, error=str(error))
                measurements.append(row)
    witness = max(measurements, key=lambda row: row["volume_mm3"] if row["volume_mm3"] is not None else -1)
    valid_rows = [row for row in measurements if row["boolean_valid"]]
    invalid = sum(not row["boolean_valid"] for row in measurements)
    maximum = max((r["volume_mm3"] for r in measurements if r["volume_mm3"] is not None), default=None)
    maximum_valid = max((r["volume_mm3"] for r in valid_rows), default=None)
    return {"samples": 9, "travel_mm": travel, "approach_from_local": direction,
            "maximum_unintended_volume_mm3": maximum, "maximum_witness": witness,
            "maximum_valid_volume_mm3": maximum_valid, "invalid_boolean_count": invalid,
            "invalid_witnesses": [r for r in measurements if not r["boolean_valid"]],
            "nominal_sample_clear": invalid == 0 and maximum_valid is not None and maximum_valid < 1e-6,
            "moving_volume_mm3": sum(geometry[key].Volume() for key in keys),
            "status": "UNKNOWN", "continuous_sweep_verified": False,
            "moving": keys, "obstacles": obstacles}


def _aggregate_paths(paths):
    """Composite measurements never substitute zero for absent valid evidence."""
    valid = [p["maximum_valid_volume_mm3"] for p in paths
             if p["maximum_valid_volume_mm3"] is not None and isfinite(p["maximum_valid_volume_mm3"])]
    diagnostic = [p["maximum_unintended_volume_mm3"] for p in paths
                  if p["maximum_unintended_volume_mm3"] is not None and isfinite(p["maximum_unintended_volume_mm3"])]
    invalid = sum(p["invalid_boolean_count"] for p in paths)
    maximum = max(valid, default=None)
    return {"maximum_unintended_volume_mm3": maximum, "maximum_valid_volume_mm3": maximum,
            "diagnostic_maximum_volume_mm3": max(diagnostic, default=None),
            "invalid_boolean_count": invalid,
            "invalid_witnesses": [dict(w, child_path_index=i) for i, p in enumerate(paths) for w in p["invalid_witnesses"]],
            "nominal_sample_clear": bool(paths) and invalid == 0 and all(p["nominal_sample_clear"] for p in paths),
            "status": "UNKNOWN"}


def _axis_assembly_path_review(inputs, axis):
    g = dict(local_review_geometry(inputs, axis))
    neutral = Pose("axis_assembly", 25, 0, 0)
    basis = _basis(axis)
    rotation, _, _ = platform_transform(neutral)
    frame_basis = tuple(tuple(sum(rotation[i][k] * basis[k][j] for k in range(3)) for j in range(3)) for i in range(3))
    inverse = tuple(zip(*frame_basis))
    pin_in_frame = tuple(tuple(sum(inverse[i][k] * basis[k][j] for k in range(3)) for j in range(3)) for i in range(3))
    fixed_pin_keys = ("ball", "pin_shoulder", "pin_head", "pin_m5_thread_envelope", "shim", "spacer", "m5_nut_envelope", "m5_tool_envelope")
    for key in fixed_pin_keys:
        g[key] = _rigid_transform(g[key], pin_in_frame, (0, 0, 0))
    positive_pin = tuple(pin_in_frame[i][1] for i in range(3))
    negative_pin = tuple(-v for v in positive_pin)
    center = joint_reference(axis, neutral)["ball_center"]
    translation = tuple(-sum(row[i] * center[i] for i in range(3)) for row in inverse)
    actual_eye = next(part.shape for part in actuator_parts(axis, neutral) if "NEIGUAN" in part.name)
    g["actual_supplier_moving_part"] = _rigid_transform(actual_eye, inverse, translation)
    for key in ("upper_frame", "upper_brackets"):
        g[key] = _rigid_transform(transform_upper_frame_shape(group_shape(key), neutral), inverse, translation)
    # T-nuts enter the separate crossmember before its ends meet side members.
    # Retain the historical section; its shallow floor is a reported mismatch.
    sx, sy = revd_data.upper_support_points()[axis - 1]
    crossmember = next(s for s in group_shape("upper_frame").Solids()
                       if abs(s.BoundingBox().xlen - 640) < 1e-6
                       and abs(s.Center().y - sy) < 1e-6)
    g["isolated_crossmember"] = _rigid_transform(transform_upper_frame_shape(crossmember, neutral), inverse, translation)
    stages = []
    def check(stage, keys, direction, obstacles, travel=40, phase="BEFORE_FRAME_ATTACHMENT"):
        row = _path_measurements(g, keys, direction, obstacles, travel)
        row.update(stage=stage, axis=axis, assembly_phase=phase)
        stages.append(row)
        return row
    nut_paths = []
    # Insert left-position nut first from +frame X, then the right-position nut.
    # Both must be retained in position before closing the crossmember ends.
    for index, dx in ((1, -22), (2, 22)):
        obstacles = ["isolated_crossmember"] + (["tnut_1_UNVERIFIED_SLOT"] if index == 2 else [])
        nut_paths.append(check("tnut_end_insertion", [f"tnut_{index}_UNVERIFIED_SLOT"],
                               tuple(basis[0]), obstacles, 320 + 11.5 + 2 - (sx + dx),
                               "BEFORE_CROSSMEMBER_ENDS_CLOSED"))
        stages.pop()
    stages.append({"axis": axis, "stage": "tnut_end_insertion", "assembly_phase": "BEFORE_CROSSMEMBER_ENDS_CLOSED",
                   "paths": nut_paths, "samples": 18, "obstacles": ["isolated_crossmember"],
                   **_aggregate_paths(nut_paths), "route": "+FRAME_X_END_OF_SEPARATE_CROSSMEMBER",
                   "prerequisite": "Insert and position both nuts before side/corner members close ends; retention during frame assembly unverified"})
    check("housing_insertion", ["housing", "ball"], (0, 1, 0), ["bracket"])
    check("m6_retention", ["m6_retainer_envelope"], (0, 0, 1), ["bracket", "housing"])
    tool_paths = [check("tool_access", ["m6_tool_envelope"], (0, 0, 1), ["bracket", "housing", "ball"])]
    stages.pop()
    frame_obstacles = ["upper_frame", "upper_brackets", "tnut_1_UNVERIFIED_SLOT", "tnut_2_UNVERIFIED_SLOT"]
    check("bracket_approach", ["bracket", "housing", "ball", "m6_retainer_envelope"], (0, 0, -1),
          frame_obstacles, phase="FRAME_POSITIONING_BEFORE_EYE")
    check("profile_attachment", ["mount_bolt_1_envelope", "mount_bolt_2_envelope"], (0, 0, -1),
          ["bracket", "housing", "m6_retainer_envelope"] + frame_obstacles, phase="FRAME_ATTACHED_BEFORE_EYE")
    for key in ("mount_tool_1_envelope", "mount_tool_2_envelope"):
        tool_paths.append(check("tool_access", [key], (0, 0, -1), ["bracket", "housing", "ball"] + frame_obstacles,
                                phase="FRAME_ATTACHED_BEFORE_EYE"))
        stages.pop()
    for stage, keys, direction, obstacles in (
        ("shim_insertion", ["shim"], negative_pin, ["bracket", "housing", "ball"]),
        ("eye_approach", ["actual_supplier_moving_part"], negative_pin, ["bracket", "housing", "ball", "shim"]),
        ("pin_insertion", ["pin_shoulder", "pin_head", "pin_m5_thread_envelope"], negative_pin, ["bracket", "housing", "ball", "shim", "actual_supplier_moving_part"]),
        ("spacer_insertion", ["spacer"], positive_pin, ["bracket", "housing", "ball", "pin_shoulder", "pin_m5_thread_envelope"]),
        ("m5_nut", ["m5_nut_envelope"], positive_pin, ["bracket", "housing", "ball", "spacer", "pin_m5_thread_envelope"]),
    ):
        check(stage, keys, direction, obstacles + frame_obstacles + ["mount_bolt_1_envelope", "mount_bolt_2_envelope"], phase="AFTER_FRAME_ATTACHMENT")
    tool_paths.append(check("tool_access", ["m5_tool_envelope"], positive_pin,
                            ["bracket", "housing", "ball", "actual_supplier_moving_part"] + frame_obstacles,
                            phase="AFTER_FRAME_ATTACHMENT"))
    stages.pop()
    stages.append({"axis": axis, "stage": "tool_access", "samples": 36, "paths": tool_paths,
                   **_aggregate_paths(tool_paths), "handle_sweep_verified": False})
    return stages


@lru_cache(maxsize=4)
def assembly_path_review(inputs: PocketInputs) -> dict:
    """Three staged, sampled paths. Not assembly approval or a swept proof."""
    return {"review_only": True, "assembly_verified": False, "fabrication_release": False, "purchase_release": False,
            "control_power_test_release": False, "motor_power_release": False,
            "nominal_grip_mm": 20 + inputs.phs_ball_width_mm + 1.5,
            "continuous_shoulder_contact_length_mm": inputs.shoulder_contact_length_mm,
            "stages": [row for axis in (1, 2, 3) for row in _axis_assembly_path_review(inputs, axis)],
            "slot_review": {"status": "UNKNOWN/HOLD", "historical_model_depth_mm": 6.9,
                            "candidate_insertion_mm": 7.5, "model_floor_overlap_mm": 0.6,
                            "actual_dnf3030_interference_proven": False,
                            "note": "Historical 2.5 mm lip plus 4.4 mm cavity differs from prior 10.5 mm floor source. Delivered section and clamp capacity unverified; retained model unchanged."},
            "intentional_contacts": ["housing OD / annular saddle", "neck end / bracket seat", "M6 thread / housing female thread", "ball spherical race / housing", "eye-shim-ball-spacer axial stack", "bolt head / seat", "bracket mount face / profile", "T-nut / profile slot lips"],
            "unresolved": list(inputs.unresolved_evidence) + ["Internal ball/race and neck are assumed envelopes; verify exact supplier geometry", "Unknown head fillet and shoulder transition represented by separate keepout, NOT cleared", "Pin head seating on cylindrical vendor eye needs actual contact geometry", "All-pose actual-eye/frame and cross-axis collisions deferred to full audit", "Actual 3030 slot, nut positioning before frame closure and tool rotations unverified", "Sampled paths are not continuous sweeps; lower R final installation unverified", "Axis-specific candidates do not establish one orderable bracket SKU", "Housing fit/clearance and M6 lock/preload/capture under reversing +/-750 N unverified"]}
