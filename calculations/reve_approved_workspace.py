"""Approved Rev E pose-space screens built on the retained Rev D geometry.

The supplier switch trip points are not yet verified.  Nominal 205/305 mm
values are accepted as inputs for analysis, but never make a purchase release.
"""

from __future__ import annotations

import json
import sys
from math import ceil, hypot
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fusion_scripts.ProfileRadialRevD import revd_data


PIN_LENGTH_MIN_MM = 210.0
PIN_LENGTH_MAX_MM = 280.0
Z0_ABSOLUTE_PIN_MM = 224.2075


def approved_pose_grid():
    """Return the 27 explicitly approved corner/centre poses."""

    return tuple(
        {
            "lift_mm": lift_mm,
            "pitch_deg": pitch_deg,
            "roll_deg": roll_deg,
        }
        for lift_mm, pitch_deg, roll_deg in product(
            (0.0, 25.0, 50.0),
            (-3.0, 0.0, 3.0),
            (-3.0, 0.0, 3.0),
        )
    )


def dense_pose_grid():
    """Return the finite 5 mm/0.5 degree screening grid (not a proof)."""

    return tuple(
        (lift_index * 5.0, pitch_index * 0.5, roll_index * 0.5)
        for lift_index, pitch_index, roll_index in product(
            range(11), range(-6, 7), range(-6, 7)
        )
    )


def sample_pose_segment(
    start,
    end,
    *,
    max_lift_step_mm: float = 1.0,
    max_angle_step_deg: float = 0.1,
):
    """Linearly sample an allowed pose-space segment including both ends."""

    if max_lift_step_mm <= 0.0 or max_angle_step_deg <= 0.0:
        raise ValueError("sampling steps must be positive")
    deltas = tuple(end[index] - start[index] for index in range(3))
    interval_count = max(
        1,
        ceil(abs(deltas[0]) / max_lift_step_mm),
        ceil(abs(deltas[1]) / max_angle_step_deg),
        ceil(abs(deltas[2]) / max_angle_step_deg),
    )
    return tuple(
        tuple(
            start[index] + deltas[index] * step / interval_count
            for index in range(3)
        )
        for step in range(interval_count + 1)
    )


def speed_screen(
    *,
    pitch_rate_deg_s: float,
    roll_rate_deg_s: float,
    lift_rate_mm_s: float = 0.0,
):
    """Finite-grid Jacobian screen for required actuator pin speed.

    This samples the approved pose box; it is not an interval proof of the
    continuous workspace.  The acceptance disturbance is the vector norm of
    pitch and roll angular rates, not 1 degree/s on both axes at once.
    """

    angle_step = 1e-4
    lift_step = 1e-4
    maximum = -1.0
    worst = None
    for lift_mm, pitch_deg, roll_deg in dense_pose_grid():
        pitch_plus = revd_data.pin_lengths(
            lift_mm, pitch_deg + angle_step, roll_deg
        )
        pitch_minus = revd_data.pin_lengths(
            lift_mm, pitch_deg - angle_step, roll_deg
        )
        roll_plus = revd_data.pin_lengths(
            lift_mm, pitch_deg, roll_deg + angle_step
        )
        roll_minus = revd_data.pin_lengths(
            lift_mm, pitch_deg, roll_deg - angle_step
        )
        lift_plus = revd_data.pin_lengths(
            lift_mm + lift_step, pitch_deg, roll_deg
        )
        lift_minus = revd_data.pin_lengths(
            lift_mm - lift_step, pitch_deg, roll_deg
        )
        for axis in range(3):
            d_length_d_pitch = (
                pitch_plus[axis] - pitch_minus[axis]
            ) / (2.0 * angle_step)
            d_length_d_roll = (
                roll_plus[axis] - roll_minus[axis]
            ) / (2.0 * angle_step)
            d_length_d_lift = (
                lift_plus[axis] - lift_minus[axis]
            ) / (2.0 * lift_step)
            required = abs(
                d_length_d_pitch * pitch_rate_deg_s
                + d_length_d_roll * roll_rate_deg_s
                + d_length_d_lift * lift_rate_mm_s
            )
            if required > maximum:
                maximum = required
                worst = {
                    "lift_mm": lift_mm,
                    "pitch_deg": pitch_deg,
                    "roll_deg": roll_deg,
                    "actuator": axis + 1,
                    "required_mm_s": required,
                    "d_length_d_pitch_mm_per_deg": d_length_d_pitch,
                    "d_length_d_roll_mm_per_deg": d_length_d_roll,
                    "d_length_d_lift": d_length_d_lift,
                }

    angular_rate_vector = hypot(pitch_rate_deg_s, roll_rate_deg_s)
    return {
        "pitch_rate_deg_s": pitch_rate_deg_s,
        "roll_rate_deg_s": roll_rate_deg_s,
        "lift_rate_mm_s": lift_rate_mm_s,
        "angular_rate_vector_deg_s": angular_rate_vector,
        "maximum_required_mm_s": maximum,
        "screen_kind": (
            "ACCEPTANCE" if angular_rate_vector <= 1.0 + 1e-12 else "STRESS_ONLY"
        ),
        "sampled_pose_count": len(dense_pose_grid()),
        "claim": "FINITE_GRID_SCREEN_ONLY",
        "worst_case": worst,
    }


