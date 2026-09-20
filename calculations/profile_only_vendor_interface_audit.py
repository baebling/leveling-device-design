"""Audit the Rev A profile-only model against published vendor dimensions.

This is a release-gate calculation, not a replacement CAD model.  It records
where the current model disagrees with dimensions visible in the product
drawings so that an old STEP package cannot be mistaken for fabrication data.
"""

from __future__ import annotations

import json
from math import fmod
from pathlib import Path

from cad.minimal_profile_only_assembly import M, lower_tangent_rail_data


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = (
    ROOT
    / "outputs"
    / "minimal_profile_only_revA"
    / "verification"
    / "vendor_interface_audit_2026-08-31.json"
)


VENDOR = {
    "lmb10": {
        "overall_length_mm": 56.0,
        "overall_width_mm": 26.0,
        "overall_height_mm": 44.0,
        "inside_width_mm": 20.0,
        "pin_center_height_mm": 36.0,
        "plate_thickness_mm": 3.0,
        "pivot_bore_mm": 6.2,
        "mount_feature_diameter_mm": 8.0,
        "mount_feature_spacing_mm": 36.0,
        "mount_features": "one round hole and one open U-slot",
    },
    "phs6": {
        "overall_length_mm": 39.0,
        "head_diameter_mm": 18.0,
        "head_width_mm": 9.0,
        "ring_bore_mm": 6.0,
        "ring_width_mm": 6.75,
        "thread": "M6x1",
        "ring_center_to_thread_end_mm": 30.0,
        "female_thread_effective_depth_mm": 14.0,
        "jam_nut_height_mm": 5.0,
        "tilt_alpha1_deg": 8.0,
        "tilt_alpha2_deg": 13.0,
        "tilt_alpha3_deg": 30.0,
        "static_radial_load_n": 6860.0,
    },
    "dnf4040": {
        "size_mm": 40.0,
        "slot_opening_mm": 8.3,
        "slot_internal_width_mm": 20.5,
        "slot_depth_mm": 13.0,
        "slot_lip_mm": 4.5,
        "center_bore_mm": 6.8,
        "center_tap": "M8",
    },
    "dnf3030": {
        "size_mm": 30.0,
        "slot_opening_mm": 6.3,
        "slot_internal_width_mm": 10.2,
        "slot_depth_mm": 6.2,
        "slot_lip_mm": 2.5,
        "center_bore_mm": 5.0,
    },
    "lm4075oe_1075": {
        "retracted_pin_center_mm_at_100_stroke": 205.0,
        "extended_pin_center_mm_at_100_stroke": 305.0,
        "end_bore_mm": 6.4,
        "rod_diameter_mm": 20.0,
        "housing_width_mm": 40.0,
        "housing_height_mm": 75.0,
        "eye_width_mm": None,
    },
}


def acute_line_angle_deg(a_deg: float, b_deg: float) -> float:
    """Return the acute angle between two unoriented lines."""
    delta = abs(fmod(a_deg - b_deg, 180.0))
    if delta > 90.0:
        delta = 180.0 - delta
    return delta


def connector_audit() -> list[dict]:
    inner_boundary = M.outer_width_mm / 2.0 - M.lower_profile_mm
    rows = []
    for rail in lower_tangent_rail_data():
        for endpoint_index, endpoint in enumerate((rail["start"], rail["end"]), start=1):
            x, y = endpoint
            if abs(abs(x) - inner_boundary) < 1e-3:
                outer_member_axis_deg = 90.0
                boundary = "X side member"
            elif abs(abs(y) - inner_boundary) < 1e-3:
                outer_member_axis_deg = 0.0
                boundary = "Y cross member"
            else:
                raise AssertionError(f"Rail endpoint is not on the frame boundary: {endpoint}")
            joint_angle = acute_line_angle_deg(rail["angle_deg"], outer_member_axis_deg)
            rows.append(
                {
                    "rail": f"A{rail['index']}",
                    "endpoint": endpoint_index,
                    "boundary": boundary,
                    "rail_axis_deg": round(rail["angle_deg"], 6),
                    "outer_member_axis_deg": outer_member_axis_deg,
                    "actual_joint_angle_deg": round(joint_angle, 6),
                    "4035_requires_deg": 90.0,
                    "passes_4035": abs(joint_angle - 90.0) < 1e-6,
                }
            )
    return rows


