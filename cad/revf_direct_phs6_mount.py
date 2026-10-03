"""Direct-M6 PHS6 mounting review for the Rev F self-weight PoC.

This candidate removes the machined housing pocket and the split keyhole
backup.  One axisymmetric PHS6 female shank is clamped directly to one simple
plate with a MISUMI CBS6-12 low-head screw.  The same plate is rotated during
assembly for A1/A2/A3, so only one custom upper-part SKU is required.

Status is a conditional prototype-order recommendation, not certification or
approval for a cart, payload, person, fatigue, stall loading, or field use.
"""

from __future__ import annotations

from functools import lru_cache
from itertools import combinations, product
import json
from math import pi, radians, sin
from pathlib import Path

import cadquery as cq

from cad.profile_radial_reve_actual_vendor import (
    Pose,
    actuator_parts,
    group_shape,
    transform_upper_frame_shape,
)
from cad.profile_radial_revf_upper_pocket_review import (
    _place,
    joint_reference,
    phs_components,
)
from cad.revf_quote_package import _mount_rotation_deg
from cad.revf_upper_pocket_inputs import load_inputs
from cad.revf_upper_pocket_pose_audit import audit_pose


DIRECT_MOUNT_SPEC = {
    "prototype_order_recommendation": "CONDITIONAL GO",
    "formal_purchase_release": False,
    "scope": "supervised indoor self-weight PoC; no cart, payload, or person",
    "custom_part_types": 1,
    "order_quantity": 3,
    "material": "A6061-T6 or A6061P-T651",
    "length_mm": 60.0,
    "width_mm": 30.0,
    "thickness_mm": 9.0,
    "mount_pitch_mm": 44.0,
    "mount_hole_diameter_mm": 6.6,
    "centre_hole_diameter_mm": 6.6,
    "counterbore_diameter_mm": 11.0,
    "counterbore_depth_mm": 4.5,
    "centre_fastener": "MISUMI CBS6-12; M6x12; SCM435; strength class 10.9",
    "centre_fastener_quantity": 3,
    "phs6_thread": "M6 x 1.0, blind depth 12 mm",
    "phs6_ball_centre_to_mount_face_mm": 30.0,
    "assembly_torque_screen_nm": 4.0,
    "medium_threadlocker": "Loctite 243 class or equivalent",
    "required_articulation_limit_deg": 13.0,
    "review_force_per_axis_n": 750.0,
}


def _box(x: float, y: float, z: float, centre) -> cq.Shape:
    return cq.Workplane("XY").box(x, y, z).val().translate(centre)


def _cylinder(radius: float, length: float, start, direction=(0, 0, 1)) -> cq.Shape:
    return cq.Solid.makeCylinder(radius, length, cq.Vector(*start), cq.Vector(*direction))


def build_direct_mount_plate() -> cq.Shape:
    """One 60x30x9 plate; local ball centre is z=0 and mount face z=39."""
    d = DIRECT_MOUNT_SPEC
    plate = _box(d["length_mm"], d["width_mm"], d["thickness_mm"], (0, 0, 34.5))
    for x in (-d["mount_pitch_mm"] / 2, d["mount_pitch_mm"] / 2):
        plate = plate.cut(_cylinder(d["mount_hole_diameter_mm"] / 2, 11, (x, 0, 29)))
    plate = plate.cut(_cylinder(d["centre_hole_diameter_mm"] / 2, 11, (0, 0, 29)))
    plate = plate.cut(
        _cylinder(
            d["counterbore_diameter_mm"] / 2,
            d["counterbore_depth_mm"],
            (0, 0, 39 - d["counterbore_depth_mm"]),
        )
    )
    return plate.clean()


