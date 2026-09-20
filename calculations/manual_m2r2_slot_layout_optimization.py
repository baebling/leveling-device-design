"""Phase-1 slot-position screen for the Manual M2R2 cart BOM.

The only variables are the lower SHAT12 positions in the existing 4080
slots and the neutral upper-frame height.  No purchased part or extrusion
cut length changes.  Results are preliminary and require CAD interference
review after concept approval.
"""

from __future__ import annotations

import csv
import json
from math import asin, cos, degrees, radians, sin, sqrt
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from calculations.manual_m2r2_cart_dof_simulation import AXES, P, UPPER, rotation, values


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "manual_m2r2_cart_dof_simulation"
TARGET_NEUTRAL_LENGTH_MM = 280.0
UPPER_FRAME_TOP_ABOVE_PIN_MM = 63.0
SHAT12_FOOT_LENGTH_ALONG_REAR_RAIL_MM = 42.0


def geometry(horizontal_offset_mm: float):
    inner_coordinate = 250.0 - horizontal_offset_mm
    lower = np.array(
        (
            (0.0, inner_coordinate, 63.0),
            (-inner_coordinate, -180.0, 63.0),
            (inner_coordinate, -180.0, 63.0),
        ),
        dtype=float,
    )
    vertical = sqrt(TARGET_NEUTRAL_LENGTH_MM**2 - horizontal_offset_mm**2)
    upper_pin_z = 63.0 + vertical
    return lower, upper_pin_z


def pose_for_geometry(horizontal_offset_mm: float, pitch_deg: float, roll_deg: float, z_offset_mm: float = 0.0):
    lower, upper_pin_z = geometry(horizontal_offset_mm)
    r = rotation(pitch_deg, roll_deg)
    t = np.array((-250.0 * r[0, 1], -180.0 * (1.0 - r[1, 1]), upper_pin_z + z_offset_mm))
    upper = UPPER @ r.T + t
    return lower, r, t, upper


def z_interval(horizontal_offset_mm: float, pitch_deg: float, roll_deg: float):
    lower, _, _, upper = pose_for_geometry(horizontal_offset_mm, pitch_deg, roll_deg)
    delta = upper - lower
    h2 = np.sum(delta[:, :2] ** 2, axis=1)
    dz = delta[:, 2]
    low = [sqrt(max(0.0, P.reviewed_min_pin_distance_mm**2 - item)) - vertical for item, vertical in zip(h2, dz)]
    high = [sqrt(P.reviewed_max_pin_distance_mm**2 - item) - vertical for item, vertical in zip(h2, dz)]
    return max(low), min(high)


def evaluate(horizontal_offset_mm: float, limit_deg: float):
    lengths = []
    phs_angles = []
    ranks = []
    locked_ranks = []
    locked_conditions = []
    z_intervals = []
    for pitch_deg in values(limit_deg, 0.25):
        for roll_deg in values(limit_deg, 0.25):
            lower, r, t, upper = pose_for_geometry(horizontal_offset_mm, float(pitch_deg), float(roll_deg))
            delta = upper - lower
            leg_length = np.linalg.norm(delta, axis=1)
            unit = delta / leg_length[:, None]
            upper_axes = AXES @ r.T
            angle = np.degrees(np.arcsin(np.clip(np.abs(np.einsum("ij,ij->i", unit, upper_axes)), 0.0, 1.0)))
            lever = upper - t
            passive = np.hstack((AXES, np.cross(lever, AXES) / P.characteristic_length_mm))
            locked = np.vstack((passive, np.hstack((unit, np.cross(lever, unit) / P.characteristic_length_mm))))
            sv = np.linalg.svd(locked, compute_uv=False)
            lengths.extend(leg_length.tolist())
            phs_angles.extend(angle.tolist())
            ranks.append(int(np.linalg.matrix_rank(passive, tol=1e-9)))
            locked_ranks.append(int(np.linalg.matrix_rank(locked, tol=1e-9)))
            locked_conditions.append(float(sv[0] / sv[-1]))
            z_intervals.append(z_interval(horizontal_offset_mm, float(pitch_deg), float(roll_deg)))
    lower, upper_pin_z = geometry(horizontal_offset_mm)
    minimum = min(lengths)
    maximum = max(lengths)
    margin = min(minimum - P.reviewed_min_pin_distance_mm, P.reviewed_max_pin_distance_mm - maximum)
    rear_support_foot_clearance = 2.0 * lower[2, 0] - SHAT12_FOOT_LENGTH_ALONG_REAR_RAIL_MM
    return {
        "horizontal_joint_offset_mm": horizontal_offset_mm,
        "lower_joint_points_mm": lower.tolist(),
        "upper_pin_z_mm": upper_pin_z,
        "estimated_overall_top_z_mm": upper_pin_z + UPPER_FRAME_TOP_ABOVE_PIN_MM,
        "neutral_pin_distance_mm": TARGET_NEUTRAL_LENGTH_MM,
        "angle_limit_deg": limit_deg,
        "minimum_pin_distance_mm": minimum,
        "maximum_pin_distance_mm": maximum,
        "minimum_length_margin_mm": margin,
        "maximum_turns_from_neutral": max(abs(minimum - TARGET_NEUTRAL_LENGTH_MM), abs(maximum - TARGET_NEUTRAL_LENGTH_MM)) / (2.0 * P.m12_pitch_mm),
        "maximum_required_phs_angle_deg": max(phs_angles),
        "minimum_passive_rank": min(ranks),
        "minimum_locked_rank": min(locked_ranks),
        "maximum_locked_condition_number": max(locked_conditions),
        "robust_common_z_interval_length_only_mm": [max(x[0] for x in z_intervals), min(x[1] for x in z_intervals)],
        "rear_pair_shat12_foot_clearance_mm": rear_support_foot_clearance,
        "length_window_pass": margin >= 0.0,
        "mobility_pass": min(ranks) == 3 and min(locked_ranks) == 6,
    }


