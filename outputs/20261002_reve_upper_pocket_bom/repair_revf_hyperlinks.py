"""Repair native hyperlink relationships after artifact-tool row relocation.

The workbook itself is authored with artifact-tool. Its documented row-copy API
retains displaced native hyperlink relationships, even when contents are cleared.
This narrowly scoped openpyxl pass restores exact targets by BOM ID and four
unpriced HOLD candidates. The artifact-tool HYPERLINK() formula is unimplemented
and yields a polluted cached label, so native relationships are necessary. This
pass does not author values, formulas, layout, or purchase data.
"""

from pathlib import Path
import re

from openpyxl import load_workbook


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "outputs/20261002_reve_followthrough/2026_BIZ-Lab_재료비관리_RevE_연속검수.xlsx"
TARGET = Path(__file__).resolve().parent / "2026_BIZ-Lab_재료비관리_RevF_상부포켓검토.xlsx"
ID_PREFIX = re.compile(r"^([A-Z][A-Z0-9]*)\.")
BRACKET_IDS = {"UP01A", "UP01B", "UP01C"}


def indexed(sheet):
    result = {}
    for row in range(4, sheet.max_row + 1):
        match = ID_PREFIX.match(str(sheet[f"I{row}"].value or ""))
        if match:
            result[match.group(1)] = row
    return result


source_book = load_workbook(SOURCE)
target_book = load_workbook(TARGET)
source_sheet = source_book["Sheet1"]
target_sheet = target_book["Sheet1"]
source_rows = indexed(source_sheet)
target_rows = indexed(target_sheet)

for identifier, row in target_rows.items():
    target_link = target_sheet[f"G{row}"]
    if identifier in BRACKET_IDS:
        target_link.value = None
        target_link.hyperlink = None
        continue
    assert identifier in source_rows, f"Unexpected retained ID {identifier}"
    source_link = source_sheet[f"G{source_rows[identifier]}"]
    assert source_link.hyperlink and source_link.hyperlink.target == source_link.value
    assert target_link.value == source_link.value, f"Displayed URL drift: {identifier}"
    target_link.hyperlink = source_link.hyperlink.target

# The first summary row was formerly a priced item during the row shift.
target_sheet["G70"].value = None
target_sheet["G70"].hyperlink = None

hold_urls = {
    77: "https://kr.misumi-ec.com/vona2/detail/110300095750/?HissuCode=HCDGH6-35",
    78: "https://kr.misumi-ec.com/vona2/detail/110300095750/?HissuCode=HCDGH6-35",
    79: "https://kr.misumi-ec.com/vona2/detail/110302677010/?HissuCode=WSSB10-6-4",
    80: "https://kr.misumi-ec.com/vona2/detail/110300239250/?HissuCode=PACK-SCB6-12-YBM",
}
for row, expected in hold_urls.items():
    cell = target_sheet[f"G{row}"]
    assert cell.value == expected, f"G{row}: candidate URL text drift"
    cell.hyperlink = expected
target_sheet["G81"].hyperlink = None

target_book.save(TARGET)
source_book.close()
target_book.close()
print(f"Restored {len(target_rows) - len(BRACKET_IDS)} paid and {len(hold_urls)} HOLD hyperlinks")