def _dense_grid_audit():
    rows = []
    for lift_mm, pitch_deg, roll_deg in dense_pose_grid():
        rows.append(
            {
                "lift_mm": lift_mm,
                "pitch_deg": pitch_deg,
                "roll_deg": roll_deg,
                "pin_lengths_mm": revd_data.pin_lengths(
                    lift_mm, pitch_deg, roll_deg
                ),
            }
        )
    minimum = min(min(row["pin_lengths_mm"]) for row in rows)
    maximum = max(max(row["pin_lengths_mm"]) for row in rows)
    return {
        "pose_count": len(rows),
        "minimum_pin_mm": minimum,
        "maximum_pin_mm": maximum,
        "passes": minimum >= PIN_LENGTH_MIN_MM and maximum <= PIN_LENGTH_MAX_MM,
        "claim": "FINITE_GRID_SCREEN_ONLY",
        "grid_spacing": {
            "lift_mm": 5.0,
            "pitch_deg": 0.5,
            "roll_deg": 0.5,
        },
        "rows": rows,
    }


def write_verification_json(path):
    """Write the reproducible preliminary workspace verification payload."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    approved = software_window_audit()
    dense = _dense_grid_audit()
    payload = {
        "schema_version": 1,
        "analysis_date": "2026-09-17",
        "geometry_basis": "ProfileRadialRevD retained geometry",
        "fabrication_status": "NOT APPROVED FOR FABRICATION",
        "approved_27_pose_audit": approved,
        "dense_grid_audit": dense,
        "speed_screens": {
            "acceptance_vector_rate": speed_screen(
                pitch_rate_deg_s=2 ** -0.5,
                roll_rate_deg_s=2 ** -0.5,
            ),
            "stress_one_degree_per_axis": speed_screen(
                pitch_rate_deg_s=1.0,
                roll_rate_deg_s=1.0,
            ),
        },
        "release_ready": False,
        "release_blockers": [
            "Actual L_low_switch and L_high_switch are not supplier-verified.",
            "Supplier hard-end overtravel is not verified.",
            "Independent mechanical stop design is not yet verified.",
            "Finite grids do not prove the continuous workspace.",
        ],
    }
    serialized = json.dumps(payload, ensure_ascii=False, indent=2)
    destination.write_text(serialized + "\n", encoding="utf-8")
    return json.loads(serialized)


def software_window_audit(
    l_low_switch_mm: float = 205.0,
    l_high_switch_mm: float = 305.0,
    *,
    supplier_limits_verified: bool = False,
):
    """Screen the 27 poses against the approved absolute pin window.

    ``passes`` reports the mathematical screen only. ``release_ready`` also
    requires written supplier verification of the actual switch trip points.
    """

    if l_low_switch_mm >= l_high_switch_mm:
        raise ValueError("L_low_switch must be smaller than L_high_switch")

    rows = []
    for pose in approved_pose_grid():
        lengths = revd_data.pin_lengths(
            pose["lift_mm"], pose["pitch_deg"], pose["roll_deg"]
        )
        rows.append({**pose, "pin_lengths_mm": lengths})

    minimum = min(min(row["pin_lengths_mm"]) for row in rows)
    maximum = max(max(row["pin_lengths_mm"]) for row in rows)
    command_window_inside_switches = (
        l_low_switch_mm < PIN_LENGTH_MIN_MM
        and PIN_LENGTH_MAX_MM < l_high_switch_mm
    )
    passes = (
        minimum >= PIN_LENGTH_MIN_MM
        and maximum <= PIN_LENGTH_MAX_MM
        and command_window_inside_switches
    )

    return {
        "pose_count": len(rows),
        "minimum_pin_mm": minimum,
        "maximum_pin_mm": maximum,
        "software_window_mm": [PIN_LENGTH_MIN_MM, PIN_LENGTH_MAX_MM],
        "l_low_switch_mm": l_low_switch_mm,
        "l_high_switch_mm": l_high_switch_mm,
        "relative_software_window_mm": [
            PIN_LENGTH_MIN_MM - l_low_switch_mm,
            PIN_LENGTH_MAX_MM - l_low_switch_mm,
        ],
        "z0_offset_from_low_switch_mm": Z0_ABSOLUTE_PIN_MM - l_low_switch_mm,
        "command_window_inside_switches": command_window_inside_switches,
        "supplier_limits_verified": supplier_limits_verified,
        "input_status": (
            "SUPPLIER_VERIFIED" if supplier_limits_verified else "NOMINAL_UNVERIFIED"
        ),
        "passes": passes,
        "release_ready": passes and supplier_limits_verified,
        "rows": rows,
    }


if __name__ == "__main__":
    output = (
        ROOT
        / "verification"
        / "reve_approved_workspace_2026-09-17.json"
    )
    result = write_verification_json(output)
    print(
        json.dumps(
            {
                "output": str(output),
                "approved": result["approved_27_pose_audit"]["passes"],
                "dense": result["dense_grid_audit"]["passes"],
                "release_ready": result["release_ready"],
            },
            ensure_ascii=False,
        )
    )
