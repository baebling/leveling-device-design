"""Review-only screen of stock upper-joint fasteners, never a release model.

This module does not change the active Rev E bill of materials or CAD export.
It intentionally keeps nominal contact-plane arithmetic separate from unknown
fits, strength, tightening force, stock tolerances, and tool access.
"""

from __future__ import annotations

from itertools import product
import json
from pathlib import Path


def candidate_stud_stack() -> dict:
    """Return nominal FABB6-28/SNTRCS6/2-shim/SP306 contact planes.

    z=0 is the PHS6 ball/pivot centre, positive z points into the 3030
    underside slot. The existing 10 mm stud engagement inside the PHS6 is
    assumed, not newly approved here.
    """

    stud_start = 20.0
    stud_tip = stud_start + 28.0
    jam_nut = (30.0, 35.0)
    thin_nut = (jam_nut[1], jam_nut[1] + 3.0)
    shims = (thin_nut[1], thin_nut[1] + 2 * 0.5)
    profile_outer = 39.0
    slot_lip = profile_outer + 2.5
    slot_nut = (slot_lip, slot_lip + 5.0)
    slot_floor = profile_outer + 10.5
    return {
        "stud_start_z_from_phs_mm": stud_start,
        "stud_tip_z_from_phs_mm": stud_tip,
        "jam_nut_z_from_phs_mm": jam_nut,
        "thin_nut_z_from_phs_mm": thin_nut,
        "shim_z_from_phs_mm": shims,
        "profile_outer_face_z_from_phs_mm": profile_outer,
        "slot_lip_z_from_phs_mm": slot_lip,
        "slot_nut_body_z_from_phs_mm": slot_nut,
        "slot_floor_z_from_phs_mm": slot_floor,
        "slot_nut_geometric_overlap_mm": max(0.0, min(stud_tip, slot_nut[1]) - slot_nut[0]),
        "tip_past_slot_nut_mm": stud_tip - slot_nut[1],
        "slot_floor_clearance_mm": slot_floor - stud_tip,
        "nominal_external_stack_closed": shims[1] == profile_outer,
        "effective_thread_engagement_verified": False,
        "clamp_force_verified": False,
    }


def candidate_cb6_stack() -> dict:
    """Nominal axial stations of one CB6-55 upper pivot screw.

    t=0 is the PHS6 pivot centre and +t follows the world-fixed lower
    hinge axis. The rear actuator eye is centred at -16 mm. The 9 mm
    TRUSCO ball width, not the CAD model's conservative 10 mm outer
    envelope, defines the physical pin stack.
    """

    eye_centre = -16.0
    eye_width = 20.0
    eye = (eye_centre - eye_width / 2.0, eye_centre + eye_width / 2.0)
    ball_width = 9.0
    ball = (-ball_width / 2.0, ball_width / 2.0)
    shims = (eye[1], ball[0])
    underhead = eye[0]
    screw_length = 55.0
    thread_length = 24.0
    # CB cites JIS B1176 dimensional precision. MISUMI's JIS M6x55
    # table distinguishes ls,min=26 from lg,max=31. 55-24=31 is the
    # MAXIMUM grip boundary, not guaranteed full-diameter smooth shank.
    # https://jp.misumi-ec.com/tech-info/categories/technical_data/td01/a0196.html
    guaranteed_plain_shank_min = 26.0
    max_grip = screw_length - thread_length
    max_grip_end = underhead + max_grip
    screw_tip = underhead + screw_length
    nut = (max_grip_end, max_grip_end + 5.0)
    possible_transition = (
        underhead + guaranteed_plain_shank_min,
        max_grip_end,
    )
    required_smooth = ball[1] - underhead
    return {
        "actuator_eye_t_from_phs_mm": eye,
        "shims_t_from_phs_mm": shims,
        "phs_ball_t_from_phs_mm": ball,
        "underhead_t_from_phs_mm": underhead,
        "guaranteed_plain_shank_length_min_mm": guaranteed_plain_shank_min,
        "max_grip_length_mm": max_grip,
        "stack_requires_plain_shank_mm": required_smooth,
        "plain_shank_guarantee_shortfall_mm": required_smooth - guaranteed_plain_shank_min,
        "possible_thread_transition_t_from_phs_mm": possible_transition,
        "thread_transition_possible_inside_phs_ball": (
            possible_transition[0] < ball[1] and possible_transition[1] > ball[0]
        ),
        "retaining_nut_t_from_phs_mm": nut,
        "screw_tip_t_from_phs_mm": screw_tip,
        "exposed_thread_tail_t_from_phs_mm": (nut[1], screw_tip),
        "max_grip_minus_nominal_stack_mm_not_endplay_guarantee": max_grip_end - ball[1],
        "fit_and_retention_verified": False,
    }


