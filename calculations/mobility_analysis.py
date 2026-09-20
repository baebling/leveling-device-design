from itertools import product
from math import acos, cos, degrees, radians, sin, sqrt

import numpy as np

from cad.assembly import actuator_lengths
from cad.common import platform_center_z, transform_point
from cad.parameters import P, Pose
from cad import guide_mechanism


LIFT_GRID_MM = tuple(float(v) for v in range(0, int(P.target_lift_mm) + 1, 10))
ANGLE_CASES_DEG = (3.0, 5.0, 8.0)


def rotation_matrix(pitch_deg, roll_deg):
    """Same extrinsic X(roll), then Y(pitch) convention as cad.common."""
    cr, sr = cos(radians(roll_deg)), sin(radians(roll_deg))
    cp, sp = cos(radians(pitch_deg)), sin(radians(pitch_deg))
    rx = np.array([
        [1.0, 0.0, 0.0],
        [0.0, cr, -sr],
        [0.0, sr, cr],
    ])
    ry = np.array([
        [cp, 0.0, sp],
        [0.0, 1.0, 0.0],
        [-sp, 0.0, cp],
    ])
    return ry @ rx


def unit(vector):
    vector = np.array(vector, dtype=float)
    norm = np.linalg.norm(vector)
    if norm <= 1e-12:
        raise ValueError("zero-length vector")
    return vector / norm


def angle_between_deg(a, b):
    dot = float(np.clip(np.dot(unit(a), unit(b)), -1.0, 1.0))
    return degrees(acos(dot))


def actuator_axis_data(pose):
    platform_z = platform_center_z(pose)
    rows = []
    rot = rotation_matrix(pose.pitch_deg, pose.roll_deg)
    inv_rot = rot.T
    for idx, ((top_x, top_y), (base_x, base_y)) in enumerate(zip(P.support_points_xy, P.base_points_xy), start=1):
        top = transform_point((top_x, top_y, 0.0), pose, platform_z)
        top_np = np.array([top.x, top.y, top.z])
        base_np = np.array([base_x, base_y, P.base_joint_z_mm], dtype=float)
        axis_base = unit(top_np - base_np)
        axis_upper_local = unit(inv_rot @ (base_np - top_np))
        rows.append({
            "actuator": idx,
            "axis_base": axis_base,
            "axis_upper_local": axis_upper_local,
        })
    return rows


def reference_axis_data():
    return actuator_axis_data(Pose(50.0, 0.0, 0.0, True, "neutral_reference"))


def joint_articulation_summary(angle_deg):
    reference = reference_axis_data()
    rows = []
    for lift, pitch, roll in product(LIFT_GRID_MM, (-angle_deg, 0.0, angle_deg), (-angle_deg, 0.0, angle_deg)):
        pose = Pose(lift, pitch, roll, True, "joint_sweep")
        for current, ref in zip(actuator_axis_data(pose), reference):
            lower_angle = angle_between_deg(current["axis_base"], ref["axis_base"])
            upper_angle = angle_between_deg(current["axis_upper_local"], ref["axis_upper_local"])
            rows.append({
                "lift_mm": lift,
                "pitch_deg": pitch,
                "roll_deg": roll,
                "actuator": current["actuator"],
                "lower_joint_deviation_deg": lower_angle,
                "upper_joint_deviation_deg": upper_angle,
            })
    worst_lower = max(rows, key=lambda row: row["lower_joint_deviation_deg"])
    worst_upper = max(rows, key=lambda row: row["upper_joint_deviation_deg"])
    return {
        "angle_case_deg": angle_deg,
        "maximum_lower_joint_deviation_deg": worst_lower["lower_joint_deviation_deg"],
        "worst_lower_pose": worst_lower,
        "maximum_upper_joint_deviation_deg": worst_upper["upper_joint_deviation_deg"],
        "worst_upper_pose": worst_upper,
    }


def cardan_tilt_deg(pitch_deg, roll_deg):
    normal = rotation_matrix(pitch_deg, roll_deg) @ np.array([0.0, 0.0, 1.0])
    return angle_between_deg(normal, np.array([0.0, 0.0, 1.0]))


def cardan_summary(angle_deg):
    rows = []
    for pitch, roll in product((-angle_deg, 0.0, angle_deg), repeat=2):
        rows.append({
            "pitch_deg": pitch,
            "roll_deg": roll,
            "cardan_tilt_deg": cardan_tilt_deg(pitch, roll),
        })
    worst = max(rows, key=lambda row: row["cardan_tilt_deg"])
    return {
        "angle_case_deg": angle_deg,
        "maximum_cardan_tilt_deg": worst["cardan_tilt_deg"],
        "worst_pose": worst,
        "passes_current_design_angle": worst["cardan_tilt_deg"] <= P.cardan_design_angle_deg,
        "passes_current_hard_stop": worst["cardan_tilt_deg"] <= P.cardan_hard_stop_angle_deg,
    }