def m6_stack_screen() -> dict:
    """Length-only fit screen for CBS6-12 and the TRUSCO 12 mm blind thread."""
    plate_web = DIRECT_MOUNT_SPEC["thickness_mm"] - DIRECT_MOUNT_SPEC["counterbore_depth_mm"]
    length_bounds = (11.65, 12.35)
    engagement = (length_bounds[0] - plate_web, length_bounds[1] - plate_web)
    clearance = (12.0 - engagement[1], 12.0 - engagement[0])
    return {
        "bolt_length_bounds_mm": list(length_bounds),
        "plate_web_mm": plate_web,
        "engagement_bounds_mm": [round(value, 2) for value in engagement],
        "blind_bottom_clearance_bounds_mm": [round(value, 2) for value in clearance],
        "minimum_engagement_diameters": engagement[0] / 6.0,
        # MISUMI CBS M6 head E=4 mm; the 4.5 mm recess leaves 0.5 mm.
        "head_height_mm": 4.0,
        "head_flush_margin_mm": DIRECT_MOUNT_SPEC["counterbore_depth_mm"] - 4.0,
        "fit_screen_pass": engagement[0] >= 6.0 and clearance[0] >= 2.0,
        "thread_material_and_stripping_capacity_verified": False,
    }


def _annular_mean_radius_mm(outer_radius: float, inner_radius: float) -> float:
    return (2.0 / 3.0) * (outer_radius**3 - inner_radius**3) / (
        outer_radius**2 - inner_radius**2
    )


@lru_cache(maxsize=1)
def required_articulation_deg() -> float:
    inputs = load_inputs()
    poses = (
        Pose(f"required_{index}", lift, pitch, roll)
        for index, (lift, pitch, roll) in enumerate(
            product((0.0, 25.0, 50.0), (-3.0, 0.0, 3.0), (-3.0, 0.0, 3.0))
        )
    )
    return max(max(audit_pose(pose, inputs)["articulation_deg"]) for pose in poses)


def direct_mount_static_screen(force_n: float = 750.0) -> dict:
    """Conservative hand screen; supplier PHS6 thread proof remains open."""
    if force_n <= 0:
        raise ValueError("positive force magnitude required")
    d = DIRECT_MOUNT_SPEC
    tensile_area_mm2 = 20.1  # ISO metric M6 coarse tensile-stress area.
    articulation = required_articulation_deg()
    lateral = force_n * sin(radians(articulation))
    overturn = lateral * d["phs6_ball_centre_to_mount_face_mm"] / 1000.0

    # Low-preload bound uses the low assembly torque and adverse K=0.25.
    minimum_preload = d["assembly_torque_screen_nm"] / (0.25 * 0.006)
    foot_radius = _annular_mean_radius_mm(6.5, 3.3)
    head_radius = _annular_mean_radius_mm(5.0, 3.3)
    friction_capacity = 0.10 * minimum_preload * (foot_radius + head_radius) / 1000.0
    total_bolt_stress = (minimum_preload + force_n) / tensile_area_mm2

    plate_section_modulus = 30.0 * 9.0**2 / 6.0
    plate_moment_nmm = force_n * 44.0 / 4.0
    plate_bending = plate_moment_nmm / plate_section_modulus
    head_bearing_area = pi * (11.0**2 - 6.6**2) / 4.0
    foot_bearing_area = pi * (13.0**2 - 6.6**2) / 4.0
    head_bearing = (minimum_preload + force_n) / head_bearing_area
    foot_bearing = minimum_preload / foot_bearing_area

    screen = {
        "force_n": force_n,
        "required_articulation_deg": articulation,
        "lateral_force_at_required_articulation_n": lateral,
        "overturning_moment_nm": overturn,
        "external_axial_stress_mpa": force_n / tensile_area_mm2,
        "minimum_preload_n": minimum_preload,
        "separation_margin": minimum_preload / force_n,
        "friction_moment_capacity_nm": friction_capacity,
        "friction_moment_margin_at_required_articulation": friction_capacity / overturn,
        "combined_preload_plus_external_stress_mpa": total_bolt_stress,
        "bolt_proof_stress_mpa": 830.0,
        "bolt_proof_margin": 830.0 / total_bolt_stress,
        "plate_bending_stress_mpa": plate_bending,
        "plate_yield_screen_mpa": 240.0,
        "plate_yield_margin": 240.0 / plate_bending,
        "counterbore_floor_bearing_mpa": head_bearing,
        "phs6_foot_bearing_mpa": foot_bearing,
        "m6_stack": m6_stack_screen(),
        "supplier_thread_capacity_verified": False,
        "profile_tnut_capacity_verified": False,
        "purchase_release": False,
    }
    screen["conditional_geometry_screen_pass"] = bool(
        screen["friction_moment_margin_at_required_articulation"] >= 1.5
        and screen["bolt_proof_margin"] >= 1.5
        and screen["plate_yield_margin"] >= 1.5
        and screen["m6_stack"]["fit_screen_pass"]
    )
    return screen


