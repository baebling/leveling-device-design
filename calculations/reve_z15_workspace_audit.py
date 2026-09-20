"""Finite Rev E screen for the rebaselined physical Z=15--65 mm envelope.

This module intentionally keeps the retained Rev D kinematics and Rev E CAD
geometry unchanged.  It is a reproducible, finite digital screen only; it is
not a continuous-workspace proof or a release record.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from itertools import product
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fusion_scripts.ProfileRadialRevD import revd_data


PHYSICAL_Z_GRID_MM = tuple(float(value) for value in range(15, 70, 5))
PITCH_GRID_DEG = tuple(value * 0.5 for value in range(-6, 7))
ROLL_GRID_DEG = PITCH_GRID_DEG
MAX_Z_COLLISION_ANGLES_DEG = (-3.0, 0.0, 3.0)


@dataclass(frozen=True)
class CollisionPose:
    """Small pose contract for monkeypatchable collision-call tests."""

    label: str
    lift_mm: float
    pitch_deg: float
    roll_deg: float


def physical_pose_grid():
    """Return the required 11 x 13 x 13 finite physical-Z grid."""

    return tuple(
        (physical_z_mm, pitch_deg, roll_deg)
        for physical_z_mm, pitch_deg, roll_deg in product(
            PHYSICAL_Z_GRID_MM, PITCH_GRID_DEG, ROLL_GRID_DEG
        )
    )


def _pose_record(physical_z_mm, pitch_deg, roll_deg, axis, lengths):
    return {
        "physical_z_mm": physical_z_mm,
        "pitch_deg": pitch_deg,
        "roll_deg": roll_deg,
        "axis": axis + 1,
        "pin_length_mm": lengths[axis],
        "pin_lengths_mm": list(lengths),
    }


def _production_collision_contract():
    """Load CadQuery-dependent Rev E collision objects only when needed."""

    from cad.profile_radial_reve_actual_vendor import Pose, collision_audit

    return Pose, collision_audit


def audit_reve_z15_workspace(
    *, collision_check=None, pose_factory=None, progress_callback=None
):
    """Screen all required kinematic samples and nine maximum-Z CAD poses.

    The optional arguments exist so unit tests can verify the collision-call
    contract without importing the CadQuery kernel.  Production callers leave
    them unset, which invokes ``cad...collision_audit`` for every required
    physical-Z=65 mm pose.
    """

    if collision_check is None:
        pose_factory, collision_check = _production_collision_contract()
    elif pose_factory is None:
        pose_factory = CollisionPose

    poses = physical_pose_grid()
    minimum = None
    maximum = None
    for physical_z_mm, pitch_deg, roll_deg in poses:
        lengths = revd_data.pin_lengths(physical_z_mm, pitch_deg, roll_deg)
        for axis, pin_length_mm in enumerate(lengths):
            record = _pose_record(
                physical_z_mm, pitch_deg, roll_deg, axis, lengths
            )
            if minimum is None or pin_length_mm < minimum["pin_length_mm"]:
                minimum = record
            if maximum is None or pin_length_mm > maximum["pin_length_mm"]:
                maximum = record

    collision_rows = []
    collision_angles = tuple(product(MAX_Z_COLLISION_ANGLES_DEG, repeat=2))
    for index, (pitch_deg, roll_deg) in enumerate(collision_angles, start=1):
        physical_z_mm = PHYSICAL_Z_GRID_MM[-1]
        if progress_callback is not None:
            progress_callback(
                f"collision {index}/{len(collision_angles)}: physical Z="
                f"{physical_z_mm:g} mm, pitch={pitch_deg:+.1f} deg, "
                f"roll={roll_deg:+.1f} deg"
            )
        pose = pose_factory(
            f"PHYSICAL_Z{physical_z_mm:g}_P{pitch_deg:g}_R{roll_deg:g}",
            physical_z_mm,
            pitch_deg,
            roll_deg,
        )
        collision = collision_check(pose)
        collision_rows.append(
            {
                "physical_z_mm": physical_z_mm,
                "pitch_deg": pitch_deg,
                "roll_deg": roll_deg,
                "collision": collision,
            }
        )

    all_collision_pass = all(row["collision"].get("passes", False) for row in collision_rows)
    return {
        "schema_version": 1,
        "analysis_date": "2026-09-20",
        "geometry_basis": "Retained ProfileRadialRevD kinematics and Rev E actual-vendor CAD collision model",
        "coordinate_basis": "physical_z_mm is the retained Rev D lift coordinate; command Z=0~50 mm maps to physical Z=15~65 mm",
        "fabrication_status": "NOT APPROVED FOR FABRICATION",
        "purchase_status": "NOT APPROVED FOR PURCHASE",
        "physical_z_grid_mm": list(PHYSICAL_Z_GRID_MM),
        "pitch_grid_deg": list(PITCH_GRID_DEG),
        "roll_grid_deg": list(ROLL_GRID_DEG),
        "grid_cardinality": {
            "physical_z_samples": len(PHYSICAL_Z_GRID_MM),
            "pitch_samples": len(PITCH_GRID_DEG),
            "roll_samples": len(ROLL_GRID_DEG),
            "pose_samples": len(poses),
            "pin_length_evaluations": len(poses) * 3,
        },
        "kinematic_pin_length_screen": {
            "minimum_pin_length_mm": minimum["pin_length_mm"],
            "maximum_pin_length_mm": maximum["pin_length_mm"],
            "worst_minimum": minimum,
            "worst_maximum": maximum,
            "required_screen_window_mm": [221.0, 290.0],
            "passes": (
                minimum["pin_length_mm"] >= 221.0
                and maximum["pin_length_mm"] <= 290.0
            ),
        },
        "maximum_physical_z_collision_screen": {
            "physical_z_mm": PHYSICAL_Z_GRID_MM[-1],
            "pitch_roll_grid_deg": list(MAX_Z_COLLISION_ANGLES_DEG),
            "pose_count": len(collision_rows),
            "results": collision_rows,
            "passes": all_collision_pass,
        },
        "finite_screen_pass": (
            minimum["pin_length_mm"] >= 221.0
            and maximum["pin_length_mm"] <= 290.0
            and all_collision_pass
        ),
        "continuous_workspace_proven": False,
        "actual_switch_points_verified": False,
        "guide_overlap_asserted": False,
        "guide_overlap_basis": "No central-guide overlap is asserted unless the modeled assemblies explicitly contain and check that guide.",
        "release_ready": False,
        "fallback_recommendation": "Retain the physical Z=15 mm datum and reduce command maximum Z to 35 mm if a later physical guide or cable check fails.",
        "limitations": [
            "Finite sampling is not a continuous-workspace proof.",
            "Actual actuator internal limit-switch trip points are unverified.",
            "Guide overlap is not asserted unless modeled assemblies explicitly contain and check the guide.",
            "No fabrication or purchase release is granted by this digital screen.",
        ],
    }


def render_markdown_report(audit):
    """Render the human-readable companion to the generated JSON payload."""

    kinematics = audit["kinematic_pin_length_screen"]
    minimum = kinematics["worst_minimum"]
    maximum = kinematics["worst_maximum"]
    collisions = audit["maximum_physical_z_collision_screen"]
    collision_rows = "\n".join(
        "| {pitch:+.1f} | {roll:+.1f} | {passes} | {volume:.6f} |".format(
            pitch=row["pitch_deg"],
            roll=row["roll_deg"],
            passes="PASS" if row["collision"].get("passes", False) else "FAIL",
            volume=float(row["collision"].get("maximum_volume_mm3", float("nan"))),
        )
        for row in collisions["results"]
    )
    return f"""# Rev E physical Z=15--65 mm workspace audit