def actuator_jacobian(pose):
    base_lengths = np.array(actuator_lengths(pose), dtype=float)
    deltas = (
        ("lift", 0.1),
        ("pitch_rad", 1e-4),
        ("roll_rad", 1e-4),
    )
    columns = []
    for name, delta in deltas:
        if name == "lift":
            plus = Pose(pose.lift_mm + delta, pose.pitch_deg, pose.roll_deg, True, "jac_plus")
            minus = Pose(pose.lift_mm - delta, pose.pitch_deg, pose.roll_deg, True, "jac_minus")
        elif name == "pitch_rad":
            d = degrees(delta)
            plus = Pose(pose.lift_mm, pose.pitch_deg + d, pose.roll_deg, True, "jac_plus")
            minus = Pose(pose.lift_mm, pose.pitch_deg - d, pose.roll_deg, True, "jac_minus")
        else:
            d = degrees(delta)
            plus = Pose(pose.lift_mm, pose.pitch_deg, pose.roll_deg + d, True, "jac_plus")
            minus = Pose(pose.lift_mm, pose.pitch_deg, pose.roll_deg - d, True, "jac_minus")
        columns.append((np.array(actuator_lengths(plus)) - np.array(actuator_lengths(minus))) / (2.0 * delta))
    jac = np.column_stack(columns)
    # Keep a reference to the nominal value to make debugging easier.
    return jac, base_lengths


def jacobian_summary(angle_deg):
    rows = []
    for lift, pitch, roll in product(LIFT_GRID_MM, (-angle_deg, 0.0, angle_deg), (-angle_deg, 0.0, angle_deg)):
        pose = Pose(lift, pitch, roll, True, "jacobian_sweep")
        jac, lengths = actuator_jacobian(pose)
        singular_values = np.linalg.svd(jac, compute_uv=False)
        normalized_jac = jac.copy()
        normalized_jac[:, 1:] = normalized_jac[:, 1:] / P.support_radius_mm
        normalized_singular_values = np.linalg.svd(normalized_jac, compute_uv=False)
        rows.append({
            "lift_mm": lift,
            "pitch_deg": pitch,
            "roll_deg": roll,
            "rank": int(np.linalg.matrix_rank(jac, tol=1e-6)),
            "condition_number": float(singular_values[0] / singular_values[-1]),
            "normalized_condition_number": float(normalized_singular_values[0] / normalized_singular_values[-1]),
            "minimum_singular_value": float(singular_values[-1]),
            "lengths_mm": tuple(float(v) for v in lengths),
        })
    worst_condition = max(rows, key=lambda row: row["condition_number"])
    worst_rank = min(rows, key=lambda row: row["rank"])
    return {
        "angle_case_deg": angle_deg,
        "minimum_rank": worst_rank["rank"],
        "worst_rank_pose": worst_rank,
        "maximum_condition_number": worst_condition["condition_number"],
        "maximum_normalized_condition_number": max(row["normalized_condition_number"] for row in rows),
        "worst_condition_pose": worst_condition,
    }


def central_guide_constraint_summary():
    # Platform twist variables: tx, ty, tz, rx, ry, rz.
    with_cardan = np.array([
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],  # tx = 0
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0],  # ty = 0
        [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],  # yaw rz = 0
    ])
    rigid_keyed_slide = np.array([
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],  # tx = 0
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0],  # ty = 0
        [0.0, 0.0, 0.0, 1.0, 0.0, 0.0],  # roll rx = 0
        [0.0, 0.0, 0.0, 0.0, 1.0, 0.0],  # pitch ry = 0
        [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],  # yaw rz = 0
    ])
    return {
        "with_yaw_transmitting_2axis_cardan": {
            "constraint_rank": int(np.linalg.matrix_rank(with_cardan)),
            "passive_platform_dof": 6 - int(np.linalg.matrix_rank(with_cardan)),
            "allowed_motion": "tz, rx, ry",
        },
        "rigid_keyed_slide_without_cardan": {
            "constraint_rank": int(np.linalg.matrix_rank(rigid_keyed_slide)),
            "passive_platform_dof": 6 - int(np.linalg.matrix_rank(rigid_keyed_slide)),
            "allowed_motion": "tz only; pitch and roll would bind",
        },
    }


def guide_overlap_summary():
    rows = []
    for lift in LIFT_GRID_MM:
        pose = Pose(lift, 0.0, 0.0, True, "overlap")
        rows.append({
            "lift_mm": lift,
            "overlap_mm": guide_mechanism.overlap_mm(platform_center_z(pose)),
        })
    worst = min(rows, key=lambda row: row["overlap_mm"])
    return {
        "minimum_overlap_mm": worst["overlap_mm"],
        "worst_overlap_pose": worst,
        "required_minimum_overlap_mm": P.guide_min_overlap_mm,
        "passes_current_overlap_screen": worst["overlap_mm"] >= P.guide_min_overlap_mm,
    }


def main():
    print({"central_guide_constraints": central_guide_constraint_summary()})
    print({"guide_overlap": guide_overlap_summary()})
    for angle in ANGLE_CASES_DEG:
        print({"cardan": cardan_summary(angle)})
        print({"joint_articulation": joint_articulation_summary(angle)})
        print({"actuator_jacobian": jacobian_summary(angle)})


if __name__ == "__main__":
    main()
