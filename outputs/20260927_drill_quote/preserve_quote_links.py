from copy import copy
from pathlib import Path
import sys

from openpyxl import load_workbook
from openpyxl.workbook.properties import CalcProperties


source = Path(sys.argv[1])
target = Path(sys.argv[2])
workbook = load_workbook(source)
sheet = workbook['Sheet1']

# The spreadsheet engine available for this task does not expose native
# hyperlink editing. Keep the supplied template and its clickable URL cells.
sheet.insert_rows(37, amount=2)

items = [
    (
        '재료비 구매', '나비엠알오', 'HSS 금속용 드릴 Ø6.8 mm',
        'SD 6.8 / K11176399', 1, 'https://m.navimro.com/p/K11176399/', 2090,
        'T01. M8×1.25 절삭탭 밑구멍용. A1~A3 직접 가공 시만 구매. 1EA. 공구비 승인·드릴 척 확인.'
    ),
    (
        '재료비 구매', '나비엠알오', 'HSS 금속용 드릴 Ø9.0 mm',
        'D1101090 / K01216966', 1, 'https://m.navimro.com/p/K01216966/', 21990,
        'T02. M8 클리어런스 홀용. A1~A3 직접 가공 시만 구매. 1PK(5EA). 공구비 승인·드릴 척 확인.'
    ),
]

for row_num, values in zip((37, 38), items):
    for column_num, value in enumerate(values, start=2):
        template = sheet.cell(36, column_num)
        cell = sheet.cell(row_num, column_num)
        cell._style = copy(template._style)
        cell.alignment = copy(template.alignment)
        cell.value = value

# Row insertion does not consistently update hyperlink references in xlsx
# templates. Rebind each moved native link to the URL visible in its own cell.
for row_num in range(37, 68):
    cell = sheet.cell(row_num, 7)
    cell.hyperlink = str(cell.value)
    cell.font = copy(sheet['G36'].font)

for row_num in range(37, 68):
    sheet.row_dimensions[row_num].height = 30
for row_num in (68, 69, 70):
    sheet.row_dimensions[row_num].height = 16.5
sheet.row_dimensions[71].height = 30

sheet['B68'] = '공급가액 소계 (업체 가공안)'
sheet['H68'] = '=SUM(H4:H36,H39:H67)'
sheet['B69'] = '부가세 (10%)'
sheet['H69'] = '=ROUND(H68*10%,0)'
sheet['B70'] = '총 액 (부가세 포함)'
sheet['H70'] = '=SUM(H68:H69)'
sheet['B71'] = '잔 액'
sheet['H71'] = '=$I$2-H70'
sheet['I71'] = '드릴 선택품 24,080원(VAT 포함 26,488원). 외주가공안과 중복이므로 기본 합계 제외.'

workbook.calculation = CalcProperties(calcMode='auto', fullCalcOnLoad=True)
target.parent.mkdir(parents=True, exist_ok=True)
workbook.save(target)
