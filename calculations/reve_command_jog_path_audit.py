"""Finite command/JOG path screens for HOME-eligible Rev E operation."""

from __future__ import annotations

import json
import sys
from itertools import product
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from calculations.reve_approved_workspace import (
    PIN_LENGTH_MAX_MM,
    PIN_LENGTH_MIN_MM,
    dense_pose_grid,
    sample_pose_segment,
)
from calculations.reve_home_path_audit import pose_metrics
from fusion_scripts.ProfileRadialRevD import revd_data


HOME_PARK_POSE = (0.0, 0.0, 0.0)


def _dense_adjacent_jog_segments():
    """Yield each positive-direction neighbor edge of the screening grid."""

    for lift_index, pitch_index, roll_index in product(
        range(11), range(-6, 7), range(-6, 7)
    ):
        start = (
            lift_index * 5.0,
            pitch_index * 0.5,
            roll_index * 0.5,
        )
        if lift_index < 10:
            yield start, (
                (lift_index + 1) * 5.0,
                pitch_index * 0.5,
                roll_index * 0.5,
            )
        if pitch_index < 6:
            yield start, (
                lift_index * 5.0,
                (pitch_index + 1) * 0.5,
                roll_index * 0.5,
            )
        if roll_index < 6:
            yield start, (
                lift_index * 5.0,
                pitch_index * 0.5,
                (roll_index + 1) * 0.5,
            )


def _screen_pose(pose):
    lift_mm, pitch_deg, roll_deg = pose
    lengths = revd_data.pin_lengths(lift_mm, pitch_deg, roll_deg)
    platform = revd_data.solve_platform(pitch_deg, roll_deg)
    metrics = pose_metrics(
        SimpleNamespace(
            pitch_deg=pitch_deg,
            roll_deg=roll_deg,
            yaw_rad=platform["yaw_rad"],
        )
    )
    return lengths, metrics


def audit_home_eligible_command_jog_paths(
    *,
    home_park_pose=HOME_PARK_POSE,
    maximum_tilt_deg: float = 5.0,
    phs_limit_deg: float = 13.0,
):
    """Screen dense starts to HOME park plus all dense-grid JOG edges.

    This is a finite controller-policy screen. It does not prove arbitrary
    endpoint-to-endpoint commands or the continuous workspace.
    """

    poses = tuple(dense_pose_grid())
    minimum_pin = float("inf")
    maximum_pin = float("-inf")
    maximum_tilt = float("-inf")
    maximum_articulation = float("-inf")
    worst_pin_min = None
    worst_pin_max = None
    worst_tilt = None
    worst_articulation = None
    sampled = 0

    def screen_segment(kind, segment_index, start, end):
        nonlocal minimum_pin, maximum_pin, maximum_tilt, maximum_articulation
        nonlocal worst_pin_min, worst_pin_max, worst_tilt, worst_articulation
        nonlocal sampled
        for sample_index, pose in enumerate(sample_pose_segment(start, end)):
            lengths, metrics = _screen_pose(pose)
            sampled += 1
            local_min = min(lengths)
            local_max = max(lengths)
            if local_min < minimum_pin:
                minimum_pin = local_min
                worst_pin_min = {
                    "kind": kind,
                    "segment_index": segment_index,
                    "sample_index": sample_index,
                    "pose": pose,
                    "pin_lengths_mm": lengths,
                }
            if local_max > maximum_pin:
                maximum_pin = local_max
                worst_pin_max = {
                    "kind": kind,
                    "segment_index": segment_index,
                    "sample_index": sample_index,
                    "pose": pose,
                    "pin_lengths_mm": lengths,
                }
            if metrics["tilt_deg"] > maximum_tilt:
                maximum_tilt = metrics["tilt_deg"]
                worst_tilt = {
                    "kind": kind,
                    "segment_index": segment_index,
                    "sample_index": sample_index,
                    "pose": pose,
                    "tilt_deg": metrics["tilt_deg"],
                }
            if metrics["maximum_phs_articulation_deg"] > maximum_articulation:
                maximum_articulation = metrics["maximum_phs_articulation_deg"]
                worst_articulation = {
                    "kind": kind,
                    "segment_index": segment_index,
                    "sample_index": sample_index,
                    "pose": pose,
                    "maximum_phs_articulation_deg": metrics[
                        "maximum_phs_articulation_deg"
                    ],
                }

    for index, start in enumerate(poses):
        screen_segment("DENSE_TO_HOME_PARK", index, start, home_park_pose)

    jog_segments = tuple(_dense_adjacent_jog_segments())
    for index, (start, end) in enumerate(jog_segments):
        screen_segment("DENSE_ADJACENT_JOG", index, start, end)

    finite_pass = (
        minimum_pin >= PIN_LENGTH_MIN_MM
        and maximum_pin <= PIN_LENGTH_MAX_MM
        and maximum_tilt <= maximum_tilt_deg
        and maximum_articulation <= phs_limit_deg
    )
    return {
        "scope": "DENSE_GRID_TO_HOME_PARK_AND_DENSE_ADJACENT_JOG_SEGMENTS",
        "dense_pose_count": len(poses),
        "park_pose": tuple(float(value) for value in home_park_pose),
        "park_segment_count": len(poses),
        "jog_segment_count": len(jog_segments),
        "sampled_state_count": sampled,
        "sampling_step": {"lift_mm": 1.0, "angle_deg": 0.1},
        "software_pin_window_mm": [PIN_LENGTH_MIN_MM, PIN_LENGTH_MAX_MM],
        "minimum_pin_mm": minimum_pin,
        "maximum_pin_mm": maximum_pin,
        "maximum_tilt_deg": maximum_tilt,
        "tilt_limit_deg": maximum_tilt_deg,
        "maximum_phs_articulation_deg": maximum_articulation,
        "phs_limit_deg": phs_limit_deg,
        "phs_limit_source": "LDK_PHS6_DATASHEET",
        "finite_screen_pass": finite_pass,
        "continuous_workspace_proven": False,
        "full_path_cad_collision_audited": False,
        "release_ready": False,
        "worst_minimum_pin": worst_pin_min,
        "worst_maximum_pin": worst_pin_max,
        "worst_tilt": worst_tilt,
        "worst_articulation": worst_articulation,
        "release_blockers": [
            "This finite policy screen does not cover arbitrary endpoint-to-endpoint commands.",
            "Final LMB/PHS/independent-stop geometry is not included in a full-path CAD collision audit.",
            "Supplier switch trip lengths, overtravel, current, and encoder counts/mm remain unverified.",
        ],
    }


def write_command_jog_audit_json(path, **audit_kwargs):
    """Write the reproducible command/JOG finite-screen artifact."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "analysis_date": "2026-09-17",
        "geometry_basis": "ProfileRadialRevD retained geometry",
        "fabrication_status": "NOT APPROVED FOR FABRICATION",
        **audit_home_eligible_command_jog_paths(**audit_kwargs),
    }
    serialized = json.dumps(payload, ensure_ascii=False, indent=2)
    destination.write_text(serialized + "\n", encoding="utf-8")
    return json.loads(serialized)


if __name__ == "__main__":
    output = ROOT / "verification" / "reve_command_jog_path_audit_2026-09-17.json"
    result = write_command_jog_audit_json(output)
    print(
        json.dumps(
            {
                "output": str(output),
                "sampled_state_count": result["sampled_state_count"],
                "finite_screen_pass": result["finite_screen_pass"],
                "release_ready": result["release_ready"],
            },
            ensure_ascii=False,
        )
    )