def candidate_joint_solids(pose, axis_index: int) -> dict:
    """Conservative, nominal screw envelopes on a current Rev E pose.

    The upper stud rotates with the 3030 frame. The CB6 pivot axis does not:
    it follows the world-fixed lower revolute joint tangent. Contact with
    the intended eye, PHS6 ball and slot nut is therefore not a clash.
    """

    if axis_index not in (1, 2, 3):
        raise ValueError("axis_index must be 1, 2, or 3")
    import cadquery as cq

    from cad import profile_radial_reve_actual_vendor as active

    support = active.revd_data.upper_support_points()[axis_index - 1]
    tangent = active.revd_data.support_basis()[axis_index - 1][1]
    phs_z = active.revd_data.P.upper_ring_z_collapsed_mm

    def upright(radius, start_z, length):
        cylinder = cq.Solid.makeCylinder(
            radius, length, cq.Vector(support[0], support[1], phs_z + start_z)
        )
        return active.transform_upper_shape(cylinder, pose)

    def upright_ring(outer_radius, start_z, length):
        outside = upright(outer_radius, start_z, length)
        bore = upright(3.05, start_z - 0.01, length + 0.02)
        return outside.cut(bore)

    eye = active.upper_eye_points(pose)[axis_index - 1]
    phs = tuple(eye[i] + 16.0 * tangent[i] for i in range(3))

    def point(t):
        return cq.Vector(*(phs[i] + t * tangent[i] for i in range(3)))

    def pivot_cylinder(radius, start_t, length):
        return cq.Solid.makeCylinder(radius, length, point(start_t), cq.Vector(*tangent))

    def pivot_ring(outer_radius, start_t, length):
        return pivot_cylinder(outer_radius, start_t, length).cut(
            pivot_cylinder(3.05, start_t - 0.01, length + 0.02)
        )

    slot_nut = cq.Workplane("XY").box(23.0, 10.0, 5.0).val().translate(
        (support[0], support[1], phs_z + 44.0)
    )
    return {
        "stud": upright(3.0, 20.0, 28.0),
        # F12 is an existing 5 mm M6 nut. Cylinders bound nominal hex flats.
        "jam_nut": upright_ring(5.8, 30.0, 5.0),
        # SNTRCS6 is AF8, height 3 mm; circumradius is about 4.62 mm.
        "thin_nut": upright_ring(4.62, 35.0, 3.0),
        "outer_shims": upright_ring(6.0, 38.0, 1.0),
        "slot_nut_23x10x5_envelope": active.transform_upper_shape(slot_nut, pose),
        # MISUMI CB M6 head A=10 mm, E=6 mm; underhead L=55 mm.
        "bolt_head": pivot_cylinder(5.0, -32.0, 6.0),
        # OD6 is only a conservative clash envelope over the 31 mm
        # max-grip region. At least its final 5 mm may be thread/runout.
        "shank_outer_envelope": pivot_cylinder(3.0, -26.0, 31.0),
        "thread_under_nut": pivot_cylinder(3.0, 5.0, 5.0),
        "retaining_nut": pivot_ring(5.8, 5.0, 5.0),
        "thread_tail": pivot_cylinder(3.0, 10.0, 19.0),
        "eye_shims": pivot_ring(6.0, -6.0, 1.5),
    }


def screened_intersection_mm3(first, second) -> float:
    """Return true solid overlap, using bounding boxes only as a prefilter."""

    a = first.BoundingBox()
    b = second.BoundingBox()
    if (
        a.xmax < b.xmin or b.xmax < a.xmin
        or a.ymax < b.ymin or b.ymax < a.ymin
        or a.zmax < b.zmin or b.zmax < a.zmin
    ):
        return 0.0
    return first.intersect(second).Volume()


def _thin_spanner_corridors(pose, axis_index: int):
    """Four *assumed* 30×10×2.5 mm straight approach slabs.

    This is a gross volume availability probe only; it is not a wrench
    drawing, cannot establish engagement/torque, and omits the user's hand.
    """

    import cadquery as cq

    from cad import profile_radial_reve_actual_vendor as active

    support = active.revd_data.upper_support_points()[axis_index - 1]
    phs_z = active.revd_data.P.upper_ring_z_collapsed_mm
    rows = {}
    for label, dx, dy, length_x, length_y in (
        ("x_plus", 20.0, 0.0, 30.0, 10.0),
        ("x_minus", -20.0, 0.0, 30.0, 10.0),
        ("y_plus", 0.0, 20.0, 10.0, 30.0),
        ("y_minus", 0.0, -20.0, 10.0, 30.0),
    ):
        local = cq.Workplane("XY").box(length_x, length_y, 2.5).val().translate(
            (support[0] + dx, support[1] + dy, phs_z + 36.5)
        )
        rows[label] = active.transform_upper_shape(local, pose)
    return rows


