"""Four-million-won project budget for the NAVIMRO fabrication release."""

import csv
from pathlib import Path

from calculations.navimro_single_order_cost import summarize_bom


CAP_KRW = 4_000_000
ALLOWANCES = (
    ("freight_and_long_item_surcharge", 150_000, "NAVIMRO/forwarder provisional allowance"),
    ("outsourced_cut_drill_acrylic_work", 300_000, "Local shop quote allowance; DXF supplied"),
    ("missing_drill_crimp_measurement_tools", 100_000, "Use only if the laboratory lacks the listed tools"),
    ("misc_labels_spacers_small_consumables", 50_000, "Non-catalogue fit-up allowance"),
    ("price_change_and_rework_contingency", 400_000, "Do not spend before technical hold items close"),
)


def budget_summary():
    bom = summarize_bom()
    known = bom["priced_total_krw_vat_included"]
    allowance_total = sum(value for _, value, _ in ALLOWANCES)
    planned = known + allowance_total
    return {
        "navimro_known_subtotal_krw": known,
        "allowance_total_krw": allowance_total,
        "planned_total_krw": planned,
        "budget_cap_krw": CAP_KRW,
        "headroom_krw": CAP_KRW - planned,
        "within_cap": planned <= CAP_KRW,
        "hold_lines": bom["hold_lines"],
    }


def write_outputs(root=None):
    root = Path(root) if root else Path(__file__).resolve().parents[1]
    output_dir = root / "outputs" / "navimro_fabrication" / "tables"
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = budget_summary()
    csv_path = output_dir / "navimro_budget_4m.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(("budget_item", "amount_krw_vat_included_or_reserved", "basis"))
        writer.writerow(("NAVIMRO_BOM_49_LINES", summary["navimro_known_subtotal_krw"], "verified product-page prices 2026-08-27"))
        for name, value, basis in ALLOWANCES:
            writer.writerow((name, value, basis))
        writer.writerow(("PLANNED_TOTAL", summary["planned_total_krw"], ""))
        writer.writerow(("BUDGET_CAP", summary["budget_cap_krw"], "user confirmed"))
        writer.writerow(("HEADROOM", summary["headroom_krw"], "must remain non-negative at purchase release"))

    md_path = output_dir.parent / "navimro_budget_4m.md"
    lines = [
        "# NAVIMRO 4,000,000 KRW Budget Gate",
        "",
        f"- Known NAVIMRO BOM subtotal: **{summary['navimro_known_subtotal_krw']:,} KRW** (VAT included).",
        f"- Reserved freight, fabrication, tools, consumables and contingency: **{summary['allowance_total_krw']:,} KRW**.",
        f"- Planned total: **{summary['planned_total_krw']:,} KRW**.",
        f"- Remaining headroom: **{summary['headroom_krw']:,} KRW** below the 4,000,000 KRW cap.",
        "",
        "The known subtotal includes the logged-in fan and filter prices and two 6 m steel flat bars. The reserve is not a quotation. Replace each allowance with a written amount before release and keep the final total at or below the cap.",
        "",
        "## One-order release gate",
        "",
        "1. Obtain written confirmation for the actuator end accessory, pin-centre length, current, Hall wiring, U/H bracket stack, latch rating and shaft-collar holding data.",
        "2. Ask NAVIMRO for one consolidated quote containing all 49 BOM rows, VAT, long-item freight and dispatch dates.",
        "3. Obtain one local quote for the supplied DXF/cut-list package; do not permit vendor-pattern holes to be drilled before the delivered parts are available.",
        "4. Release the single NAVIMRO order only when the consolidated quote plus local fabrication quote and reserves remain within 4,000,000 KRW.",
    ]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return [csv_path, md_path]


if __name__ == "__main__":
    print(budget_summary())
    for path in write_outputs():
        print(path)

