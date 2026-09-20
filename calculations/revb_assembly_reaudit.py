"""Independent assembly-feasibility re-audit for profile-only Rev B."""

from __future__ import annotations

import json
from pathlib import Path

from cad.minimal_profile_only_revb import (
    connector_fastener_axis_audit,
    joint_axis_alignment_audit,
    support_azimuth_audit,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = (
    ROOT
    / "outputs"
    / "minimal_profile_only_revB"
    / "verification"
    / "revB_assembly_reaudit_2026-08-31.json"
)


def run_audit():
    joints = joint_axis_alignment_audit()
    supports = support_azimuth_audit()
    connectors = connector_fastener_axis_audit()
    passes = joints["passes"] and supports["passes"] and connectors["passes"]
    return {
        "revision": "B",
        "status": "REJECTED_ASSEMBLY_GEOMETRY_REDESIGN_REQUIRED",
        "fabrication_release": False,
        "purchase_release": False,
        "passes": passes,
        "joint_axis_alignment": joints,
        "support_azimuth": supports,
        "connector_fastener_axes": connectors,
        "blocking_findings": [
            "4035 and DCB3025 second-leg fasteners are modeled vertical instead of horizontal.",
            "The 14.5 mm upper single-side offset creates a non-perpendicular actuator/pin stack even at zero tilt.",
            "Support azimuth gaps are 90/90/180 degrees rather than the requested 120/120/120 degrees.",
        ],
    }


def main():
    result = run_audit()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