def placed_direct_mount_plate(axis_index: int, pose: Pose) -> cq.Shape:
    """Place the identical SKU at one axis; assembly rotation is not a new part."""
    if axis_index not in (1, 2, 3):
        raise ValueError("axis_index must be 1, 2, or 3")
    local = build_direct_mount_plate().rotate(
        (0, 0, 0), (0, 0, 1), _mount_rotation_deg(axis_index)
    )
    return _place(local, axis_index, pose)


def _broad_overlap(first: cq.Shape, second: cq.Shape, tolerance=1e-7) -> bool:
    a, b = first.BoundingBox(), second.BoundingBox()
    return not (
        a.xmax < b.xmin - tolerance
        or b.xmax < a.xmin - tolerance
        or a.ymax < b.ymin - tolerance
        or b.ymax < a.ymin - tolerance
        or a.zmax < b.zmin - tolerance
        or b.zmax < a.zmin - tolerance
    )


def _intersection(first: cq.Shape, second: cq.Shape) -> dict:
    if not _broad_overlap(first, second):
        return {"valid": True, "volume_mm3": 0.0}
    try:
        common = first.intersect(second)
        volume = float(common.Volume())
        return {
            "valid": bool(first.isValid() and second.isValid() and common.isValid() and volume >= -1e-8),
            "volume_mm3": max(0.0, volume),
        }
    except Exception as error:
        return {"valid": False, "volume_mm3": None, "error": str(error)}


@lru_cache(maxsize=1)
def audit_direct_mount_poses() -> tuple[dict, ...]:
    """Audit the 27 required Z/pitch/roll corner and centre combinations."""
    inputs = load_inputs()
    rows = []
    for index, (lift, pitch, roll) in enumerate(
        product((0.0, 25.0, 50.0), (-3.0, 0.0, 3.0), (-3.0, 0.0, 3.0))
    ):
        pose = Pose(f"direct_{index}", lift, pitch, roll)
        plates = [placed_direct_mount_plate(axis, pose) for axis in (1, 2, 3)]
        frame = transform_upper_frame_shape(group_shape("upper_frame"), pose)
        frame_brackets = transform_upper_frame_shape(group_shape("upper_brackets"), pose)
        lower = cq.Compound.makeCompound(
            [group_shape(name) for name in ("lower_frame", "lower_brackets", "lower_adapters")]
        )
        actuators = cq.Compound.makeCompound(
            [part.shape for axis in (1, 2, 3) for part in actuator_parts(axis, pose)]
        )
        measurements = []
        for axis, plate in enumerate(plates, 1):
            housing = phs_components(axis, pose)["housing"]
            for label, obstacle in (
                ("upper_frame_surface_contact", frame),
                ("upper_frame_brackets", frame_brackets),
                ("phs6_foot_surface_contact", housing),
                ("actuators", actuators),
                ("lower_structure", lower),
            ):
                measured = _intersection(plate, obstacle)
                measured.update(pair=[f"A{axis}_direct_plate", label])
                measurements.append(measured)
        for first, second in combinations(range(3), 2):
            measured = _intersection(plates[first], plates[second])
            measured.update(pair=[f"A{first + 1}_direct_plate", f"A{second + 1}_direct_plate"])
            measurements.append(measured)

        kinematic = audit_pose(pose, inputs)
        valid = all(row["valid"] for row in measurements)
        positive = [row["volume_mm3"] for row in measurements if row["volume_mm3"] is not None]
        rows.append(
            {
                "pose": {"lift_mm": lift, "pitch_deg": pitch, "roll_deg": roll},
                "same_plate_sku_all_axes": True,
                "boolean_valid": valid,
                "unexpected_interference_mm3": max(positive, default=0.0),
                "maximum_articulation_deg": max(kinematic["articulation_deg"]),
                "actuator_lengths_mm": kinematic["pin_lengths_mm"],
                "actuator_length_window_pass": kinematic["normal_window_pass"],
                "measurements": measurements,
            }
        )
    return tuple(rows)