def candidate_pose_screen(pose) -> dict:
    """Screen candidate solids against listed Rev E structures at one pose.

    Zero in this list cannot clear tolerances, fatigue, tool fit, stock
    variation, wiring, old invalid stops, or unlisted solid pairs.
    """

    import cadquery as cq

    from cad import profile_radial_reve_actual_vendor as active

    structures = {
        "upper_frame": active.transform_upper_frame_shape(active.group_shape("upper_frame"), pose),
        "upper_brackets": active.transform_upper_frame_shape(active.group_shape("upper_brackets"), pose),
        "lower_frame": active.group_shape("lower_frame"),
        "lower_brackets": active.group_shape("lower_brackets"),
        "lower_adapters": active.group_shape("lower_adapters"),
        "lower_joints": cq.Compound.makeCompound(list(active.lower_joint_shapes())),
    }
    actuators = {
        f"actuator_{axis}": cq.Compound.makeCompound(
            [part.shape for part in active.actuator_parts(axis, pose)]
        )
        for axis in (1, 2, 3)
    }
    solid_checks = []
    thin_spanner_approaches = []
    for axis in (1, 2, 3):
        solids = candidate_joint_solids(pose, axis)
        for part_name, part in solids.items():
            for target_name, target in structures.items():
                # These have a designed contact/slot passage, so even a
                # positive volume here is a model-fit warning, not a generic
                # frame clash verdict.
                mated = target_name == "upper_frame" and part_name in {
                    "stud", "slot_nut_23x10x5_envelope"
                }
                volume = screened_intersection_mm3(part, target)
                solid_checks.append({
                    "pair": f"A{axis}_{part_name}__{target_name}",
                    "classification": "mated_interface_envelope" if mated else "gross_structural",
                    "overlap_mm3": round(volume, 6),
                })
            if part_name in {"bolt_head", "retaining_nut", "thread_tail"}:
                for target_name, target in actuators.items():
                    volume = screened_intersection_mm3(part, target)
                    solid_checks.append({
                        "pair": f"A{axis}_{part_name}__{target_name}",
                        "classification": "eye_face_contact_or_clash" if (
                            part_name == "bolt_head" and target_name == f"actuator_{axis}"
                        ) else "gross_actuator",
                        "overlap_mm3": round(volume, 6),
                    })
        for direction, corridor in _thin_spanner_corridors(pose, axis).items():
            checks = {
                name: round(screened_intersection_mm3(corridor, target), 6)
                for name, target in {**structures, **actuators}.items()
            }
            thin_spanner_approaches.append({
                "axis": axis,
                "direction": direction,
                "blade_envelope_mm": [30.0, 10.0, 2.5],
                "largest_modeled_overlap_mm3": max(checks.values()),
                "overlaps_by_target_mm3": checks,
                "actual_wrench_fit_verified": False,
            })
    gross = [
        row["overlap_mm3"] for row in solid_checks
        if row["classification"].startswith("gross_")
    ]
    return {
        "pose": pose.label,
        "axis_count": 3,
        "solid_checks": solid_checks,
        "thin_spanner_approaches": thin_spanner_approaches,
        "max_gross_overlap_mm3": max(gross, default=0.0),
        "assembly_release": False,
        "screen_scope": "NOMINAL_LISTED_SOLIDS_AND_ASSUMED_2P5MM_SPANNER_CORRIDORS_ONLY",
    }


def candidate_grid_screen(poses=None, on_pose=None) -> dict:
    """Aggregate the 3×3×3 ordered workspace grid without release claims."""

    if poses is None:
        from cad.profile_radial_reve_actual_vendor import Pose

        poses = (
            Pose(f"Z{lift:g}_P{pitch:g}_R{roll:g}", lift, pitch, roll)
            for lift, pitch, roll in product(
                (0.0, 25.0, 50.0), (-3.0, 0.0, 3.0), (-3.0, 0.0, 3.0)
            )
        )
    rows = []
    for pose in poses:
        row = candidate_pose_screen(pose)
        rows.append(row)
        if on_pose is not None:
            on_pose(row)
    mated = [
        check["overlap_mm3"]
        for row in rows for check in row["solid_checks"]
        if check["classification"] == "mated_interface_envelope"
    ]
    eye_face = [
        check["overlap_mm3"]
        for row in rows for check in row["solid_checks"]
        if check["classification"] == "eye_face_contact_or_clash"
    ]
    gross = [row["max_gross_overlap_mm3"] for row in rows]
    blocked_tool = sum(
        approach["largest_modeled_overlap_mm3"] > 0.1
        for row in rows for approach in row["thin_spanner_approaches"]
    )
    return {
        "revision": "REVE_UPPER_JOINT_STOCK_CANDIDATES_REVIEW_ONLY_20261002",
        "pose_count": len(rows),
        "axes_per_pose": 3,
        "candidate_stud_stack": candidate_stud_stack(),
        "candidate_cb6_stack": candidate_cb6_stack(),
        "max_gross_overlap_mm3": max(gross, default=0.0),
        "max_mated_interface_overlap_mm3": max(mated, default=0.0),
        "max_eye_face_overlap_mm3": max(eye_face, default=0.0),
        "head_eye_contact_status": "HOLD_UNRESOLVED_REAL_BREP_OVERLAP",
        "pivot_fit_status": "REJECT_CB6_55_26MM_MIN_PLAIN_SHANK_LT_30P5MM_STACK",
        "blocked_assumed_thin_spanner_corridor_count": blocked_tool,
        "profile_slot_status": "MODEL_SECTION_MISMATCH_OLD_FUSION_VS_PUBLISHED_DNF3030",
        "profile_slot_note": (
            "Old Fusion upper_frame material starts about 6.9 mm inside the "
            "nominal lower face at the stud location, whereas the published "
            "DNF3030 slot floor is 10.5 mm deep. Its positive overlaps "
            "cannot establish collision of delivered supplier hardware."
        ),
        "tool_access_verified": False,
        "fit_tolerance_verified": False,
        "strength_verified": False,
        "assembly_release": False,
        "purchase_release": False,
        "fabrication_release": False,
        "rows": rows,
    }


