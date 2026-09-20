"""Verify the Manual 3-RPS Rev M1 BOM against the native Fusion manifest.

The same deterministic audit is executed three times.  The output is a compact
JSON record used by the design verification log and final workbook.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "manual_3rps_rev_m1_fusion_native"
BOM_PATH = ROOT / "procurement" / "manual_rev_m1_bom_data_2026-09-02.json"
VALIDATION_PATH = OUTPUT / "Manual_3RPS_RevM1_validation.json"
FUSION_PATH = OUTPUT / "Manual_3RPS_RevM1_fusion_interference.json"
STEP_PATH = OUTPUT / "Manual_3RPS_RevM1_step_audit.json"
AUDIT_PATH = OUTPUT / "Manual_3RPS_RevM1_bom_cad_audit.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def audit_once(bom, validation, fusion, step, pass_index):
    names = tuple(validation.get("fusion_component_names", ()))
    row_reports = []
    exact_coverage = set()
    all_coverage = set()

    for row in bom["rows"]:
        matched = set()
        for pattern in row.get("cad_patterns", ()):
            expression = re.compile(pattern)
            matched.update(name for name in names if expression.search(name))

        expected = int(row.get("cad_occurrence_expected", 0))
        factor = int(row.get("physical_qty_per_cad_occurrence", 1))
        proxy = bool(row.get("cad_proxy", False))
        count_ok = len(matched) == expected
        physical_ok = proxy or expected == 0 or int(row["used_qty"]) == expected * factor
        all_coverage.update(matched)
        if not proxy:
            exact_coverage.update(matched)

        row_reports.append(
            {
                "line_id": row["line_id"],
                "matched_cad_occurrences": len(matched),
                "expected_cad_occurrences": expected,
                "physical_used_qty": row["used_qty"],
                "physical_qty_per_cad_occurrence": factor,
                "cad_proxy": proxy,
                "count_ok": count_ok,
                "physical_qty_ok": physical_ok,
                "matched_names": sorted(matched),
            }
        )

    budgetary_total = sum(
        float(row["budgetary_unit_price_krw"]) * float(row["order_qty"])
        for row in bom["rows"]
    )
    known_subtotal = sum(
        float(row["unit_price_krw"]) * float(row["order_qty"])
        for row in bom["rows"]
        if row.get("unit_price_krw") is not None
    )
    forbidden_electrical_terms = (
        "actuator",
        "battery",
        "controller",
        "diode",
        "fuse",
        "encoder",
        "imu",
        "sensor",
        "24v",
        "12v",
    )
    searchable = "\n".join(
        " ".join(
            str(row.get(key, ""))
            for key in ("category", "item", "exact_spec", "supplier_code")
        ).lower()
        for row in bom["rows"]
    )
    forbidden_hits = sorted(
        term
        for term in forbidden_electrical_terms
        if re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", searchable)
    )
    uncovered = sorted(set(names) - exact_coverage)

    checks = {
        "native_component_count_is_129": len(names) == 129,
        "all_nonproxy_cad_components_covered": not uncovered,
        "all_bom_row_cad_counts_match": all(row["count_ok"] for row in row_reports),
        "all_physical_quantities_match_cad": all(row["physical_qty_ok"] for row in row_reports),
        "no_active_electrical_items": not forbidden_hits,
        "budgetary_total_below_4m_cap": budgetary_total <= float(bom["budget_cap_krw"]),
        "fusion_interference_three_passes_zero": bool(fusion.get("all_zero"))
        and int(fusion.get("pass_count", 0)) == 3,
        "step_independent_audit_pass": bool(step.get("pass")),
        "digital_layout_pass": bool(validation.get("digital_layout_passes")),
    }
    signature = {
        "component_count": len(names),
        "covered_component_count": len(exact_coverage),
        "row_counts": tuple(
            (row["line_id"], row["matched_cad_occurrences"], row["count_ok"])
            for row in row_reports
        ),
        "budgetary_total_krw": budgetary_total,
        "checks": tuple(sorted(checks.items())),
    }
    return {
        "pass": pass_index,
        "native_component_count": len(names),
        "exact_covered_component_count": len(exact_coverage),
        "all_matched_component_count": len(all_coverage),
        "uncovered_component_names": uncovered,
        "forbidden_electrical_term_hits": forbidden_hits,
        "known_subtotal_krw": known_subtotal,
        "budgetary_total_krw": budgetary_total,
        "budget_remaining_krw": float(bom["budget_cap_krw"]) - budgetary_total,
        "quote_required_rows": sum(
            1 for row in bom["rows"] if row.get("unit_price_krw") is None
        ),
        "checks": checks,
        "rows": row_reports,
        "signature": signature,
        "passes": all(checks.values()),
    }


def main():
    bom = load(BOM_PATH)
    validation = load(VALIDATION_PATH)
    fusion = load(FUSION_PATH)
    step = load(STEP_PATH)
    passes = [
        audit_once(bom, validation, fusion, step, pass_index)
        for pass_index in range(1, 4)
    ]
    repeatable = passes[0]["signature"] == passes[1]["signature"] == passes[2]["signature"]
    result = {
        "revision": bom["revision"],
        "bom_source": str(BOM_PATH),
        "fusion_validation_source": str(VALIDATION_PATH),
        "pass_count": 3,
        "repeatable": repeatable,
        "passes": passes,
        "all_pass": repeatable and all(row["passes"] for row in passes),
    }
    AUDIT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "pass_count": result["pass_count"],
                "repeatable": result["repeatable"],
                "all_pass": result["all_pass"],
                "native_component_count": passes[0]["native_component_count"],
                "covered_component_count": passes[0]["exact_covered_component_count"],
                "uncovered_component_count": len(passes[0]["uncovered_component_names"]),
                "bom_rows": len(bom["rows"]),
                "budgetary_total_krw": passes[0]["budgetary_total_krw"],
                "budget_remaining_krw": passes[0]["budget_remaining_krw"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    raise SystemExit(0 if result["all_pass"] else 1)


if __name__ == "__main__":
    main()
