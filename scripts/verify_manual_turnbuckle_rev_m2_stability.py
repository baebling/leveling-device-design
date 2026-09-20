"""Run the Rev M2 self-standing audit twice and persist deterministic results."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from calculations.manual_turnbuckle_rev_m2_stability import self_standing_audit


OUT = ROOT / "outputs" / "manual_turnbuckle_rev_m2"
AUDIT = OUT / "Manual_3RPS_RevM2_self_standing_verification.json"


def _digest(payload):
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def main():
    cycles = [self_standing_audit(), self_standing_audit()]
    hashes = [_digest(cycle) for cycle in cycles]
    repeated_results_identical = hashes[0] == hashes[1]
    result = {
        "method": "two deterministic numerical audit cycles",
        "cycles": cycles,
        "cycle_sha256": hashes,
        "repeated_results_identical": repeated_results_identical,
        "locked_static_self_standing_pass": all(cycle["pass"] for cycle in cycles),
        "whole_unit_external_tip_resistance_verified": False,
        "purchase_release": False,
        "fabrication_release": False,
        "pass": all(cycle["pass"] for cycle in cycles) and repeated_results_identical,
    }
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    AUDIT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {
        "audit": str(AUDIT),
        "cycles": len(cycles),
        "repeated_results_identical": repeated_results_identical,
        "constraint_pose_count": cycles[0]["constraint"]["pose_count"],
        "gravity_case_count": cycles[0]["gravity"]["case_count"],
        "minimum_constraint_rank": cycles[0]["constraint"]["minimum_rank"],
        "minimum_gravity_reaction_n": cycles[0]["gravity"]["minimum_reaction_n"],
        "maximum_equivalent_axial_n": cycles[0]["gravity"]["maximum_equivalent_axial_n"],
        "pass": result["pass"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