## Result

`{'PASS-DIGITAL' if audit['finite_screen_pass'] else 'FAIL-DIGITAL'}` — preliminary finite CAD/kinematics screen only. It does **not** grant fabrication or purchase release.

## Exact finite grid

| Dimension | Samples | Values |
|---|---:|---|
| Physical Z | {audit['grid_cardinality']['physical_z_samples']} | 15, 20, …, 65 mm |
| Pitch | {audit['grid_cardinality']['pitch_samples']} | -3.0, -2.5, …, +3.0° |
| Roll | {audit['grid_cardinality']['roll_samples']} | -3.0, -2.5, …, +3.0° |
| Pose samples | {audit['grid_cardinality']['pose_samples']} | 11 × 13 × 13 |
| Pin-length evaluations | {audit['grid_cardinality']['pin_length_evaluations']} | three axes per pose |

The retained `revd_data.pin_lengths` calculation returned a minimum of **{kinematics['minimum_pin_length_mm']:.6f} mm** at physical Z={minimum['physical_z_mm']:.0f} mm, pitch={minimum['pitch_deg']:+.1f}°, roll={minimum['roll_deg']:+.1f}°, axis {minimum['axis']}; and a maximum of **{kinematics['maximum_pin_length_mm']:.6f} mm** at physical Z={maximum['physical_z_mm']:.0f} mm, pitch={maximum['pitch_deg']:+.1f}°, roll={maximum['roll_deg']:+.1f}°, axis {maximum['axis']}. This is within the finite-screen bounds 221.0--290.0 mm.

