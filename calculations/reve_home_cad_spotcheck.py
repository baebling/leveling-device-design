"""CadQuery collision spot-checks for representative preliminary HOME states."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from calculations.reve_forward_kinematics import solve_pose_from_lengths


def _record(label, path_worst):
    pose = path_worst["pose"]
    return {
        "label": label,
        "lift_mm": pose["lift_mm"],
        "pitch_deg": pose["pitch_deg"],
        "roll_deg": pose["roll_deg"],
        "yaw_rad": pose["yaw_rad"],
        "lengths_mm": path_worst["lengths_mm"],
    }


def extract_pose_records(home_payload):
    """Extract the four declared states without importing CadQuery."""

    selected = home_payload["selected_order_summary"]
    restart = home_payload["phase_reset_restart_witness"]
    equal_low = solve_pose_from_lengths(
        (205.0, 205.0, 205.0),
        seed=(0.0, 0.0, -20.0, 0.0, 0.0, 0.0),
    )
    return [
        _record("HOME_WORST_TILT", selected["worst_tilt"]["path_worst"]),
        _record(
            "HOME_WORST_ARTICULATION",
            selected["worst_articulation"]["path_worst"],
        ),
        _record("HOME_STATELESS_RESTART_FAILURE", restart["worst_tilt"]),
        {
            "label": "HOME_EQUAL_LOW_NOMINAL",
            "lift_mm": equal_low.lift_mm,
            "pitch_deg": equal_low.pitch_deg,
            "roll_deg": equal_low.roll_deg,
            "yaw_rad": equal_low.yaw_rad,
            "lengths_mm": equal_low.target_lengths_mm,
        },
    ]


def run_cad_spotcheck(home_json_path, output_path):
    """Run exact solid intersections for representative states only."""

    from cad.profile_radial_reve_actual_vendor import (
        Pose,
        VENDOR_STEP,
        collision_audit,
        vendor_shapes,
    )

    home_path = Path(home_json_path)
    destination = Path(output_path)
    home_payload = json.loads(home_path.read_text(encoding="utf-8"))
    rows = []
    for record in extract_pose_records(home_payload):
        pose = Pose(
            record["label"],
            record["lift_mm"],
            record["pitch_deg"],
            record["roll_deg"],
        )
        rows.append({**record, "collision": collision_audit(pose)})
    payload = {
        "schema_version": 1,
        "analysis_date": "2026-09-17",
        "geometry_basis": (
            "retained Rev E CAD with LM4075OE vendor STEP plus public-dimension "
            "LMB-10 and MISUMI TRUSCO PHS6 supplier-interface envelopes"
        ),
        "vendor_step": str(VENDOR_STEP),
        "vendor_part_count": len(vendor_shapes()),
        "scope": "REPRESENTATIVE_HOME_STATES_ONLY",
        "full_path_cad_collision_audited": False,
        "spotcheck_pass": all(row["collision"]["passes"] for row in rows),
        "release_ready": False,
        "release_blockers": [
            "Representative-state spot-check is not a full-path collision audit.",
            "Supplier-interface envelopes are not manufacturing-detail CAD; verify received-part widths before drilling.",
            "Actual lower-limit trip lengths are not verified.",
        ],
        "rows": rows,
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, ensure_ascii=False, indent=2)
    destination.write_text(serialized + "\n", encoding="utf-8")
    return json.loads(serialized)


if __name__ == "__main__":
    result = run_cad_spotcheck(
        ROOT / "verification" / "reve_home_path_audit_2026-09-17.json",
        ROOT / "verification" / "reve_home_cad_spotcheck_2026-09-17.json",
    )
    print(
        json.dumps(
            {
                "pose_count": len(result["rows"]),
                "spotcheck_pass": result["spotcheck_pass"],
                "full_path_cad_collision_audited": result[
                    "full_path_cad_collision_audited"
                ],
                "release_ready": result["release_ready"],
            },
            ensure_ascii=False,
        )
    )
