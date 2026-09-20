"""Phase-1 kinematic audit for the cart-backed Manual M2R2 3-RPS concept.

This is an analytical concept model, not fabrication CAD.  It uses the joint
centres already fixed in the M2R2F1 review model and records the MISUMI cart
substitutions that preserve those centres.  X, Y and yaw are constrained by
the three lower revolute axes; Z, roll and pitch remain the commanded modes.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from math import asin, cos, degrees, radians, sin, sqrt
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "manual_m2r2_cart_dof_simulation"


@dataclass(frozen=True)
class Parameters:
    lower_points_mm: tuple[tuple[float, float, float], ...] = (
        (0.0, 75.0, 63.0),
        (-75.0, -180.0, 63.0),
        (75.0, -180.0, 63.0),
    )
    upper_local_points_mm: tuple[tuple[float, float, float], ...] = (
        (0.0, 250.0, 0.0),
        (-250.0, -180.0, 0.0),
        (250.0, -180.0, 0.0),
    )
    lower_revolute_axes: tuple[tuple[float, float, float], ...] = (
        (1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, 1.0, 0.0),
    )
    upper_pin_z_mm: float = 281.0
    reviewed_min_pin_distance_mm: float = 260.0
    reviewed_max_pin_distance_mm: float = 300.0
    stb_stud_thread_length_mm: float = 38.0
    minimum_internal_thread_engagement_mm: float = 18.0
    m12_pitch_mm: float = 1.75
    characteristic_length_mm: float = 250.0
    design_leg_screen_load_n: float = 600.0
    supported_mass_screen_kg: float = 20.0
    gravity_m_s2: float = 9.80665
    grid_step_deg: float = 0.25


P = Parameters()
LOWER = np.asarray(P.lower_points_mm, dtype=float)
UPPER = np.asarray(P.upper_local_points_mm, dtype=float)
AXES = np.asarray(P.lower_revolute_axes, dtype=float)

CART_BOM = {
    "turnbuckle": "STB-M12 x3",
    "lower_eye": "BJ761-12011N x3",
    "coupling_nut": "NTFL12-36 x3",
    "upper_rod_end": "IKO PHS12L x3",
    "shaft_support": "SHAT12 x12",
    "shaft": "SFU12-100 x6",
    "shaft_collar": "SCSJ12-6 x12",
    "right_hand_jam_nut": "HNT1-ST-M12 x6",
    "left_hand_jam_nut": "HNT1A-STAY-M12 x3",
    "support_fastener": "CB5-16 + HNTT8-5 + FWSSB-D9-V5.5-T1, each x24",
    "shims": "PCIMR12-18-1.0 / CIMR12-18-0.5 / CIMR12-18-0.2",
}


def rotation(pitch_deg: float, roll_deg: float) -> np.ndarray:
    pitch = radians(pitch_deg)
    roll = radians(roll_deg)
    rx = np.array(
        ((1.0, 0.0, 0.0), (0.0, cos(roll), -sin(roll)), (0.0, sin(roll), cos(roll)))
    )
    ry = np.array(
        ((cos(pitch), 0.0, sin(pitch)), (0.0, 1.0, 0.0), (-sin(pitch), 0.0, cos(pitch)))
    )
    return ry @ rx


def pose(pitch_deg: float, roll_deg: float, z_offset_mm: float = 0.0):
    """Return the yaw=0 branch that exactly satisfies the three R constraints."""
    r = rotation(pitch_deg, roll_deg)
    t = np.array(
        (
            -250.0 * r[0, 1],
            -180.0 * (1.0 - r[1, 1]),
            P.upper_pin_z_mm + z_offset_mm,
        )
    )
    q = UPPER @ r.T + t
    return r, t, q


def scaled_constraint_jacobians(pitch_deg: float, roll_deg: float, z_offset_mm: float = 0.0):
    r, t, q = pose(pitch_deg, roll_deg, z_offset_mm)
    lever = q - t
    delta = q - LOWER
    lengths = np.linalg.norm(delta, axis=1)
    unit = delta / lengths[:, None]
    passive = np.hstack((AXES, np.cross(lever, AXES) / P.characteristic_length_mm))
    length_rows = np.hstack((unit, np.cross(lever, unit) / P.characteristic_length_mm))
    locked = np.vstack((passive, length_rows))
    return passive, locked


def required_rod_end_angles_deg(r: np.ndarray, link_unit: np.ndarray) -> np.ndarray:
    """Rod axis departure from perpendicular to each transformed upper pin axis."""
    upper_axes = AXES @ r.T
    dot = np.einsum("ij,ij->i", link_unit, upper_axes)
    return np.degrees(np.arcsin(np.clip(np.abs(dot), 0.0, 1.0)))


def evaluate_pose(pitch_deg: float, roll_deg: float, z_offset_mm: float = 0.0) -> dict:
    r, t, q = pose(pitch_deg, roll_deg, z_offset_mm)
    delta = q - LOWER
    lengths = np.linalg.norm(delta, axis=1)
    unit = delta / lengths[:, None]
    phs_angles = required_rod_end_angles_deg(r, unit)
    passive, locked = scaled_constraint_jacobians(pitch_deg, roll_deg, z_offset_mm)
    locked_sv = np.linalg.svd(locked, compute_uv=False)
    length_margin = min(
        float(np.min(lengths - P.reviewed_min_pin_distance_mm)),
        float(np.min(P.reviewed_max_pin_distance_mm - lengths)),
    )
    engagement = P.stb_stud_thread_length_mm - max(
        0.0, float(np.max(lengths)) - P.reviewed_min_pin_distance_mm
    ) / 2.0
    return {
        "pitch_deg": float(pitch_deg),
        "roll_deg": float(roll_deg),
        "z_offset_mm": float(z_offset_mm),
        "translation_mm": t.tolist(),
        "upper_points_mm": q.tolist(),
        "lengths_mm": lengths.tolist(),
        "turns_from_neutral": ((lengths - neutral_lengths()) / (2.0 * P.m12_pitch_mm)).tolist(),
        "required_phs_angles_deg": phs_angles.tolist(),
        "max_required_phs_angle_deg": float(np.max(phs_angles)),
        "length_margin_mm": length_margin,
        "minimum_internal_thread_engagement_mm": engagement,
        "passive_constraint_rank": int(np.linalg.matrix_rank(passive, tol=1e-9)),
        "locked_constraint_rank": int(np.linalg.matrix_rank(locked, tol=1e-9)),
        "locked_minimum_singular_value": float(locked_sv[-1]),
        "locked_condition_number": float(locked_sv[0] / locked_sv[-1]),
        "length_window_pass": bool(length_margin >= -1e-9),
        "thread_engagement_pass": bool(
            engagement >= P.minimum_internal_thread_engagement_mm - 1e-9
        ),
    }


def neutral_lengths() -> np.ndarray:
    _, _, q = pose(0.0, 0.0, 0.0)
    return np.linalg.norm(q - LOWER, axis=1)


def values(limit_deg: float, step_deg: float):
    count = int(round(2.0 * limit_deg / step_deg))
    return np.linspace(-limit_deg, limit_deg, count + 1)


def z_interval_length_only(pitch_deg: float, roll_deg: float) -> tuple[float, float]:
    _, _, q = pose(pitch_deg, roll_deg, 0.0)
    delta = q - LOWER
    horizontal_sq = np.sum(delta[:, :2] ** 2, axis=1)
    vertical = delta[:, 2]
    lower = []
    upper = []
    for h2, dz in zip(horizontal_sq, vertical):
        if h2 >= P.reviewed_max_pin_distance_mm**2:
            return float("inf"), float("-inf")
        min_vertical = sqrt(max(0.0, P.reviewed_min_pin_distance_mm**2 - h2))
        max_vertical = sqrt(P.reviewed_max_pin_distance_mm**2 - h2)
        lower.append(min_vertical - dz)
        upper.append(max_vertical - dz)
    return max(lower), min(upper)


def sweep(limit_deg: float) -> dict:
    rows = []
    z_intervals = []
    for pitch_deg in values(limit_deg, P.grid_step_deg):
        for roll_deg in values(limit_deg, P.grid_step_deg):
            row = evaluate_pose(float(pitch_deg), float(roll_deg))
            rows.append(row)
            z_intervals.append(z_interval_length_only(float(pitch_deg), float(roll_deg)))
    all_lengths = np.asarray([row["lengths_mm"] for row in rows])
    all_phs = np.asarray([row["required_phs_angles_deg"] for row in rows])
    robust_z_min = max(item[0] for item in z_intervals)
    robust_z_max = min(item[1] for item in z_intervals)
    return {
        "limit_deg": limit_deg,
        "pose_count": len(rows),
        "minimum_pin_distance_mm": float(np.min(all_lengths)),
        "maximum_pin_distance_mm": float(np.max(all_lengths)),
        "total_required_length_span_mm": float(np.max(all_lengths) - np.min(all_lengths)),
        "maximum_absolute_turns_from_neutral": float(
            np.max(np.abs((all_lengths - neutral_lengths()) / (2.0 * P.m12_pitch_mm)))
        ),
        "maximum_required_phs_angle_deg": float(np.max(all_phs)),
        "minimum_length_margin_mm": float(min(row["length_margin_mm"] for row in rows)),
        "minimum_thread_engagement_mm": float(
            min(row["minimum_internal_thread_engagement_mm"] for row in rows)
        ),
        "minimum_passive_rank": min(row["passive_constraint_rank"] for row in rows),
        "minimum_locked_rank": min(row["locked_constraint_rank"] for row in rows),
        "minimum_locked_singular_value": float(
            min(row["locked_minimum_singular_value"] for row in rows)
        ),
        "maximum_locked_condition_number": float(
            max(row["locked_condition_number"] for row in rows)
        ),
        "max_abs_dependent_x_mm": float(max(abs(row["translation_mm"][0]) for row in rows)),
        "max_abs_dependent_y_mm": float(max(abs(row["translation_mm"][1]) for row in rows)),
        "robust_common_z_interval_length_only_mm": [robust_z_min, robust_z_max],
        "robust_common_z_span_length_only_mm": max(0.0, robust_z_max - robust_z_min),
        "all_length_window_pass": all(row["length_window_pass"] for row in rows),
        "all_thread_engagement_pass": all(row["thread_engagement_pass"] for row in rows),
        "all_intended_mobility_pass": all(
            row["passive_constraint_rank"] == 3 and row["locked_constraint_rank"] == 6
            for row in rows
        ),
        "rows": rows,
    }


def neutral_actuation_sensitivity() -> dict:
    # Columns: Z in mm, roll and pitch in degrees.
    step_z = 1e-3
    step_angle = 1e-4
    columns = []
    for plus, minus, step in (
        ((0.0, 0.0, step_z), (0.0, 0.0, -step_z), step_z),
        ((0.0, step_angle, 0.0), (0.0, -step_angle, 0.0), step_angle),
        ((step_angle, 0.0, 0.0), (-step_angle, 0.0, 0.0), step_angle),
    ):
        lp = np.asarray(evaluate_pose(plus[0], plus[1], plus[2])["lengths_mm"])
        lm = np.asarray(evaluate_pose(minus[0], minus[1], minus[2])["lengths_mm"])
        columns.append((lp - lm) / (2.0 * step))
    matrix = np.column_stack(columns)

    # Dimensionless conditioning with rotations scaled by the 250 mm support radius.
    angle_scale_deg = degrees(1.0 / P.characteristic_length_mm)
    scaled = matrix.copy()
    scaled[:, 1:] *= angle_scale_deg
    sv = np.linalg.svd(scaled, compute_uv=False)
    return {
        "columns": ["z_mm", "roll_deg", "pitch_deg"],
        "d_length_matrix": matrix.tolist(),
        "rank": int(np.linalg.matrix_rank(matrix)),
        "scaled_condition_number": float(sv[0] / sv[-1]),
        "interpretation": "Rows A1/A2/A3; entries are mm link change per mm Z or per degree roll/pitch.",
    }


def load_screen(limit_deg: float, cg_offset_mm: float) -> dict:
    weight = P.supported_mass_screen_kg * P.gravity_m_s2
    min_reaction = float("inf")
    max_reaction = float("-inf")
    max_abs_axial = 0.0
    worst = None
    directions = np.arange(0.0, 360.0, 5.0) if cg_offset_mm else np.array((0.0,))
    for pitch_deg in values(limit_deg, 0.5):
        for roll_deg in values(limit_deg, 0.5):
            _, t, q = pose(float(pitch_deg), float(roll_deg))
            eq = np.vstack((q[:, 0], q[:, 1], np.ones(3)))
            link_unit = (q - LOWER) / np.linalg.norm(q - LOWER, axis=1)[:, None]
            for direction_deg in directions:
                direction = radians(float(direction_deg))
                cg = t[:2] + cg_offset_mm * np.array((cos(direction), sin(direction)))
                reactions = np.linalg.solve(eq, np.array((weight * cg[0], weight * cg[1], weight)))
                axial = reactions / link_unit[:, 2]
                min_reaction = min(min_reaction, float(np.min(reactions)))
                max_reaction = max(max_reaction, float(np.max(reactions)))
                index = int(np.argmax(np.abs(axial)))
                if abs(float(axial[index])) > max_abs_axial:
                    max_abs_axial = abs(float(axial[index]))
                    worst = {
                        "pitch_deg": float(pitch_deg),
                        "roll_deg": float(roll_deg),
                        "cg_direction_deg": float(direction_deg),
                        "leg": index + 1,
                        "reaction_n": float(reactions[index]),
                        "axial_n": float(axial[index]),
                    }
    return {
        "supported_mass_kg": P.supported_mass_screen_kg,
        "cg_offset_mm": cg_offset_mm,
        "minimum_vertical_reaction_n": min_reaction,
        "maximum_vertical_reaction_n": max_reaction,
        "all_reactions_compressive": min_reaction >= 0.0,
        "maximum_absolute_equivalent_link_axial_n": max_abs_axial,
        "design_leg_screen_load_n": P.design_leg_screen_load_n,
        "screen_load_ratio": P.design_leg_screen_load_n / max_abs_axial,
        "worst_case": worst,
        "limitations": "Rigid static vertical-load distribution only; no shock, friction, frame flexure, slot slip or STB compression rating.",
    }


def standard_pose_rows():
    pairs = (
        (0, 0), (3, 0), (-3, 0), (0, 3), (0, -3),
        (3, 3), (3, -3), (-3, 3), (-3, -3),
    )
    return [evaluate_pose(pitch, roll) for pitch, roll in pairs]


def write_pose_csv(rows: list[dict]):
    path = OUTPUT / "standard_pose_adjustments.csv"
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["pitch_deg", "roll_deg", "L1_mm", "L2_mm", "L3_mm", "A1_turns", "A2_turns", "A3_turns", "max_PHS_angle_deg"]
        )
        for row in rows:
            writer.writerow(
                [row["pitch_deg"], row["roll_deg"], *row["lengths_mm"], *row["turns_from_neutral"], row["max_required_phs_angle_deg"]]
            )


def plot_workspace(sweep3: dict):
    grid = values(3.0, P.grid_step_deg)
    margin = np.asarray([row["length_margin_mm"] for row in sweep3["rows"]]).reshape(len(grid), len(grid))
    angle = np.asarray([row["max_required_phs_angle_deg"] for row in sweep3["rows"]]).reshape(len(grid), len(grid))
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.5), constrained_layout=True)
    im0 = axes[0].imshow(margin, origin="lower", extent=(-3, 3, -3, 3), aspect="equal", cmap="viridis")
    axes[0].contour(grid, grid, margin, levels=[0], colors="red", linewidths=1.5)
    axes[0].set(title="Turnbuckle length margin (mm)", xlabel="Roll (deg)", ylabel="Pitch (deg)")
    fig.colorbar(im0, ax=axes[0], label="Nearest 260/300 mm boundary")
    im1 = axes[1].imshow(angle, origin="lower", extent=(-3, 3, -3, 3), aspect="equal", cmap="magma")
    axes[1].set(title="Required PHS12L articulation", xlabel="Roll (deg)", ylabel="Pitch (deg)")
    fig.colorbar(im1, ax=axes[1], label="Required angle (deg)")
    fig.suptitle("Manual M2R2, fixed-height ±3° workspace")
    fig.savefig(OUTPUT / "workspace_margin_and_joint_angle.png", dpi=180)
    plt.close(fig)


def plot_adjustments(rows: list[dict]):
    labels = [f"P{row['pitch_deg']:+g}/R{row['roll_deg']:+g}" for row in rows]
    turns = np.asarray([row["turns_from_neutral"] for row in rows])
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(11.0, 4.8), constrained_layout=True)
    width = 0.24
    for leg in range(3):
        ax.bar(x + (leg - 1) * width, turns[:, leg], width, label=f"A{leg + 1}")
    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.set_xticks(x, labels, rotation=35, ha="right")
    ax.set_ylabel("Turnbuckle body turns from neutral")
    ax.set_title("Adjustment commands; 1 turn = 3.5 mm pin-distance change")
    ax.legend(ncol=3)
    fig.savefig(OUTPUT / "standard_pose_turns.png", dpi=180)
    plt.close(fig)


def plot_geometry():
    fig = plt.figure(figsize=(10.5, 4.8), constrained_layout=True)
    for panel, (pitch, roll, title) in enumerate(((0, 0, "Neutral"), (3, 3, "Pitch +3°, roll +3°")), 1):
        ax = fig.add_subplot(1, 2, panel, projection="3d")
        _, t, q = pose(pitch, roll)
        lower_loop = np.vstack((LOWER, LOWER[0]))
        upper_loop = np.vstack((q, q[0]))
        ax.plot(*lower_loop.T, color="#4c78a8", linewidth=2, label="Lower R centres")
        ax.plot(*upper_loop.T, color="#f58518", linewidth=2, label="Upper S centres")
        for index in range(3):
            ax.plot(*np.vstack((LOWER[index], q[index])).T, color="#333333", linewidth=2)
            ax.text(*q[index], f" A{index + 1}")
        ax.scatter(*t, color="red", s=25, label="Platform origin")
        ax.set(xlim=(-300, 300), ylim=(-250, 300), zlim=(0, 350), xlabel="X mm", ylabel="Y mm", zlabel="Z mm", title=title)
        ax.set_box_aspect((600, 550, 350))
        if panel == 1:
            ax.legend(fontsize=8)
    fig.suptitle("M2R2 analytical joint-centre model — preliminary")
    fig.savefig(OUTPUT / "joint_centre_geometry.png", dpi=180)
    plt.close(fig)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    sweep_results = {str(limit): sweep(limit) for limit in (3.0, 5.0, 8.0)}
    standard = standard_pose_rows()
    neutral_z = z_interval_length_only(0.0, 0.0)
    result = {
        "status": "PHASE_1_PRELIMINARY_NOT_APPROVED_FOR_FABRICATION",
        "parameters": asdict(P),
        "cart_bom_basis": CART_BOM,
        "coordinate_system": {
            "X": "device length direction",
            "Y": "device width direction",
            "Z": "up",
            "pitch": "rotation about Y",
            "roll": "rotation about X",
            "rotation_order": "Ry(pitch) @ Rx(roll)",
        },
        "equations": {
            "upper_joint": "q_i = R_y(pitch) R_x(roll) p_i + t",
            "link_length": "L_i = norm(q_i - b_i)",
            "lower_R_constraint": "a_i dot (q_i - b_i) = 0",
            "turnbuckle_command": "turns_i = (L_i - L_i_neutral) / (2 * 1.75 mm)",
        },
        "neutral_pin_distances_mm": neutral_lengths().tolist(),
        "neutral_common_z_interval_length_only_mm": list(neutral_z),
        "neutral_common_z_span_length_only_mm": neutral_z[1] - neutral_z[0],
        "neutral_actuation_sensitivity": neutral_actuation_sensitivity(),
        "sweeps": sweep_results,
        "standard_poses": standard,
        "load_cases": {
            "20kg_centered": load_screen(3.0, 0.0),
            "20kg_100mm_offset": load_screen(3.0, 100.0),
            "20kg_150mm_offset": load_screen(3.0, 150.0),
        },
        "joint_angle_decision": {
            "catalog_allowable_angle_confirmed": True,
            "catalog_conservative_allowable_angle_deg": 8.0,
            "required_minimum_deg_without_margin": sweep_results["3.0"]["maximum_required_phs_angle_deg"],
            "margin_deg": 8.0 - sweep_results["3.0"]["maximum_required_phs_angle_deg"],
            "source": "IKO PILLOBALL catalogue Table 11: d=12 mm PHS alpha1=8 deg, alpha2=13 deg; conservative alpha1 used.",
        },
        "conclusions": {
            "kinematic_leveling_at_fixed_height_plus_minus_3_deg": bool(
                sweep_results["3.0"]["all_length_window_pass"]
                and sweep_results["3.0"]["all_thread_engagement_pass"]
                and sweep_results["3.0"]["all_intended_mobility_pass"]
            ),
            "unconditional_purchase_release": False,
            "reason_purchase_not_released": "STB-M12 compression rating remains a supplier-confirmation item; mechanical stops and actual cart interface are unresolved.",
        },
    }
    with (OUTPUT / "dof_simulation_results.json").open("w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
    write_pose_csv(standard)
    plot_workspace(sweep_results["3.0"])
    plot_adjustments(standard)
    plot_geometry()
    print(json.dumps({
        "output": str(OUTPUT),
        "neutral_lengths_mm": result["neutral_pin_distances_mm"],
        "sweep_summary": {key: {k: v for k, v in value.items() if k != "rows"} for key, value in sweep_results.items()},
        "sensitivity": result["neutral_actuation_sensitivity"],
        "load_cases": result["load_cases"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