## Rev E CAD collisions at physical Z=65 mm

`cad.profile_radial_reve_actual_vendor.collision_audit` was run for the required nine pitch/roll corner-and-centre combinations.

| Pitch (°) | Roll (°) | Result | Maximum unintended intersection (mm³) |
|---:|---:|---|---:|
{collision_rows}

All nine CAD results: **{'PASS' if collisions['passes'] else 'FAIL'}**.

## Limits and next gate

- This finite sampling is not a continuous-workspace proof.
- Actual actuator internal limit-switch trip points remain unverified.
- Guide overlap is not asserted unless the modeled assemblies explicitly contain and check that guide.
- This result grants no fabrication or purchase release.
- If a later physical guide or cable check fails, retain the physical Z=15 mm datum and reduce command maximum Z to 35 mm.
"""


def write_workspace_audit_artifacts(json_path, markdown_path, **audit_kwargs):
    """Run the production audit and write only the required JSON/Markdown artifacts."""

    audit = audit_reve_z15_workspace(**audit_kwargs)
    json_destination = Path(json_path)
    markdown_destination = Path(markdown_path)
    json_destination.parent.mkdir(parents=True, exist_ok=True)
    markdown_destination.parent.mkdir(parents=True, exist_ok=True)
    json_destination.write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    markdown_destination.write_text(render_markdown_report(audit), encoding="utf-8")
    return audit


if __name__ == "__main__":
    json_output = ROOT / "verification" / "reve_z15_workspace_audit_2026-09-20.json"
    markdown_output = ROOT / "verification" / "reve_z15_workspace_audit_2026-09-20.md"
    result = write_workspace_audit_artifacts(
        json_output,
        markdown_output,
        progress_callback=lambda message: print(message, flush=True),
    )
    print(
        json.dumps(
            {
                "json_output": str(json_output),
                "markdown_output": str(markdown_output),
                "pose_samples": result["grid_cardinality"]["pose_samples"],
                "minimum_pin_length_mm": result["kinematic_pin_length_screen"]["minimum_pin_length_mm"],
                "maximum_pin_length_mm": result["kinematic_pin_length_screen"]["maximum_pin_length_mm"],
                "maximum_z_collision_pass": result["maximum_physical_z_collision_screen"]["passes"],
                "finite_screen_pass": result["finite_screen_pass"],
                "release_ready": result["release_ready"],
            },
            ensure_ascii=False,
        )
    )