def pivot_bolt_stack_audit(eye_width_mm: float = 18.0) -> dict:
    """Screen an ISO 4014 M6x50 pivot using the unverified eye width note."""
    bolt_length = 50.0
    thread_length = 18.0
    plain_shank = bolt_length - thread_length
    phs_head_width = VENDOR["phs6"]["head_width_mm"]
    washer_total = 2.0 * 1.6
    grip_without_shims = eye_width_mm + phs_head_width + washer_total
    required_shim = max(0.0, plain_shank - grip_without_shims)
    return {
        "status": "CONDITIONAL_EYE_WIDTH_NOT_PUBLISHED",
        "bolt": "ISO 4014 M6x50 property class 8.8",
        "plain_shank_mm": plain_shank,
        "assumed_eye_width_mm": eye_width_mm,
        "phs6_head_width_mm": phs_head_width,
        "two_washers_total_mm": washer_total,
        "grip_without_shims_mm": grip_without_shims,
        "minimum_total_shim_to_reach_thread_mm": round(required_shim, 3),
        "recommended_trial_total_shim_mm": 2.0,
        "note": "Do not release until the delivered actuator eye width is measured.",
    }


def build_audit() -> dict:
    phs_required_offset = (
        VENDOR["phs6"]["ring_center_to_thread_end_mm"]
        + VENDOR["phs6"]["jam_nut_height_mm"]
    )
    connector_rows = connector_audit()
    failed_connector_rows = [row for row in connector_rows if not row["passes_4035"]]
    release_blockers = [
        "LMB-10 side mounting cannot place its two 36 mm-spaced base features in one 4040 side slot.",
        "A2/A3 oblique lower rails form 30/60 degree joints; the selected 4035 connector is 90 degree only.",
        "The CAD places the PHS6 center only 20 mm below the profile bottom; the published 30 mm body plus 5 mm jam nut requires at least 35 mm.",
        "The 297 mm lower rails are not an orderable fixed length in the selected NAVIMRO DNF4040 rows; 300 mm would intersect the current boundary unless geometry changes.",
        "LM4075OE eye axial width is not dimensioned in the published drawing and no matching vendor STEP is present.",
    ]
    return {
        "design": "Minimal 3-RPS Profile-Only Rev A",
        "audit_date": "2026-08-31",
        "fabrication_release": False,
        "status": "BLOCKED_VENDOR_INTERFACE_MISMATCH",
        "published_dimensions": VENDOR,
        "lmb10_mount": {
            "status": "FAIL_CURRENT_CAD",
            "base_feature_spacing_mm": VENDOR["lmb10"]["mount_feature_spacing_mm"],
            "4040_side_slot_opening_mm": VENDOR["dnf4040"]["slot_opening_mm"],
            "top_mount_line_to_current_tangent_slot_deg": 90.0,
            "side_mount_feature_line": "vertical",
            "current_single_side_slot_feature_line": "along extrusion at one fixed height",
        },
        "lower_connector_joints": connector_rows,
        "failed_4035_joint_count": len(failed_connector_rows),
        "phs6_vertical_stack": {
            "status": "FAIL_CURRENT_CAD",
            "cad_profile_bottom_to_ring_center_mm": M.upper_frame_bottom_local_z_mm,
            "published_ring_center_to_thread_end_mm": VENDOR["phs6"][
                "ring_center_to_thread_end_mm"
            ],
            "jam_nut_height_mm": VENDOR["phs6"]["jam_nut_height_mm"],
            "minimum_profile_bottom_to_ring_center_mm": phs_required_offset,
            "cad_shortfall_mm": phs_required_offset - M.upper_frame_bottom_local_z_mm,
        },
        "upper_stud_candidate": {
            "status": "GEOMETRIC_SCREEN_PASS_PHYSICAL_TRIAL_REQUIRED",
            "spring_nut": "NAVIMRO SP306 / K14671215 / 30-series M6 / 23x10x5 mm",
            "set_screw": "NAVIMRO K47053034 / M6x30 / 25 pack",
            "phs6_target_thread_engagement_mm": 12.0,
            "phs6_effective_thread_depth_mm": 14.0,
            "note": "Confirm actual spring-nut seating and jam-nut wrench clearance on one axis.",
        },
        "upper_pivot_bolt": pivot_bolt_stack_audit(),
        "profile_and_connector_bom_corrections": {
            "4040_700": "K92787708",
            "4040_620": "K92787705",
            "4040_300": "K92787692",
            "3030_700": "K42296106",
            "3030_640": "K42296071",
            "4035_connector": "K92782553; two M8 bolt/nut sets per connector",
            "dcb3025_connector": "K56842696; two M6 bolt/nut sets per connector",
            "sp306_m6_spring_nut": "K14671215; 100 pack",
            "sp408_m8_spring_nut": "K14671419; 100 pack",
        },
        "release_blockers": release_blockers,
    }


def main() -> None:
    audit = build_audit()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
