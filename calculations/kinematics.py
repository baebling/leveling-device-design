from dataclasses import asdict
from itertools import product
from math import sqrt

from cad.assembly import actuator_lengths
from cad.parameters import P, Pose


def pose_grid(angle_deg=None):
    a = P.recommended_angle_deg if angle_deg is None else float(angle_deg)
    for lift, pitch, roll in product((0.0, P.target_lift_mm), (-a, 0.0, a), (-a, 0.0, a)):
        yield Pose(lift, pitch, roll, True, f"z{lift:g}_p{pitch:g}_r{roll:g}")


def evaluate_grid(angle_deg=None):
    rows = []
    for pose in pose_grid(angle_deg):
        lengths = actuator_lengths(pose)
        rows.append({
            **asdict(pose),
            "a1_mm": lengths[0], "a2_mm": lengths[1], "a3_mm": lengths[2],
            "min_mm": min(lengths), "max_mm": max(lengths),
        })
    return rows


def summary(angle_deg=None):
    rows = evaluate_grid(angle_deg)
    values = [r[key] for r in rows for key in ("a1_mm", "a2_mm", "a3_mm")]
    min_len, max_len = min(values), max(values)
    return {
        "angle_deg": P.recommended_angle_deg if angle_deg is None else float(angle_deg),
        "minimum_length_mm": min_len,
        "maximum_length_mm": max_len,
        "required_span_mm": max_len - min_len,
        "retracted_margin_mm": min_len - P.actuator_retracted_mm,
        "extended_margin_mm": P.actuator_extended_mm - max_len,
        "passes_commercial_actuator": (
            min_len >= P.actuator_retracted_mm + P.actuator_min_end_margin_mm
            and max_len <= P.actuator_extended_mm - P.actuator_min_end_margin_mm
        ),
    }


def platform_corner_heights(pose):
    from cad.common import platform_center_z, transform_point
    zc = platform_center_z(pose)
    corners = []
    for x in (-P.platform_length_mm / 2, P.platform_length_mm / 2):
        for y in (-P.platform_width_mm / 2, P.platform_width_mm / 2):
            corners.append(transform_point((x, y, P.module_top_above_joint_mm), pose, zc).z)
    return corners