def build_review() -> dict:
    rows = audit_direct_mount_poses()
    screen = direct_mount_static_screen()
    return {
        "status": "CONDITIONAL GO FOR SELF-WEIGHT POC CUSTOM-PLATE QUOTATION",
        "formal_purchase_release": False,
        "one_custom_plate_sku": True,
        "custom_plate_quantity": 3,
        "centre_fastener_quantity": 3,
        "spec": DIRECT_MOUNT_SPEC,
        "m6_stack": m6_stack_screen(),
        "static_screen": screen,
        "pose_count": len(rows),
        "all_pose_booleans_valid": all(row["boolean_valid"] for row in rows),
        "maximum_unexpected_interference_mm3": max(row["unexpected_interference_mm3"] for row in rows),
        "maximum_articulation_deg": max(row["maximum_articulation_deg"] for row in rows),
        "minimum_actuator_length_mm": min(min(row["actuator_lengths_mm"]) for row in rows),
        "maximum_actuator_length_mm": max(max(row["actuator_lengths_mm"]) for row in rows),
        "all_actuator_lengths_in_normal_window": all(row["actuator_length_window_pass"] for row in rows),
        "poses": rows,
        "remaining_gates": [
            "TRUSCO PHS6 female-thread material/proof and permitted tightening torque are not published in the checked drawing.",
            "Delivered 3030 profile slot and T-nut pullout/slip capacity remain unverified.",
            "Hold PHS6 orientation while tightening CBS6-12; apply medium threadlocker and witness mark.",
            "After assembly, perform unloaded hand/jog sweep before motor-powered automatic levelling.",
        ],
    }


def export_direct_mount_review(output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    step_dir = output_dir / "step"
    step_dir.mkdir(exist_ok=True)
    plate_step = step_dir / "UPPER_PHS6_DIRECT_MOUNT_PLATE_A6061_60x30x9_QTY3.step"
    cq.exporters.export(build_direct_mount_plate(), str(plate_step))

    collapsed = Pose("collapsed", 0.0, 0.0, 0.0)
    three_axis = cq.Compound.makeCompound(
        [placed_direct_mount_plate(axis, collapsed) for axis in (1, 2, 3)]
    )
    assembly_step = step_dir / "UPPER_PHS6_DIRECT_MOUNT_THREE_AXIS_REVIEW.step"
    cq.exporters.export(three_axis, str(assembly_step))

    report = build_review()
    audit_json = output_dir / "direct_mount_audit.json"
    audit_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    readme = output_dir / "README_DIRECT_MOUNT_REVIEW.md"
    readme.write_text(
        "# PHS6 중앙 M6 직접체결 검토\n\n"
        "**결론: 감독하 실내 자중 시연용 시제품에 한해 CONDITIONAL GO.**\n\n"
        "- 맞춤 상부 부품은 동일한 A6061 60×30×9 판 1종이며 **3개** 주문한다.\n"
        "- 중앙 체결은 MISUMI **CBS6-12** 3개를 사용한다. M6×12, SCM435, 강도구분 10.9 후보다.\n"
        "- 프로파일 체결 Ø6.6 관통 2개(피치 44), 중앙 Ø6.6 관통 및 상면 Ø11×4.5 카운터보어다.\n"
        "- PHS6는 판에 먼저 조립한다. 4 N·m 저토크 검토값, 중강도 나사고정제, 체결 확인선을 사용한다.\n"
        "- 키홀 지지판과 U볼트는 사용하지 않는다. 그리스 니플과 베어링 외통은 완전히 개방된다.\n\n"
        "## 제한\n\n"
        "이 판단은 750 N/축, Z 0–50 mm, 동시 pitch/roll ±3°, 카트·적재물·사람 없는 자중 PoC에만 해당한다. "
        "PHS6 암나사 재질·허용 체결토크와 실제 프로파일 T너트 용량은 공개 도면에서 확인되지 않았다. "
        "따라서 인증·피로·스톨·사람 탑승 적합성 또는 정식 구매승인을 의미하지 않는다.\n",
        encoding="utf-8",
    )
    return {
        "plate_step": plate_step,
        "assembly_step": assembly_step,
        "audit_json": audit_json,
        "readme": readme,
    }

