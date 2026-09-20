from itertools import product
from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("XDG_CACHE_HOME", str(ROOT / ".cache"))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplcache"))
for path in (ROOT,):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from cad.parameters import P, Pose
from calculations.actuator_geometry import actuator_lengths


LIFT_GRID_MM = tuple(float(v) for v in range(0, int(P.target_lift_mm) + 1, 10))
ANGLE_GRID_DEG = tuple(round(v * 0.25, 2) for v in range(0, 33))  # 0.00 to 8.00 deg
CHECK_ANGLES_DEG = (3.0, 5.0, 8.0)
END_MARGIN_CASES_MM = (P.actuator_min_end_margin_mm, 15.0)


def length_margins(pose, end_margin_mm):
    lengths = actuator_lengths(pose)
    return {
        "lengths_mm": lengths,
        "minimum_length_mm": min(lengths),
        "maximum_length_mm": max(lengths),
        "retracted_margin_mm": min(lengths) - P.actuator_retracted_mm,
        "extended_margin_mm": P.actuator_extended_mm - max(lengths),
        "minimum_effective_margin_mm": min(
            min(lengths) - (P.actuator_retracted_mm + end_margin_mm),
            (P.actuator_extended_mm - end_margin_mm) - max(lengths),
        ),
    }


def pose_is_valid(lift_mm, pitch_deg, roll_deg, end_margin_mm):
    margins = length_margins(Pose(lift_mm, pitch_deg, roll_deg, True, "workspace"), end_margin_mm)
    return margins["minimum_effective_margin_mm"] >= 0.0


def combined_angle_passes(lift_mm, angle_deg, end_margin_mm):
    rows = []
    for pitch, roll in product((-angle_deg, 0.0, angle_deg), repeat=2):
        pose = Pose(lift_mm, pitch, roll, True, "combined_check")
        margins = length_margins(pose, end_margin_mm)
        rows.append({**margins, "lift_mm": lift_mm, "pitch_deg": pitch, "roll_deg": roll})
    worst = min(rows, key=lambda row: row["minimum_effective_margin_mm"])
    return {
        "lift_mm": lift_mm,
        "angle_deg": angle_deg,
        "end_margin_mm": end_margin_mm,
        "passes": worst["minimum_effective_margin_mm"] >= 0.0,
        "worst_minimum_effective_margin_mm": worst["minimum_effective_margin_mm"],
        "worst_pose": {
            "pitch_deg": worst["pitch_deg"],
            "roll_deg": worst["roll_deg"],
            "minimum_length_mm": worst["minimum_length_mm"],
            "maximum_length_mm": worst["maximum_length_mm"],
            "retracted_margin_mm": worst["retracted_margin_mm"],
            "extended_margin_mm": worst["extended_margin_mm"],
        },
    }


def max_symmetric_angle_at_lift(lift_mm, end_margin_mm):
    valid_angle = 0.0
    for angle in ANGLE_GRID_DEG:
        if combined_angle_passes(lift_mm, angle, end_margin_mm)["passes"]:
            valid_angle = angle
        else:
            break
    return {
        "lift_mm": lift_mm,
        "end_margin_mm": end_margin_mm,
        "max_symmetric_pitch_roll_deg": valid_angle,
    }


def workspace_summary():
    summaries = []
    for end_margin in END_MARGIN_CASES_MM:
        lift_rows = [max_symmetric_angle_at_lift(lift, end_margin) for lift in LIFT_GRID_MM]
        angle_rows = [
            combined_angle_passes(lift, angle, end_margin)
            for lift in LIFT_GRID_MM
            for angle in CHECK_ANGLES_DEG
        ]
        summaries.append({
            "end_margin_mm": end_margin,
            "minimum_supported_symmetric_angle_deg": min(
                row["max_symmetric_pitch_roll_deg"] for row in lift_rows
            ),
            "lift_rows": lift_rows,
            "check_rows": angle_rows,
        })
    return summaries


if __name__ == "__main__":
    for summary in workspace_summary():
        print({
            "end_margin_mm": summary["end_margin_mm"],
            "minimum_supported_symmetric_angle_deg": summary["minimum_supported_symmetric_angle_deg"],
            "lift_rows": summary["lift_rows"],
        })
        for row in summary["check_rows"]:
            if row["angle_deg"] in (3.0, 5.0, 8.0) and row["lift_mm"] in (0.0, 50.0, 100.0):
                print(row)