def load_screen(horizontal_offset_mm: float, cg_offset_mm: float):
    weight = P.supported_mass_screen_kg * P.gravity_m_s2
    min_reaction = float("inf")
    max_abs_axial = 0.0
    directions = np.arange(0.0, 360.0, 5.0) if cg_offset_mm else (0.0,)
    for pitch_deg in values(3.0, 0.5):
        for roll_deg in values(3.0, 0.5):
            lower, _, t, upper = pose_for_geometry(horizontal_offset_mm, float(pitch_deg), float(roll_deg))
            eq = np.vstack((upper[:, 0], upper[:, 1], np.ones(3)))
            unit = (upper - lower) / np.linalg.norm(upper - lower, axis=1)[:, None]
            for direction_deg in directions:
                direction = radians(float(direction_deg))
                cg = t[:2] + cg_offset_mm * np.array((cos(direction), sin(direction)))
                reactions = np.linalg.solve(eq, np.array((weight * cg[0], weight * cg[1], weight)))
                axial = reactions / unit[:, 2]
                min_reaction = min(min_reaction, float(np.min(reactions)))
                max_abs_axial = max(max_abs_axial, float(np.max(np.abs(axial))))
    return {
        "cg_offset_mm": cg_offset_mm,
        "minimum_vertical_reaction_n": min_reaction,
        "all_reactions_compressive": min_reaction >= 0.0,
        "maximum_absolute_equivalent_link_axial_n": max_abs_axial,
        "screen_load_ratio_to_600N": P.design_leg_screen_load_n / max_abs_axial,
    }