def save_candidate_review(path: str | Path, review: dict) -> None:
    """Write a candidate-only JSON after enforcing three explicit no-release gates."""

    for gate in ("assembly_release", "purchase_release", "fabrication_release"):
        if review.get(gate) is not False:
            raise ValueError(f"{gate} must be explicitly false for candidate review")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def candidate_axis1_review_assembly():
    """One neutral-axis STEP source, including the known-wrong old slot.

    The included upper cross-member is *not* the published DNF3030 section;
    visual collisions there are deliberate model-mismatch evidence.
    """

    import cadquery as cq

    from cad import profile_radial_reve_actual_vendor as active

    pose = active.POSES["neutral"]
    assembly = cq.Assembly(name="A1_STOCK_CANDIDATES_OLD_SLOT_REVIEW_NOT_FOR_FABRICATION")
    names = {
        "stud": "A1_FABB6_28_FULL_THREAD_STUD",
        "jam_nut": "A1_F12_EXISTING_M6_JAM_NUT",
        "thin_nut": "A1_SNTRCS6_THIN_NUT",
        "outer_shims": "A1_CIMR6_12_0P5_TWO_SHIMS",
        "slot_nut_23x10x5_envelope": "A1_SP306_23X10X5_ENVELOPE",
        "bolt_head": "A1_CB6_55_HEAD",
        "shank_outer_envelope": "A1_CB6_55_OUTER_ENVELOPE_NOT_SMOOTH_SHANK_PROOF",
        "thread_under_nut": "A1_CB6_55_THREAD_UNDER_NUT",
        "retaining_nut": "A1_F10_EXISTING_M6_RETENTION_NUT",
        "thread_tail": "A1_CB6_55_THREAD_TAIL_19MM",
        "eye_shims": "A1_F09_THREE_EYE_SHIMS",
    }
    for key, shape in candidate_joint_solids(pose, 1).items():
        assembly.add(shape, name=names[key], color=cq.Color(0.78, 0.60, 0.15))

    crossbars = [
        shape for shape in active.group_shape("upper_frame").Solids()
        if shape.BoundingBox().ymin < 250.0 < shape.BoundingBox().ymax
        and shape.BoundingBox().xmin < 0.0 < shape.BoundingBox().xmax
    ]
    if len(crossbars) != 1:
        raise ValueError(f"Expected one old A1 upper cross-member, got {len(crossbars)}")
    assembly.add(
        active.transform_upper_frame_shape(crossbars[0], pose),
        name="A1_OLD_UPPER_CROSSBAR_SECTION_MODEL_MISMATCH",
        color=cq.Color(0.25, 0.25, 0.25),
    )
    assembly.add(
        active.transform_upper_shape(active.upper_joint_local_shapes()[0], pose),
        name="A1_PHS6_SUPPLIER_ENVELOPE_NOT_EXACT_CAD",
        color=cq.Color(0.30, 0.52, 0.70),
    )
    vendor_eye = [
        part.shape for part in active.actuator_parts(1, pose)
        if "_NEIGUAN_" in part.name
    ]
    if len(vendor_eye) != 1:
        raise ValueError(f"Expected one A1 moving actuator STEP solid, got {len(vendor_eye)}")
    assembly.add(
        vendor_eye[0],
        name="A1_VENDOR_NEIGUAN_WITH_REAL_EYE",
        color=cq.Color(0.75, 0.77, 0.79),
    )
    return assembly
