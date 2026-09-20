from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOM_PATH = ROOT / "procurement" / "navimro_single_order_bom.csv"


def summarize_bom(path: Path = BOM_PATH) -> dict[str, object]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    priced_total = 0
    priced_by_category: dict[str, int] = defaultdict(int)
    unknown_price_lines: list[str] = []
    hold_lines: list[str] = []

    for row in rows:
        quantity = int(row["order_qty"])
        unit_price = int(row["unit_price_krw_vat_included"])
        extended = int(row["extended_price_krw"])
        if extended != quantity * unit_price:
            raise ValueError(f"Subtotal mismatch: {row['line_id']}")
        priced_total += extended
        priced_by_category[row["category"]] += extended
        if unit_price == 0:
            unknown_price_lines.append(row["line_id"])
        if row["order_status"].startswith("HOLD"):
            hold_lines.append(row["line_id"])

    return {
        "line_count": len(rows),
        "priced_total_krw_vat_included": priced_total,
        "priced_by_category_krw": dict(sorted(priced_by_category.items())),
        "unknown_price_lines": tuple(unknown_price_lines),
        "hold_lines": tuple(hold_lines),
    }


if __name__ == "__main__":
    print(summarize_bom())