def pose_command(horizontal_offset_mm: float, pitch_deg: float, roll_deg: float):
    lower, r, t, upper = pose_for_geometry(horizontal_offset_mm, pitch_deg, roll_deg)
    delta = upper - lower
    lengths = np.linalg.norm(delta, axis=1)
    unit = delta / lengths[:, None]
    upper_axes = AXES @ r.T
    angles = np.degrees(np.arcsin(np.clip(np.abs(np.einsum("ij,ij->i", unit, upper_axes)), 0.0, 1.0)))
    return {
        "pitch_deg": pitch_deg,
        "roll_deg": roll_deg,
        "lengths_mm": lengths.tolist(),
        "turns_from_280mm_neutral": ((lengths - TARGET_NEUTRAL_LENGTH_MM) / (2.0 * P.m12_pitch_mm)).tolist(),
        "required_phs_angles_deg": angles.tolist(),
        "dependent_translation_xy_mm": t[:2].tolist(),
    }


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    offsets = np.arange(160.0, 220.01, 5.0)
    rows = [evaluate(float(offset), 3.0) for offset in offsets]
    recommended = rows[-1]
    recommended_sweeps = {str(angle): evaluate(220.0, angle) for angle in (3.0, 5.0, 8.0)}
    command_pairs = (
        (0, 0), (3, 0), (-3, 0), (0, 3), (0, -3),
        (3, 3), (3, -3), (-3, 3), (-3, -3),
    )
    recommended_commands = [pose_command(220.0, pitch, roll) for pitch, roll in command_pairs]
    comparisons = {
        "current_M2R2F1": {
            "horizontal_joint_offset_mm": 175.0,
            "neutral_pin_distance_mm": 279.5514263959317,
            "upper_pin_z_mm": 281.0,
            "estimated_overall_top_z_mm": 344.0,
            "minimum_pin_distance_mm": 261.3785038726062,
            "maximum_pin_distance_mm": 296.53221502037377,
            "minimum_length_margin_mm": 1.3785038726061885,
            "maximum_turns_from_neutral": 5.192263578092999,
            "maximum_required_phs_angle_deg": 2.415345589209901,
        },
        "recommended_slot_only_revision": recommended,
    }
    result = {
        "status": "PHASE_1_PRELIMINARY_NOT_APPROVED_FOR_FABRICATION",
        "optimization_scope": "Move lower SHAT12 joint centres in existing 4080 slots; retain every cart BOM item and profile cut length.",
        "selection_rule": "Largest screened offset with at least 15 mm rear SHAT12 foot-to-foot clearance.",
        "candidate_rows": rows,
        "comparison": comparisons,
        "recommended_angle_sweeps": recommended_sweeps,
        "recommended_standard_pose_commands": recommended_commands,
        "recommended_load_cases": {
            "20kg_centered": load_screen(recommended["horizontal_joint_offset_mm"], 0.0),
            "20kg_100mm_offset": load_screen(recommended["horizontal_joint_offset_mm"], 100.0),
            "20kg_150mm_offset": load_screen(recommended["horizontal_joint_offset_mm"], 150.0),
        },
        "limitations": [
            "The 18 mm rear support-foot clearance uses the 42 mm nominal SHAT12 foot length; casting fillets and tool access need detailed CAD/physical confirmation.",
            "No solid interference result is claimed for the revised slot positions before concept approval.",
            "STB-M12 compression rating and IKO PHS12L allowable articulation remain supplier-confirmation items.",
            "Actual cart coupling geometry is unknown and is not inferred.",
        ],
    }
    with (OUTPUT / "slot_layout_optimization.json").open("w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
    with (OUTPUT / "slot_layout_candidates.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=[key for key in rows[0] if key not in ("lower_joint_points_mm", "robust_common_z_interval_length_only_mm")])
        writer.writeheader()
        writer.writerows([{key: value for key, value in row.items() if key in writer.fieldnames} for row in rows])
    with (OUTPUT / "recommended_standard_pose_adjustments.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(("pitch_deg", "roll_deg", "L1_mm", "L2_mm", "L3_mm", "A1_turns", "A2_turns", "A3_turns", "max_PHS_angle_deg"))
        for row in recommended_commands:
            writer.writerow((row["pitch_deg"], row["roll_deg"], *row["lengths_mm"], *row["turns_from_280mm_neutral"], max(row["required_phs_angles_deg"])))
    labels = [f"P{row['pitch_deg']:+g}/R{row['roll_deg']:+g}" for row in recommended_commands]
    turns = np.asarray([row["turns_from_280mm_neutral"] for row in recommended_commands])
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(11.0, 4.8), constrained_layout=True)
    width = 0.24
    for leg in range(3):
        ax.bar(x + (leg - 1) * width, turns[:, leg], width, label=f"A{leg + 1}")
    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.set_xticks(x, labels, rotation=35, ha="right")
    ax.set_ylabel("Turnbuckle body turns from 280 mm neutral")
    ax.set_title("Recommended M2R2-S220 commands; 1 turn = 3.5 mm")
    ax.legend(ncol=3)
    fig.savefig(OUTPUT / "recommended_standard_pose_turns.png", dpi=180)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), constrained_layout=True)
    axes[0].plot(offsets, [row["minimum_length_margin_mm"] for row in rows], marker="o")
    axes[0].axvline(220.0, color="tab:red", linestyle="--", label="recommended")
    axes[0].set(xlabel="Horizontal joint offset (mm)", ylabel="Worst length margin (mm)", title="±3° turnbuckle margin")
    axes[0].grid(alpha=0.3)
    axes[0].legend()
    axes[1].plot(offsets, [row["estimated_overall_top_z_mm"] for row in rows], marker="o", label="overall height")
    axes[1].plot(offsets, [row["rear_pair_shat12_foot_clearance_mm"] for row in rows], marker="s", label="rear foot clearance")
    axes[1].axvline(220.0, color="tab:red", linestyle="--")
    axes[1].set(xlabel="Horizontal joint offset (mm)", ylabel="mm", title="Height and assembly clearance")
    axes[1].grid(alpha=0.3)
    axes[1].legend()
    fig.suptitle("M2R2 slot-only layout optimization — same purchased parts")
    fig.savefig(OUTPUT / "slot_layout_optimization.png", dpi=180)
    plt.close(fig)
    fig = plt.figure(figsize=(10.5, 4.8), constrained_layout=True)
    for panel, (pitch, roll, title) in enumerate(((0, 0, "Revised neutral"), (3, 3, "Revised pitch +3°, roll +3°")), 1):
        ax = fig.add_subplot(1, 2, panel, projection="3d")
        lower, _, t, upper = pose_for_geometry(220.0, pitch, roll)
        lower_loop = np.vstack((lower, lower[0]))
        upper_loop = np.vstack((upper, upper[0]))
        ax.plot(*lower_loop.T, color="#4c78a8", linewidth=2, label="Lower R centres")
        ax.plot(*upper_loop.T, color="#f58518", linewidth=2, label="Upper S centres")
        for index in range(3):
            ax.plot(*np.vstack((lower[index], upper[index])).T, color="#333333", linewidth=2)
            ax.text(*upper[index], f" A{index + 1}")
        ax.scatter(*t, color="red", s=25, label="Platform origin")
        ax.set(xlim=(-300, 300), ylim=(-250, 300), zlim=(0, 320), xlabel="X mm", ylabel="Y mm", zlabel="Z mm", title=title)
        ax.set_box_aspect((600, 550, 320))
        if panel == 1:
            ax.legend(fontsize=8)
    fig.suptitle("Recommended slot-only revision — same MISUMI cart BOM")
    fig.savefig(OUTPUT / "recommended_joint_centre_geometry.png", dpi=180)
    plt.close(fig)
    print(json.dumps({"comparison": comparisons, "recommended_load_cases": result["recommended_load_cases"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
